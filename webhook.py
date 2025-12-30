from flask import Flask, request
import requests
import os

app = Flask(__name__)   # ✅ FIXED

BOT_TOKEN = "8504676875:AAHX9Gwy7ognF4s-4k5Kt4fjVwBnXpXejk8"
CHAT_ID = "-1003303267979"

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, data=payload)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)

    if not data or "message" not in data:
        return "OK", 200

    text = data["message"].get("text", "")
    send_to_telegram(text)
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
