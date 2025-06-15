def sma_signal(df):
    if len(df) < 31:
        return "HOLD"

    short = df["close"].rolling(10).mean()
    long = df["close"].rolling(30).mean()

    if short.isna().iloc[-1] or long.isna().iloc[-1]:
        return "HOLD"

    if short.iloc[-2] < long.iloc[-2] and short.iloc[-1] > long.iloc[-1]:
        return "BUY"
    if short.iloc[-2] > long.iloc[-2] and short.iloc[-1] < long.iloc[-1]:
        return "SELL"
    return "HOLD"
