# Base image set karein (Ubuntu latest)
FROM ubuntu:latest

# System update karein aur required packages install karein
RUN apt-get update && apt-get install -y \
    python3 python3-pip curl git && \
    apt-get clean

# Python aur Pip version check karein
RUN python3 --version && pip3 --version

# FastAPI aur required Python packages install karein
RUN pip3 install --no-cache-dir fastapi uvicorn requests

# Ollama install karein
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Model ko load karein
RUN ollama pull llama3

# Port expose karein
EXPOSE 8000 11434

# Pehle Ollama server start karein, fir FastAPI app start karein
CMD ollama serve & uvicorn main:app --host 0.0.0.0 --port 8000
