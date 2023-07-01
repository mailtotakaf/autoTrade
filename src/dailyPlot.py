import matplotlib.pyplot as plt
import pandas as pd
from yahoo_finance_api2 import share
from yahoo_finance_api2.exceptions import YahooFinanceError
from statistics import pstdev
import sys


class Plot:
    def __init__(self):
        ticker = 'PEN'
        bare_data = y_data_15(ticker)

        # グラフの描画
        plt.figure()
        plot_daily(bare_data, ticker)
        plt.title(ticker)

        # 15データ
        # bare_data15 = y_data_15(ticker)
        # y_list_15 = bare_data15['close']
        # plt.plot(y_list_15.index * 2.85, y_list_15)

        # グラフの表示
        plt.show()


def plot_daily(bare_data, ticker):
    # 手数料
    charge = 0.5 / 100

    plt.grid(True)

    y_list = bare_data['close']
    x_list = y_list.index
    y_list_high = bare_data['high']
    y_list_low = bare_data['low']

    buy_x_list = []
    sell_x_list = []
    prev_flg = None
    add_up_buy_price = 0
    add_up_sell_price = 0
    dealings = 0
    add_up_charge = 0
    default_buy_price = 0
    default_buy_charge = 0
    stdev = get_stdev(x_list, y_list)

    high_low = get_high_low_average(y_list_high, y_list_low)

    sell_base_high = 0
    buy_base_low = 0

    for (i, j) in enumerate(y_list, 0):
        # if sell_base_high < j:
        #     sell_base_high = j
        #
        # if buy_base_low > j:
        #     buy_base_low = j

        if i == 0:
            buy_x_list.append(i)
            add_up_buy_price = j
            prev_flg = "buy"
            dealings = 1
            add_up_charge = (j * charge)
            print("Buy:", j)
            print("Buy_charge:", (j * charge))
            default_buy_price = j
            default_buy_charge = j * charge
            # base
            sell_base_high = j
            buy_base_low = j
        else:
            # base
            if sell_base_high < j:
                sell_base_high = j

            if buy_base_low > j:
                buy_base_low = j

            # if (y_list[i - 1] + stdev) < y_list[i]:
            if buy_base_low + stdev < y_list[i]:
                if prev_flg != "buy":
                    buy_x_list.append(i)
                    add_up_buy_price += j
                    prev_flg = "buy"
                    dealings += 1
                    add_up_charge += (j * charge)
                    print("Buy:", j)
                    print("Buy_charge:", (j * charge))
            # elif (y_list[i - 1] - stdev) > y_list[i]:
            elif (sell_base_high - stdev) > y_list[i]:
                if prev_flg != "sell":
                    sell_x_list.append(i)
                    add_up_sell_price += j
                    prev_flg = "sell"
                    dealings += 1
                    add_up_charge += (j * charge)
                    print("Sell:", j)
                    print("Sell_charge:", (j * charge))
    if prev_flg == "buy":
        print("Sell_last:", j)
        print("Sell_charge:", (j * charge))
        add_up_sell_price += j

    plt.plot(x_list, y_list, '.', linestyle='solid', marker="o", markevery=sell_x_list, color="red")
    plt.plot(x_list, y_list, '.', linestyle='solid', marker="o", markevery=buy_x_list, color="green")

    plt.plot(x_list, y_list_high)
    plt.plot(x_list, y_list_low)

    print("=================================")
    print("stdev:", stdev)
    print("profit:", add_up_sell_price - add_up_buy_price)
    print("dealings:", dealings)
    print("add_up_charge:", add_up_charge)
    print("total-profit(profit-add_up_charge):", add_up_sell_price - add_up_buy_price - add_up_charge)
    print("---------------------------------")
    print("A: holding_case:", j - default_buy_price)
    print("B: holding_case_charge:", j * charge + default_buy_charge)
    print("holding_case A-B:", (j - default_buy_price) - (j * charge + default_buy_charge))


def get_high_low_average(y_list_high, y_list_low):
    data = y_list_high - y_list_low


def get_stdev(x_list, y_list):
    # 移動平均のプロット
    mean = y_list.rolling(3).mean()
    # meanIndexes = x_list - pd.DateOffset(days=2)
    # plt.plot(meanIndexes, mean)

    # plt.plot(x_list, mean)

    mean_arr = mean.array
    y_list_arr = y_list.array

    # 移動平均から見た標準偏差　TODO: 要調整
    devi_list = y_list_arr[2:] - mean_arr[2:]
    stdev = pstdev(devi_list)
    return stdev


def y_data_5(ticker):
    my_share = share.Share(ticker)
    symbol_data = None

    try:
        symbol_data = my_share.get_historical(
            share.PERIOD_TYPE_DAY, 1,
            share.FREQUENCY_TYPE_MINUTE, 5)
    except YahooFinanceError as e:
        print(e.message)
        sys.exit(1)

    df = pd.DataFrame(symbol_data)
    df["datetime"] = pd.to_datetime(df.timestamp, unit="ms")
    return df


def y_data_15(ticker):
    my_share = share.Share(ticker)
    symbol_data = None

    try:
        symbol_data = my_share.get_historical(
            share.PERIOD_TYPE_DAY, 1,
            share.FREQUENCY_TYPE_MINUTE, 15)
    except YahooFinanceError as e:
        print(e.message)
        sys.exit(1)

    df = pd.DataFrame(symbol_data)
    df["datetime"] = pd.to_datetime(df.timestamp, unit="ms")
    return df


# クラスのインスタンスを作成
my_obj = Plot()
