import pandas as pd
import numpy as np

# =========================================================
# 1. LOAD DATA
# =========================================================

df = pd.read_csv("2022.csv")

df["timestamp"] = pd.to_datetime(df["timestamp"])

df = df.sort_values("timestamp").reset_index(drop=True)


# =========================================================
# 2. EXACT 5-MINUTE TARGET
# =========================================================

future = df[["timestamp", "close"]].copy()

future["timestamp"] = (
    future["timestamp"] - pd.Timedelta(minutes=5)
)

future = future.rename(
    columns={"close": "future_close"}
)

df = df.merge(
    future,
    on="timestamp",
    how="left"
)

df["future_return"] = (
    (df["future_close"] - df["close"])
    / df["close"]
)


# =========================================================
# 3. FUNCTION FOR PAST PRICE
# =========================================================

def get_past_price(df, minutes):

    current = df[["timestamp"]].copy()

    current["lookup_time"] = (
        current["timestamp"]
        - pd.Timedelta(minutes=minutes)
    )

    history = df[
        ["timestamp", "close"]
    ].copy()

    history = history.rename(
        columns={
            "timestamp": "history_timestamp",
            "close": f"close_{minutes}m_ago"
        }
    )

    current = current.sort_values("lookup_time")

    history = history.sort_values(
        "history_timestamp"
    )

    result = pd.merge_asof(
        current,
        history,
        left_on="lookup_time",
        right_on="history_timestamp",
        direction="backward"
    )

    result = result.sort_values("timestamp")

    return result[
        [
            "timestamp",
            f"close_{minutes}m_ago"
        ]
    ]


# =========================================================
# 4. PAST PRICE FEATURES
# =========================================================

for minutes in [5, 10, 15]:

    past = get_past_price(df, minutes)

    df = df.merge(
        past,
        on="timestamp",
        how="left"
    )

    df[f"return_{minutes}m"] = (
        df["close"]
        / df[f"close_{minutes}m_ago"]
        - 1
    )


# =========================================================
# 5. NORMAL FEATURES
# =========================================================

df["return_1m"] = df["close"].pct_change()

df["SMA_5"] = (
    df["close"].rolling(5).mean()
)

df["SMA_15"] = (
    df["close"].rolling(15).mean()
)

df["SMA_30"] = (
    df["close"].rolling(30).mean()
)

df["EMA_10"] = (
    df["close"]
    .ewm(span=10, adjust=False)
    .mean()
)


# =========================================================
# 6. RSI
# =========================================================

delta = df["close"].diff()

gain = delta.clip(lower=0)

loss = -delta.clip(upper=0)

avg_gain = gain.rolling(14).mean()

avg_loss = loss.rolling(14).mean()

rs = avg_gain / (avg_loss + 1e-9)

df["RSI"] = (
    100 - (100 / (1 + rs))
)


# =========================================================
# 7. MACD
# =========================================================

ema12 = (
    df["close"]
    .ewm(span=12, adjust=False)
    .mean()
)

ema26 = (
    df["close"]
    .ewm(span=26, adjust=False)
    .mean()
)

df["MACD"] = ema12 - ema26


# =========================================================
# 8. VOLATILITY
# =========================================================

df["volatility"] = (
    df["return_1m"]
    .rolling(30)
    .std()
)


# =========================================================
# 9. VOLUME
# =========================================================

df["volume_change"] = (
    df["volume"].pct_change()
)


# =========================================================
# 10. CLEAN
# =========================================================

df = df.replace(
    [np.inf, -np.inf],
    np.nan
)

df = df.dropna().reset_index(drop=True)


# =========================================================
# 11. SAVE
# =========================================================

df.to_csv(
    "features_v3.csv",
    index=False
)


# =========================================================
# 12. CHECK RESULTS
# =========================================================

print("Shape:")
print(df.shape)

print("\nSample:")

print(
    df[
        [
            "timestamp",
            "close",
            "close_5m_ago",
            "return_5m",
            "close_10m_ago",
            "return_10m",
            "close_15m_ago",
            "return_15m",
            "future_close",
            "future_return"
        ]
    ].head(20).to_string(index=False)
)