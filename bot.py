from instabot import Bot
import os
import base64
import json
import time

# ✅ Environment Variables from Railway
USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")
SESSION_DATA = os.environ.get("SESSION_DATA")

# ✅ Bot Initialization with Fresh Session
bot = Bot(clear_session=True)  # Important for session reset

# ✅ Improved Session Handling
def handle_sessions():
    global bot
    if SESSION_DATA:
        try:
            print("🔁 Decoding Session Data...")
            decoded_data = base64.b64decode(SESSION_DATA).decode()
            session_json = json.loads(decoded_data)
            
            # ✅ Validate Session Structure
            required_keys = ['uuid', 'cookie', 'device_settings']
            if not all(key in session_json for key in required_keys):
                raise ValueError("Invalid session structure")
                
            if 'ds_user' not in session_json['cookie']:
                raise KeyError("ds_user missing in cookie")

            # ✅ Save Session Properly
            session_path = f"config/{USERNAME}_uuid_and_cookie.json"
            os.makedirs("config", exist_ok=True)
            
            with open(session_path, 'w') as f:
                json.dump(session_json, f)
                
            print("💾 Session Restored from ENV")
            
            # ✅ Advanced Login with Session
            if bot.login(username=USERNAME, password=PASSWORD, use_cookie=True):
                print("✅ Login Success with Restored Session!")
                return True
                
        except Exception as e:
            print(f"❌ Session Error: {str(e)}")
    
    # ✅ Fresh Login if Session Fails
    print("🔐 Starting Fresh Login...")
    if bot.login(username=USERNAME, password=PASSWORD):
        new_session = bot.api.get_uuid_and_cookie()  # Get updated session format
        bot.save_session()  # Save properly for next time
        
        # ✅ Encode New Session for Railway
        encoded_session = base64.b64encode(json.dumps(new_session).encode()).decode()
        print(f"🆕 NEW_SESSION_DATA: {encoded_session}")
        return True
        
    return False

# ✅ Execute Session Handling
if not handle_sessions():
    raise Exception("❌ Critical Login Failure")

# ✅ Safe DM Functions (Updated)
def smart_delay(actions_count):
    base_delay = max(30, 10 * actions_count)
    randomized_delay = base_delay + int(time.time() % 30)
    print(f"⏳ Smart Delay: {randomized_delay}s")
    time.sleep(randomized_delay)

def safe_dm(user, message, count):
    try:
        if bot.send_message(message, [user]):
            print(f"✉️ Sent to {user}")
            smart_delay(count)
            return True
    except Exception as e:
        print(f"⚠️ Failed {user}: {str(e)}")
        time.sleep(120)  # Extra cooling period on failure
    return False

# ✅ Targets Configuration
EXCLUDED_USERS = ["SHANSKARI_BALAK 👻💯"]
TARGET_LIST = ["user1", "user2", "user3", "SHANSKARI_BALAK 👻💯"]
MESSAGE_TEXT = "https://ig.me/j/AbadvPz94HkLPUro/"

# ✅ Intelligent Sending Logic
MAX_DAILY = 30
DAILY_COOLDOWN = 86400  # 24 hours in seconds
action_counter = 0

# ✅ Main Execution Loop
for idx, user in enumerate([u for u in TARGET_LIST if u not in EXCLUDED_USERS]):
    if action_counter >= MAX_DAILY:
        print(f"🌙 Daily limit reached. Sleeping {DAILY_COOLDOWN//3600} hours...")
        time.sleep(DAILY_COOLDOWN)
        action_counter = 0
        
    if safe_dm(user, MESSAGE_TEXT, idx+1):
        action_counter += 1
        
print("🎉 Mission Completed!") 
