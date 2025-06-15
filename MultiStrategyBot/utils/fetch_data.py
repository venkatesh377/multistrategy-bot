import requests
import pandas as pd

def get_15m_candles(pair):
    # Format pair using active markets' format
    market = "I-" + pair.replace("-", "_")  # e.g. SOL-INR → I-SOL_INR
    url = f"https://public.coindcx.com/market_data/candles?pair={market}&interval=15m"

    try:
        resp = requests.get(url)
        data = resp.json()
        if not isinstance(data, list) or not data:
            print(f"⚠️ No candle data returned for {pair}")
            return pd.DataFrame()

        df = pd.DataFrame(data)
        df = df.rename(columns={"time":"timestamp"})
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = df[col].astype(float)
        return df

    except Exception as e:
        print(f"❌ Error fetching candles for {pair}:", e)
        return pd.DataFrame()
