import requests
import pandas as pd
import ta
import time

SYMBOL = "BTCUSDT"
INTERVAL = "1m"
LIMIT = 50

def get_candles():
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": SYMBOL,
        "interval": INTERVAL,
        "limit": LIMIT
    }
    data = requests.get(url, params=params).json()

    df = pd.DataFrame(
        data,
        columns=[
            "time", "open", "high", "low", "close",
            "volume", "close_time", "qav",
            "trades", "taker_base", "taker_quote", "ignore"
        ]
    )

    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)

    return df

def run_engine():
    while True:
        try:
            df = get_candles()

            df["EMA_9"] = ta.trend.ema_indicator(df["close"], window=9)
            df["EMA_21"] = ta.trend.ema_indicator(df["close"], window=21)
            df["RSI"] = ta.momentum.rsi(df["close"], window=14)

            last = df.iloc[-1]

            # 🔎 LONG CONDITION
            if (
                last["EMA_9"] > last["EMA_21"]
                and 40 < last["RSI"] < 60
                and last["close"] > last["EMA_21"]
            ):
                entry = round(last["close"], 2)
                stop_loss = round(df["low"].iloc[-5:].min(), 2)

                risk = entry - stop_loss

                tp1 = round(entry + risk * 1.0, 2)
                tp2 = round(entry + risk * 1.5, 2)
                tp3 = round(entry + risk * 2.0, 2)

                print("🟢 LONG SIGNAL FOUND")
                print("Entry:", entry)
                print("Stop Loss:", stop_loss)
                print("TP1:", tp1, "TP2:", tp2, "TP3:", tp3)
            else:
                print("No trade condition")

            time.sleep(60)

        except Exception as e:
            print("Engine error:", e)
            time.sleep(60)

if __name__ == "__main__":
    run_engine()
