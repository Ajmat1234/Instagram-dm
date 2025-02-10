from instagrapi import Client
import json
import time
import random
import os
import base64

# 🔑 Instagram Login Credentials (use encoded session)
SESSION_JSON = os.environ.get('SESSION_JSON')  # Environment variable se session load karein

# 🎯 Targeting Settings
DM_MESSAGES = [
    "Hi!", "Hello!", "Hey there!", "What's up?", "Good morning!"
]
DM_LIMIT = 10  # Ek baar me max 10 DMs
REST_TIME = 3 * 60 * 60  # 3 ghante ka rest
START_TIME = 0  # Koi bhi time limit nahi hai
END_TIME = 23  # Bot kabhi bhi kaam karega
SEND_DM_INTERVAL = 60  # 1 minute ka gap between DMs

# 🚀 Login Function
def login():
    cl = Client()

    # Decode Base64 session if available
    if SESSION_JSON:
        decoded_session = base64.b64decode(SESSION_JSON).decode('utf-8')
        session_data = json.loads(decoded_session)
        cl.set_settings(session_data)
        try:
            cl.login(session_data['username'], session_data['password'])
        except:
            print("⚠️ Session expired, logging in again...")
            cl.login(session_data['username'], session_data['password'])
            cl.dump_settings("session.json")
    else:
        print("⚠️ No session found, logging in...")
        USERNAME = "zehra.bloom_"
        PASSWORD = "Ajmat1234@"
        cl.login(USERNAME, PASSWORD)
        cl.dump_settings("session.json")
    
    return cl

# 📌 Function to Get Target Users from Feed Reels Comments + Suggestions
def get_target_users(cl):
    target_users = set()
    
    # ✅ 1. **Tumhare Feed me Jo Reels Aati Hain, Unke Comments se Ladkiyon ke Usernames Lega**
    feed_reels = cl.user_feed(cl.user_id, amount=10)  # Tumhare feed ke 10 latest reels
    for reel in feed_reels:
        try:
            comments = cl.media_comments(reel.id, amount=50)  # Har reel ke 50 comments check karega
            for comment in comments:
                if "girl" in comment.user.username.lower() or "queen" in comment.user.username.lower() or comment.user.username.endswith("a"):
                    target_users.add(comment.user.username)
        except:
            pass
    
    # ✅ 2. **Suggested Users Se Bhi Ladkiyon Ko Target Karega**
    suggested_users = cl.user_following(cl.user_id)
    for user in suggested_users:
        if "girl" in user.username.lower() or "queen" in user.username.lower() or user.username.endswith("a"):
            target_users.add(user.username)

    return list(target_users)

# ✉️ Function to Send DMs
def send_dm(cl, user):
    try:
        message = random.choice(DM_MESSAGES)  # Random message select karega
        cl.direct_send(message, [cl.user_id_from_username(user)])
        print(f"✅ Message sent to {user}")
        return True
    except:
        print(f"❌ DM failed for {user}")
        return False

# 🔄 Main Bot Function
def bot():
    cl = login()
    
    while True:
        target_users = get_target_users(cl)
        success_count = 0
        
        for user in target_users:
            if success_count >= DM_LIMIT:
                print(f"⚠️ DM limit {DM_LIMIT} reached, resting for {REST_TIME} seconds...")
                time.sleep(REST_TIME)
                success_count = 0  # Reset count after rest
                
            if send_dm(cl, user):
                success_count += 1
            
            time.sleep(SEND_DM_INTERVAL)  # Ek minute ka gap between DMs
        
        print(f"🔄 Next cycle start hoga 3 ghante ke baad...")
        time.sleep(REST_TIME)

# 🚀 Start the bot
if __name__ == "__main__":
    bot()
