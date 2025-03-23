import os
import base64
import json
import shutil
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired

# 1. Environment Variables (Railway पर सेट करें)
USERNAME = os.environ["USERNAME"]  # Required
PASSWORD = os.environ["PASSWORD"]  # Required
SESSION_DATA = os.environ.get("SESSION_DATA", "")  # First run: Keep empty

# 2. Session Files Cleanup
def clear_sessions():
    if os.path.exists("session.json"):
        os.remove("session.json")
    print("✅ पुराने Sessions डिलीट किए गए")

# 3. Session Generation Logic
def generate_new_session():
    try:
        client = Client()
        
        # Login with Credentials
        client.login(USERNAME, PASSWORD)
        
        # Generate Session Data
        session_data = client.dump_settings()
        
        # Convert to Base64
        json_data = json.dumps(session_data, indent=2)
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
    # Initialize Client
    client = Client()
    
    # Decode and Load Session Data
    decoded = json.loads(base64.b64decode(SESSION_DATA))
    client.load_settings(decoded)
    
    # Force Login Check
    client.get_timeline_feed()
    print("✅ Session सफलतापूर्वक लोड हुआ!")
    
    # Example: Send DM
    # user_id = client.user_id_from_username("target_username")
    # client.direct_send("Hello from instagrapi!", user_ids=[user_id])
    
except (LoginRequired, ChallengeRequired) as e:
    print(f"❌ Session Expired: {str(e)}")
    print("❗ SESSION_DATA को रीसेट करके फिर से डिप्लॉय करें")
    exit(1)
except Exception as e:
    print(f"❌ अनजान एरर: {str(e)}")
    exit(1)
