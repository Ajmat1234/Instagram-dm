from instabot import Bot
import base64
import json
import os

# ✅ Environment Variables from Railway
USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")
SESSION_DATA = os.environ.get("SESSION_DATA")

# ✅ Bot Init
bot = Bot()

# ✅ Session Restore Logic
if SESSION_DATA:
    print("🔁 Restoring Session from Base64...")
    decoded_session = base64.b64decode(SESSION_DATA).decode()
    
    # ✅ Session Ko Config Folder Me Save Karo
    session_file_path = "config/{}_uuid_and_cookie.json".format(USERNAME)
    os.makedirs("config", exist_ok=True)
    
    # ✅ Write Correct Format
    with open(session_file_path, "w") as file:
        file.write(decoded_session)
    
    # ✅ Login Using Restored Session
    if bot.login(username=USERNAME, password=PASSWORD, use_cookie=True):
        print("✅ Session Restored Successfully!")
    else:
        print("❌ Session Restore Failed. Normal Login Attempting...")
        bot.login(username=USERNAME, password=PASSWORD)
        bot.save_session()
else:
    print("🔐 No Session Found. Normal Login Starting...")
    bot.login(username=USERNAME, password=PASSWORD)
    bot.save_session()
