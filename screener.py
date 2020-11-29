import pandas as pd
import yfinance as yf
from ta.momentum import RSIIndicator, stochrsi_k
from ta.trend import MACD as md
from ta.volatility import AverageTrueRange as atr

def spef(symbol,start_date,end_date):
    data = yf.download(symbol, start=start_date, end=end_date)
    df = pd.DataFrame(data)

    RSI = RSIIndicator(close=df['Close'])
    df["RSI"] = RSI.rsi()

    Stochk = stochrsi_k(close=df['Close'])
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

    for i in range(0,len(df)):
        if df["RSI"].iloc[i] > 50 and df["Stochk"][i] > 50 and df["MACD_diff"][i] > 0:
            df["Signal"][i] = "Buy"
        elif df["RSI"].iloc[i] < 50 and df["Stochk"][i] < 50 and df["MACD_diff"][i] < 0:
            df["Signal"][i] = "Sell"
        else:
            df["Signal"][i] = "Neutral"

    return df

def scan(file_path,start_date,end_date):

    buys = pd.DataFrame()
    sells = pd.DataFrame()
    buy_list = []
    buy_list_sl = []
    buy_list_tp = []
    sell_list = []
    sell_list_tp = []
    sell_list_sl = []
    buy_list_sq = []
    sell_list_sq = []
    on_squeeze = []

    with open(file_path) as f:
        lines = f.read().splitlines()
        for symbol in lines:
            print(symbol)
            data = yf.download(symbol, start=start_date, end=end_date)
            df = pd.DataFrame(data)

            if df.empty:
                continue

            RSI = RSIIndicator(close=df['Close'])
            df["RSI"] = RSI.rsi()

            Stochk = stochrsi_k(close=df['Close'])
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

            for i in range(0,len(df)):
                if df["RSI"].iloc[i] > 50 and df["Stochk"][i] > 50 and df["MACD_diff"][i] > 0:
                    df["Signal"][i] = "Buy"
                elif df["RSI"].iloc[i] < 50 and df["Stochk"][i] < 50 and df["MACD_diff"][i] < 0:
                    df["Signal"][i] = "Sell"
                else:
                    df["Signal"][i] = "Neutral"

            if df["Signal"].iloc[-1] == "Buy" and (df["Signal"].iloc[-2] != "Buy"):
                buy_list.append(symbol)
                buy_list_sl.append(df["Close"].iloc[-1]-(df["ATR"].iloc[-1]*1.4))
                buy_list_tp.append(df["Close"].iloc[-1]+(df["ATR"].iloc[-1]*2.8))
                buy_list_sq.append(df['squeeze_on'].iloc[-1])
            elif df["Signal"].iloc[-1] == "Sell" and (df["Signal"].iloc[-2] != "Sell"):
                sell_list.append(symbol)
                sell_list_sl.append(df["Close"].iloc[-1]+(df["ATR"].iloc[-1]*1.4))
                sell_list_tp.append(df["Close"].iloc[-1]-(df["ATR"].iloc[-1]*2.8))
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
                
    return buys, sells, on_squeeze


def spfl(symbol_list,start_date,end_date):

    buys = pd.DataFrame()
    sells = pd.DataFrame()
    buy_list = []
    buy_list_sl = []
    buy_list_tp = []
    sell_list = []
    sell_list_tp = []
    sell_list_sl = []
    buy_list_sq = []
    sell_list_sq = []
    on_squeeze = []

    for symbol in symbol_list:
        print(symbol)
        data = yf.download(symbol, start=start_date, end=end_date)
        df = pd.DataFrame(data)

        if df.empty:
            continue

        RSI = RSIIndicator(close=df['Close'])
        df["RSI"] = RSI.rsi()

        Stochk = stochrsi_k(close=df['Close'])
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

        for i in range(0,len(df)):
            if df["RSI"].iloc[i] > 50 and df["Stochk"][i] > 50 and df["MACD_diff"][i] > 0:
                df["Signal"][i] = "Buy"
            elif df["RSI"].iloc[i] < 50 and df["Stochk"][i] < 50 and df["MACD_diff"][i] < 0:
                df["Signal"][i] = "Sell"
            else:
                df["Signal"][i] = "Neutral"

        if df["Signal"].iloc[-1] == "Buy" and (df["Signal"].iloc[-2] != "Buy"):
            buy_list.append(symbol)
            buy_list_sl.append(df["Close"].iloc[-1]-(df["ATR"].iloc[-1]*1.4))
            buy_list_tp.append(df["Close"].iloc[-1]+(df["ATR"].iloc[-1]*2.8))
            buy_list_sq.append(df['squeeze_on'].iloc[-1])
        elif df["Signal"].iloc[-1] == "Sell" and (df["Signal"].iloc[-2] != "Sell"):
            sell_list.append(symbol)
            sell_list_sl.append(df["Close"].iloc[-1]+(df["ATR"].iloc[-1]*1.4))
            sell_list_tp.append(df["Close"].iloc[-1]-(df["ATR"].iloc[-1]*2.8))
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
                
    return buys, sells, on_squeeze

    