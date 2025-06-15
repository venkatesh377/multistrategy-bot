import requests
import time
import hmac
import hashlib
import json
import os

def place_real_order(api_key, api_secret, side, market, price, quantity):
    url = "https://api.coindcx.com/exchange/v1/orders/create"
    timestamp = int(time.time() * 1000)
    body = {
        "market": market.replace("-", "_"),
        "side": side.lower(),
        "order_type": "market_order",
        "total_quantity": quantity,
        "timestamp": timestamp
    }
    signature = hmac.new(api_secret.encode(), json.dumps(body).encode(), hashlib.sha256).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "X-AUTH-APIKEY": api_key,
        "X-AUTH-SIGNATURE": signature
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(body))
        return response.json()
    except Exception as e:
        return {"error": str(e)}