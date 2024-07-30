import requests
import time
import pandas as pd
import numpy as np

ETRADE_API_KEY = 'your_etrade_api_key'
ETRADE_SECRET_KEY = 'your_etrade_secret_key'
ETRADE_OAUTH_TOKEN = 'your_etrade_oauth_token'
ETRADE_OAUTH_TOKEN_SECRET = 'your_etrade_oauth_token_secret'
ETRADE_BASE_URL = 'https://api.etrade.com'

def authenticate():
    auth_url = f"{ETRADE_BASE_URL}/oauth/request_token"
    response = requests.get(auth_url, auth=(ETRADE_API_KEY, ETRADE_SECRET_KEY))
    response_data = response.json()
    oauth_token = response_data['oauth_token']
    oauth_token_secret = response_data['oauth_token_secret']
    return oauth_token, oauth_token_secret

def get_market_data(symbol, oauth_token, oauth_token_secret):
    url = f"{ETRADE_BASE_URL}/v1/market/quote/{symbol}.json"
    headers = {
        'Authorization': f"Bearer {oauth_token}",
        'oauth_token_secret': oauth_token_secret
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    return data

def place_trade(order_details, oauth_token, oauth_token_secret):
    url = f"{ETRADE_BASE_URL}/v1/accounts/{account_id}/orders/place" # type: ignore
    headers = {
        'Authorization': f"Bearer {oauth_token}",
        'oauth_token_secret': oauth_token_secret
    }
    response = requests.post(url, json=order_details, headers=headers)
    return response.json()

def scalping_strategy(market_data):
    short_window = 5
    long_window = 15
    signals = pd.DataFrame(index=market_data.index)
    signals['signal'] = 0.0
    signals['short_mavg'] = market_data['price'].rolling(window=short_window, min_periods=1, center=False).mean()
    signals['long_mavg'] = market_data['price'].rolling(window=long_window, min_periods=1, center=False).mean()
    signals['signal'][short_window:] = np.where(signals['short_mavg'][short_window:] > signals['long_mavg'][short_window:], 1.0, 0.0)
    signals['positions'] = signals['signal'].diff()
    return signals

def trading_bot(symbol):
    oauth_token, oauth_token_secret = authenticate()
    while True:
        market_data = get_market_data(symbol, oauth_token, oauth_token_secret)
        signals = scalping_strategy(market_data)
        if signals['positions'].iloc[-1] == 1.0:
            print("Buy signal detected")
            order_details = {
                'symbol': symbol,
                'quantity': 1,
                'orderType': 'MARKET',
                'action': 'BUY'
            }
            place_trade(order_details, oauth_token, oauth_token_secret)
        elif signals['positions'].iloc[-1] == -1.0:
            print("Sell signal detected")
            order_details = {
                'symbol': symbol,
                'quantity': 1,
                'orderType': 'MARKET',
                'action': 'SELL'
            }
            place_trade(order_details, oauth_token, oauth_token_secret)
        time.sleep(60)

if __name__ == "__main__":
    trading_bot('BTC-USD')
