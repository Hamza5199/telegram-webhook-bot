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

# ===== COINS CONFIG =====
PAIRS = [
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "ADAUSDT"
]

INTERVAL = "1m"
LIMIT = 50

last_signal_time = {}

def get_candles(symbol):
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
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
        for symbol in PAIRS:
            try:
                now = time.time()

                # ⛔ Cooldown: 10 minutes per coin
                if symbol in last_signal_time and now - last_signal_time[symbol] < 600:
                    continue

                df = get_candles(symbol)

                df["EMA_9"] = ta.trend.ema_indicator(df["close"], window=9)
                df["EMA_21"] = ta.trend.ema_indicator(df["close"], window=21)
                df["RSI"] = ta.momentum.rsi(df["close"], window=14)

                last = df.iloc[-1]

                if (
                    last["EMA_9"] > last["EMA_21"]
                    and 40 < last["RSI"] < 60
                    and last["close"] > last["EMA_21"]
                ):
                    entry = round(last["close"], 4)
                    stop_loss = round(df["low"].iloc[-5:].min(), 4)
                    risk = entry - stop_loss

                    tp1 = round(entry + risk * 1.0, 4)
                    tp2 = round(entry + risk * 1.5, 4)
                    tp3 = round(entry + risk * 2.0, 4)

                    dca1 = round(entry - risk * 0.3, 4)
                    dca2 = round(entry - risk * 0.6, 4)

                    message = f"""
🔱 {symbol} SCALPING SIGNAL 🔱

🟢 LONG
Entry: {entry}
DCA1: {dca1}
DCA2: {dca2}
Stop Loss: {stop_loss}

🎯 TP1: {tp1}
🎯 TP2: {tp2}
🎯 TP3: {tp3}

⏱ Timeframe: 1m
⚠️ Risk management required
"""

                    send_to_telegram(message)
                    last_signal_time[symbol] = now

            except Exception as e:
                print(f"{symbol} error:", e)

        time.sleep(60)

# ===== START BACKGROUND THREAD =====
threading.Thread(target=scalping_bot, daemon=True).start()

@app.route("/")
def home():
    return "Multi-coin scalping bot is running"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
