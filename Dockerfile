FROM node:20

# ================= System Dependencies =================
RUN apt-get update && apt-get install -y \
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

# ================= Chrome Install =================
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -x google-chrome-stable_current_amd64.deb /tmp/chrome \
    && mv /tmp/chrome/opt/google/chrome/chrome /usr/bin/google-chrome-stable \
    && rm -rf /tmp/chrome google-chrome-stable_current_amd64.deb

# ================= PM2 Setup =================
ENV NPM_CONFIG_PREFIX=/home/node/.npm-global
ENV PATH=$PATH:/home/node/.npm-global/bin
RUN npm install -g pm2@latest --unsafe-perm

# ================= App Setup =================
USER node
WORKDIR /app
COPY --chown=node:node package*.json ./
RUN npm install --production
COPY --chown=node:node . .

# ================= Final Run =================
CMD ["sh", "-c", "Xvfb :99 -screen 0 1024x768x24 & pm2-runtime ecosystem.config.js"]
