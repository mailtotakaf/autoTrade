from psycopg2 import Error
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.rktn.Login import login

import time
from selenium.webdriver.common.by import By
import psycopg2
from datetime import datetime
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select


display_width = 1900  # 1920
display_height = 1000  # 1080

today_date = datetime.now().date()
date_str = today_date.strftime('%Y-%m-%d')

rating_report_sql = ("select d.ticker from (SELECT c.ticker, CASE WHEN c.today <> 0 THEN ROUND(((b.new_price - c.today) / c.today * 100)::numeric, 0) "
                     "ELSE NULL END AS diff_per2 FROM hold_tickers a INNER JOIN reasonable_prices b ON a.ticker = b.ticker "
                     "LEFT OUTER JOIN yahoo_price c ON a.ticker = c.ticker where c.create_date = CURRENT_DATE and c.ticker ~ '[^0-9]' ORDER BY diff_per2 desc) d;")

# rating_report_sql = "select ticker from hold_tickers;"


def openchart(driver, ticker, x_position, y_position, width, height):
    new_window_handle = None
    original_window_handle = None
    try:
        time.sleep(1)
        # 元のウィンドウのハンドルを取得
        original_window_handle = driver.current_window_handle

        # 楽天ロゴを
        el = driver.find_element(By.CSS_SELECTOR, 'a[data-ratid="mem_pc_gnavi_rsec-logo"]')
        # 新しいタブで
        driver.execute_script("arguments[0].setAttribute('target', '_blank'); arguments[0].click();", el)
        # 新しいウィンドウのハンドルを取得
        new_window_handle = driver.window_handles[-1]
        # 新しいウィンドウに切り替える
        driver.switch_to.window(new_window_handle)
        # セレクトボックスを特定
        select_element = driver.find_element(By.NAME, "stoc-type-01")
        # セレクトボックスから米国株式を選択
        select = Select(select_element)
        select.select_by_value("1")  # value="1" が米国株式を示しています

        # rat_Pulldown_compIdイベントを手動で発火させる
        script = """
        dataLayer.push({'event': 'rat_SelectPull','rat_Pulldown_compId':'mem_pc_gnavi_switch-search_pulldown'})
        """
        driver.execute_script(script)

        # ticker入力
        el = driver.find_element(By.ID, "search-stock-01")
        el.send_keys(ticker)

        # 検索ボタンクリック
        el = driver.find_element(By.ID, "searchStockFormSearchBtn")
        el.click()
        time.sleep(1)

        # 「詳細チャートへ」ボタンクリック
        el = driver.find_element(By.ID, "pcm-002-4-btn")
        driver.execute_script("arguments[0].click();", el)
        time.sleep(1)

        open_chart(driver, x_position, y_position, width, height)
    except Exception as e:
        print('Error. ticker:', ticker)
        print(e)
    finally:
        # ベースウィンドウに切り替える
        driver.switch_to.window(new_window_handle)
        # ベースウィンドウを閉じる
        driver.close()
        # 元のウィンドウに戻る
        driver.switch_to.window(original_window_handle)


def get_index(driver, ticker, x_position, y_position, width, height):
    new_window_handle = None
    original_window_handle = None
    try:
        time.sleep(1)
        el = driver.find_element(By.CSS_SELECTOR, 'a[data-ratid="mem_pc_gnavi_market-top"]')
        el.click()
        time.sleep(1)
        # 元のウィンドウのハンドルを取得
        original_window_handle = driver.current_window_handle

        link = None
        if ticker == 1:
            # "NYダウ" というテキストを持つリンクを見つけてクリック
            link = driver.find_element(By.XPATH, "//table[@class='tbl-data-01']//a[text()='NYダウ']")
        elif ticker == 2:
            link = driver.find_element(By.XPATH, "//table[@class='tbl-data-01']//a[text()='ナスダック総合指数']")
        elif ticker == 3:
            link = driver.find_element(By.XPATH, "//table[@class='tbl-data-01']//a[text()='S&P500指数']")
        # 新しいタブで
        driver.execute_script("arguments[0].setAttribute('target', '_blank'); arguments[0].click();", link)
        # 新しいウィンドウのハンドルを取得
        new_window_handle = driver.window_handles[-1]
        # 新しいウィンドウに切り替える
        driver.switch_to.window(new_window_handle)

        open_chart(driver, x_position, y_position, width, height)
    except Exception as e:
        print('Error. ticker:', ticker)
        print(e)
    finally:
        # ベースウィンドウに切り替える
        driver.switch_to.window(new_window_handle)
        # ベースウィンドウを閉じる
        driver.close()
        # 元のウィンドウに戻る
        driver.switch_to.window(original_window_handle)


def open_chart(driver, x_position, y_position, width, height):
    # テクニカルチャートクリック
    el = driver.find_element(By.XPATH, "//input[@type='image' and @alt='テクニカルチャート']")
    driver.execute_script("arguments[0].click();", el)

    # チャートウィンドウのハンドルを取得
    chart_window_handle = driver.window_handles[-1]
    # チャートウィンドウに切り替える
    driver.switch_to.window(chart_window_handle)
    # 時計プルダウンクリック
    driver.find_element(By.ID, 'mi-period').click()
    # 1分足ラジオチェック
    driver.find_element(By.NAME, '1').click()
    # シフト移動量を大きくするために画面最大化
    driver.maximize_window()
    # 時計プルダウンを消すためにクリックする
    driver.find_element(By.ID, "chartbox").click()
    # chartbox要素を探します
    chartbox = driver.find_element(By.ID, "chartbox")
    # ActionChainsを使用して要素をクリックしてドラッグします
    actions = ActionChains(driver)
    # チャートウィンドウのサイズを変更
    driver.set_window_size(width, height)
    # JavaScriptを使って少しスクロール
    driver.execute_script("window.scrollBy(0, 100);")
    # 再シフト調整（ウィンドウ最小だと移動量50くらいが限度なので9回くらい必要）
    for i in range(9):
        actions.click_and_hold(chartbox).move_by_offset(-50, 0).release().perform()
    # ウィンドウの位置を移動するJavaScriptコード
    script = f'''
        window.moveTo({x_position}, {y_position});
    '''
    # ウィンドウにJavaScriptコードを実行する
    driver.execute_script(script)


def loop_tickers(ticker_list):
    num_of_line = 2
    list_len = len(ticker_list)
    if list_len > 24:
        num_of_line = 3

    # 横に並ぶ数
    remainder = list_len % num_of_line
    x_cnt = round(list_len / num_of_line) + remainder
    # 横幅
    width = round(display_width / x_cnt)
    # 高さ
    height = max(400, round(display_height / num_of_line))
    x_position = 0
    y_position = 0

    driver = login()
    if list_len > 0:
        x_idx = 0
        for idx, ticker in enumerate(ticker_list):
            if x_cnt <= x_idx:  # 改行
                x_position = 0
                x_idx = 0
                y_position = y_position + height

            x_position = width * x_idx
            x_idx += 1
            if ticker in [1,2,3]:
                # インデックス
                get_index(driver, ticker, x_position, y_position, width, height)
            else:
                openchart(driver, ticker, x_position, y_position, width, height)

        time.sleep(60 * 60 * 6)  # 9字から15時まで6時間
    else:
        print("loop_tickers error.")


def postgres():
    global cursor, connector
    try:
        connector = psycopg2.connect('postgresql://{user}:{password}@{host}:{port}/{dbname}'.format(
            user="postgres",
            password="postgres",
            host="localhost",
            port="5432",
            dbname="postgres"))

        cursor = connector.cursor()
        return cursor
    except(Exception, Error) as error:
        print("Error: DB connection.", error)


def get_ticker_list(sql):
    try:
        cursor = postgres()
        cursor.execute(sql)
        ticker_list = cursor.fetchall()
        ticker_list = [item[0] for item in ticker_list]
        cursor.close()
        connector.close()
        return ticker_list
    except(Exception, Error) as error:
        print("Error: get_ticker_list.", error)
    

class OpenChats:
    def __init__(self):
        ticker_list = get_ticker_list(rating_report_sql)
        # ticker_list = ['NVTS']
        ticker_list = ticker_list + [1,2,3]  # インデックス追加
        print("ticker_list:", ticker_list)
        loop_tickers(ticker_list)


my_obj = OpenChats()

# TODO: reasonable_pricesのデータがinvester.comから取れてないとOpenChartsできない