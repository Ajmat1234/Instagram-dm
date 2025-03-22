from instabot import Bot
import os
import base64
import json
import time
import shutil

# ✅ Environment Variables
USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")
SESSION_DATA = os.environ.get("SESSION_DATA")

# ✅ Session Cleanup (New Fix)
if os.path.exists("config"):
    shutil.rmtree("config")
    print("🧹 Old session files cleaned!")

# ✅ Bot Initialization (Corrected)
bot = Bot()  # Removed clear_session parameter

# ✅ Improved Session Handler
def handle_sessions():
    if SESSION_DATA:
        try:
            print("🔁 Decoding Session...")
            decoded = json.loads(base64.b64decode(SESSION_DATA))
            
            # Validate session structure
            if 'cookie' not in decoded or 'ds_user' not in decoded['cookie']:
                raise ValueError("Invalid session format")
                
            # Save session file
            os.makedirs("config", exist_ok=True)
            session_file = f"config/{USERNAME}_uuid_and_cookie.json"
            
            with open(session_file, 'w') as f:
                json.dump(decoded, f)
                
            # Login with session
            if bot.login(username=USERNAME, password=PASSWORD, use_cookie=True):
                print("✅ Session login successful!")
                return True
                
        except Exception as e:
            print(f"❌ Session error: {str(e)}")
            return False
            
    # Fresh login if no session
    print("🔐 Starting fresh login...")
    if bot.login(username=USERNAME, password=PASSWORD):
        new_session = bot.api.get_uuid_and_cookie()
        encoded = base64.b64encode(json.dumps(new_session).encode()).decode()
        print(f"🆕 NEW_SESSION_DATA: {encoded}")
        return True
        
    return False

# ✅ Main Execution
if not handle_sessions():
    raise SystemExit("❌ Login failed, stopping script")

# ✅ DM Configuration
EXCLUDED = ["SHANSKARI_BALAK 👻💯"]
TARGETS = [u for u in ["user1", "user2", "user3", "SHANSKARI_BALAK 👻💯"] if u not in EXCLUDED]
MESSAGE = "https://ig.me/j/AbadvPz94HkLPUro/"

# ✅ Smart Sending Logic
MAX_DMS = 30
SENT = 0

for i, user in enumerate(TARGETS):
    try:
        if SENT >= MAX_DMS:
            print("💤 Daily limit reached, sleeping 24h...")
            time.sleep(86400)
            SENT = 0
            
        bot.send_message(MESSAGE, [user])
        print(f"✉️ Sent to {user} ({i+1}/{len(TARGETS)})")
        SENT += 1
        time.sleep(30 + (i * 2))  # Progressive delay
        
    except Exception as e:
        print(f"⚠️ Error with {user}: {str(e)}")
        time.sleep(120)
        
print("🎉 All messages processed!")
