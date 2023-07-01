import datetime
import os
import time
import ccxt
import pandas as pd
from psycopg2 import extras

from src.db.postgres import get_cursor

coincheck_apiKey = os.getenv('COINCHECK_API_KEY')
coincheck_secret = os.getenv('COINCHECK_SECRET')
coincheck = ccxt.coincheck({'apiKey': coincheck_apiKey, 'secret': coincheck_secret})

ticker = "BTC/JPY"
interval_sec = 10  # 5分に設定
wait_for_mean = 2  # 10日移動平均


def get_row_list(row_list):
    result = coincheck.fetch_ticker(symbol=ticker)
    ask = float(result["ask"])
    bid = float(result["bid"])
    diff_per = (ask - bid) / ask * float(100)
    timestamp = result["timestamp"]
    dt = datetime.datetime.fromtimestamp(timestamp / 1000)
    print(ticker, "--------------", dt)
    # print("ask:", ask)
    # print("bid:", bid)
    # print("diff:", ask - bid)
    # print("diff_per:", diff_per)
    print("30回手数料=", diff_per * 30)

    row = (ask, bid, diff_per, dt)
    row_list.append(row)
    if len(row_list) > 12:
        row_list.pop(0)  # 古いデータを削除
    # print("len(row_list)=", len(row_list))
    return row_list


def get_judged(row_list, buy_flg):
    y_list = [item[0] for item in row_list]
    y_list = pd.Series(y_list)

    # 移動平均
    y_list_mean_s = y_list.rolling(window=5, min_periods=1).mean()

    buy_flg = strategy_minutes(y_list_mean_s, y_list.iloc[-1], buy_flg)

    return buy_flg


def strategy_minutes(y_list_mean_s, y, buy_flg):
    if buy_flg:
        # ======Sell======上ってるとき売らない==============================================
        if y_list_mean_s.iloc[-2] > y_list_mean_s.iloc[-1]:
            if y_list_mean_s.iloc[-1] > y:
                buy_flg = False
    else:
        # =======Buy===下ってるとき買わない=========================================
        if y_list_mean_s.iloc[-2] < y_list_mean_s.iloc[-1]:
            if y > y_list_mean_s.iloc[-1]:  # 5日移動平均を超えたら
                buy_flg = True
    return buy_flg


def insert(row_list):
    cursor, connector = get_cursor()
    extras.execute_values(cursor, "INSERT INTO streams values %s", row_list)
    connector.commit()
    connector.close()


def get_y_list():
    cursor, connector = get_cursor()
    select_sql = "select col_1 from streams"
    cursor.execute(select_sql)
    return cursor.fetchall()


class Stream:
    def __init__(self):
        row_list = []
        buy_flg = False

        while True:
            row_list = get_row_list(row_list)
            if len(row_list) > wait_for_mean:
                buy_flg = get_judged(row_list, buy_flg)
                print("---------------------buy_flg:---", buy_flg)

            time.sleep(interval_sec)


my_obj = Stream()
