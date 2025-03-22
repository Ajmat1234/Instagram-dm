from instabot import Bot
import os
import base64
import json
import shutil
import uuid

# 1. Environment Variables
USERNAME = os.environ["USERNAME"]
PASSWORD = os.environ["PASSWORD"]
SESSION_DATA = os.environ.get("SESSION_DATA", "")

# 2. Session Management
def clear_old_sessions():
    if os.path.exists("config"):
        shutil.rmtree("config")
    print("✅ पुराने sessions साफ़ किए गए")

# 3. New Session Generator
def create_fresh_session():
    try:
        bot = Bot()
        if not bot.login(username=USERNAME, password=PASSWORD):
            raise Exception("Login Failed: Wrong Credentials")
        
        # Generate New Session Data
        session = {
            "uuid": str(uuid.uuid4()),
            "cookie": bot.api.cookie_jar.get_cookies_dict(),
            "device_settings": bot.api.device_settings
        }
        
        # Add Critical Fields
        session["cookie"]["ds_user"] = USERNAME
        session["cookie"]["ds_user_id"] = str(bot.user_id)
        session["cookie"]["csrftoken"] = bot.api.token
        
        # Encode for Railway
        json_data = json.dumps(session, indent=2)
        encoded = base64.urlsafe_b64encode(json_data.encode()).decode()
        
        print("\n" + "🚨🚨🚨 COPY BELOW SESSION_DATA 🚨🚨🚨")
        print(encoded)
        print("🚨🚨🚨 PASTE IN RAILWAY ENV VARIABLES 🚨🚨🚨\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

# 4. Main Execution Flow
if __name__ == "__main__":
    clear_old_sessions()
    
    if not SESSION_DATA.strip():
        print("🆕 नया Session बनाया जा रहा है...")
        if create_fresh_session():
            exit(0)  # First run complete
        else:
            exit(1)
    
    try:
        # Session Restore Logic
        decoded = json.loads(base64.b64decode(SESSION_DATA))
        bot = Bot()
        
        # Manual Session Injection
        bot.api.uuid = decoded["uuid"]
        bot.api.cookie_jar = decoded["cookie"]
        bot.api.device_settings = decoded["device_settings"]
        
        print("✅ Session Restore Successful!")
        
        # DM Sending Code
        targets = ["user1", "user2", "user3"]
        for user in targets:
            bot.send_message("Your message", [user])
            print(f"Sent to {user}")
            time.sleep(30)
            
    except Exception as e:
        print(f"❌ Session Error: {str(e)}")
        print("🔄 कृपया SESSION_DATA हटाकर फिर से डिप्लॉय करें")
        exit(1)
