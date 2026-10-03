import pandas as pd
import numpy as np


# =========================================================
# 1. LOAD DATA
# =========================================================

df = pd.read_csv("2022.csv")

df["timestamp"] = pd.to_datetime(df["timestamp"])

# Sort chronologically
df = df.sort_values("timestamp").reset_index(drop=True)


# =========================================================
# 2. REMOVE DUPLICATE TIMESTAMPS
# =========================================================

df = df.drop_duplicates(
    subset="timestamp"
).reset_index(drop=True)


# =========================================================
# 3. CREATE 1-MINUTE TIMELINE
# =========================================================

df = df.set_index("timestamp")

df = df.resample("1min").asfreq()


# =========================================================
# 4. HANDLE MISSING MARKET DATA
# =========================================================

# Forward fill close because we need a continuous
# price series for calculating indicators.

df["close"] = df["close"].ffill()


# If there was no trade during a minute,
# volume should be 0.

df["volume"] = df["volume"].fillna(0)


# Remove rows where close is still missing
# (mainly before the first real price).

df = df.dropna(
    subset=["close"]
)


# =========================================================
# 5. FUTURE PRICE / TARGET
# =========================================================

# Price exactly 5 minutes in the future.

df["future_close"] = (
    df["close"].shift(-5)
)


# Future 5-minute return

df["future_return"] = (
    (df["future_close"] - df["close"])
    / df["close"]
)


# =========================================================
# 6. RETURNS
# =========================================================

df["return_1m"] = (
    df["close"].pct_change(1)
)

df["return_5m"] = (
    df["close"].pct_change(5)
)

df["return_10m"] = (
    df["close"].pct_change(10)
)

df["return_15m"] = (
    df["close"].pct_change(15)
)


# =========================================================
# 7. MOVING AVERAGES
# =========================================================

df["SMA_5"] = (
    df["close"]
    .rolling(5)
    .mean()
)

df["SMA_15"] = (
    df["close"]
    .rolling(15)
    .mean()
)

df["SMA_30"] = (
    df["close"]
    .rolling(30)
    .mean()
)


# =========================================================
# 8. EMA
# =========================================================

df["EMA_10"] = (
    df["close"]
    .ewm(
        span=10,
        adjust=False
    )
    .mean()
)


# =========================================================
# 9. RSI
# =========================================================

delta = df["close"].diff()

gain = delta.clip(lower=0)

loss = -delta.clip(upper=0)

avg_gain = (
    gain
    .rolling(14)
    .mean()
)

avg_loss = (
    loss
    .rolling(14)
    .mean()
)

# Avoid division by zero

avg_loss = avg_loss.replace(
    0,
    np.nan
)

rs = avg_gain / avg_loss

df["RSI"] = (
    100 -
    (
        100 /
        (1 + rs)
    )
)


# =========================================================
# 10. MACD
# =========================================================

ema_12 = (
    df["close"]
    .ewm(
        span=12,
        adjust=False
    )
    .mean()
)

ema_26 = (
    df["close"]
    .ewm(
        span=26,
        adjust=False
    )
    .mean()
)

df["MACD"] = (
    ema_12 - ema_26
)


# =========================================================
# 11. VOLATILITY
# =========================================================

df["volatility"] = (
    df["return_1m"]
    .rolling(30)
    .std()
)


# =========================================================
# 12. VOLUME CHANGE
# =========================================================

# IMPORTANT:
# pct_change() creates infinity when the previous
# volume is 0.
#
# Replace infinity with NaN and remove later.

df["volume_change"] = (
    df["volume"]
    .pct_change()
)

df["volume_change"] = (
    df["volume_change"]
    .replace(
        [np.inf, -np.inf],
        np.nan
    )
)


# =========================================================
# 13. REMOVE INFINITE VALUES
# =========================================================

df = df.replace(
    [np.inf, -np.inf],
    np.nan
)


# =========================================================
# 14. REMOVE INVALID ROWS
# =========================================================

df = df.dropna().reset_index()


# =========================================================
# 15. FINAL SAFETY CHECK
# =========================================================

# Check whether any infinity remains.

numeric_columns = df.select_dtypes(
    include=[np.number]
).columns

infinite_count = np.isinf(
    df[numeric_columns].to_numpy()
).sum()

print("\nInfinite values:", infinite_count)


# Check missing values

missing_count = df.isna().sum().sum()

print("Missing values:", missing_count)


# =========================================================
# 16. DISPLAY SHAPE
# =========================================================

print("\nShape:")

print(df.shape)


# =========================================================
# 17. DISPLAY SAMPLE
# =========================================================

print("\nSample:")

print(
    df[
        [
            "timestamp",
            "close",

            "return_1m",
            "return_5m",
            "return_10m",
            "return_15m",

            "SMA_5",
            "SMA_15",
            "SMA_30",

            "EMA_10",

            "RSI",
            "MACD",

            "volatility",

            "volume",
            "volume_change",

            "future_close",
            "future_return"
        ]
    ]
    .head(20)
    .to_string(index=False)
)


# =========================================================
# 18. SAVE
# =========================================================

df.to_csv(
    "features_v4.csv",
    index=False
)

print(
    "\nSaved as features_v4.csv"
)