import time
import os
import random
import requests
import io
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import base64
import re


# def search(image_path):
#     options = Options()
#     options.add_argument('--start-maximized')

#     options.add_argument(
#         'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
#     )

#     options.add_argument('--disable-blink-features=AutomationControlled')
#     options.add_experimental_option('excludeSwitches', ['enable-automation'])
#     options.add_experimental_option('useAutomationExtension', False)

#     driver = webdriver.Chrome(
#         service=Service(ChromeDriverManager().install()), options=options
#     )

#     driver.execute_script(
#         "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
#     )

#     try:
#         driver.get('https://lens.google.com/')
#         time.sleep(random.uniform(2, 5))

#         driver.execute_script('window.scrollTo(0, document.body.scrollHeight / 2);')
#         time.sleep(random.uniform(1, 3))

#         try:
#             captcha = driver.find_element(
#                 By.XPATH, '//iframe[contains(@src, "recaptcha")]'
#             )
#             print()
#             driver.quit()
#             return None
#         except:
#             pass
#         upload_input = driver.find_element(By.XPATH, '//input[@type="file"]')
#         if not os.path.exists(image_path):
#             print(f"{image_path}")
#             driver.quit()
#             return None
#         upload_input.send_keys(os.path.abspath(image_path))

#         time.sleep(random.uniform(5, 10))

#         result = driver.current_url
#         print(f"this is the resss .. . . . . .{result}")
#         return result
#     finally:
#         driver.quit()


# path = './test/images.png'
# base_url = search(path)

# for testing the download function
# image_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS_Sh_79KXtNm6WEXmv53vl5VN5sTkAPw_44g&s"
wd = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

url = 'https://www.google.com/search?sca_esv=49f8345e411de2b2&rlz=1C1GCEA_enIR1115IR1115&sxsrf=AHTn8zp8J8JaD4RDdUqG8s-jfA7U7zxr8Q:1747836789785&q=random+funny+pictures&udm=2&fbs=ABzOT_CWdhQLP1FcmU5B0fn3xuWpA-dk4wpBWOGsoR7DG5zJBsoP4kyzn2c6zz4kirWu1xixFt8Lz6aOKC7HiMUhzJnXeJOAaH_NFgXWvrqYZRtGwqR-s2wEnkWj9Q7DfGvbKJIGweaALa22OoDJCVpF1jHNBzLlPKfXJvyKqq2YI9OdE181O6sPM3Vbfqg_HCCCgkkpq-dg&sa=X&ved=2ahUKEwik5eu337SNAxUA7rsIHeUYDXcQtKgLegQIFRAB&biw=1536&bih=703&dpr=1.25'



def get_images(wd, url, max_images=10):
    wd.get(url)
    time.sleep(2)
    images = wd.find_elements(By.TAG_NAME, 'img')
    print(images)
    image_urls = set()


    for img in images:
        image_url = img.get_attribute('src') or img.get_attribute('data-src')
        if image_url and "data:image/gif" not in image_url:
            width = int(img.get_attribute('width') or 0)
            height = int(img.get_attribute('height') or 0)
            if width >= 100 and height >= 100:
                image_urls.add(image_url)
        if len(image_urls) >= max_images:
            break

    return list(image_urls) if image_urls else []

def download_images(download_path, image_urls):
    os.makedirs(download_path, exist_ok=True)

    for i, url in enumerate(image_urls):
        try:
            if url.startswith("data:image"):
                # Handle base64-encoded data URI
                # Extract the base64 part (after the comma)
                base64_string = re.match(r'data:image\/[a-z]+;base64,(.*)', url).group(1)
                # Decode base64 data
                image_content = base64.b64decode(base64_string)
            else:
                # Handle regular URL
                image_content = requests.get(url).content
        
            # saving the image as bytes using io
            image_file = io.BytesIO(image_content)
            # trsforming it to a image
            image = Image.open(image_file)
            file_path = os.path.join(download_path, f"image_{i+1}.jpg")
            image.save(file_path, 'JPEG')
            print(f"Downloaded {file_path}")
        except Exception as e:
            print(f"Failed to download {url}: {e}")


image_urls = get_images(wd, url, 1)

download_images("downloaded_images", image_urls)

wd.quit()
