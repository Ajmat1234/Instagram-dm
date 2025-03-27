FROM python:3.11-slim
RUN apt-get update && apt-get install -y libnss3 libatk-bridge2.0-0 libgtk-4-dev libgraphene-1.0-0
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:10000"]
