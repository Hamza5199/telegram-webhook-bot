import ccxt
import pandas as pd
import pandas_ta as ta
import requests
import os

# ===== Telegram config =====
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=payload)

# ===== Binance setup =====
exchange = ccxt.binance({
    "enableRateLimit": True,
    "options": {
        "defaultType": "future"
    }
})

def generate_signal():
    candles = exchange.fetch_ohlcv(
        symbol="BTC/USDT",
        timeframe="5m",
        limit=50
    )

    df = pd.DataFrame(
        candles,
        columns=["time", "open", "high", "low", "close", "volume"]
    )

    # Indicators
    df["EMA_9"] = ta.ema(df["close"], length=9)
    df["EMA_21"] = ta.ema(df["close"], length=21)
    df["RSI"] = ta.rsi(df["close"], length=14)

    last = df.iloc[-1]
    prev = df.iloc[-2]

    if (
        last["close"] > last["EMA_21"] and
        prev["EMA_9"] < prev["EMA_21"] and
        last["EMA_9"] > last["EMA_21"] and
        35 < last["RSI"] < 50
    ):
        entry = round(last["close"], 2)
        stop_loss = round(df["low"].iloc[-5:].min(), 2)

        risk = entry - stop_loss

        tp1 = round(entry + risk * 0.5, 2)
        tp2 = round(entry + risk * 1.0, 2)
        tp3 = round(entry + risk * 1.5, 2)

        dca1 = round(entry - risk * 0.3, 2)
        dca2 = round(entry - risk * 0.6, 2)

        message = (
            "🔱 Trade: #BTCUSDT 🔱\n"
            "🟢 LONG SCALP (5m)\n\n"
            f"Entry: {entry}\n"
            f"DCA1: {dca1}\n"
            f"DCA2: {dca2}\n"
            f"Stop-Loss: {stop_loss}\n\n"
            f"🎯 TP1: {tp1}\n"
            f"🎯 TP2: {tp2}\n"
            f"🎯 TP3: {tp3}\n\n"
            "Mode: Auto Scalping Bot"
        )

        send_to_telegram(message)

generate_signal()
