# Python base image (Debian-based)
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y curl && \
    curl -fsSL https://ollama.com/install.sh | sh

# Install Python packages
RUN pip3 install fastapi uvicorn python-ollama

# Copy app files
COPY main.py start.sh /app/
WORKDIR /app

# Make script executable
RUN chmod +x start.sh

# Expose ports
EXPOSE 8000 11434

# Start command
CMD ["./start.sh"]
