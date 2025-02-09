# Ollama base image se shuru karein
FROM docker.io/ollama/ollama:latest

# Package list update aur Python/pip install
RUN apt-get update && apt-get install -y python3 python3-pip

# Python packages install
RUN pip3 install fastapi uvicorn requests

# PORT environment variable (Platform override ke liye taiyar)
ENV PORT=8000

# Port expose karein
EXPOSE $PORT

# Command with dynamic port
CMD uvicorn your_app_name:app --host 0.0.0.0 --port $PORT
