import os
import time
import requests
from datetime import datetime, timedelta

# Configuration
INTERVAL_HOURS = 52
WARNING_LEAD_MINUTES = 10
STATE_FILE = "last_ping.txt"
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
ROLE_ID = os.getenv("ROLE_ID")

def get_state():
    if not os.path.exists(STATE_FILE):
        return {"warning": 0, "main": 0}
    with open(STATE_FILE, "r") as f:
        lines = f.read().splitlines()
        if len(lines) < 2:
            return {"warning": 0, "main": 0}
        return {"warning": float(lines[0]), "main": float(lines[1])}

def save_state(warning_ts, main_ts):
    with open(STATE_FILE, "w") as f:
        f.writelines([f"{warning_ts}\n", f"{main_ts}\n"])

def send_ping(content, title, color):
    payload = {
        "username": "Event Tracker",
        "content": f"<@&{ROLE_ID}>",
        "embeds": [{
            "title": title,
            "description": content,
            "color": color,
            "timestamp": datetime.utcnow().isoformat()
        }],
        "allowed_mentions": {"roles": [ROLE_ID]}
    }
    requests.post(WEBHOOK_URL, json=payload)

if __name__ == "__main__":
    state = get_state()
    now = datetime.now()
    
    # Calculate when the NEXT main event should be
    last_main_dt = datetime.fromtimestamp(state['main'])
    next_main_dt = last_main_dt + timedelta(hours=INTERVAL_HOURS)
    
    # Calculate when the Warning should happen (10 mins before Main)
    next_warning_dt = next_main_dt - timedelta(minutes=WARNING_LEAD_MINUTES)

    # 1. Check for Warning Ping
    if now >= next_warning_dt and state['warning'] <= state['main']:
        send_ping("⚠️ **10 MINUTE WARNING:** The event starts shortly!", "Upcoming Event", 16776960) # Yellow
        save_state(now.timestamp(), state['main'])
        print("Warning ping sent.")

    # 2. Check for Main Ping
    elif now >= next_main_dt:
        send_ping("⚔️ **EVENT STARTING NOW:** Good luck!", "Event Active", 15158332) # Red
        save_state(state['warning'], now.timestamp())
        print("Main ping sent.")
    
    else:
        print(f"Waiting... Next Warning at {next_warning_dt}")
