def breakout_signal(df):
    if len(df) < 8:
        return "HOLD"

    high7 = df["high"].rolling(7).max()
    low7 = df["low"].rolling(7).min()

    if high7.isna().iloc[-2] or low7.isna().iloc[-2]:
        return "HOLD"

    price = df["close"].iloc[-1]

    if price > high7.iloc[-2]:
        return "BUY"
    if price < low7.iloc[-2]:
        return "SELL"
    return "HOLD"
