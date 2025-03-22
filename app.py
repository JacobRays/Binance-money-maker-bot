import os
from binance.client import Client
import requests
from datetime import datetime
import time

# Proxy settings
proxy = {
    'http': 'http://200.174.198.86:8888',  # Brazil proxy
    'https': 'http://200.174.198.86:8888',
}

# Set up the Binance client with proxy
os.environ['HTTP_PROXY'] = proxy['http']
os.environ['HTTPS_PROXY'] = proxy['https']
client = Client('NVEbS2NVZ9JWHX2CF9KDgL2dSLmM08WLghm9c7txXB5cxrrQFsKOm0LKXFkj81GE', '8a30DhaVRMCZodf41JLfIBB7tfYEgmBXva9eyQwPCGTr1hzZ3UaZZpwNkWB91a1g')

# Function to log the bot's public IP
def log_public_ip():
    try:
        # Log IP with proxy (should show the proxy IP)
        response = requests.get('https://api.ipify.org?format=json', proxies=proxy)
        response.raise_for_status()
        proxy_ip = response.json()['ip']
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        print(f'{timestamp} - Bot Public IP (via proxy): {proxy_ip}')

        # Log IP without proxy (should show Render's IP)
        response = requests.get('https://api.ipify.org?format=json')
        response.raise_for_status()
        render_ip = response.json()['ip']
        print(f'{timestamp} - Bot Public IP (Render): {render_ip}')
        return proxy_ip, render_ip
    except Exception as e:
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        print(f'{timestamp} - Error fetching public IP: {str(e)}')
        return None, None

# Main bot logic
def run_bot():
    while True:
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        print(f'{timestamp} - Starting new cycle...')

        # Log the public IPs
        proxy_ip, render_ip = log_public_ip()

        try:
            # Check Funding Wallet balance
            funding_balance = client.get_asset_balance(asset='USDT')
            print(f'{timestamp} - Current Funding USDT balance: {funding_balance["free"]}')

            if float(funding_balance['free']) < 1:
                print(f'{timestamp} - Funding Wallet balance not detected--transfer 1+ USDT from Funding to Spot manually when possible.')

            # Check Spot Wallet balances
            print(f'{timestamp} - Your Spot Balances:')
            spot_pepe = client.get_asset_balance(asset='PEPE')
            spot_hmstr = client.get_asset_balance(asset='HMSTR')
            print(f'{timestamp} - PEPE: {spot_pepe["free"]}')
            print(f'{timestamp} - HMSTR: {spot_hmstr["free"]}')

            # Wait 1 minute before the next cycle
            print(f'{timestamp} - Waiting 1 minute for next cycle...')
            time.sleep(60)
        except Exception as e:
            print(f'{timestamp} - Bot error: {str(e)}')
            time.sleep(60)

if __name__ == '__main__':
    run_bot()
