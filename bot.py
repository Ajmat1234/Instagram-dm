from instagrapi import Client
import json
import time
import random
import base64
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# ---- Load Environment Variables ----
load_dotenv()
SESSION_DATA = os.getenv("SESSION_DATA")

# ---- Configuration ----
HASHTAGS = [
    "btsarmy", "btsforever", "btson", "btslove", "btsfan",
    "girlsfashion", "cutegirls", "instagirl", "girllove", "trendylook",
    "selfielove", "queenstyle", "girlcrush", "femininevibes"
]
BTS_KEYWORDS = ["bts", "army", "bangtan", "jungkook", "taehyung", "jimin", "suga", "rm", "jin", "jhope"]

DM_MESSAGES = [
    "Hey! I saw your profile and just wanted to say hi! 😊",
    "Hi there! Your posts are amazing, keep shining! ✨",
    "Hello! Just passing by to send you positive vibes! 💕",
    "Hey! Love your profile, just wanted to drop a compliment! 🌸"
]

USERNAME_FILE = "usernames.json"
MAX_DAILY_DMS = 20  
DM_DELAY = 60  
BREAK_TIME = 14400  

# ---- Instagram Client Setup ----
bot = Client()

def load_session():
    if SESSION_DATA:
        try:
            decoded_data = base64.b64decode(SESSION_DATA)
            with open("ig_session.json", "wb") as f:
                f.write(decoded_data)

            print("📝 Session file decoded and saved.")
            bot.load_settings("ig_session.json")
            bot.get_timeline_feed()
            print("✅ Session login successful!")
            return True
        except Exception as e:
            print(f"❌ Session load error: {str(e)}")
    return False

def login():
    if load_session():
        return

    print("🔑 Logging in fresh...")
    bot.login("Zehra.bloom_", "Ajmat1234@")  # Username & Password without 2-step verification
    
    session_data = bot.get_settings()
    encoded_session = base64.b64encode(json.dumps(session_data).encode()).decode()
    
    with open("ig_session.json", "w") as f:
        json.dump(session_data, f)
    
    print("🔹 Copy and paste this SESSION_DATA into Railway environment variables:")
    print(encoded_session)

# ---- Function to collect usernames ----
def collect_usernames():
    usernames = set()
    for hashtag in HASHTAGS:
        try:
            print(f"🔍 Searching for posts under #{hashtag}...")
            posts = bot.hashtag_medias_top(hashtag, amount=10)
            for post in posts:
                username = post.user.username.lower()
                usernames.add(username)
        except Exception as e:
            print(f"⚠️ Error fetching from #{hashtag}: {e}")

    with open(USERNAME_FILE, "w") as f:
        json.dump(list(usernames), f)
    print(f"✅ Collected {len(usernames)} usernames.")
    return usernames

# ---- Function to filter BTS-related usernames ----
def filter_bts_usernames():
    try:
        with open(USERNAME_FILE, "r") as f:
            usernames = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    bts_users = []
    for username in usernames:
        try:
            user_info = bot.user_info_by_username(username)
            full_name = user_info.full_name.lower() if user_info.full_name else ""
            bio = user_info.biography.lower() if user_info.biography else ""

            if any(keyword in username for keyword in BTS_KEYWORDS) or any(keyword in full_name for keyword in BTS_KEYWORDS) or any(keyword in bio for keyword in BTS_KEYWORDS):
                bts_users.append(username)
        except Exception as e:
            print(f"⚠️ Could not fetch info for {username}: {e}")

    print(f"🎯 {len(bts_users)} BTS-related accounts found.")
    return bts_users

# ---- Function to send DMs safely ----
def send_dms(usernames):
    count = 0
    retry_attempts = 0

    while count < MAX_DAILY_DMS and retry_attempts < 3:
        for username in usernames:
            if count >= MAX_DAILY_DMS:
                break

            try:
                user_id = bot.user_id_from_username(username)
                message = random.choice(DM_MESSAGES)
                bot.direct_send(message, [user_id])
                print(f"✅ DM sent to {username}")

                count += 1
                time.sleep(DM_DELAY + random.randint(5, 15))  

            except Exception as e:
                print(f"❌ Could not DM {username}: {e}")
                continue

        if count < MAX_DAILY_DMS:
            print("⚠️ Not enough DMs sent, retrying after 5 minutes...")
            time.sleep(300)  
            retry_attempts += 1

    print("🚀 All possible DMs sent for now. Taking a short break.")

# ---- Main Execution ----
if __name__ == "__main__":
    login()
    while True:
        print("\n🚀 Starting Instagram DM bot...\n")
        collect_usernames()
        bts_usernames = filter_bts_usernames()

        if bts_usernames:
            send_dms(bts_usernames)
        else:
            print("⚠️ No BTS-related usernames found. Retrying in 10 minutes.")
            time.sleep(600)
