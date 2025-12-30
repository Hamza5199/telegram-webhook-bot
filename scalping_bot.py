import ccxt
import pandas as pd
import pandas_ta as ta

exchange = ccxt.binance({
    "enableRateLimit": True,
    "options": {
        "defaultType": "future"
    }
})

def fetch_candles():
    candles = exchange.fetch_ohlcv(
        symbol="BTC/USDT",
        timeframe="5m",
        limit=50
    )

    df = pd.DataFrame(
        candles,
        columns=["time", "open", "high", "low", "close", "volume"]
    )

    # EMA indicators
    df["EMA_9"] = ta.ema(df["close"], length=9)
    df["EMA_21"] = ta.ema(df["close"], length=21)

    print(df.tail())

fetch_candles()
