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

# JSON file to store active users
JSON_FILE = "active_girls.json"

# Function to check if user is likely a girl
def is_likely_female(username: str, full_name: str = None, bio: str = None) -> bool:
    # Common Indian female names (expanded)
    female_names = [
        "priya", "anju", "neha", "simran", "pooja", "rani", "kavita", "meera",
        "sonia", "tanu", "divya", "isha", "kriti", "shruti", "vidya", "jaya",
        "rekha", "sneha", "radha", "lata", "geeta", "mona", "tina", "ritu",
        "arti", "shweta", "manju", "kiran", "nisha", "preeti", "anjali"
    ]
    
    # Common female nicknames
    female_nicknames = [
        "babu", "doll", "cute", "sweet", "baby", "gudiya", "pari", "angel",
        "star", "moon", "sunny", "pinky", "chinky", "tweety", "bubbly"
    ]
    
    # Common female last names
    female_lastnames = [
        "sharma", "verma", "gupta", "singh", "kaur", "patel", "mehta",
        "jain", "yadav", "thakur", "chauhan", "rana", "reddy", "nair"
    ]
    
    # Female keywords in bio
    female_keywords = [
        "girl", "she", "queen", "princess", "lady", "di", "sis", "bhabhi",
        "beauty", "cute", "angel", "doll", "fashion", "makeup", "love",
        "mom", "wife", "sister", "daughter", "fairy", "diva"
    ]
    
    # BTS-related names/usernames (popular among girls)
    bts_related = [
        "bts", "army", "jungkook", "jimin", "taehyung", "v", "jin", "suga",
        "jhope", "rm", "kpop", "bangtan", "purple", "borobudur"
    ]
    
    # Common female emojis
    female_emojis = [
        "💕", "💖", "💗", "💓", "💞", "💜", "🌸", "🌺", "🌹", "💐",
        "✨", "🌟", "💋", "👑", "🎀", "🦋", "🐾", "🌈", "🍓", "🍒"
    ]
    
    # Convert all to lowercase for matching
    username_lower = username.lower()
    full_name_lower = full_name.lower() if full_name else ""
    bio_lower = bio.lower() if bio else ""
    
    # Check username
    if any(name in username_lower for name in female_names + female_nicknames):
        return True
    if any(lastname in username_lower for lastname in female_lastnames):
        return True
    if any(bts in username_lower for bts in bts_related):
        return True
    
    # Check full name
    if full_name_lower:
        if any(name in full_name_lower for name in female_names):
            return True
        if any(lastname in full_name_lower for lastname in female_lastnames):
            return True
    
    # Check bio
    if bio_lower:
        if any(keyword in bio_lower for keyword in female_keywords):
            return True
        if any(emoji in bio for emoji in female_emojis):  # Emoji check in original bio
            return True
        if any(bts in bio_lower for bts in bts_related):
            return True
    
    # Regex for feminine patterns
    if re.search(r"[aiey]$", username_lower):  # Ends with 'a', 'i', 'e', 'y'
        return True
    if re.search(r"xx$", username_lower):  # Ends with 'xx' (common in girl usernames)
        return True
    
    # Fallback: No strong male indicators
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

# Main bot logic
def scrape_active_girls():
    logging.info("Bot started processing...")
    
    # Load existing data
    active_girls = load_json_data()
    
    # Target hashtag for reels (female-centric)
    hashtag = "beauty"  # Change to any hashtag like "fashion", "makeup", etc.
    
    # Scrape reels from hashtag
    try:
        posts = L.get_hashtag_posts(hashtag)
        for post in posts:
            # Only recent posts (last 24 hours)
            if post.date > datetime.now() - timedelta(hours=24):
                logging.info(f"Scraping comments from post: {post.shortcode}")
                
                # Get commenters
                for comment in post.get_comments():
                    username = comment.owner.username
                    
                    # Skip if already in list
                    if username in active_girls:
                        continue
                    
                    # Get profile details (public only)
                    try:
                        profile = instaloader.Profile.from_username(L.context, username)
                        full_name = profile.full_name
                        bio = profile.biography
                    except Exception as e:
                        full_name = None
                        bio = None
                        logging.warning(f"Could not fetch profile for {username}: {e}")
                    
                    # Check if likely female
                    if is_likely_female(username, full_name, bio):
                        active_girls.append(username)
                        logging.info(f"Found active girl: @{username} (Name: {full_name or 'N/A'})")
                    
                    # Save every 5 users
                    if len(active_girls) % 5 == 0:
                        save_json_data(active_girls)
                        logging.info(f"Saved {len(active_girls)} users to {JSON_FILE}")
                    
                    # Check if 20 users reached
                    if len(active_girls) >= 20:
                        logging.info(f"Reached 20 active girls: {active_girls}")
                        return active_girls
                
                # Random delay to avoid detection
                time.sleep(random.uniform(5, 15))  # Increased range for safety
    
    except Exception as e:
        logging.error(f"Error occurred: {e}")
    
    finally:
        save_json_data(active_girls)
        logging.info(f"Bot finished. Total active girls found: {len(active_girls)}")
    
    return active_girls

if __name__ == "__main__":
    active_girls = scrape_active_girls()
    print(f"Check 'bot_progress.log' for progress and '{JSON_FILE}' for results!")
