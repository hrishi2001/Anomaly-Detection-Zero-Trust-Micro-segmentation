#ml/train_model.py
import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
import os

# Paths
LOG_FILE = "logs/requests.csv"
MODEL_FILE = "ml/api_anomaly_model.pkl"
ANOMALY_LOG_FILE = "logs/requests_with_anomaly.csv"
ANOMALIES_ONLY_FILE = "logs/anomalies_only.csv"

# Step 1: Load logs
if not os.path.exists(LOG_FILE):
    raise FileNotFoundError(f"{LOG_FILE} not found. Make sure Phase 1+2 are complete.")

df = pd.read_csv(LOG_FILE)

# Step 2: Convert categorical to numeric
df["method_code"] = df["method"].astype('category').cat.codes
df["endpoint_code"] = df["endpoint"].astype('category').cat.codes

# Step 3: Select features
X = df[["method_code", "endpoint_code", "status_code"]]

# Step 4: Train Isolation Forest
model = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
model.fit(X)

# Step 5: Predict anomalies (-1 = anomaly, 1 = normal)
df["anomaly_if_model"] = model.predict(X)

# Step 6: Hybrid rule-based anomaly detection
# Treat specific status codes as anomalies
df["anomaly"] = df.apply(
    lambda row: -1 if row["status_code"] in [401, 403, 500] else row["anomaly_if_model"],
    axis=1
)

# Step 7: Save model
os.makedirs("ml", exist_ok=True)
joblib.dump(model, MODEL_FILE)

# Step 8: Save all predictions
os.makedirs("logs", exist_ok=True)
df.to_csv(ANOMALY_LOG_FILE, index=False)

# Step 9: Save only anomalies
anomalies_df = df[df["anomaly"] == -1]
if not anomalies_df.empty:
    anomalies_df.to_csv(ANOMALIES_ONLY_FILE, index=False)
    print(f"Anomalies saved to {ANOMALIES_ONLY_FILE}")
else:
    print("No anomalies detected in this dataset.")

# Step 10: Print sample predictions
print(f"Model trained and saved to {MODEL_FILE}")
print(f"Anomaly predictions saved to {ANOMALY_LOG_FILE}")
print("Sample predictions:")
print(df[["timestamp", "endpoint", "method", "status_code", "anomaly"]].head())
