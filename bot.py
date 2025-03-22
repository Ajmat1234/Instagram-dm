from instabot import Bot
import os
import base64
import json
import time
import shutil
import uuid

# ✅ Environment Variables
USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")
SESSION_DATA = os.environ.get("SESSION_DATA")

# ✅ Session Cleanup
if os.path.exists("config"):
    shutil.rmtree("config")
    print("🧹 पुराने session files डिलीट किए गए!")

# ✅ Bot Initialization
bot = Bot()

# ✅ Session Generator (New Fix)
def generate_new_session():
    print("🔄 नया session बना रहे हैं...")
    
    # Generate fresh UUID
    new_uuid = str(uuid.uuid4())
    
    # Get device settings from API
    device_settings = {
        "app_version": "267.0.0.19.301",
        "android_version": 33,
        "android_release": "13.0.0",
        "phone_manufacturer": "OnePlus",
        "phone_device": "NE2215",
        "phone_dpi": "420dpi",
        "phone_resolution": "1080x2260",
        "phone_chipset": "Snapdragon 8 Gen 1"
    }
    
    # Create complete session structure
    new_session = {
        "uuid": new_uuid,
        "cookie": bot.api.cookie_jar.get_cookies_dict(),
        "device_settings": device_settings
    }
    
    # Add mandatory Instagram fields
    new_session['cookie']['ds_user'] = USERNAME
    new_session['cookie']['ds_user_id'] = bot.user_id
    new_session['cookie']['csrftoken'] = bot.api.token
    
    return new_session

# ✅ Session Validation
def validate_session(data):
    required_keys = ['uuid', 'cookie', 'device_settings']
    for key in required_keys:
        if key not in data:
            raise ValueError(f"Missing key: {key}")
    
    cookie_keys = ['ds_user', 'ds_user_id', 'csrftoken']
    for key in cookie_keys:
        if key not in data['cookie']:
            raise ValueError(f"Cookie में {key} missing")

# ✅ Session Handler
def handle_sessions():
    if SESSION_DATA:
        try:
            print("🔁 Session डिकोड कर रहे हैं...")
            decoded = json.loads(base64.b64decode(SESSION_DATA))
            validate_session(decoded)
            
            # Save session file
            os.makedirs("config", exist_ok=True)
            with open(f"config/{USERNAME}_uuid_and_cookie.json", "w") as f:
                json.dump(decoded, f, indent=2)
            
            # Force reload session
            bot.api.uuid = decoded['uuid']
            bot.api.device_settings = decoded['device_settings']
            bot.api.set_cookies(decoded['cookie'])
            
            print("✅ Session restore successful!")
            return True
            
        except Exception as e:
            print(f"❌ Session error: {str(e)}")
            return False
            
    # Fresh login flow
    if bot.login(username=USERNAME, password=PASSWORD):
        new_session = generate_new_session()
        
        # Save and encode session
        encoded = base64.b64encode(json.dumps(new_session).encode()).decode()
        print(f"🆕 NEW_SESSION_DATA:\n{encoded}")
        
        # Save locally for next run
        with open(f"config/{USERNAME}_uuid_and_cookie.json", "w") as f:
            json.dump(new_session, f)
            
        return True
        
    return False

# ✅ Main Execution
if not handle_sessions():
    raise SystemExit("❌ Login failed, stopping script")

# ... (बाकी का कोड पहले जैसा ही रहेगा)
