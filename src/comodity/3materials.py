# http://api.scraperlink.com/investpy/
# https://qiita.com/danishi/items/07dd1b2f2a28255f7a85

import matplotlib.pyplot as plt
from psycopg2 import Error
import urllib.request
import json
from datetime import datetime, timedelta


class Plot:
    def __init__(self):
        self.loop_check()

    def loop_check(self):
        global max, min
        ticker_list = ['Gold', 'Silver', 'Platinum']

        d_data_list_dict = {}
        all_tickers_middles = []
        for idx, ticker in enumerate(ticker_list, 0):
            print('ticker:', ticker)
            d_data_list = []

            try:
                body = getMaterialData(self, ticker)
                x_list = [datetime.strptime(d['rowDateTimestamp'], "%Y-%m-%dT%H:%M:%SZ") for d in body['data']]
                y_list = [float(d['last_close'].replace(',', '')) for d in body['data']]

                max_val = max(y_list)
                min_val = min(y_list)
                middle_val = (max_val + min_val) / 2
                d_data_list.append(y_list)
                d_data_list.append(x_list)
                d_data_list.append(middle_val)
                d_data_list.append(ticker)

                all_tickers_middles.append(middle_val)
            except(Exception, Error) as error:
                print("Error: get_ticker_list.", error)

            d_data_list_dict[ticker] = d_data_list

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

        plot(shifted_d_list_dict)


def plot(d_data_list_dict):
    colors = ['#888', '#00f', '#0f0', '#0ff', '#f00']
    plt.figure()
    plt.grid(True)
    plt.tight_layout()
    # plt.title("Indexes")

    for idx, (key, val) in enumerate(d_data_list_dict.items()):
        y_list = val[0]
        x_list = val[1]
        # plt.plot(x_list, y_list, color=colors[idx % 5], label=val[2])
        plt.plot(x_list, y_list, label=val[2])
        plt.xticks(x_list, rotation=90)

    # 凡例を表示
    plt.legend()
    plt.show()


def getMaterialData(self, material):
    now = datetime.now()
    six_months_ago = now - timedelta(days=30 * 6)
    start_date = six_months_ago.strftime("%Y-%m-%d")
    end_date = now.strftime("%Y-%m-%d")

    url = 'http://api.scraperlink.com/investpy/?email=mailtotakaf@gmail.com&type=historical_data&product=commodities' \
          '&from_date=' + start_date + '&to_date=' + end_date + '&time_frame=Daily&name=' + material

    try:
        with urllib.request.urlopen(url) as response:
            body = json.loads(response.read())
            return body
    except Exception as e:
        print("exception:", e)


# クラスのインスタンスを作成
my_obj = Plot()
