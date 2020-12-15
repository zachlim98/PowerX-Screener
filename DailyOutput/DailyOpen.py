import os
import pandas as pd
import yfinance as yf
from ta.momentum import RSIIndicator, stoch
from ta.trend import MACD as md
from ta.volatility import AverageTrueRange as atr
from datetime import datetime

dataframes = {}
buys = {}
sells = {}
buy_list = []
buy_list_sl = []
buy_list_tp = []
sell_list = []
sell_list_tp = []
sell_list_sl = []
buy_list_sq = []
sell_list_sq = []
buy_list_osq = []
sell_list_osq = []
on_squeeze = []
outof_squeeze = []

with open('ticker.csv') as f:
    lines = f.read().splitlines()
    for symbol in lines:
        print(symbol)
        data = yf.download(symbol, start="2020-01-01", end=datetime.today().strftime('%Y-%m-%d'))
        df = pd.DataFrame(data)

        RSI = RSIIndicator(close=df['Close'], n=7)
        df["RSI"] = RSI.rsi()

        Stochk = stoch(high=df["High"],low=df["Low"],close=df["Close"]).rolling(window=3).mean()
        df["Stochk"] = Stochk

        MACD = md(close=df['Close'])
        df["MACD_diff"] = MACD.macd_diff()

        AvgTru = atr(high=df['High'],low=df['Low'],close=df['Close'],n=7)
        df["ATR"] = AvgTru.average_true_range()

        df["Signal"] = ""

        df['20sma'] = df['Close'].rolling(window=20).mean()
        df['stddev'] = df['Close'].rolling(window=20).std()
        df['lower_band'] = df['20sma'] - (2 * df['stddev'])
        df['upper_band'] = df['20sma'] + (2 * df['stddev'])

        df['TR'] = abs(df['High'] - df['Low'])
        df['ATR'] = df['TR'].rolling(window=20).mean()

        df['lower_keltner'] = df['20sma'] - (df['ATR'] * 1.5)
        df['upper_keltner'] = df['20sma'] + (df['ATR'] * 1.5)

        def in_squeeze(df):
            return df['lower_band'] > df['lower_keltner'] and df['upper_band'] < df['upper_keltner']

        df['squeeze_on'] = df.apply(in_squeeze, axis=1)

        if df["squeeze_on"].iloc[-1]==True:
            on_squeeze.append(symbol)

        if (df["squeeze_on"].iloc[-1]==False) and (df["squeeze_on"].iloc[-2]==True):
            outof_squeeze.append(symbol)

        for i in range(0,len(df)):
            if df["RSI"].iloc[i] > 50 and df["Stochk"][i] > 50 and df["MACD_diff"][i] > 0:
                df["Signal"][i] = "Buy"
            elif df["RSI"].iloc[i] < 50 and df["Stochk"][i] < 50 and df["MACD_diff"][i] < 0:
                df["Signal"][i] = "Sell"
            else:
                df["Signal"][i] = "Neutral"

            if df["Signal"].iloc[-1] == "Buy" and (df["Signal"].iloc[-2] != "Buy"):
                buy_list.append(symbol)
                buy_list_sl.append(df["Close"].iloc[-1]-(df["ATR"].iloc[-1]*1.3))
                buy_list_tp.append(df["Close"].iloc[-1]+(df["ATR"].iloc[-1]*2.2))
                buy_list_sq.append(df['squeeze_on'].iloc[-1])
            elif df["Signal"].iloc[-1] == "Sell" and (df["Signal"].iloc[-2] != "Sell"):
                sell_list.append(symbol)
                sell_list_sl.append(df["Close"].iloc[-1]+(df["ATR"].iloc[-1]*1.3))
                sell_list_tp.append(df["Close"].iloc[-1]-(df["ATR"].iloc[-1]*2.2))
                sell_list_sq.append(df['squeeze_on'].iloc[-1])
            else:
                continue

        buys = pd.DataFrame({
            "Symbol" : buy_list,
            "SL" : buy_list_sl,
            "TP" : buy_list_tp,
            "Squeeze" : buy_list_sq
        })

        sells = pd.DataFrame({
            "Symbol" : sell_list,
            "SL" : sell_list_sl,
            "TP" : sell_list_tp,
            "Squeeze" : sell_list_sq
        })

        oos = pd.DataFrame({
            "Out of squeeze" : outof_squeeze
        })

buys.to_csv("buys.csv")
sells.to_csv("sells.csv")
oos.to_csv("oos.csv")