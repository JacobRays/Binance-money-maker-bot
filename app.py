import os
import requests
from flask import Flask, jsonify
from dotenv import load_dotenv

load_dotenv()  # Only works locally; Render will use environment config

app = Flask(__name__)

BINANCE_API_KEY = os.getenv('NVeBs2NVZ9JwHX2CF9KDgL2dSLmM08WLghm9c7tXXb5cxrRQFsK0m0lKxFKj8lGE')
BINANCE_PROXY = os.getenv('BINANCE_PROXY')  # Optional proxy

@app.route('/')
def home():
    return "Binance Money Maker Bot is running."

@app.route('/ping-binance')
def ping_binance():
    try:
        headers = {"X-MBX-APIKEY": BINANCE_API_KEY}
        proxies = {"http": BINANCE_PROXY, "https": BINANCE_PROXY} if BINANCE_PROXY else None
        response = requests.get(
            "https://api.binance.com/api/v3/ping",
            headers=headers,
            proxies=proxies,
            timeout=10
        )
        response.raise_for_status()
        return jsonify({"status": "Binance reachable", "response": response.json()})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
