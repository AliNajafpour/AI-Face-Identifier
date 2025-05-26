import os
import time
import io
import base64
import re
import shutil
import requests
from bs4 import BeautifulSoup
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys


def setup_driver():
    options = Options()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return driver


def search_google_lens(driver, image_path):
    driver.get('https://lens.google.com/')
    time.sleep(2)
    button = driver.find_element(By.XPATH, '//button[@aria-label="Accept all"]')
    if button:
        button.click()
    wait = WebDriverWait(driver, 30)
    

    if not os.path.exists(image_path):
        print('Image not found!')
        return False

    upload_input = wait.until(
        EC.presence_of_element_located((By.XPATH, '//input[@type="file"]'))
    )
    upload_input.send_keys(os.path.abspath(image_path))

    try:
        wait.until(
            EC.presence_of_all_elements_located((By.TAG_NAME, 'img'))
        )
        time.sleep(3)

    except Exception:
        driver.save_screenshot('./results/lens_result_fail.png')
        print('No results loaded or blocked by CAPTCHA.')
        return False

    return True


def extract_images(driver, max_images=10):
    wait = WebDriverWait(driver, 10)

    image_elements = driver.find_elements(By.TAG_NAME, 'img')
    image_urls = set()

    for img in image_elements:
        src = img.get_attribute('src') or img.get_attribute('data-src')
        if src and 'data:image/gif' not in src:
            width = int(img.get_attribute('width') or 0)
            height = int(img.get_attribute('height') or 0)
            if width >= 100 and height >= 100:
                image_urls.add(src)
        if len(image_urls) >= max_images:
            break
        source_urls = set()
        links = driver.find_elements(By.XPATH, '//a[@href]')
        for link in links:
            href = link.get_attribute('href')
            if 'google.com' not in href:
                source_urls.add(href)


    return list(image_urls), list(source_urls)[0 : max_images + 10]

def extract_data_first(driver, class_name='I9S4yc', count_limit=10):
    try:
        span = driver.find_element(By.CLASS_NAME, class_name)
        text = span.text.strip()

        print(f'the Name is: {text}')
        url = f'https://www.google.com/search?q={text}'

        driver.get(url)
        time.sleep(3)

        links = driver.find_elements(By.CLASS_NAME, 'zReHs')

        count = 0

        with open('./results/links.txt', 'w', encoding='utf-8') as f:
            f.write("")

        for link in links:
            href = link.get_attribute('href')
            print(href)               
            if 'wikipedia.org' in href:
                with open('./results/links.txt', 'a', encoding='utf-8') as f:
                    f.write(href + '\n')
                return href
            
            elif 'linkedin.com' in href:
                with open('./results/links.txt', 'a', encoding='utf-8') as f:
                    f.write(href + '\n')
                return href

            if count < count_limit:
                count += 1
                with open('./results/links.txt', 'a', encoding='utf-8') as f:
                    f.write(href + '\n')

        return True
    except Exception as e:
        print(f"Could not find span with class '{class_name}': {e}")


def wiki_extract(url):
    pattern = '//[a-z]{2,3}\.'
    en_url = re.sub(pattern, '//', url)
    # using the English wikipedia if possible
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(en_url, headers=headers)
    if str(response.status_code).startswith('2'):
        soup = BeautifulSoup(response.text, 'html.parser')
    else:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

    title = soup.find('h1').text.strip()
    text = ''
    data = soup.find_all('p')
    count = 0
    # get only the first paragraph
    for p in data:
        if len(p.get_text()) > 20:
            text = p.get_text()
            break

    with open('./results/wikiResults.txt', 'w', encoding='utf-8') as f:
        f.write(text)
    print('Extract Completed')
    return text


def linkedin_extract(driver , url):
    LINKEDIN_EMAIL = 'arsprogramming123@gmail.com'
    LINKEDIN_PASSWORD = 'ars13861201'
    try:
        driver.get('https://www.linkedin.com/login')
        time.sleep(2)
        email_input = driver.find_element(By.ID, 'username')
        password_input = driver.find_element(By.ID, 'password')
        email_input.send_keys(LINKEDIN_EMAIL)
        password_input.send_keys(LINKEDIN_PASSWORD)
        password_input.send_keys(Keys.RETURN)
        time.sleep(5)
        driver.get(url)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        name_tag = soup.select_one('h1.inline.t-24.v-align-middle.break-words')
        name = name_tag.text.strip() if name_tag else 'Name not found'
        title_tag = soup.select_one('div.text-body-medium.break-words')
        title = title_tag.text.strip() if title_tag else 'Title not found'
        location_tag = soup.select_one('span.text-body-small.inline.t-black--light')
        location = location_tag.text.strip() if location_tag else 'Location not found'

        try:
            contact_btn = driver.find_element(
                By.CSS_SELECTOR, 'a[href*="overlay/contact-info"]'
            )
            contact_btn.click()
            time.sleep(3)

            contact_soup = BeautifulSoup(driver.page_source, 'html.parser')
            contact_sections = contact_soup.select(
                'section.pv-contact-info__contact-type'
            )

            contact_info = {}
            for section in contact_sections:
                header = section.find('h3')
                if not header:
                    continue
                label = header.text.strip()
                link = section.find('a', href=True)
                description = section.find('span')

                contact_info[label] = {
                    'url': link['href'].strip() if link else None,
                    'description': description.text.strip() if description else ''
                }
        except Exception as e:
            contact_info = {'error': f"Failed to extract contact info: {str(e)}"}
        with open(
            './results/results.txt', 'w', encoding='utf-8'
        ) as file:
            file.write(f"Name: {name}\n")
            file.write(f"Title: {title}\n")
            file.write(f"Location: {location}\n")
            file.write("Contact Info:\n")
            if "error" in contact_info:
                file.write(f" - Error: {contact_info['error']}\n")
            else:
                for k, v in contact_info.items():
                    file.write(f" - {k}: {v['url'] or 'N/A'} ({v['description']})\n")

    finally:
        pass

def save_source_urls(
    source_urls, file_name='./results/sourceURLs.txt'
):
    with open(file_name, 'w', encoding='utf-8') as file:
        for url in source_urls:
            file.write(f"{url}\n")


def download_images(download_path, image_urls):
    if os.path.exists(download_path) and os.path.isdir(download_path):
        shutil.rmtree(download_path)
    os.makedirs(download_path, exist_ok=True)
    for i, url in enumerate(image_urls):
        try:
            if url.startswith('data:image'):
                match = re.match(r'data:image\/[a-z]+;base64,(.*)', url)
                if match:
                    base64_string = match.group(1)
                    image_content = base64.b64decode(base64_string)
                else:
                    continue
            else:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                image_content = response.content
            image_file = io.BytesIO(image_content)
            image = Image.open(image_file)
            file_path = os.path.join(download_path, f"image_{i + 1}.jpg")
            image.save(file_path, 'JPEG')
            print(f"Downloaded {file_path}")
        except Exception as e:
            print(f"Failed to download {url}: {e}")


def urlproccessor(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
    with open(output_file, 'w', encoding='utf-8'):
        pass
    with open(output_file, 'a', encoding='utf-8') as f_out:
        for url in urls:
            try:
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')

                title = soup.title.string.strip() if soup.title else 'No Title'
                paragraphs = [
                    p.get_text(strip=True)
                    for p in soup.find_all('p')
                    if p.get_text(strip=True)
                ]
                with open(output_file, 'w', encoding='utf-8') as f:
                    pass
                f_out.write(f'URL: {url}\n')
                f_out.write(f'Title: {title}\n')
                f_out.write('First paragraphs:\n')
                for para in paragraphs[:3]:
                    f_out.write(f'- {para}\n')
                f_out.write('\n' + '-' * 60 + '\n\n')
            except Exception as e:
                f_out.write(f'URL: {url}\n')
                f_out.write(f'Error processing: {str(e)}\n')
                f_out.write('\n' + '-' * 60 + '\n\n')
    print(f'Extraction completed. Results saved in "{output_file}".')


def main(path):
    driver = setup_driver()
    try:
        search_google_lens(driver, image_path)
        image_urls, source_urls = extract_images(driver, max_images=10)

        try:
            result = extract_data_first(driver, class_name='I9S4yc')
            if 'wikipedia.org' in result:
                wiki_extract(result)
                return
            
            elif 'linkedin.com' in result:
                linkedin_extract(driver, result)
        
        except:
            if image_urls:
                print(f"found {len(image_urls)} images.")
                download_images(
                    './results/downloaded_images', image_urls
                )

            else:
                print('no images found.')

            if source_urls:
                print(f"found {len(source_urls)} source URLs.")
                save_source_urls(source_urls)

            else:
                print('no source URLs found.')

            input_file = './results/sourceURLs.txt'
            output_file = './results/results.txt'
            urlproccessor(input_file, output_file)

    finally:
        driver.quit()



# Set your image path here
image_path = 'test_assets/images/testnf2.jpg'
main(image_path)
