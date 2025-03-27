# Dockerfile
FROM node:20

# Install required packages and Google Chrome
RUN apt-get update && apt-get install -y \
  wget \
  curl \
  gnupg \
  unzip \
  && apt-get clean

# Install Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
  && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
  && apt-get update \
  && apt-get install -y google-chrome-stable \
  && apt-get clean

# Install Node dependencies
COPY package*.json ./
RUN npm install

# Copy all files
COPY . .

# Start application
CMD ["node", "bot.js"]
