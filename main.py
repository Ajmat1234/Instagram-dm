from instagrapi import Client
from flask import Flask, request
import json
from datetime import datetime, timedelta
import pytz
import os
import base64

app = Flask(__name__)

WELCOME_MSGS = [
    "Welcome @{username}, humein khushi hai ki aap hamare group mein shamil hue!",
    "Hello @{username}, aapka swagat hai, enjoy kijiye!"
]
TRACKING_FILE = "user_track.json"

def load_users():
    try:
        with open(TRACKING_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_user(user_id, last_mentioned):
    users = load_users()
    users[user_id] = last_mentioned.isoformat()
    with open(TRACKING_FILE, "w") as f:
        json.dump(users, f)

def should_welcome(user_id):
    users = load_users()
    if user_id not in users:
        return True
    last_mentioned = datetime.fromisoformat(users[user_id])
    return datetime.now(pytz.utc) - last_mentioned > timedelta(hours=24)

bot = Client()

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
SESSION_DATA = os.getenv("SESSION_DATA")

def save_session_to_env():
    with open("ig_session.json", "rb") as f:
        session_data = base64.b64encode(f.read()).decode()
    os.environ["SESSION_DATA"] = session_data
    print("✅ Session updated successfully in environment variable!")

def load_or_login():
    if SESSION_DATA:
        try:
            session_bytes = base64.b64decode(SESSION_DATA)
            with open("ig_session.json", "wb") as f:
                f.write(session_bytes)
            bot.load_settings("ig_session.json")
            print("✅ Session restored from environment variable.")
        except Exception as e:
            print(f"⚠️ Error loading session: {e}, logging in again...")
            auto_login_and_save()
    else:
        print("⚠️ No session found. Logging in...")
        auto_login_and_save()

def auto_login_and_save():
    bot.login(username=USERNAME, password=PASSWORD)
    bot.dump_settings("ig_session.json")
    save_session_to_env()
    print("✅ New session created and saved to environment variable!")

load_or_login()

def get_username(user_id):
    try:
        user = bot.user_info(user_id)
        return user.username
    except Exception:
        return "user"

@app.route("/send_message", methods=["POST"])
def send_message():
    data = request.json
    user_id = data.get("user_id")
    thread_id = data.get("thread_id")

    if not user_id or not thread_id:
        return {"status": "error", "message": "Missing user_id or thread_id"}

    if should_welcome(user_id):
        username = get_username(user_id)
        welcome_msg = random.choice(WELCOME_MSGS).format(username=username)
        bot.direct_answer(thread_id=thread_id, text=welcome_msg)
        save_user(user_id, datetime.now(pytz.utc))
        print(f"👋 Sent to @{username}: {welcome_msg}")
        return {"status": "success", "message": f"Sent to {username}"}
    else:
        return {"status": "skipped", "message": "User already welcomed"}

@app.route("/", methods=["GET"])
def home():
    return {"status": "success", "message": "Bot is running perfectly!"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render के PORT को लें
    app.run(host='0.0.0.0', port=port)  # Hardcoded 5000 हटाएं
