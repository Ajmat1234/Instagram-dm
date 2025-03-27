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
# Dockerfile में ये लाइन जोड़ें
RUN echo "PORT Value: $PORT"  # Build logs में पोर्ट वैल्यू चेक करें

# --------- App Copy ---------
COPY . .

# --------- Run Command ---------
# गलत:
CMD ["sh", "-c", "Xvfb :99 -screen 0 1024x768x24 & gunicorn main:app -b 0.0.0.0:${PORT} & node bot.js"]
