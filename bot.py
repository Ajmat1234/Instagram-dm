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
    print("🧹 पुराने session files साफ़ किए गए!")

# ✅ Bot Initialization
bot = Bot()

# ✅ Base64 Decoding Fix
def safe_b64decode(data):
    try:
        # Add missing padding
        missing_padding = len(data) % 4
        if missing_padding:
            data += '=' * (4 - missing_padding)
        return base64.urlsafe_b64decode(data)
    except Exception as e:
        raise ValueError(f"Base64 डिकोडिंग में समस्या: {str(e)}")

# ✅ Session Validator
def validate_session(data):
    required = {
        "top": ["uuid", "cookie", "device_settings"],
        "cookie": ["ds_user", "ds_user_id", "csrftoken", "sessionid"]
    }
    
    for key in required["top"]:
        if key not in data:
            raise KeyError(f"Missing key: {key}")
    
    for key in required["cookie"]:
        if key not in data["cookie"]:
            raise KeyError(f"Cookie में {key} गायब है")

# ✅ Session Handler (Fully Fixed)
def handle_sessions():
    if SESSION_DATA:
        try:
            print("🔍 Session डिकोडिंग शुरू...")
            
            # Step 1: Base64 Decode
            decoded_bytes = safe_b64decode(SESSION_DATA)
            
            # Step 2: Convert to JSON
            decoded_str = decoded_bytes.decode('utf-8').strip()
            if not decoded_str:
                raise ValueError("खाली JSON डेटा")
                
            session_data = json.loads(decoded_str)
            
            # Step 3: Validate Structure
            validate_session(session_data)
            
            # Step 4: Save to File
            os.makedirs("config", exist_ok=True)
            with open(f"config/{USERNAME}_uuid_and_cookie.json", "w") as f:
                json.dump(session_data, f, indent=2)
                
            # Step 5: Manual Session Injection
            bot.api.uuid = session_data["uuid"]
            bot.api.cookie_jar = session_data["cookie"]
            bot.api.device_settings = session_data["device_settings"]
            
            print("✅ Session सफलतापूर्वक लोड हुआ!")
            return True
            
        except Exception as e:
            print(f"❌ गंभीर Session त्रुटि: {str(e)}")
            print(f"💡 DEBUG: Raw Session Data: {SESSION_DATA[:50]}...")
            return False

    # Fresh Login Flow
    print("🔐 नया लॉगिन प्रक्रिया शुरू...")
    if bot.login(username=USERNAME, password=PASSWORD):
        # Generate New Session
        new_uuid = str(uuid.uuid4())
        new_session = {
            "uuid": new_uuid,
            "cookie": bot.api.cookie_jar.get_cookies_dict(),
            "device_settings": bot.api.device_settings
        }
        
        # Add Critical Fields
        new_session["cookie"]["ds_user"] = USERNAME
        new_session["cookie"]["ds_user_id"] = str(bot.user_id)
        new_session["cookie"]["csrftoken"] = bot.api.token
        
        # Encode and Save
        json_str = json.dumps(new_session, indent=2)
        encoded = base64.urlsafe_b64encode(json_str.encode()).decode()
        print(f"🆕 NEW_SESSION_DATA:\n{encoded}")
        
        return True
        
    return False

# ✅ Main Execution
if not handle_sessions():
    raise SystemExit("❌ लॉगिन विफल, स्क्रिप्ट बंद")

# ✅ DM Configuration
TARGETS = [u for u in ["user1", "user2", "user3"] if u != "SHANSKARI_BALAK 👻💯"]
MESSAGE = "https://ig.me/j/AbadvPz94HkLPUro/"

# ✅ Smart Sending
for i, user in enumerate(TARGETS):
    try:
        bot.send_message(MESSAGE, [user])
        print(f"✓ {i+1}/{len(TARGETS)}: {user} को भेजा गया")
        time.sleep(30 + (i * 5))  # Progressive delay
    except Exception as e:
        print(f"✗ {user} में त्रुटि: {str(e)}")
        time.sleep(120)

print("🎉 सभी संदेश सफलतापूर्वक भेजे गए!")
