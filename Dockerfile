# Ollama base image se shuru karein
FROM docker.io/ollama/ollama:latest

# System dependencies aur Python setup
RUN apt-get update && \
    apt-get install -y python3 python3-pip curl && \
    pip3 install fastapi uvicorn requests python-ollama

# Ollama server start karke Mistral model pull karein
RUN (ollama serve > /dev/null 2>&1 &) && \
    sleep 10 && \  # Server start hone ke liye wait
    ollama pull mistral

# App ka code copy karein
COPY main.py /app/main.py
WORKDIR /app

# Final command - Ollama aur FastAPI ek saath chalayein
CMD sh -c "ollama serve & uvicorn main:app --host 0.0.0.0 --port 8000"
