from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired, LoginRequired, UserNotFound
from instagrapi.extractors import extract_user_short
from instagrapi.types import DirectThread
import instagrapi.extractors
import os
import json
import time
import random
import base64
from datetime import datetime, timedelta

# Enhanced monkey patch for thread extraction
def patched_extract_direct_thread(data: dict) -> DirectThread:
    # Handle None and invalid inviter data
    inviter_data = data.get("inviter") or {}
    if inviter_data is None or not isinstance(inviter_data, dict):
        inviter_data = {}

    # Advanced user data cleaning
    def clean_users(users):
        return [u for u in users if isinstance(u, dict) and u.get("pk") or u.get("id")]
    
    users = clean_users(data.get("users", []))
    left_users = clean_users(data.get("left_users", []))
    
    # Safe user extraction with fallback
    def safe_extract(user):
        try:
            return extract_user_short(user)
        except:
            return None
    
    return DirectThread(
        id=data.get("id"),
        name=data.get("thread_title"),
        users=[u for u in (safe_extract(user) for user in users) if u],
        left_users=[u for u in (safe_extract(user) for user in left_users) if u],
        admin_user_ids=data.get("admin_user_ids", []),
        items=data.get("items"),
        last_activity_at=data.get("last_activity_at"),
        muted=data.get("muted"),
        is_pin=data.get("is_pin"),
        named=data.get("named"),
        canonical=data.get("canonical"),
        pending=data.get("pending"),
        archived=data.get("archived"),
        thread_type=data.get("thread_type"),
        viewer_id=data.get("viewer_id"),
        thread_has_older=data.get("thread_has_older"),
        thread_has_newer=data.get("thread_has_newer"),
        newest_cursor=data.get("newest_cursor"),
        oldest_cursor=data.get("oldest_cursor"),
        is_spam=data.get("is_spam"),
        last_seen_at=data.get("last_seen_at"),
        inviter=safe_extract(inviter_data) if inviter_data else None,
    )

instagrapi.extractors.extract_direct_thread = patched_extract_direct_thread

# ... [बाकी कोड वैसा ही रखें जो पिछले संदेश में था] 

# Configuration
EXCLUDED_GROUP = "SHANSKARI_BALAK👻💯"
DM_LINK = "https://ig.me/j/AbadvPz94HkLPUro/"
TRACKING_FILE = "dm_tracking.json"
DAILY_DM_LIMIT = 30
DELAY_RANGE = (600, 1200)
BREAK_DURATION = 28800

# Environment Variables
USERNAME = os.environ["USERNAME"]
PASSWORD = os.environ["PASSWORD"]
SESSION_DATA = os.environ.get("SESSION_DATA", "")

# Tracking system
def load_tracking():
    try:
        with open(TRACKING_FILE, "r") as f:
            data = json.load(f)
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
    return user_id not in data['sent_users'] and data['daily_count'] < DAILY_DM_LIMIT

# Bot functions
def is_private_user(user_id):
    try:
        user = bot.user_info(user_id)
        return user.is_private
    except UserNotFound:
        return True
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

# Fixed session handling
def handle_session(client):
    try:
        if SESSION_DATA:
            # Decode and save to temp file
            decoded = base64.b64decode(SESSION_DATA)
            session_dict = json.loads(decoded)
            
            with open("temp_session.json", "w") as f:
                json.dump(session_dict, f)
            
            client.load_settings("temp_session.json")
            os.remove("temp_session.json")
            
            client.get_timeline_feed()
            print("✅ Session loaded successfully!")
            return client
    except Exception as e:
        print(f"⚠️ Session error: {str(e)}")
    
    # Manual login if session fails
    try:
        print("Attempting manual login...")
        client.login(USERNAME, PASSWORD)
        print("✅ Manual login successful!")
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
            try:
                process_groups()
                print("Cycling again in 1 hour...")
                time.sleep(3600)
            except Exception as e:
                print(f"⚠️ Critical error: {str(e)}")
                print("Restarting bot in 5 minutes...")
                time.sleep(300)
    else:
        print("❌ Bot failed to start")
