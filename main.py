from instagrapi import Client
import time
import random
import json

# Instagram Credentials
USERNAME = "zehra.bloom_"
PASSWORD = "Ajmat1234@"

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
        # Normal login without OTP
        bot.login(USERNAME, PASSWORD)
        return True
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False

# Function to get target users from feed reels
def get_target_users():
    target_users = set()

    # Fetch 10 latest posts from the user's feed
    feed_reels = bot.user_medias(bot.user_id, amount=10)  # Change user_feed to user_medias
    for reel in feed_reels:
        try:
            comments = bot.media_comments(reel.id, amount=50)  # Check the first 50 comments
            for comment in comments:
                if "girl" in comment.user.username.lower() or "queen" in comment.user.username.lower() or comment.user.username.endswith("a"):
                    target_users.add(comment.user.username)
        except:
            pass

    # Return list of target users
    return list(target_users)

# Function to send DMs
def send_dm(user):
    DM_MESSAGES = [
        "Hi!", "Hello!", "Hey there!", "What's up?", "Good morning!"
    ]
    message = random.choice(DM_MESSAGES)  # Random message selection
    try:
        bot.direct_send(message, [bot.user_id_from_username(user)])
        print(f"✅ Message sent to {user}")
    except Exception as e:
        print(f"❌ DM failed for {user}, Error: {e}")

# Main Execution
if handle_login():
    print(f"\n✅ Successfully Logged In! User ID: {bot.user_id}")
    bot.dump_settings("ig_session.json")  # Save session

    # Fetch target users and send DMs
    target_users = get_target_users()
    for user in target_users:
        send_dm(user)
        time.sleep(60)  # Wait for 1 minute before sending the next DM

else:
    print("❌ Login failed. Please check credentials.")
