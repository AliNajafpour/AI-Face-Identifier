import time
import os
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def search(image_path):
    options = Options()
    options.add_argument("--start-maximized")

    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    try:
        driver.get("https://lens.google.com/")
        time.sleep(random.uniform(2, 5))
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
        time.sleep(random.uniform(1, 3))

        try:
            captcha = driver.find_element(By.XPATH, '//iframe[contains(@src, "recaptcha")]')
            print()
            driver.quit()
            return None
        except:
            pass

        upload_input = driver.find_element(By.XPATH, '//input[@type="file"]')
        if not os.path.exists(image_path):
            print(f"{image_path}")
            driver.quit()
            return None
        upload_input.send_keys(os.path.abspath(image_path))

        time.sleep(random.uniform(5, 10))

        result = driver.current_url
        print(f"{result}")
        return result

    finally:
        driver.quit()

path = './test/images.png'
search(path)