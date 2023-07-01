# webdriver_managerで自動的にSeleniumとChromeバージョンを一致させる
# https://scr.marketing-wizard.biz/dev/webdriver-manager-selenium-chrome
from telnetlib import EC

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
from psycopg2 import Error
from src.db.postgres import get_cursor
from resources import settings

def get_owned_tickers():
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get('https://www.rakuten-sec.co.jp/ITS/V_ACT_Login.html')

    # https://stackoverflow.com/questions/71097378/selenium-common-exceptions-invalidargumentexception-message-invalid-argument
    el = driver.find_element(By.ID, 'form-login-id')
    el.clear()
    el.send_keys(settings.RKTN_ID)

    el = driver.find_element(By.ID, 'form-login-pass')
    el.send_keys(settings.RKTN_PASS)

    # https://qiita.com/shiratatsu/items/9f390970e38b66f0c290
    el = driver.find_element(By.NAME, 'loginform')
    el.submit()

    time.sleep(2)
    el = driver.find_element(By.CLASS_NAME, 'pcmm-btlk-link')
    # el = driver.find_element(By.XPATH, "//span[text()='保有商品一覧']")
    # el = driver.find_element(By.XPATH, '//span[text()="\\u4fdd\\u6709\\u5546\\u54c1\\u4e00\\u89a7"]')
    # el = driver.find_element(By.CLASS_NAME, 'pcmm-btlk__text')
    # el = WebDriverWait(driver, 10).until(
    #     EC.presence_of_element_located((By.XPATH, '//span[text()="\\u4fdd\\u6709\\u5546\\u54c1\\u4e00\\u89a7"]'))
    # )
    # el.click()
    driver.execute_script('arguments[0].click();', el)
    time.sleep(2)

    divElem = driver.find_element(By.ID, 'table_possess_data')
    tableElem = divElem.find_element(By.TAG_NAME, "table")
    trElem = tableElem.find_elements(By.TAG_NAME, "tr")
    ticker = ""
    ticker_list = []
    for tr in trElem:
        try:
            ticker = tr.find_elements(By.CSS_SELECTOR, ".align-C.R0")
            ticker_str = ""
            print("ticker:", ticker[0].text)
            if ticker[0].text.isdecimal():
                ticker_str = ticker[0].text + ".T"
            else:
                ticker_str = ticker[0].text
                
            ticker_list.append(ticker_str)
        except Exception as e:
            print("error:", e)

    # print("ticker_list:", ticker_list)
    return ticker_list


class Rktn:
    def __init__(self):
        owned_ticker_list = get_owned_tickers()
        print("owned_ticker_list:", owned_ticker_list)
        self.insertResult(owned_ticker_list)

    def insertResult(self, owned_ticker_list):
        cursor, connector = get_cursor()
        try:
            # 全false
            cursor.execute("update ticker_jp set owned = false;")
            connector.commit()
            # update
            placeholders = ', '.join(['%s'] * len(owned_ticker_list))
            sql = f"UPDATE ticker_jp SET owned = true WHERE ticker IN ({placeholders})"
            cursor.execute(sql, owned_ticker_list)
            connector.commit()
            print("update success.")
        except(Exception, Error) as error:
            print("Error: DB connection.", error)
        connector.close()


# クラスのインスタンスを作成
my_obj = Rktn()
