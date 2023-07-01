import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import date, timedelta
from pandas_datareader import data as pdr
import yfinance as yfin
from statistics import pstdev
import mplfinance as mpf

class Plot:
    def __init__(self):
        ticker = '2531.T'
        bare_data = y_data(ticker)

        # グラフの描画
        plt.figure()
        plot2year(bare_data, ticker)
        plot_quarter(bare_data, ticker)

        # グラフの表示
        plt.tight_layout()
        plt.show()


def plot2year(bare_data, ticker):
    plt.subplot(2, 1, 1)  # 2行1列の1番目のサブプロット
    plt.grid(True)

    close_data = bare_data['Close']
    # 2分割
    split_2year = np.array_split(close_data, 2)
    # 近似プロットlast_year
    plt.plot(slope_plot_data(split_2year[0]))
    # 近似プロットquarters
    quarters = np.array_split(split_2year[1], 4)
    plt.plot(slope_plot_data(quarters[0]))
    plt.plot(slope_plot_data(quarters[1]))
    plt.plot(slope_plot_data(quarters[2]))
    plt.plot(slope_plot_data(quarters[3]))

    # # 2年分データプロット
    plt.plot(close_data)
    plt.title(ticker)


def plot_quarter(bare_data, ticker):
    # 手数料
    charge = 0.5 / 100

    plt.subplot(2, 1, 2)  # 2行1列の2番目のサブプロット
    plt.grid(True)

    # 2分割
    split_2year = np.array_split(bare_data, 2)
    # quarterプロット
    quarters = np.array_split(split_2year[1], 4)

    y_list = quarters[3]['Close']

    # クロス時点再現のために任意の箇所日付でスライス
    # y_list = y_list[0: 27]

    x_list = y_list.index

    y_list_high = quarters[3]['High']
    y_list_low = quarters[3]['Low']

    buy_x_list = []
    sell_x_list = []
    prev_flg = None
    add_up_buy_price = 0
    add_up_sell_price = 0
    dealings = 0
    add_up_charge = 0
    last_buy_price = 0
    default_buy_price = 0
    last_sell_price = 0
    stdev = get_stdev(x_list, y_list)
    for (i, j) in enumerate(y_list, 0):
        if i == 0:
            buy_x_list.append(i)
            add_up_buy_price += j
            prev_flg = "buy"
            dealings += 1
            add_up_charge += (j * charge)
            print("Buy, add_up_charge:", (j * charge))
            last_buy_price = j
            default_buy_price = j + (j * charge)
        else:
            # if y_list[i - 1] < y_list[i] and y_list[i - 2] < y_list[i]:

            # buy の場合は、"かつ、stdev以上"（買いすぎ防止）　
            # if y_list[i - 1] < y_list[i] and y_list[i - 2] < y_list[i] and (y_list[i - 1] + stdev) < y_list[i]:
            # stdevだけ
            # if (y_list[i - 1] + stdev) < y_list[i]:
            if (y_list[i - 1] + stdev) < y_list[i]:
                if prev_flg != "buy":
                    buy_x_list.append(i)
                    add_up_buy_price += j
                    prev_flg = "buy"
                    dealings += 1
                    add_up_charge += (j * charge)
                    print("Buy, add_up_charge:", (j * charge))
                    last_buy_price = j
            # elif y_list[i - 1] > y_list[i] and y_list[i - 2] > y_list[i]:

            # sellの場合は、"もしくは、stdev以下" （すぐ売る）：リアルタイム時にstdevが活きる予定
            # TODO: 2日連続で下落した瞬間に売る（リアルタイム時）
            # elif (y_list[i - 1] > y_list[i] and y_list[i - 2] > y_list[i]) or (y_list[i - 1] - stdev) > y_list[i]:
            elif (y_list[i - 1] - stdev) > y_list[i]:
                if prev_flg != "sell":
                    sell_x_list.append(i)
                    add_up_sell_price += j
                    prev_flg = "sell"
                    dealings += 1
                    add_up_charge += (j * charge)
                    print("Sell, add_up_charge:", (j * charge))
                    last_sell_price = j - (j * charge)
    if prev_flg == "buy":
        # add_up_sell_price += last_buy_price
        add_up_sell_price += j

    x_labels = x_list.strftime('%m-%d')
    plt.xticks(x_list, x_labels, rotation=90)
    plt.plot(x_list, y_list, '.', linestyle='solid', marker="o", markevery=sell_x_list, color="red")
    plt.plot(x_list, y_list, '.', linestyle='solid', marker="o", markevery=buy_x_list, color="green")

    # 移動平均
    y_list_mean_s = y_list.rolling(window=5, min_periods=1).mean()
    y_list_mean_l = y_list.rolling(window=10, min_periods=1).mean()
    plt.plot(x_list, y_list_mean_s, color="#faa")
    plt.plot(x_list, y_list_mean_l, color="#aaf")

    # plt.plot(x_list, y_list_high)
    # plt.plot(x_list, y_list_low)

    # 近似プロットmonth
    months = np.array_split(y_list, 3)
    plt.plot(slope_plot_data(months[0]))
    plt.plot(slope_plot_data(months[1]))
    plt.plot(slope_plot_data(months[2]))

    # RSI
    plt.twinx()
    rsi_y_list = get_rsi(y_list)
    plt.plot(x_list, rsi_y_list, linestyle='dotted', color="blue")

    # print("add_up_buy_price:", add_up_buy_price)
    # print("add_up_sell_price:", add_up_sell_price)
    print("stdev:", stdev)
    print("profit:", add_up_sell_price - add_up_buy_price)
    print("dealings:", dealings)
    print("add_up_charge:", add_up_charge)
    print("total-profit(profit-add_up_charge):", add_up_sell_price - add_up_buy_price - add_up_charge)
    # print("holding_case:", last_sell_price - default_buy_price)
    print("holding_case:", j - default_buy_price)


def get_stdev(x_list, y_list):
    # 移動平均のプロット
    mean = y_list.rolling(3).mean()

    # meanIndexes = x_list - pd.DateOffset(days=2)
    # plt.plot(meanIndexes, mean)

    mean_arr = mean.array
    y_list_arr = y_list.array

    # 4日移動平均から見た標準偏差　TODO: 要調整
    devi_list = y_list_arr[2:] - mean_arr[2:]
    stdev = pstdev(devi_list)
    # print("stdev:", stdev)
    return stdev


def get_slope(bare_data):
    # インデックスの配列を作成
    indices = np.arange(len(bare_data))

    # polyfit関数を使用して最小二乗法による回帰直線の係数を計算
    slope, _ = np.polyfit(indices, bare_data, 1)

    print("傾き:", slope)
    return slope


def slope_plot_data(bare_data):
    first_date = bare_data.index[0]
    end_date = bare_data.index[-1]
    first_val = bare_data[0]

    # 傾き
    slope = get_slope(bare_data)

    bare_len = len(bare_data)
    mod_end_val = first_val + slope * bare_len

    return pd.Series([first_val, mod_end_val],
                     index=[pd.Timestamp(first_date), pd.Timestamp(end_date)])


def y_data(ticker):
    yfin.pdr_override()

    today = date.today()
    startday = today - timedelta(days=730)

    pd_data = pdr.get_data_yahoo(ticker, startday)
    # close_data = pd_data['Close']
    # return close_data
    return pd_data

def get_rsi(y_list):
    # RSIを計算
    period = 14
    delta = y_list.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rsi_y_list = 100 * (avg_gain / (avg_gain + avg_loss))
    # df['RSI'] = rsi

    # チャートプロット
    apd_rsi = [
        mpf.make_addplot(rsi_y_list, panel=1, ylabel='RSI', color='b'),
        mpf.make_addplot([30] * len(rsi_y_list.index), panel=1, color='gray'),
        mpf.make_addplot([70] * len(rsi_y_list.index), panel=1, color='gray')
    ]
    return rsi_y_list


# クラスのインスタンスを作成
my_obj = Plot()
