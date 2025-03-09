from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired
import time
import random
import os
import base64
import json
from datetime import datetime, timedelta

# ---- Instagram Credentials ----
USERNAME = "kalllu_kaliiyaaa"
PASSWORD = "Ajmat1234@@@"
SESSION_ENV_VAR = "INSTA_SESSION_DATA"
TARGET_GROUP_LINK = "https://ig.me/j/AbadvPz94HkLPUro/"  # Your group link

# ---- Initialize Client ----
bot = Client()
bot.delay_range = [2, 5]

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
        if load_session_from_env() and bot.login(USERNAME, PASSWORD):
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

WELCOME_MSG = [
    "नमस्ते {user}! स्वागत है! 🎉",
    "{user} आया ओए! पार्टी शुरू! 🥳"
]

BAD_WORDS = ['mc', 'bc', 'chutiya', 'gandu', 'bhosdi', 'madarchod']

# ---- Tracking ----
last_revive_time = {}
warned_users = set()
joined_users = set()

def get_target_group():
    try:
        # Extract thread ID from group link
        thread_id = TARGET_GROUP_LINK.split('/j/')[-1].strip('/')
        return bot.direct_thread(thread_id)
    except Exception as e:
        print(f"❌ Group error: {e}")
        return None

def process_group(thread):
    now = datetime.now()
    thread_id = thread.id
    
    # Check last message time
    messages = bot.direct_thread_messages(thread_id, amount=1)
    last_msg_time = messages[0].timestamp if messages else now - timedelta(minutes=21)
    
    # Revival logic
    if (now - last_msg_time).total_seconds() > GC_DEAD_TIME:
        if thread_id not in last_revive_time or (now - last_revive_time[thread_id]).total_seconds() > REVIVE_COOLDOWN:
            msg = random.choice(FUNNY_REVIVE)
            bot.direct_send(msg, thread_ids=[thread_id])
            last_revive_time[thread_id] = now
            print(f"💀 Revived group")
    
    # Message processing
    messages = bot.direct_thread_messages(thread_id, amount=20)
    for msg in messages:
        # Bad words check
        if msg.text and any(word in msg.text.lower() for word in BAD_WORDS):
            if msg.user_id != bot.user_id and msg.user.pk not in warned_users:
                user = f"@{msg.user.username}"
                bot.direct_send(random.choice(WARNINGS).format(user=user), thread_ids=[thread_id])
                warned_users.add(msg.user.pk)
                print(f"⚠️ Warned {user}")
        
        # New member check
        if msg.item_type == 'action' and 'added' in msg.text:
            new_user = next((u for u in msg.users if u.pk not in joined_users), None)
            if new_user:
                bot.direct_send(random.choice(WELCOME_MSG).format(user=f"@{new_user.username}"), thread_ids=[thread_id])
                joined_users.add(new_user.pk)
                print(f"🎉 Welcomed @{new_user.username}")

def monitor_group():
    while True:
        try:
            print("\n🔍 Checking group...")
            group = get_target_group()
            if group:
                process_group(group)
            time.sleep(GC_CHECK_INTERVAL)
        except Exception as e:
            print(f"❌ Error: {str(e)[:100]}")
            time.sleep(60)

if __name__ == "__main__":
    print("\n🚀 Bot Started!")
    monitor_group()
