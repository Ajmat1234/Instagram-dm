from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired, LoginRequired
import os
import base64
import json

# Environment Variables
USERNAME = os.environ["USERNAME"]
PASSWORD = os.environ["PASSWORD"]
SESSION_DATA = os.environ.get("SESSION_DATA", "")

def handle_session(client):
    """Secure session management with auto-renewal"""
    try:
        if SESSION_DATA:
            # Decode base64 to session dictionary
            decoded = base64.b64decode(SESSION_DATA)
            session_dict = json.loads(decoded)
            
            # Temporary file for loading session
            with open("temp_session.json", "w") as f:
                json.dump(session_dict, f)
            
            client.load_settings("temp_session.json")
            os.remove("temp_session.json")
            
            # Validate session
            client.get_timeline_feed()
            print("✅ Existing session loaded successfully!")
            return client
            
    except (LoginRequired, ChallengeRequired, Exception) as e:
        print(f"⚠️ Session error: {str(e)}")

    # New login attempt
    try:
        client.login(USERNAME, PASSWORD)
        
        # Generate and print new session
        new_session = client.get_settings()
        encoded = base64.b64encode(
            json.dumps(new_session).encode()
        ).decode()
        
        print("\n" + "="*50)
        print("🚨 NEW SESSION_DATA (Copy this to ENV):")
        print(encoded)
        print("="*50)
        
        return client
        
    except Exception as e:
        print(f"❌ Login failed: {str(e)}")
        return None

if __name__ == "__main__":
    # Initialize client
    bot = Client()
    
    # Authentication flow
    authenticated_client = handle_session(bot)
    
    if authenticated_client:
        print("🤖 Authentication successful! Add your functions here")
        # Add your custom functions after this line
        
    else:
        print("❌ Bot failed to start")
