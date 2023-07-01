from psycopg2 import Error
from src.rktn.Login import login
import time
from selenium.webdriver.common.by import By
import psycopg2
from datetime import datetime

# display_width = 1900  # 1920
# display_height = 1000  # 1080

# 125 % ( 80 %)
display_width = 3000  # 3840
display_height = 1700  # 2160

today_date = datetime.now().date()
date_str = today_date.strftime('%Y-%m-%d')
# selectSql = f"select ticker from (select distinct on (ticker) * from rating_report where create_date = '{date_str}' and diff_per > 0) a order by a.diff_per desc;"
# selectSql = f"select ticker from (select distinct on (ticker) * from rating_report where create_date = '2024-02-14' and diff_per > 0) a order by a.diff_per desc;"
selectSql = f"select ticker from (SELECT DISTINCT ON (ticker) * FROM rating_report WHERE \"new\" IN ('買い', 'Ｂｕｙ', '１', 'Ａ', 'アウトパフォーム', 'オーバーウエート') AND create_date = '{date_str}' AND diff_per > 0) a order by a.diff_per desc;"

# TODO: 日経225？ 平均も追加する

def openchart(driver, ticker, x_position, y_position, width, height):
    try:
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
        # チャートウィンドウのサイズを変更
        driver.set_window_size(width, height)
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


def get_ticker_list():
    try:
        cursor = postgres()
        cursor.execute(selectSql)
        ticker_list = cursor.fetchall()
        ticker_list = [item[0] for item in ticker_list]
        cursor.close()
        connector.close()
        return ticker_list
    except(Exception, Error) as error:
        print("Error: get_ticker_list.", error)


class OpenChats:
    def __init__(self):
        ticker_list = get_ticker_list()
        print("ticker_list:", ticker_list)
        loop_tickers(ticker_list)


my_obj = OpenChats()
