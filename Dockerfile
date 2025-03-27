FROM python:3.11-slim

# Playwright और dependencies इंस्टॉल करो
RUN apt-get update && apt-get install -y libnss3 libatk-bridge2.0-0 libgtk-4-dev libgraphene-1.0-0

# वर्किंग डायरेक्ट्री सेट करो
WORKDIR /app

# फाइल्स कॉपी करो
COPY . .

# requirements.txt से dependencies इंस्टॉल करो
RUN pip install -r requirements.txt

# Playwright इंस्टॉल करो
RUN playwright install --with-deps

# ऐप चलाओ
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:10000"]
