FROM node:20-slim

# System dependencies
RUN apt-get update -o Acquire::CheckValid-Until=false -o Acquire::Check-Date=false && \
    apt-get install -y --no-install-recommends \
    wget \
    python3 \
    python3-venv \
    libgl1 \
    libnss3 \
    libxss1 \
    libasound2 \
    libxtst6 \
    libgbm1 \
    && rm -rf /var/lib/apt/lists/*

# Chrome install
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -x google-chrome-stable_current_amd64.deb /tmp/chrome && \
    mv /tmp/chrome/opt/google/chrome/chrome /usr/bin/google-chrome-stable && \
    rm -rf /tmp/chrome google-chrome-stable_current_amd64.deb

# Python virtualenv
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Node setup
COPY package*.json .
RUN npm install --production

# App setup
USER node
COPY --chown=node:node . .

# Environment
ENV CHROME_BIN=/usr/bin/google-chrome-stable \
    PUPPETEER_SKIP_DOWNLOAD=true \
    NODE_ENV=production

CMD ["pm2-runtime", "ecosystem.config.js"]
