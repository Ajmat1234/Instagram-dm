from flask import Flask, request, jsonify
from instagrapi import Client
from playwright.sync_api import sync_playwright
import json
import os
import base64
import random
import threading
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)

# ---------------- Config and Environment ----------------
WELCOME_MSGS = [
    "Welcome @{username}, humein khushi hai ki aap hamare group mein shamil hue!",
    "Hello @{username}, aapka swagat hai, enjoy kijiye!"
]
TRACKING_FILE = "user_track.json"

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
SESSION_DATA = os.getenv("SESSION_DATA")

# ---------------- User Tracking ----------------
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

# ---------------- Session Management ----------------
def load_or_login():
    bot = Client()
    if SESSION_DATA:
        try:
            session_bytes = base64.b64decode(SESSION_DATA)
            with open("ig_session.json", "wb") as f:
                f.write(session_bytes)
            bot.load_settings("ig_session.json")
            print("✅ Session restored from environment variable.")
        except Exception as e:
            print(f"⚠️ Error loading session: {e}, logging in again...")
            bot.login(username=USERNAME, password=PASSWORD)
    else:
        print("⚠️ No session found. Logging in...")
        bot.login(username=USERNAME, password=PASSWORD)
    return bot

bot = load_or_login()

# ---------------- Playwright Monitoring ----------------
def monitor_dms():
    """Real-time DM Monitoring with Playwright"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Login to Instagram
        page.goto("https://www.instagram.com/accounts/login/")
        page.fill('input[name="username"]', USERNAME)
        page.fill('input[name="password"]', PASSWORD)
        page.click('button[type="submit"]')
        page.wait_for_selector('svg[aria-label="Home"]')

        # Navigate to DM Inbox
        page.goto('https://www.instagram.com/direct/inbox/')
        page.wait_for_selector('div[role="grid"]')
        
        print("📡 Monitoring DMs...")
        while True:
            page.reload(wait_until="networkidle")
            dms = page.locator('div[role="grid"]').all_inner_texts()
            for dm in dms:
                if "New message" in dm:
                    handle_new_dm(dm)
            page.wait_for_timeout(10000)  # Wait for 10 seconds before checking again

def handle_new_dm(dm):
    """Handle New DM and Send Auto-response"""
    user_id = dm.split()[0]
    if should_welcome(user_id):
        username = get_username(user_id)
        welcome_msg = random.choice(WELCOME_MSGS).format(username=username)
        bot.direct_answer(thread_id=user_id, text=welcome_msg)
        save_user(user_id, datetime.now(pytz.utc))
        print(f"👋 Sent to @{username}: {welcome_msg}")

def get_username(user_id):
    """Get Username from User ID"""
    try:
        user = bot.user_info(user_id)
        return user.username
    except Exception:
        return "user"

# ---------------- Flask Endpoints ----------------
@app.route('/')
def home():
    """Health Check Endpoint"""
    return jsonify({"status": "Bot is running", "message": "DM monitoring active!"})

@app.route('/start_monitoring', methods=["POST"])
def start_monitoring():
    """Start DM Monitoring"""
    thread = threading.Thread(target=monitor_dms)
    thread.start()
    return jsonify({"status": "success", "message": "DM Monitoring started"})

@app.route('/stop_monitoring', methods=["POST"])
def stop_monitoring():
    """Stop DM Monitoring"""
    # Stopping threads in Python is tricky, better to kill manually for now
    return jsonify({"status": "error", "message": "Stopping monitoring manually is advised"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
