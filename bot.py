import instaloader
from instaloader import Hashtag
from datetime import datetime, timedelta
import json
import logging
import time
import random
import re
from typing import List

# Configure logging
logging.basicConfig(
    filename="bot_progress.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Configure Instaloader with modern parameters
L = instaloader.Instaloader(
    max_connection_attempts=3,
    request_timeout=60,
    sleep=True,
    sleep_time=300,  # 5 minutes between batches
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
)

# Improved proxy configuration (uncomment if needed)
# L.context._session.proxies = {
#     "http": "http://username:password@proxy:port",
#     "https": "http://username:password@proxy:port"
# }

JSON_FILE = "active_girls.json"

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

def load_json_data() -> List[str]:
    try:
        with open(JSON_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_json_data(data: List[str]):
    with open(JSON_FILE, "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def handle_hashtag_errors(hashtag: str):
    """Handle rate limits and temporary bans"""
    logger.warning(f"Potential rate limit detected for #{hashtag}")
    sleep_time = random.randint(600, 1200)  # 10-20 minutes
    logger.info(f"Sleeping for {sleep_time//60} minutes")
    time.sleep(sleep_time)

def get_hashtag_posts_safe(hashtag: str):
    """Safe method to get hashtag posts with modern Instaloader API"""
    try:
        hashtag_obj = Hashtag.from_name(L.context, hashtag)
        return hashtag_obj.get_posts()
    except instaloader.exceptions.QueryReturnedNotFoundException:
        logger.error(f"Hashtag #{hashtag} not found or banned")
        return []
    except instaloader.exceptions.ConnectionException as e:
        logger.error(f"Connection error for #{hashtag}: {str(e)}")
        handle_hashtag_errors(hashtag)
        return []

def scrape_active_girls():
    logger.info("Bot started processing...")
    
    active_girls = load_json_data()
    hashtags = ["beauty", "fashion", "makeup", "reelsindia", "bts", "girls"]
    
    for hashtag in hashtags:
        if len(active_girls) >= 20:
            break
            
        logger.info(f"Processing hashtag: #{hashtag}")
        posts = get_hashtag_posts_safe(hashtag)
        
        if not posts:
            continue
            
        try:
            for post in posts:
                if len(active_girls) >= 20:
                    break
                    
                if post.date < datetime.now() - timedelta(hours=24):
                    continue
                    
                logger.info(f"Processing post: {post.shortcode}")
                
                try:
                    comments = post.get_comments()
                except Exception as e:
                    logger.error(f"Error getting comments: {str(e)}")
                    continue
                
                for comment in comments:
                    try:
                        username = comment.owner.username
                        if username in active_girls:
                            continue
                            
                        # Add random delay between profile checks
                        time.sleep(random.uniform(5, 15))
                        
                        profile = instaloader.Profile.from_username(L.context, username)
                        if is_likely_female(username, profile.full_name, profile.biography):
                            active_girls.append(username)
                            logger.info(f"Added {username} - Total: {len(active_girls)}")
                            save_json_data(active_girls)
                            
                    except instaloader.exceptions.ProfileNotExistsException:
                        continue
                    except Exception as e:
                        logger.error(f"Error processing comment: {str(e)}")
                        continue
                        
                # Random delay between posts
                time.sleep(random.uniform(15, 30))
        
        except Exception as e:
            logger.error(f"Critical error processing #{hashtag}: {str(e)}")
            handle_hashtag_errors(hashtag)
            continue
            
    logger.info(f"Completed. Total found: {len(active_girls)}")
    return active_girls

if __name__ == "__main__":
    try:
        active_girls = scrape_active_girls()
        print(f"Results saved to {JSON_FILE}")
    except KeyboardInterrupt:
        logger.warning("Process interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
