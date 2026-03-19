import os
import time
import requests
from datetime import datetime, timedelta

# Configuration
INTERVAL_HOURS = 0
STATE_FILE = "last_ping.txt"
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
ROLE_ID = os.getenv("ROLE_ID")

def should_ping():
    # If the file doesn't exist, it's the first run, so we SHOULD ping.
    if not os.path.exists(STATE_FILE):
        print("No state file found. Starting fresh.")
        return True
    
    with open(STATE_FILE, "r") as f:
        content = f.read().strip()
        if not content:
            return True
        last_run_ts = float(content)
    
    last_run_dt = datetime.fromtimestamp(last_run_ts)
    next_run_dt = last_run_dt + timedelta(hours=INTERVAL_HOURS)
    
    print(f"Last ping was at: {last_run_dt}")
    print(f"Next ping scheduled for: {next_run_dt}")
    
    return datetime.now() >= next_run_dt

if __name__ == "__main__":
    if not WEBHOOK_URL or not ROLE_ID:
        print("ERROR: Missing DISCORD_WEBHOOK or ROLE_ID in Secrets!")
        exit(1)

    if should_ping():
        # Discord Payload
        payload = {
            "content": f"<@&{ROLE_ID}> The event is starting!",
            "allowed_mentions": {"roles": [ROLE_ID]} # Critical for the @role to work
        }
        
        response = requests.post(WEBHOOK_URL, json=payload)
        
        if response.status_code == 204:
            with open(STATE_FILE, "w") as f:
                f.write(str(time.time()))
            print("Ping sent successfully.")
        else:
            print(f"Failed to send ping. Discord returned: {response.status_code}")
            exit(1)
    else:
        print("Not time to ping yet. Skipping.")
