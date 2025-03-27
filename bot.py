from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired
import json
import time
import random
import os
import base64
from datetime import datetime, timedelta
import pytz

# Configuration
WELCOME_MSGS = [
    "Welcome @{username}, humein khushi hai ki aap hamare group mein shamil hue!",
    "Hello @{username}, aapka swagat hai, enjoy kijiye!"
]
TRACKING_FILE = "user_track.json"

# Environment Variables
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
SESSION_DATA = os.getenv("SESSION_DATA")

# User tracking system
def load_users():
    try:
        with open(TRACKING_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_user(user_id, last_mentioned):
    users = load_users()
    users[user_id] = last_mentioned.isoformat()
    with open(TRACKING_FILE, "w") as f:
        json.dump(users, f)

def should_welcome(user_id):
    users = load_users()
    if user_id not in users:
        return True
    last_mentioned = datetime.fromisoformat(users[user_id])
    return datetime.now(pytz.utc) - last_mentioned > timedelta(hours=12)

# Load session file from environment variable
def load_session_from_env():
    if SESSION_DATA:
        try:
            decoded_data = base64.b64decode(SESSION_DATA)
            with open("ig_session.json", "wb") as f:
                f.write(decoded_data)
            print("📝 Session file decoded and saved.")
            return True
        except Exception as e:
            print(f"❌ Failed to decode SESSION_DATA: {e}")
            return False
    return False

# Authentication code handler
def handle_challenge():
    challenge_url = bot.last_json.get("challenge", {}).get("api_path")
    if challenge_url:
        print(f"🔒 Challenge URL: {challenge_url}")
        code = input("Enter code here: ")  # Manual code entry
        bot.challenge_resolve(challenge_url, code)
        print("✅ Challenge resolved, re-logging in...")
        bot.login(USERNAME, PASSWORD)
        bot.dump_settings("ig_session.json")

# Bot logic
def forever_bot():
    last_checked_message_id = None  # To track the latest message processed
    while True:
        try:
            print(f"\n🌀 {datetime.now(pytz.utc).strftime('%H:%M:%S')} - Scanning...")
            threads = bot.direct_threads(amount=3)  # Reduced to 3 for stealth
            for thread in threads:
                if thread.is_group:
                    messages = bot.direct_messages(thread_id=thread.id, amount=1)  # Only latest message
                    for msg in messages:
                        if last_checked_message_id == msg.id:
                            continue  # Skip if already processed
                        if msg.user_id != bot.user_id and should_welcome(msg.user_id):
                            # Check if message is recent (within 1 minute)
                            if msg.timestamp > datetime.now(pytz.utc) - timedelta(minutes=1):
                                username = get_username(msg.user_id)
                                welcome_msg = random.choice(WELCOME_MSGS).format(username=username)
                                bot.direct_answer(thread_id=thread.id, text=welcome_msg)
                                save_user(msg.user_id, datetime.now(pytz.utc))
                                print(f"👋 Sent to @{username}: {welcome_msg}")
                        last_checked_message_id = msg.id  # Update last processed message

            # स्लीप हटा दिया, अब तुरंत अगला स्कैन शुरू होगा

        except ChallengeRequired:
            print("🔒 Challenge detected, handling authentication...")
            handle_challenge()

        except Exception as e:
            print(f"⚠️ Error: {str(e)}")
            time.sleep(300)  # एरर पर 5 मिनट का ब्रेक रखा, बाकी स्लीप हटा दिया

def get_username(user_id):
    try:
        user = bot.user_info(user_id)
        return user.username
    except Exception:
        return "user"

# Start bot function
def start_bot():
    global bot
    bot = Client()

    # Rate limiting to avoid detection (Instagram के लिए जरूरी)
    bot.delay_range = [1, 3]  # API कॉल्स के बीच 1-3 सेकंड का रैंडम डिले, थोड़ा तेज़ किया

    if load_session_from_env():
        try:
            bot.load_settings("ig_session.json")
            print("✅ Logged in using session!")
        except:
            print("❌ Session load failed, attempting manual login...")
            bot.login(USERNAME, PASSWORD)
            bot.dump_settings("ig_session.json")
    else:
        print("❌ No session found, logging in manually...")
        bot.login(USERNAME, PASSWORD)
        bot.dump_settings("ig_session.json")

    print(f"🚀 Bot started: {datetime.now(pytz.utc).strftime('%d-%m-%Y %H:%M')}")
    forever_bot()

if __name__ == "__main__":
    start_bot()
