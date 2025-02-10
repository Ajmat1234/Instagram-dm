# Ollama base image se shuru karein
FROM docker.io/ollama/ollama:latest

# Package list update karein aur Python aur pip install karein
RUN apt-get update && apt-get install -y python3 python3-pip

# Zaroori Python packages install karein
RUN pip3 install fastapi uvicorn requests

# Default PORT environment variable set karein
ENV PORT=8000

# FastAPI app ke liye port expose karein
EXPOSE 8000

# Command jo app ko run kare
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT}
