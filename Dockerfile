# Ollama base image
FROM ollama/ollama:latest

# Install Python and dependencies
RUN apk add --no-cache python3 py3-pip curl
RUN pip3 install fastapi uvicorn requests python-ollama

# Copy app files
COPY main.py start.sh /app/
WORKDIR /app

# Make script executable
RUN chmod +x start.sh

# Expose required ports
EXPOSE 8000 11434

# Start command
CMD ["./start.sh"]
