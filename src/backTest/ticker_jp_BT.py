import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yfin
import psycopg2
from psycopg2 import Error
from datetime import datetime
from yahooquery import Ticker
import const

sheet_name = "ticker_jp"
charge = 0.15 / 100

# strategy = "simple"
# strategy = ""
strategy = "memory"

# mode = ""
mode = "plotMode"

# plotModeSql = "select ticker, name from ticker_jp where ticker in ('1720.T', '3907.T', '5139.T', '5997.T', '6558.T', '7211.T', '9994.T')"
# plotModeSql = "select * from months_results where last_price < 1000 and l_slope < m_slope and m_slope > 100 and last_rsi < 40 order by last_rsi asc;"
# plotModeSql = "select * from months_results where hyouka = 1 order by last_rsi;"
# plotModeSql = "select mr.ticker, mr.name from months_results mr inner join ticker_jp tj on mr.ticker = tj.ticker " \
#               "where tj.industory_kbn2 in ('銀行 ') and last_price < 1000 and last_rsi < 50 order by mr.last_rsi asc;"
# plotModeSql = "select * from months_results mr inner join ticker_jp tj on mr.ticker = tj.ticker left join rktn_hyouka rh " \
# "on rh.ticker = mr.ticker where tj.industory_kbn2 in ('鉄鋼・非鉄 ') and last_price < 1000 and last_rsi < 50 " \
# "and rh.hyouka != 3 order by mr.last_rsi asc;"
# plotModeSql = "select mr.ticker, mr.name from months_results mr inner join ticker_jp tj on mr.ticker = tj.ticker " \
#               "left join rktn_hyouka rh on rh.ticker = mr.ticker where tj.industory_kbn2 in ('情報通信・サービスその他 ') " \
#               "and tj.industory_kbn1 = '情報・通信業' and last_price < 1000 and last_rsi < 40 and per != 0 and hyouka != 3 order by rh.per asc;"
# plotModeSql = "select mr.ticker, mr.name from months_results mr inner join ticker_jp tj on mr.ticker = tj.ticker " \
#               "left join rktn_hyouka rh on rh.ticker = mr.ticker where tj.industory_kbn2 in ('情報通信・サービスその他 ') " \
#               "and tj.industory_kbn1 = 'サービス業' and last_price < 1000 and last_rsi < 40 and hyouka != 3 and per != 0 order by rh.per asc;"
# plotModeSql = "select mr.ticker, mr.name from months_results mr inner join ticker_jp tj on mr.ticker = tj.ticker " \
#               "left join rktn_hyouka rh on rh.ticker = mr.ticker where tj.industory_kbn2 in ('機械 ') " \
#               "and last_price < 1000 and last_rsi < 40 and per != 0 order by rh.per asc;"
# plotModeSql = "select mr.ticker, mr.name from months_results mr inner join ticker_jp tj on mr.ticker = tj.ticker left join rktn_hyouka rh on rh.ticker = mr.ticker order by mr.p_up_per desc;"
# plotModeSql = "select tj.ticker, tj.name from  ticker_jp tj where ticker in ('2670.T', '2991.T', '3180.T', '3939.T', '4334.T', '4440.T', '4838.T', '5830.T', '6181.T', '6535.T', '7211.T', '7279.T', '7804.T', '8381.T', '9432.T', '9994.T');"
# plotModeSql = "select tj.ticker, tj.name from  ticker_jp tj where ticker in ('4173.T', '3628.T', '4334.T');"
plotModeSql = "select tj.ticker, tj.name from  ticker_jp tj where ticker in ('9994.T');"

# db_name = 'months_results'
# term = '6mo'
# bar = '1d'

# db_name = 'days_results'
# term = '6mo'
# bar = '1d'

db_name = 'minutes_results'
term = '2d'
bar = '5m'


class Plot:
    def __init__(self):
        start = time.time()

        ticker_list = self.get_ticker_list()
        self.loop_check(ticker_list)
        if mode != "plotMode":
            # 業界別変化率
            p_up_per_avg_row = self.select_p_up_per_avg()
            self.insert_p_up_per_avg(p_up_per_avg_row)
            p_up_per_avg_list = self.get_p_up_per_avg_list()
            self.plot_p_up_per_avg_list(p_up_per_avg_list)
        print("処理時間：", time.time() - start)

    def plot_p_up_per_avg_list(self, p_up_per_avg_list):
        bank_list = []
        electric_gus_list = []
        iron_metal_list = []
        car_list = []
        trade_whole_list = []
        transport_list = []
        energy_list = []
        material_sci_list = []
        construct_list = []
        machine_list = []
        food_list = []
        retail_list = []
        real_est_list = []
        finance_list = []
        pharma_list = []
        it_list = []
        elec_precision_list = []
        none_list = []
        create_timestamp_list = []
        x_labels = []

        for row in p_up_per_avg_list:
            bank_list.append(row[0])
            electric_gus_list.append(row[1])
            iron_metal_list.append(row[2])
            car_list.append(row[3])
            trade_whole_list.append(row[4])
            transport_list.append(row[5])
            energy_list.append(row[6])
            material_sci_list.append(row[7])
            construct_list.append(row[8])
            machine_list.append(row[9])
            food_list.append(row[10])
            retail_list.append(row[11])
            real_est_list.append(row[12])
            finance_list.append(row[13])
            pharma_list.append(row[14])
            it_list.append(row[15])
            elec_precision_list.append(row[16])
            none_list.append(row[17])
            create_timestamp_list.append(row[18])
            datetime_obj = datetime.strptime(str(row[18]), "%Y-%m-%d %H:%M:%S.%f")
            x_labels.append(datetime_obj.strftime("%m/%d-%H:%M"))

        plt.figure()
        plt.grid(True)
        plt.xticks(create_timestamp_list, x_labels, rotation=90)
        plt.legend(prop={'family': 'MS Gothic'})
        plt.title("price_up_per_average")

        plt.plot(create_timestamp_list, bank_list, label="bank")
        plt.plot(create_timestamp_list, electric_gus_list, label="electric_gus")
        plt.plot(create_timestamp_list, iron_metal_list, label="iron_metal")
        plt.plot(create_timestamp_list, car_list, label="car")
        plt.plot(create_timestamp_list, trade_whole_list, label="trade_whole")
        plt.plot(create_timestamp_list, transport_list, label="transport")
        plt.plot(create_timestamp_list, energy_list, label="energy")
        plt.plot(create_timestamp_list, material_sci_list, label="material_sci")
        plt.plot(create_timestamp_list, construct_list, label="construct")
        plt.plot(create_timestamp_list, machine_list, label="machine")
        plt.plot(create_timestamp_list, food_list, label="food")
        plt.plot(create_timestamp_list, retail_list, label="retail")
        plt.plot(create_timestamp_list, real_est_list, label="real_est")
        plt.plot(create_timestamp_list, finance_list, label="finance")
        plt.plot(create_timestamp_list, pharma_list, label="pharma")
        plt.plot(create_timestamp_list, it_list, label="it")
        plt.plot(create_timestamp_list, elec_precision_list, label="elec_precision")
        plt.plot(create_timestamp_list, none_list, label="none")
        plt.legend()
        plt.show()

    def get_p_up_per_avg_list(self):
        try:
            cursor = self.postgres()
            sql = "select * from p_up_per_avg"
            cursor.execute(sql)
            list = cursor.fetchall()
            return list
        except(Exception, Error) as error:
            print("Error: get_p_up_per_avg_list.", error)
        finally:
            cursor.close()
            connector.close()

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
        cursor = self.postgres()

        for idx, tickers in enumerate(ticker_list, 0):
            try:
                print('tickers:', tickers)
                bare_data = y_data(tickers[0])

                if db_name == 'months_results':
                    rtn_profits = get_months_results(bare_data)
                    self.insert_months_results(rtn_profits, tickers[0], tickers[1])
                else:
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

    def insert_months_results(self, rtn_dict, ticker, name):
        sql = "insert into " + db_name + \
              " (" \
              "ticker," \
              "name," \
              "m_l_per," \
              "m_price," \
              "last_price," \
              "p_up_per," \
              "last_rsi," \
              "l_slope," \
              "m_slope," \
              "over_m_pd," \
              "create_timestamp" \
              ") values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, current_timestamp)"

        cursor.execute(sql, (
            ticker,
            name,
            rtn_dict['m_l_per'],
            rtn_dict['m_price'],
            rtn_dict['last_price'],
            rtn_dict['p_up_per'],
            rtn_dict['last_rsi'],
            rtn_dict['l_slope'],
            rtn_dict['m_slope'],
            rtn_dict['over_m_price_past_days']
        ))

    def select_p_up_per_avg(self):
        try:
            cursor = self.postgres()
            sql = "select tj.industory_kbn2, avg(mr.p_up_per) as p_up_per_avg from months_results mr " \
                  "inner join ticker_jp tj on mr.ticker = tj.ticker group by tj.industory_kbn2 order by avg(mr.p_up_per) desc;"
            cursor.execute(sql)
            row = cursor.fetchall()
            return row
        except(Exception, Error) as error:
            print("Error: select_p_up_per_avg.", error)
        finally:
            cursor.close()
            connector.close()

    def insert_p_up_per_avg(self, row):
        try:
            cursor = self.postgres()
            sql = "insert into p_up_per_avg " \
                  " (" \
                  "bank," \
                  "electric_gus," \
                  "iron_metal," \
                  "car," \
                  "trade_whole," \
                  "transport," \
                  "energy," \
                  "material_sci," \
                  "construct," \
                  "machine," \
                  "food," \
                  "retail," \
                  "real_est," \
                  "finance," \
                  "pharma," \
                  "it," \
                  "elec_precision," \
                  "none," \
                  "create_timestamp" \
                  ") values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, current_timestamp)"

            cursor.execute(sql, (
                get_value_by_key(row, '銀行 '),
                get_value_by_key(row, '電力・ガス '),
                get_value_by_key(row, '鉄鋼・非鉄 '),
                get_value_by_key(row, '自動車・輸送機 '),
                get_value_by_key(row, '商社・卸売 '),
                get_value_by_key(row, '運輸・物流 '),
                get_value_by_key(row, 'エネルギー資源 '),
                get_value_by_key(row, '素材・化学 '),
                get_value_by_key(row, '建設・資材 '),
                get_value_by_key(row, '機械 '),
                get_value_by_key(row, '食品 '),
                get_value_by_key(row, '小売 '),
                get_value_by_key(row, '不動産 '),
                get_value_by_key(row, '金融（除く銀行） '),
                get_value_by_key(row, '医薬品 '),
                get_value_by_key(row, '情報通信・サービスその他 '),
                get_value_by_key(row, '電機・精密 '),
                get_value_by_key(row, '')
            ))
            connector.commit()
        except(Exception, Error) as error:
            print("Error: insert_p_up_per_avg.", error)
        finally:
            cursor.close()
            connector.close()


def get_value_by_key(row, key):
    for item in row:
        if item[0] == key:
            return item[1]
    return None


def get_results(bare_data, ticker, company_name):
    up_price_memory = 0
    down_price_memory = 0
    buy_past_days = 0
    y_list = bare_data['Close']
    volume_list = bare_data['Volume']
    x_list = []
    try:
        buy_strategy = const.buy_strategy_dict[ticker]
        sell_strategy = const.sell_strategy_dict[ticker]
    except:
        buy_strategy = 1.002
        sell_strategy = 1.002


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
            up_price_memory = y

        rtn = None
        if db_name == 'minutes_results':
            rtn = strategy_minutes(witch_deal, x, y, y_list_mean_s, y_list_mean_m, y_list_mean_l, y_list, buy_x_list,
                                   add_up_buy_price,
                                   y_list_length, sell_x_list, add_up_sell_price, last_buy_price, buy_past_days,
                                   rsi_y_list, sum_up_charge, up_price_memory, down_price_memory, buy_strategy, sell_strategy)
        else:
            rtn = strategy_days(witch_deal, x, y, y_list_mean_s, y_list_mean_l, y_list, buy_x_list, add_up_buy_price,
                                y_list_length, sell_x_list, add_up_sell_price, last_buy_price, buy_past_days,
                                sum_up_charge)

        witch_deal, x, y, y_list_mean_s, y_list_mean_l, y_list, buy_x_list, add_up_buy_price, y_list_length, \
            sell_x_list, add_up_sell_price, last_buy_price, buy_past_days, sum_up_charge, up_price_memory, down_price_memory = rtn

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
    buy_strategy = strategy_profit / first_buy_price * 100
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

    return strategy_profit, natural_profit, buy_past_days, last_y, sell_past_days, buy_strategy, natural_per, diff_per, last_rsi, buy_sell_cnt, volume, stdev


def get_months_results(bare_data):
    y_list = bare_data['Close']
    rsi_y_list = get_rsi(y_list)

    # 移動平均
    y_list_mean_l = y_list.rolling(window=75, min_periods=1).mean()
    y_list_mean_m = y_list.rolling(window=25, min_periods=1).mean()
    # y_list_mean_s = y_list.rolling(window=5, min_periods=1).mean()

    m_l_per = y_list_mean_m[-1] / y_list_mean_l[-1] * 100
    start_price = y_list[0]
    m_price = y_list_mean_m[-1]
    last_price = y_list[-1]
    last_rsi = rsi_y_list[-1]
    l_slope = y_list_mean_l[-1] / y_list_mean_l[-2] * 100
    m_slope = y_list_mean_m[-1] / y_list_mean_m[-2] * 100
    p_up_per = (y_list[-1] - y_list[-2]) / y_list[-1] * 100

    over_m_price_past_days = 0
    y_list_len = len(y_list)
    ps_flg = False
    for i, v in enumerate(y_list):
        if ps_flg:
            if y_list[i] < y_list_mean_m[i]:
                ps_flg = False
        else:
            if y_list[i] > y_list_mean_m[i]:
                over_m_price_past_days = y_list_len - i
                ps_flg = True

    m_l_per = round(m_l_per, 2)
    m_price = round(m_price)
    last_price = round(last_price)
    start_price = round(start_price)
    l_slope = round(l_slope, 2)
    m_slope = round(m_slope, 2)
    p_up_per = round(p_up_per, 3)
    rtn_dict = {"m_l_per": m_l_per, "m_price": m_price, "last_price": last_price, "p_up_per": p_up_per,
                "start_price": start_price,
                "last_rsi": last_rsi, "l_slope": l_slope, "m_slope": m_slope,
                "over_m_price_past_days": over_m_price_past_days}
    return rtn_dict


def get_volume(volume_list):
    volume = 0
    if max(volume_list) > 1000:
        scaled_volume_list = [x / 10000 for x in volume_list]
        volume = sum(scaled_volume_list)
    else:
        volume = sum(volume_list)
    return volume


def plot(x_list, y_list_mean_s, y_list_mean_m, y_list_mean_l, x_labels, y_list, sell_x_list, buy_x_list, ticker,
         company_name,
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


def strategy_minutes(witch_deal, x, y, y_list_mean_s, y_list_mean_m, y_list_mean_l, y_list, buy_x_list,
                     add_up_buy_price,
                     y_list_length,
                     sell_x_list, add_up_sell_price, last_buy_price, buy_past_days, rsi_y_list, sum_up_charge,
                     up_price_memory, down_price_memory, buy_strategy, sell_strategy):
    if strategy == "simple":
        # # =======Buy===買うときは15分前と比較（移動平均s が下がってるとき以外）=========================================
        if witch_deal == 'sell':
            if y_list_mean_s[x - 1] < y_list_mean_s[x]:  # 移動平均S が上がってるときだけ
                if y > y_list[x - 3]:
                    buy_x_list.append(x)
                    add_up_buy_price += y
                    witch_deal = 'buy'
                    last_buy_price = y
                    buy_past_days = y_list_length - x
                    sum_up_charge += y * charge

        # ======Sell======売るときは5分前と比較==============================================
        elif witch_deal == 'buy':
            if y < y_list[x - 3]:
                sell_x_list.append(x)
                add_up_sell_price += y
                witch_deal = 'sell'
                sum_up_charge += y * charge

        # =======Buy===1分前と比較するだけ=========================================
        # if witch_deal == 'sell':
        #     if y > y_list[x - 1]:
        #         buy_x_list.append(x)
        #         add_up_buy_price += y
        #         witch_deal = 'buy'
        #         last_buy_price = y
        #         buy_past_days = y_list_length - x
        #         sum_up_charge += y * charge
        #
        # # ======Sell======上ってるとき売らない==============================================
        # elif witch_deal == 'buy':
        #     if y_list_mean_s[x - 1] > y_list_mean_s[x]:
        #         if y_list_mean_s[x] > y:
        #             sell_x_list.append(x)
        #             add_up_sell_price += y
        #             witch_deal = 'sell'
        #             sum_up_charge += y * charge

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
    elif strategy == "memory":
        # ======Buy======売った時からの最低値から10円上がったら買い==============================================
        if witch_deal == 'sell':
            # if (y - down_price_memory) > 10:
            if (y/down_price_memory) > buy_strategy:
                buy_x_list.append(x)
                add_up_buy_price += y
                witch_deal = 'buy'
                last_buy_price = y
                buy_past_days = y_list_length - x
                sum_up_charge += y * charge
                up_price_memory = y  # リセット

            if down_price_memory > y:
                down_price_memory = y

        # ======Sell======買った時からの最高値から10円下がったら売り==============================================
        elif witch_deal == 'buy':
            # if (up_price_memory - y) > 10:
            if (up_price_memory/y) > sell_strategy:
                sell_x_list.append(x)
                add_up_sell_price += y
                witch_deal = 'sell'
                sum_up_charge += y * charge
                down_price_memory = y  # リセット

            if up_price_memory < y:
                up_price_memory = y
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

    return witch_deal, x, y, y_list_mean_s, y_list_mean_l, y_list, buy_x_list, add_up_buy_price, y_list_length, \
        sell_x_list, add_up_sell_price, last_buy_price, buy_past_days, sum_up_charge, up_price_memory, down_price_memory


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

    yfin_data = yfin.download(ticker, period=term, interval=bar)
    # return yfin.download(ticker, period=term, interval=bar, start="2023-11-13", end="2023-11-15") # TODO: デバッグ用

    # yq_data = Ticker(ticker).valuation_measures
    # print("yq_data:", yq_data)
    return yfin_data


# クラスのインスタンスを作成
my_obj = Plot()
