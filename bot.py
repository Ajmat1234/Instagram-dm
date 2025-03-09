from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired
import time
import random
import os
import base64
from datetime import datetime, timedelta

# ---- Instagram Credentials ----
USERNAME = "kalllu_kaliiyaaa"
PASSWORD = "Ajmat1234@@@"
SESSION_ENV_VAR = "INSTA_SESSION_DATA"  # Railway environment variable name

# ---- Initialize Client ----
bot = Client()
bot.delay_range = [2, 5]  # More natural delays

# ---- Session Management ----
def load_session_from_env():
    session_data = os.getenv(SESSION_ENV_VAR)
    if session_data:
        try:
            decoded = base64.b64decode(session_data)
            bot.set_settings(decoded)
            print("✅ Session loaded from environment")
            return True
        except Exception as e:
            print(f"⚠️ Session load failed: {e}")
    return False

def save_session_to_env():
    session_data = bot.get_settings()
    encoded = base64.b64encode(session_data).decode()
    # In Railway, you'd set this as environment variable
    print(f"👉 NEW SESSION DATA:\n{encoded}")

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

# ---- Group Chat Monitoring ----
GC_CHECK_INTERVAL = 300  # 5 minutes
GC_DEAD_TIME = 1200  # 20 minutes in seconds

# ---- Message Templates ----
FUNNY_REVIVE = [
    "Yeh gc toh kab ka mar gaya tha, koi zinda hai? 💀",
    "Chatti khatam, sab so gaye kya? 😴",
    "Aree koi baat karo na... Ghosting mat karo yaar! 👻",
    "Admin ji, yeh group toh museum ban gaya hai 🏛️"
]

WARNINGS = [
    "Mind your language {user}! Next time @king_of_status_4u_ will ban you! ⚠️",
    "Gaali dena band karo {user}, warna complaint kar denge @king_of_status_4u_ ko! 🚫"
]

WELCOME_MSG = [
    "Welcome {user}! Dil ki gali me aapka swagat hai! 🎉",
    "Aaye ho toh memes leke aaye ho {user}? 😂",
    "{user} aa gaya! Ab party shuru karo! 🥳"
]

BAD_WORDS = ['mc', 'bc', 'chutiya', 'gandu', 'bhosdi', 'madarchod', 'lavde', 'randi', 'kutta']

# ---- Tracking Variables ----
gc_activity = {}  # {thread_id: last_active}
warned_users = set()  # Track warned users
joined_users = set()  # Track new members

def get_greeting():
    now = datetime.now().hour
    if 5 <= now < 12:
        return "Good Morning! ☀️ Chai peelo guys!"
    elif 12 <= now < 17:
        return "Good Afternoon! 🕶️ Lunch ho gaya?"
    elif 17 <= now < 21:
        return "Good Evening! 🌆 Time for masti!"
    else:
        if now >= 22 or now < 5:
            return "🌙 Raat ho gayi, so jaao warna mommy daant dengi!"
        return "Good Night! 😴 Sweet Dreams!"

def process_group_chat(thread):
    thread_id = thread.id
    last_activity = gc_activity.get(thread_id, datetime.now() - timedelta(minutes=21))
    
    # Check for inactivity
    if (datetime.now() - last_activity).total_seconds() > GC_DEAD_TIME:
        msg = random.choice(FUNNY_REVIVE)
        bot.direct_send(msg, thread_ids=[thread_id])
        print(f"💀 Revived {thread.title}")
        gc_activity[thread_id] = datetime.now()
        return
    
    # Check messages
    messages = bot.direct_thread_messages(thread_id, amount=20)
    for msg in messages:
        # Check bad words
        if any(word in msg.text.lower() for word in BAD_WORDS) and msg.user_id != bot.user_id:
            user = f"@{msg.user.username}"
            warning = random.choice(WARNINGS).format(user=user)
            bot.direct_send(warning, thread_ids=[thread_id])
            print(f"⚠️ Warned {user} in {thread.title}")
            warned_users.add(msg.user.pk)
        
        # Check new members
        if msg.item_type == 'action' and 'joined' in msg.text:
            if msg.user.pk not in joined_users:
                welcome = random.choice(WELCOME_MSG).format(user=f"@{msg.user.username}")
                bot.direct_send(welcome, thread_ids=[thread_id])
                joined_users.add(msg.user.pk)
                print(f"🎉 Welcomed {msg.user.username}")
    
    # Send time-based messages
    greeting = get_greeting()
    if datetime.now().minute % 30 == 0:  # Every 30 minutes
        bot.direct_send(greeting, thread_ids=[thread_id])
        print(f"🕒 Sent greeting to {thread.title}")

def monitor_groups():
    while True:
        try:
            print("\n🔍 Checking group chats...")
            threads = bot.direct_threads(selected_filter="group")
            
            for thread in threads:
                try:
                    process_group_chat(thread)
                except Exception as e:
                    print(f"❌ Error processing {thread.title}: {e}")
            
            time.sleep(GC_CHECK_INTERVAL)
            
        except Exception as e:
            print(f"❌ Critical error: {e}")
            time.sleep(60)

# ---- Main Execution ----
if __name__ == "__main__":
    print("\n🚀 Starting Group Chat Monitor Bot...")
    monitor_groups()
