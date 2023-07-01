from psycopg2 import Error

from src.db.postgres import get_cursor
import yfinance as yfin
import numpy as np

from src.rktn.Login import login
import time
from selenium.webdriver.common.by import By

term = '6mo'
bar = '1d'

sheet_name = 'nikkei500'
class AutoBuy:

    def plot(self, bare_data, ticker, buy_list):
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
            buy_list.append(ticker)

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
        return buy_list

    def loop_check(self, ticker_list):
        buy_list = []
        for idx, ticker in enumerate(ticker_list, 0):
            try:
                print('ticker:', ticker)
                bare_data = yfin.download(ticker, period=term, interval=bar)
                buy_list = self.plot(bare_data, ticker, buy_list)
            except Exception as e:
                print('Error. ticker:', ticker)
                print(e)
        return buy_list

    def get_ticker_list(self):
        cursor, connector = get_cursor()
        try:
            cursor.execute("select dra.ticker from days_results dra inner join ticker t on dra.ticker = t.ticker "
"where dra.sheet_name = '" + sheet_name + "' and strategy_per > 0 and last_price < 2000 and buy_past_days = 1 order by dra.buy_past_days asc")
            ticker_list = cursor.fetchall()
            return ticker_list
        except(Exception, Error) as error:
            print("Error: get_ticker_list.", error)
        finally:
            cursor.close()
            connector.close()

    def auto_by_one(self, driver, ticker):

        try:
            time.sleep(2)
            el = driver.find_element(By.CSS_SELECTOR, 'a[data-ratid="mem_pc_gnavi_domestic-top"]')
            driver.execute_script("arguments[0].click();", el)
            time.sleep(1)
            el = driver.find_element(By.ID, 'dscrCdNm2')
            el.clear()
            ticker = ticker[:-2]
            el.send_keys(ticker)
            el = driver.find_element(By.CSS_SELECTOR, 'img[title="検索"]')
            driver.execute_script("arguments[0].click();", el)
            time.sleep(1)
            # 買いボタン
            el = driver.find_element(By.CSS_SELECTOR,
                'a[class="pcmm_jpstk-btlk-buy pcmm_jpstk-btlk-filled pcmm_jpstk-btlk--xs pcmm_jpstk-btlk--block"]')
            driver.execute_script("arguments[0].click();", el)
            time.sleep(1)
            # 数量
            el = driver.find_element(By.ID, 'orderValue')
            el.clear()
            el.send_keys('100')
            # 成行ラジオボタン
            el = driver.find_element(By.ID, 'priceMarket')
            driver.execute_script("arguments[0].click();", el)
            el = driver.find_element(By.NAME, "password")
            el.clear()
            el.send_keys("4105")
            el = driver.find_element(By.ID, 'ormit_checkbox')
            driver.execute_script("arguments[0].click();", el)
            el = driver.find_element(By.ID, 'ormit_sbm')
            driver.execute_script("arguments[0].click();", el)
            time.sleep(2)
            # メイン画面へ戻る
            el = driver.find_element(By.CLASS_NAME, "pcm-gl-logo-img")
            driver.execute_script("arguments[0].click();", el)
        except Exception as e:
            print('Error. ticker:', ticker)
            print(e)

    def loop_buy(self, buy_list):
        driver = login()
        for ticker_tuple in buy_list:
            ticker = ticker_tuple[0]
            self.auto_by_one(driver, ticker)

    def __init__(self):
        buy_list = self.get_ticker_list()
        # buy_list = self.loop_check(ticker_list)
        # buy_list = [('PHI',), ('RGLD',), ('AXP',)]
        # buy_list = [('MPC',)]
        self.loop_buy(buy_list)


my_obj = AutoBuy()
