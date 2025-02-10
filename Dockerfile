FROM ubuntu:22.04

# Install dependencies
RUN apt update && apt install -y wget unzip curl xvfb python3 python3-pip \
    && wget -q "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb" -O chrome.deb \
    && apt install -y ./chrome.deb \
    && rm chrome.deb \
    && wget -q "https://chromedriver.storage.googleapis.com/LATEST_RELEASE" -O latest_version.txt \
    && CHROME_VERSION=$(cat latest_version.txt) \
    && wget -q "https://chromedriver.storage.googleapis.com/${CHROME_VERSION}/chromedriver_linux64.zip" -O chromedriver.zip \
    && unzip chromedriver.zip \
    && mv chromedriver /usr/local/bin/ \
    && rm -f chromedriver.zip latest_version.txt

# Install Python libraries
RUN pip3 install requests

# Add your bot script
COPY bot.py /bot.py

# Make the bot.py executable
RUN chmod +x /bot.py

# Run the bot script continuously
CMD ["python3", "/bot.py"]
