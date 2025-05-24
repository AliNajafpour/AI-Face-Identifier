import os
import time
import io
import base64
import random
import re
import shutil
import requests
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
    return list(image_urls)


def save_links(image_urls, file_name='links.txt'):
    with open(file_name, 'w') as file:
        for url in image_urls:
            if url.startswith('data:image'):
                base64_string = re.match(r'data:image\/[a-z]+;base64,(.*)', url).group(
                    1
                )
                image_content = base64.b64decode(base64_string)
                file.write(f"{image_content}\n")
            else:
                file.write(f"{url}\n")
                


def download_images(download_path, image_urls):
    if os.path.exists(download_path) and os.path.isdir(download_path):
        shutil.rmtree(download_path)
    os.makedirs(download_path, exist_ok=True)
    for i, url in enumerate(image_urls):
        try:
            if url.startswith('data:image'):
                base64_string = re.match(r'data:image\/[a-z]+;base64,(.*)', url).group(
                    1
                )
                image_content = base64.b64decode(base64_string)
            else:
                response = requests.get(url, timeout=10)
                image_content = response.content
            image_file = io.BytesIO(image_content)
            image = Image.open(image_file)
            file_path = os.path.join(download_path, f"image_{i + 1}.jpg")
            image.save(file_path, 'JPEG')
            print(f"Downloaded {file_path}")
        except Exception as e:
            print(f"Failed to download {url}: {e}")


def main(image_path):
    driver = setup_driver()

    try:
        if not search_google_lens(driver, image_path):
            print('Image search failed or blocked.')
            return
        image_urls = extract_images(driver, max_images=10)
        if image_urls:
            save_links(image_urls)
            download_images('downloaded_images', image_urls)
        else:
            print('No images found.')
    finally:
        driver.quit()


# Set your image path here
image_path = 'D:/ARS/programming/faceidentifier/1/AI-Face-Identifier/test/download4.png'
main(image_path)
