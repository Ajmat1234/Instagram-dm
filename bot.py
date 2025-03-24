from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired, LoginRequired, UserNotFound
import os
import json
import time
import random
import base64
from datetime import datetime, timedelta

# Configuration
EXCLUDED_GROUP = "SHANSKARI_BALAK👻💯"
DM_LINK = "https://ig.me/j/AbadvPz94HkLPUro/"
TRACKING_FILE = "dm_tracking.json"
DAILY_DM_LIMIT = 30
DELAY_RANGE = (600, 1200)  # 10-20 minutes
BREAK_DURATION = 28800  # 8 hours
CHECK_INTERVAL = 1800  # 30 minutes

# Environment Variables with fallback
USERNAME = os.environ.get("USERNAME", "tumhara_username")  # Apna username yahan daalo
PASSWORD = os.environ.get("PASSWORD", "tumhara_password")  # Apna password yahan daalo
SESSION_DATA = os.environ.get("SESSION_DATA", "eyJ1dWlkcyI6eyJwaG9uZV9pZCI6IjRjYzkwODJlLWU5NzctNDNhMi1hYmNlLTMyMWY4NjE4MTgyZCIsInV1aWQiOiIwMDI2NmE5NS1mM2U3LTRmYjEtYTg1Ny05ZTM5NmM4MjgwZmIiLCJjbGllbnRfc2Vzc2lvbl9pZCI6ImZkNTdkOTlmLTdiNmUtNDY2MC1hNTFmLTU0MDg2MDY4ZTEwYSIsImFkdmVydGlzaW5nX2lkIjoiYmM4YzMzODItOGI2YS00ZWNhLTliNTktNzM4NWI1NzhjNzkzIiwiYW5kcm9pZF9kZXZpY2VfaWQiOiJhbmRyb2lkLWJkM2MyYTNmMDAxY2JjMzEiLCJyZXF1ZXN0X2lkIjoiNWVmNWFmYTItZThhMC00N2JjLTlkNGEtMDAwMzA2YWJjMDM3IiwidHJheV9zZXNzaW9uX2lkIjoiNDg5ZWU2NGEtNGFlYS00OGQwLWFkMTUtNmRiZDEyYzNkZThkIn0sIm1pZCI6IlotQlJhQUFCQUFFOUc5TTZEcXlWZGNNU0E0QVciLCJpZ191X3J1ciI6bnVsbCwiaWdfd3d3X2NsYWltIjpudWxsLCJhdXRob3JpemF0aW9uX2RhdGEiOnsiZHNfdXNlcl9pZCI6IjU3MjU3Mzc3MDYzIiwic2Vzc2lvbmlkIjoiNTcyNTczNzcwNjMlM0E1aEx5NDFsYTJ2bEFWbCUzQTE3JTNBQVllQVdrY0owMDlmQ0F0YU9ocklvSFRCRGpjQ0dwTFR0YWl0OWR1akJnIn0sImNvb2tpZXMiOnt9LCJsYXN0X2xvZ2luIjoxNzQyNzU0MTYxLjk1NDc1NTgsImRldmljZV9zZXR0aW5ncyI6eyJhcHBfdmVyc2lvbiI6IjMxMi4wLjAuMjUuMTE5IiwiYW5kcm9pZF92ZXJzaW9uIjozNCwiYW5kcm9pZF9yZWxlYXNlIjoiMTQuMC4wIiwiZHBpIjoiNDgwZHBpIiwicmVzb2x1dGlvbiI6IjEwODB4MjQwMCIsIm1hbnVmYWN0dXJlciI6InNhbXN1bmciLCJkZXZpY2UiOiJTTVM5MThCIiwibW9kZWwiOiJHYWxheHkgUzIzIFVsdHJhIn0sInVzZXJfYWdlbnQiOiJJbnN0YWdyYW0gMjY5LjAuMC4xOC43NSBBbmRyb2lkICgyNi84LjAuMDsgNDgwZHBpOyAxMDgweDE5MjA7IE9uZVBsdXM7IDZUIERldjsgZGV2aXRyb247IHFjb207IGVuX1VTOzMxNDY2NTI1NikiLCJjb3VudHJ5IjoiVVMiLCJjb3VudHJ5X2NvZGUiOjEsImxvY2FsZSI6ImVuX1VTIiwidGltZXpvbmVfb2Zmc2V0IjotMTQ0MDB9")  # Tumhara base64 session data

# Tracking system
def load_tracking():
    try:
        with open(TRACKING_FILE, "r") as f:
            data = json.load(f)
            data['last_reset'] = datetime.fromisoformat(data['last_reset']) if isinstance(data.get('last_reset'), str) else datetime.now()
            return data
    except:
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
def is_private_user(bot, user_id):
    try:
        return bot.user_info(user_id).is_private
    except:
        return True

def send_dm(bot, user_id):
    try:
        bot.direct_send(DM_LINK, user_ids=[user_id])
        return True
    except Exception as e:
        print(f"DM Failed: {str(e)}")
        return False

def process_groups(bot):
    tracking_data = reset_daily_counter(load_tracking())
    
    while True:
        try:
            print(f"\n🌀 {datetime.now().strftime('%H:%M:%S')} - scanning...")
            threads = bot.direct_threads(amount=10)  # Check only 10 latest threads
            if threads is None:
                print("⚠️ No threads received from Instagram! Session might be expired.")
                return False  # Trigger session refresh

            for thread in threads:
                if thread is None:
                    print("⚠️ Skipping invalid thread!")
                    continue
                if not getattr(thread, 'is_group', False) or getattr(thread, 'title', '') == EXCLUDED_GROUP:
                    continue

                messages = bot.direct_messages(thread_id=thread.id, amount=5)
                if messages is None:
                    print(f"⚠️ No messages received for thread {thread.id}!")
                    continue

                for msg in messages:
                    if msg is None or getattr(msg, 'user_id', None) == bot.user_id:
                        continue

                    if tracking_data['daily_count'] >= DAILY_DM_LIMIT:
                        print("Daily limit reached! Taking 8 hour break...")
                        time.sleep(BREAK_DURATION)
                        tracking_data = reset_daily_counter(load_tracking())
                        break

                    user_id = getattr(msg, 'user_id', None)
                    if user_id and is_user_eligible(user_id, tracking_data) and not is_private_user(bot, user_id):
                        if send_dm(bot, user_id):
                            tracking_data['sent_users'].append(user_id)
                            tracking_data['daily_count'] += 1
                            save_tracking(tracking_data)
                            delay = random.randint(*DELAY_RANGE)
                            print(f"✅ DM sent to user {user_id}! Next DM in {delay//60} minutes...")
                            time.sleep(delay)

            break  # Exit inner loop after one scan

        except ChallengeRequired:
            print("🔒 Challenge detected, restarting in 5 minutes...")
            time.sleep(300)
            return False
        except Exception as e:
            print(f"⚠️ Error: {str(e)}")
            time.sleep(300)
            return False

# Session handling with refresh option
def handle_session(client, force_login=False):
    if not force_login:
        try:
            if SESSION_DATA:
                session_json = base64.b64decode(SESSION_DATA).decode('utf-8')
                session_dict = json.loads(session_json)
                client.set_settings(session_dict)
                client.get_timeline_feed()
                print("✅ Session loaded from ENV!")
                return client
        except Exception as e:
            print(f"⚠️ Session error: {str(e)}")
    
    try:
        client.login(USERNAME, PASSWORD)
        print("✅ Logged in successfully!")
        return client
    except Exception as e:
        print(f"❌ Login failed: {str(e)}")
        return None

# Main execution
if __name__ == "__main__":
    bot = Client()
    bot_instance = handle_session(bot)
    
    if bot_instance:
        print("🤖 Bot started! Monitoring groups...")
        while True:
            if not process_groups(bot_instance):
                print("⚠️ Session issue detected, attempting to refresh...")
                bot_instance = handle_session(bot, force_login=True)
                if not bot_instance:
                    print("❌ Bot failed to restart, exiting...")
                    break
            print("Next check in 30 minutes...")
            time.sleep(CHECK_INTERVAL)
    else:
        print("❌ Bot failed to start")
