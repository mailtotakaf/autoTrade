from collections import Counter

import yfinance as yfin
from datetime import date, timedelta
from pandas_datareader import data as pdr
import matplotlib.pyplot as plt


# クラスのインスタンスを作成
class Edges:
    def __init__(self):
        ticker = 'EXAI'
        days = 360
        close_data = y_data(ticker, days)
        edge_list = getEdges(close_data)

        max_value = max(edge_list)
        min_value = min(edge_list)
        print("最大値:", max_value)
        print("最小値:", min_value)
        value_depth = max_value - min_value
        print("最大値 - 最小値:", value_depth)
        freq_num = 20
        freq_depth = value_depth / freq_num
        print("freq_depth:", freq_depth)

        # 現在価格
        current_price = close_data[-1]
        print("current_price:", current_price)

        # 度数分布表
        counter(edge_list, freq_depth)
        # プロット
        plot(edge_list, ticker, freq_num, current_price, days)


def getEdges(close_data):
    # close_data = bare_data['Close']
    # arr = close_data.array
    edge_list = []
    for i, d in enumerate(close_data):
        # print(d)
        one = close_data[i - 2]
        two = close_data[i - 1]
        three = close_data[i]

        if two < one and two < three:
            edge_list.append(two)

        if two > one and two > three:
            edge_list.append(two)

    return edge_list


def plot(edge_list, ticker, freq_num, current_price, days):
    plt.hist(edge_list, bins=freq_num, color='blue', edgecolor='black')  # binsはビン（階級）の数を指定します
    plt.xlabel('$')
    plt.ylabel('frequency')
    title = ticker + ":" + str(days)
    plt.title(title)

    # 赤色のラインを追加
    plt.axvline(x=current_price, color='red', linestyle='-', label=f'current_price:{round(current_price, 2)}')
    # 凡例を表示
    plt.legend()

    # グラフを表示
    plt.show()


def counter(edge_list, freq_depth):
    # 度数幅を指定
    # bin_width = 3  # 例: 1単位ごとに度数を計算
    # # データを度数幅に合わせてバケットに分ける
    # buckets = [(x // bin_width) * bin_width for x in edge_list]
    # データを度数幅に合わせてバケットに分ける
    buckets = [(x // freq_depth) * freq_depth for x in edge_list]

    # バケットごとの度数分布を計算
    data_counts = Counter(buckets)

    # データの度数分布を表示
    for bucket, count in sorted(data_counts.items()):
        print(f'{bucket}-{bucket + freq_depth}: {count}回')


def y_data(ticker, days):
    yfin.pdr_override()

    today = date.today()
    startday = today - timedelta(days=days)

    pd_data = pdr.get_data_yahoo(ticker, startday)
    close_data = pd_data['Close']
    return close_data
    # return pd_data


my_obj = Edges()
