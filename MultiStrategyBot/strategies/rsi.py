import pandas as pd

def rsi_signal(df):
    if len(df) < 15:
        return "HOLD"

    delta = df["close"].diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    roll_up = up.rolling(14).mean()
    roll_down = down.rolling(14).mean()
    rs = roll_up / roll_down
    rsi = 100 - (100 / (1 + rs))

    if rsi.empty or pd.isna(rsi.iloc[-1]):
        return "HOLD"

    last = rsi.iloc[-1]
    return "BUY" if last < 30 else "SELL" if last > 70 else "HOLD"
