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


def get_images(wd, url):
    def scroll_down(wd):
        wd.execute_script('window.scrollTo(0,document.body.scrollHeight);')

    url = 'https://www.google.com/search?sca_esv=49f8345e411de2b2&rlz=1C1GCEA_enIR1115IR1115&sxsrf=AHTn8zp8J8JaD4RDdUqG8s-jfA7U7zxr8Q:1747836789785&q=random+funny+pictures&udm=2&fbs=ABzOT_CWdhQLP1FcmU5B0fn3xuWpA-dk4wpBWOGsoR7DG5zJBsoP4kyzn2c6zz4kirWu1xixFt8Lz6aOKC7HiMUhzJnXeJOAaH_NFgXWvrqYZRtGwqR-s2wEnkWj9Q7DfGvbKJIGweaALa22OoDJCVpF1jHNBzLlPKfXJvyKqq2YI9OdE181O6sPM3Vbfqg_HCCCgkkpq-dg&sa=X&ved=2ahUKEwik5eu337SNAxUA7rsIHeUYDXcQtKgLegQIFRAB&biw=1536&bih=703&dpr=1.25'
    wd.get(url)
    ali = 0
    image_urls = set()
    # 10 is the number of images the we want to get them

    while len(image_urls) < 10:
        preview_images = wd.find_elements(By.CLASS_NAME, 'YQ4gaf')
        if preview_images:
            print('THUMBNAILS')
        else:
            time.sleep(2) 
            continue
        for img in preview_images[len(preview_images) : 10]:
            try:
                img.click()
                time.sleep(2)
                print('CLICK!')
            except Exception as e:
                print('RID! Error:')
            print('RESIDIM BE BOZARGE!')
            Large_images = wd.find_elements(By.CLASS_NAME, 'FyHeAf')
            for image in Large_images:
                ali = ali + 1
                if image.get_attribute('src') and 'http' in image.get_attribute('src'):
                    image_urls.add(image.get_attribute('src'))
                    print('Found an image!')
    return image_urls


def download_images(download_path, url, filename):
    try:
        image_content = requests.get(url).content
        # saving the image as bytes using io
        image_file = io.BytesIO(image_content)
        # trsforming it to a image
        image = Image.open(image_file)
        file_path = download_path + filename
        # saving the image
        with open(file_path, 'wb') as f:
            image.save(f, 'JPEG')
        print('Succes')
    except Exception as e:
        print('Failed')


base_url = 'https://www.google.com/search?q=random+funny+pictures&sca_esv=49f8345e411de2b2&rlz=1C1GCEA_enIR1115IR1115&udm=2&biw=1536&bih=271&sxsrf=AHTn8zqqCZmpFyHdwj4Shl6ykkjzhZeBdA%3A1747838210742&ei=AuUtaP2HLZjk7_UPjvejwAc&ved=0ahUKEwj9kLTd5LSNAxUY8rsIHY77CHgQ4dUDCBE&uact=5&oq=random+funny+pictures&gs_lp=EgNpbWciFXJhbmRvbSBmdW5ueSBwaWN0dXJlczIHECMYJxjJAjIGEAAYBxgeMgYQABgHGB4yBRAAGIAEMgUQABiABDIFEAAYgAQyBRAAGIAEMgUQABiABDIEEAAYHjIEEAAYHki3A1AAWABwAXgAkAEAmAEAoAEAqgEAuAEDyAEAmAIBoAIMmAMAiAYBkgcBMaAHALIHALgHAMIHAzMtMcgHCQ&sclient=img'
top_urls = get_images(wd, base_url)
