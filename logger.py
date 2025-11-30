import pandas as pd
from fastapi import Request
from datetime import datetime
import os
import joblib
from sklearn.ensemble import IsolationForest

LOG_FILE = "logs/requests.csv"
MODEL_FILE = "ml/api_anomaly_model.pkl"
ANOMALIES_ONLY_FILE = "logs/anomalies_only.csv"

os.makedirs("logs", exist_ok=True)

async def log_request(request: Request, response_status: int):
    # --- Log the request ---
    from datetime import datetime

    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")  # fallback

    log_entry = {
        "timestamp": timestamp,
        "endpoint": request.url.path,
        "method": request.method,
        "status_code": int(response_status),
        "label": "",
        "path": str(request.url.path),
    }
    # Append to requests.csv
    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)
        df = pd.concat([df, pd.DataFrame([log_entry])], ignore_index=True)
    else:
        df = pd.DataFrame([log_entry])
    df.to_csv(LOG_FILE, index=False)

    # --- Anomaly Detection ---
    if not os.path.exists(MODEL_FILE):
        return  # model not trained yet

    model = joblib.load(MODEL_FILE)

    # Add numeric encoding
    df["method_code"] = df["method"].astype('category').cat.codes
    df["endpoint_code"] = df["endpoint"].astype('category').cat.codes

    # Predict anomalies for last row
    last_row = df.iloc[[-1]].copy()
    X_last = last_row[["method_code", "endpoint_code", "status_code"]]
    last_row["anomaly_if_model"] = model.predict(X_last)
    
    # Hybrid rule: treat specific status codes as anomalies
    last_row["anomaly"] = last_row.apply(
        lambda row: -1 if row["status_code"] in [401, 403, 500] else row["anomaly_if_model"],
        axis=1
    )

    # Make sure all columns exist
    for col in ["path", "method_code", "endpoint_code", "anomaly_if_model", "anomaly"]:
        if col not in last_row.columns:
            last_row[col] = last_row.get(col, "")

    # Append to anomalies_only.csv if anomaly
    if last_row["anomaly"].iloc[0] == -1:
        if os.path.exists(ANOMALIES_ONLY_FILE):
            df_anom = pd.read_csv(ANOMALIES_ONLY_FILE)
            df_anom = pd.concat([df_anom, last_row], ignore_index=True)
        else:
            df_anom = last_row
        df_anom.to_csv(ANOMALIES_ONLY_FILE, index=False)
