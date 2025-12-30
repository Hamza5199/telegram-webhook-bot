from flask import Flask
import requests
import os
import threading
import time
import pandas as pd
import ta

app = Flask(__name__)

# ===== TELEGRAM CONFIG =====
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, data=payload)

# ===== BINANCE DATA =====
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

# ===== SCALPING ENGINE =====
def scalping_bot():
    while True:
        try:
            df = get_candles()

            df["EMA_9"] = ta.trend.ema_indicator(df["close"], window=9)
            df["EMA_21"] = ta.trend.ema_indicator(df["close"], window=21)
            df["RSI"] = ta.momentum.rsi(df["close"], window=14)

            last = df.iloc[-1]

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

                message = f"""
🔱 BTCUSDT SCALPING SIGNAL 🔱

🟢 LONG
Entry: {entry}
Stop Loss: {stop_loss}

🎯 TP1: {tp1}
🎯 TP2: {tp2}
🎯 TP3: {tp3}

⏱ Timeframe: 1m
⚠️ Use proper risk management
"""

                send_to_telegram(message)

            time.sleep(60)

        except Exception as e:
            print("Bot error:", e)
            time.sleep(60)

# ===== START BACKGROUND THREAD =====
threading.Thread(target=scalping_bot, daemon=True).start()

@app.route("/")
def home():
    return "Scalping bot is running"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
