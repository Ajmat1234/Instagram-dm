import requests
import mysql.connector
import google.generativeai as genai
from datetime import datetime
from flask import Flask, Response, jsonify
import schedule
import time
import threading

# Flask app
app = Flask(__name__)

# API Keys
RAPIDAPI_KEY = "e5609b396bmshc7f942bfe60c9cdp110cfcjsn8296e1012489"
GEMINI_API_KEY = "AIzaSyALVGk-yBmkohV6Wqei63NARTd9xD-O7TI"

# MySQL config
db_config = {
    "host": "sql12.freesqldatabase.com",
    "user": "sql12777526",
    "password": "sAQEtY6NF2",
    "database": "sql12777526",
    "port": 3306
}

# Configure Gemini API
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    print(f"[{datetime.now()}] Gemini API configured successfully")
except Exception as e:
    print(f"[{datetime.now()}] Error configuring Gemini API: {e}")

# Health check endpoint
@app.route('/health')
def health():
    return Response("OK", status=200)

# Manual generate endpoint
@app.route('/manual-generate', methods=['GET'])
def manual_generate():
    try:
        result, details = main()
        return jsonify({
            "status": "success",
            "message": result,
            "details": details
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "details": []
        }), 500

def insert_topic(topic):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("SELECT title FROM topics WHERE title = %s", (topic,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO topics (title) VALUES (%s)", (topic,))
            conn.commit()
            print(f"[{datetime.now()}] Inserted topic: {topic}")
        else:
            print(f"[{datetime.now()}] Topic already exists: {topic}")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[{datetime.now()}] Error in insert_topic: {e}")

def generate_topic_with_gemini(data):
    try:
        if not data or len(data.strip()) < 10:
            print(f"[{datetime.now()}] No valid data for Gemini: {data}")
            return None
        prompt = f"From the following data, generate a concise topic summary of 50-100 words:\n\n{data}"
        response = model.generate_content(prompt)
        topic = response.text.strip()
        word_count = len(topic.split())
        if 50 <= word_count <= 100:
            print(f"[{datetime.now()}] Generated topic (words: {word_count}): {topic}")
            return topic
        else:
            # Fallback: Trim or expand topic to fit 50-100 words
            if word_count > 100:
                topic = " ".join(topic.split()[:100])
                print(f"[{datetime.now()}] Trimmed topic to 100 words: {topic}")
                return topic
            elif word_count < 50:
                topic += " " + "This summary provides insights into recent trends and updates in the given context."
                word_count = len(topic.split())
                if 50 <= word_count <= 100:
                    print(f"[{datetime.now()}] Expanded topic (words: {word_count}): {topic}")
                    return topic
                print(f"[{datetime.now()}] Topic word count {word_count} still out of range after expansion")
                return None
    except Exception as e:
        print(f"[{datetime.now()}] Error in generate_topic_with_gemini: {e}")
        return None

def fetch_facebook_posts():
    url = "https://facebook-scraper3.p.rapidapi.com/page/posts"
    querystring = {"page_id": "100064860875397"}
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "facebook-scraper3.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()
        print(f"[{datetime.now()}] Facebook API response: {data}")
        raw_data = data.get("results", [])
        if raw_data:
            raw_text = " ".join([item.get("message", "") for item in raw_data if isinstance(item, dict) and item.get("message")])
            print(f"[{datetime.now()}] Fetched Facebook posts data: {raw_text[:100]}...")
            return generate_topic_with_gemini(raw_text)
        print(f"[{datetime.now()}] No Facebook posts data found")
        return None
    except Exception as e:
        print(f"[{datetime.now()}] Error in fetch_facebook_posts: {e}")
        return None

def fetch_news_topics():
    url = "https://real-time-news-data.p.rapidapi.com/topic-news-by-section"
    params = {
        "topic": "TECHNOLOGY",
        "section": "CAQiSkNCQVNNUW9JTDIwdk1EZGpNWFlTQldWdUxVZENHZ0pKVENJT0NBUWFDZ29JTDIwdk1ETnliSFFxQ2hJSUwyMHZNRE55YkhRb0FBKi4IACoqCAoiJENCQVNGUW9JTDIwdk1EZGpNWFlTQldWdUxVZENHZ0pKVENnQVABUAE",
        "limit": "100",
        "country": "US",
        "lang": "en"
    }
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "real-time-news-data.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        print(f"[{datetime.now()}] News API response: {data}")
        raw_data = data.get("data", {}).get("articles", [])
        if raw_data:
            raw_text = " ".join([item.get("title", "") for item in raw_data if item.get("title")])
            print(f"[{datetime.now()}] Fetched news topics data: {raw_text[:100]}...")
            return generate_topic_with_gemini(raw_text)
        print(f"[{datetime.now()}] No news topics data found")
        return None
    except Exception as e:
        print(f"[{datetime.now()}] Error in fetch_news_topics: {e}")
        return None

def fetch_web_search():
    url = "https://real-time-web-search.p.rapidapi.com/search"
    headers = {
        "Content-Type": "application/json",
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "real-time-web-search.p.rapidapi.com"
    }
    # Simplified query for testing
    payload = {
        "q": "chatgpt OR AI OR coding OR health OR world news",
        "limit": 10
    }
    try:
        response = requests.get(url, headers=headers, params=payload)
        response.raise_for_status()
        data = response.json()
        print(f"[{datetime.now()}] Web search API response: {data}")
        raw_data = data.get("data", [])
        if raw_data:
            raw_text = " ".join([item.get("title", "") for item in raw_data if item.get("title")])
            print(f"[{datetime.now()}] Fetched web search data: {raw_text[:100]}...")
            return generate_topic_with_gemini(raw_text)
        print(f"[{datetime.now()}] No web search data found")
        return None
    except Exception as e:
        print(f"[{datetime.now()}] Error in fetch_web_search: {e}")
        return None

def main():
    all_topics = set()
    details = []
    
    for fetcher in [fetch_facebook_posts, fetch_news_topics, fetch_web_search]:
        try:
            topic = fetcher()
            if topic and topic.strip():
                all_topics.add(topic)
                details.append(f"Success: Added topic from {fetcher.__name__}: {topic[:50]}...")
                print(f"[{datetime.now()}] Added topic from {fetcher.__name__}")
            else:
                details.append(f"Failed: No valid topic from {fetcher.__name__}")
                print(f"[{datetime.now()}] No valid topic from {fetcher.__name__}")
        except Exception as e:
            details.append(f"Error in {fetcher.__name__}: {str(e)}")
            print(f"[{datetime.now()}] Error in {fetcher.__name__}: {e}")
    
    print(f"[{datetime.now()}] Fetched {len(all_topics)} unique topics.")
    for topic in all_topics:
        insert_topic(topic)
    
    return f"Fetched and saved {len(all_topics)} topics to database.", details

# Auto-generate every 10 minutes
def run_scheduler():
    print(f"[{datetime.now()}] Scheduler running...")
    schedule.every(10).minutes.do(main)
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

# Start scheduler in a separate thread
def start_scheduler_thread():
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    print(f"[{datetime.now()}] Scheduler started: Running main() every 10 minutes.")

if __name__ == "__main__":
    # Start the scheduler
    start_scheduler_thread()
    # Run Flask app
    app.run(host="0.0.0.0", port=10000)
