from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse
import pandas as pd
import os

router = APIRouter()
ANOMALY_FILE = "logs/anomalies_only.csv"

def load_anomalies():
    try:
        df = pd.read_csv(ANOMALY_FILE)
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
    except FileNotFoundError:
        df = pd.DataFrame()
    return df

HTML_TEMPLATE = """ 
<html>
<head><title>Anomalies Dashboard</title></head>
<body>
<h2>Anomalies Dashboard</h2>
<form method="get">
Endpoint: <input type="text" name="endpoint" value="{endpoint}">
Method: <input type="text" name="method" value="{method}">
Status Code: <input type="text" name="status_code" value="{status_code}">
Date From: <input type="date" name="date_from" value="{date_from}">
Date To: <input type="date" name="date_to" value="{date_to}">
<input type="submit" value="Filter">
<button type="submit" name="clear" value="true">Clear Filter</button>
</form>
<br>
<table border="1">
<tr>
<th>S.no</th>
{headers}
</tr>
{rows}
</table>
</body>
</html>
"""

@router.get("/", response_class=HTMLResponse)
async def anomalies(
    endpoint: str = Query(default=""),
    method: str = Query(default=""),
    status_code: int | None = Query(default=None),
    date_from: str = Query(default=""),
    date_to: str = Query(default=""),
    clear: str = Query(default=None)
):
    df = load_anomalies()

    if clear == "true":
        endpoint = method = date_from = date_to = ""
        status_code = None

    if not df.empty:
        if endpoint:
            df = df[df["endpoint"].str.contains(endpoint)]
        if method:
            df = df[df["method"].str.contains(method)]
        if status_code is not None:
            df = df[df["status_code"] == status_code]
        if date_from:
            df = df[df["timestamp"] >= pd.to_datetime(date_from)]
        if date_to:
            df = df[df["timestamp"] <= pd.to_datetime(date_to)]

    df = df.sort_values(by="timestamp", ascending=False)

    headers_html = "".join([f"<th>{col.title().replace('_','')}</th>" for col in df.columns])
    rows_html = ""
    for i, (_, row) in enumerate(df.iterrows(), start=1):
        rows_html += "<tr>" + f"<td>{i}</td>" + "".join([f"<td>{row[col]}</td>" for col in df.columns]) + "</tr>"

    return HTML_TEMPLATE.format(
        endpoint=endpoint,
        method=method,
        status_code=status_code or "",
        date_from=date_from,
        date_to=date_to,
        headers=headers_html,
        rows=rows_html
    )
