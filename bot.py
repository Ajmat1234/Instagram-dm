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

# ---- Updated Proxy List ----
PROXIES = [
    "http://152.67.213.161:80",    # Reliable Indian proxy
    "http://194.195.119.194:3128",  # Premium
    "http://45.117.179.53:8080",   # Mumbai based
    "http://103.148.210.77:80",    # Delhi server
    "http://49.36.127.84:8080"    # Fast Indian proxy
]

# ---- Initialize Client ----
bot = Client()
bot.delay_range = [random.uniform(2.5, 6.7), random.uniform(7.1, 12.3)]  # Dynamic delay
IST = pytz.timezone("Asia/Kolkata")

# ---- Enhanced Messages ----
FUNNY_REVIVE = [
    "Group तो मर गया... कोई ज़िंदा है? 💀",
    "चुप्पी का सुनामी आ गया क्या? 🌊",
    "अरे यार! बात करो ना... 👻",
    "क्या सब सो गए? 😴 जगाओ किसी को!"
]

WARNINGS = [
    "{user} भाई! भाषा संभालो! ⚠️",
    "ऐसे शब्द नहीं चलेंगे {user}! 🚫",
    "ये ग्रुप सैफ जोन है {user} 😡",
    "वार्निंग 1/3 ⚠️ {user}"
]

WELCOME_MSGS = [
    "नमस्ते {user}! स्वागत है! 🎉",
    "{user} आया ओए! पार्टी शुरू! 🥳",
    "😍 {user}, TUSSI AA GYE HO TO MUJHE CHHOD KR N JAANA! 🥺",
    "👋 ओये {user}! कैसे हो?"
]

BAD_WORDS = [
    'mc', 'bc', 'chutiya', 'gandu', 
    'bhosdi', 'madarchod', 'lavde', 'lund',
    'jhaat', 'gaand', 'kutta', 'kuttiya',
    'randi', 'kamina', 'harami'
]

# ---- Tracking System ----
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
    return users.get(user_id) is None or \
        (datetime.now(IST) - datetime.fromisoformat(users[user_id]).total_seconds() > 43200  # 12 hours

# ---- Advanced Anti-Detection ----
def setup_stealth():
    try:
        device_config = {
            "app_version": "121.0.0.29.119",
            "version_code": "199381241",  # Critical fix added
            "android_version": random.randint(27, 33),
            "android_release": f"{random.choice([8,9,10,11,12])}.0.0",
            "dpi": f"{random.choice([480,420,400])}dpi",
            "resolution": random.choice(["1080x1920", "1080x2280", "720x1600"]),
            "manufacturer": random.choice(["Xiaomi", "Samsung", "Realme"]),
            "device": random.choice(["Redmi Note 10", "Galaxy A52", "Narzo 50"]),
            "model": "Custom Device",
            "cpu": "qcom",
            "user_agent": ""
        }
        bot.set_device(device_config)
        
        # Smart Proxy Rotation
        global PROXIES
        if PROXIES:
            proxy = random.choice(PROXIES)
            bot.set_proxy(proxy)
            print(f"🌀 Testing proxy: {proxy}")
            # Test proxy connection
            bot.get_timeline_feed()  # Simple API call to test
        else:
            print("⚠️ No proxies left! Using direct connection")
        
        bot.set_uuids({
            "phone_id": str(uuid.uuid4()),
            "uuid": str(uuid.uuid4()),
            "client_session_id": str(uuid.uuid4()),
            "advertising_id": str(uuid.uuid4()),
        })
        
        bot.set_locale("en_IN")
        bot.set_timezone_offset(19800)  # IST
        bot.nonce = str(random.randint(1000000, 9999999))
        
    except Exception as e:
        print(f"🛑 Stealth Error: {str(e)[:100]}")
        if PROXIES:
            PROXIES.remove(proxy)
            print(f"Removed bad proxy: {proxy} | Remaining: {len(PROXIES)}")

# ---- Session Management ----
def load_session():
    try:
        session_data = os.getenv(SESSION_ENV_VAR)
        if session_data:
            decoded = base64.b64decode(session_data).decode()
            bot.set_settings(json.loads(decoded))
            if not validate_session():
                print("🔄 Session expired, re-login required")
                return False
            print("✅ Session loaded")
            return True
    except Exception as e:
        print(f"❌ Session Error: {str(e)[:50]}")
    return False

def validate_session():
    try:
        bot.get_timeline_feed()
        return True
    except:
        return False

def save_session():
    try:
        session_json = json.dumps(bot.get_settings())
        encoded = base64.b64encode(session_json.encode()).decode()
        print(f"🔑 New Session: {encoded[:30]}...")
    except Exception as e:
        print(f"💾 Save Failed: {str(e)[:50]}")

# ---- Smart Login System ----
def handle_challenge():
    try:
        print("🔐 Solving security challenge...")
        bot.challenge_resolve(bot.last_challenge_path)
        if bot.challenge_complete():
            print("✅ Challenge passed")
            return True
    except Exception as e:
        print(f"❌ Challenge Error: {str(e)[:100]}")
    return False

def login():
    for attempt in range(5):
        try:
            setup_stealth()
            if load_session() and validate_session():
                return True
                
            print(f"🔑 Login attempt {attempt+1}/5")
            login_response = bot.login(USERNAME, PASSWORD)
            
            if login_response.get("challenge_required"):
                if handle_challenge():
                    save_session()
                    return True
                    
            if login_response.get("authenticated"):
                save_session()
                print("✅ Login successful")
                return True
                
        except (LoginRequired, ChallengeRequired) as e:
            print(f"⚠️ Login Issue: {str(e)[:100]}")
            time.sleep(random.randint(15, 45))
        except Exception as e:
            print(f"🚨 Critical Error: {str(e)[:100]}")
            time.sleep(random.randint(30, 90))
    
    print("❌ Maximum login attempts reached")
    return False

# ---- Human-like Behavior ----
def human_delay():
    time.sleep(random.uniform(1.5, random.choice([3.2, 4.7, 6.1])))

def random_activity():
    actions = [
        lambda: bot.feed_timeline(),
        lambda: bot.user_following(bot.user_id, count=random.randint(1,3)),
        lambda: bot.get_recent_activity()
    ]
    if random.random() < 0.4:
        random.choice(actions)()
        human_delay()

# ---- Group Management ----
def process_group(thread):
    try:
        random_activity()
        now = datetime.now(IST)
        
        messages = bot.direct_messages(thread_id=thread.id, amount=random.randint(8,12))
        
        # Revival System
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
            # New Member Handling
            if msg.item_type == 'action' and 'added' in msg.text.lower():
                for user in msg.users:
                    if should_welcome(str(user.pk)):
                        welcome_msg = random.choice(WELCOME_MSGS).format(user=f"@{user.username}")
                        bot.direct_send(welcome_msg, thread_ids=[thread.id])
                        save_user(str(user.pk))
                        print(f"🎉 Welcomed @{user.username}")
                        human_delay()

            # Bad Word Filter
            elif msg.item_type == 'text':
                text = msg.text.lower()
                if any(bad_word in text for bad_word in BAD_WORDS):
                    if msg.user_id != bot.user_id and msg.user_id not in warned_users:
                        try:
                            user_info = bot.user_info(msg.user_id)
                            warning = random.choice(WARNINGS).format(user=f"@{user_info.username}")
                            bot.direct_send(warning, thread_ids=[thread.id])
                            warned_users.add(msg.user_id)
                            print(f"⚠️ Warned @{user_info.username}")
                            human_delay()
                        except Exception as e:
                            print(f"🚫 Warning Error: {str(e)[:50]}")

    except Exception as e:
        print(f"❌ Group Error: {str(e)[:100]}")
        time.sleep(random.randint(30, 90))

# ---- Monitoring System ----
def monitor_groups():
    error_count = 0
    while True:
        try:
            check_interval = random.choice([180, 240, 300, 360])  # 3-6 mins
            print(f"⏳ Next check in {check_interval//60} mins")
            
            threads = bot.direct_threads(amount=random.randint(15, 25))
            groups = [t for t in threads if t.is_group]
            
            for thread in random.sample(groups, k=min(5, len(groups))):
                process_group(thread)
                time.sleep(random.uniform(10, 20))
                
            error_count = max(0, error_count-1)
            time.sleep(check_interval)
            
        except Exception as e:
            error_count += 1
            wait_time = min(error_count * 120, 1800)  # Max 30 mins
            print(f"🚨 Critical Error: Cooling down {wait_time//60} mins")
            time.sleep(wait_time + random.randint(-60, 60))
            
            if error_count > 3:
                print("🔄 Attempting re-login...")
                if login():
                    error_count = 0

if __name__ == "__main__":
    print("\n🚀 Starting Ultra Group Manager v2.0")
    if login():
        monitor_groups()
    else:
        print("❌ Critical Login Failure - Check credentials/proxy")
