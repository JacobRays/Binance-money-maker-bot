import os
import time
from binance.client import Client
from binance.enums import *

# Setup Binance API keys (ensure your API keys are stored securely)
API_KEY = os.getenv('NVeBs2NVZ9JwHX2CF9KDgL2dSLmM08WLghm9c7tXXb5cxrRQFsK0m0lKxFKj8lGE')
API_SECRET = os.getenv('8a30DhaVRMCZodf41JLfIBB7tfYEgmBXva9eyQwPCGTr1hzZ3UaZZpwNkWB91a1g')

client = Client(API_KEY, API_SECRET)

# Define the trading pair and balance for trading
TRADING_PAIR = 'BTCUSDT'
BALANCE = 0.01768249
STOP_LOSS_PERCENTAGE = 0.02  # 2% stop loss
TAKE_PROFIT_PERCENTAGE = 0.05  # 5% take profit

# Fetch market data (order book)
def get_market_data(pair):
    depth = client.get_order_book(symbol=pair)
    return depth

# Get current price
def get_current_price(pair):
    ticker = client.get_symbol_ticker(symbol=pair)
    return float(ticker['price'])

# Buy at lowest ask price
def buy_at_lowest_price(pair):
    market_data = get_market_data(pair)
    lowest_ask = float(market_data['asks'][0][0])  # Lowest ask price
    quantity = BALANCE / lowest_ask
    order = client.order_limit_buy(
        symbol=pair,
        quantity=quantity,
        price=str(lowest_ask)
    )
    return order, lowest_ask

# Sell at highest bid price
def sell_at_highest_price(pair):
    market_data = get_market_data(pair)
    highest_bid = float(market_data['bids'][0][0])  # Highest bid price
    quantity = BALANCE  # Assume the bot sells all
    order = client.order_limit_sell(
        symbol=pair,
        quantity=quantity,
        price=str(highest_bid)
    )
    return order

# Take Profit Logic
def check_take_profit(buy_price):
    current_price = get_current_price(TRADING_PAIR)
    if current_price >= buy_price * (1 + TAKE_PROFIT_PERCENTAGE):
        sell_order = sell_at_highest_price(TRADING_PAIR)
        print(f"Take Profit Triggered. Sold at {sell_order['fills'][0]['price']}")
        return True
    return False

# Stop Loss Logic
def check_stop_loss(buy_price):
    current_price = get_current_price(TRADING_PAIR)
    if current_price <= buy_price * (1 - STOP_LOSS_PERCENTAGE):
        sell_order = sell_at_highest_price(TRADING_PAIR)
        print(f"Stop Loss Triggered. Sold at {sell_order['fills'][0]['price']}")
        return True
    return False

# Main trading loop for Binance Money Maker Bot
def trade():
    # Buy at the lowest price
    buy_order, buy_price = buy_at_lowest_price(TRADING_PAIR)
    print(f"Binance Money Maker Bot bought at {buy_price}")

    # Continuously monitor for Take Profit or Stop Loss
    while True:
        if check_take_profit(buy_price):
            break
        if check_stop_loss(buy_price):
            break

        # Wait for a short interval before checking again
        time.sleep(30)  # Adjust the sleep time based on your strategy

if __name__ == '__main__':
    trade()
