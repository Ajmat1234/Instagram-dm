from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired
import json
import os
import base64



# Environment Variables (Set this in your environment or Railway.com)
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
SESSION_DATA = os.getenv("SESSION_DATA")

# User tracking system
def load_users():
    try:
        with open(TRACKING_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_user(user_id, last_mentioned):
    users = load_users()
    users[user_id] = last_mentioned.isoformat()  # Save time as string format
    with open(TRACKING_FILE, "w") as f:
        json.dump(users, f)

def should_welcome(user_id):
    users = load_users()
    if user_id not in users:
        return True
    last_mentioned = datetime.fromisoformat(users[user_id])
    return datetime.now() - last_mentioned > timedelta(hours=12)  # 12 hours gap

# Load session file from environment variable
def load_session_from_env():
    if SESSION_DATA:
        try:
            decoded_data = base64.b64decode(SESSION_DATA)
            with open("ig_session.json", "wb") as f:
                f.write(decoded_data)
            print("📝 Session file decoded aur save ho gaya.")
            return True
        except Exception as e:
            print(f"❌ SESSION_DATA decode nahi ho saka: {e}")
            return False
    return False

# Authentication code handler
def handle_challenge():
    challenge_url = bot.last_json.get("challenge", {}).get("api_path")
    if challenge_url:
        print(f"🔒 Challenge URL: {challenge_url}")
        code = input("Enter code here: ")  # Replace with actual code entry mechanism
        bot.challenge_resolve(challenge_url, code)
        print("✅ Challenge resolved, re-logging in...")
        bot.login(USERNAME, PASSWORD)
        bot.dump_settings("ig_session.json")

# Start bot function
def start_bot():
    global bot
    bot = Client()

    if load_session_from_env():  
        try:
            bot.load_settings("ig_session.json")
            print("✅ Logged in using session!")
        except:
            print("❌ Session load fail, manual login kar raha hoon...")
            bot.login(USERNAME, PASSWORD)
            bot.dump_settings("ig_session.json")  
    else:
        print("❌ Session nahi mila, manually login kar rahe hain...")
        bot.login(USERNAME, PASSWORD)
        bot.dump_settings("ig_session.json")  

    print(f"🚀 Bot started: {datetime.now().strftime('%d-%m-%Y %H:%M')}")
    forever_bot()

if __name__ == "__main__":
    start_bot()
