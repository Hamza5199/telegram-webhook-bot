import ccxt
import pandas as pd

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

    print(df.tail())

fetch_candles()
