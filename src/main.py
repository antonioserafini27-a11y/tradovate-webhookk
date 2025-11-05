from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# === Tradovate API Credentials ===
TRADOVATE_CLIENT_ID = os.environ.get("TRADOVATE_CLIENT_ID")
TRADOVATE_USERNAME = os.environ.get("TRADOVATE_USERNAME")
TRADOVATE_PASSWORD = os.environ.get("TRADOVATE_PASSWORD")
TRADOVATE_DEMO = True  # set to False for live trading

# === Global Token Cache ===
auth_token = None
account_id = None

# === Auth Function ===
def authenticate():
    global auth_token, account_id

    host = "https://demo.tradovateapi.com" if TRADOVATE_DEMO else "https://live.tradovateapi.com"
    url = f"{host}/auth/accesstokenrequest"

    payload = {
        "name": TRADOVATE_USERNAME,
        "password": TRADOVATE_PASSWORD,
        "appId": TRADOVATE_CLIENT_ID,
        "appVersion": "1.0",
        "cid": TRADOVATE_CLIENT_ID,
        "sec": "",
        "deviceId": "tradingview-webhook-bot"
    }

    res = requests.post(url, json=payload)
    res.raise_for_status()
    data = res.json()
    auth_token = data['accessToken']

    # Get Account ID
    headers = {"Authorization": f"Bearer {auth_token}"}
    account_res = requests.get(f"{host}/account/list", headers=headers)
    account_res.raise_for_status()
    accounts = account_res.json()
    account_id = accounts[0]['id']

# === Trade Execution ===
def place_trade(side, symbol, quantity):
    if not auth_token:
        authenticate()

    host = "https://demo.tradovateapi.com" if TRADOVATE_DEMO else "https://live.tradovateapi.com"
    headers = {"Authorization": f"Bearer {auth_token}"}

    order = {
        "accountId": account_id,
        "action": side,
        "symbol": symbol,
        "orderQty": quantity,
        "orderType": "Market",
        "timeInForce": "Day"
    }

    order_res = requests.post(f"{host}/order/placeorder", json=order, headers=headers)
    order_res.raise_for_status()
    return order_res.json()

# === Webhook Route ===
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    action = data.get("action")
    symbol = data.get("symbol")
    quantity = data.get("quantity", 1)

    if action and symbol:
        try:
            result = place_trade(action.upper(), symbol, quantity)
            return jsonify({"status": "success", "order": result})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    else:
        return jsonify({"status": "error", "message": "Missing 'action' or 'symbol'"}), 400

# === Run App ===
app.run(host='0.0.0.0', port=8080)
