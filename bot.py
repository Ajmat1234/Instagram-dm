from instabot import Bot
import os
import base64
import json
import shutil
import uuid
import sys

# 1. Environment Variables (Railway पर सेट करें)
USERNAME = os.environ["USERNAME"]
PASSWORD = os.environ["PASSWORD"]
SESSION_DATA = os.environ.get("SESSION_DATA", "")

# 2. Session Files साफ़ करें
def clear_sessions():
    if os.path.exists("config"):
        shutil.rmtree("config")
    print("✅ पुराने Sessions डिलीट किए गए")

# 3. नया Session बनाएँ
def generate_session():
    try:
        bot = Bot()
        if not bot.login(username=USERNAME, password=PASSWORD):
            raise Exception("❌ Instagram Login Failed! क्रेडेंशियल्स जाँचें")
        
        # Session Data तैयार करें
        session = {
            "uuid": str(uuid.uuid4()),
            "cookie": bot.api.cookie_jar.get_cookies_dict(),
            "device_settings": bot.api.device_settings
        }
        
        # Important Fields जोड़ें
        session["cookie"]["ds_user"] = USERNAME
        session["cookie"]["ds_user_id"] = str(bot.user_id)
        session["cookie"]["csrftoken"] = bot.api.token
        
        # Base64 में Encode करें
        json_data = json.dumps(session, indent=2)
        encoded = base64.urlsafe_b64encode(json_data.encode()).decode()
        
        # Railway Logs में दिखाएँ
        print("\n" + "="*50)
        print("🚨 COPY BELOW SESSION_DATA FOR RAILWAY 🚨")
        print(encoded)
        print("="*50 + "\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

# 4. Main Function
if __name__ == "__main__":
    clear_sessions()
    
    if not SESSION_DATA.strip():
        print("🆕 नया Session बनाया जा रहा है...")
        if generate_session():
            sys.exit(0)  # First Run Complete
        else:
            sys.exit(1)
    
    try:
        # Existing Session Restore
        decoded = json.loads(base64.b64decode(SESSION_DATA))
        bot = Bot()
        
        # Manual Session Load
        bot.api.uuid = decoded["uuid"]
        bot.api.cookie_jar = decoded["cookie"]
        bot.api.device_settings = decoded["device_settings"]
        
        print("✅ Session Restore Successful!")
        
        # DM भेजने का कोड
        # ... (अपना DM Logic यहाँ जोड़ें)
        
    except Exception as e:
        print(f"❌ Session Error: {str(e)}")
        print("❗ SESSION_DATA गलत है! इसे हटाकर फिर से डिप्लॉय करें")
        sys.exit(1)
