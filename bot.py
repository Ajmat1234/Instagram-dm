from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import random
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def login():
    # ... existing code ...
    
    # Wait for login to complete
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Welcome')]"))
    )
    print("✅ Successfully Logged In!")
# Instagram Credentials
USERNAME = "zehra.bloom_"
PASSWORD = "Ajmat1234@"

# Messages List
DM_MESSAGES = [
    "Hi!", "Hello!", "Hey there!", "What's up?", "Good morning!"
]

# Filtering Criteria
nicknames = ["cutie", "pookie", "queen", "princess", "darling", "babe"]
common_endings = ["a", "ie", "y", "xo", "luv", "babe", "angel", "lovebug"]

# Start WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Headless Mode
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

# Login Function
def login():
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(5)

    username_input = driver.find_element(By.NAME, "username")
    password_input = driver.find_element(By.NAME, "password")

    username_input.send_keys(USERNAME)
    password_input.send_keys(PASSWORD)
    password_input.send_keys(Keys.RETURN)

    time.sleep(5)  # Wait for login
    print("✅ Successfully Logged In!")

# Function to find target users
def find_target_users(username):
    driver.get(f"https://www.instagram.com/{username}/")
    time.sleep(5)

    try:
        # Open Following List
        following_btn = driver.find_element(By.XPATH, "//a[contains(@href,'/following/')]")
        following_btn.click()
        time.sleep(5)

        # Scroll through following list and collect users
        target_users = set()
        for _ in range(5):  # Scroll 5 times
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
            time.sleep(2)

        # Extract usernames
        users = driver.find_elements(By.XPATH, "//a[contains(@href, '/')]")
        for user in users:
            username = user.text.lower()
            if any(nick in username for nick in nicknames) or any(username.endswith(end) for end in common_endings):
                target_users.add(username)

        return list(target_users)

    except Exception as e:
        print(f"❌ Error finding users: {e}")
        return []

# Function to send DM
def send_dm(user):
    try:
        message = random.choice(DM_MESSAGES)

        # Open DM Page
        driver.get(f"https://www.instagram.com/direct/t/{user}/")
        time.sleep(5)

        # Type and Send Message
        message_box = driver.find_element(By.XPATH, "//textarea")
        message_box.send_keys(message)
        message_box.send_keys(Keys.RETURN)

        print(f"✅ Message sent to {user}")
        time.sleep(60)  # 1 min delay
    except Exception as e:
        print(f"❌ Failed to send DM to {user}: {e}")

# Main Function
def main():
    login()

    usernames = ["bezubanlafz__", "editz_lover___05", "salu____0209"]

    for username in usernames:
        target_users = find_target_users(username)

        if target_users:
            print(f"✅ Found {len(target_users)} target users from {username}")
            for user in target_users[:10]:  # Send DM to first 10 users
                send_dm(user)

    print("⏳ Sleeping for 3 hours before restarting...")
    time.sleep(10800)  # Sleep for 3 hours

# Run the bot
while True:
    main()
