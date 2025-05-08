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
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string

# Download NLTK data
nltk.download('punkt')
nltk.download('stopwords')

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

# New endpoint to delete duplicate topics
@app.route('/delete-duplicates', methods=['GET'])
def delete_duplicates():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, title, added_at FROM topics ORDER BY added_at DESC")
        topics = cursor.fetchall()
        
        if not topics:
            cursor.close()
            conn.close()
            return jsonify({
                "status": "success",
                "message": "No topics found in the database.",
                "deleted_count": 0
            })

        # Extract titles and IDs
        titles = [topic['title'] for topic in topics]
        topic_ids = [topic['id'] for topic in topics]
        added_at_timestamps = [topic['added_at'] for topic in topics]

        # Compute similarity matrix
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(titles)
        similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

        # Find duplicates (similarity > 0.7)
        to_delete = set()
        for i in range(len(titles)):
            if i in to_delete:
                continue
            for j in range(i + 1, len(titles)):
                if similarity_matrix[i][j] > 0.7:
                    # Keep the topic with the latest timestamp
                    if added_at_timestamps[i] > added_at_timestamps[j]:
                        to_delete.add(j)
                    else:
                        to_delete.add(i)

        # Delete duplicate topics
        deleted_count = 0
        for idx in to_delete:
            cursor.execute("DELETE FROM topics WHERE id = %s", (topic_ids[idx],))
            print(f"[{datetime.now()}] Deleted duplicate topic ID {topic_ids[idx]}: {titles[idx]}")
            deleted_count += 1

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "message": f"Deleted {deleted_count} duplicate topics.",
            "deleted_count": deleted_count
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error deleting duplicates: {str(e)}",
            "deleted_count": 0
        }), 500

def extract_keywords(text):
    """
    Extract keywords from text for better duplicate detection.
    """
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text.lower())
    # Remove punctuation and stopwords
    keywords = [word for word in tokens if word not in string.punctuation and word not in stop_words]
    return set(keywords)

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
        # Fetch existing topics from database
        cursor.execute("SELECT title FROM topics")
        existing_topics = [row[0] for row in cursor.fetchall()]
        
        # Double check for duplicates
        if existing_topics:
            # TF-IDF based similarity check
            vectorizer = TfidfVectorizer()
            all_texts = existing_topics + [topic]
            tfidf_matrix = vectorizer.fit_transform(all_texts)
            similarity_matrix = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
            max_similarity = similarity_matrix.max()
            if max_similarity > 0.7:
                print(f"[{datetime.now()}] Topic too similar to existing (TF-IDF similarity: {max_similarity}): {topic}")
                cursor.close()
                conn.close()
                return False
            
            # Keyword overlap check
            topic_keywords = extract_keywords(topic)
            for existing_topic in existing_topics:
                existing_keywords = extract_keywords(existing_topic)
                # Calculate keyword overlap
                common_keywords = topic_keywords.intersection(existing_keywords)
                overlap_ratio = len(common_keywords) / max(len(topic_keywords), len(existing_keywords))
                if overlap_ratio > 0.6:
                    print(f"[{datetime.now()}] Topic too similar to existing (keyword overlap: {overlap_ratio}): {topic}")
                    cursor.close()
                    conn.close()
                    return False
        
        # Insert if not similar
        cursor.execute("INSERT INTO topics (title) VALUES (%s)", (topic,))
        conn.commit()
        print(f"[{datetime.now()}] Inserted topic: {topic}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"[{datetime.now()}] Error in insert_topic: {e}")
        return False

def generate_topic_with_gemini(data, perspective="summary"):
    try:
        if not data or len(data.strip()) < 10:
            print(f"[{datetime.now()}] No valid data for Gemini: {data}")
            return None
        # Different prompts for different perspectives with added creativity
        if perspective == "summary":
            prompt = f"Analyze the following data and generate a concise blog topic summary of 50-100 words with a unique angle:\n\n{data}"
        elif perspective == "opinion":
            prompt = f"Analyze the following data and generate a blog topic with a creative opinion or bold perspective in 50-100 words:\n\n{data}"
        elif perspective == "question":
            prompt = f"Analyze the following data and generate a blog topic as a thought-provoking question with an unusual twist in 50-100 words:\n\n{data}"
        elif perspective == "narrative":
            prompt = f"Analyze the following data and generate a blog topic in a storytelling style with a fresh narrative in 50-100 words:\n\n{data}"
        elif perspective == "controversial":
            prompt = f"Analyze the following data and generate a blog topic with a controversial or unconventional take in 50-100 words:\n\n{data}"
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
    perspectives = ["summary", "opinion", "question", "narrative", "controversial"]
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
    
    for fetcher in [fetch_news_topics, fetch_web_search]:
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
    
    print(f"[{datetime.now()}] Fetched {len(all_topics)} unique topics before final filtering.")
    # Final insertion with duplicate check
    saved_count = 0
    for topic in all_topics:
        if insert_topic(topic):
            saved_count += 1
    
    return f"Fetched and saved {saved_count} topics to database.", details

# Auto-generate every 30 minutes
def run_scheduler():
    print(f"[{datetime.now()}] Scheduler running...")
    schedule.every(30).minutes.do(main)
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

# Start scheduler in a separate thread
def start_scheduler_thread():
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    print(f"[{datetime.now()}] Scheduler started: Running main() every 30 minutes.")

if __name__ == "__main__":
    # Start the scheduler
    start_scheduler_thread()
    # Run Flask app
    app.run(host="0.0.0.0", port=10000)
