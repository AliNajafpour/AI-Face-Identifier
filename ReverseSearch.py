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
    wait = WebDriverWait(driver, 20)

    if not os.path.exists(image_path):
        print('Image not found!')
        return False
    upload_input = wait.until(
        EC.presence_of_element_located((By.XPATH, '//input[@type="file"]'))
    )
    upload_input.send_keys(os.path.abspath(image_path))

    try:
        wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//img[contains(@src,"gstatic") or contains(@src,"googleusercontent")]'
                )
            )
        )
    except Exception:
        driver.save_screenshot('lens_result_fail.png')
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
    links = driver.find_elements(By.XPATH, '//a[@href and contains(@href, "http")]')
    source_urls = {
        link.get_attribute('href') for link in links if link.get_attribute('href')
    }

    return list(image_urls), list(source_urls)[0:max_images+10]


def extract_data_first(driver, class_name='I9S4yc'):
    try:
        span = driver.find_element(By.CLASS_NAME, class_name)
        text = span.text.strip()
        
        print(f'the Name is: {text}')
        url = f'https://www.google.com/search?q={text}'

        driver.get(url)
        time.sleep(3)

        links = driver.find_elements(By.XPATH, '//a[contains(@href, "wikipedia.org")]')
        for link in links:
            href = link.get_attribute('href')
            if 'wikipedia.org' in href:
                print(href)
                return href
        print("Wikipedia link not found.")
        return None

    except Exception as e:
        print(f"Could not find span with class '{class_name}': {e}")


def wiki_extract(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    title = soup.find('h1').text.strip()

    data = soup.find_all('p')
    for p in data:
        text = p.get_text(strip=True)

    print(text[:500])
    with open('./results.txt', 'w') as f:
        f.write(text)
    return text


def save_source_urls(source_urls, file_name='./sourceURLs.txt'):
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


def main(image_path):
    driver = setup_driver()
    try:
        if not search_google_lens(driver, image_path):
            print('image search failed or blocked.')
            return
        image_urls, source_urls = extract_images(driver, max_images=10)

        if image_urls:
            print(f"found {len(image_urls)} images.")
            download_images('downloaded_images', image_urls)
        else:
            print('no images found.')
        if source_urls:
            print(f"found {len(source_urls)} source URLs.")
            save_source_urls(source_urls)
        else:
            print('no source URLs found.')
        input_file = './sourceURLs.txt'
        output_file = 'results.txt'
        # urlproccessor(input_file, output_file)
        result = extract_data_first(driver, class_name='I9S4yc')
        wiki_extract(result)
    finally:
        driver.quit()


# Set your image path here
image_path = './test/download1.png'
main(image_path)
