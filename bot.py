from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired
import time
import random
import os
import base64
import json
import uuid
from datetime import datetime, timedelta
import pytz

# ---- Credentials ----
USERNAME = "kalllu_kaliiyaaa"
PASSWORD = "Ajmat1234@@@"
SESSION_FILE = "session_data.json"

# ---- Initialize Client ----
bot = Client()
bot.delay_range = [5, 10]  # Human-like delay
IST = pytz.timezone("Asia/Kolkata")

# ---- Device Spoofing ----
def setup_stealth():
def setup_stealth():
    try:
        bot.set_device({
            "app_version": "321.0.0.18.114",
            "version_code": "321180114",
            "android_version": random.randint(26, 33),
            "android_release": f"{random.randint(9, 14)}.0.0",
            "dpi": random.choice(["480dpi", "420dpi", "400dpi"]),
            "resolution": random.choice(["1080x2400", "1440x3120", "1080x1920"]),
            "manufacturer": random.choice(["Samsung", "Google", "OnePlus", "Xiaomi"]),
            "device": random.choice(["Galaxy S23", "Pixel 7", "OnePlus 11", "Redmi K50"]),
            "model": "Custom Phone",
            "cpu": "qcom",
            "user_agent": f"Instagram 321.0.0.18.114 Android ({random.randint(26, 33)}; {random.choice(['Pixel 7', 'Galaxy S23', 'OnePlus 11'])})"
        })

        bot.set_uuids({
            "phone_id": str(uuid.uuid4()),
            "uuid": str(uuid.uuid4()),
            "client_session_id": str(uuid.uuid4()),
            "advertising_id": str(uuid.uuid4()),
        })
        
        bot.set_locale("en_US")
        bot.set_timezone_offset(19800)  # Indian Timezone
        
        bot.nonce = str(random.randint(1000000, 9999999))

    except Exception as e:
        print(f"Stealth Setup Error: {str(e)[:50]}")

# ---- Secure Session Management ----
def load_session():
    try:
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, "r") as f:
                session_data = json.load(f)
                bot.set_settings(session_data)
                print("✅ Session loaded successfully")
                return True
    except Exception as e:
        print(f"Session Load Error: {str(e)[:50]}")
    return False

def save_session():
    try:
        with open(SESSION_FILE, "w") as f:
            json.dump(bot.get_settings(), f)
            print("🔑 Session saved securely")
    except Exception as e:
        print(f"Save Session Failed: {str(e)[:50]}")

# ---- Handle Login ----
def login():
    for _ in range(3):
        try:
            setup_stealth()
            if load_session() and bot.user_id:
                return True
                
            login_response = bot.login(USERNAME, PASSWORD)
            if login_response and login_response.get("challenge_required"):
                if handle_challenge():
                    save_session()
                    return True
                    
            save_session()
            return True
            
        except (LoginRequired, ChallengeRequired) as e:
            print(f"Login Issue: {str(e)[:50]}")
            time.sleep(random.randint(10, 30))
        except Exception as e:
            print(f"Login Failed: {str(e)[:50]}")
            time.sleep(random.randint(20, 40))
    return False

# ---- Handle Instagram Challenges ----
def handle_challenge():
    try:
        bot.challenge_resolve(bot.last_challenge_path)
        return bot.challenge_complete()
    except Exception as e:
        print(f"Challenge Error: {str(e)[:50]}")
        return False

# ---- Human-like Delay ----
def human_delay():
    time.sleep(random.uniform(2, 6))  # Random delay in seconds

def random_activity():
    if random.random() < 0.3:
        try:
            bot.feed_timeline()
            human_delay()
        except:
            pass

# ---- Smart Group Management ----
def process_group(thread):
    try:
        random_activity()
        now = datetime.now(IST)

        messages = bot.direct_messages(thread_id=thread.id, amount=random.randint(8,12))

        last_msg = next((msg for msg in messages if msg.item_type != 'action'), None)
        if last_msg:
            last_time = last_msg.timestamp.astimezone(IST)
            if (now - last_time).total_seconds() > 1800:  # 30 min inactivity check
                bot.direct_send("Group inactive! Koi hai? 👀", thread_ids=[thread.id])
                print(f"💀 Revived {thread.id}")
                human_delay()

        for msg in messages:
            if msg.item_type == 'text':
                text = msg.text.lower()
                if "spam" in text:
                    bot.direct_send("⚠️ No spamming allowed!", thread_ids=[thread.id])
                    print("🚨 Spam detected and warned!")
                    human_delay()

    except Exception as e:
        print(f"Group Error: {str(e)[:50]}")
        time.sleep(random.randint(30, 60))

def monitor_groups():
    error_count = 0
    while True:
        try:
            check_interval = random.randint(300, 450) * random.uniform(0.8, 1.2)
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
