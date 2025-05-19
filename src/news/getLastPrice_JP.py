import pandas as pd
import yfinance as yfin
import psycopg2
from psycopg2 import Error
from datetime import datetime, timedelta
import time

today_date = datetime.now().date()
# today_date = datetime.now().date() - timedelta(days=1) # デバッグ用。24:00過ぎに使用する場合。

yesterday_date = today_date - timedelta(days=1)

today_str = today_date.strftime('%Y-%m-%d')
yesterday_str = yesterday_date.strftime('%Y-%m-%d')
plotModeSql = (f"select ticker from rating_report where create_date = '{today_str}' "
               f"and new in ('買い', 'Ｂｕｙ', '１', 'Ａ', 'アウトパフォーム', 'オーバーウエート') order by diff_per desc;")

term = '5d'
bar = '1d'
interval = 2


def loop_check(ticker_list):
    for ticker_str in ticker_list:
        ticker = ""
        try:
            uppercase_ticker = ticker_str[0]
            ticker = int(uppercase_ticker)
            print('ticker:', ticker)
            tTicker = str(ticker) + ".T"

            # チェックだけ
            # ticker = yfin.Ticker(tTicker)
            # print(ticker.info)

            bare_data = yfin.download(tTicker, period=term, interval=bar)
            update_db(bare_data, ticker)

            time.sleep(interval)  # 2秒休憩
        except Exception as e:
            print('Error at loop_check. ticker:', ticker)
            print(e)


def update_db(bare_data, ticker):
    try:
        yesterday_date = pd.to_datetime(bare_data.index[-2])
        today_date = pd.to_datetime(bare_data.index[-1])

        yesterday_price = bare_data.loc[yesterday_date, 'Close']
        today_price = bare_data.loc[today_date, 'Close']

        print(f"yesterday: {yesterday_date}: {yesterday_price}")
        print(f"today: {today_date}: {today_price}")

        diff = round(today_price - yesterday_price, 1)
        diff_per = round(diff / today_price * 100, 1)

        upsert_postgres(ticker, yesterday_price, today_price, diff, diff_per)
    except Exception as e:
        print("Error: update_db.", e)
        upsert_postgres(ticker, 0, 0, 0, 0)  # あさイチ登録されない対策の確認中。
        print("0で登録しときますた")


def upsert_postgres(ticker, yesterday, today, diff, diff_per):
    try:
        sql = f"insert into rating_report_price values ({ticker}, {yesterday}, {today}, {diff}, {diff_per}, '{today_str}') " \
              f"on conflict (ticker, create_date) do update set yesterday = {yesterday}, today = {today}, diff = {diff}, diff_per = {diff_per};"
        cursor = postgres()
        cursor.execute(sql)
        connector.commit()
        cursor.close()
        connector.close()
    except(Exception, Error) as error:
        print("Error: upsert_postgres.", error)


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
        cursor.execute(plotModeSql)
        ticker_list = cursor.fetchall()
        cursor.close()
        connector.close()
        return ticker_list
    except(Exception, Error) as error:
        print("Error: get_ticker_list.", error)


class GetLastPrice:
    def __init__(self):
        ticker_list = get_ticker_list()
        loop_check(ticker_list)


# クラスのインスタンスを作成
my_obj = GetLastPrice()
