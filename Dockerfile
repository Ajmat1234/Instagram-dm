FROM node:20-bullseye # Slim image नहीं

# ================= System Dependencies =================
RUN apt-get update -o Acquire::CheckValid-Until=false \
    && apt-get install -y --no-install-recommends \
    wget \
    xvfb \
    libgl1 \
    libnss3 \
    libxss1 \
    libasound2 \
    libxtst6 \
    libgbm1 \
    fonts-freefont-ttf \
    && rm -rf /var/lib/apt/lists/*

# ================= Chrome Installation =================
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -x google-chrome-stable_current_amd64.deb /tmp/chrome \
    && mv /tmp/chrome/opt/google/chrome/chrome /usr/bin/google-chrome-stable \
    && rm -rf /tmp/chrome google-chrome-stable_current_amd64.deb

# ================= PM2 Setup =================
RUN npm install -g pm2@latest --unsafe-perm --scripts-prepend-node-path=true
ENV PATH="/usr/local/bin:${PATH}"

# ================= App Setup =================
WORKDIR /app
COPY package*.json .
RUN npm install --production
COPY . .

# ================= Permissions =================
RUN chmod 755 /usr/bin/google-chrome-stable

# ================= Startup Script =================
RUN echo '#!/bin/sh\nXvfb :99 -screen 0 1024x768x24 &\nexec pm2-runtime ecosystem.config.js' > /start.sh \
    && chmod +x /start.sh

CMD ["/start.sh"]
