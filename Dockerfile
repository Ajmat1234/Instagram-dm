# =============== Stage 1: Base Setup =============== 
FROM node:20-slim as base

# Set working directory
WORKDIR /app

# =============== Stage 2: Builder =============== 
FROM base as builder

# Install system dependencies
RUN apt-get update -o Acquire::CheckValid-Until=false -o Acquire::Check-Date=false && \
    apt-get install -y --no-install-recommends \
    wget \
    python3 \
    python3-pip \
    gcc \
    python3-dev \
    libgl1 \
    libnss3 \
    libxss1 \
    libasound2 \
    libxtst6 \
    libgbm1 \
    fonts-freefont-ttf \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome manually
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -x google-chrome-stable_current_amd64.deb /tmp/chrome && \
    mv /tmp/chrome/opt/google/chrome/chrome /usr/bin/google-chrome-stable && \
    rm -rf /tmp/chrome google-chrome-stable_current_amd64.deb

# =============== Stage 3: Production =============== 
FROM base as production

# Copy system dependencies from builder
COPY --from=builder /usr/bin/google-chrome-stable /usr/bin/google-chrome-stable
COPY --from=builder /usr/lib/ /usr/lib/

# Python setup
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Node setup
COPY package*.json .
RUN npm install --production --force

# Add user and permissions
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Copy app files
COPY --chown=appuser:appuser . .

# Environment variables
ENV CHROME_BIN=/usr/bin/google-chrome-stable \
    PUPPETEER_SKIP_DOWNLOAD=true \
    DISPLAY=:99 \
    NODE_ENV=production

# PM2 setup
RUN npm install pm2 -g
CMD ["pm2-runtime", "ecosystem.config.js"]
