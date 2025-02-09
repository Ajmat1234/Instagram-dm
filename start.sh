#!/bin/sh

# Ollama server start करें
ollama serve &

# Wait for Ollama to be ready
until curl -s http://localhost:11434 >/dev/null; do
  sleep 1
done

# Mistral model डाउनलोड करें
ollama pull mistral

# FastAPI app start करें
uvicorn main:app --host 0.0.0.0 --port 8000
