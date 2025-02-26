from instagrapi import Client
import time
import random
import os
import base64
import threading

# Configuration
NOTIFY_MSGS = [
    "🚀 Attention @{mentions}! Tum sabko bulaya gaya hai! 😎",
    "🔥 Hello @{mentions}, sabhi yahan dhyan dein! Koi important baat hai! 💬",
    "👋 @{mentions}, sabko tag kar diya gaya hai! Ab koi ignore nahi kar sakta! 😂",
    "💥 @{mentions}, bas tumhari kami thi! Ab sabhi yahan hai! 🤩"
]

# Environment Variables
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
SESSION_DATA = os.getenv("SESSION_DATA")

# Load session file from environment variable
def load_session_from_env():
    if SESSION_DATA:
        try:
            decoded_data = base64.b64decode(SESSION_DATA)
            with open("ig_session.json", "wb") as f:
                f.write(decoded_data)
            print("📝 Session file decoded aur save ho gaya.")
            return True
        except Exception as e:
            print(f"❌ SESSION_DATA decode error: {e}")
            return False
    return False

# Human-like delay function
def human_delay(min_time=5, max_time=15):
    delay = random.uniform(min_time, max_time)
    print(f"⏳ Human-like delay: {round(delay, 2)} seconds")
    time.sleep(delay)

# Get all group members and mention them
def mention_all_members(thread):
    mention_list = []

    for user in thread.users:
        if user != bot.user_id:
            try:
                user_data = bot.user_info(user)
                username = user_data.dict().get("username", "Unknown")
                mention_list.append(f"@{username}")
                human_delay(2, 5)  # Small delay for each request
            except Exception as e:
                print(f"⚠️ Failed to fetch user info: {e}")
                continue  

    if len(mention_list) > 10:
        chunks = [mention_list[i:i + 10] for i in range(0, len(mention_list), 10)]
        for chunk in chunks:
            mention_text = ", ".join(chunk)
            message = random.choice(NOTIFY_MSGS).format(mentions=mention_text)
            bot.direct_answer(thread.id, text=message)
            human_delay(30, 60)  # Random delay to avoid spam
    else:
        mention_text = ", ".join(mention_list)
        message = random.choice(NOTIFY_MSGS).format(mentions=mention_text)
        bot.direct_answer(thread.id, text=message)

    print(f"🔔 Notification sent to: {mention_list}")

# Continuous bot function (scanning groups)
def scan_groups():
    while True:
        try:
            print(f"\n🌀 Scanning groups at {time.strftime('%H:%M:%S')}")
            threads = bot.direct_threads(amount=10)  
            for thread in threads:
                if thread.is_group:
                    mention_all_members(thread)
                    human_delay(60, 120)  

        except Exception as e:
            print(f"⚠️ Error: {str(e)}")
            human_delay(5, 10)

# Start bot function
def start_bot():
    global bot
    bot = Client()

    if load_session_from_env():
        try:
            bot.load_settings("ig_session.json")
            human_delay(3, 8)  # Fake human-like action delay
            bot.get_timeline_feed()  
            print("✅ Logged in using session!")
        except:
            print("❌ Session invalid, manual login kar raha hoon...")
            bot.login(USERNAME, PASSWORD)
            human_delay(5, 15)
            bot.dump_settings("ig_session.json")
    else:
        print("❌ Session nahi mila, manually login kar rahe hain...")
        bot.login(USERNAME, PASSWORD)
        human_delay(5, 15)
        bot.dump_settings("ig_session.json")

    # Dummy action to make login look human-like
    print("📢 Sending a random feed request to mimic human behavior...")
    bot.get_timeline_feed()  
    human_delay(5, 10)

    print(f"🚀 Bot started: {time.strftime('%d-%m-%Y %H:%M')}")
    scan_thread = threading.Thread(target=scan_groups)
    scan_thread.start()

if __name__ == "__main__":
    start_bot()
