from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired
import time
import random
import os
import base64
import json
from datetime import datetime, timedelta

# ---- Instagram Credentials ----
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
SESSION_ENV_VAR = "INSTA_SESSION_DATA"
TARGET_GROUP_LINK = "https://ig.me/j/AbadvPz94HkLPUro/"  # Instagram Group Link

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
            print("✅ Session loaded successfully!")
            return True
        except Exception as e:
            print(f"⚠️ Session loading error: {e}")
    return False

def save_session_to_env():
    try:
        session_json = json.dumps(bot.get_settings())
        encoded = base64.b64encode(session_json.encode('utf-8')).decode('utf-8')
        print(f"👉 NEW SESSION DATA:\n{encoded}")
    except Exception as e:
        print(f"❌ Session save failed: {e}")

# ---- Login Function ----
def login():
    try:
        if load_session_from_env() and bot.login(USERNAME, PASSWORD):
            print("✅ Logged in using session!")
            return True
    except (LoginRequired, ChallengeRequired) as e:
        print(f"⚠️ Login issue: {e}")

    try:
        print("⚠️ Trying manual login...")
        bot.login(USERNAME, PASSWORD)
        save_session_to_env()
        return True
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return False

if not login():
    exit("❌ Login error, exiting...")

# ---- Group Monitoring Settings ----
GC_CHECK_INTERVAL = 180  # Check every 3 minutes
GC_DEAD_TIME = 1200      # If inactive for 20 minutes, send revive message
REVIVE_COOLDOWN = 1800   # 30 minutes cooldown before reviving again

# ---- Messages ----
FUNNY_REVIVE = [
    "Group तो मर गया... कोई ज़िंदा है? 💀",
    "इतनी शांति क्यों? कोई बोलो! 😱",
    "Hello hello... कोई है? 👀"
]

WARNINGS = [
    "{user} भाई! भाषा संभालो! ⚠️",
    "{user}, अपशब्द मत बोलो, नहीं तो हटाया जा सकता है! 🚫"
]

WELCOME_MSG = [
    "नमस्ते {user}! स्वागत है! 🎉",
    "{user} आया ओए! अब मज़ा आएगा! 🥳"
]

BAD_WORDS = ['mc', 'bc', 'chutiya', 'gandu', 'bhosdi', 'madarchod']

# ---- Tracking Variables ----
last_revive_time = {}
warned_users = set()
joined_users = set()

# ---- Get Target Group Thread ID ----
def get_target_group():
    try:
        thread_id = bot.direct_thread_id_from_link(TARGET_GROUP_LINK)
        return bot.direct_thread(thread_id)
    except Exception as e:
        print(f"❌ Error fetching group: {e}")
        return None

# ---- Process Group Messages ----
def process_group(thread):
    now = datetime.now()
    thread_id = thread.id

    try:
        messages = bot.direct_messages(thread_id, amount=5)  # Fetch last 5 messages
        last_msg_time = messages[0].timestamp if messages else now - timedelta(minutes=21)

        # Check if group is inactive and needs revival
        if (now - last_msg_time).total_seconds() > GC_DEAD_TIME:
            if thread_id not in last_revive_time or (now - last_revive_time[thread_id]).total_seconds() > REVIVE_COOLDOWN:
                msg = random.choice(FUNNY_REVIVE)
                bot.direct_send(msg, thread_ids=[thread_id])
                last_revive_time[thread_id] = now
                print(f"💀 Group revived with message: {msg}")

        # Process each message
        for msg in messages:
            # Check for bad words
            if msg.text and any(word in msg.text.lower() for word in BAD_WORDS):
                if msg.user_id != bot.user_id and msg.user.pk not in warned_users:
                    user = f"@{msg.user.username}"
                    bot.direct_send(random.choice(WARNINGS).format(user=user), thread_ids=[thread_id])
                    warned_users.add(msg.user.pk)
                    print(f"⚠️ Warned {user}")

            # Welcome new members
            if msg.item_type == 'action' and 'added' in msg.text:
                new_user = next((u for u in msg.users if u.pk not in joined_users), None)
                if new_user:
                    bot.direct_send(random.choice(WELCOME_MSG).format(user=f"@{new_user.username}"), thread_ids=[thread_id])
                    joined_users.add(new_user.pk)
                    print(f"🎉 Welcomed @{new_user.username}")

    except Exception as e:
        print(f"⚠️ Error processing group: {e}")

# ---- Main Loop to Monitor Group ----
def monitor_group():
    while True:
        try:
            print("\n🔍 Checking group activity...")
            group = get_target_group()
            if group:
                process_group(group)
            time.sleep(GC_CHECK_INTERVAL)
        except Exception as e:
            print(f"❌ Error in main loop: {str(e)[:100]}")
            time.sleep(60)

if __name__ == "__main__":
    print("\n🚀 Bot Started!")
    monitor_group()
