# नया अपडेटेड Dockerfile
FROM node:20

# Python 3 और pip3 इंस्टॉल करें
RUN apt-get update && apt-get install -y python3 python3-pip

# Chrome dependencies और अन्य जरूरी पैकेजेस
RUN apt-get install -y \
  wget \
  curl \
  gnupg \
  unzip \
  gcc \
  python3-dev \
  libgbm-dev \
  libxshmfence-dev \
  libnss3-dev \
  libasound2 \
  libatk-bridge2.0-0 \
  libx11-xcb1 \
  libxcomposite1 \
  libxdamage1 \
  libxfixes3 \
  libxrandr2 \
  libdrm2 \
  libgbm1 \
  libgtk-3-0 \
  libxkbcommon0 \
  --no-install-recommends

# Google Chrome स्थापित करें
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
  && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
  && apt-get update \
  && apt-get install -y google-chrome-stable fonts-ipafont-gothic fonts-wqy-zenhei fonts-thai-tlwg fonts-kacst fonts-freefont-ttf \
  && rm -rf /var/lib/apt/lists/*

# Python dependencies इंस्टॉल करें
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Node dependencies इंस्टॉल करें
COPY package*.json ./
RUN npm install

# एप्लिकेशन फाइल्स कॉपी करें
COPY . .

# Flask और Node बॉट एक साथ चलाएं (PM2 का उपयोग)
RUN npm install pm2 -g
CMD ["pm2-runtime", "ecosystem.config.js"]
