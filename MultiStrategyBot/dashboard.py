import streamlit as st
import pandas as pd
import json
import os
from utils.fetch_data import get_15m_candles
from strategies.rsi import rsi_signal
from strategies.sma_crossover import sma_signal
import matplotlib.pyplot as plt

STATE_FILE = "controller.json"
TRADE_LOG = "logs/trades.csv"
SETTINGS_FILE = "settings.json"

# Load/save state
def load_state():
    if not os.path.exists(STATE_FILE):
        save_state("STOPPED")
    with open(STATE_FILE, "r") as f:
        return json.load(f)["state"]

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump({"state": state}, f)

# Load/save config
def load_settings():
    default = {"sl_percent": 3.0, "tp_percent": 5.0, "budget": 1000}
    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "w") as f:
            json.dump(default, f)
    with open(SETTINGS_FILE, "r") as f:
        return json.load(f)

def save_settings(sl, tp, budget):
    with open(SETTINGS_FILE, "w") as f:
        json.dump({"sl_percent": sl, "tp_percent": tp, "budget": budget}, f)

st.set_page_config(page_title="Trading Bot Dashboard", layout="wide")
st.title("🚀 Trading Bot Control Panel")

# Bot state controls
state = load_state()
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🟢 START"):
        save_state("RUNNING")
        st.rerun()
with col2:
    if st.button("🔴 STOP"):
        save_state("STOPPED")
        st.rerun()
with col3:
    if st.button("🔁 RESET"):
        save_state("STOPPED")
        st.rerun()
st.markdown(f"### Current State: **{state}**")

# Settings controls
settings = load_settings()
st.subheader("⚙️ Trade Configuration")
sl = st.slider("Stop Loss %", 1.0, 10.0, float(settings["sl_percent"]), step=0.5)
tp = st.slider("Take Profit %", 1.0, 20.0, float(settings["tp_percent"]), step=0.5)
budget = st.number_input("Trade Budget (INR)", min_value=100, max_value=10000, value=int(settings["budget"]))
if st.button("💾 Save Settings"):
    save_settings(sl, tp, budget)
    st.success("Settings updated")

# Trade status
st.subheader("📈 Current Trade (Live from trades.csv)")
if os.path.exists(TRADE_LOG):
    df = pd.read_csv(TRADE_LOG)
    if not df.empty:
        last = df.tail(1).iloc[0]
        st.write(f"**{last['pair']}** | {last['action']} @ ₹{last['price']}")
        st.write(f"Balance: ₹{last['balance']} | P&L: ₹{last['pnl']}")
    else:
        st.info("No trades yet.")
else:
    st.info("No trades yet.")

# Trade history
st.subheader("📂 Trade History")
if os.path.exists(TRADE_LOG):
    df = pd.read_csv(TRADE_LOG)
    st.dataframe(df.tail(20), use_container_width=True)
else:
    st.write("No trade log found.")

# Summary stats
st.subheader("📊 Performance Summary")
if os.path.exists(TRADE_LOG):
    df = pd.read_csv(TRADE_LOG)
    wins = df[df["pnl"] > 0]
    losses = df[df["pnl"] < 0]
    total = len(df)
    win_rate = (len(wins) / total) * 100 if total else 0
    total_pnl = df["pnl"].sum()
    avg_win = wins["pnl"].mean() if not wins.empty else 0
    avg_loss = losses["pnl"].mean() if not losses.empty else 0
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Trades", total)
    col2.metric("Win Rate", f"{win_rate:.2f}%")
    col3.metric("Total P&L", f"₹{total_pnl:.2f}")
    col4.metric("Avg Win / Loss", f"₹{avg_win:.2f} / ₹{avg_loss:.2f}")
else:
    st.write("No performance data available.")
# 📊 Technical Chart Viewer
st.subheader("📉 Technical Chart Viewer")

coin = st.selectbox("Select Coin to View", [
    "SOL-INR", "XRP-INR", "USDT-INR", "BUSD-INR", "DOT-INR",
    "ADA-INR", "MATIC-INR", "ETH-INR", "BTC-INR", "LINK-INR"
])

df = get_15m_candles(coin)

if not df.empty:
    df["RSI"] = df["close"].rolling(14).apply(lambda x: 100 - (100 / (1 + ((x.diff().clip(lower=0).mean()) / (abs(x.diff()).mean() + 1e-9)))))
    df["SMA20"] = df["close"].rolling(window=20).mean()

    fig, ax = plt.subplots(3, 1, figsize=(10, 6), sharex=True)
    
    # Price with SMA
    ax[0].plot(df["close"], label="Close Price", color='blue')
    ax[0].plot(df["SMA20"], label="SMA 20", color='orange')
    ax[0].legend(loc="upper left")
    ax[0].set_ylabel("Price")

    # RSI
    ax[1].plot(df["RSI"], color='purple')
    ax[1].axhline(70, linestyle="--", color="red", linewidth=1)
    ax[1].axhline(30, linestyle="--", color="green", linewidth=1)
    ax[1].set_ylabel("RSI")

    # Volume (if needed)
    ax[2].bar(df.index, df["volume"], color='grey')
    ax[2].set_ylabel("Volume")

    st.pyplot(fig)
else:
    st.warning("No data available for this coin.")
