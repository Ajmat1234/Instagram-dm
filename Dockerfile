# Ollama Base Image Use Karein
FROM ollama/ollama

# FastAPI Install Karein
RUN pip install fastapi uvicorn requests

# Model Load Karein
RUN ollama pull mistral

# Copy Application Files
COPY . /app
WORKDIR /app

# Run Server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
