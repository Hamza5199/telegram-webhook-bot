from flask import Flask, request
import requests

app = Flask(__name__)

BOT_TOKEN = "8504676875:AAHX9Gwy7ognF4s-4k5Kt4fjVwBnXpXejk8"
CHAT_ID = "-1003303267979"   # tumhara channel ID

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, data=payload)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    message = data.get("message", "No message received")
    send_to_telegram(message)
    return "OK"

if __name__ == "__main__":
import os
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
