import time
from selenium.webdriver.common.by import By
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
import psycopg2
from psycopg2 import Error
from datetime import datetime

from src.news.const import kab_news_id, kab_news_pass
today_date = datetime.now().date()
date_str = today_date.strftime('%Y-%m-%d')

# market = 'jp'
market = 'us'
# witch_calender = "left"
witch_calender = "right"


def get_page_data(driver):
    time.sleep(1)
    # 銘柄総合クリックでプルダウン表示
    link_element = driver.find_element(By.CSS_SELECTOR, 'a.nav-link.dropdown-toggle[href="/stocks/jp"]')
    link_element.click()
    time.sleep(1)

    if market == 'jp':
        # 決算カレンダー-日本株クリック
        link_element = driver.find_element(By.CSS_SELECTOR, 'a.dropdown-item[href="/fresult/calendar/jp"]')
        link_element.click()
        time.sleep(1)
    elif market == 'us':
        # 決算カレンダー-米国株クリック
        link_element = driver.find_element(By.CSS_SELECTOR, 'a.dropdown-item[href="/fresult/calendar/us"]')
        link_element.click()
        time.sleep(1)

    if witch_calender == "left":
        # 左側のLeftカレンダー上の月クリック
        link_element = driver.find_element(By.XPATH, '//*[@id="calendar-1"]//a')
        link_element.click()
        time.sleep(1)
    elif witch_calender == "right":
        # 右側のRightカレンダー上の月クリック
        link_element = driver.find_element(By.XPATH, '//*[@id="calendar-2"]//a')
        link_element.click()
        time.sleep(1)

    # href属性に 'contents_per_page=100' が含まれる <a> タグを探してクリック
    link_element = driver.find_element(By.XPATH, '//a[contains(@href, "contents_per_page=100")]')
    link_element.click()
    time.sleep(1)

    get_table_data(driver)

    while(True):
        try:
            # 次へボタン
            next_button = driver.find_element(By.CSS_SELECTOR, 'li.page-item.next a.page-link')
            next_button.click()
            time.sleep(1)
        except Exception as e:
            print("次へボタンなくなった.", e)
            break

        get_table_data(driver)


def login():
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get('https://member.kabushiki.jp/portalNews/LoginNews.do')

    el = driver.find_element(By.NAME, 'userID')
    el.clear()
    el.send_keys(kab_news_id)

    el = driver.find_element(By.NAME, 'pass')
    el.send_keys(kab_news_pass)

    el = driver.find_element(By.CLASS_NAME, 'btnapply')
    el.click()

    driver.maximize_window()
    return driver


def get_table_data(driver):
    # テーブル要素を取得
    table = driver.find_element(By.CLASS_NAME, 'closing-table')
    # テーブルの行を取得
    rows = table.find_elements(By.TAG_NAME, 'tr')

    # ヘッダー行をスキップして、各行のデータを取得
    cursor, connector = postgres()
    for row in rows[1:]:
        cells = row.find_elements(By.TAG_NAME, 'td')
        row_data = [cell.text for cell in cells]
        insert_db(row_data, cursor)

    connector.commit()
    connector.close()


def insert_db(row_data, cursor):
    sql = None
    try:
        if market == 'jp':
            sql = f"INSERT INTO closing_date values (%s, %s, %s, %s, CURRENT_DATE);"
        elif market == 'us':
            sql = f"INSERT INTO closing_date_us values (%s, %s, %s, %s, %s, %s, CURRENT_DATE);"
        cursor.execute(sql, row_data)
    except Exception as e:
        print("dbエラー.", e)


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


class GetClosingData:
    def __init__(self):
        driver = login()
        get_page_data(driver)


my_obj = GetClosingData()
