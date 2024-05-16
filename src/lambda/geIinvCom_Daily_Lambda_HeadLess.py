from decimal import Decimal

import boto3
import random
import time

from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import undetected_chromedriver as uc

# ヘッドレスモードを有効にするためのオプションを設定
chrome_options = Options()
chrome_options.add_argument("--headless")  # ヘッドレスモードで実行
chrome_options.add_argument("--disable-gpu")  # 一部の環境で必要
chrome_options.add_argument("--no-sandbox")  # サンドボックスを無効化（Docker環境などで必要な場合）
chrome_options.add_argument("--disable-dev-shm-usage")  # 共有メモリ使用を無効化（リソースが少ない環境での問題を回避）
# ChromeDriverManagerでドライバーを管理
service = ChromeService(ChromeDriverManager().install())

today_date = datetime.now().date()
date_str = today_date.strftime('%Y-%m-%d')

chrome_driver_version = '126.0.6478.128'

dynamodb = boto3.resource('dynamodb')

investerComPass = "YourPass"
investerComId = "YourId"
rktnId = "YourId"
rktnPass = "YourPass"


def invester_login():
    print("invester_login start")
    options = uc.ChromeOptions()
    options.add_argument('--headless')  # ヘッドレスモードを有効化
    options.add_argument('--disable-gpu')  # GPUを無効化
    options.add_argument('--no-sandbox')  # サンドボックスを無効化 (必要に応じて)
    options.add_argument('--disable-dev-shm-usage')  # /dev/shmの使用を無効化 (メモリ不足の問題を解消するため)
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36") #dummy
    driver = uc.Chrome(service=ChromeService(ChromeDriverManager(driver_version=chrome_driver_version).install()), options=options)

    driver.get('https://jp.investing.com/')
    driver.maximize_window()

    time.sleep(rand_from(1.0))
    el = driver.find_element(By.CSS_SELECTOR,'button[data-test="login-btn"]')
    driver.execute_script("arguments[0].click();", el)
    time.sleep(rand_from(1.0))
    el = driver.find_element(By.CSS_SELECTOR, "button.social-auth-button_button__4UcrI.social-auth-button_icon__0fp5Q.social-auth-button_email__emi7S")
    driver.execute_script("arguments[0].click();", el)
    time.sleep(rand_from(1.0))

    el = driver.find_element(By.CSS_SELECTOR,"div.input_wrapper__WaPd4 input.input_input__WivCD")
    el.send_keys(investerComId)
    time.sleep(rand_from(1.0))

    el = driver.find_element(By.CLASS_NAME, 'input_password__2qtWo')
    el.send_keys(investerComPass)
    time.sleep(rand_from(1.0))

    login_button = driver.find_element(By.CLASS_NAME, 'signin_primaryBtn__54rGh')
    driver.execute_script("arguments[0].click();", login_button)
    time.sleep(rand_from(1.0))
    print("invester_loginしたっしょ")
    return driver


def get_ratings(ticker_list):
    driver = invester_login()
    for ticker in ticker_list:
        reasonable_price = None
        try:
            p = get_rating(driver, ticker)
            if ',' in p:
                p = get_rating(driver, ticker).replace(",", "")
            reasonable_price = float(p)
            # reasonable_price = "12345"
        except Exception as e:
            print(f"get_rating error: {e}")
        if reasonable_price is not None:
            old_tuple = get_old(ticker)
            insert_db(ticker, reasonable_price, old_tuple)


def insert_db(ticker, reasonable_price, old_tuple):
    print("DB登録")
    old_price = 0
    old_date = None
    if old_tuple:
        old_price = old_tuple['new_price']
        old_date = old_tuple['new_date']

    print("old_price:", old_price)
    print("reasonable_price:", reasonable_price)

    if old_price != reasonable_price:
        # 新規登録 or 更新
        new_price = reasonable_price
        try:
            # テーブルの指定
            table = dynamodb.Table('reasonable_prices')
            # 現在の日付を取得
            current_date = datetime.now().date().isoformat()  # 'YYYY-MM-DD'形式

            item = {
                'ticker': ticker,
                'new_price': Decimal(str(new_price)),
                'new_date': current_date,
                'old_price': Decimal(str(old_price)),
                'old_date': old_date
            }
            # データの挿入
            table.put_item(Item=item)

            print("更新しますた")
        except Exception as e:
            print("insert_dbエラー.", e)
    else:
        print("Unchanged, do not update.")


def get_old(ticker):
    print("get_old start.")
    # テーブルの指定
    table = dynamodb.Table('reasonable_prices')
    try:
        # アイテムの取得
        response = table.get_item(
            Key={'ticker': ticker},
            ProjectionExpression='new_price, new_date'  # 取得する属性を指定
        )
        # 取得したデータの表示
        item = response.get('Item')
        return item
    except Exception as e:
        print("get_oldエラー.", e)


def get_rating(driver, ticker):
    print("get_rating start.")
    time.sleep(rand_from(1.0))
    # 検索するTicker入力
    search_input = None
    try:
        time.sleep(rand_from(1.0))
        search_input = driver.find_element(By.CSS_SELECTOR, 'input[name="q"]')
        driver.execute_script("arguments[0].click();", search_input)

        search_input.send_keys(str(ticker))
        time.sleep(rand_from(1.0))

        # 一番上に表示されたやつクリック
        el = driver.find_element(By.CLASS_NAME, 'mainSearch_symbol__YMUvc')
        driver.execute_script("arguments[0].click();", el)
        print("一番上に表示されたやつクリックしたぽよ")

        # 適正価格を取得
        # el = driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/div[1]/div[2]/div[1]/div[1]/div[3]/div[2]/div[1]/div/div[2]/div[1]')
        print("implicitly_wait(10)してる")
        driver.implicitly_wait(30)
        print("implicitly_wait(10)おわた")

        # ページタイトルを確認
        title = driver.title
        print("title:", title)

        # 遷移先のページで特定の要素を探す
        element = driver.find_element(By.CSS_SELECTOR, "h1")
        print("要素が見つかりました:", element.text)

        # スクリーンショットを撮影して保存
        screenshot_path = "screenshot.png"
        driver.save_screenshot(screenshot_path)

        el = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="__next"]/div[2]/div[1]/div[2]/div[1]/div[1]/div[3]/div[2]/div[1]/div/div[2]/div[1]'))
        )
        print("WebDriverWaitおわた")
        price = el.text
        print("適正価格：", price)
        return price
    except Exception as e:
        print("get_rating Exception:", e)
        # search_input.clear()
        # print("search_input.clear()おわた")

def rand_from(from_val = 1.0):
    return random.uniform(from_val, from_val + 2.0)


def rktn_login():
    # WebDriverを起動
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # driver = webdriver.Chrome()
    driver.get('https://www.rakuten-sec.co.jp/ITS/V_ACT_Login.html')

    el = driver.find_element(By.ID, 'form-login-id')
    el.clear()
    el.send_keys(rktnId)

    el = driver.find_element(By.ID, 'form-login-pass')
    el.send_keys(rktnPass)

    el = driver.find_element(By.NAME, 'loginform')
    el.submit()
    return driver


def get_owned_tickers_jp(driver):
    time.sleep(2)
    el = driver.find_element(By.CLASS_NAME, 'pcmm-btlk-link')
    driver.execute_script('arguments[0].click();', el)
    time.sleep(2)

    divElem = driver.find_element(By.ID, 'table_possess_data')
    tableElem = divElem.find_element(By.TAG_NAME, "table")
    trElem = tableElem.find_elements(By.TAG_NAME, "tr")
    ticker_list = []
    for tr in trElem:
        try:
            ticker = tr.find_elements(By.CSS_SELECTOR, ".align-C.R0")
            print("ticker:", ticker[0].text)
            ticker_str = ticker[0].text
            ticker_list.append(ticker_str)
        except Exception as e:
            print("error:", e)
    return ticker_list


def insert_hold_tickers(ticker_list):
    print("insert_hold_tickers登録")
    # テーブルの指定
    table = dynamodb.Table('hold_tickers')

    try:
        # テーブルの全アイテムをスキャン
        response = table.scan()

        # アイテムを一つずつ削除
        with table.batch_writer() as batch:
            for item in response['Items']:
                batch.delete_item(
                    Key={
                        'ticker': item['ticker']
                    }
                )

        # itemsリストに変換
        items = [{'ticker': ticker} for ticker in ticker_list]
        # バッチライターを使用してデータを一括挿入
        with table.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)

    except Exception as e:
        print("insert_hold_tickers登録エラー.", e)


class GetInvComDailyLambda:
    def __init__(self):
        start = time.time()
        # driver = rktn_login()
        # owned_tickers = get_owned_tickers_jp(driver)
        # owned_tickers = ['6855', '7267', 'BMO', 'PRU', 'DXCM', 'NKE', 'NVTS', 'MBLY', 'ALTM', 'BBY', 'CVX']
        # owned_tickers = ['NVTS', 'MBLY', 'ALTM', 'BBY', 'CVX']
        owned_tickers = ['6855', '7267']

        # insert_hold_tickers(owned_tickers)

        if len(owned_tickers):
            get_ratings(owned_tickers)

        end = time.time()
        processing_time = end - start
        print("processing_time:", processing_time)

my_obj = GetInvComDailyLambda()