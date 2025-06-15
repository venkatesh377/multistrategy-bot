def decide_signal(signals):
    if signals.count("BUY") >= 2:
        return "BUY"
    if signals.count("SELL") >= 2:
        return "SELL"
    return "HOLD"
