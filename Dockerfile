FROM node:20-slim

# ============ System Dependencies ============
RUN apt-get update -o Acquire::CheckValid-Until=false -o Acquire::Check-Date=false && \
    apt-get install -y --no-install-recommends \
    wget \
    python3 \
    xvfb \
    libgl1 \
    libnss3 \
    libxss1 \
    libasound2 \
    libxtst6 \
    libgbm1 \
    && rm -rf /var/lib/apt/lists/*

# ============ Chrome Install ============ 
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -x google-chrome-stable_current_amd64.deb /tmp/chrome && \
    mv /tmp/chrome/opt/google/chrome/chrome /usr/bin/google-chrome-stable && \
    rm -rf /tmp/chrome google-chrome-stable_current_amd64.deb

# ============ PM2 Global Install ============
RUN npm install -g pm2@latest --unsafe-perm

# ============ App Setup ============ 
WORKDIR /app
COPY package*.json .
RUN npm install --production

COPY . .

# ============ Fix Permissions ============
RUN chmod +x /usr/bin/google-chrome-stable

# ============ Run Commands ============ 
ENV DISPLAY=":99" \
    CHROME_BIN="/usr/bin/google-chrome-stable"

CMD Xvfb :99 -screen 0 1024x768x24 & pm2-runtime ecosystem.config.js
