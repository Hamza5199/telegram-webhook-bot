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

            print(
                f"[DATA] {SYMBOL} | "
                f"Close: {last['close']} | "
                f"EMA9: {round(last['EMA_9'],2)} | "
                f"EMA21: {round(last['EMA_21'],2)} | "
                f"RSI: {round(last['RSI'],2)}"
            )

            time.sleep(60)

        except Exception as e:
            print("Engine error:", e)
            time.sleep(60)

if __name__ == "__main__":
    run_engine()
