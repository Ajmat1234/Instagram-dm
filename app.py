import requests
import mysql.connector
import google.generativeai as genai
from datetime import datetime
from flask import Flask, Response, jsonify

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
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Health check endpoint
@app.route('/health')
def health():
    return Response("OK", status=200)

# Endpoint to fetch and save topics
@app.route('/fetch-topics', methods=['GET'])
def fetch_topics_endpoint():
    try:
        result = main()
        return jsonify({"status": "success", "message": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

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
        cursor.close()
        conn.close()
        print(f"Inserted topic: {topic}")
    except Exception as e:
        print(f"Error in insert_topic: {e}")

def generate_topic_with_gemini(data):
    try:
        prompt = f"From the following data, generate a concise topic summary of 50-100 words:\n\n{data}"
        response = model.generate_content(prompt)
        topic = response.text.strip()
        word_count = len(topic.split())
        if 50 <= word_count <= 100:
            print(f"Generated topic (words: {word_count}): {topic}")
            return topic
        else:
            print(f"Topic word count {word_count} out of range (50-100)")
            return None
    except Exception as e:
        print(f"Error in generate_topic_with_gemini: {e}")
        return None

def fetch_facebook_reels():
    url = "https://facebook-scraper3.p.rapidapi.com/page/reels"
    querystring = {"page_id": "100064860875397"}
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "facebook-scraper3.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()
        raw_data = data.get("data", [])
        if raw_data:
            raw_text = " ".join([item.get("title", "") for item in raw_data if isinstance(item, dict) and item.get("title")])
            print("Fetched Facebook reels data")
            return generate_topic_with_gemini(raw_text)
        print("No Facebook reels data found")
        return None
    except Exception as e:
        print(f"Error in fetch_facebook_reels: {e}")
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
        raw_data = data.get("articles", [])
        if raw_data:
            raw_text = " ".join([item.get("title", "") for item in raw_data if item.get("title")])
            print("Fetched news topics data")
            return generate_topic_with_gemini(raw_text)
        print("No news topics data found")
        return None
    except Exception as e:
        print(f"Error in fetch_news_topics: {e}")
        return None

def fetch_web_search():
    url = "https://real-time-web-search.p.rapidapi.com/search"
    headers = {
        "Content-Type": "application/json",
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "real-time-web-search.p.rapidapi.com"
    }
    queries = {
        "queries": ["chatgpt", "AI", "coding", "health", "world news"],
        "limit": "10"
    }
    try:
        response = requests.post(url, headers=headers, json=queries)
        response.raise_for_status()
        data = response.json()
        raw_data = data.get("results", [])
        if raw_data:
            raw_text = " ".join([item.get("title", "") for item in raw_data if item.get("title")])
            print("Fetched web search data")
            return generate_topic_with_gemini(raw_text)
        print("No web search data found")
        return None
    except Exception as e:
        print(f"Error in fetch_web_search: {e}")
        return None

def main():
    all_topics = set()
    for fetcher in [fetch_facebook_reels, fetch_news_topics, fetch_web_search]:
        try:
            topic = fetcher()
            if topic and topic.strip():
                all_topics.add(topic)
                print(f"Added topic from {fetcher.__name__}")
            else:
                print(f"No valid topic from {fetcher.__name__}")
        except Exception as e:
            print(f"Error in {fetcher.__name__}: {e}")
    
    print(f"Fetched {len(all_topics)} unique topics.")
    for topic in all_topics:
        insert_topic(topic)
    return f"Fetched and saved {len(all_topics)} topics to database."

if __name__ == "__main__":
    # Run Flask app
    app.run(host="0.0.0.0", port=10000)
