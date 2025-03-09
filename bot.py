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

# ---- Session Management ----
def load_session_from_env():
    try:
        session_data = os.getenv(SESSION_ENV_VAR)
        if session_data:
            decoded = base64.b64decode(session_data).decode()
            bot.set_settings(json.loads(decoded))
            print("✅ Session loaded")
            return True
    except Exception as e:
        print(f"Session Error: {str(e)[:50]}")
    return False

def save_session_to_env():
    try:
        session_json = json.dumps(bot.get_settings())
        encoded = base64.b64encode(session_json.encode()).decode()
        print(f"🔑 New Session: {encoded[:30]}...")
    except Exception as e:
        print(f"Save Failed: {str(e)[:50]}")

# ---- Enhanced Login ----
def handle_challenge():
    try:
        bot.challenge_resolve(bot.last_challenge_path)
        return bot.challenge_complete()
    except Exception as e:
        print(f"Challenge Error: {str(e)[:50]}")
        return False

def login():
    for _ in range(3):
        try:
            setup_stealth()
            if load_session_from_env() and bot.user_id:
                return True
                
            login_response = bot.login(USERNAME, PASSWORD)
            if login_response and login_response.get("challenge_required"):
                if handle_challenge():
                    save_session_to_env()
                    return True
                    
            save_session_to_env()
            return True
            
        except (LoginRequired, ChallengeRequired) as e:
            print(f"Login Issue: {str(e)[:50]}")
            time.sleep(random.randint(10, 30))
        except Exception as e:
            print(f"Login Failed: {str(e)[:50]}")
            time.sleep(random.randint(20, 40))
    return False

# ---- Human Behavior ----
def human_delay():
    time.sleep(random.uniform(1.2, 4.8))

def random_activity():
    if random.random() < 0.25:
        try:
            bot.feed_timeline()
            human_delay()
        except:
            pass

# ---- Group Logic ----
def process_group(thread):
    try:
        random_activity()
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
                    human_delay()

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
                        human_delay()

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
                            human_delay()
                        except Exception as e:
                            print(f"User Info Error: {str(e)[:50]}")

    except Exception as e:
        print(f"Group Error: {str(e)[:50]}")
        time.sleep(random.randint(30, 60))

def monitor_groups():
    error_count = 0
    while True:
        try:
            check_interval = random.randint(250, 350) * random.uniform(0.8, 1.2)
            print(f"⏳ Next Check: {check_interval//60} mins")
            
            threads = bot.direct_threads(amount=random.randint(15, 25))
            for thread in random.sample(threads, k=min(3, len(threads))):
                if thread.is_group:
                    process_group(thread)
                    time.sleep(random.uniform(5, 15))
                    
            error_count = max(0, error_count-1)
            time.sleep(check_interval)
            
        except Exception as e:
            error_count += 1
            wait_time = 60 * min(error_count, 10)
            print(f"⚠️ Cooling Down: {wait_time//60} mins")
            time.sleep(wait_time + random.randint(-30, 30))

if __name__ == "__main__":
    print("🚀 Starting Smart Group Manager")
    if login():
        monitor_groups()
    else:
        print("❌ Critical Login Failure")
