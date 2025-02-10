import base64
import json
import os
from instagrapi import Client

# Environment variable se session load karein
SESSION_JSON = os.environ.get('SESSION_JSON')  # Ensure this is set in your environment

# 🔑 Instagram Login Credentials (use encoded session)
def login():
    cl = Client()

    if SESSION_JSON:
        try:
            # Decode Base64 session if available
            decoded_session = base64.b64decode(SESSION_JSON).decode('utf-8')
            session_data = json.loads(decoded_session)
            cl.set_settings(session_data)
            print("🔑 Session loaded successfully.")
            return cl  # Session load successful, no need for login

        except Exception as e:
            print(f"⚠️ Error loading session: {e}")
            print("🔑 Session expired or invalid, logging in again...")

    # Agar session nahi hai, toh login karenge
    USERNAME = "zehra.bloom_"  # Replace with your username
    PASSWORD = "Ajmat1234@"    # Replace with your password
    cl.login(USERNAME, PASSWORD)
    cl.dump_settings("session.json")  # Save session for later use
    print(f"🔑 Logged in as {USERNAME}")
    return cl

# Main Bot Function
def bot():
    cl = login()

    while True:
        target_users = get_target_users(cl)
        success_count = 0

        for user in target_users:
            if success_count >= DM_LIMIT:
                print(f"⚠️ DM limit {DM_LIMIT} reached, resting for {REST_TIME} seconds...")
                time.sleep(REST_TIME)
                success_count = 0  # Reset count after rest

            if send_dm(cl, user):
                success_count += 1

            time.sleep(SEND_DM_INTERVAL)  # Ek minute ka gap between DMs

        print(f"🔄 Next cycle start hoga 3 ghante ke baad...")
        time.sleep(REST_TIME)

if __name__ == "__main__":
    bot()
