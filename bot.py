from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired
import time
import random
import os
import base64
import json
from datetime import datetime, timedelta
import pytz
import uuid

# ---- Instagram Credentials ----
USERNAME = "kalllu_kaliiyaaa"
PASSWORD = "Ajmat1234@@@"
SESSION_ENV_VAR = "INSTA_SESSION_DATA"

# ---- Proxy Settings ----
PROXIES = [
    "http://212.69.125.33:80",
    "http://50.231.110.26:3128",
    "http://189.202.188.149:8080",
    "http://50.175.123.230:80",
    "http://50.218.208.10:80",
    "http://50.169.222.241:80",
    "http://50.207.199.83:80",
    "http://50.221.230.186:80",
    "http://185.172.214.112:80",
    "http://49.207.36.81:80"  # India proxy
]

# ---- Initialize Client ----
bot = Client()
bot.delay_range = [3, 7]
IST = pytz.timezone("Asia/Kolkata")

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
TRACKING_FILE = "user_track.json"
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

# ---- Anti-Detection Setup ----
def setup_stealth():
    try:
        bot.set_device({
            "app_version": "121.0.0.29.119",
            "version_code": "195820218",  # Fixed missing key
            "android_version": random.randint(25, 30),
            "android_release": f"{random.randint(8,12)}.0.0",
            "dpi": random.choice(["480dpi", "420dpi", "400dpi"]),
            "resolution": random.choice(["1080x1920", "1080x2280", "720x1280"]),
            "manufacturer": random.choice(["Xiaomi", "Samsung", "OnePlus"]),
            "device": random.choice(["Redmi Note 8", "Galaxy S21", "Nord 2"]),
            "model": "Custom Phone",
            "cpu": "qcom",
            "user_agent": ""
        })
        
        if PROXIES:
            bot.set_proxy(random.choice(PROXIES))
        
        bot.set_uuids({
            "phone_id": str(uuid.uuid4()),
            "uuid": str(uuid.uuid4()),
            "client_session_id": str(uuid.uuid4()),
            "advertising_id": str(uuid.uuid4()),
        })
        
        bot.set_locale("en_IN")
        bot.set_timezone_offset(19800)
        bot.nonce = str(random.randint(1000000, 9999999))
        
    except Exception as e:
        print(f"Stealth Error: {str(e)[:50]}")

# ---- Login System ----
def login():
    try:
        setup_stealth()
        bot.login(USERNAME, PASSWORD)
        print("✅ Logged in successfully!")
        return True
    except ChallengeRequired:
        print("⚠️ Challenge required. Trying to resolve...")
        return False
    except LoginRequired:
        print("⚠️ Login required. Restarting session...")
        return False
    except Exception as e:
        print(f"❌ Login failed: {str(e)}")
        return False

# ---- Group Logic ----
def process_group(thread):
    try:
        now = datetime.now(IST)
        messages = bot.direct_messages(thread_id=thread.id, amount=random.randint(8,12))
        
        # Revival Logic
        last_msg = next((msg for msg in messages if msg.item_type != 'action'), None)
        if last_msg:
            last_time = last_msg.timestamp.astimezone(IST)
            if (now - last_time).total_seconds() > 1200:
                if thread.id not in last_revive_time or (now - last_revive_time[thread.id]).total_seconds() > 1200:
                    bot.direct_send(random.choice(FUNNY_REVIVE), thread_ids=[thread.id])
                    last_revive_time[thread.id] = now
                    print(f"💀 Revived {thread.id}")

        # Message Processing
        for msg in messages:
            # New Member Check
            if msg.item_type == 'action' and 'added' in msg.text.lower():
                for user in msg.users:
                    if should_welcome(str(user.pk)):
                        bot.direct_send(
                            random.choice(WELCOME_MSGS).format(user=f"@{user.username}"),
                            thread_ids=[thread.id]
                        )
                        save_user(str(user.pk))
                        print(f"🎉 Welcomed @{user.username}")

            # Bad Word Check
            elif msg.item_type == 'text':
                text = msg.text.lower()
                if any(word in text for word in BAD_WORDS):
                    if msg.user_id != bot.user_id and msg.user_id not in warned_users:
                        try:
                            user_info = bot.user_info(msg.user_id)
                            user = f"@{user_info.username}"
                            bot.direct_send(random.choice(WARNINGS).format(user=user), thread_ids=[thread.id])
                            warned_users.add(msg.user_id)
                            print(f"⚠️ Warned {user}")
                        except Exception as e:
                            print(f"User Info Error: {str(e)[:50]}")

    except Exception as e:
        print(f"Group Error: {str(e)[:50]}")

def monitor_groups():
    if not login():
        print("❌ Bot failed to login. Exiting.")
        return

    while True:
        try:
            threads = bot.direct_threads(amount=10)
            for thread in threads:
                if thread.is_group:
                    process_group(thread)
                    time.sleep(random.uniform(5, 15))
            time.sleep(random.randint(250, 350))
        except Exception as e:
            print(f"⚠️ Error in monitoring: {str(e)[:50]}")
            time.sleep(60)

if __name__ == "__main__":
    print("🚀 Starting Smart Group Manager")
    monitor_groups()
