from psycopg2 import Error

from src.db.postgres import get_cursor
import yfinance as yfin
import numpy as np

from src.rktn.Login import login
import time
from selenium.webdriver.common.by import By

term = '6mo'
bar = '1d'


def get_owned_tickers(driver):
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


def plot(bare_data, ticker, sell_list):
    buy_past_days = 0
    y_list = bare_data['Close']
    x_list = y_list.index

    buy_x_list = []
    sell_x_list = []
    add_up_buy_price = 0
    add_up_sell_price = 0
    witch_deal = 'default'

    # 移動平均
    y_list_mean_s = y_list.rolling(window=5, min_periods=1).mean()
    y_list_mean_l = y_list.rolling(window=10, min_periods=1).mean()

    first_buy_price = 0
    last_buy_price = 0
    last_sell_price = 0
    deviationList = []
    last_y = 0
    last_x = 0
    y_list_length = len(y_list)
    print("y_list_length:", y_list_length)
    for (x, y) in enumerate(y_list, 0):
        if witch_deal == 'default':
            first_buy_price = y
            witch_deal = 'buy'
            last_buy_price = y
            add_up_buy_price += y

        if witch_deal == 'sell':
            if y_list_mean_s[x] > y_list_mean_l[x]:  # 上昇時
                if y > y_list_mean_s[x] > y_list[x - 1]:  # 5日移動平均を超えたら
                    # if y > y_list_mean_s[x]:  # 5日移動平均を超えたら
                    buy_x_list.append(x)
                    add_up_buy_price += y
                    witch_deal = 'buy'
                    last_buy_price = y
                    buy_past_days = y_list_length - x

        # ======Sell====================================================
        elif witch_deal == 'buy':
            if y_list_mean_s[x] > y_list_mean_l[x]:  # 上昇時
                # 上昇時は10日移動平均を割り込むまで売らない
                if y_list_mean_l[x] > y:
                    sell_x_list.append(x)
                    add_up_sell_price += y
                    witch_deal = 'sell'
                    last_sell_price = y
                    print(last_sell_price - last_buy_price)
            else:
                # 5日移動平均を割り込んだら売り
                if y_list_mean_s[x] > y:
                    sell_x_list.append(x)
                    add_up_sell_price += y
                    witch_deal = 'sell'
                    last_sell_price = y
                    print(last_sell_price - last_buy_price)

        last_y = y
        last_x = x

    print('sell_x_list:', sell_x_list)
    print("len(y_list):", len(y_list))
    if (sell_x_list[-1] + 1) == len(y_list):
        print("売りアラート")
        sell_list.append(ticker)

    # 最後がbuyで終わった場合は、
    if witch_deal == 'buy':
        # 最後のlast_y売り
        add_up_sell_price += last_y
        sell_x_list.append(last_x)
        # print(last_y - last_buy_price)

    # strategy_profit = add_up_sell_price - add_up_buy_price
    # natural_profit = last_y - first_buy_price
    # print("strategy_profit:", strategy_profit)
    # print("普通に持ってたら：", natural_profit)
    # print("差額：", strategy_profit - natural_profit)
    # print("buy_past_days:", buy_past_days)

    # return strategy_profit, natural_profit, buy_past_days, stdev, last_y
    return sell_list


def loop_check(ticker_list):
    sell_list = []
    for idx, ticker in enumerate(ticker_list, 0):
        try:
            print('ticker:', ticker)
            bare_data = yfin.download(ticker, period=term, interval=bar)
            sell_list = plot(bare_data, ticker, sell_list)
        except Exception as e:
            print('Error. ticker:', ticker)
            print(e)
    return sell_list


def auto_sell_one(driver, ticker):

    try:
        time.sleep(2)
        el = driver.find_element(By.CSS_SELECTOR, 'a[data-ratid="mem_pc_gnavi_domestic-top"]')
        driver.execute_script("arguments[0].click();", el)
        time.sleep(1)
        # 売り一覧へ
        el = driver.find_element(By.ID, "jp-stk-top-btn-sell")
        driver.execute_script("arguments[0].click();", el)
        time.sleep(1)
        # 対象の売りボタン
        ticker = ticker[:-2]
        link_xpath = '//a[contains(@href, "/ord") and contains(@href, "dscrCd=' + ticker + '")]'
        el = driver.find_element(By.XPATH, link_xpath)
        driver.execute_script("arguments[0].click();", el)
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
        el = driver.find_element(By.CLASS_NAME, "pcm-gl-logo-img")
        driver.execute_script("arguments[0].click();", el)
    except Exception as e:
        print('Error. ticker:', ticker)
        print(e)


def loop_sell(sell_list, driver):
    if len(sell_list) > 0:
        # driver = login()
        for ticker_tuple in sell_list:
            ticker = ticker_tuple[0]
            auto_sell_one(driver, ticker)
    else:
        print("nothing to sell.")


class AutoSell:

    # def get_ticker_list(self):
    #     # cursor, connector = get_cursor()
    #     try:
    #         # cursor.execute("select ticker from ticker where hold = true")
    #         # cursor.execute(
    #         #     "select ticker from days_results where sheet_name = 'direct' and sell_past_days != 0 order by sell_past_days asc, diff desc")  # デバッグ要
    #         # ticker_list = cursor.fetchall()
    #         return ticker_list
    #     except(Exception, Error) as error:
    #         print("Error: get_ticker_list.", error)
    #     finally:
    #         cursor.close()
    #         connector.close()

    def __init__(self):
        driver = login()
        owned_ticker_list = get_owned_tickers(driver)
        print("owned_ticker_list:", owned_ticker_list)

        # ticker_list = self.get_ticker_list()
        sell_list = loop_check(owned_ticker_list)
        # sell_list = [('PHI',), ('RGLD',), ('AXP',)]
        # sell_list = [('MPC',)]
        loop_sell(sell_list, driver)


my_obj = AutoSell()
