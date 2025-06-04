import os
import time
import io
import base64
import re
import shutil
import requests
from bs4 import BeautifulSoup
from PIL import Image
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from transformers import pipeline
from boilerpy3 import extractors
import sites_data_scrap
from lingua import Language, LanguageDetectorBuilder

# models
english_qa = pipeline(
    'question-answering',
    model='deepset/roberta-base-squad2',
    tokenizer='deepset/roberta-base-squad2',
    model_max_lengh=2000
)
persian_qa = pipeline(
    'question-answering',
    model='pedramyazdipoor/persian_xlm_roberta_large',
    model_max_lengh=2000
)

english_ner = pipeline(
    'ner', model='dslim/bert-base-NER', aggregation_strategy='simple'
)
persian_ner = pipeline(
    'ner',
    model='HooshvareLab/bert-base-parsbert-ner-uncased',
    aggregation_strategy='simple'
)


def detect_lang(text):
    languages = [Language.ENGLISH, Language.PERSIAN]

    detector = LanguageDetectorBuilder.from_languages(*languages).build()

    language = detector.detect_language_of(text)

    if language == Language.ENGLISH:
        return 'e'
    elif language == Language.PERSIAN:
        return 'p'


def eng_text_analysis(text):
    entities = english_ner(text)
    names = []
    name = None
    if len(entities) > 0:
        for entity in entities:
            if entity['entity_group'] == 'PER':
                names.append(entity['word'])
    else:
        return None
    name = max(set(names), key=names.count)

    # Extract occupation and nationality using QA
    questions = {
        'occupation': f"What is the occupation of {name}?",
        'nationality': f"What is the nationality of {name}?"
    }

    results = {'name': name}
    for key, question in questions.items():
        answer = english_qa(question=question, context=text)
        results[key] = answer['answer'] if answer['score'] > 0.2 else None
    print('Name:', results['name'])
    print('Occupation:', results['occupation'])
    print('Nationality:', results['nationality'])
    return results


def per_text_analysis(text):
    entities = persian_ner(text)
    names = []
    name = None
    if len(entities) > 0:
        for entity in entities:
            if entity['entity_group'] == 'person':
                names.append(entity['word'])
    else:
        return None
    name = max(set(names), key=names.count)
    # Extract occupation and nationality using QA
    questions = {'occupation': f"شغل {name} چیست؟", 'nationality': f"ملیت {name} چیست؟"}

    results = {'name': name}
    for key, question in questions.items():
        answer = persian_qa(question=question, context=text)
        results[key] = answer['answer'] if answer['score'] > 0.2 else None
    print('Name:', results['name'])
    print('Occupation:', results['occupation'])
    print('Nationality:', results['nationality'])
    return results


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
    try:
        button = driver.find_element(By.XPATH, '//button[@aria-label="Accept all"]')
        button.click()
    except:
        pass
    wait = WebDriverWait(driver, 30)

    if not os.path.exists(image_path):
        print('Image not found!')
        return False
    upload_input = wait.until(
        EC.presence_of_element_located((By.XPATH, '//input[@type="file"]'))
    )
    upload_input.send_keys(os.path.abspath(image_path))

    try:
        wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'img')))
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
    links = driver.find_elements(By.XPATH, '//a[@href and contains(@href, "http")]')

    tabs = driver.find_elements(By.CLASS_NAME, 'T3FoJb')
    exact_results = tabs[3]
    exact_results_source_urls = None
    try:
        exact_results.click()
        try:
            exact_results_links = driver.find_elements(
                By.XPATH, '//a[@href and contains(@href, "http")]'
            )

            exact_results_source_urls = {
                link.get_attribute('href')
                for link in exact_results_links
                if link.get_attribute('href')
                and 'google.com' not in link.get_attribute('href')
            }

            driver.back()
        except:
            print('failed to get the links of the exact mathces')
    except:
        print('cant go to the exact matches')
    source_urls = {
        link.get_attribute('href')
        for link in links
        if link.get_attribute('href') and 'google.com' not in link.get_attribute('href')
    }
    if exact_results_source_urls:
        source_urls = source_urls.union(exact_results_source_urls)
    return list(image_urls), list(source_urls)[0 : max_images + 10]


def search_name(driver, name=None, class_name='I9S4yc', count_limit=100):
    if name is None and class_name is not None:
        try:
            span = driver.find_element(By.CLASS_NAME, class_name)
            name = span.text.strip()
        except:
            print('element not found!')
    print(f'the Name is: {name}')
    url = f'https://www.google.com/search?q={name}'

    driver.get(url)
    time.sleep(3)

    links = driver.find_elements(By.CLASS_NAME, 'zReHs')

    count = 0

    with open('./results/links.txt', 'w', encoding='utf-8') as f:
        f.write('')
    for link in links:
        href = link.get_attribute('href')
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


def save_urls(source_urls, file_name='urls.txt'):
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

#WEBSITES EXTRACTIONS

def wikipedia_extract(url):
    pattern = '//[a-z]{2,3}\\.'
    en_url = re.sub(pattern, '//', url)
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
    for p in data:
        if len(p.get_text()) > 20:
            text = p.get_text()
            break
    if text == '':
        count = 0
        spans = soup.find_all('span')
        for span in spans:
            text += span.get_text() + '\n'
            count += 1
            if count == 10:
                break
    with open('./results/data.txt', 'w', encoding='utf-8') as f:
        f.write(title + '\n')
        f.write(text)
    print('Extract Completed')
    print(text)
    return text


def linkedin_extract(driver, url):
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
        time.sleep(15)
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
        with open('./results/results.txt', 'w', encoding='utf-8') as file:
            file.write(f"Name: {name}\n")
            file.write(f"Title: {title}\n")
            file.write(f"Location: {location}\n")
            file.write("Contact Info:\n")
            if 'error' in contact_info:
                file.write(f" - Error: {contact_info['error']}\n")
            else:
                for k, v in contact_info.items():
                    file.write(f" - {k}: {v['url'] or 'N/A'} ({v['description']})\n")
    finally:
        pass

def github_extract(url , result):
    pattern = '//[a-z]{2,3}\\.'
    en_url = re.sub(pattern, '//', url)
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(en_url, headers=headers)

    if str(response.status_code).startswith('2'):
        soup = BeautifulSoup(response.text, 'html.parser')
    else:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
    name_tag = soup.select_one('span.p-name.vcard-fullname')
    name = name_tag.text.strip() if name_tag else 'Name not found'
    readme_tag = soup.select_one('article.markdown-body.entry-content')
    with open('./results/results.txt', 'w', encoding='utf-8') as file:
        file.write(f"Name: {name}\n")
        if readme_tag:
            readme = readme_tag.text.strip() if name_tag else 'ReadMe not found'
            file.write(f"Read Me:{readme}\n")
    
def main(path):
    driver = setup_driver()
    try:
        search_google_lens(driver, image_path)
        image_urls, source_urls = extract_images(driver, max_images=10)
        try:
            save_urls(source_urls, file_name='./results/sourceURLs.txt')
        except:
            print("couldn't save the source links.")
        try:
            related_names = driver.find_elements(By.CLASS_NAME, 'I9S4yc')
            if len(related_names) > 0:
                result = search_name(driver, class_name='I9S4yc')
                if 'wikipedia.org' in result:
                    text = wikipedia_extract(result)
                    lang = detect_lang(text)
                    if lang == 'e':
                        results = eng_text_analysis(text)
                    elif lang == 'p':
                        results = per_text_analysis(text)
                    else:
                        results = None
                elif 'linkedin.com' in result:
                    linkedin_extract(driver, result)
                    return
                # elif 'x.com' in result:
                #     pass
                # elif 'github.com' in result:
                #     pass
                # elif 'instagram.com' in result:
                #     pass
                # elif 'facebook.com' in result:
                #     pass
                else:
                    sites_data_scrap.sites_data_scrap_relevant(
                        './results/sourceURLs.txt', './results/data.txt'
                    )
                    with open('./results/data.txt', 'r', encoding='utf-8') as f:
                        text = f.read()
                    lang = detect_lang(text)
                    if lang == 'e':
                        results = eng_text_analysis(text)
                    elif lang == 'p':
                        results = per_text_analysis(text)
                    else:
                        results = None
                    if results is None:
                        sites_data_scrap.sites_data_scrap_all(
                            './results/sourceURLs.txt', './results/data.txt'
                        )
                        with open('./results/data.txt', 'r', encoding='utf-8') as f:
                            text = f.read()
                        lang = detect_lang(text)
                        if lang == 'e':
                            results = eng_text_analysis(text)
                        elif lang == 'p':
                            results = per_text_analysis(text)
                        else:
                            results = None
                    return results
            else:
                sites_data_scrap.sites_data_scrap_relevant(
                    './results/sourceURLs.txt', './results/data.txt'
                )
                with open('./results/data.txt', 'r', encoding='utf-8') as f:
                    text = f.read()
                lang = detect_lang(text)
                if lang == 'e':
                    results = eng_text_analysis(text)
                elif lang == 'p':
                    results = per_text_analysis(text)
                else:
                    results = None
                if results is None:
                    sites_data_scrap.sites_data_scrap_all(
                        './results/sourceURLs.txt', './results/data.txt'
                    )
                    with open('./results/data.txt', 'r', encoding='utf-8') as f:
                        text = f.read()
                    lang = detect_lang(text)
                    if lang == 'e':
                        results = eng_text_analysis(text)
                    elif lang == 'p':
                        results = per_text_analysis(text)
                    else:
                        results = None
                if results['name']:
                    if results['occupation'] is None or results['nationality'] is None:
                        result = search_name(
                            driver, name=results['name'], class_name=''
                        )
                        if 'wikipedia.org' in result:
                            text = wikipedia_extract(result)
                            lang = detect_lang(text)
                            if lang == 'e':
                                results = eng_text_analysis(text)
                            elif lang == 'p':
                                results = per_text_analysis(text)
                            else:
                                results = None
                        elif 'linkedin.com' in result:
                            linkedin_extract(driver, result)
                            return
                        # elif 'x.com' in result:
                        #     pass
                        # elif 'github.com' in result:
                        #     pass
                        # elif 'instagram.com' in result:
                        #     pass
                        # elif 'facebook.com' in result:
                        #     pass
                        else:
                            sites_data_scrap.sites_data_scrap_relevant(
                                './results/sourceURLs.txt', './results/data.txt'
                            )
                            with open('./results/data.txt', 'r', encoding='utf-8') as f:
                                text = f.read()
                            lang = detect_lang(text)
                            if lang == 'e':
                                results = eng_text_analysis(text)
                            elif lang == 'p':
                                results = per_text_analysis(text)
                            else:
                                results = None
                            if results is None:
                                sites_data_scrap.sites_data_scrap_all(
                                    './results/sourceURLs.txt', './results/data.txt'
                                )
                                with open(
                                    './results/data.txt', 'r', encoding='utf-8'
                                ) as f:
                                    text = f.read()
                                lang = detect_lang(text)
                                if lang == 'e':
                                    results = eng_text_analysis(text)
                                elif lang == 'p':
                                    results = per_text_analysis(text)
                                else:
                                    results = None
                            return results
                return results
        except Exception as e:
            print(e)
            if image_urls:
                print(f"found {len(image_urls)} images.")
                download_images('./results/downloaded_images', image_urls)
            else:
                print('no images found.')
            if source_urls:
                print(f"found {len(source_urls)} source URLs.")
            else:
                print('no source URLs found.')
            input_file = './results/sourceURLs.txt'
            output_file = './results/results.txt'
            urlproccessor(input_file, output_file)
    finally:
        driver.quit()


# Set your image path here
image_path = 'test_assets/images/test2.jpg'
main(image_path)
