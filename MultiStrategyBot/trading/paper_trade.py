import os
import csv
from datetime import datetime
from utils.fetch_data import get_15m_candles

class PaperTrader:
    def __init__(self, start_budget):
        self.csv = "logs/trades.csv"
        os.makedirs(os.path.dirname(self.csv), exist_ok=True)
        self.budget = start_budget
        self.active = None  # (pair, action, entry, amount, sl, tp)

    def has_active_trade(self):
        return self.active is not None

    def execute_trade(self, pair, action, entry_price):
        sl = round(entry_price * 0.97, 2)
        tp = round(entry_price * 1.05, 2)
        amount = self.budget / entry_price
        self.active = (pair, action, entry_price, amount, sl, tp)
        self.log_trade(pair, action, entry_price, self.budget, 0, sl, tp, "ENTRY")

    def close_trade(self, price, reason="CLOSE"):
        pair, action, entry_price, amount, sl, tp = self.active
        value = amount * price
        pnl = value - self.budget
        self.budget += pnl
        self.log_trade(pair, "SELL" if action == "BUY" else "BUY", price, self.budget, pnl, sl, tp, reason)
        self.active = None

    def log_trade(self, pair, action, price, balance, pnl, sl, tp, reason):
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            pair, action, round(price, 2),
            round(balance, 2), round(pnl, 2),
            round(sl, 2), round(tp, 2), reason
        ]
        with open(self.csv, "a", newline="") as f:
            csv.writer(f).writerow(row)
        print(f"[{row[0]}] {pair} {action} @ ₹{price:.2f} | Bal: ₹{balance:.2f} | P&L: ₹{pnl:+.2f} | SL: ₹{sl:.2f} | TP: ₹{tp:.2f} | {reason}")

    def save_state(self):
        if not self.active:
            return

        pair, action, entry_price, amount, sl, tp = self.active

        # ✅ TEST MODE: Simulate SL hit without API
        if pair.strip().upper() == "TEST-INR":
            print("💡 Simulating SL hit for TEST-INR...")
            fake_price = sl - 1
            self.close_trade(fake_price, reason="SIMULATED STOP-LOSS")
            return

        df = get_15m_candles(pair)
        if df.empty or "close" not in df.columns or df["close"].dropna().empty:
            print(f"⚠️ Skipping {pair}: no valid price data.")
            return

        price = df["close"].dropna().iloc[-1]

        if action == "BUY":
            if price <= sl:
                self.close_trade(price, reason="STOP-LOSS")
            elif price >= tp:
                self.close_trade(price, reason="TAKE-PROFIT")
        elif action == "SELL":
            if price >= sl:
                self.close_trade(price, reason="STOP-LOSS")
            elif price <= tp:
                self.close_trade(price, reason="TAKE-PROFIT")
