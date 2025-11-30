#data.py
from fastapi import APIRouter
import pandas as pd
import os

router = APIRouter()

ANOMALY_FILE = "logs/anomalies_only.csv"

@router.get("/anomalies")
def get_anomalies():
    if not os.path.exists(ANOMALY_FILE):
        return {"error": "No anomalies found yet. Train the model first."}

    df = pd.read_csv(ANOMALY_FILE)
    return df.to_dict(orient="records")
