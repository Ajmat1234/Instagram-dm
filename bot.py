from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired
from instagrapi.types import DirectMessage
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

def process_group_chat(thread):
    now = datetime.now(IST)

    try:
        # Get last 20 messages for better tracking
        messages = bot.direct_messages(thread_id=thread.id, amount=20)
        
        # Find last non-action message
        last_msg_time = now
        for msg in messages:
            if msg.type != 'action':
                last_msg_time = msg.timestamp.astimezone(IST)
                break

        # Revival logic for inactive groups
        if (now - last_msg_time).total_seconds() > GC_DEAD_TIME:
            if thread.id not in last_revive_time or (now - last_revive_time[thread.id]).total_seconds() > REVIVE_COOLDOWN:
                msg = random.choice(FUNNY_REVIVE)
                bot.direct_send(msg, thread_ids=[thread.id])
                last_revive_time[thread.id] = now
                print(f"💀 Revived group {thread.id}")

        # Process messages
        for msg in messages:
            # Skip action messages for content checks
            if msg.type == 'action':
                continue

            # Bad words check
            if msg.text and any(word in msg.text.lower() for word in BAD_WORDS):
                if msg.user_id != bot.user_id and msg.user.pk not in warned_users:
                    user = f"@{msg.user.username}"
                    bot.direct_send(random.choice(WARNINGS).format(user=user), thread_ids=[thread.id])
                    warned_users.add(msg.user.pk)
                    print(f"⚠️ Warned {user} in group {thread.id}")

    except Exception as e:
        print(f"❌ Error processing group {thread.id}: {e}")

def process_join_events(thread):
    try:
        messages = bot.direct_messages(thread_id=thread.id, amount=20)
        for msg in messages:
            # Check for user added events
            if msg.type == 'action' and 'added' in msg.text.lower():
                # Extract added users
                new_users = [u for u in msg.users if u.pk not in joined_users]
                for user in new_users:
                    bot.direct_send(
                        random.choice(WELCOME_MSG).format(user=f"@{user.username}"),
                        thread_ids=[thread.id]
                    )
                    joined_users.add(user.pk)
                    print(f"🎉 Welcomed @{user.username} in {thread.id}")

    except Exception as e:
        print(f"❌ Join event error in {thread.id}: {e}")

def monitor_groups():
    while True:
        try:
            print("\n🔍 Checking group chats...")
            threads = bot.direct_threads(thread_type="private")  # Get group chats
            for thread in threads:
                if thread.is_group:  # Process only group chats
                    process_join_events(thread)
                    process_group_chat(thread)
            time.sleep(GC_CHECK_INTERVAL)
        except Exception as e:
            print(f"❌ Main error: {str(e)[:100]}")
            time.sleep(60)

if __name__ == "__main__":
    print("\n🚀 Group Chat Bot Started!")
    monitor_groups()
