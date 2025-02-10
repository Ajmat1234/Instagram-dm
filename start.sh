#!/bin/bash

# Start Ollama
ollama serve &

# Wait for Ollama server
while ! curl -s http://localhost:11434; do
  sleep 1
done

# Download model
ollama pull mistral || echo "Model pull failed, continuing..."

# Start FastAPI
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
