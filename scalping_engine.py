import requests
import time

SYMBOL = "BTCUSDT"
INTERVAL = "1m"
LIMIT = 20

def get_latest_price():
    url = "https://api.binance.com/api/v3/ticker/price"
    params = {"symbol": SYMBOL}
    response = requests.get(url, params=params)
    data = response.json()
    return float(data["price"])

def run_engine():
    while True:
        try:
            price = get_latest_price()
            print(f"[ENGINE] {SYMBOL} Price:", price)
            time.sleep(60)
        except Exception as e:
            print("Engine error:", e)
            time.sleep(60)

if __name__ == "__main__":
    run_engine()
