import time
import yfinance as yf
import pandas as pd
import ta
from datetime import datetime
from alpaca_trade_api.rest import REST
from twilio.rest import Client

# 🔐 Alpaca Paper Trading Keys
API_KEY = "your_key_here"
API_SECRET = "your_secret_here"
BASE_URL = 'https://paper-api.alpaca.markets'
api = REST(API_KEY, API_SECRET, BASE_URL)

# 🔐 Twilio WhatsApp Credentials
TWILIO_ACCOUNT_SID = "your_sid_here"
TWILIO_AUTH_TOKEN = "your_token_here"
FROM_WHATSAPP_NUMBER = "whatsapp:+14155238886"
TO_WHATSAPP_NUMBER = "whatsapp:+91your_number_here"
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# ✅ List of tickers to analyze
tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "CRM"]  # Add/remove as needed

def send_whatsapp_message(message):
    client.messages.create(body=message, from_=FROM_WHATSAPP_NUMBER, to=TO_WHATSAPP_NUMBER)

def analyze_stock(symbol):
    df = yf.download(symbol, period='60d', interval='1h')
    df.dropna(inplace=True)
    close_prices = df['Close']
    rsi = ta.momentum.RSIIndicator(close_prices).rsi()
    macd_obj = ta.trend.MACD(close_prices)
    macd_line = macd_obj.macd()
    macd_signal = macd_obj.macd_signal()

    latest_rsi = rsi.iloc[-1]
    latest_macd = macd_line.iloc[-1]
    latest_signal = macd_signal.iloc[-1]
    latest_price = close_prices.iloc[-1]

    print(f"🔎 {symbol} - RSI: {latest_rsi:.2f}, MACD: {latest_macd:.2f}, Signal: {latest_signal:.2f}")
    action = "HOLD"
    if latest_rsi < 30 and latest_macd > latest_signal:
        action = "BUY"
    elif latest_rsi > 70 and latest_macd < latest_signal:
        action = "SELL"

    print(f"➡️ {symbol} Decision: {action} at ${latest_price:.2f}")
    return action, latest_price

def get_position_qty(symbol):
    try:
        position = api.get_position(symbol)
        return int(float(position.qty))
    except:
        return 0

def execute_trade(symbol, action, price):
    qty = int(1000 / price)
    if action == "BUY":
        api.submit_order(symbol=symbol, qty=qty, side='buy', type='market', time_in_force='gtc')
        msg = f"✅ BUY: {qty} shares of {symbol} at ${price:.2f}"
        send_whatsapp_message(msg)
        print(msg)

    elif action == "SELL":
        position_qty = get_position_qty(symbol)
        if position_qty > 0:
            api.submit_order(symbol=symbol, qty=position_qty, side='sell', type='market', time_in_force='gtc')
            msg = f"❌ SELL: {position_qty} shares of {symbol} at ${price:.2f}"
            send_whatsapp_message(msg)
            print(msg)

def log_to_csv(symbol, action, price):
    with open("trading_log.csv", "a") as f:
        f.write(f"{datetime.now()},{symbol},{action},{price:.2f}\n")

# 🔁 Daily automation
def wait_until_market_open():
    while True:
        clock = api.get_clock()
        if clock.is_open and (datetime.now().minute >= 30):
            print("✅ Market is open + 30 min passed. Starting trades...\n")
            break
        else:
            print("⏳ Waiting for market open + 30 min...")
            time.sleep(60)

def run_bot():
    print("🚀 Running AI Trading Bot...\n")
    for symbol in tickers:
        try:
            action, price = analyze_stock(symbol)
            if action != "HOLD":
                execute_trade(symbol, action, price)
            log_to_csv(symbol, action, price)
        except Exception as e:
            print(f"⚠️ Error processing {symbol}: {e}")

# MAIN LOOP
if __name__ == "__main__":
    wait_until_market_open()
    run_bot()
