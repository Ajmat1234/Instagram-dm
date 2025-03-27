from instagrapi import Client
from flask import Flask, request
import json
from datetime import datetime, timedelta
import pytz
import os

app = Flask(__name__)

# Configuration
WELCOME_MSGS = [
    "Welcome @{username}, humein khushi hai ki aap hamare group mein shamil hue!",
    "Hello @{username}, aapka swagat hai, enjoy kijiye!"
]
TRACKING_FILE = "user_track.json"
SESSION_FILE = "/var/data/ig_session.json"

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

# Load session if available
if os.path.exists(SESSION_FILE):
    bot.load_settings(SESSION_FILE)
else:
    bot.login(username=USERNAME, password=PASSWORD)
    bot.dump_settings(SESSION_FILE)

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
