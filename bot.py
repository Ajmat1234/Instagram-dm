from instabot import Bot
import time
import os
import base64

# ✅ Environment Variables from Railway.com
USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")
SESSION_DATA = os.environ.get("SESSION_DATA")

# ✅ Bot Initialization
bot = Bot()

# ✅ Check if SESSION_DATA is Available
if SESSION_DATA:
    print("🔁 Restoring Session from Base64...")
    decoded_session = base64.b64decode(SESSION_DATA).decode()

    # ✅ Session ko config folder me save karo
    session_file_path = "config/{}_uuid_and_cookie.json".format(USERNAME)
    with open(session_file_path, "w") as file:
        file.write(decoded_session)
    
    # ✅ Bot ko session se login karao
    bot.load_session()
    print("✅ Session Restored Successfully!")
else:
    # ✅ Agar session nahi hai to normal login karo
    print("🔐 No Session Found, Logging in Normally...")
    bot.login(username=USERNAME, password=PASSWORD)
    bot.save_session()
    print("✅ New Session Saved Successfully!")

# ✅ Safe Delay Setup to Avoid Detection
def safe_delay(count):
    delay = 20 + (5 * count)
    print(f"🕒 Sleeping for {delay} seconds to avoid detection...")
    time.sleep(delay)

# ✅ DM Sending Function with Safety Checks
def send_safe_dm(user, message, count):
    try:
        # ✅ Check if User is Valid
        if bot.get_user_info(user)["is_private"] == False:  # Public Accounts Only
            bot.send_message(message, [user])
            print(f"✅ Message sent to {user}")
            safe_delay(count)
        else:
            print(f"🔒 Skipping {user} (Private Account)")
    except Exception as e:
        print(f"❌ Error sending to {user}: {e}")

# ✅ Exclude GC Members from DM List
excluded_gc = ["SHANSKARI_BALAK 👻💯"]  # Members ko DM mat bhejo

# ✅ Target Users List (Add Your Target Usernames Here)
users_to_message = ["user1", "user2", "user3", "SHANSKARI_BALAK 👻💯"]

# ✅ Filtered User List (Excluding GC Members)
filtered_users = [user for user in users_to_message if user not in excluded_gc]

# ✅ Safe Daily Limit for DMs
MAX_DAILY_DMS = 30
DAILY_SLEEP_TIME = 86400  # 24 hours sleep after limit
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
