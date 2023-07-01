import boto3
import matplotlib.pyplot as plt
import pandas as pd
import psycopg2
from psycopg2 import Error
from boto3.dynamodb.conditions import Key
from datetime import datetime

ticker = "BTC-JPY"

# mode = ""
mode = "plotMode"

term = '1d'
bar = '1m'


class Plot:
    def __init__(self):
        bare_data = scan_dynamo()
        rtn_profits = get_results(bare_data)
        if mode != "plotMode":
            insert_results(rtn_profits)


def get_results(bare_data):
    buy_past_days = 0

    df = pd.DataFrame(bare_data, index=range(len(bare_data)))
    y_list = df['buy_price']
    y_list_sell_price = df['sell']
    y_list_diff_per = df['diff']
    x_list = df['unix_time']

    buy_x_list = []
    sell_x_list = []
    add_up_buy_price = 0
    add_up_sell_price = 0
    witch_deal = 'default'

    # 移動平均
    y_list_mean_l = y_list.rolling(window=10, min_periods=1).mean()  # 未使用
    y_list_mean_s = y_list.rolling(window=5, min_periods=1).mean()

    first_buy_price = 0
    last_buy_price = 0
    deviationList = []
    last_y = 0
    last_x = 0
    y_list_length = len(y_list)
    for x in range(len(y_list)):
        y = y_list[x]
        if witch_deal == 'default':
            first_buy_price = y
            witch_deal = 'buy'
            last_buy_price = y
            add_up_buy_price += y
            buy_x_list.append(x)

        rtn = strategy_minutes(witch_deal, x, y, y_list_mean_s, y_list_mean_l, y_list, buy_x_list, add_up_buy_price,
                               y_list_length, sell_x_list, add_up_sell_price, last_buy_price, buy_past_days)

        witch_deal, x, y, y_list_mean_s, y_list_mean_l, y_list, buy_x_list, add_up_buy_price, y_list_length, sell_x_list, add_up_sell_price, last_buy_price, buy_past_days = rtn

        last_y = y
        last_x = x

        # deviation = y_list[x] - y_list_mean_s[x] # TypeError: unsupported operand type(s) for -: 'decimal.Decimal' and 'float'
        # dev_per = deviation / y_list_mean_s[x]
        # deviationList.append(dev_per)

    # stdev = np.std(deviationList)

    sell_past_days = 99
    if witch_deal == 'sell':
        sell_past_days = len(y_list) - sell_x_list[-1]

    # 最後がbuyで終わった場合は、
    if witch_deal == 'buy':
        # 最後のlast_y売り
        add_up_sell_price += last_y
        sell_x_list.append(last_x)

    strategy_profit = add_up_sell_price - add_up_buy_price
    natural_profit = last_y - first_buy_price
    strategy_per = strategy_profit / first_buy_price * 100
    natural_per = natural_profit / first_buy_price * 100
    diff_per = (strategy_profit - natural_profit) / last_y * 100
    print("strategy_profit:", strategy_profit)
    print("普通に持ってたら：", natural_profit)
    print("差額：", strategy_profit - natural_profit)
    print("買い回数：", len(buy_x_list))
    print("売り回数：", len(sell_x_list))
    buy_sell_cnt = len(buy_x_list) + len(sell_x_list)

    if mode == "plotMode":
        # x_labels = x_list
        x_labels = unix_time_format(x_list)
        plot(x_list, y_list_mean_s, y_list_mean_l, x_labels, y_list, sell_x_list, buy_x_list, y_list_sell_price, y_list_diff_per)

    return strategy_profit, natural_profit, buy_past_days, last_y, sell_past_days, strategy_per, natural_per, diff_per, buy_sell_cnt


def unix_time_format(x_list):
    formatted_times = []
    for unix_time in x_list:
        # Unix時間をPythonのdatetimeオブジェクトに変換
        dt_object = datetime.utcfromtimestamp(unix_time)
        # フォーマットを指定して文字列に変換
        formatted_time = dt_object.strftime("%m/%d %H:%M:%S")
        formatted_times.append(formatted_time)

    return formatted_times


def plot(x_list, y_list_mean_s, y_list_mean_l, x_labels, y_list, sell_x_list, buy_x_list, y_list_sell_price, y_list_diff_per):
    plt.figure()
    plt.grid(True)
    plt.xticks(x_list, x_labels, rotation=90)
    plt.legend(prop={'family': 'MS Gothic'})
    plt.title(ticker, fontname='MS Gothic')

    # plt.plot(x_list, y_list_mean_s, color="#faa")
    # plt.plot(x_list, y_list_mean_l, color="#aaf")
    plt.plot(x_list, y_list, '.', linestyle='solid', marker="o", markevery=sell_x_list, color="red")
    plt.plot(x_list, y_list, '.', linestyle='solid', marker="o", markevery=buy_x_list, color="black")

    plt.plot(x_list, y_list_sell_price, '.', linestyle='solid', color="red")

    # RSI
    plt.twinx()
    # plt.plot(x_list, rsi_y_list, linestyle='dotted', color="blue")
    # plt.plot(x_list, volume_list, linestyle='dotted', color="blue")
    plt.plot(x_list, y_list_diff_per, linestyle='dotted', color="blue")
    plt.show()


def strategy_minutes(witch_deal, x, y, y_list_mean_s, y_list_mean_l, y_list, buy_x_list, add_up_buy_price,
                     y_list_length,
                     sell_x_list, add_up_sell_price, last_buy_price, buy_past_days):
    try:
        # =======Buy===ただ1分前と比べるだけ=========================================
        if witch_deal == 'sell':
            if y_list[x - 1] < y_list[x]:
                buy_x_list.append(x)
                add_up_buy_price += y
                witch_deal = 'buy'
                last_buy_price = y
                buy_past_days = y_list_length - x

        # ======Sell======ただ1分前と比べるだけ==============================================
        elif witch_deal == 'buy':
            if y_list[x - 1] > y_list[x]:
                sell_x_list.append(x)
                add_up_sell_price += y
                witch_deal = 'sell'
    except Exception as e:
        print('Error.', e)
    return witch_deal, x, y, y_list_mean_s, y_list_mean_l, y_list, buy_x_list, add_up_buy_price, y_list_length, sell_x_list, add_up_sell_price, last_buy_price, buy_past_days


def insert_results(rtn_profits):
    cursor = postgres()
    try:
        strategy_profit, natural_profit, buy_past_days, last_price, sell_past_days, strategy_per, natural_per, diff_per, buy_sell_cnt = rtn_profits

        sql = "insert into minutes_results" \
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
              "create_timestamp" \
              ") values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, current_timestamp)"

        cursor.execute(sql, (
            ticker,
            round(strategy_profit),
            round(natural_profit),
            buy_past_days,
            round(strategy_profit - natural_profit),
            last_price,
            sell_past_days,
            strategy_per,
            natural_per,
            diff_per,
            0,
            0,
            buy_sell_cnt,
            0,
            "dynamo",
            term + "/" + bar
        ))
    except Exception as e:
        print('Error.', e)

    finally:
        connector.commit()
        cursor.close()
        connector.close()


def postgres():
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


def scan_dynamo():
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('Streams')
        response = table.query(
            KeyConditionExpression=Key('dummy').eq(1) & Key('unix_time').gt(0),
            ScanIndexForward=True,  # Set to False to get items in descending order
            # Limit=30  # Limit the result to 30 items
        )
        items = response['Items']
        return items
    except Exception as e:
        print(f"Error: {e}")
        return None


# クラスのインスタンスを作成
my_obj = Plot()
