# 対象Tickerは株式新聞から選ぶ。
# このBTは： 5minごと。、trendごとにstrateguを変化させる。

import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yfin
import psycopg2
from psycopg2 import Error

plotModeSql = "select tj.ticker, tj.name from  ticker_jp tj where ticker in ('9994.T');"

# 最小取引単位
div_dict = {
    "9994.T": 0.5,
    "9432.T": 0.1,
}

term = '2d'
bar = '5m'
start_date = "2023-12-26"
end_date = "2023-12-27" \
           "" \
           "z1  "


def strategy_minutes(witch_deal, x, y, y_list_mean_s, y_list_mean_m, y_list_mean_l, y_list, buy_x_list,
                     add_up_buy_price, y_list_length, sell_x_list, add_up_sell_price, last_buy_price, sum_up_charge,
                     ticker, memory_price, up_count, trend):
    if x > 0:
        if (y - round(y_list[x - 1], 1)) < (-1 * 2 * div_dict[ticker]) \
                or (witch_deal == "buy" and memory_price > y) or trend == "down":
            trend = "down"
            up_count = 0
        # elif witch_deal == 'sell' and ((y - memory_price) >= (div_dict[ticker])):
        elif witch_deal == 'sell' and ((y - memory_price) >= (div_dict[ticker])) or trend == "up":
            trend = "up"
        else:
            trend = "range"
            up_count = 0
        print(f"{x} trend:{trend} {y} / memory_price: {memory_price}")

    if trend == "range":
        # ======Buy====================================================
        if witch_deal == 'sell':
            if round((y - memory_price), 1) <= (-1 * div_dict[ticker]):
                buy_x_list.append(x)
                add_up_buy_price += y
                witch_deal = 'buy'
                last_buy_price = y
                memory_price = y  # リセット
                print(f"range_buy. {y}")

        # ======Sell====================================================
        elif witch_deal == 'buy':
            if (y - memory_price) > div_dict[ticker]:
                sell_x_list.append(x)
                add_up_sell_price += y
                witch_deal = 'sell'
                memory_price = y  # リセット
                print(f"range_sell. {y}")

    elif trend == "up":
        if witch_deal == 'sell':
            buy_x_list.append(x)
            add_up_buy_price += y
            witch_deal = 'buy'
            last_buy_price = y
            memory_price = y  # リセット
            print(f"up_buy. {y}")

    elif trend == "down":
        # down時は売りだけ
        if witch_deal == 'buy':
            sell_x_list.append(x)
            add_up_sell_price += y
            witch_deal = 'sell'
            memory_price = y  # リセット
            print(f"down_sell. {y}")

        if y > round(y_list[x - 1], 1):
            trend = "range"
            memory_price = y  # リセット
        elif y == round(y_list[x - 1], 1):
            trend = "up"
            memory_price = y  # リセット

    else:
        print("trend定義なし？")

    return witch_deal, x, y, y_list_mean_s, y_list_mean_l, y_list, buy_x_list, add_up_buy_price, y_list_length, \
        sell_x_list, add_up_sell_price, last_buy_price, sum_up_charge, memory_price, up_count, trend


def loop_check(ticker_list):
    for idx, tickers in enumerate(ticker_list, 0):
        try:
            print('tickers:', tickers)
            bare_data = y_data(tickers[0])
            get_results(bare_data, tickers[0], tickers[1])

        except Exception as e:
            print('Error. ticker:', tickers)
            print(e)


def get_results(bare_data, ticker, company_name):
    memory_price = 0
    up_count = 0
    trend = ""
    y_list = bare_data['Close']
    x_list = []
    hours = 18

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
    last_y = 0
    last_x = 0
    y_list_length = len(y_list)
    for (x, y) in enumerate(y_list, 0):
        # print("")
        # print(f"y: {y}")
        y = round(y, 1)  # 四捨五入
        if witch_deal == 'default':
            first_buy_price = y
            witch_deal = 'buy'
            last_buy_price = y
            add_up_buy_price += y
            buy_x_list.append(x)
            memory_price = y
            up_count = 0
            trend = ""

        rtn = strategy_minutes(witch_deal, x, y, y_list_mean_s, y_list_mean_m, y_list_mean_l, y_list, buy_x_list,
                               add_up_buy_price, y_list_length, sell_x_list, add_up_sell_price, last_buy_price,
                               sum_up_charge, ticker, memory_price, up_count, trend)

        witch_deal, x, y, y_list_mean_s, y_list_mean_l, y_list, buy_x_list, add_up_buy_price, y_list_length, \
            sell_x_list, add_up_sell_price, last_buy_price, sum_up_charge, \
            memory_price, up_count, trend = rtn

        last_y = y
        last_x = x

    # 最後がbuyで終わった場合は、
    if witch_deal == 'buy':
        # 最後のlast_y売り
        add_up_sell_price += last_y
        sell_x_list.append(last_x)

    strategy_profit = add_up_sell_price - add_up_buy_price
    natural_profit = last_y - first_buy_price
    print("strategy_profit:", strategy_profit)
    print("普通に持ってたら：", natural_profit)
    print("差額：", strategy_profit - natural_profit)
    print("買い回数：", len(buy_x_list))
    print("売り回数：", len(sell_x_list))

    x_labels = [timestamp.strftime('%H-%M') for timestamp in x_list]
    plot(x_list, y_list_mean_s, y_list_mean_m, y_list_mean_l, x_labels, y_list, sell_x_list, buy_x_list, ticker,
         company_name)


def plot(x_list, y_list_mean_s, y_list_mean_m, y_list_mean_l, x_labels, y_list, sell_x_list, buy_x_list, ticker,
         company_name):
    plt.figure()
    plt.grid(True)
    plt.xticks(x_list, x_labels, rotation=90)
    plt.legend(prop={'family': 'MS Gothic'})
    # plt.title(ticker + ":" + company_name, fontname='MS Gothic')
    plt.title(ticker, fontname='MS Gothic')

    plt.plot(x_list, y_list_mean_s, color="#8f8")
    plt.plot(x_list, y_list_mean_m, color="#f88")
    # plt.plot(x_list, y_list_mean_l, color="#88f")
    plt.plot(x_list, y_list, '.', linestyle='solid', marker="o", markevery=sell_x_list, color="red")
    plt.plot(x_list, y_list, '.', linestyle='solid', marker="o", markevery=buy_x_list, color="black")
    plt.show()


def y_data(ticker):
    return yfin.download(ticker, period=term, interval=bar, start=start_date, end=end_date)


def postgres():
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


class Plot:
    def __init__(self):
        ticker_list = get_ticker_list()
        loop_check(ticker_list)


# クラスのインスタンスを作成
my_obj = Plot()
