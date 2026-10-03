import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

import numpy as np


# =========================================================
# 1. LOAD DATA
# =========================================================

df = pd.read_csv("features_v4.csv")

df["timestamp"] = pd.to_datetime(df["timestamp"])

df = df.sort_values("timestamp").reset_index(drop=True)


# =========================================================
# 2. FEATURES
# =========================================================

features = [

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
    "volume_change"
]


# =========================================================
# 3. TRAIN / TEST SPLIT
# =========================================================

train = df[
    df["timestamp"] < "2022-12-01"
]

test = df[
    (df["timestamp"] >= "2022-12-01") &
    (df["timestamp"] < "2023-01-01")
]


X_train = train[features]

X_test = test[features]


# =========================================================
# 4. TARGET
# =========================================================

# We predict the percentage return
# over the next 5 minutes.

y_train = train["future_return"]

y_test = test["future_return"]


print("Training rows:", len(X_train))

print("Testing rows:", len(X_test))

print("Features:", len(features))


# =========================================================
# 5. TRAIN MODEL
# =========================================================

print("\nTraining Random Forest Regressor...")


model = RandomForestRegressor(

    n_estimators=300,

    max_depth=12,

    min_samples_leaf=10,

    random_state=42,

    n_jobs=-1
)


model.fit(

    X_train,

    y_train
)


print("Training completed!")


# =========================================================
# 6. PREDICT RETURN
# =========================================================

predicted_return = model.predict(X_test)


# =========================================================
# 7. CONVERT RETURN → PRICE
# =========================================================

predicted_price = (

    test["close"].values *

    (1 + predicted_return)

)


actual_price = test["future_close"].values


# =========================================================
# 8. EVALUATION
# =========================================================

mae_return = mean_absolute_error(

    y_test,

    predicted_return
)


rmse_return = np.sqrt(

    mean_squared_error(

        y_test,

        predicted_return
    )

)


mae_price = mean_absolute_error(

    actual_price,

    predicted_price
)


rmse_price = np.sqrt(

    mean_squared_error(

        actual_price,

        predicted_price
    )

)


print("\n================================")

print("RETURN RESULTS")

print("================================")


print("MAE:", mae_return)

print("RMSE:", rmse_return)


print("\n================================")

print("PRICE RESULTS")

print("================================")


print("MAE:", mae_price)

print("RMSE:", rmse_price)


# =========================================================
# 9. DIRECTIONAL ACCURACY
# =========================================================

actual_direction = y_test > 0

predicted_direction = predicted_return > 0


direction_accuracy = (

    actual_direction == predicted_direction

).mean()


print(

    "\nDirectional Accuracy:",

    direction_accuracy * 100,

    "%"

)

# =========================================================
# 10. PREDICTION COMPARISON
# =========================================================

results = test[
    [
        "timestamp",
        "future_close"
    ]
].copy()


# Rename future_close to actual_price
results.rename(
    columns={
        "future_close": "actual_price"
    },
    inplace=True
)


# Add predicted price
results["predicted_price"] = predicted_price


# Calculate absolute error
results["error"] = (
    results["actual_price"]
    - results["predicted_price"]
).abs()


# Round values for easier reading
results["actual_price"] = results["actual_price"].round(2)

results["predicted_price"] = results["predicted_price"].round(2)

results["error"] = results["error"].round(2)


# =========================================================
# 11. DISPLAY COMPARISON
# =========================================================

print("\n================================")
print("ACTUAL VS PREDICTED PRICE")
print("================================")

print(
    results[
        [
            "timestamp",
            "actual_price",
            "predicted_price",
            "error"
        ]
    ].head(20).to_string(index=False)
)


# =========================================================
# 12. SAVE RESULTS
# =========================================================

results.to_csv(
    "prediction_results.csv",
    index=False
)

print("\nAll predictions saved to prediction_results.csv")