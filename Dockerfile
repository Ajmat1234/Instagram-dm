# Base image with Node.js and Python
FROM node:20

# Install system dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    python3 \
    python3-pip \
    xvfb \
    --no-install-recommends

# Python dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Node.js dependencies
COPY package*.json .
RUN npm install --production

# App copy
COPY . .

# Run Flask and Node.js together
CMD ["sh", "-c", "Xvfb :99 -screen 0 1024x768x24 & gunicorn main:app --bind 0.0.0.0:${PORT} & node bot.js"]
