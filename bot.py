from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired
import time
import random
import os
import base64
import json
from datetime import datetime, timedelta
import pytz

# ---- Instagram Credentials ----
USERNAME = "kalllu_kaliiyaaa"
PASSWORD = "Ajmat1234@@@"
SESSION_ENV_VAR = "INSTA_SESSION_DATA"

# ---- Initialize Client ----
bot = Client()
bot.delay_range = [2, 5]

# ---- Set Indian Timezone ----
IST = pytz.timezone("Asia/Kolkata")

# ---- Session Management ----
def load_session_from_env():
    session_data = os.getenv(SESSION_ENV_VAR)
    if session_data:
        try:
            decoded_bytes = base64.b64decode(session_data.encode('utf-8'))
            decoded_str = decoded_bytes.decode('utf-8')
            bot.set_settings(json.loads(decoded_str))
            print("✅ Session loaded")
            return True
        except Exception as e:
            print(f"⚠️ Session error: {e}")
    return False

def save_session_to_env():
    try:
        session_json = json.dumps(bot.get_settings())
        encoded = base64.b64encode(session_json.encode('utf-8')).decode('utf-8')
        print(f"👉 NEW SESSION:\n{encoded}")
    except Exception as e:
        print(f"❌ Save failed: {e}")

# ---- Login ----
def login():
    try:
        if load_session_from_env():
            bot.login(USERNAME, PASSWORD)
            print("✅ Logged in")
            return True
    except (LoginRequired, ChallengeRequired) as e:
        print(f"⚠️ Login issue: {e}")
    
    try:
        print("⚠️ New login...")
        bot.login(USERNAME, PASSWORD)
        save_session_to_env()
        return True
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return False

if not login():
    exit("❌ Login error")

# ---- Group Settings ----
GC_CHECK_INTERVAL = 300  # 5 minutes
GC_DEAD_TIME = 1200      # 20 minutes
REVIVE_COOLDOWN = 1200   # 20 minutes cooldown
TRACKING_FILE = "user_track.json"

# ---- Messages ----
FUNNY_REVIVE = [
    "Group तो मर गया... कोई ज़िंदा है? 💀",
    "चुप्पी का सुनामी आ गया क्या? 🌊",
    "अरे यार! बात करो ना... 👻"
]

WARNINGS = [
    "{user} भाई! भाषा संभालो! ⚠️",
    "ऐसे शब्द नहीं चलेंगे {user}! 🚫"
]

WELCOME_MSGS = [
    "नमस्ते {user}! स्वागत है! 🎉",
    "{user} आया ओए! पार्टी शुरू! 🥳",
    "😍 {user}, TUSSI AA GYE HO TO MUJHE CHHOD KR N JAANA! 🥺"
]

BAD_WORDS = ['mc', 'bc', 'chutiya', 'gandu', 'bhosdi', 'madarchod']

# ---- Tracking ----
last_revive_time = {}
warned_users = set()

def load_users():
    try:
        with open(TRACKING_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_user(user_id):
    users = load_users()
    users[user_id] = datetime.now(IST).isoformat()
    with open(TRACKING_FILE, "w") as f:
        json.dump(users, f)

def should_welcome(user_id):
    users = load_users()
    if user_id not in users:
        return True
    last_mentioned = datetime.fromisoformat(users[user_id]).astimezone(IST)
    return datetime.now(IST) - last_mentioned > timedelta(hours=12)

# ---- Main Logic ----
def process_group(thread):
    now = datetime.now(IST)
    
    try:
        messages = bot.direct_messages(thread_id=thread.id, amount=10)
        
        # Revival logic
        last_msg_time = now
        if messages:
            for msg in messages:
                if msg.item_type != 'action':  # Changed here
                    last_msg_time = msg.timestamp.astimezone(IST)
                    break

        if (now - last_msg_time).total_seconds() > GC_DEAD_TIME:
            if thread.id not in last_revive_time or (now - last_revive_time[thread.id]).total_seconds() > REVIVE_COOLDOWN:
                bot.direct_send(random.choice(FUNNY_REVIVE), thread_ids=[thread.id])
                last_revive_time[thread.id] = now
                print(f"💀 Revived {thread.id}")

        # Process messages
        for msg in messages:
            # New member check
            if msg.item_type == 'action' and 'added' in msg.text.lower():  # Changed here
                for user in msg.users:
                    if should_welcome(str(user.pk)):
                        bot.direct_send(
                            random.choice(WELCOME_MSGS).format(user=f"@{user.username}"),
                            thread_ids=[thread.id]
                        )
                        save_user(str(user.pk))
                        print(f"🎉 Welcomed @{user.username}")

            # Bad word check
            elif msg.item_type == 'text':  # Changed here
                text = msg.text.lower()
                if any(word in text for word in BAD_WORDS):
                    if msg.user_id != bot.user_id and msg.user.pk not in warned_users:
                        user = f"@{msg.user.username}"
                        bot.direct_send(random.choice(WARNINGS).format(user=user), thread_ids=[thread.id])
                        warned_users.add(msg.user.pk)
                        print(f"⚠️ Warned {user}")

    except Exception as e:
        print(f"❌ Error in {thread.id}: {str(e)[:100]}")

def monitor_groups():
    while True:
        try:
            print("\n🔍 Checking groups...")
            threads = bot.direct_threads(amount=20)
            for thread in threads:
                if thread.is_group:
                    process_group(thread)
            time.sleep(GC_CHECK_INTERVAL)
        except Exception as e:
            print(f"❌ Main error: {str(e)[:100]}")
            time.sleep(60)

if __name__ == "__main__":
    print("\n🚀 Group Manager Started!")
    monitor_groups()
