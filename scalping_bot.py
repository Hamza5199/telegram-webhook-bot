import ccxt

exchange = ccxt.binance({
    "enableRateLimit": True,
    "options": {
        "defaultType": "future"
    }
})

def get_price():
    ticker = exchange.fetch_ticker("BTC/USDT")
    price = ticker["last"]
    print("BTC price:", price)

get_price()
