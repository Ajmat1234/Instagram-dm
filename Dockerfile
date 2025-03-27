FROM node:20-bullseye # Debian-based for Chrome compatibility

# ==================== Chrome Installation ====================
# Official Google Chrome installation (Latest stable)
RUN apt-get update && apt-get install -y \
    curl gnupg ca-certificates \
    fonts-ipafont-gothic fonts-wqy-zenhei fonts-thai-tlwg fonts-kacst fonts-freefont-ttf \
    --no-install-recommends

RUN curl -sSL https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o chrome.deb && \
    apt-get install -y ./chrome.deb && \
    rm chrome.deb && \
    rm -rf /var/lib/apt/lists/*

# ==================== System Dependencies ====================
# All required libraries (Updated 2024)
RUN apt-get update && apt-get install -y \
    libgbm-dev libxshmfence-dev libgl1-mesa-glx libasound2 \
    libnss3-dev libxss1 libx11-xcb1 libdrm-dev libxtst6 \
    libatk-bridge2.0-0 libgtk-3-0 libxcomposite1 libxrandr2 \
    --no-install-recommends

# ==================== Python Setup ====================
RUN apt-get install -y python3 python3-pip gcc python3-dev
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# ==================== Node Setup ====================
COPY package*.json ./
RUN npm install --force

# ==================== User Permissions ====================
RUN groupadd -r chromeuser && useradd -r -g chromeuser -G audio,video chromeuser
RUN mkdir -p /home/chromeuser/Downloads && chown -R chromeuser:chromeuser /home/chromeuser
USER chromeuser

# ==================== Final Config ====================
COPY --chown=chromeuser:chromeuser . .
ENV CHROME_BIN=/usr/bin/google-chrome-stable
ENV PUPPETEER_SKIP_DOWNLOAD=true
EXPOSE 5000

CMD ["pm2-runtime", "ecosystem.config.js"]
