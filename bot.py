from instagrapi import Client
import json
import time
import random
from datetime import datetime, timedelta

# ---- Configuration ----
SESSION_DATA = "your_session_data_here"  # Railway ke ENV me yeh set karna
BTS_HASHTAGS = ["btsarmy", "btsforever", "btson", "btslove", "btsfan"]
COMMON_GIRL_NAMES = ["priya", "shreya", "anjali", "neha", "pooja", "queen", "baby", "angel", "cutie", "sweetie"]
DM_MESSAGES = [
    "Hey! I saw your profile and just wanted to say hi! 😊",
    "Hi there! Your posts are amazing, keep shining! ✨",
    "Hello! Just passing by to send you positive vibes! 💕",
    "Hey! Love your profile, just wanted to drop a compliment! 🌸"
]

USERNAME_FILE = "usernames.json"
MAX_DAILY_DMS = 20  # Ek baar me sirf 20 DM bhejne hain
DM_DELAY = 60  # 1 minute ka delay har message ke beech
BREAK_TIME = 14400  # 4 ghante (in seconds)

# ---- Instagram Client Setup ----
bot = Client()
bot.load_settings(SESSION_DATA)

# ---- Function to collect usernames ----
def collect_usernames():
    usernames = set()

    for hashtag in BTS_HASHTAGS:
        try:
            print(f"🔍 Searching for posts under #{hashtag}...")
            posts = bot.hashtag_medias_top(hashtag, amount=10)
            
            for post in posts:
                username = post.user.username.lower()
                if username not in usernames:
                    usernames.add(username)
        except Exception as e:
            print(f"⚠️ Error fetching from #{hashtag}: {e}")

    # Save collected usernames
    with open(USERNAME_FILE, "w") as f:
        json.dump(list(usernames), f)

    print(f"✅ Collected {len(usernames)} usernames.")
    return usernames

# ---- Function to filter girl usernames ----
def filter_girl_usernames():
    try:
        with open(USERNAME_FILE, "r") as f:
            usernames = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    filtered_users = [u for u in usernames if any(name in u for name in COMMON_GIRL_NAMES)]

    print(f"🎯 {len(filtered_users)} potential girl accounts found.")
    return filtered_users

# ---- Function to send DMs safely ----
def send_dms(usernames):
    count = 0

    for username in usernames:
        if count >= MAX_DAILY_DMS:
            print("🚀 20 DMs sent. Taking a 4-hour break...")
            time.sleep(BREAK_TIME)
            count = 0

        try:
            user_id = bot.user_id_from_username(username)
            message = random.choice(DM_MESSAGES)

            bot.direct_send(message, [user_id])
            print(f"✅ DM sent to {username}")

            count += 1
            time.sleep(DM_DELAY + random.randint(5, 15))  # Safe delay

        except Exception as e:
            print(f"❌ Could not DM {username}: {e}")
            continue

# ---- Main Execution ----
if __name__ == "__main__":
    while True:
        print("\n🚀 Starting Instagram BTS DM bot...\n")
        collect_usernames()
        girl_usernames = filter_girl_usernames()

        if girl_usernames:
            send_dms(girl_usernames)
        else:
            print("⚠️ No target usernames found. Retrying after 1 hour.")
            time.sleep(3600)
