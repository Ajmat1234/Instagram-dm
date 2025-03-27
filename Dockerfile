FROM node:20

# System dependencies
RUN apt-get update -o Acquire::CheckValid-Until=false && \
    apt-get install -y \
    wget \
    xvfb \
    libgl1 \
    libnss3 \
    libxss1 \
    libasound2 \
    libxtst6 \
    libgbm1 \
    fonts-freefont-ttf \
    --no-install-recommends

# Chrome Installation (नया तरीका)
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && mkdir -p /tmp/chrome \
    && dpkg -x google-chrome-stable_current_amd64.deb /tmp/chrome \
    && mv /tmp/chrome/opt/google/chrome/chrome /usr/local/bin/chrome \
    && ln -s /usr/local/bin/chrome /usr/bin/google-chrome-stable \
    && rm -rf /tmp/chrome google-chrome-stable_current_amd64.deb

# Permissions Fix
RUN chmod 755 /usr/local/bin/chrome && chmod +x /usr/bin/google-chrome-stable

# PM2 Setup
RUN npm install -g pm2@latest --unsafe-perm

# App Setup
WORKDIR /app
COPY . .
RUN npm install --production

# Final Run Command
CMD ["sh", "-c", "Xvfb :99 -screen 0 1024x768x24 & pm2-runtime ecosystem.config.js"]
