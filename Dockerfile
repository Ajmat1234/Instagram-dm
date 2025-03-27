FROM node:20

# सभी जरूरी dependencies इंस्टॉल करें
RUN apt-get update && \
    apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    lsb-release \
    xdg-utils

# Google Chrome स्थापित करें
RUN wget -q -O- https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor > /etc/apt/trusted.gpg.d/google.gpg && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable --no-install-recommends

# Python और pip इंस्टॉल करें
RUN apt-get install -y python3 python3-pip

# Python dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Node dependencies
COPY package*.json ./
RUN npm install

# एप्लिकेशन फाइल्स कॉपी करें
COPY . .

# Permissions सेट करें
RUN chmod -R 755 /usr/bin/google-chrome-stable

# PM2 से दोनों प्रोसेस चलाएं
RUN npm install pm2 -g
CMD ["pm2-runtime", "ecosystem.config.js"]
