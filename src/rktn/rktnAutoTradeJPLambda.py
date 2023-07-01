from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
import boto3
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup
from tempfile import mkdtemp

# 本番開始：2023/12/25：実現損益 -225,733円から
buy_strategy_dict = {
    "9994": 1.003,
    "9432": 1.002,
    "3628": 1.007,
}

sell_strategy_dict = {
    "9994": 1.003,
    "9432": 1.002,
    "3628": 1.007,
}

zaraba_strategy_dict = {
    "9994": 0.5,
    "9432":
}


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
    driver.get("https://www.rakuten-sec.co.jp/ITS/V_ACT_Login.html")
    driver = owned_auto_sell(driver)
    auto_buy(driver)
    print("END---------------------------------処理時間：", time.time() - start)


def owned_auto_sell(driver):
    print("owned_auto_sell calling.")
    time.sleep(1)
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
    print("login OK.")
    time.sleep(4)

    try:
        # 保有商品一覧
        el = driver.find_element(By.CLASS_NAME, 'pcmm-btlk-link')
        driver.execute_script('arguments[0].click();', el)
        time.sleep(4)
        print("owned list page.")

        divElem = driver.find_element(By.ID, 'table_possess_data')
        tableElem = divElem.find_element(By.TAG_NAME, "table")
        trElem = tableElem.find_elements(By.TAG_NAME, "tr")

        for tr in trElem[3:]:
            ticker = ""
            try:
                # ---------------------ticker
                row = tr.find_elements(By.CSS_SELECTOR, ".align-C.R0")
                if len(row) == 0:
                    # print("len(row) == 0. continue.")
                    continue
                ticker = row[0].text
                print("ticker:", ticker)

                lines = tr.text.split('\n')
                # ------------------現在値
                now_price_str = lines[3].replace("円", "")
                now_price_str = now_price_str.replace(",", "")
                now_price = float(now_price_str)

                # 保有数量
                amount_str = lines[2]
                matches = re.search(r'\b\d+\b', amount_str)
                amount = int(matches[0])

                memory_price = 0
                update_price = 0
                res = get_updown_dynamo(ticker)
                if res is not None:
                    memory_price = float(res['memory_price']['N'])

                if now_price < memory_price:
                    update_price = now_price
                else:
                    update_price = memory_price

                row_dict = {
                    "ticker": ticker,
                    "memory_price": update_price,
                    "amount": amount,
                }
                upsert_updown(row_dict)

                # -----------------売り判定
                if (now_price - memory_price) > zaraba_strategy_dict[ticker]:
                    # 銘柄リンク押下
                    link_elem = tr.find_element(By.TAG_NAME, "a")
                    link_url = link_elem.get_attribute("href")
                    driver.execute_script("window.open('{}', '_blank');".format(link_url))
                    # 新しいウィンドウへの切り替え
                    driver.switch_to.window(driver.window_handles[1])
                    auto_sell_one(driver, ticker, amount, now_price)
                    # 元のウィンドウに戻る
                    driver.switch_to.window(driver.window_handles[0])

            except Exception as e:
                print(f"error at owned_auto_sell. ticker: {ticker} / e: {e}")
    except Exception as e:
        print(f"とりあえず保有一覧ない場合のエラー握り潰し")
    return driver


def get_updown_dynamo(ticker):
    print("get_updown_dynamo calling.")
    try:
        dynamodb = boto3.client('dynamodb')
        options = {
            'TableName': 'UpDown',
            'Key': {
                'ticker': {'S': str(ticker)},
            }
        }
        ret = dynamodb.get_item(**options)
        item = ret.get('Item')
        if item:
            # print(f"get_updown_dynamo response. item: {item}")
            return item
        else:
            print(f"get_updown_dynamo no result. return None.")
            return None
    except Exception as e:
        print(f"Error at get_updown_dynamo: ticekr: {ticker} / e:{e}")
        return None


def upsert_updown(row_dict):
    print("upsert_updown calling.")
    try:
        unix_time = int(time.time())
        client = boto3.client('dynamodb')
        client.put_item(
            TableName="UpDown",
            Item={
                "ticker": {"S": row_dict['ticker']},
                "memory_price": {"N": str(row_dict['memory_price'])},
                "amount": {"N": str(row_dict['amount'])},
                "unix_time": {"N": str(unix_time)},
                "jp_time": {"S": str(jp_time(unix_time))},
            }
        )
        print(f"upsert_updown success. ticker: {row_dict['ticker']}")
    except Exception as e:
        print(f"Error: at upsert_updown. ticker: {row_dict['ticker']} / e: {e}")


def jp_time(unix_time):
    utc_time = datetime.utcfromtimestamp(float(unix_time))
    jp_time = utc_time.replace(tzinfo=timezone.utc) + timedelta(hours=9)
    return jp_time


def auto_sell_one(driver, ticker, amount, now_price):
    try:
        print("auto_sell_one calling.")
        # 個別銘柄画面に遷移
        time.sleep(2)
        # 売り注文ボタン
        sell_button_xpath = '//a[@class="pcmm_jpstk-btlk-sell pcmm_jpstk-btlk-filled pcmm_jpstk-btlk--xs pcmm_jpstk-btlk--block"]'
        el = driver.find_element(By.XPATH, sell_button_xpath)
        driver.execute_script("arguments[0].click();", el)

        # 対象の売りボタン
        link_xpath = '//a[contains(@href, "/ord") and contains(@href, "dscrCd=' + ticker + '")]'
        el = driver.find_element(By.XPATH, link_xpath)
        driver.execute_script("arguments[0].click();", el)
        # 数量
        el = driver.find_element(By.ID, 'orderValue')
        el.clear()
        el.send_keys(amount)
        # # 成行ラジオボタン
        # el = driver.find_element(By.ID, 'priceMarket')
        # driver.execute_script("arguments[0].click();", el)
        print(f"指値セットnow_price:${now_price}円")
        el = driver.find_element(By.ID, 'marketOrderPrice')
        el.clear()
        el.send_keys(now_price)

        el = driver.find_element(By.NAME, "password")
        el.clear()
        el.send_keys("4105")
        el = driver.find_element(By.ID, 'ormit_checkbox')
        driver.execute_script("arguments[0].click();", el)
        # 注文ボタン
        el = driver.find_element(By.ID, 'ormit_sbm')
        driver.execute_script("arguments[0].click();", el)
        time.sleep(2)
        # dynamoのamountを0にする
        row_dict = {
            "ticker": ticker,
            "memory_price": now_price,
            "amount": 0,
        }
        upsert_updown(row_dict)

        print(f"auto_sell_one success: ticker: {ticker}")
        # 画面クローズ
        driver.close()
    except Exception as e:
        print(f'Error at auto_sell_one. ticker: {ticker}/ e: {e}')
        # 画面クローズ
        driver.close()


def auto_buy(driver):
    print("auto_buy calling.")
    try:
        element = driver.find_element(By.XPATH, '//a[@data-ratid="mem_pc_gnavi_rsec-logo"]')
        driver.execute_script("arguments[0].click();", element)
        # お気に入り
        time.sleep(2)
        print("お気に入り一覧クリック前")
        element = driver.find_element(By.XPATH, '//a[@class="pcmm-btlk-link pcmm-btlk--sm"]')
        driver.execute_script("arguments[0].click();", element)
        time.sleep(2)
        print("テーブルのHTMLを取得まえ")
        table_html = driver.find_element(By.XPATH, "//table[@class='tbl-data-01']").get_attribute('outerHTML')
        soup = BeautifulSoup(table_html, 'html.parser')
        print("テーブルから行を取得まえ")
        rows = soup.find('tbody').find_all('tr')
        print("各行ごとにデータを取得します")
        for row in rows[1:]:
            try:
                # セルのデータを取得
                cells = row.find_all(['th', 'td'])
                ticker = cells[1].get_text(strip=True)
                if ticker == "":
                    # print("ticker == "". continue.")
                    continue
                now_price = cells[7].get_text(strip=True)
                print("ticker：", ticker)
                # print("name：", cells[2].get_text(strip=True))
                now_price = re.search(r'(\d[\d,]*\.\d+|\d[\d,]*)', now_price).group()
                now_price = now_price.replace(",", "")
                now_price = float(now_price)
                print("現在値：", now_price)
                res = get_updown_dynamo(ticker)
                row_dict = {
                    "ticker": ticker,
                    "memory_price": now_price,
                    "amount": 0,
                }
                # 保有していない場合のみ処理
                if res is None:
                    print("新規登録")
                    upsert_updown(row_dict)
                else:
                    res_amount = int(res['amount']['N'])
                    if res_amount == 0:
                        print("現在持っているamountは0でつ")
                        memory_price = float(res['memory_price']['N'])
                        if (memory_price - now_price) > zaraba_strategy_dict[ticker]:
                            print("買うっす")
                            link = cells[3].find("a")
                            href_value = link.get('href')
                            driver.execute_script("window.open('{}', '_blank');".format(href_value))
                            print("個別銘柄の新しいウィンドウへの切り替え")
                            driver.switch_to.window(driver.window_handles[1])
                            buy_one(driver, ticker, now_price)
                            print("無事買えた？のでdynamo更新")
                            row_dict['amount'] = 100
                            upsert_updown(row_dict)

            except Exception as e:
                print(f"error at auto_buy for.:{e}")

    except Exception as e:
        print(f"error at auto_buy.: {e}")


def buy_one(driver, ticker, now_price):
    print("buy_one calling. ticker:", ticker)
    try:
        time.sleep(2)
        print("買いボタン押下")
        el = driver.find_element(By.CSS_SELECTOR,
                                 'a[class="pcmm_jpstk-btlk-buy pcmm_jpstk-btlk-filled pcmm_jpstk-btlk--xs pcmm_jpstk-btlk--block"]')
        driver.execute_script("arguments[0].click();", el)
        time.sleep(2)
        print("数量入力")
        el = driver.find_element(By.ID, 'orderValue')
        el.clear()
        el.send_keys('100')
        # print("成行ラジオボタン")
        # el = driver.find_element(By.ID, 'priceMarket')
        # driver.execute_script("arguments[0].click();", el)
        print(f"指値セットnow_price:${now_price}円")
        el = driver.find_element(By.ID, 'marketOrderPrice')
        el.clear()
        el.send_keys(now_price)

        el = driver.find_element(By.NAME, "password")
        el.clear()
        el.send_keys("4105")
        el = driver.find_element(By.ID, 'ormit_checkbox')
        driver.execute_script("arguments[0].click();", el)
        el = driver.find_element(By.ID, 'ormit_sbm')
        driver.execute_script("arguments[0].click();", el)
        time.sleep(2)
        # 画面クローズ
        driver.close()
        # 元のウィンドウに戻る
        print("buy_one success. ticker:", ticker)
        driver.switch_to.window(driver.window_handles[0])
    except Exception as e:
        print(f'buy_one Error. ticker: {ticker} / e: {e}')
