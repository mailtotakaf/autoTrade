import time
import matplotlib.pyplot as plt
import yfinance as yfin
import psycopg2
from psycopg2 import Error

term = '2mo'
bar = '1d'

sheet_name = 'index'

or_ticker = ""
# or_ticker = '3865.T'


class Plot:
    def __init__(self):
        start = time.time()
        self.loop_check()
        print("処理時間：", time.time() - start)  # 1536.2

    def postgres(self):
        global cursor, connector
        try:
            connector = psycopg2.connect('postgresql://{user}:{password}@{host}:{port}/{dbname}'.format(
                user="postgres",
                password="YourPW",
                host="localhost",
                port="5432",
                dbname="trading"))

            cursor = connector.cursor()
            return cursor
        except(Exception, Error) as error:
            print("Error: DB connection.", error)

    def loop_check(self):
        global max, min
        ticker_list = self.get_ticker_list()
        cursor = self.postgres()

        d_data_list_dict = {}
        all_tickers_middles = []
        for idx, ticker in enumerate(ticker_list, 0):
            print('ticker:', ticker)
            d_data_list = []

            try:
                bare_data = y_data(ticker)
                closeData = bare_data['Close']

                y_list = []
                x_list = []
                for timestamp, price in closeData.items():
                    y_list.append(price)
                    x_list.append(timestamp)

                select_query = "select company_name from ticker where ticker = %s"
                cursor.execute(select_query, ticker)
                company_name = cursor.fetchall()
                print("company_name:", company_name)

                max_val = max(y_list)
                min_val = min(y_list)
                middle_val = (max_val + min_val) / 2
                d_data_list.append(y_list)
                d_data_list.append(x_list)
                d_data_list.append(middle_val)
                d_data_list.append(company_name)

                all_tickers_middles.append(middle_val)
            except(Exception, Error) as error:
                print("Error: get_ticker_list.", error)

            d_data_list_dict[ticker] = d_data_list

        cursor.close()
        connector.close()

        all_mid_max = max(all_tickers_middles)
        all_mid_min = min(all_tickers_middles)

        all_middle = (all_mid_max + all_mid_min) / 2
        shifted_d_list_dict = {}
        all_max_list = []
        all_min_list = []
        for idx, (key, val) in enumerate(d_data_list_dict.items()):
            try:
                shifted_d_data_list = []
                mid = val[2]
                add = all_middle - mid
                shifted_data_list = [y + add for y in val[0]]
                shifted_d_data_list.append(shifted_data_list)
                shifted_d_data_list.append(val[1])
                shifted_d_data_list.append(val[3])

                all_max_list.append(max(shifted_data_list))
                all_min_list.append(min(shifted_data_list))

                shifted_d_list_dict[key] = shifted_d_data_list
            except(Exception, Error) as error:
                print("Error: shifted_d_list_dict.", error)

        all_max = max(all_max_list)
        all_min = min(all_min_list)
        print("all_max:", all_max)
        print("all_min:", all_min)

        plot(shifted_d_list_dict)

    def getPriceListFromDB(self, ticker, cursor):
        select_query = "select ic.ticker, ic.last_price, ic.date_time, t.company_name from index_chart ic " \
                       "inner join ticker t on ic.ticker = t.ticker where ic.ticker = %s order by ic.date_time asc;"
        cursor.execute(select_query, ticker)
        bare_data = cursor.fetchall()
        return bare_data

    def get_ticker_list(self):
        try:
            cursor = self.postgres()

            if or_ticker != "":
                select_sql = "SELECT ticker FROM ticker where sheet_name = '" + sheet_name + "' or ticker = '" + or_ticker + "'"
            else:
                select_sql = "SELECT ticker FROM ticker where sheet_name = '" + sheet_name + "'"

            cursor.execute(select_sql)

            ticker_list = cursor.fetchall()
            return ticker_list
        except(Exception, Error) as error:
            print("Error: get_ticker_list.", error)
        finally:
            cursor.close()
            connector.close()

    def insert_results(self, ticker, bare_data, cursor):
        closeData = bare_data['Close']
        valuesStr = ""
        try:
            for timestamp, price in closeData.items():
                valuesStr += "('" + ticker[0] + "', " + str(price) + ", '" + str(timestamp) + "'),"

            valuesStr = valuesStr[:-1]  # 最後のカンマ削除

            insertSql = "insert into index_chart values " + valuesStr
            cursor.execute(insertSql)
        except(Exception, Error) as error:
            print("Error: insert into index_chart.", error)


def plot(d_data_list_dict):
    colors = ['#888', '#00f', '#0f0', '#0ff', '#f00']
    plt.figure()
    plt.grid(True)
    plt.tight_layout()
    plt.title("Indexes")

    for idx, (key, val) in enumerate(d_data_list_dict.items()):
        y_list = val[0]
        x_list = val[1]
        # plt.plot(x_list, y_list, color=colors[idx % 5], label=val[2])
        plt.plot(x_list, y_list, label=val[2])
        plt.xticks(x_list, rotation=90)

    # 凡例を表示
    plt.legend()
    plt.show()


def y_data(ticker):
    # https://note.com/misamisa333/n/n0d574c96b8d6
    return yfin.download(ticker, period=term, interval=bar)


# クラスのインスタンスを作成
my_obj = Plot()
