from instagrapi import Client
from flask import Flask, request
import json
from datetime import datetime, timedelta
import pytz
import os
import base64

app = Flask(__name__)

# Configuration
WELCOME_MSGS = [
    "Welcome @{username}, humein khushi hai ki aap hamare group mein shamil hue!",
    "Hello @{username}, aapka swagat hai, enjoy kijiye!"
]
TRACKING_FILE = "user_track.json"

# User tracking system
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

# Initialize instagrapi
bot = Client()

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
SESSION_DATA = os.getenv("SESSION_DATA")

def save_session_to_env():
    """Session ko base64 me encode karke environment variable me save karega"""
    with open("ig_session.json", "rb") as f:
        session_data = base64.b64encode(f.read()).decode()
    os.environ["SESSION_DATA"] = session_data
    print("✅ Session updated successfully in environment variable!")

def load_or_login():
    """Agar SESSION_DATA valid hai to load karega, warna login karke naya session save karega"""
    if SESSION_DATA:
        try:
            # Decode session data from base64
            session_bytes = base64.b64decode(SESSION_DATA)
            with open("ig_session.json", "wb") as f:
                f.write(session_bytes)

            # Load session from ig_session.json
            bot.load_settings("ig_session.json")
            print("✅ Session restored from environment variable.")
        except Exception as e:
            print(f"⚠️ Error loading session: {e}, logging in again...")
            auto_login_and_save()
    else:
        print("⚠️ No session found. Logging in...")
        auto_login_and_save()

def auto_login_and_save():
    """Agar session fail ho jaye to auto-login karke naya session save karega"""
    bot.login(username=USERNAME, password=PASSWORD)
    bot.dump_settings("ig_session.json")
    save_session_to_env()
    print("✅ New session created and saved to environment variable!")

# Load or login at startup
load_or_login()

def get_username(user_id):
    try:
        user = bot.user_info(user_id)
        return user.username
    except Exception:
        return "user"

# Flask endpoint to send message
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

# Flask endpoint to manually reset session
@app.route("/", methods=["GET"])
def home():
    return {"status": "success", "message": "Bot is running perfectly!"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
