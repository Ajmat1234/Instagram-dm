#!/bin/sh

# Start Ollama in background
ollama serve &

# Wait until Ollama is ready
while ! curl -s http://localhost:11434 >/dev/null; do
  sleep 1
done

# Pull Mistral model
ollama pull mistral

# Start FastAPI
uvicorn main:app --host 0.0.0.0 --port 8000
