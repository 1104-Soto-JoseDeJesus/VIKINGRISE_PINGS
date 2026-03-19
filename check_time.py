import os
import time
import requests
from datetime import datetime, timedelta

# Configuration
INTERVAL_HOURS = 52
STATE_FILE = "last_ping.txt"
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
ROLE_ID = os.getenv("ROLE_ID")

def should_ping():
    if not os.path.exists(STATE_FILE):
        return True
    
    with open(STATE_FILE, "r") as f:
        last_run_ts = float(f.read().strip())
    
    last_run_dt = datetime.fromtimestamp(last_run_ts)
    return datetime.now() >= last_run_dt + timedelta(hours=INTERVAL_HOURS)

if should_ping():
    # Send Discord Ping
    payload = {"content": f"<@&{ROLE_ID}> The event is starting!"}
    requests.post(WEBHOOK_URL, json=payload)
    
    # Update timestamp
    with open(STATE_FILE, "w") as f:
        f.write(str(time.time()))
    print("Ping sent and timestamp updated.")
else:
    print("Not time yet.")
