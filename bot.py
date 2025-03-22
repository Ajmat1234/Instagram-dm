from instabot import Bot
import os
import base64
import json
import time

# ✅ Environment Variables from Railway
USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")
SESSION_DATA = os.environ.get("SESSION_DATA")

# ✅ Bot Initialization
bot = Bot()

# ✅ Session Restore Logic
if SESSION_DATA:
    print("🔁 Restoring Session from Base64...")
    decoded_session = base64.b64decode(SESSION_DATA).decode()

    # ✅ Save Session in Correct Format
    session_file_path = "config/{}_uuid_and_cookie.json".format(USERNAME)
    os.makedirs("config", exist_ok=True)

    with open(session_file_path, "w") as file:
        file.write(decoded_session)

    # ✅ Attempt Login Using Restored Session
    if bot.login(username=USERNAME, password=PASSWORD, use_cookie=True):
        print("✅ Session Restored Successfully!")
    else:
        print("❌ Session Restore Failed. Logging in Normally...")
        bot.login(username=USERNAME, password=PASSWORD)
        bot.save_session()
else:
    print("🔐 No Session Found. Normal Login Starting...")
    bot.login(username=USERNAME, password=PASSWORD)
    bot.save_session()

# ✅ Safe Delay to Avoid Detection
def safe_delay(count):
    delay = 20 + (5 * count)
    print(f"🕒 Sleeping for {delay} seconds to avoid detection...")
    time.sleep(delay)

# ✅ Safe DM Sending Function
def send_safe_dm(user, message, count):
    try:
        bot.send_message(message, [user])
        print(f"✅ Message sent to {user}")
        safe_delay(count)
    except Exception as e:
        print(f"❌ Error sending to {user}: {e}")

# ✅ Exclude GC Members from DM List
excluded_gc = ["SHANSKARI_BALAK 👻💯"]
users_to_message = ["user1", "user2", "user3", "SHANSKARI_BALAK 👻💯"]

# ✅ Filter GC Members
filtered_users = [user for user in users_to_message if user not in excluded_gc]

# ✅ Safe Daily Limit for DMs
MAX_DAILY_DMS = 30
DAILY_SLEEP_TIME = 86400  # 24 hours
count = 0

# ✅ Start Sending DMs
for user in filtered_users:
    if count < MAX_DAILY_DMS:
        send_safe_dm(user, "https://ig.me/j/AbadvPz94HkLPUro/", count)
        count += 1
    else:
        print("🎉 Daily DM limit reached, sleeping for 24 hours...")
        time.sleep(DAILY_SLEEP_TIME)
        count = 0
