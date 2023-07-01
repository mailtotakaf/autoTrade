# webdriver_managerで自動的にSeleniumとChromeバージョンを一致させる
# https://scr.marketing-wizard.biz/dev/webdriver-manager-selenium-chrome
# from selenium import webdriver
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
import time
# from resources import settings
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service as ChromeService
from selenium import webdriver
from tempfile import mkdtemp
from selenium.webdriver.common.by import By


def handler(event=None, context=None):
    options = webdriver.ChromeOptions()
    service = webdriver.ChromeService("/opt/chromedriver")

    options.binary_location = '/opt/chrome/chrome'
    options.add_argument("--headless=new")
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280x1696")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--no-zygote")
    options.add_argument(f"--user-data-dir={mkdtemp()}")
    options.add_argument(f"--data-path={mkdtemp()}")
    options.add_argument(f"--disk-cache-dir={mkdtemp()}")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument('--lang=ja_JP.UTF-8')

    driver = webdriver.Chrome(options=options, service=service)
    driver.get("https://www.rakuten-sec.co.jp/ITS/V_ACT_Login.html")

    owned_ticker_list = get_owned_tickers(driver)
    print("owned_ticker_list:", owned_ticker_list)


def get_owned_tickers(driver):
    print("get_owned_tickers calling.")
    time.sleep(2)
    # options = Options()
    # options.add_argument('--headless')
    # driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    # driver = webdriver.Chrome(service=ChromeService(), options=options)
    # driver = webdriver.Chrome(service=service, options=options)
    # driver.get('https://www.rakuten-sec.co.jp/ITS/V_ACT_Login.html')

    # https://stackoverflow.com/questions/71097378/selenium-common-exceptions-invalidargumentexception-message-invalid-argument
    el = driver.find_element(By.ID, 'form-login-id')
    el.clear()
    # el.send_keys(settings.RKTN_ID)
    el.send_keys("DummyDi")

    el = driver.find_element(By.ID, 'form-login-pass')
    # el.send_keys(settings.RKTN_PASS)
    el.send_keys("DummySsap")

    # https://qiita.com/shiratatsu/items/9f390970e38b66f0c290
    el = driver.find_element(By.NAME, 'loginform')
    el.submit()
    print("login OK 4.")
    time.sleep(1)

    el = driver.find_element(By.CLASS_NAME, 'pcmm-btlk-link')
    # el = driver.find_element(By.XPATH, "//span[text()='保有商品一覧']")
    # el = driver.find_element(By.XPATH, '//span[text()="\\u4fdd\\u6709\\u5546\\u54c1\\u4e00\\u89a7"]')
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

# def insertResult(owned_ticker_list):
#     cursor, connector = get_cursor()
#     try:
#         # 全false
#         cursor.execute("update ticker_jp set owned = false;")
#         connector.commit()
#         # update
#         placeholders = ', '.join(['%s'] * len(owned_ticker_list))
#         sql = f"UPDATE ticker_jp SET owned = true WHERE ticker IN ({placeholders})"
#         cursor.execute(sql, owned_ticker_list)
#         connector.commit()
#         print("update success.")
#     except(Exception, Error) as error:
#         print("Error: DB connection.", error)
#     connector.close()

# class Rktn:
#     def __init__(self):
# def handler(event=None, context=None):
#     owned_ticker_list = get_owned_tickers()
#     print("owned_ticker_list:", owned_ticker_list)
# self.insertResult(owned_ticker_list)

# def insertResult(self, owned_ticker_list):
#     cursor, connector = get_cursor()
#     try:
#         # 全false
#         cursor.execute("update ticker_jp set owned = false;")
#         connector.commit()
#         # update
#         placeholders = ', '.join(['%s'] * len(owned_ticker_list))
#         sql = f"UPDATE ticker_jp SET owned = true WHERE ticker IN ({placeholders})"
#         cursor.execute(sql, owned_ticker_list)
#         connector.commit()
#         print("update success.")
#     except(Exception, Error) as error:
#         print("Error: DB connection.", error)
#     connector.close()


# クラスのインスタンスを作成
# my_obj = Rktn()
