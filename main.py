from instagrapi import Client
import time
import random
import json

# Instagram Credentials
USERNAME = "zehra.bloom_"
PASSWORD = "Ajmat1234@"

# Nicknames, common endings, and creative variations
nicknames = [
    "Cutie", "Pookie", "Queen", "Princess", "Darling", "Babe", "Sweetheart", "Honey", "Angel", 
    "Sunshine", "Love", "Baby", "Gorgeous", "Sweetie", "Missy", "Lovely", "Diva", "Peaches", 
    "Cupcake", "Cherry", "Blossom", "Star", "Sparkle", "Babe", "Princess", "Cutiepie", 
    "Lovebug", "Sweetiepie", "Babycakes", "Honeybunch", "Darling"
]

common_endings = [
    "a", "ie", "y", "xoxo", "luv", "love", "xo", "babe", "cutiepie", "princess", 
    "angel", "lovebug", "sweetiepie", "babycakes", "honeybunch", "darling"
]

creative_variations = [
    "CuteAngel", "SweetiePie", "PrincessLove", "CutieQueen", "BabeSweet", "XoAngel"
]

# Realistic Device Setup
bot = Client()
bot.set_device({
    "app_version": "312.0.0.25.119",
    "android_version": 34,
    "android_release": "14.0.0",
    "dpi": "480dpi",
    "resolution": "1080x2400",
    "manufacturer": "samsung",
    "device": "SM-S918B",
    "model": "Galaxy S23 Ultra"
})

# Function to handle login
def handle_login():
    try:
        # Try to load session from file if it exists
        bot.load_settings("ig_session.json")
        print("\n✅ Loaded session successfully.")
        
        # Try a simple request to check if the session is valid
        bot.get_me()
        return True
    except Exception as e:
        print("\n❌ Session invalid or expired, logging in...")
        try:
            bot.login(USERNAME, PASSWORD)
            bot.dump_settings("ig_session.json")  # Save session after login
            return True
        except Exception as e:
            print(f"❌ Error during login: {str(e)}")
            return False

# Function to get target users from followers and comments
def get_target_users_from_url(urls):
    target_users = set()
    
    for url in urls:
        try:
            # Extract user ID from the URL
            username = url.split("instagram.com/")[1].split("?")[0]
            user_id = bot.user_id_from_username(username)

            # Fetch followers of the user
            followers = bot.user_followers(user_id, amount=100)  # Limit to 100 followers
            for follower in followers:
                if any(nickname.lower() in follower.username.lower() for nickname in nicknames) or any(follower.username.endswith(ending) for ending in common_endings):
                    target_users.add(follower.username)
            
            # Fetch latest 10 media and check comments
            feed_reels = bot.user_medias(user_id, amount=10)
            for reel in feed_reels:
                try:
                    comments = bot.media_comments(reel.id, amount=50)
                    for comment in comments:
                        if any(nickname.lower() in comment.user.username.lower() for nickname in nicknames) or any(comment.user.username.endswith(ending) for ending in common_endings):
                            target_users.add(comment.user.username)
                except Exception as e:
                    print(f"❌ Error fetching comments for reel {reel.id}: {e}")
                    pass

        except Exception as e:
            print(f"❌ Error processing URL {url}: {e}")
    
    return list(target_users)

# Function to send DMs
def send_dm(user):
    DM_MESSAGES = [
        "Hi!", "Hello!", "Hey there!", "What's up?", "Good morning!"
    ]
    message = random.choice(DM_MESSAGES)  # Random message selection
    try:
        print(f"\n✉️ Sending DM to {user}...")
        bot.direct_send(message, [bot.user_id_from_username(user)])
        print(f"✅ Message sent to {user}")
    except Exception as e:
        print(f"❌ DM failed for {user}, Error: {e}")

# Main Execution
def main():
    urls = [
        "https://www.instagram.com/bezubanlafz__?igsh=ZG8zZGRnNTVrejcx",
        "https://www.instagram.com/editz_lover___05?igsh=MTh4b3d5ZmJnYzdi",
        "https://www.instagram.com/salu____0209?igsh=ZWc2a2NjMGZsaGNt"
    ]

    if handle_login():
        print(f"\n✅ Successfully Logged In! User ID: {bot.user_id}")

        # Fetch target users and send DMs
        target_users = get_target_users_from_url(urls)
        if target_users:
            print(f"\nFound {len(target_users)} target users.")
            for user in target_users:
                send_dm(user)
                time.sleep(60)  # Wait for 1 minute before sending the next DM
        else:
            print("❌ No target users found.")
    else:
        print("❌ Login failed. Please check credentials.")

# Run the bot continuously
while True:
    main()
    time.sleep(1800)  # Sleep for 30 minutes before restarting the process
