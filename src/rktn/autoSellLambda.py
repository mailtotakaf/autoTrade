import time
from selenium.webdriver.common.by import By
from selenium import webdriver
from tempfile import mkdtemp

def handler(event=None, context=None):
    print("START---------------------------------")
    start = time.time()
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
    driver = login(driver)
    owned_ticker_list = get_owned_tickers(driver)
    print("owned_ticker_list:", owned_ticker_list)
    loop_sell(owned_ticker_list, driver)
    print("END---------------------------------処理時間：", time.time() - start)


def get_owned_tickers(driver):
    print("get_owned_tickers calling.")
    el = driver.find_element(By.CLASS_NAME, 'pcmm-btlk-link')
    el.click()
    time.sleep(2)

    divElem = driver.find_element(By.ID, 'table_possess_data')
    tableElem = divElem.find_element(By.TAG_NAME, "table")
    trElem = tableElem.find_elements(By.TAG_NAME, "tr")
    ticker = ""
    ticker_list = []
    for tr in trElem:
        try:
            ticker = tr.find_elements(By.CSS_SELECTOR, ".align-C.R0")
            ticker_str = ticker[0].text
            ticker_list.append(ticker_str)
        except Exception as e:
            print("error:", e)

    return ticker_list


def auto_sell_one(driver, ticker):
    print("auto_sell_one calling.")
    try:
        time.sleep(2)
        el = driver.find_element(By.CSS_SELECTOR, 'a[data-ratid="mem_pc_gnavi_domestic-top"]')
        driver.execute_script("arguments[0].click();", el)
        time.sleep(2)
        # 売り一覧へ
        el = driver.find_element(By.ID, "jp-stk-top-btn-sell")
        driver.execute_script("arguments[0].click();", el)
        print("売り一覧表示")
        time.sleep(2)
        # 対象の売りボタン
        # ticker = ticker[:-2]
        link_xpath = '//a[contains(@href, "/ord") and contains(@href, "dscrCd=' + ticker + '")]'
        el = driver.find_element(By.XPATH, link_xpath)
        driver.execute_script("arguments[0].click();", el)
        print("対象の売りボタン押下")
        # 数量
        el = driver.find_element(By.ID, 'orderValue')
        el.clear()
        el.send_keys('100')
        # 成行ラジオボタン
        el = driver.find_element(By.ID, 'priceMarket')
        driver.execute_script("arguments[0].click();", el)
        el = driver.find_element(By.NAME, "password")
        el.clear()
        el.send_keys("4105")
        el = driver.find_element(By.ID, 'ormit_checkbox')
        driver.execute_script("arguments[0].click();", el)
        el = driver.find_element(By.ID, 'ormit_sbm')
        driver.execute_script("arguments[0].click();", el)
        time.sleep(2)
        # メイン画面へ戻る
        print(f"売りました。：{ticker}. return to main.")
        el = driver.find_element(By.CLASS_NAME, "pcm-gl-logo-img")
        driver.execute_script("arguments[0].click();", el)
    except Exception as e:
        print('Error. ticker:', ticker)
        print(e)


def loop_sell(sell_list, driver):
    if len(sell_list) > 0:
        for ticker in sell_list:
            if ticker != "9432":
                auto_sell_one(driver, ticker)
            else:
                print("pass:", ticker)
    else:
        print("nothing to sell.")


def login(driver):
    print("login calling.")
    driver.get('https://www.rakuten-sec.co.jp/ITS/V_ACT_Login.html')
    time.sleep(1)

    el = driver.find_element(By.ID, 'form-login-id')
    el.clear()
    el.send_keys('DummyDi')

    el = driver.find_element(By.ID, 'form-login-pass')
    el.send_keys('DummySsap')

    el = driver.find_element(By.NAME, 'loginform')
    el.submit()

    driver.maximize_window()
    print("login OK.")
    time.sleep(2)

    return driver


# class AutoSell:
#     def __init__(self):
#         driver = login()
#         owned_ticker_list = get_owned_tickers(driver)
#         print("owned_ticker_list:", owned_ticker_list)
#         loop_sell(owned_ticker_list, driver)
#
#
# my_obj = AutoSell()
