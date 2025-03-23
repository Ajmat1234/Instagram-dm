import os
import base64
import json
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired

# ENV वेरिएबल्स
USERNAME = os.environ["USERNAME"]
PASSWORD = os.environ["PASSWORD"]
SESSION_DATA = os.environ.get("SESSION_DATA", "")

def safe_login():
    client = Client()
    
    # पहले से मौजूद session_data चेक करें
    if SESSION_DATA:
        try:
            # Base64 डेटा को डिक्शनरी में कन्वर्ट करें
            decoded_data = base64.b64decode(SESSION_DATA).decode()
            session_dict = json.loads(decoded_data)
            
            # सीधे डिक्शनरी से सेटिंग्स लोड करें
            client.load_settings(session_dict)
            
            # सेशन वैलिडेट करें
            client.get_timeline_feed()
            print("✅ पुराने सेशन से लॉगिन सफल!")
            return client
            
        except (LoginRequired, ChallengeRequired, json.JSONDecodeError):
            print("⚠️ सेशन एक्सपायर, नया लॉगिन कर रहा हूं...")

    # नया लॉगिन अटेम्प्ट
    try:
        client.login(USERNAME, PASSWORD)
        
        # नया session_data जनरेट करें
        new_session = client.get_settings()
        encoded_session = base64.b64encode(
            json.dumps(new_session).encode()
        ).decode()
        
        print("\n" + "="*50)
        print("🚨 नया SESSION_DATA कॉपी करें:")
        print(encoded_session)
        print("="*50)
        
        return client
        
    except Exception as e:
        print(f"❌ गंभीर एरर: {str(e)}")
        return None

# मुख्य एक्जीक्यूशन
if __name__ == "__main__":
    client = safe_login()
    
    if client:
        # यहां अपना मुख्य कोड लिखें
        print("🤖 बॉट सफलतापूर्वक चालू हुआ!")
        # उदाहरण: client.direct_send("हैलो!", user_ids=[...])
    else:
        print("❌ बॉट स्टार्ट नहीं हो पाया")
