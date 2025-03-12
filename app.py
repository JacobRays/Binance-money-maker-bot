import requests
from bs4 import BeautifulSoup
from binance.client import Client
from flask import Flask
import time
import pandas as pd
from binance.enums import *
import hashlib
import json
import os
import logging
import threading

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s", filename="trading_log.txt")
logger = logging.getLogger()

API_KEY ="NVeBs2NVZ9JwHX2CF9KDgL2dSLmM08WLghm9c7tXXb5cxrRQFsK0m0lKxFKj8lGE"
API_SECRET = "8a30DhaVRMCZodf41JLfIBB7tfYEgmBXva9eyQwPCGTr1hzZ3UaZZpwNkWB91a1g"
client = Client(API_KEY, API_SECRET, requests_params={"proxies": {"http": "http://45.151.162.198:6600", "https": "http://45.151.162.198:6600"}})

YOUR_PASSWORD = "Premium01!"
hashed_password = hashlib.sha256(YOUR_PASSWORD.encode()).hexdigest()

WITHDRAW_ADDRESS = "0xb98ee32218e0aDdD822Daaeb0BAdd509CCfCac49"
PAYPAL_ADDRESS = "premiumrays01@gmail.com"

DEFAULT_PAIR = "DOGEUSDT"
TRADE_FILE = "trades.json"

app = Flask(__name__)

def verify_password(password):
    input_hash = hashlib.sha256(password.encode()).hexdigest()
    return input_hash == hashed_password

def get_trading_pairs():
    exchange_info = client.get_exchange_info()
    pairs = {symbol['symbol']: float(symbol['filters'][2]['minQty']) for symbol in exchange_info['symbols'] if symbol['status'] == "TRADING"}
    return pairs

def load_trades():
    if os.path.exists(TRADE_FILE):
        with open(TRADE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_trades(trades):
    with open(TRADE_FILE, 'w') as f:
        json.dump(trades, f)

def fetch_red_packet_codes_square():
    url = "https://www.binance.com/en/square"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        posts = soup.find_all("div", class_="post-content")
        codes = []
        for post in posts:
            text = post.get_text()
            if "#RedPacketMission" in text or "Red Packet" in text:
                code = [word for word in text.split() if word.startswith("BP")]
                if code and code[0] not in codes:
                    codes.append(code[0])
        return codes if codes else ["No new Square codes."]
    except Exception as e:
        return [f"Square error: {e}"]

def fetch_red_packet_codes_x():
    url = "https://x.com/binance"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        tweets = soup.find_all("div", class_="tweet")
        codes = []
        for tweet in tweets:
            text = tweet.get_text()
            if "Red Packet" in text or "#RedPacket" in text:
                code = [word for word in text.split() if word.startswith("BP")]
                if code and code[0] not in codes:
                    codes.append(code[0])
        return codes if codes else ["No new X codes."]
    except Exception as e:
        return [f"X error: {e}"]

def run_reward_errands():
    rewards = []
    try:
        usdt_balance = float(client.get_asset_balance(asset="USDT")['free'])
        bnb_balance = float(client.get_asset_balance(asset="BNB")['free'])
        
        if usdt_balance > 0.01:
            logger.info("Auto-staking USDT in Simple Earn...")
            earn_products = client.get_lending_product_list()
            for product in earn_products:
                if product['asset'] == "USDT" and product['status'] == "SUBSCRIBABLE":
                    client.lending_purchase(product_id=product['productId'], amount=min(0.01, usdt_balance))
                    rewards.append(f"Staked {min(0.01, usdt_balance)} USDT in Simple Earn")
                    break
        
        if bnb_balance > 0.001:
            logger.info("Auto-staking BNB in Simple Earn...")
            earn_products = client.get_lending_product_list()
            for product in earn_products:
                if product['asset'] == "BNB" and product['status'] == "SUBSCRIBABLE":
                    client.lending_purchase(product_id=product['productId'], amount=min(0.001, bnb_balance))
                    rewards.append(f"Staked {min(0.001, bnb_balance)} BNB in Simple Earn")
                    break
        
        pools = client.get_staking_product_list(stakingType="POOL")
        if pools:
            for pool in pools:
                if bnb_balance > 0.001 and pool['asset'] == "BNB":
                    logger.info("Auto-joining Launchpool with BNB...")
                    client.stake(asset="BNB", productId=pool['productId'], amount=min(0.001, bnb_balance))
                    rewards.append(f"Joined Launchpool: {pool['asset']}")
                elif usdt_balance > 0.01 and pool['asset'] == "USDT":
                    logger.info("Auto-joining Launchpool with USDT...")
                    client.stake(asset="USDT", productId=pool['productId'], amount=min(0.01, usdt_balance))
                    rewards.append(f"Joined Launchpool: {pool['asset']}")
        
        if bnb_balance > 0:
            rewards.append("Holding BNB for HODLer Airdrops - auto-distributed")
        
        rewards.append("Check Binance app 'Earn' > 'Megadrop' for manual tasks")
        
        return rewards if rewards else ["No auto-joinable rewards yet."]
    except Exception as e:
        return [f"Reward error: {e}"]

def calculate_atr_and_trend(symbol, period=14):
    try:
        klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1HOUR, f"{period + 20} hours ago UTC")
        df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_volume', 'trades', 'tb_base', 'tb_quote', 'ignore'])
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['close'] = df['close'].astype(float)
        
        df['tr1'] = df['high'] - df['low']
        df['tr2'] = abs(df['high'] - df['close'].shift())
        df['tr3'] = abs(df['low'] - df['close'].shift())
        df['true_range'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
        atr = df['true_range'].rolling(window=period).mean().iloc[-1]
        
        ma_short = df['close'].rolling(window=5).mean().iloc[-1]
        ma_long = df['close'].rolling(window=20).mean().iloc[-1]
        trend = "UP" if ma_short > ma_long else "DOWN"
        
        current_price = float(client.get_symbol_ticker(symbol=symbol)['price'])
        return current_price, atr, trend
    except Exception as e:
        logger.error(f"Error calculating ATR/trend for {symbol}: {e}")
        return None, None, None

def trade_with_atr(symbol, min_qty, trades):
    current_price, atr, trend = calculate_atr_and_trend(symbol)
    if not atr:
        return
    
    base_asset = symbol[:-4] if symbol.endswith("USDT") else symbol[:-3]
    quote_asset = "USDT" if symbol.endswith("USDT") else "BNB"
    quote_balance = float(client.get_asset_balance(asset=quote_asset)['free'])
    base_balance = float(client.get_asset_balance(asset=base_asset)['free'])
    
    trade_value = quote_balance * 0.1
    qty = max(min_qty, trade_value / current_price)
    min_trade_value = qty * current_price

    logger.info(f"{symbol} - Price: ${current_price}, ATR: ${atr:.4f}, Trend: {trend}")
    
    if quote_balance < min_trade_value:
        logger.warning(f"Insufficient {quote_asset}: {quote_balance:.6f} < {min_trade_value:.6f}")
        return
    
    avg_price = float(client.get_avg_price(symbol=symbol)['price'])
    if trend == "UP" and current_price <= avg_price * 0.99:
        take_profit = current_price + (6 * atr)
        stop_loss = current_price - (1.5 * atr)
        logger.info(f"Auto-buying {qty:.6f} {base_asset} at ${current_price}")
        logger.info(f"Initial TP: ${take_profit:.4f}, SL: ${stop_loss:.4f}")
        try:
            client.order_market_buy(symbol=symbol, quantity=qty)
            trades[symbol] = {"qty": qty, "entry_price": current_price, "take_profit": take_profit, "stop_loss": stop_loss, "atr": atr}
            save_trades(trades)
        except Exception as e:
            logger.error(f"Buy error: {e}")
    elif symbol in trades:
        monitor_position(symbol, trades)

def monitor_position(symbol, trades):
    trade = trades[symbol]
    qty = trade["qty"]
    entry_price = trade["entry_price"]
    take_profit = trade["take_profit"]
    stop_loss = trade["stop_loss"]
    atr = trade["atr"]
    
    current_price = float(client.get_symbol_ticker(symbol=symbol)['price'])
    if current_price >= entry_price + (4 * atr):
        trail_stop = current_price - (2 * atr)
        logger.info(f"Trailing stop activated at ${trail_stop:.4f}")
        if current_price <= trail_stop:
            logger.info(f"Auto-selling {qty:.6f} {symbol[:-4]} at ${current_price} (trailing stop)")
            try:
                client.order_market_sell(symbol=symbol, quantity=qty)
                del trades[symbol]
                save_trades(trades)
            except Exception as e:
                logger.error(f"Sell error: {e}")
    elif current_price >= take_profit:
        logger.info(f"Auto-selling {qty:.6f} {symbol[:-4]} at ${current_price} (take profit)")
        try:
            client.order_market_sell(symbol=symbol, quantity=qty)
            del trades[symbol]
            save_trades(trades)
        except Exception as e:
            logger.error(f"Sell error: {e}")
    elif current_price <= stop_loss:
        logger.info(f"Auto-selling {qty:.6f} {symbol[:-4]} at ${current_price} (stop loss)")
        try:
            client.order_market_sell(symbol=symbol, quantity=qty)
            del trades[symbol]
            save_trades(trades)
        except Exception as e:
            logger.error(f"Sell error: {e}")

def trading_loop():
    pairs = get_trading_pairs()
    selected_pairs = [DEFAULT_PAIR]  # Default to DOGEUSDT; customize here if needed
    trades = load_trades()
    
    while True:
        logger.info("\nStarting new cycle...")
        
        square_codes = fetch_red_packet_codes_square()
        logger.info("Red Packet Codes from Binance Square (claim in Binance app):")
        for code in square_codes:
            logger.info(f"- {code}")
        
        x_codes = fetch_red_packet_codes_x()
        logger.info("Red Packet Codes from X (claim in Binance app):")
        for code in x_codes:
            logger.info(f"- {code}")
        
        rewards = run_reward_errands()
        logger.info("Airdrop/Reward Actions:")
        for reward in rewards:
            logger.info(f"- {reward}")
        
        usdt_balance = float(client.get_asset_balance(asset="USDT")['free'])
        logger.info(f"Current USDT balance: {usdt_balance:.6f}")
       

@app.route('/ping')
def ping():
    return "Alive"

threading.Thread(target=trading_loop, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
