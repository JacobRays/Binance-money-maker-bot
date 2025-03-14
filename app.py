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

# Log to console for Render
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger()

# Binance API with proxy (your credentials)
API_KEY = "NVeBs2NVZ9JwHX2CF9KDgL2dSLmM08WLghm9c7tXXb5cxrRQFsK0m0lKxFKj8lGE"
API_SECRET = "8a30DhaVRMCZodf41JLfIBB7tfYEgmBXva9eyQwPCGTr1hzZ3UaZZpwNkWB91a1g"
PROXY_USERNAME = "bnshfbty"
PROXY_PASSWORD = "546filwfebpk"
proxy_url = f"http://{PROXY_USERNAME}:{PROXY_PASSWORD}@45.151.162.198:6600"
client = Client(API_KEY, API_SECRET, requests_params={"proxies": {"http": proxy_url, "https": proxy_url}})

# Other settings (your values)
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
    try:
        exchange_info = client.get_exchange_info()
        pairs = {symbol['symbol']: float(symbol['filters'][2]['minQty']) for symbol in exchange_info['symbols'] if symbol['status'] == "TRADING"}
        return pairs
    except Exception as e:
        logger.error(f"Error fetching trading pairs: {e}")
        return {}

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
        df['tr2'] = ab
