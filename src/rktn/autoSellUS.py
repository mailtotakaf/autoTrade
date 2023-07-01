from psycopg2 import Error

from src.db.postgres import get_cursor
import yfinance as yfin
import numpy as np

from src.rktn.Login import login
import time
from selenium.webdriver.common.by import By

term = '6mo'
bar = '1d'


class AutoSell:

    def plot(self, bare_data, ticker, sell_list):
        buy_past_days = 0
        y_list = bare_data['Close']
        x_list = y_list.index

        buy_x_list = []
        sell_x_list = []
        add_up_buy_price = 0
        add_up_sell_price = 0
        witch_deal = 'default'

        # 移動平均
        y_list_mean_s = y_list.rolling(window=5, min_periods=1).mean()
        y_list_mean_l = y_list.rolling(window=10, min_periods=1).mean()

        first_buy_price = 0
        last_buy_price = 0
        last_sell_price = 0
        deviationList = []
        last_y = 0
        last_x = 0
        y_list_length = len(y_list)
        print("y_list_length:", y_list_length)
        for (x, y) in enumerate(y_list, 0):
            if witch_deal == 'default':
                first_buy_price = y
                witch_deal = 'buy'
                last_buy_price = y
                add_up_buy_price += y

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
                        last_sell_price = y
                        print(last_sell_price - last_buy_price)
                else:
                    # 5日移動平均を割り込んだら売り
                    if y_list_mean_s[x] > y:
                        sell_x_list.append(x)
                        add_up_sell_price += y
                        witch_deal = 'sell'
                        last_sell_price = y
                        print(last_sell_price - last_buy_price)

            last_y = y
            last_x = x

        print('sell_x_list:', sell_x_list)
        print("len(y_list):", len(y_list))
        if (sell_x_list[-1] + 1) == len(y_list):
            print("売りアラート")
            sell_list.append(ticker)

        # 最後がbuyで終わった場合は、
        if witch_deal == 'buy':
            # 最後のlast_y売り
            add_up_sell_price += last_y
            sell_x_list.append(last_x)
            # print(last_y - last_buy_price)

        # strategy_profit = add_up_sell_price - add_up_buy_price
        # natural_profit = last_y - first_buy_price
        # print("strategy_profit:", strategy_profit)
        # print("普通に持ってたら：", natural_profit)
        # print("差額：", strategy_profit - natural_profit)
        # print("buy_past_days:", buy_past_days)

        # return strategy_profit, natural_profit, buy_past_days, stdev, last_y
        return sell_list

    def loop_check(self, ticker_list):
        sell_list = []
        for idx, ticker in enumerate(ticker_list, 0):
            try:
                print('ticker:', ticker)
                bare_data = yfin.download(ticker, period=term, interval=bar)
                sell_list = self.plot(bare_data, ticker, sell_list)
            except Exception as e:
                print('Error. ticker:', ticker)
                print(e)
        return sell_list

    def get_ticker_list(self):
        cursor, connector = get_cursor()
        try:
            cursor.execute("select ticker from ticker where hold = true")
            # cursor.execute(
            #     "select ticker from days_results where sheet_name = 'direct' and sell_past_days != 0 order by sell_past_days asc, diff desc")  # デバッグ要
            ticker_list = cursor.fetchall()
            return ticker_list
        except(Exception, Error) as error:
            print("Error: get_ticker_list.", error)
        finally:
            cursor.close()
            connector.close()

    def auto_sell_one(self, driver, ticker):

        try:
            time.sleep(2)
            el = driver.find_element(By.ID, 'myshortcut')
            # https://qiita.com/toimenbou/items/635a6e0e241149317e32
            driver.execute_script("arguments[0].click();", el)
            time.sleep(1)
            el = driver.find_element(By.PARTIAL_LINK_TEXT, "売り注文-米国株式")
            driver.execute_script("arguments[0].click();", el)
            time.sleep(2)

            # 数量
            # amount_el = driver.find_element(By.XPATH,
            #     "//tr/td/a[text()='" + ticker + "']/following-sibling::td[3]/ul/li[1]")
            # amount = amount_el.text

            el = driver.find_element(By.CSS_SELECTOR, "button[onclick*='tickerCd=" + ticker + "']")
            driver.execute_script("arguments[0].click();", el)
            time.sleep(2)

            # 数量
            el = driver.find_element(By.CSS_SELECTOR, ".pcmm-foreign-stock-bubble__txt span")
            amount = el.text

            el = driver.find_element(By.ID, "orderValueInput")
            el.clear()  # テキストボックス内の既存のテキストをクリア
            el.send_keys(amount)

            el = driver.find_element(By.ID, "price-market")
            driver.execute_script("arguments[0].click();", el)

            el = driver.find_element(By.ID, "password")
            el.clear()
            el.send_keys("4105")

            el = driver.find_element(By.CLASS_NAME, "pcmm-foreign-stock-chb-normal__label")
            driver.execute_script("arguments[0].click();", el)
            time.sleep(2)

            # 売りポチる
            el = driver.find_element(By.ID, "orderSubmit")
            driver.execute_script("arguments[0].click();", el)
            time.sleep(2)

            # メイン画面へ戻る
            el = driver.find_element(By.CLASS_NAME, "pcm-gl-logo-img")
            driver.execute_script("arguments[0].click();", el)
        except Exception as e:
            print('Error. ticker:', ticker)
            print(e)

    def loop_sell(self, sell_list):
        if len(sell_list) > 0:
            driver = login()
            for ticker_tuple in sell_list:
                ticker = ticker_tuple[0]
                self.auto_sell_one(driver, ticker)
        else:
            print("nothing to sell.")

    def __init__(self):
        ticker_list = self.get_ticker_list()
        sell_list = self.loop_check(ticker_list)
        # sell_list = [('PHI',), ('RGLD',), ('AXP',)]
        # sell_list = [('MPC',)]
        self.loop_sell(sell_list)


my_obj = AutoSell()
