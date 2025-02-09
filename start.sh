#!/bin/sh

# Ollama start करें
ollama serve &

# Wait for Ollama (with timeout)
timeout=30
while ! curl -s http://localhost:11434 >/dev/null; do
  sleep 1
  timeout=$((timeout-1))
  [ $timeout -le 0 ] && echo "Ollama timeout!" && exit 1
done

# Model download करें
ollama pull mistral || echo "Model pull failed, continuing..."

# FastAPI start करें
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
