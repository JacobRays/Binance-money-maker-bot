import os
import requests
import time
from datetime import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

# Load credentials from environment variables
BINANCE_API_KEY = os.getenv('NVeBs2NVZ9JwHX2CF9KDgL2dSLmM08WLghm9c7tXXb5cxrRQFsK0m0lKxFKj8lGE')
BINANCE_API_SECRET = os.getenv('8a30DhaVRMCZodf41JLfIBB7tfYEgmBXva9eyQwPCGTr1hzZ3UaZZpwNkWB91a1g')

# Proxy settings (set these as environment variables or edit here)
PROXY_HOST = os.getenv('PROXY_HOST', '200.174.198.86')
PROXY_PORT = os.getenv('PROXY_PORT', '8888')

proxy = {
    'http': f'http://{PROXY_HOST}:{PROXY_PORT}',
    'https': f'http://{PROXY_HOST}:{PROXY_PORT}'
}

# Set system environment for proxy (affects all requests & most libraries)
os.environ['HTTP_PROXY'] = proxy['http']
os.environ['HTTPS_PROXY'] = proxy['https']

# Initialize Binance Client
client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

def log_public_ip():
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    try:
        # IP via proxy
        proxy_ip = requests.get('https://api.ipify.org?format=json', proxies=proxy, timeout=10).json()['ip']
        print(f'{timestamp} - Bot Public IP (via proxy): {proxy_ip}')
    except Exception as e:
        print(f'{timestamp} - Error getting proxy IP: {str(e)}')
        proxy_ip = None

    try:
        # IP without proxy (Render IP)
        render_ip = requests.get('https://api.ipify.org?format=json', timeout=10).json()['ip']
        print(f'{timestamp} - Render Server IP: {render_ip}')
    except Exception as e:
        print(f'{timestamp} - Error getting render IP: {str(e)}')
        render_ip = None

    return proxy_ip, render_ip

def get_wallet_balance(asset, wallet_type="spot"):
    """Fetch balance from either spot or funding wallet"""
    try:
        if wallet_type == "spot":
            balance = client.get_asset_balance(asset=asset)
            return float(balance['free'])
        elif wallet_type == "funding":
            funding_balances = client.funding_get_balance(asset=asset)
            if funding_balances and len(funding_balances) > 0:
                return float(funding_balances[0]['free'])
            else:
                return 0.0
    except BinanceAPIException as e:
        print(f"API Error fetching {wallet_type} balance for {asset}: {e}")
    except BinanceRequestException as e:
        print(f"Request Error fetching {wallet_type} balance for {asset}: {e}")
    except Exception as e:
        print(f"General Error fetching {wallet_type} balance for {asset}: {e}")
    return None

def run_bot():
    while True:
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        print(f'{timestamp} - Starting monitoring cycle...')

        log_public_ip()

        # Check balances
        usdt_funding = get_wallet_balance("USDT", "funding")
        if usdt_funding is not None:
            print(f'{timestamp} - Funding Wallet USDT: {usdt_funding}')
            if usdt_funding < 1:
                print(f'{timestamp} - Warning: Funding Wallet USDT below 1 — manual top-up recommended.')

        pepe_spot = get_wallet_balance("PEPE", "spot")
        if pepe_spot is not None:
            print(f'{timestamp} - Spot Wallet PEPE: {pepe_spot}')

        hmstr_spot = get_wallet_balance("HMSTR", "spot")
        if hmstr_spot is not None:
            print(f'{timestamp} - Spot Wallet HMSTR: {hmstr_spot}')

        print(f'{timestamp} - Sleeping for 60 seconds before next cycle...\n')
        time.sleep(60)

if __name__ == "__main__":
    # Confirm required env vars
    if not BINANCE_API_KEY or not BINANCE_API_SECRET:
        print("ERROR: Missing Binance API credentials. Set BINANCE_API_KEY and BINANCE_API_SECRET as environment variables.")
    else:
        run_bot()
