import time
import os
import json

from dotenv import load_dotenv
from real_trade import place_real_order
from utils.fetch_data import get_15m_candles
from strategies.rsi import rsi_signal
from strategies.sma_crossover import sma_signal
from strategies.breakout import breakout_signal
from logic.signal_evaluator import decide_signal
from trading.paper_trade import PaperTrader

def load_settings():
    default = {"sl_percent": 3.0, "tp_percent": 5.0, "budget": 1000}
    try:
        with open("settings.json", "r") as f:
            return json.load(f)
    except:
        return default

# 🚦 Control panel state reader
def get_bot_state():
    try:
        with open("controller.json", "r") as f:
            return json.load(f).get("state", "STOPPED")
    except:
        return "STOPPED"

# 🔐 Load keys and flags from .env
load_dotenv()
API_KEY = os.getenv("COINDCX_API_KEY", "").strip()
API_SECRET = os.getenv("COINDCX_API_SECRET", "").strip()
REAL_TRADING = os.getenv("REAL_TRADING", "False").strip().lower() == "true"

settings = load_settings()
SL_PERCENT = float(settings.get("sl_percent", 3.0))
TP_PERCENT = float(settings.get("tp_percent", 5.0))
TRADE_BUDGET = float(settings.get("budget", 1000))

# 🪙 Coins to scan
COINS = [
    "SOL-INR", "XRP-INR", "USDT-INR", "BUSD-INR", "DOT-INR",
    "ADA-INR", "MATIC-INR", "ETH-INR", "BTC-INR", "LINK-INR"
]

trader = PaperTrader(start_budget=TRADE_BUDGET)

# 🔁 Bot loop
while True:
    if get_bot_state() != "RUNNING":
        print("⏸ Bot is currently stopped by dashboard.")
        time.sleep(5)
        continue

    if trader.has_active_trade():
        print("Already in an active trade; waiting for SL/TP check...")
    else:
        for pair in COINS:
            df = get_15m_candles(pair)

            if df.empty or "close" not in df.columns or df["close"].dropna().empty:
                print(f"⚠️ Skipping {pair}: no valid candle data.")
                continue

            sigs = {
                "RSI": rsi_signal(df),
                "SMA": sma_signal(df),
                "Breakout": breakout_signal(df),
            }

            action = decide_signal(list(sigs.values()))
            print(f"Pair {pair}: signals {sigs} → {action}")

            if action in ("BUY", "SELL"):
                price = df["close"].dropna().iloc[-1]

                if REAL_TRADING:
                    quantity = round(TRADE_BUDGET / price, 4)
                    result = place_real_order(API_KEY, API_SECRET, action, pair, price, quantity)
                    print("🚀 Real order placed:", result)
                else:
                    trader.execute_trade(pair, action, price)
                break  # Stop after one trade

    trader.save_state()
    time.sleep(10)
