import requests
import mysql.connector
from datetime import datetime

RAPIDAPI_KEY = "e5609b396bmshc7f942bfe60c9cdp110cfcjsn8296e1012489"

# MySQL config
db_config = {
    "host": "sql12.freesqldatabase.com",
    "user": "sql12777526",
    "password": "sAQEtY6NF2",
    "database": "sql12777526",
    "port": 3306
}

def insert_topic(topic):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS topics (id INT AUTO_INCREMENT PRIMARY KEY, title TEXT, added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    cursor.execute("SELECT title FROM topics WHERE title = %s", (topic,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO topics (title) VALUES (%s)", (topic,))
        conn.commit()
    cursor.close()
    conn.close()

def fetch_facebook_reels():
    url = "https://facebook-scraper3.p.rapidapi.com/page/reels"
    querystring = {"page_id": "100064860875397"}
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "facebook-scraper3.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()
    return [item.get("title", "") for item in data if item.get("title")]

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
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    return [item.get("title", "") for item in data.get("articles", []) if item.get("title")]

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
    response = requests.post(url, headers=headers, json=queries)
    data = response.json()
    return [item.get("title", "") for item in data.get("results", []) if item.get("title")]

def main():
    all_topics = set()

    for fetcher in [fetch_facebook_reels, fetch_news_topics, fetch_web_search]:
        try:
            topics = fetcher()
            all_topics.update([t.strip() for t in topics if t.strip()])
        except Exception as e:
            print(f"Error in {fetcher.__name__}: {e}")

    print(f"Fetched {len(all_topics)} unique topics.")
    for topic in all_topics:
        insert_topic(topic)
    print("All topics saved to database.")

if __name__ == "__main__":
    main()
