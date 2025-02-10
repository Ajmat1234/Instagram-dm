RUN wget -qO- "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json" | \
    jq -r '.channels.Stable.version' > chrome_version.txt && \
    CHROME_VERSION=$(cat chrome_version.txt) && \
    wget -q "https://chromedriver.storage.googleapis.com/${CHROME_VERSION}/chromedriver_linux64.zip" -O chromedriver.zip && \
    unzip chromedriver.zip && \
    mv chromedriver /usr/local/bin/ && \
    rm -f chromedriver.zip chrome_version.txt
