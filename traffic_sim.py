#tests/traffic_sim.py
import pandas as pd
import random
from datetime import datetime, timedelta

# Endpoints and methods
endpoints = ["/login", "/get-data", "/update-profile", "/delete-account", "/admin"]
methods = ["GET", "POST", "PUT", "DELETE"]

# Labels: 0=normal, 1=malicious
labels = ["normal", "malicious"]

# Number of entries
num_entries = 5000

# Start and end date for timestamps
start_time = datetime(2024, 9, 15)
end_time = datetime.now()
total_seconds = int((end_time - start_time).total_seconds())

# Generate sample requests
data = []

for i in range(num_entries):
    # Random timestamp between start and end
    ts = start_time + timedelta(seconds=random.randint(0, total_seconds))
    
    ep = random.choice(endpoints)
    method = random.choice(methods)
    
    # Random status codes
    if random.random() < 0.85:   # 85% normal traffic
        status = random.choice([200, 201, 204])
        label = "normal"
    else:                        # 15% malicious
        status = random.choice([401, 403, 404, 500])
        label = "malicious"
    
    data.append([ts, ep, method, status, label])

# Save to CSV
df = pd.DataFrame(data, columns=["timestamp", "endpoint", "method", "status_code", "label"])

# Ensure logs folder exists
import os
os.makedirs("logs", exist_ok=True)

df.to_csv("logs/requests.csv", index=False)
print(f"Generated {num_entries} traffic entries in logs/requests.csv")
