# Ubuntu base image use karein
FROM ubuntu:latest

# System update karein aur zaroori packages install karein
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv curl git && \
    apt-get clean

# Python virtual environment create karein aur activate karein
RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Python aur Pip version check karein
RUN python3 --version && pip --version

# FastAPI aur zaroori Python libraries install karein
RUN pip install --no-cache-dir fastapi uvicorn requests

# Ollama install karein
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Port expose karein
EXPOSE 8000 11434

# Command to start Ollama and API together
CMD bash -c "ollama serve & sleep 10 && ollama pull llama3 && uvicorn main:app --host 0.0.0.0 --port 8000"
