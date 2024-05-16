from selenium import webdriver
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
import os

load_dotenv()
rktnId = os.getenv("RKTN_ID")
rktnPass = os.getenv("RKTN_PW")
def login():
    driver = webdriver.Chrome()
    driver.get('https://www.rakuten-sec.co.jp/ITS/V_ACT_Login.html')

    el = driver.find_element(By.ID, 'form-login-id')
    el.clear()
    el.send_keys(rktnId)

    el = driver.find_element(By.ID, 'form-login-pass')
    el.send_keys(rktnPass)

    el = driver.find_element(By.NAME, 'loginform')
    el.submit()

    driver.maximize_window()
    return driver