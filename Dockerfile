# Base Image
FROM mcr.microsoft.com/playwright/python:v1.39.0

# Set working directory
WORKDIR /app

# Copy Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy Node dependencies
COPY package*.json .
RUN npm install --production

# Copy all project files
COPY . .

# Install Playwright browsers
RUN playwright install

# Run Flask and Node
CMD ["sh", "-c", "gunicorn main:app -b 0.0.0.0:$PORT & node bot.js"]
