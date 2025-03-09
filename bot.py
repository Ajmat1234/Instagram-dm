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
            print("✅ Session loaded from environment")
            return True
        except Exception as e:
            print(f"⚠️ Session load failed: {e}")
    return False

def save_session_to_env():
    try:
        session_json = json.dumps(bot.get_settings())
        encoded = base64.b64encode(session_json.encode('utf-8')).decode('utf-8')
        print(f"👉 NEW SESSION DATA:\n{encoded}")
    except Exception as e:
        print(f"❌ Failed to save session: {e}")

# ---- Login Function ----
def login():
    try:
        if load_session_from_env():
            bot.login(USERNAME, PASSWORD)
            print("✅ Logged in via session")
            return True
    except (LoginRequired, ChallengeRequired) as e:
        print(f"⚠️ Session login failed: {e}")
    
    try:
        print("⚠️ Attempting fresh login...")
        bot.login(USERNAME, PASSWORD)
        save_session_to_env()
        print("✅ Fresh login successful")
        return True
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return False

if not login():
    exit("❌ Could not login")

# ---- Group Chat Settings ----
GC_CHECK_INTERVAL = 300
GC_DEAD_TIME = 1200

# ---- Messages ----
FUNNY_REVIVE = [
    "Yeh gc toh kab ka mar gaya tha, koi zinda hai? 💀",
    "Chat khatam, sab so gaye kya? 😴",
    "Aree koi baat karo na... Ghosting mat karo yaar! 👻"
]

WARNINGS = [
    "Mind your language {user}! @king_of_status_4u_ will ban you! ⚠️",
    "Gaali dena band karo {user}! 🚫"
]

WELCOME_MSG = [
    "Welcome {user}! Dil ki gali me aapka swagat hai! 🎉",
    "{user} aa gaya! Ab party shuru karo! 🥳"
]

BAD_WORDS = ['mc', 'bc', 'chutiya', 'gandu', 'bhosdi', 'madarchod']

# ---- Tracking ----
gc_activity = {}
warned_users = set()
joined_users = set()

def process_group_chat(thread):
    thread_id = thread.id
    last_active = gc_activity.get(thread_id, datetime.now() - timedelta(minutes=21))
    
    if (datetime.now() - last_active).total_seconds() > GC_DEAD_TIME:
        msg = random.choice(FUNNY_REVIVE)
        bot.direct_send(msg, thread_ids=[thread_id])
        print(f"💀 Revived {thread.title}")
        gc_activity[thread_id] = datetime.now()
        return
    
    messages = bot.direct_thread_messages(thread_id, amount=20)
    for msg in messages:
        if any(word in msg.text.lower() for word in BAD_WORDS) and msg.user_id != bot.user_id:
            user = f"@{msg.user.username}"
            bot.direct_send(random.choice(WARNINGS).format(user=user), thread_ids=[thread_id])
            warned_users.add(msg.user.pk)
        
        if msg.item_type == 'action' and 'joined' in msg.text:
            if msg.user.pk not in joined_users:
                bot.direct_send(random.choice(WELCOME_MSG).format(user=f"@{msg.user.username}"), thread_ids=[thread_id])
                joined_users.add(msg.user.pk)

def monitor_groups():
    while True:
        try:
            print("\n🔍 Checking group chats...")
            # सभी threads लो और group वाले filter करो
            all_threads = bot.direct_threads()
            group_threads = [t for t in all_threads if t.type == 'group']
            
            for thread in group_threads:
                try:
                    process_group_chat(thread)
                except Exception as e:
                    print(f"❌ Error processing {thread.title}: {e}")
            
            time.sleep(GC_CHECK_INTERVAL)
            
        except Exception as e:
            print(f"❌ Critical error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    print("\n🚀 Bot Started!")
    monitor_groups()
