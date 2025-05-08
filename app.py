import requests
import mysql.connector
import google.generativeai as genai
from datetime import datetime
from flask import Flask, Response, jsonify
import schedule
import time
import threading
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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

# Endpoint to fetch saved topics
@app.route('/get-topics', methods=['GET'])
def get_topics():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM topics ORDER BY added_at DESC")
        topics = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({
            "status": "success",
            "message": f"Found {len(topics)} topics in the database.",
            "topics": topics
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error fetching topics: {str(e)}",
            "topics": []
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

def generate_topic_with_gemini(data, perspective="summary"):
    try:
        if not data or len(data.strip()) < 10:
            print(f"[{datetime.now()}] No valid data for Gemini: {data}")
            return None
        # Different prompts for different perspectives
        if perspective == "summary":
            prompt = f"Analyze the following data and generate a concise blog topic summary of 50-100 words:\n\n{data}"
        elif perspective == "opinion":
            prompt = f"Analyze the following data and generate a blog topic with an opinion or perspective in 50-100 words:\n\n{data}"
        elif perspective == "question":
            prompt = f"Analyze the following data and generate a blog topic in the form of a thought-provoking question in 50-100 words:\n\n{data}"
        response = model.generate_content(prompt)
        topic = response.text.strip()
        topic = topic.replace("**", "").replace("\n", " ")
        word_count = len(topic.split())
        if 50 <= word_count <= 100:
            print(f"[{datetime.now()}] Generated topic (words: {word_count}): {topic}")
            return topic
        else:
            if word_count > 100:
                topic = " ".join(topic.split()[:100])
                print(f"[{datetime.now()}] Trimmed topic to 100 words: {topic}")
                return topic
            elif word_count < 50:
                topic += " This summary highlights key trends and insights for blog content creation."
                word_count = len(topic.split())
                if 50 <= word_count <= 100:
                    print(f"[{datetime.now()}] Expanded topic (words: {word_count}): {topic}")
                    return topic
                print(f"[{datetime.now()}] Topic word count {word_count} still out of range after expansion")
                return None
    except Exception as e:
        print(f"[{datetime.now()}] Error in generate_topic_with_gemini: {e}")
        return None

def filter_unique_items(items):
    # Remove duplicates from raw data based on text similarity
    if not items:
        return []
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(items)
    similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
    unique_items = []
    seen_indices = set()
    for i in range(len(items)):
        if i not in seen_indices:
            unique_items.append(items[i])
            # Mark similar items (similarity > 0.8) as seen
            for j in range(len(items)):
                if i != j and similarity_matrix[i][j] > 0.8:
                    seen_indices.add(j)
    return unique_items

def filter_unique_topics(topics):
    # Filter out similar topics based on text similarity
    if not topics:
        return []
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(topics)
    similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
    unique_topics = []
    seen_indices = set()
    for i in range(len(topics)):
        if i not in seen_indices:
            unique_topics.append(topics[i])
            # Mark similar topics (similarity > 0.7) as seen
            for j in range(len(topics)):
                if i != j and similarity_matrix[i][j] > 0.7:
                    seen_indices.add(j)
    return unique_topics

def generate_multiple_topics(data, chunk_size=5, source_name=""):
    topics = []
    if not data:
        print(f"[{datetime.now()}] No data to generate topics for {source_name}")
        return topics
    
    # Filter unique items from raw data
    unique_data = filter_unique_items(data)
    print(f"[{datetime.now()}] Filtered {len(data) - len(unique_data)} duplicate items from {source_name}")

    # Divide data into chunks
    perspectives = ["summary", "opinion", "question"]
    for i in range(0, len(unique_data), chunk_size):
        chunk = unique_data[i:i + chunk_size]
        raw_text = " ".join(chunk)
        print(f"[{datetime.now()}] Processing chunk for {source_name}: {raw_text[:100]}...")
        # Generate topics with different perspectives
        for idx, perspective in enumerate(perspectives):
            topic = generate_topic_with_gemini(raw_text, perspective=perspective)
            if topic:
                topics.append(topic)
    # Filter similar topics
    unique_topics = filter_unique_topics(topics)
    print(f"[{datetime.now()}] Generated {len(unique_topics)} unique topics from {source_name}")
    return unique_topics

def fetch_facebook_posts():
    # List of popular Facebook page IDs
    page_ids = ["100044534166687", "100064615539257", "100064849585551"]  # Updated page IDs (e.g., BBC News, National Geographic, BuzzFeed)
    all_posts = []
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "facebook-scraper3.p.rapidapi.com"
    }
    try:
        for page_id in page_ids:
            url = "https://facebook-scraper3.p.rapidapi.com/page/posts"
            querystring = {"page_id": page_id}
            response = requests.get(url, headers=headers, params=querystring)
            response.raise_for_status()
            data = response.json()
            print(f"[{datetime.now()}] Facebook API response for {page_id}: {data}")
            raw_data = data.get("results", [])
            if raw_data:
                posts = [(item.get("message", ""), item.get("timestamp", 0)) for item in raw_data if item.get("message") and item.get("timestamp")]
                all_posts.extend(posts)
        
        if all_posts:
            # Sort by timestamp to get the latest posts
            all_posts.sort(key=lambda x: x[1], reverse=True)  # Latest first
            latest_contents = [post for post, _ in all_posts]
            print(f"[{datetime.now()}] Fetched Facebook posts data: {latest_contents[:100]}...")
            return generate_multiple_topics(latest_contents, chunk_size=5, source_name="Facebook posts")
        print(f"[{datetime.now()}] No Facebook posts data found")
        return []
    except Exception as e:
        print(f"[{datetime.now()}] Error in fetch_facebook_posts: {e}")
        return []

def fetch_twitter_trends():
    url = "https://twitter-trends5.p.rapidapi.com/twitter/api/trends"
    querystring = {"woeid": "23424977"}  # WOEID for worldwide trends
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "twitter-trends5.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()
        print(f"[{datetime.now()}] Twitter Trends API response: {data}")
        raw_data = data.get("trends", [])
        if raw_data:
            trends = [item.get("name", "") for item in raw_data if item.get("name")]
            print(f"[{datetime.now()}] Fetched Twitter trends data: {trends[:100]}...")
            return generate_multiple_topics(trends, chunk_size=5, source_name="Twitter trends")
        print(f"[{datetime.now()}] No Twitter trends data found")
        return []
    except Exception as e:
        print(f"[{datetime.now()}] Error in fetch_twitter_trends: {e}")
        return []

def fetch_news_topics():
    url = "https://real-time-news-data.p.rapidapi.com/top-headlines"
    params = {
        "country": "US",
        "lang": "en",
        "limit": "20"
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
        raw_data = data.get("data", [])
        if raw_data:
            titles = [item.get("title", "") for item in raw_data if item.get("title")]
            return generate_multiple_topics(titles, chunk_size=5, source_name="News topics")
        print(f"[{datetime.now()}] No news topics data found")
        return []
    except Exception as e:
        print(f"[{datetime.now()}] Error in fetch_news_topics: {e}")
        return []

def fetch_web_search():
    url = "https://real-time-web-search.p.rapidapi.com/search"
    headers = {
        "Content-Type": "application/json",
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "real-time-web-search.p.rapidapi.com"
    }
    payload = {
        "q": "chatgpt OR AI OR coding OR health OR world news",
        "limit": 20
    }
    try:
        response = requests.get(url, headers=headers, params=payload)
        response.raise_for_status()
        data = response.json()
        print(f"[{datetime.now()}] Web search API response: {data}")
        raw_data = data.get("data", [])
        if raw_data:
            titles = [item.get("title", "") for item in raw_data if item.get("title")]
            return generate_multiple_topics(titles, chunk_size=5, source_name="Web search")
        print(f"[{datetime.now()}] No web search data found")
        return []
    except Exception as e:
        print(f"[{datetime.now()}] Error in fetch_web_search: {e}")
        return []

def main():
    all_topics = set()
    details = []
    
    for fetcher in [fetch_facebook_posts, fetch_twitter_trends, fetch_news_topics, fetch_web_search]:
        try:
            topics = fetcher()
            if topics:
                for topic in topics:
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
