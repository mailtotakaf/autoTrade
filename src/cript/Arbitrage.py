# https://di-acc2.com/programming/python/14975/
# API通信で利用
import json
import os

import requests
import ccxt

# グラフの可視化で利用
from time import sleep
from itertools import count
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.animation import FuncAnimation
from matplotlib import rcParams

import settings

rcParams["font.family"]     = "sans-serif"
rcParams["font.sans-serif"] = "Hiragino Maru Gothic Pro"
plt.style.use('fivethirtyeight')
mpl.use('TkAgg')

COINCHECK_API_KEY = settings.COINCHECK_API_KEY
COINCHECK_SECRET = settings.COINCHECK_SECRET

""" ↓要修正↓ """

# # APIキー＆シークレットキー(GMO)
# gmo_apiKey  = "GMOコインのAPIキーを入力"
# gmo_secret  = "GMOコインのシークレットキーを入力"
#
# # APIキー＆シークレットキー(Huobi)
# huobi_apiKey  = "BitTrade（旧：Huobi Japan）のAPIキーを入力"
# huobi_secret  = "BitTrade（旧：Huobi Japan）のシークレットキーを入力"

coincheck_apiKey  = os.getenv('COINCHECK_API_KEY')
coincheck_secret  = os.getenv('COINCHECK_SECRET')

bitflyer_apiKey  = os.getenv('BITFLYER_API_KEY')
bitflyer_secret  = os.getenv('BITFLYER_SECRET')

bittrade_apiKey  = os.getenv('BITTRADE_API_KEY')
bittrade_secret  = os.getenv('BITTRADE_SECRET')

""" ↑要修正↑ """

# インスタンス
coincheck = ccxt.coincheck({'apiKey':coincheck_apiKey,'secret':coincheck_secret})
bitflyer = ccxt.coincheck({'apiKey':bitflyer_apiKey,'secret':bitflyer_secret})
bittrade = ccxt.huobijp({'apiKey':bittrade_apiKey,'secret':bittrade_secret})

# 取引通過（ビットコイン以外を指定したい場合はここを修正）
# gmo_symbol     = "BTC"
coincheck_symbol = "BTC/JPY"
bittrade_symbol   = "BTC/JPY"

# # GMOコイン 板情報
# def gmo_ticker(symbol):
#     ita_prep = requests.get('https://api.coin.z.com/public/v1/ticker?symbol'+symbol)
#     result = ita_prep.json()['data'][0]
#     return result
#
# # Huobi 板情報
# def huobi_ticker(symbol):
#     result = huobi.fetch_ticker(symbol=symbol)
#     return result

# Coincheck 板情報
def coincheck_ticker(symbol):
    result = coincheck.fetch_ticker(symbol=symbol)
    return result

# bitflyer 板情報
def bitflyer_ticker(symbol):
    result = bitflyer.fetch_ticker(symbol=symbol)
    return result

# bittrade 板情報
def bittrade_ticker(symbol):
    result = bittrade.fetch_ticker(symbol=symbol)
    return result

# グラフ軸
index            = count() # x軸(カウント)
x                = []      # x軸
y_gmo_ask        = []      # gmo(買値)
y_gmo_bid        = []      # gmo(売値)
y_huobi_ask      = []      # Huobi(買値)
y_huobi_bid      = []      # Huobi(売値)
y_coincheck_ask  = []      # Coincheck(買値)
y_coincheck_bid  = []      # Coincheck(売値)
y_bitflyer_ask  = []      # bitflyer(買値)
y_bitflyer_bid  = []      # bitflyer(売値)
y_bittrade_ask  = []      # bittrade(買値)
y_bittrade_bid  = []      # bittrade(売値)

# グラフ可視化関数
def animate(i):
    # X軸
    x.append(next(index))
    # Y軸
    # y_gmo_ask.append(float(gmo_ticker(gmo_symbol)["ask"]))                    # GMO買値
    # y_gmo_bid.append(float(gmo_ticker(gmo_symbol)["bid"]))                    # GMO買値
    # y_huobi_ask.append(float(huobi_ticker(huobi_symbol)["ask"]))              # huobi買値
    # y_huobi_bid.append(float(huobi_ticker(huobi_symbol)["bid"]))              # huobi買値
    y_coincheck_ask.append(float(coincheck_ticker(coincheck_symbol)["ask"]))  # coincheck買値
    y_coincheck_bid.append(float(coincheck_ticker(coincheck_symbol)["bid"]))  # coincheck買値
    y_bitflyer_ask.append(float(bitflyer_ticker(coincheck_symbol)["ask"]))
    y_bitflyer_bid.append(float(bitflyer_ticker(coincheck_symbol)["bid"]))
    y_bittrade_ask.append(float(bittrade_ticker(coincheck_symbol)["ask"]))
    y_bittrade_bid.append(float(bittrade_ticker(coincheck_symbol)["bid"]))

    # アービトラージ(計算)
    # buy       = [y_gmo_ask[-1],y_huobi_ask[-1],y_coincheck_ask[-1]]
    # sell      = [y_gmo_bid[-1],y_huobi_bid[-1],y_coincheck_bid[-1]]
    # buy_min   = min(y_gmo_ask[-1],y_huobi_ask[-1],y_coincheck_ask[-1])
    # sell_max  = max(y_gmo_bid[-1],y_huobi_bid[-1],y_coincheck_bid[-1])
    # kakakusa  = sell_max - buy_min

    # アービトラージ(買い取引所特定)
    # if buy_min == buy[0]:
    #     buy_name = "GMOコイン"
    # elif buy_min == buy[1]:
    #     buy_name = "BitTrade"
    # elif buy_min == buy[2]:
    #     buy_name = "Coincheck"
    #
    # # アービトラージ(売り取引所特定)
    # if sell_max == sell[0]:
    #     sell_name = "GMOコイン"
    # elif sell_max == sell[1]:
    #     sell_name = "BitTrade"
    # elif sell_max == sell[2]:
    #     sell_name = "Coincheck"

    # グラフ設定
    plt.cla()
    # main_text = "買:" + buy_name + " 売:" + sell_name + " 価格差利益:" + str(int(kakakusa)) + "[円]"
    # plt.title(main_text,color="red")
    plt.xlabel("Time")
    plt.ylabel("Bitcoin[BTC]")
    # plt.plot(x,y_gmo_ask ,label="GMO[買]")
    # plt.plot(x,y_gmo_bid ,label="GMO[売]")
    # plt.plot(x,y_huobi_ask ,label="Huobi[買]")
    # plt.plot(x,y_huobi_bid ,label="Huobi[売]")
    plt.plot(x,y_coincheck_ask ,label="Coincheck[買]")
    plt.plot(x,y_coincheck_bid ,label="Coincheck[売]")
    plt.plot(x, y_bitflyer_ask, label="bitflyer[買]")
    plt.plot(x, y_bitflyer_bid, label="bitflyer[売]")
    plt.plot(x, y_bittrade_ask, label="bittrade[買]")
    plt.plot(x, y_bittrade_bid, label="bittrade[売]")
    plt.legend(loc="upper left")
    plt.tight_layout()


# アニメーショングラフ適用
ani = FuncAnimation(plt.gcf(),animate,interval=1000)

# グラフ表示
plt.tight_layout()
plt.show()