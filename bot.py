from instabot import Bot
import time
from datetime import datetime

# ✅ Login Credentials
username = "forever_yours_74"
password = "Ajmat7377@"

# ✅ DM Message & GC Info
dm_message = "https://ig.me/j/AbadvPz94HkLPUro/"
excluded_gc_name = "SHANSKARI_BALAK 👻💯"
sent_users_file = "sent_users.txt"
max_daily_dms = 30

# ✅ Bot Initialization
bot = Bot()
bot.login(username=username, password=password)

# ✅ Pehle se DM bheje hue log ko load karo
def load_sent_users():
    try:
        with open(sent_users_file, "r") as file:
            return set(file.read().splitlines())
    except FileNotFoundError:
        return set()

# ✅ Naye DM bhejne ke baad user ko save karo
def save_sent_user(username):
    with open(sent_users_file, "a") as file:
        file.write(f"{username}\n")

# ✅ Apne GC ko exclude karne ka function
def exclude_gc_members():
    excluded_members = []
    try:
        excluded_members = bot.get_user_followers(excluded_gc_name)
    except Exception as e:
        print(f"⚠️ Error while fetching excluded GC members: {e}")
    return set(excluded_members)

# ✅ DM bhejne wala function
def send_dm_to_users(users, excluded_members):
    sent_users = load_sent_users()
    count = 0

    for user in users:
        if user not in sent_users and user not in excluded_members and count < max_daily_dms:
            try:
                bot.send_message(dm_message, [user])
                print(f"✅ Message sent to: {user}")
                save_sent_user(user)
                count += 1
                time.sleep(10 + (5 * count))  # Random delay for safety
            except Exception as e:
                print(f"❌ Error sending to {user}: {e}")

        if count >= max_daily_dms:
            print("🎉 Daily DM limit reached. Sleeping for 24 hours...")
            time.sleep(86400)  # Sleep for 24 hours
            break

# ✅ Group se users ko fetch karne ka function
def get_users_from_gc(group_id):
    try:
        users = bot.get_user_followers(group_id)
        return users
    except Exception as e:
        print(f"⚠️ Error fetching users from group {group_id}: {e}")
        return []

# ✅ Apne GC ko exclude karo
excluded_members = exclude_gc_members()

# ✅ Dusre GC ke IDs jahan se members ko DM karna hai
group_ids = ["group_id_1", "group_id_2"]  # Apne target GCs ke IDs yahan daalo

# ✅ Main Loop
while True:
    for group_id in group_ids:
        users = get_users_from_gc(group_id)
        send_dm_to_users(users, excluded_members)

    print("😴 Sleeping for 24 hours before next run...")
    time.sleep(86400)  # 24 hours sleep
