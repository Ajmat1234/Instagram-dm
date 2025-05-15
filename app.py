from flask import Flask
import requests
import xml.etree.ElementTree as ET
import time
import threading
import json
import os

app = Flask(__name__)

SITEMAP_URL = "https://work-lyart-rho.vercel.app/sitemap.xml"
INDEXNOW_KEY = "0e06de419d2847e486f3c9ca7097931d"
KEY_LOCATION = f"https://work-lyart-rho.vercel.app/{INDEXNOW_KEY}.txt"
HOST = "work-lyart-rho.vercel.app"
SUBMITTED_URLS_FILE = "/tmp/submitted_urls.json"  # instead of current directory
INDEXNOW_API = "https://api.indexnow.org/indexnow"

def load_submitted_urls():
    if os.path.exists(SUBMITTED_URLS_FILE):
        with open(SUBMITTED_URLS_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_submitted_urls(urls):
    with open(SUBMITTED_URLS_FILE, "w") as f:
        json.dump(list(urls), f)

def extract_urls_from_sitemap(sitemap_url):
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        return [url.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text
                for url in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url")]
    except Exception as e:
        print("Error reading sitemap:", e)
        return []

def submit_url_to_indexnow(url):
    payload = {
        "host": HOST,
        "key": INDEXNOW_KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": [url]
    }
    try:
        response = requests.post(INDEXNOW_API, json=payload, headers={
            "Content-Type": "application/json"
        })
        print(f"Submitted: {url} | Status: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error submitting {url}: {e}")
        return False

def indexnow_worker():
    while True:
        print("Checking sitemap for new URLs...")
        urls = extract_urls_from_sitemap(SITEMAP_URL)
        submitted_urls = load_submitted_urls()
        new_urls = [url for url in urls if url not in submitted_urls]

        print(f"Found {len(new_urls)} new URLs to submit.")
        for url in new_urls:
            success = submit_url_to_indexnow(url)
            if success:
                submitted_urls.add(url)
                save_submitted_urls(submitted_urls)
            time.sleep(2)  # avoid too many rapid requests
        print("Sleeping for 2 hours...\n")
        time.sleep(2 * 60 * 60)

# background thread to keep it running
threading.Thread(target=indexnow_worker, daemon=True).start()

@app.route("/")
def home():
    return "IndexNow Pinger is running (POST version)."

@app.route("/ping")
def ping():
    return "Pong - Still alive!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
