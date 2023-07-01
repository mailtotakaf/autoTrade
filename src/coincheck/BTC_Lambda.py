# https://qiita.com/ti-ginkgo/items/7e15bdac6618c07534be

# レイヤー
# https://tech-deliberate-jiro.com/lambda-layer/

# Hello World アプリケーションのデプロイ
# https://docs.aws.amazon.com/ja_jp/serverless-application-model/latest/developerguide/serverless-getting-started-hello-world.html

import time
import requests
from psycopg2._psycopg import Error
from privateAPI import coincheck
from datetime import datetime, timedelta, timezone
import boto3
from boto3.dynamodb.conditions import Key

path_orders = '/api/exchange/orders'
path_balance = '/api/accounts/balance'

ticker_list = ["btc_jpy"]

# ticker_list = ["btc_jpy",
#                "etc_jpy",
#                "lsk_jpy",
#                "mona_jpy",
#                "plt_jpy",
#                "fnct_jpy",
#                "dai_jpy",
#                "wbtc_jpy"]

market_buy_amount = 330  # 0.005 BTC 以上


def lambda_handler(event, context):
# def main():
    old_flg = None
    judged_flg = None
    res = None

    try:
        hold_amount = get_hold_amount()
        time.sleep(1)  # Nonce
        if hold_amount > 0.0005:  # 0.005 BTC（最低買い量）の10%
            old_flg = "buy"
            judged_flg = "buy"
        else:
            old_flg = "sell"
            judged_flg = "sell"

        new_row = get_new_row()
        old_dynamo_row_list = scan_dynamo()

        if len(old_dynamo_row_list) > 0:
            judged_flg = get_judged(old_dynamo_row_list, new_row, judged_flg)
            # 連続で買ったりしないように、old_flgと比較する
            if judged_flg != old_flg:
                print("----------------------------------------------------------judged_flg:---", judged_flg)
                if old_flg == "sell":
                    res = buy()
                    print("buy()'s res:", res)
                    # res = "buy"
                elif old_flg == "buy":
                    res = sell(old_flg)
            print("")
        insert_dynamo(new_row, res)
    except(Exception, Error) as error:
        print("---------XXX-----------at init def Error. continue...", error)


def get_hold_amount():
    result = coincheck.get(path_balance)
    hold_amount = result['btc']
    return float(hold_amount)


def sell(old_flg):
    result = None
    try:
        hold_amount = get_hold_amount()
        time.sleep(1)  # Nonce
        params = {
            "pair": "btc_jpy",
            "order_type": "market_sell",
            "amount": hold_amount,
        }
        result = coincheck.post(path_orders, params)
        print(result)
        is_success = result['success']
        print("is_success sell:", is_success)
        if is_success:
            old_flg = "sell"
    except(Exception, Error) as error:
        print("---------XXX-----------sell Error:", error)
    return result


def buy():
    result = None
    try:
        params = {
            "pair": "btc_jpy",
            "order_type": "market_buy",
            "market_buy_amount": market_buy_amount,  # 量ではなく金額
        }
        result = coincheck.post(path_orders, params)
        print(result)
    except(Exception, Error) as error:
        print("---------XXX-----------buy Error:", error)
    return result


def get_new_row():
    rtn_list = get_new_data()  # tickerごとの結果リスト
    rtn_dict = rtn_list[0]  # とりあえず btc_jpy だけ

    buy_price = float(rtn_dict["buy_price"])
    sell_price = float(rtn_dict["sell_price"])
    diff_per = (buy_price - sell_price) / buy_price * float(100)

    new_row = (buy_price, sell_price, diff_per)
    return new_row


def get_judged(old_dynamo_row_list, new_row, judged_flg):
    try:
        now = datetime.now()
        formatted_now = now.strftime("%Y/%m/%d %H:%M:%S")
        new_buy_price = new_row[0]
        new_sell_price = new_row[1]
        new_diff_per = new_row[2]
        print(f"new_buy_price: {new_buy_price}/// now_time: {formatted_now}")

        old_row = old_dynamo_row_list[0]  # 直近のデータ
        old_dynamo_price = old_row["buy_price"]
        old_jp_time = old_row["jp_time"]
        print(f"old_dynamo_price: {old_dynamo_price}/// old_jp_time: {old_jp_time}")

        if judged_flg == "sell":
            # ======Buy======1分前と比較するだけ==============================================
            if new_buy_price > old_dynamo_price:
                judged_flg = "buy"
        else:
            # =======Sell===1分前と比較するだけ=========================================
            if new_buy_price < old_dynamo_price:
                judged_flg = "sell"
        print("judged_flg:", judged_flg)

    except(Exception, Error) as error:
        print("---------XXX-----------at get_judged Error.", error)
    return judged_flg


def get_new_data():
    rtn_list = []
    for idx, ticker in enumerate(ticker_list):
        sell_price = 0
        try:
            URL = 'https://coincheck.com/api/exchange/orders/rate'
            params = {'order_type': 'sell', 'pair': 'btc_jpy', 'amount': 1}
            params['pair'] = ticker
            data = requests.get(URL, params=params).json()
            sell_price = float(data['price'])
            # print("sell_price=", sell_price)

            params = {'order_type': 'buy', 'pair': 'btc_jpy', 'amount': 1}
            params['pair'] = ticker
            data = requests.get(URL, params=params).json()
            buy_price = float(data['price'])
            print("now_buy_price=", buy_price)

            rtn_dict = {'ticker': ticker,
                        'buy_price': buy_price,
                        'sell_price': sell_price
                        }
            rtn_list.append(rtn_dict)
        except(Exception, Error) as error:
            print(ticker, "Error:", error)

    return rtn_list


def insert_dynamo(row, res):
    print("insert_dynamo calling.")
    try:
        unix_time = int(time.time())
        client = boto3.client('dynamodb')
        client.put_item(
            TableName="Streams",
            Item={
                "dummy": {"N": str(1)},
                "buy_price": {"N": str(row[0])},
                "sell": {"N": str(row[1])},
                "diff": {"N": str(row[2])},
                "result": {"S": str(res)},
                "unix_time": {"N": str(unix_time)},
                "jp_time": {"S": str(jp_time(unix_time))},
            }
        )
        print("insert_dynamo inserted.")
    except(Exception, Error) as error:
        print("Error: insert_dynamo.", error)


def jp_time(unix_time):
    utc_time = datetime.utcfromtimestamp(float(unix_time))
    jp_time = utc_time.replace(tzinfo=timezone.utc) + timedelta(hours=9)
    return jp_time


def scan_dynamo():
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('Streams')
        response = table.query(
            KeyConditionExpression=Key('dummy').eq(1) & Key('unix_time').gt(0),
            ScanIndexForward=False,  # Set to False to get items in descending order
            Limit=30  # Limit the result to 30 items
        )
        items = response['Items']
        return items
    except Exception as e:
        print(f"Error: {e}")
        return None

# if __name__ == "__main__":
#     main()
