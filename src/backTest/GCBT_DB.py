import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yfin
import psycopg2
from psycopg2 import Error

# sheet_name = "direct"
# sheet_name = "nikkei500"
# sheet_name = "sp500"
# sheet_name = "cript"
sheet_name = "ticker_jp"
# sheet_name = "coincheck"
charge = 0.15 / 100

strategy = "simple"
# strategy = ""

# mode = ""
mode = "plotMode"

# plotModeSql = "select mr.ticker, t.name from days_results mr left join ticker_jp t on mr.ticker = t.ticker where mr.strategy = 'simple' and mr.buy_past_days != 0 and mr.last_price < 1000 order by mr.buy_past_days asc, mr.last_rsi asc"
plotModeSql = "select ticker, name from ticker_jp where ticker in ('9994.T', '9432.T');"

# db_name = 'days_results'
# term = '6mo'
# bar = '1d'

db_name = 'minutes_results'
term = '1d'
bar = '1m'


class Plot:
    def __init__(self):
        start = time.time()

        ticker_list = self.get_ticker_list()
        self.loop_check(ticker_list)
        print("処理時間：", time.time() - start)  # 1536.2

    def postgres(self):
        global cursor, connector
        try:
            connector = psycopg2.connect('postgresql://{user}:{password}@{host}:{port}/{dbname}'.format(
                user="postgres",
                password="Ppass#00",
                host="localhost",
                port="5432",
                dbname="trading"))

            cursor = connector.cursor()
            return cursor
        except(Exception, Error) as error:
            print("Error: DB connection.", error)

    def get_ticker_list(self):
        try:
            cursor = self.postgres()

            if mode == "plotMode":
                cursor.execute(plotModeSql)
            else:
                # select_sql = "SELECT ticker, company_name FROM ticker where sheet_name = '" + sheet_name + "'" # 洋モノ
                # select_sql = "SELECT ticker, name FROM ticker_jp"
                select_sql = "select t.ticker, t.name from ticker_jp t"

                cursor.execute(select_sql)

            ticker_list = cursor.fetchall()
            return ticker_list
        except(Exception, Error) as error:
            print("Error: get_ticker_list.", error)
        finally:
            cursor.close()
            connector.close()

    def loop_check(self, ticker_list):
        # ticker_list = self.get_ticker_list()
        cursor = self.postgres()

        for idx, tickers in enumerate(ticker_list, 0):
            try:
                print('tickers:', tickers)
                bare_data = y_data(tickers[0])
                rtn_profits = get_results(bare_data, tickers[0], tickers[1])
                if mode != "plotMode":
                    self.insert_results(rtn_profits, tickers[0], cursor)

            except Exception as e:
                print('Error. ticker:', tickers)
                print(e)

            finally:
                connector.commit()

        cursor.close()
        connector.close()

    def insert_results(self, rtn_profits, ticker, cursor):
        strategy_profit, natural_profit, buy_past_days, last_price, sell_past_days, strategy_per, natural_per, diff_per, last_rsi, buy_sell_cnt, volume, stdev = rtn_profits

        sql = "insert into " + db_name + \
              " (" \
              "ticker," \
              "strategy_profit," \
              "natural_profit," \
              "buy_past_days," \
              "diff," \
              "last_price," \
              " sell_past_days," \
              " strategy_per," \
              " natural_per," \
              " diff_per," \
              " stdev," \
              " last_rsi ," \
              " buy_sell_cnt, " \
              " volume, " \
              "sheet_name, " \
              "bar, " \
              "strategy, " \
              "create_timestamp" \
              ") values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, current_timestamp)" \
              # " ON CONFLICT (ticker)" \
              # " DO UPDATE SET " \
              # " strategy_profit = %s," \
              # " natural_profit = %s," \
              # " buy_past_days = %s," \
              # " diff = %s," \
              # " last_price = %s, " \
              # " sell_past_days = %s, " \
              # " strategy_per = %s, " \
              # " natural_per = %s, " \
              # " diff_per = %s, " \
              # " stdev = %s, " \
              # " last_rsi = %s, " \
              # " buy_sell_cnt = %s, " \
              # " volume = %s, " \
              # " sheet_name = %s," \
              # " bar = %s, " \
              # " strategy = %s, " \
              # " create_timestamp = current_timestamp"

        cursor.execute(sql, (
            ticker,
            strategy_profit,
            natural_profit,
            buy_past_days,
            strategy_profit - natural_profit,
            last_price,
            sell_past_days,
            strategy_per,
            natural_per,
            diff_per,
            stdev,
            round(last_rsi),
            buy_sell_cnt,
            volume,
            sheet_name,
            term + "/" + bar,
            strategy,

            ## UPSERT Params ##
            # strategy_profit,
            # natural_profit,
            # buy_past_days,
            # strategy_profit - natural_profit,
            # last_price,
            # sell_past_days,
            # strategy_per,
            # natural_per,
            # diff_per,
            # stdev,
            # round(last_rsi),
            # buy_sell_cnt,
            # volume,
            # sheet_name,
            # term + "/" + bar,
            # strategy
        ))


def get_results(bare_data, ticker, company_name):
    buy_past_days = 0
    y_list = bare_data['Close']
    volume_list = bare_data['Volume']
    x_list = []
    hours = 18
    if sheet_name == "cript":
        hours = 0

    if db_name == 'minutes_results':
        x_list0 = y_list.index
        # 18時間を表すTimedeltaを作成
        delta = pd.Timedelta(hours=hours)

        # 1日目の日付を取得
        first_date = x_list0[0].strftime('%Y-%m-%d')

        for date in x_list0:
            if date.date() == pd.to_datetime(first_date).date():
                # 1日目の日付のデータにのみ18時間を足して追加
                x_list.append(date + delta)
            else:
                # 2日目の日付のデータは変更せずに追加
                x_list.append(date)
    else:
        x_list = y_list.index

    rsi_y_list = get_rsi(y_list)

    buy_x_list = []
    sell_x_list = []
    add_up_buy_price = 0
    add_up_sell_price = 0
    sum_up_charge = 0
    witch_deal = 'default'

    # 移動平均
    y_list_mean_l = y_list.rolling(window=75, min_periods=1).mean()
    y_list_mean_m = y_list.rolling(window=25, min_periods=1).mean()
    y_list_mean_s = y_list.rolling(window=5, min_periods=1).mean()

    first_buy_price = 0
    last_buy_price = 0
    # last_sell_price = 0
    deviationList = []
    last_y = 0
    last_x = 0
    y_list_length = len(y_list)
    last_rsi = 0
    for (x, y) in enumerate(y_list, 0):
        if witch_deal == 'default':
            first_buy_price = y
            witch_deal = 'buy'
            last_buy_price = y
            add_up_buy_price += y
            sum_up_charge += y * charge
            buy_x_list.append(x)

        rtn = None
        if db_name == 'minutes_results':
            rtn = strategy_minutes(witch_deal, x, y, y_list_mean_s, y_list_mean_l, y_list, buy_x_list, add_up_buy_price,
                                   y_list_length, sell_x_list, add_up_sell_price, last_buy_price, buy_past_days,
                                   rsi_y_list, sum_up_charge)
        else:
            rtn = strategy_days(witch_deal, x, y, y_list_mean_s, y_list_mean_l, y_list, buy_x_list, add_up_buy_price,
                                y_list_length, sell_x_list, add_up_sell_price, last_buy_price, buy_past_days,
                                sum_up_charge)

        witch_deal, x, y, y_list_mean_s, y_list_mean_l, y_list, buy_x_list, add_up_buy_price, y_list_length, sell_x_list, add_up_sell_price, last_buy_price, buy_past_days, sum_up_charge = rtn

        last_y = y
        last_x = x

        deviation = y_list[x] - y_list_mean_s[x]
        dev_per = deviation / y_list_mean_s[x]
        deviationList.append(dev_per)

        last_rsi = rsi_y_list[x]

    stdev = np.std(deviationList)

    sell_past_days = 99
    if witch_deal == 'sell':
        sell_past_days = len(y_list) - sell_x_list[-1]

    # 最後がbuyで終わった場合は、
    if witch_deal == 'buy':
        # 最後のlast_y売り
        add_up_sell_price += last_y
        sell_x_list.append(last_x)
        sum_up_charge += charge * last_y

    strategy_profit = add_up_sell_price - add_up_buy_price
    natural_profit = last_y - first_buy_price
    strategy_per = strategy_profit / first_buy_price * 100
    natural_per = natural_profit / first_buy_price * 100
    diff_per = (strategy_profit - natural_profit) / last_y * 100
    print("strategy_profit:", strategy_profit)
    print("普通に持ってたら：", natural_profit)
    print("差額：", strategy_profit - natural_profit)
    print("手数料：", sum_up_charge)
    print("買い回数：", len(buy_x_list))
    print("売り回数：", len(sell_x_list))
    buy_sell_cnt = len(buy_x_list) + len(sell_x_list)

    if mode == "plotMode":
        if db_name == 'minutes_results':
            x_labels = [timestamp.strftime('%H-%M') for timestamp in x_list]
            plot(x_list, y_list_mean_s, y_list_mean_m, y_list_mean_l, x_labels, y_list, sell_x_list, buy_x_list, ticker,
                 company_name, rsi_y_list, volume_list)
        else:
            x_labels = x_list.strftime('%m-%d')

            plot(x_list, y_list_mean_s, y_list_mean_m, y_list_mean_l, x_labels, y_list, sell_x_list, buy_x_list, ticker,
                 company_name,
                 rsi_y_list, volume_list)

    volume = sum(volume_list)

    return strategy_profit, natural_profit, buy_past_days, last_y, sell_past_days, strategy_per, natural_per, diff_per, last_rsi, buy_sell_cnt, volume, stdev


def get_volume(volume_list):
    volume = 0
    if max(volume_list) > 1000:
        scaled_volume_list = [x / 10000 for x in volume_list]
        volume = sum(scaled_volume_list)
    else:
        volume = sum(volume_list)
    return volume


def plot(x_list, y_list_mean_s, y_list_mean_m, y_list_mean_l, x_labels, y_list, sell_x_list, buy_x_list, ticker, company_name,
         rsi_y_list, volume_list):
    plt.figure()
    plt.grid(True)
    plt.xticks(x_list, x_labels, rotation=90)
    plt.legend(prop={'family': 'MS Gothic'})
    plt.title(ticker + ":" + company_name, fontname='MS Gothic')

    plt.plot(x_list, y_list_mean_s, color="#8f8")
    plt.plot(x_list, y_list_mean_m, color="#f88")
    plt.plot(x_list, y_list_mean_l, color="#88f")
    plt.plot(x_list, y_list, '.', linestyle='solid', marker="o", markevery=sell_x_list, color="red")
    plt.plot(x_list, y_list, '.', linestyle='solid', marker="o", markevery=buy_x_list, color="black")

    # RSI
    plt.twinx()
    plt.plot(x_list, rsi_y_list, linestyle='dotted', color="blue")
    # plt.plot(x_list, volume_list, linestyle='dotted', color="blue")
    plt.show()


def strategy_days(witch_deal, x, y, y_list_mean_s, y_list_mean_l, y_list, buy_x_list, add_up_buy_price, y_list_length,
                  sell_x_list, add_up_sell_price, last_buy_price, buy_past_days, sum_up_charge):
    if strategy == "simple":
        # =======Buy============================================
        if witch_deal == 'sell':
            if y > y_list[x - 1]:
                buy_x_list.append(x)
                add_up_buy_price += y
                witch_deal = 'buy'
                last_buy_price = y
                buy_past_days = y_list_length - x

        # ======Sell====================================================
        elif witch_deal == 'buy':
            if y < y_list[x - 1]:
                sell_x_list.append(x)
                add_up_sell_price += y
                witch_deal = 'sell'
                # last_sell_price = y
    else:
        # =======Buy============================================
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
                    # last_sell_price = y
            else:
                # 5日移動平均を割り込んだら売り
                if y_list_mean_s[x] > y:
                    sell_x_list.append(x)
                    add_up_sell_price += y
                    witch_deal = 'sell'
                    # last_sell_price = y

    return witch_deal, x, y, y_list_mean_s, y_list_mean_l, y_list, buy_x_list, add_up_buy_price, y_list_length, sell_x_list, add_up_sell_price, last_buy_price, buy_past_days, sum_up_charge


def strategy_minutes(witch_deal, x, y, y_list_mean_s, y_list_mean_l, y_list, buy_x_list, add_up_buy_price,
                     y_list_length,
                     sell_x_list, add_up_sell_price, last_buy_price, buy_past_days, rsi_y_list, sum_up_charge):
    if strategy == "simple":
        # =======Buy===1分前と比較するだけ=========================================
        if witch_deal == 'sell':
            if y > y_list[x - 1]:
                buy_x_list.append(x)
                add_up_buy_price += y
                witch_deal = 'buy'
                last_buy_price = y
                buy_past_days = y_list_length - x
                sum_up_charge += y * charge

        # ======Sell======上ってるとき売らない==============================================
        elif witch_deal == 'buy':
            if y_list_mean_s[x - 1] > y_list_mean_s[x]:
                if y_list_mean_s[x] > y:
                    sell_x_list.append(x)
                    add_up_sell_price += y
                    witch_deal = 'sell'
                    sum_up_charge += y * charge

        # # # =======Buy===1分前と比較するだけ=========================================
        # if witch_deal == 'sell':
        #     if y > y_list[x - 1]:
        #         buy_x_list.append(x)
        #         add_up_buy_price += y
        #         witch_deal = 'buy'
        #         last_buy_price = y
        #         buy_past_days = y_list_length - x
        #         sum_up_charge += y * charge
        #
        # # ======Sell======1分前と比較するだけ==============================================
        # elif witch_deal == 'buy':
        #     if y < y_list[x - 1]:
        #         sell_x_list.append(x)
        #         add_up_sell_price += y
        #         witch_deal = 'sell'
        #         sum_up_charge += y * charge
    else:
        # # =======Buy===下ってるとき買わない=========================================
        if witch_deal == 'sell':
            if y_list_mean_s[x - 1] < y_list_mean_s[x]:
                if y > y_list_mean_s[x]:  # 5日移動平均を超えたら
                    buy_x_list.append(x)
                    add_up_buy_price += y
                    witch_deal = 'buy'
                    last_buy_price = y
                    buy_past_days = y_list_length - x
                    sum_up_charge += y * charge

        # ======Sell======上ってるとき売らない==============================================
        elif witch_deal == 'buy':
            if y_list_mean_s[x - 1] > y_list_mean_s[x]:
                if y_list_mean_s[x] > y:
                    sell_x_list.append(x)
                    add_up_sell_price += y
                    witch_deal = 'sell'
                    sum_up_charge += y * charge

    return witch_deal, x, y, y_list_mean_s, y_list_mean_l, y_list, buy_x_list, add_up_buy_price, y_list_length, sell_x_list, add_up_sell_price, last_buy_price, buy_past_days, sum_up_charge


def get_rsi(y_list):
    # RSIを計算
    # period = 14
    period = 42
    delta = y_list.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rsi_y_list = 100 * (avg_gain / (avg_gain + avg_loss))
    return rsi_y_list


def y_data(ticker):
    # https://note.com/misamisa333/n/n0d574c96b8d6
    return yfin.download(ticker, period=term, interval=bar)


# クラスのインスタンスを作成
my_obj = Plot()
