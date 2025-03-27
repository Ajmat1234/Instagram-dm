FROM node:20

# --------- System Dependencies ---------
RUN apt-get update && apt-get install -y \
    chromium \
    python3 \
    python3-pip \
    xvfb \
    --no-install-recommends

# --------- Python Setup ---------
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# --------- Node Setup ---------
COPY package*.json .
RUN npm install --production

# --------- App Copy ---------
COPY . .

# --------- Run Commands ---------
CMD ["sh", "-c", "Xvfb :99 -screen 0 1024x768x24 & gunicorn main:app -b 0.0.0.0:${PORT} & node bot.js"]
