import pandas as pd
import yfinance as yfin
import psycopg2
from psycopg2 import Error
from datetime import datetime, timedelta

today_date = datetime.now().date()
# today_date = datetime.now().date() - timedelta(days=1) # デバッグ用。24:00過ぎに使用する場合。

yesterday_date = today_date - timedelta(days=1)

today_str = today_date.strftime('%Y-%m-%d')
yesterday_str = yesterday_date.strftime('%Y-%m-%d')
plotModeSql = "select ticker from hold_tickers;"

term = '5d'
bar = '1d'


def loop_check(ticker_list):
    for ticker_str in ticker_list:
        ticker = ""
        try:
            uppercase_ticker = ticker_str[0]
            ticker = uppercase_ticker
            print('ticker:', ticker)
            bare_data= None
            if ticker.isdigit():
                bare_data = y_data(str(ticker) + ".T")
            else:
                bare_data = y_data(ticker)

            update_db(bare_data, ticker)

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
        sql = f"insert into yahoo_price values ('{ticker}', {today}, '{today_str}') " \
              f"on conflict (ticker, create_date) do update set today = {today};"
        cursor = postgres()
        cursor.execute(sql)
        connector.commit()
        cursor.close()
        connector.close()
    except(Exception, Error) as error:
        print("Error: upsert_postgres.", error)


def y_data(ticker):
    return yfin.download(ticker, period=term, interval=bar)


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
