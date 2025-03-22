from instabot import Bot
import os
import base64
import json
import shutil
import uuid

# 1. Environment Variables (Railway पर सेट करें)
USERNAME = os.environ["USERNAME"]  # Required
PASSWORD = os.environ["PASSWORD"]  # Required
SESSION_DATA = os.environ.get("SESSION_DATA", "")  # First run: Keep empty

# 2. Session Files Cleanup
def clear_sessions():
    if os.path.exists("config"):
        shutil.rmtree("config")
    print("✅ पुराने Sessions डिलीट किए गए")

# 3. Session Generation Logic
def generate_new_session():
    try:
        bot = Bot()
        if not bot.login(username=USERNAME, password=PASSWORD):
            raise Exception("Login Failed: Check Credentials")
        
        # Generate New Session Data
        session = {
            "uuid": str(uuid.uuid4()),
            "cookie": bot.api.cookie_jar.get_cookies_dict(),
            "device_settings": bot.api.device_settings
        }
        
        # Add Required Fields
        session["cookie"]["ds_user"] = USERNAME
        session["cookie"]["ds_user_id"] = str(bot.user_id)
        session["cookie"]["csrftoken"] = bot.api.token
        
        # Convert to Base64
        json_data = json.dumps(session, indent=2)
        encoded = base64.urlsafe_b64encode(json_data.encode()).decode()
        
        # Print for Railway Logs
        print("\n" + "="*50)
        print("🚨 COPY BELOW SESSION_DATA AND PASTE IN RAILWAY ENV VARIABLES 🚨")
        print(encoded)
        print("="*50 + "\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Critical Error: {str(e)}")
        return False

# 4. Main Execution
clear_sessions()

if not SESSION_DATA.strip():
    print("🆕 नया Session बनाया जा रहा है...")
    if generate_new_session():
        print("❗ Railway Dashboard पर जाएं → Environment Variables → SESSION_DATA सेट करें")
    else:
        print("❌ Session बनाने में असफल! Instagram ID/Password जाँचें")
    exit(0)

try:
    # Decode Session Data
    decoded = json.loads(base64.b64decode(SESSION_DATA))
    
    # Manual Session Injection
    bot = Bot()
    bot.api.uuid = decoded["uuid"]
    bot.api.cookie_jar = decoded["cookie"]
    bot.api.device_settings = decoded["device_settings"]
    
    print("✅ Session सफलतापूर्वक लोड हुआ!")
    
    # Your DM Logic Here
    # bot.send_message(...)
    
except Exception as e:
    print(f"❌ Session Error: {str(e)}")
    print("❗ SESSION_DATA गलत है! इसे हटाकर फिर से डिप्लॉय करें")
    exit(1)
