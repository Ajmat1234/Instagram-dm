# Ollama base image se shuru karein
FROM docker.io/ollama/ollama:latest

# Python aur packages install karein
RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip3 install fastapi uvicorn requests python-ollama

# Mistral model pre-download karein
RUN ollama pull mistral

# App ka code copy karein
COPY main.py /app/main.py
WORKDIR /app

# Ollama server aur FastAPI ek saath run karein
CMD sh -c "ollama serve & uvicorn main:app --host 0.0.0.0 --port 8000"
