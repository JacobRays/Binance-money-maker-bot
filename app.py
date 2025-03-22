import os
import requests
import time
import logging
from datetime import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Binance API credentials (use environment variables)
API_KEY = os.getenv('NVeBs2NVZ9JwHX2CF9KDgL2dSLmM08WLghm9c7tXXb5cxrRQFsK0m0lKxFKj8lGE')
API_SECRET = os.getenv('8a30DhaVRMCZodf41JLfIBB7tfYEgmBXva9eyQwPCGTr1hzZ3UaZZpwNkWB91a1g')

# Initialize Binance client
client = Client(API_KEY, API_SECRET)

# Function to fetch and log the bot's public IP
def log_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        response.raise_for_status()
        public_ip = response.json()['ip']
        logging.info(f'Bot Public IP: {public_ip}')
        return public_ip
    except Exception as e:
        logging.error(f'Error fetching public IP: {str(e)}')
        return None

# Function to fetch Funding Wallet balance
def get_funding_balance():
    try:
        # Fetch USDT balance in Funding Wallet
        balance = client.get_asset_balance(asset='USDT')
        usdt_balance = float(balance['free'])
        return usdt_balance
    except BinanceAPIException as e:
        logging.error(f'Error fetching Funding Wallet: {str(e)}')
        return 0.0

# Main bot logic
def run_bot():
    while True:
        logging.info('Starting new cycle...')

        # Log the public IP at the start of each cycle
        log_public_ip()

        # Fetch Funding Wallet balance
        funding_balance = get_funding_balance()
        logging.info(f'Current Funding USDT balance: {funding_balance}')
        if funding_balance < 1:
            logging.warning('Funding Wallet balance not detected--transfer 1+ USDT from Funding to Spot manually when possible.')

        # Wait 60 seconds before the next cycle
        logging.info('Waiting 60 seconds for next cycle...')
        time.sleep(60)

# Start the bot
if __name__ == '__main__':
    # Log the public IP on startup
    log_public_ip()

    # Start the bot logic
    try:
        run_bot()
    except Exception as e:
        logging.critical(f'Trading loop crashed: {str(e)}')
