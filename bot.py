from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired, LoginRequired, UserNotFound
import os
import base64
import json
import time
import random
from datetime import datetime, timedelta

# Configuration
EXCLUDED_GROUP = "SHANSKARI_BALAK👻💯"  # Your group to ignore
DM_LINK = "https://ig.me/j/AbadvPz94HkLPUro/"
TRACKING_FILE = "dm_tracking.json"
DAILY_DM_LIMIT = 30
DELAY_RANGE = (600, 1200)  # 10-20 minutes in seconds
BREAK_DURATION = 28800  # 8 hours in seconds

# Environment Variables
USERNAME = os.environ["USERNAME"]
PASSWORD = os.environ["PASSWORD"]
SESSION_DATA = os.environ.get("SESSION_DATA", "")

# Tracking system
def load_tracking():
    try:
        with open(TRACKING_FILE, "r") as f:
            data = json.load(f)
            # Convert old date format if needed
            if isinstance(data.get('last_reset'), str):
                data['last_reset'] = datetime.fromisoformat(data['last_reset'])
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {'sent_users': [], 'daily_count': 0, 'last_reset': datetime.now()}

def save_tracking(data):
    data['last_reset'] = data['last_reset'].isoformat()
    with open(TRACKING_FILE, "w") as f:
        json.dump(data, f)

def reset_daily_counter(data):
    if datetime.now() - data['last_reset'] >= timedelta(hours=24):
        data['daily_count'] = 0
        data['last_reset'] = datetime.now()
    return data

def is_user_eligible(user_id, data):
    return (
        user_id not in data['sent_users'] and
        data['daily_count'] < DAILY_DM_LIMIT
    )

# Bot functions
def is_private_user(user_id):
    try:
        user = bot.user_info(user_id)
        return user.is_private
    except UserNotFound:
        return True  # Skip if user not found
    except Exception:
        return False

def send_dm(user_id):
    try:
        bot.direct_send(DM_LINK, user_ids=[user_id])
        return True
    except Exception as e:
        print(f"DM Failed: {str(e)}")
        return False

def process_groups():
    tracking_data = load_tracking()
    tracking_data = reset_daily_counter(tracking_data)
    
    threads = bot.direct_threads()
    for thread in threads:
        if thread.is_group and thread.title != EXCLUDED_GROUP:
            messages = bot.direct_messages(thread_id=thread.id, amount=20)
            for msg in messages:
                if tracking_data['daily_count'] >= DAILY_DM_LIMIT:
                    print("Daily limit reached! Taking 8 hour break...")
                    time.sleep(BREAK_DURATION)
                    tracking_data = reset_daily_counter(load_tracking())
                    
                if msg.user_id != bot.user_id and is_user_eligible(msg.user_id, tracking_data):
                    if not is_private_user(msg.user_id):
                        if send_dm(msg.user_id):
                            tracking_data['sent_users'].append(msg.user_id)
                            tracking_data['daily_count'] += 1
                            save_tracking(tracking_data)
                            
                            delay = random.randint(*DELAY_RANGE)
                            print(f"Next DM in {delay//60} minutes...")
                            time.sleep(delay)

# Session handling (same as before)
def handle_session(client):
    try:
        if SESSION_DATA:
            decoded = base64.b64decode(SESSION_DATA)
            session_dict = json.loads(decoded)
            
            with open("temp_session.json", "w") as f:
                json.dump(session_dict, f)
            
            client.load_settings("temp_session.json")
            os.remove("temp_session.json")
            
            client.get_timeline_feed()
            print("✅ Session loaded!")
            return client
            
    except (LoginRequired, ChallengeRequired, Exception) as e:
        print(f"⚠️ Session error: {str(e)}")

    try:
        client.login(USERNAME, PASSWORD)
        new_session = client.get_settings()
        encoded = base64.b64encode(json.dumps(new_session).encode()).decode()
        print("\n" + "="*50)
        print("🚨 NEW SESSION_DATA:")
        print(encoded)
        print("="*50)
        return client
        
    except Exception as e:
        print(f"❌ Login failed: {str(e)}")
        return None

# Main execution
if __name__ == "__main__":
    bot = Client()
    authenticated_client = handle_session(bot)
    
    if authenticated_client:
        print("🤖 Bot started! Monitoring groups...")
        while True:
            process_groups()
            print("Cycling again in 1 hour...")
            time.sleep(3600)  # Check every hour
    else:
        print("❌ Bot failed to start")
