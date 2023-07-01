import yfinance as yfin
import psycopg2
from psycopg2 import Error
from datetime import datetime

today_date = datetime.now().date()
date_str = today_date.strftime('%Y-%m-%d')
plotModeSql = f"select ticker from rating_report where create_date = '{date_str}' order by diff_per desc;"
# plotModeSql = f"select ticker from rating_report  where create_date = '2024-02-06' order by diff_per desc;"

term = '2d'
bar = '1d'


def loop_check(ticker_list):
    for ticker_str in ticker_list:
        ticker = ""
        try:
            uppercase_ticker = ticker_str[0]
            ticker = int(uppercase_ticker)
            print('ticker:', ticker)
            bare_data = y_data(str(ticker) + ".T")
            update_db(bare_data, ticker)

        except Exception as e:
            print('Error. ticker:', ticker)
            print(e)


def update_db(bare_data, ticker):
    close_list = bare_data['Close']
    yesterday = round(close_list[0], 1)
    today = round(close_list[1], 1)
    diff = round(today - yesterday, 1)
    diff_per = round(diff / today * 100, 1)
    upsert_postgres(ticker, yesterday, today, diff, diff_per)


def upsert_postgres(ticker, yesterday, today, diff, diff_per):
    try:
        sql = f"insert into rating_report_price values ({ticker}, {yesterday}, {today}, {diff}, {diff_per}, '{date_str}') " \
              f"on conflict (ticker, create_date) do update set today = {today}, diff = {diff}, diff_per = {diff_per};"
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


class GetLast30Price:
    def __init__(self):
        ticker_list = get_ticker_list()
        loop_check(ticker_list)


# クラスのインスタンスを作成
my_obj = GetLast30Price()
