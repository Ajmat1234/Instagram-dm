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
GC_CHECK_INTERVAL = 300  # 5 minutes
GC_DEAD_TIME = 1200     # 20 minutes

# ---- Enhanced Messages ----
FUNNY_REVIVE = [
    "Ye group toh kab ka सोया पड़ा है! कोई जिंदा दिखाई नहीं दे रहा 😴",
    "अरे यार! बात करो ना... गूगल मैप्स बन गए क्या ये चैट? 🗺️",
    "Admin जी! ये ग्रुप अब म्यूजियम में डिस्प्ले के लिए तैयार है 🏛️",
    "चुप्पी का सुनामी आ गया क्या? 🌊"
]

WARNINGS = [
    "{user} भाई! भाषा संभाल के... वार्निंग दे रहा हूं! ⚠️",
    "ऐसे शब्द नहीं चलेंगे {user}! @king_of_status_4u_ को शिकायत कर दूंगा! 🚫",
    "ये कैसी बोली {user}? थोड़ा संयम रखो यार! 😠"
]

WELCOME_MSG = [
    "नमस्ते {user}! हमारे मस्ती भरे ग्रुप में आपका स्वागत है! 🎉",
    "ओए {user}! मेम्स लेकर आए हो ना? 😂",
    "{user} आ गया रे! अब पार्टी शुरू! 🕺💃",
    "हैलो {user}! ग्रुप रूल्स पढ़ लेना, वरना... 😉"
]

BAD_WORDS = ['mc', 'bc', 'chutiya', 'gandu', 'bhosdi', 'madarchod', 'lavde', 'randi']

# ---- Tracking ----
gc_activity = {}
warned_users = set()
joined_users = set()

def process_group_chat(thread):
    try:
        thread_id = thread.id
        last_active = gc_activity.get(thread_id, datetime.now() - timedelta(minutes=21))
        
        # Check inactivity
        if (datetime.now() - last_active).total_seconds() > GC_DEAD_TIME:
            msg = random.choice(FUNNY_REVIVE)
            bot.direct_send(msg, thread_ids=[thread_id])
            print(f"💀 Revived: {thread.title}")
            gc_activity[thread_id] = datetime.now()
            return
        
        # Process messages
        messages = bot.direct_thread_messages(thread_id, amount=25)
        for msg in messages:
            # Check bad words
            if msg.text and any(word in msg.text.lower() for word in BAD_WORDS):
                if msg.user_id != bot.user_id and msg.user.pk not in warned_users:
                    user = f"@{msg.user.username}"
                    bot.direct_send(random.choice(WARNINGS).format(user=user), thread_ids=[thread_id])
                    warned_users.add(msg.user.pk)
                    print(f"⚠️ Warned {user}")
            
            # Check new members
            if msg.item_type == 'action' and 'added' in msg.text:
                new_user = next((u for u in msg.users if u.pk not in joined_users), None)
                if new_user:
                    bot.direct_send(random.choice(WELCOME_MSG).format(user=f"@{new_user.username}"), thread_ids=[thread_id])
                    joined_users.add(new_user.pk)
                    print(f"🎉 Welcomed @{new_user.username}")
    
    except Exception as e:
        print(f"❌ Error in {thread.title}: {str(e)[:50]}")

def monitor_groups():
    while True:
        try:
            print("\n🔍 Scanning all group chats...")
            all_threads = bot.direct_threads()
            group_threads = [t for t in all_threads if t.is_group]
            
            for thread in group_threads:
                process_group_chat(thread)
            
            time.sleep(GC_CHECK_INTERVAL)
            
        except Exception as e:
            print(f"❌ Critical error: {str(e)[:100]}")
            time.sleep(60)

if __name__ == "__main__":
    print("\n🚀 Instagram Group Manager Started!")
    monitor_groups()
