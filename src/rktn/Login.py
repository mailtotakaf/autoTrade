# webdriver_managerで自動的にSeleniumとChromeバージョンを一致させる
# https://scr.marketing-wizard.biz/dev/webdriver-manager-selenium-chrome

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
from psycopg2 import Error
from src.db.postgres import get_cursor


def login():
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get('https://www.rakuten-sec.co.jp/ITS/V_ACT_Login.html')

    # https://stackoverflow.com/questions/71097378/selenium-common-exceptions-invalidargumentexception-message-invalid-argument
    el = driver.find_element(By.ID, 'form-login-id')
    el.clear()
    el.send_keys('DummyDi')

    el = driver.find_element(By.ID, 'form-login-pass')
    el.send_keys('DummySsap')

    # https://qiita.com/shiratatsu/items/9f390970e38b66f0c290
    el = driver.find_element(By.NAME, 'loginform')
    el.submit()

    driver.maximize_window()
    return driver