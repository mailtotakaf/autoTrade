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

display_width = 1900  # 1920
display_height = 1000  # 1080

today_date = datetime.now().date()
date_str = today_date.strftime('%Y-%m-%d')

# 7日前までの
rating_report_sql = "select a.ticker from rating_report a left join rating_report_price b on a.ticker = b.ticker left join closing_date cd on a.ticker = cd.ticker left join reasonable_prices rp on a.ticker = rp.ticker where a.new in ('買い', 'Ｂｕｙ', '１', 'Ａ', 'アウトパフォーム', 'オーバーウエート') and a.create_date != CURRENT_DATE and b.create_date != CURRENT_DATE and (b.today < rp.new_price or rp.new_price is null) and a.create_date >= (CURRENT_DATE - INTERVAL '3 days') and  b.create_date > (CURRENT_DATE - INTERVAL '3 days') and a.diff_per > 0 order by a.diff_per desc;"

def openchart(driver, ticker, x_position, y_position, width, height):
    try:
        if ticker != 1:
            time.sleep(1)
            el = driver.find_element(By.CSS_SELECTOR, 'a[data-ratid="mem_pc_gnavi_domestic-top"]')
            driver.execute_script("arguments[0].click();", el)
            time.sleep(1)
            el = driver.find_element(By.ID, 'dscrCdNm2')
            el.clear()
            el.send_keys(ticker)
            el = driver.find_element(By.CSS_SELECTOR, 'img[title="検索"]')
            driver.execute_script("arguments[0].click();", el)
            time.sleep(1)
            # 大きなチャートを見るクリック
            el = driver.find_element(By.LINK_TEXT, "大きなチャートを見る")

            # 新しいタブで
            driver.execute_script("arguments[0].setAttribute('target', '_blank'); arguments[0].click();", el)
            # 元のウィンドウのハンドルを取得
            original_window_handle = driver.current_window_handle
            # 元のウィンドウに切り替える
            driver.switch_to.window(original_window_handle)
            # 元のウィンドウを閉じる
            driver.close()
            # 新しいウィンドウのハンドルを取得
            new_window_handle = driver.window_handles[-1]
            # 新しいウィンドウに切り替える
            driver.switch_to.window(new_window_handle)

        # テクニカルチャートクリック
        el = driver.find_element(By.CSS_SELECTOR, 'input[src="/member/images/btn-technical-chart.gif"]')
        driver.execute_script("arguments[0].click();", el)
        # 元のウィンドウのハンドルを取得
        original_window_handle = driver.current_window_handle
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
        # 元のウィンドウに戻る
        driver.switch_to.window(original_window_handle)
    except Exception as e:
        print('Error. ticker:', ticker)
        print(e)


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
            # 日経225" というテキストを持つリンクを見つけてクリック
            link = driver.find_element(By.XPATH, "//table[@class='tbl-data-01']//a[text()='日経225']")

        # 新しいタブで
        driver.execute_script("arguments[0].setAttribute('target', '_blank'); arguments[0].click();", link)
        # 新しいウィンドウのハンドルを取得
        new_window_handle = driver.window_handles[-1]
        # 新しいウィンドウに切り替える
        driver.switch_to.window(new_window_handle)

        openchart(driver, ticker, x_position, y_position, width, height)
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


def loop_tickers(ticker_list, driver):
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

    # driver = login()
    if list_len > 0:
        x_idx = 0
        for idx, ticker in enumerate(ticker_list):
            if x_cnt <= x_idx:  # 改行
                x_position = 0
                x_idx = 0
                y_position = y_position + height

            x_position = width * x_idx
            x_idx += 1
            if ticker in [1]:
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


def get_under_list(ticker_list):
    under_list = []
    driver = None
    try:
        driver = login()
        for ticker in ticker_list:
            el = driver.find_element(By.CSS_SELECTOR, 'a[data-ratid="mem_pc_gnavi_domestic-top"]')
            driver.execute_script("arguments[0].click();", el)
            time.sleep(1)
            el = driver.find_element(By.ID, 'dscrCdNm2')
            el.clear()
            el.send_keys(ticker)
            el = driver.find_element(By.CSS_SELECTOR, 'img[title="検索"]')
            driver.execute_script("arguments[0].click();", el)
            time.sleep(1)
            # "up-02" クラスの要素を取得
            element = driver.find_element(By.CLASS_NAME, "up-02")
            # <td> 内の <nobr> タグ内の2番目の <span> 要素のテキストを取得
            nobr_element = element.find_element(By.TAG_NAME, "nobr")
            value = nobr_element.find_elements(By.TAG_NAME, "span")[0].text
            # 必要な数値部分を抽出
            percentage_value = value.split('（')[1].split('%')[0]
            if float(percentage_value) < 0:
                under_list.append(ticker)
    except Exception as e:
        print (e)

    return under_list, driver


class OpenChats:
    def __init__(self):
        ticker_list = get_ticker_list(rating_report_sql)
        print("ticker_list:", ticker_list)
        under_list, driver = get_under_list(ticker_list)
        loop_tickers(under_list, driver)


my_obj = OpenChats()
