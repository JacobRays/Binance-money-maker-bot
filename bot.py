import os
import time
from binance.client import Client
from binance.enums import *
from dotenv import load_dotenv

# Load environment variables if running locally
load_dotenv()

API_KEY = os.getenv("NVeBs2NVZ9JwHX2CF9KDgL2dSLmM08WLghm9c7tXXb5cxrRQFsK0m0lKxFKj8lGE")
API_SECRET = os.getenv("8a30DhaVRMCZodf41JLfIBB7tfYEgmBXva9eyQwPCGTr1hzZ3UaZZpwNkWB91a1g")

client = Client(API_KEY, API_SECRET)

TRADING_PAIR = 'BTCUSDT'
TRADE_AMOUNT = 0.01783444  # or equivalent in USDT
STOP_LOSS_PERCENTAGE = 0.02  # 2%
TAKE_PROFIT_PERCENTAGE = 0.05  # 5%

def get_price(symbol):
    ticker = client.get_symbol_ticker(symbol=symbol)
    return float(ticker['price'])

def place_buy_order(symbol, usdt_amount):
    price = get_price(symbol)
    quantity = round(usdt_amount / price, 6)  # Binance requires up to 6 decimal places
    order = client.order_market_buy(symbol=symbol, quantity=quantity)
    print(f"BUY executed at price {price}")
    return order, price

def place_sell_order(symbol, quantity):
    order = client.order_market_sell(symbol=symbol, quantity=quantity)
    print("SELL order executed.")
    return order

def get_wallet_balances():
    spot_balances = client.get_account()
    funding_balances = client.get_funding_wallet()
    return spot_balances, funding_balances

def transfer_from_funding_to_spot(asset, amount):
    client.transfer_funding_to_spot(asset=asset, amount=amount)
    print(f"Transferred {amount} {asset} from funding to spot wallet.")

def trade():
    # Make sure there's enough balance in spot wallet; transfer if needed
    spot_balances, funding_balances = get_wallet_balances()
    usdt_in_spot = next((float(b['free']) for b in spot_balances['balances'] if b['asset'] == 'USDT'), 0.0)

    if usdt_in_spot < TRADE_AMOUNT:
        funding_usdt = next((float(b['free']) for b in funding_balances['assets'] if b['asset'] == 'USDT'), 0.0)
        if funding_usdt >= TRADE_AMOUNT:
            transfer_from_funding_to_spot('USDT', TRADE_AMOUNT)
            time.sleep(5)  # wait for transfer to complete
        else:
            print("Not enough funds in funding or spot wallet.")
            return

    buy_order, buy_price = place_buy_order(TRADING_PAIR, TRADE_AMOUNT)
    quantity = float(buy_order['executedQty'])

    while True:
        current_price = get_price(TRADING_PAIR)
        if current_price >= buy_price * (1 + TAKE_PROFIT_PERCENTAGE):
            place_sell_order(TRADING_PAIR, quantity)
            print(f"Take profit triggered at price {current_price}")
            break
        elif current_price <= buy_price * (1 - STOP_LOSS_PERCENTAGE):
            place_sell_order(TRADING_PAIR, quantity)
            print(f"Stop loss triggered at price {current_price}")
            break
        print(f"Monitoring price: {current_price} | Buy price: {buy_price}")
        time.sleep(30)  # check every 30 seconds

if __name__ == '__main__':
    trade()
