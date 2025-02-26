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

# Environment Variables (Railway.com ya local environment me set karna hoga)
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
            print(f"❌ SESSION_DATA decode nahi ho saka: {e}")
            return False
    return False

# Get all group members and mention them
def mention_all_members(thread):
    users = thread.users
    mention_list = [f"@{bot.user_info(user).username}" for user in users if user != bot.user_id]
    
    # Agar group me bahut zyada members hain, to multiple messages bhejne honge
    if len(mention_list) > 10:
        chunks = [mention_list[i:i + 10] for i in range(0, len(mention_list), 10)]
        for chunk in chunks:
            mention_text = ", ".join(chunk)
            message = random.choice(NOTIFY_MSGS).format(mentions=mention_text)
            bot.direct_answer(thread.id, text=message)
            time.sleep(3)  # Instagram limit se bachne ke liye
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

            threads = bot.direct_threads(amount=10)  # Check latest 10 groups
            for thread in threads:
                if thread.is_group:
                    mention_all_members(thread)
                    time.sleep(60)  # 1 minute delay to avoid spam

        except Exception as e:
            print(f"⚠️ Error: {str(e)}")
            time.sleep(5)

# Start bot function
def start_bot():
    global bot
    bot = Client()

    if load_session_from_env():
        try:
            bot.load_settings("ig_session.json")
            print("✅ Logged in using session!")
        except:
            print("❌ Session load fail, manual login kar raha hoon...")
            bot.login(USERNAME, PASSWORD)
            bot.dump_settings("ig_session.json")
    else:
        print("❌ Session nahi mila, manually login kar rahe hain...")
        bot.login(USERNAME, PASSWORD)
        bot.dump_settings("ig_session.json")

    print(f"🚀 Bot started: {time.strftime('%d-%m-%Y %H:%M')}")

    # **Thread start** (Multithreading for fast execution)
    scan_thread = threading.Thread(target=scan_groups)
    scan_thread.start()

if __name__ == "__main__":
    start_bot()
