# Base image use karein
FROM ubuntu:latest

# System update karein aur zaroori packages install karein
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv curl git && \
    apt-get clean

# Python virtual environment create karein
RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# FastAPI aur zaroori Python libraries install karein
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ollama install karein
RUN curl -fsSL https://ollama.ai/install.sh | bash

# Port expose karein
EXPOSE 8000 11434

# API aur Ollama ko start karne ke liye entrypoint script likhein
COPY main.py /app/main.py
WORKDIR /app

# CMD command fix karein
CMD bash -c "ollama serve & sleep 10 && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"
