from instabot import Bot
import os
import base64
import json
import time
import shutil

# ✅ Environment Variables
USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")
SESSION_DATA = os.environ.get("SESSION_DATA")

# ✅ Session Cleanup
if os.path.exists("config"):
    shutil.rmtree("config")
    print("🧹 पुराने session files साफ़ किए गए!")

# ✅ Bot Initialization
bot = Bot()

# ✅ Session Format Validator
def validate_session(session):
    required = {
        'cookie': ['ds_user', 'ds_user_id', 'csrftoken'],
        'mandatory_keys': ['uuid', 'device_settings', 'cookie']
    }
    
    # Check top-level keys
    for key in required['mandatory_keys']:
        if key not in session:
            raise ValueError(f"Missing key: {key}")
    
    # Check cookie keys
    for key in required['cookie']:
        if key not in session['cookie']:
            raise ValueError(f"Cookie में {key} missing")
    
    return True

# ✅ Session Handler
def handle_sessions():
    if SESSION_DATA:
        try:
            print("🔁 Session डिकोड कर रहे हैं...")
            decoded = json.loads(base64.b64decode(SESSION_DATA))
            
            # Validate format
            validate_session(decoded)
            
            # Save session file
            os.makedirs("config", exist_ok=True)
            session_file = f"config/{USERNAME}_uuid_and_cookie.json"
            
            with open(session_file, 'w') as f:
                json.dump(decoded, f, indent=2)
            
            print("✅ Session format valid!")
            
            # Login with session
            if bot.login(username=USERNAME, password=PASSWORD, use_cookie=True):
                print("🔄 Session से login सफल!")
                return True
                
        except Exception as e:
            print(f"❌ Session error: {str(e)}")
            return False
            
    # Fresh login
    print("🔐 नया login शुरू कर रहे हैं...")
    if bot.login(username=USERNAME, password=PASSWORD):
        # Get NEW session data
        new_session = bot.api.get_uuid_and_cookie()
        
        # Add required fields (new fix)
        new_session['cookie']['ds_user'] = USERNAME
        new_session['device_settings'] = bot.api.device_settings
        
        # Generate new session data
        encoded = base64.b64encode(json.dumps(new_session).encode()).decode()
        print(f"🆕 NEW_SESSION_DATA:\n{encoded}")
        return True
        
    return False

# ✅ Main Execution
if not handle_sessions():
    raise SystemExit("❌ Login असफल, स्क्रिप्ट बंद की जा रही है")

# ... (rest of the code same as previous)
