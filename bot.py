from instagrapi import Client
import time
import random
import os

# ---- Instagram Credentials ----
USERNAME = "Zehra.bloom_"  # Instagram ID
PASSWORD = "Ajmat1234@@"  # Instagram Password

# ---- Instagram Client Setup ----
bot = Client()

# Function to Login
def login_instagram():
    try:
        bot.load_settings("session.json")  # Load previous session
        bot.login(USERNAME, PASSWORD)
        print("✅ Logged in using session.")
    except Exception as e:
        print(f"⚠️ Session login failed: {e}")
        try:
            bot.login(USERNAME, PASSWORD)  # Try normal login
            bot.dump_settings("session.json")  # Save new session
            print("✅ Logged in using username-password.")
        except Exception as e:
            print(f"❌ Login failed: {e}")

login_instagram()  # Call login function

DM_MESSAGES = [
    "Hey! I saw your profile and just wanted to say hi! 😊",
    "Hi there! Your posts are amazing, keep shining! ✨",
    "Hello! Just passing by to send you positive vibes! 💕",
    "Hey! Love your profile, just wanted to drop a compliment! 🌸"
]

MAX_DAILY_DMS = 15  # Ek din me max 15 DMs
DM_DELAY = 60  # Har DM ke beech 60-120 sec ka delay

# ---- Girls Name Keywords ----
GIRL_KEYWORDS = ["priya", "divya", "riya", "pinki", "nidhi", "sakshi", "simran", "soni", "shreya", "angel", "dolly", "beauty", "sweet", "baby", "pari", "queen", "cutie", "dimple", "rani"]

# ---- Boys Name Keywords ----
BOY_KEYWORDS = ["rohit", "rahul", "arjun", "abhishek", "manish", "sumit", "sachin", "ajay", "vishal", "prince", "veer", "shubham", "ravi", "dev", "rock", "king", "alpha", "hero", "bhai", "baba"]

# ---- Gender Filter Function ----
def is_girl(username, full_name):
    username = username.lower()
    full_name = full_name.lower()

    # Agar ladki ka naam mil gaya to confirm ladki
    for keyword in GIRL_KEYWORDS:
        if keyword in username or keyword in full_name:
            return True

    # Agar ladka ka naam mil gaya to confirm ladka
    for keyword in BOY_KEYWORDS:
        if keyword in username or keyword in full_name:
            return False

    # Agar gender confirm nahi ho raha to assume ladki ho sakti hai
    return True  

# ---- Get Followers of a Target Account ----
def get_followers(target_username, limit=20):
    try:
        user_id = bot.user_id_from_username(target_username)
        followers = bot.user_followers(user_id, amount=limit)
        return [(user.username, user.full_name) for user in followers.values()]
    except Exception as e:
        print(f"⚠️ Error fetching followers: {e}")
        return []

# ---- Function to Send DMs ----
def send_dms(users):
    count = 0
    for username, full_name in users:
        if count >= MAX_DAILY_DMS:
            print("🚀 DM limit reached for today.")
            break

        # Gender Check
        if not is_girl(username, full_name):
            print(f"🚫 Skipping {username} (Detected as Male)")
            continue

        try:
            user_id = bot.user_id_from_username(username)
            message = random.choice(DM_MESSAGES)
            bot.direct_send(message, [user_id])
            print(f"✅ DM sent to {username}")

            count += 1
            delay = random.randint(DM_DELAY, DM_DELAY + 60)  # Random delay
            time.sleep(delay)

        except Exception as e:
            print(f"❌ Could not DM {username}: {e}")

    print("🎯 DM sending task completed.")

# ---- Main Execution ----
if __name__ == "__main__":
    target_username = "editz_lover___05"  # Target Account ka Username

    print("\n🚀 Starting Instagram DM bot...\n")
    
    followers = get_followers(target_username, limit=30)  # Followers fetch

    if followers:
        send_dms(followers)
    else:
        print("⚠️ No followers found. Try again later.")
