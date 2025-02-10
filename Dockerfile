# Step 1: Use a base image
FROM ubuntu:latest

# Step 2: Set environment variables (optional)
ENV DEBIAN_FRONTEND=noninteractive

# Step 3: Update and install dependencies
RUN apt update && apt install -y wget unzip curl xvfb

# Step 4: Download and install Google Chrome
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt install -y ./google-chrome-stable_current_amd64.deb && \
    rm -f google-chrome-stable_current_amd64.deb

# Step 5: Fetch the correct Chrome version and install ChromeDriver
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d '.' -f 1) && \
    wget -q "https://chromedriver.storage.googleapis.com/${CHROME_VERSION}.0.0/chromedriver_linux64.zip" -O chromedriver.zip && \
    unzip chromedriver.zip && \
    mv chromedriver /usr/local/bin/ && \
    rm -f chromedriver.zip

# Step 6: Set the working directory
WORKDIR /app

# Step 7: Copy bot script and requirements file
COPY . /app

# Step 8: Install Python dependencies
RUN apt install -y python3-pip && pip3 install -r requirements.txt

# Step 9: Set the entrypoint
CMD ["python3", "bot.py"]
