import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def search(image_path):
    options = Options()
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get("https://lens.google.com/")

    time.sleep(3)

    upload_input = driver.find_element(By.XPATH, '//input[@type="file"]')
    upload_input.send_keys(os.path.abspath(image_path))

    time.sleep(7)

    result = driver.current_url
    print(result)

    return result


path = './test/images.png'
search(path)