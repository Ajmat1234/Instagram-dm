RUN apt update && apt install -y wget unzip curl xvfb \
    && wget -q "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb" -O chrome.deb \
    && apt install -y ./chrome.deb \
    && rm chrome.deb \
    && wget -q "https://chromedriver.storage.googleapis.com/LATEST_RELEASE" -O latest_version.txt \
    && CHROME_VERSION=$(cat latest_version.txt) \
    && wget -q "https://chromedriver.storage.googleapis.com/${CHROME_VERSION}/chromedriver_linux64.zip" -O chromedriver.zip \
    && unzip chromedriver.zip \
    && mv chromedriver /usr/local/bin/ \
    && rm -f chromedriver.zip latest_version.txt
