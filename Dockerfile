# Base image set karein (Ollama ke saath)
FROM ubuntu:latest

# System update aur zaroori packages install karein
RUN apt-get update && apt-get install -y \
    python3 python3-pip curl && \
    apt-get clean

# FastAPI aur zaroori Python libraries install karein
RUN pip3 install fastapi uvicorn requests

# Ollama install karein
RUN curl -fsSL https://ollama.ai/install.sh | sh

# AI model ko pull karein (Llama3 ka example diya hai)
RUN ollama pull llama3

# Default PORT set karein
ENV PORT=8000

# Port expose karein
EXPOSE 8000 11434

# Pehle Ollama server start karein, fir FastAPI app start karein
CMD ollama serve & uvicorn main:app --host 0.0.0.0 --port ${PORT}
