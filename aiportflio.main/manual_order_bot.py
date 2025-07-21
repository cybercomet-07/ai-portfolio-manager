import alpaca_trade_api as tradeapi
from twilio.rest import Client

# === Alpaca Credentials ===
ALPACA_API_KEY = "your_key_here"
ALPACA_SECRET_KEY = "your_secret_key"
BASE_URL = 'https://paper-api.alpaca.markets'

# === Twilio WhatsApp Credentials ===
TWILIO_ACCOUNT_SID = "your_sid_here"
TWILIO_AUTH_TOKEN = "your_auth_here"
FROM_WHATSAPP = 'whatsapp:+14155238886'
TO_WHATSAPP = 'whatsapp:+91your_num_here'

# === Setup API Clients ===
api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, BASE_URL)
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# === Order Details ===
symbol = "CRM"  # ✅ Salesforce
qty = 2
side = "buy"
type = "market"
time_in_force = "gtc"

# === Place Order ===
print(f"[⏳] Placing order for {qty}x {symbol} ({side.upper()})...")
order = api.submit_order(
    symbol=symbol,
    qty=qty,
    side=side,
    type=type,
    time_in_force=time_in_force
)

# === Send WhatsApp message ===
message = f"📈 Order Placed from Python!\nSymbol: {symbol}\nQty: {qty}\nSide: {side.upper()}\nOrder ID: {order.id}"
twilio_client.messages.create(
    body=message,
    from_=FROM_WHATSAPP,
    to=TO_WHATSAPP
)

print("✅ Order placed and WhatsApp message sent!")
