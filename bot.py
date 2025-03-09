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
    "http://212.69.125.33:80",      # Replace :80 with actual port if needed
    "http://50.231.110.26:3128",   # Example with port
    "http://189.202.188.149:8080",
    "http://50.175.123.230:80",
    "http://50.218.208.10:80",
    "http://50.169.222.241:80",
    "http://50.207.199.83:80",
    "http://50.221.230.186:80",
    "http://185.172.214.112:80",
    "http://49.207.36.81:80"        # India proxy
]

# ---- Initialize Client ----
bot = Client()
bot.delay_range = [3, 7]  # More natural delay range

# ---- Advanced Anti-Detection Setup ----
def setup_stealth():
    try:
        # Random device fingerprint
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
        
        # Rotate proxy
        if PROXIES:
            proxy = random.choice(PROXIES)
            bot.set_proxy(proxy)
            print(f"🔁 Using proxy: {proxy}")
        
        # Randomize identifiers
        bot.set_uuids({
            "phone_id": str(uuid.uuid4()),
            "uuid": str(uuid.uuid4()),
            "client_session_id": str(uuid.uuid4()),
            "advertising_id": str(uuid.uuid4()),
        })
        
        # Location settings
        bot.set_locale("en_IN")
        bot.set_timezone_offset(19800)  # IST offset
        bot.nonce = str(random.randint(1000000, 9999999))
        
    except Exception as e:
        print(f"⚠️ Stealth error: {str(e)[:50]}")

# ---- Session Management ----
def load_session_from_env():
    try:
        session_data = os.getenv(SESSION_ENV_VAR)
        if session_data:
            decoded = base64.b64decode(session_data).decode('utf-8')
            bot.set_settings(json.loads(decoded))
            print("✅ Session loaded")
            return True
    except Exception as e:
        print(f"❌ Session load error: {str(e)[:50]}")
    return False

def save_session_to_env():
    try:
        session_json = json.dumps(bot.get_settings())
        encoded = base64.b64encode(session_json.encode()).decode()
        print(f"🔑 New session: {encoded[:30]}...")  # Truncated for security
    except Exception as e:
        print(f"❌ Session save failed: {str(e)[:50]}")

# ---- Enhanced Login Flow ----
def handle_challenge():
    try:
        print("⏳ Solving challenge...")
        # Simple email-based challenge solve
        bot.challenge_resolve(bot.last_challenge_path)
        return bot.challenge_complete()
    except Exception as e:
        print(f"❌ Challenge error: {str(e)[:50]}")
        return False

def login():
    for attempt in range(3):
        try:
            setup_stealth()
            if load_session_from_env() and bot.user_id:
                print("✅ Session is valid")
                return True
                
            login_response = bot.login(USERNAME, PASSWORD)
            if login_response and login_response.get("challenge_required"):
                if handle_challenge():
                    save_session_to_env()
                    return True
                    
            save_session_to_env()
            print("✅ Login successful")
            return True
            
        except (LoginRequired, ChallengeRequired) as e:
            print(f"⚠️ Login issue: {str(e)[:50]}")
            time.sleep(random.randint(10, 30))
        except Exception as e:
            print(f"❌ Login attempt {attempt+1} failed: {str(e)[:50]}")
            time.sleep(random.randint(20, 40))
            
    return False

# ---- Human Behavior Simulation ----
def human_delay():
    time.sleep(random.uniform(1.2, 4.8))

def random_activity():
    if random.random() < 0.25:
        try:
            bot.feed_timeline()
            print("📰 Simulated feed view")
            human_delay()
        except:
            pass

# ---- Group Management Logic ----
GC_CHECK_INTERVAL = random.randint(250, 350)  # 4-6 minutes variance
GC_DEAD_TIME = 1200
TRACKING_FILE = "user_track.json"

# ... (Keep your original message arrays and tracking functions as-is)

def process_group(thread):
    try:
        random_activity()
        human_delay()
        
        # Original group processing logic
        messages = bot.direct_messages(thread_id=thread.id, amount=random.randint(8,12))
        
        # Revival logic
        last_msg = next((msg for msg in messages if msg.item_type != 'action'), None)
        if last_msg:
            last_time = last_msg.timestamp.astimezone(pytz.utc)
            if (datetime.now(pytz.utc) - last_time).total_seconds() > GC_DEAD_TIME:
                bot.direct_send(random.choice(FUNNY_REVIVE), thread_ids=[thread.id])
                print(f"💀 Revived {thread.id}")
                human_delay()
        
        # Message processing
        for msg in messages:
            # Your original message handling logic
            human_delay()
            
    except Exception as e:
        print(f"❌ Group error: {str(e)[:50]}")
        time.sleep(random.randint(30, 60))

def monitor_groups():
    error_count = 0
    while True:
        try:
            check_interval = GC_CHECK_INTERVAL * random.uniform(0.8, 1.2)
            print(f"⏳ Next check in {check_interval//60} mins")
            
            threads = bot.direct_threads(amount=random.randint(15, 25))
            for thread in random.sample(threads, k=min(3, len(threads))):
                if thread.is_group:
                    process_group(thread)
                    time.sleep(random.uniform(5, 15))
                    
            error_count = max(0, error_count-1)
            time.sleep(check_interval)
            
        except Exception as e:
            error_count += 1
            wait_time = 60 * min(error_count, 10)  # Max 10 minute wait
            print(f"⚠️ Error {error_count}: Cooling down {wait_time//60} mins")
            time.sleep(wait_time + random.randint(-30, 30))

# ---- Main Execution ----
if __name__ == "__main__":
    print("🚀 Starting Enhanced Bot...")
    if login():
        monitor_groups()
    else:
        print("❌ Critical login failure")
