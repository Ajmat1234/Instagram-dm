from instagrapi import Client
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

# ---- Proxy List (Optional) ----
PROXIES = [
    "http://152.67.213.161:80",
    "http://194.195.119.194:3128",
    "http://45.117.179.53:8080",
    "http://103.148.210.77:80",
    "http://49.36.127.84:8080"
]

# ---- Initialize Client ----
bot = Client()
bot.delay_range = [random.uniform(2.5, 6.7), random.uniform(7.1, 12.3)]
IST = pytz.timezone("Asia/Kolkata")

# ---- Messages ----
BOT_ENTRY_MSG = "@king_of_status_4u_ sir mai aa gya aapke gc members ki sewa me"
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
    "{user} आया ओए! पार्टी शुरू! 🥳"
]
BAD_WORDS = ['mc', 'bc', 'chutiya', 'gandu', 'bhosdi', 'madarchod', 'lavde', 'lund']

# ---- Tracking System ----
TRACKING_FILE = "user_track.json"
last_revive_time = {}
warned_users = set()
entry_message_sent = False  # यह चेक करेगा कि login के बाद msg भेजा गया है या नहीं

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

# ---- Advanced Anti-Detection ----
def setup_stealth():
    try:
        print("🛡 Setting up stealth mode...")
        device_config = {
            "app_version": "121.0.0.29.119",
            "version_code": "199381241",
            "android_version": random.randint(27, 33),
            "android_release": f"{random.choice([8,9,10,11,12])}.0.0",
            "dpi": f"{random.choice([480,420,400])}dpi",
            "resolution": random.choice(["1080x1920", "1080x2280", "720x1600"]),
            "manufacturer": random.choice(["Xiaomi", "Samsung", "Realme"]),
            "device": random.choice(["Redmi Note 10", "Galaxy A52", "Narzo 50"]),
            "model": "Custom Device",
            "cpu": "qcom"
        }
        bot.set_device(device_config)

        if PROXIES:
            proxy = random.choice(PROXIES)
            bot.set_proxy(proxy)
            print(f"🌀 Using proxy: {proxy}")

        bot.set_uuids({
            "phone_id": str(uuid.uuid4()),
            "uuid": str(uuid.uuid4()),
            "client_session_id": str(uuid.uuid4()),
            "advertising_id": str(uuid.uuid4()),
        })

        bot.set_locale("en_IN")
        bot.set_timezone_offset(19800)
    except Exception as e:
        print(f"🛑 Stealth Error: {str(e)[:100]}")

# ---- Session Management ----
def load_session():
    try:
        session_data = os.getenv(SESSION_ENV_VAR)
        if session_data:
            decoded = base64.b64decode(session_data).decode()
            bot.set_settings(json.loads(decoded))
            print("✅ Session loaded")
            return True
    except Exception as e:
        print(f"❌ Session Error: {str(e)[:50]}")
    return False

# ---- Smart Login System ----
def login():
    global entry_message_sent  # ताकि एक ही बार msg भेजा जाए
    for attempt in range(3):
        try:
            setup_stealth()
            if load_session() and bot.user_id:
                return True

            print("🔐 Logging in...")
            bot.login(USERNAME, PASSWORD)
            print("✅ Login successful")

            # Login होते ही ग्रुप में मैसेज भेजेगा
            if not entry_message_sent:
                send_entry_message()
                entry_message_sent = True

            return True

        except Exception as e:
            print(f"🚨 Login Error: {str(e)[:100]}")
            time.sleep(random.randint(30, 60))
    return False

# ---- Human-like Behavior ----
def human_delay():
    time.sleep(random.uniform(1.5, 4.5))

# ---- Send Entry Message in Group ----
def send_entry_message():
    try:
        threads = bot.direct_threads(amount=10)
        for thread in threads:
            if thread.is_group:
                bot.direct_send(BOT_ENTRY_MSG, thread_ids=[thread.id])
                print(f"🚀 Entry Message Sent in {thread.title}")
                break  # सिर्फ एक ग्रुप में भेजेगा
    except Exception as e:
        print(f"❌ Entry Message Error: {str(e)[:100]}")

# ---- Group Management ----
def process_group(thread):
    try:
        print(f"📡 Scanning messages in group: {thread.title}")
        now = datetime.now(IST)
        messages = bot.direct_messages(thread_id=thread.id, amount=10)

        # Revival Logic
        last_msg = next((msg for msg in messages if msg.item_type != 'action'), None)
        if last_msg:
            last_time = last_msg.timestamp.astimezone(IST)
            if (now - last_time).total_seconds() > 1200:
                if thread.id not in last_revive_time or (now - last_revive_time[thread.id]).total_seconds() > 1200:
                    revive_msg = random.choice(FUNNY_REVIVE)
                    bot.direct_send(revive_msg, thread_ids=[thread.id])
                    last_revive_time[thread.id] = now
                    print(f"💀 Revived group {thread.title}")
                    human_delay()

        # Message Processing
        for msg in messages:
            if msg.item_type == 'text':
                text = msg.text.lower()
                if any(bad_word in text for bad_word in BAD_WORDS):
                    user_info = bot.user_info(msg.user_id)
                    warning = random.choice(WARNINGS).format(user=f"@{user_info.username}")
                    bot.direct_send(warning, thread_ids=[thread.id])
                    print(f"⚠️ Warned @{user_info.username}")
                    human_delay()
    except Exception as e:
        print(f"❌ Group Error: {str(e)[:100]}")

# ---- Monitoring System ----
def monitor_groups():
    while True:
        threads = bot.direct_threads(amount=20)
        for thread in threads:
            if thread.is_group:
                process_group(thread)
        time.sleep(random.randint(300, 420))

# ---- Start Bot ----
if __name__ == "__main__":
    print("\n🚀 Group Manager Bot Started!")
    if login():
        monitor_groups()
    else:
        print("❌ Critical Login Failure")
