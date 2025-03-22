import requests
import time
from datetime import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException

# Binance API credentials (replace with your actual keys)
API_KEY = 'NVEbS2NVZ9JWHX2CF9KDgL2dSLmM08WLghm9c7txXB5cxrrQFsKOm0LKXFkj81GE'
API_SECRET = '8a30DhaVRMCZodf41JLfIBB7tfYEgmBXva9eyQwPCGTr1hzZ3UaZZpwNkWB91a1g'  # Replace with your actual API secret

# Initialize Binance client
client = Client(API_KEY, API_SECRET)

# Function to fetch and log the bot's public IP
def log_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        response.raise_for_status()
        public_ip = response.json()['ip']
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        print(f'{timestamp} - Bot Public IP: {public_ip}')
        return public_ip
    except Exception as e:
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        print(f'{timestamp} - Error fetching public IP: {str(e)}')
        return None

# Function to fetch Funding Wallet balance
def get_funding_balance():
    try:
        # Fetch all asset balances (Funding Wallet)
        balances = client.get_asset_balance_funding()
        usdt_balance = 0.0
        for asset in balances:
            if asset['asset'] == 'USDT':
                usdt_balance = float(asset['free'])
                break
        return usdt_balance
    except BinanceAPIException as e:
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        print(f'{timestamp} - Error fetching Funding Wallet: {str(e)}')
        return 0.0

# Main bot logic
def run_bot():
    while True:
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        print(f'{timestamp} - Starting new cycle...')

        # Log the public IP at the start of each cycle
        log_public_ip()

        # Fetch Funding Wallet balance
        funding_balance = get_funding_balance()
        print(f'{timestamp} - Current Funding USDT balance: {funding_balance}')
        if funding_balance < 1:
            print(f'{timestamp} - Funding Wallet balance not detected--transfer 1+ USDT from Funding to Spot manually when possible.')

        # Wait 60 seconds before the next cycle (as per your logs)
        print(f'{timestamp} - Waiting 60 seconds for next cycle...')
        time.sleep(60)

# Start the bot
if __name__ == '__main__':
    # Log the public IP on startup
    log_public_ip()

    # Start the bot logic
    try:
        run_bot()
    except Exception as e:
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        print(f'{timestamp} - Trading loop crashed: {str(e)}')
