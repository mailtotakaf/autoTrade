import time
from selenium.webdriver.common.by import By
from selenium import webdriver
import psycopg2
from psycopg2 import Error
import re
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

KB_ID = os.getenv("KB_ID")
KB_PW = os.getenv("KB_PW")

today_date = datetime.now().date()
date_str = today_date.strftime('%Y-%m-%d')


def login():
    driver = webdriver.Chrome()
    driver.get('https://member.kabushiki.jp/portalNews/LoginNews.do')

    el = driver.find_element(By.NAME, 'userID')
    el.clear()
    el.send_keys(KB_ID)

    el = driver.find_element(By.NAME, 'pass')
    el.send_keys(KB_PW)

    el = driver.find_element(By.CLASS_NAME, 'btnapply')
    el.click()

    driver.maximize_window()
    return driver


regex_ptn = r'・([^・＞]+)＞'

# 文字列から証券会社名を抽出する正規表現パターン
pattern = r'・(.*?)（'
def search_rating(driver):
    # driver.get('https://kabushiki.jp/news/623397')
    # driver.get('https://kabushiki.jp/news/top?date=2024-01-19&page=2') # デバッグ用に仮設定（この行不要）
    # driver.get('https://kabushiki.jp/news/top?page=2')  # デバッグ用に仮設定（この行不要）
    # driver.get('https://kabushiki.jp/news/top?page=3')  # デバッグ用に仮設定（この行不要）
    time.sleep(1)
    link_element = driver.find_element(By.PARTIAL_LINK_TEXT, "レーティング＆リポート情報")
    link_element.click()
    time.sleep(1)
    highest_val = ""

    div_elements = driver.find_elements(By.CLASS_NAME, 'cmn-summary-detail-1--main')
    for div_element in div_elements:
        rank_tuple = None
        p_elements = div_element.find_elements(By.TAG_NAME, "p")
        for p in p_elements:
            print("p.text:", p.text)
            try:
                regex_match = re.search(regex_ptn, p.text)
                if regex_match:
                    rank_tuple = extract_labels(p.text)
            except Exception as e:
                print("error.", e)

            try:
                row_list = []
                if '→' in p.text:
                    row_list = extract_info(p.text, rank_tuple)
                else:
                    row_list = extract_info_new(p.text, rank_tuple)

                insert_db(row_list)
            except Exception as e:
                print("ああerror.", e)


def extract_labels(text):
    # 「（」と「）」の間の部分を抽出
    bracket_content = text[text.find("（") + 1:text.find("）")]

    # 「・」で分割して、目的の部分を取得
    objective_part = bracket_content.split("・")[-1]

    # 「＞」で分割して目的の文字列のリストを取得
    labels = objective_part.split("＞")

    return labels


def check_current(p, driver):
    link_elements = p.find_elements(By.TAG_NAME, "a")
    link_elements[0].click()
    # 新しいウィンドウのハンドルを取得
    new_window_handle = driver.window_handles[1]
    # 新しいウィンドウに切り替え
    driver.switch_to.window(new_window_handle)
    time.sleep(3)


def insert_db(row_list):
    print("DB登録")
    try:
        cursor, connector = postgres()

        name = row_list[0]
        ticker = int(row_list[1])
        old = row_list[2]
        new = row_list[3]
        diff_per = row_list[4]
        from_price = row_list[5]
        to_price = row_list[6]
        create_date = row_list[7]
        sql = f"INSERT INTO rating_report values ('{name}', '{ticker}', '{old}', '{new}', {diff_per}, '{from_price}', '{to_price}', '{create_date}');"
        cursor.execute(sql)
        connector.commit()
        connector.close()
    except Exception as e:
        print("dbエラー.", e)


def extract_info(input_string, rank_tuple):
    row_list = []
    try:
        # 1: "（）" かっこの前の文字列
        pattern_1 = r'(.+?)（\d+）'

        # 2: "（）" かっこの中の数字
        pattern_2 = r'（(\d+)）'

        # 3: "――「」" 鍵かっこの中の文字
        pattern_3 = r'――「(.+?)」'

        # 4: "→「中立」" 鍵かっこの中の文字
        pattern_4 = r'→「(.+?)」'

        # 5: "、" に続く" 円" までの数字
        pattern_5 = r'、(\d+)円'

        # 6: 最後の"円" の直前の数字
        pattern_6 = r'→(\d+)円'

        result_1 = re.search(pattern_1, input_string).group(1)
        result_2 = re.search(pattern_2, input_string).group(1)
        result_3 = re.search(pattern_3, input_string).group(1)
        result_4 = re.search(pattern_4, input_string).group(1)
        result_5 = re.search(pattern_5, input_string).group(1)
        result_6 = re.search(pattern_6, input_string).group(1)

        print("1:", result_1)
        print("2:", result_2)
        print("3:", result_3)
        print("4:", result_4)
        print("5:", result_5)  # from
        print("6:", result_6)  # to

        int5 = int(result_5) # from
        int6 = int(result_6) # to
        price_diff = int6 - int5
        if price_diff < 0: # マイナスだったら
            return None

        print("差額price_diff：", price_diff)
        diff_per = round(price_diff / int5 * 100, 1)
        print(f"差額per diff_per: ${diff_per} %")
        row_list.append(result_1)
        row_list.append(result_2)
        row_list.append(result_3)
        row_list.append(result_4)
        row_list.append(float(diff_per))
        row_list.append(int5) # from
        row_list.append(int6) # to
        row_list.append(date_str)
        return row_list
    except Exception as e:
        print("extract_infoエラー.", e)


def extract_info_new(input_string, rank_tuple):
    row_list = []
    try:
        # 1: "（）" かっこの前の文字列
        pattern_1 = r'(.+?)（\d+）'

        # 2: "（）" かっこの中の数字
        pattern_2 = r'（(\d+)）'

        # 3: "――「」" 鍵かっこの中の文字
        pattern_3 = r'「(.+?)」'

        # 5: "、" に続く" 円" までの数字
        pattern_5 = r'、(\d+)円'

        result_1 = re.search(pattern_1, input_string).group(1)
        result_2 = re.search(pattern_2, input_string).group(1)
        result_3 = re.search(pattern_3, input_string).group(1)
        result_4 = "-"
        result_5 = re.search(pattern_5, input_string).group(1)

        # if result_3 == highest_val:
        row_list.append(result_1)
        row_list.append(result_2)
        row_list.append(result_4)
        row_list.append(result_3)  # 逆にする
        row_list.append(float(99))
        row_list.append(int(0)) # 追加
        row_list.append(int(result_5))
        row_list.append(date_str)
        return row_list
    except Exception as e:
        print("extract_info_newエラー.", e)


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
        return cursor, connector
    except(Exception, Error) as error:
        print("Error: DB connection.", error)


class RatingReport:
    def __init__(self):
        driver = login()
        search_rating(driver)


my_obj = RatingReport()
