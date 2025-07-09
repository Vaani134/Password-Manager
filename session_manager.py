import time
import os
import json

SESSION_FILE = "session.json"
SESSION_TIMEOUT = 600  # 10 minutes = 600 seconds

def start_session(username: str):
    session_data = {
        "username": username,
        "last_activity": time.time()
    }

    with open(SESSION_FILE, "w") as f:
        json.dump(session_data, f)

    print(f"✅ Session started for {username}")

def is_session_active() -> bool:
    if not os.path.exists(SESSION_FILE):
        return False

    with open(SESSION_FILE, "r") as f:
        session_data = json.load(f)

    last_activity = session_data.get("last_activity", 0)
    if time.time() - last_activity > SESSION_TIMEOUT:
        print("⏳ Session expired.")
        end_session()
        return False

    return True

def update_activity():
    if not os.path.exists(SESSION_FILE):
        return

    with open(SESSION_FILE, "r") as f:
        session_data = json.load(f)

    session_data["last_activity"] = time.time()

    with open(SESSION_FILE, "w") as f:
        json.dump(session_data, f)

def end_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
        print("🚪 Session ended.")