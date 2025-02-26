from instagrapi import Client
import time
import random
import os
import base64
import threading
from dotenv import load_dotenv  # For local testing

# Configuration
NOTIFY_MSGS = [
    "🚀 Attention {mentions}! Tum sabko bulaya gaya hai! 😎",
    "🔥 Hello {mentions}, sabhi yahan dhyan dein! 💬",
    "👋 {mentions}, sabko tag kar diya gaya hai! 😂",
    "💥 {mentions}, bas tumhari kami thi! 🤩"
]

# Improved Error Handling
MAX_RETRIES = 3
REQUEST_DELAY = (2, 5)

# Session Management
SESSION_FILE = "ig_session.json"

def load_session():
    if os.getenv("SESSION_DATA"):
        try:
            decoded = base64.b64decode(os.getenv("SESSION_DATA"))
            with open(SESSION_FILE, "wb") as f:
                f.write(decoded)
            print("✅ Session loaded from environment")
            return True
        except Exception as e:
            print(f"❌ Session load error: {str(e)}")
            return False
    return False

def human_delay(min=5, max=15):
    delay = random.uniform(min, max)
    print(f"⏳ Waiting {delay:.1f}s")
    time.sleep(delay)

def get_members(thread):
    members = []
    print(f"\n🔍 Scanning Group: {thread.id}")
    
    try:
        for user in thread.users:  # Fix: thread.user_ids → thread.users
            if user.pk == bot.user_id:
                continue
                
            for _ in range(MAX_RETRIES):
                try:
                    user_info = bot.user_info(user.pk)  # Fix: Access user.pk instead of user_id
                    if not user_info.is_private:
                        members.append(f"@{user_info.username}")
                        print(f"✅ {user_info.username}")
                    else:
                        print(f"🔒 Private: {user_info.username}")
                    break
                except Exception as e:
                    print(f"⚠️ Error @{user.pk}: {str(e)}")
                    time.sleep(random.uniform(*REQUEST_DELAY))
                    
            human_delay(1, 3)
            
    except Exception as e:
        print(f"🚨 Critical error: {str(e)}")
        
    return members

def send_mentions(thread):
    members = get_members(thread)  # Pehle sab members ko fetch karega
    if not members:
        return

    print("\n✅ All members fetched successfully!")
    
    # Batches of 10 members
    for i in range(0, len(members), 10):
        batch = members[i:i+10]
        try:
            msg = random.choice(NOTIFY_MSGS).format(mentions=", ".join(batch))
            bot.direct_send(msg, thread_ids=[thread.id])
            print(f"📩 Sent to {len(batch)} users")
            time.sleep(60)  # 1-minute delay between mentions
        except Exception as e:
            print(f"❌ Failed to send: {str(e)}")

def group_scanner():
    while True:
        try:
            print(f"\n🕒 {time.strftime('%H:%M:%S')} Checking groups...")
            threads = bot.direct_threads(amount=5)
            
            for thread in threads:
                if thread.is_group:
                    send_mentions(thread)  # Fetch all members first, then mention in batches
                    
            time.sleep(random.randint(300, 600))  # 5-10 minute scan interval
            
        except Exception as e:
            print(f"🔥 Crash: {str(e)}")
            time.sleep(random.randint(60, 120))

def start_bot():
    global bot
    bot = Client()
    
    # Login Logic
    if load_session():
        try:
            bot.load_settings(SESSION_FILE)
            bot.get_timeline_feed()  # Test session
            print("👍 Session login successful!")
        except:
            print("🔑 Session expired, logging in fresh...")
            bot.login(os.getenv("USERNAME"), os.getenv("PASSWORD"))
            bot.dump_settings(SESSION_FILE)
    else:
        print("🔑 New login...")
        bot.login(os.getenv("USERNAME"), os.getenv("PASSWORD"))
        bot.dump_settings(SESSION_FILE)
    
    # Start scanner
    threading.Thread(target=group_scanner, daemon=True).start()
    
    # Keep alive
    while True:
        time.sleep(3600)

if __name__ == "__main__":
    load_dotenv()  # Remove this line on Railway
    start_bot()
