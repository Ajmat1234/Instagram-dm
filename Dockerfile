FROM node:20

# --------- System Dependencies ---------
RUN apt-get update && apt-get install -y \
    chromium \
    fonts-freefont-ttf \
    xvfb \
    --no-install-recommends

# --------- Python Setup (Flask के लिए) ---------
RUN apt-get install -y python3 python3-pip
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# --------- Node Setup ---------
COPY package*.json .
RUN npm install --production

# --------- App Copy ---------
COPY . .

# --------- Run Command ---------
CMD ["sh", "-c", "Xvfb :99 -screen 0 1024x768x24 & node bot.js & gunicorn main:app -b 0.0.0.0:${PORT}"]
