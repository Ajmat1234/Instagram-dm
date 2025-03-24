import instaloader
from datetime import datetime, timedelta
import json
import logging
import time
import random
import re
from typing import List

# Logging setup
logging.basicConfig(
    filename="bot_progress.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)

# Instaloader instance without login
L = instaloader.Instaloader()
L.login = None  # Ensure no login

# Optional: Add proxy (uncomment and configure if needed)
# L.context._session.proxies = {"http": "http://your_proxy:port", "https": "http://your_proxy:port"}

# JSON file to store active users
JSON_FILE = "active_girls.json"

# Function to check if user is likely a girl
def is_likely_female(username: str, full_name: str = None, bio: str = None) -> bool:
    female_names = [
        "priya", "anju", "neha", "simran", "pooja", "rani", "kavita", "meera",
        "sonia", "tanu", "divya", "isha", "kriti", "shruti", "vidya", "jaya",
        "rekha", "sneha", "radha", "lata", "geeta", "mona", "tina", "ritu",
        "arti", "shweta", "manju", "kiran", "nisha", "preeti", "anjali"
    ]
    female_nicknames = [
        "babu", "doll", "cute", "sweet", "baby", "gudiya", "pari", "angel",
        "star", "moon", "sunny", "pinky", "chinky", "tweety", "bubbly"
    ]
    female_lastnames = [
        "sharma", "verma", "gupta", "singh", "kaur", "patel", "mehta",
        "jain", "yadav", "thakur", "chauhan", "rana", "reddy", "nair"
    ]
    female_keywords = [
        "girl", "she", "queen", "princess", "lady", "di", "sis", "bhabhi",
        "beauty", "cute", "angel", "doll", "fashion", "makeup", "love",
        "mom", "wife", "sister", "daughter", "fairy", "diva"
    ]
    bts_related = [
        "bts", "army", "jungkook", "jimin", "taehyung", "v", "jin", "suga",
        "jhope", "rm", "kpop", "bangtan", "purple", "borobudur"
    ]
    female_emojis = [
        "💕", "💖", "💗", "💓", "💞", "💜", "🌸", "🌺", "🌹", "💐",
        "✨", "🌟", "💋", "👑", "🎀", "🦋", "🐾", "🌈", "🍓", "🍒"
    ]
    
    username_lower = username.lower()
    full_name_lower = full_name.lower() if full_name else ""
    bio_lower = bio.lower() if bio else ""
    
    if any(name in username_lower for name in female_names + female_nicknames):
        return True
    if any(lastname in username_lower for lastname in female_lastnames):
        return True
    if any(bts in username_lower for bts in bts_related):
        return True
    if full_name_lower and any(name in full_name_lower for name in female_names):
        return True
    if full_name_lower and any(lastname in full_name_lower for lastname in female_lastnames):
        return True
    if bio_lower:
        if any(keyword in bio_lower for keyword in female_keywords):
            return True
        if any(emoji in bio for emoji in female_emojis):
            return True
        if any(bts in bio_lower for bts in bts_related):
            return True
    if re.search(r"[aiey]$", username_lower) or re.search(r"xx$", username_lower):
        return True
    
    male_keywords = ["boy", "bro", "king", "dude", "guy", "ladka", "boss"]
    if not any(mk in username_lower or (full_name_lower and mk in full_name_lower) or (bio_lower and mk in bio_lower) for mk in male_keywords):
        return True
    
    return False

# Function to load existing JSON data
def load_json_data() -> List[str]:
    try:
        with open(JSON_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Function to save to JSON
def save_json_data(data: List[str]):
    with open(JSON_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Main bot logic with rotating hashtags
def scrape_active_girls():
    logging.info("Bot started processing...")
    
    active_girls = load_json_data()
    
    # Rotating hashtags
    hashtags = ["beauty", "fashion", "makeup", "reelsindia", "bts", "girls"]
    hashtag_index = 0
    
    while hashtag_index < len(hashtags) and len(active_girls) < 20:
        hashtag = hashtags[hashtag_index]
        logging.info(f"Trying hashtag: #{hashtag}")
        
        try:
            posts = L.get_hashtag_posts(hashtag)
            for post in posts:
                if post.date > datetime.now() - timedelta(hours=24):
                    logging.info(f"Scraping comments from post: {post.shortcode}")
                    
                    for comment in post.get_comments():
                        username = comment.owner.username
                        if username in active_girls:
                            continue
                        
                        try:
                            profile = instaloader.Profile.from_username(L.context, username)
                            full_name = profile.full_name
                            bio = profile.biography
                        except Exception as e:
                            full_name = None
                            bio = None
                            logging.warning(f"Could not fetch profile for {username}: {e}")
                        
                        if is_likely_female(username, full_name, bio):
                            active_girls.append(username)
                            logging.info(f"Found active girl: @{username} (Name: {full_name or 'N/A'})")
                        
                        if len(active_girls) % 5 == 0:
                            save_json_data(active_girls)
                            logging.info(f"Saved {len(active_girls)} users to {JSON_FILE}")
                        
                        if len(active_girls) >= 20:
                            logging.info(f"Reached 20 active girls: {active_girls}")
                            return active_girls
                    
                    time.sleep(random.uniform(10, 20))  # Increased delay
        
        except instaloader.exceptions.QueryReturnedNotFoundException:
            logging.warning(f"Hashtag #{hashtag} returned 404. Switching to next hashtag.")
            hashtag_index += 1
            time.sleep(30)  # Wait before switching
            continue
        except Exception as e:
            logging.error(f"Error with #{hashtag}: {e}")
            hashtag_index += 1
            time.sleep(30)
            continue
    
    save_json_data(active_girls)
    logging.info(f"Bot finished. Total active girls found: {len(active_girls)}")
    return active_girls

if __name__ == "__main__":
    active_girls = scrape_active_girls()
    print(f"Check 'bot_progress.log' for progress and '{JSON_FILE}' for results!")
