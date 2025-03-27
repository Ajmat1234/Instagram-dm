from flask import Flask, jsonify
from instagrapi import Client
from playwright.sync_api import sync_playwright
import os
import threading
import time
import json

app = Flask(__name__)

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
MESSAGE = os.getenv("MESSAGE", "Welcome to our group!")
TRACKING_FILE = "user_track.json"

bot = Client()
bot.login(USERNAME, PASSWORD)

# ---------------- Load Users ----------------
def load_users():
    try:
        with open(TRACKING_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# ---------------- Save Users ----------------
def save_user(user_id):
    users = load_users()
    users[user_id] = time.time()
    with open(TRACKING_FILE, "w") as f:
        json.dump(users, f)

# ---------------- Check Welcome ----------------
def should_welcome(user_id):
    users = load_users()
    return user_id not in users or (time.time() - users[user_id]) > 86400

# ---------------- DM Monitoring with Playwright ----------------
def scan_dms():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.instagram.com/")
        page.wait_for_selector('input[name="username"]', timeout=30000)

        page.fill('input[name="username"]', USERNAME)
        page.fill('input[name="password"]', PASSWORD)
        page.click('button[type="submit"]')
        page.wait_for_selector('svg[aria-label="Home"]', timeout=60000)
        page.goto("https://www.instagram.com/direct/inbox/")

        while True:
            chats = page.query_selector_all('div[role="row"]')
            for chat in chats:
                user_id = chat.inner_text()
                if should_welcome(user_id):
                    thread_id = bot.direct_threads(user_id).pk
                    bot.direct_answer(thread_id=thread_id, text=MESSAGE)
                    save_user(user_id)
            time.sleep(30)

# ---------------- Start Monitoring in Thread ----------------
def start_monitoring():
    t = threading.Thread(target=scan_dms)
    t.start()

@app.route('/')
def home():
    return jsonify({"status": "Bot is running", "message": "DM Monitoring Active"})

if __name__ == "__main__":
    start_monitoring()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
