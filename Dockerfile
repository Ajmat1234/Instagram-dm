# Alpine-based image use करें (Railway compatible)
FROM ollama/ollama:latest

# System dependencies
RUN apk add --no-cache python3 py3-pip curl

# Python packages
RUN pip3 install fastapi uvicorn python-ollama

# Copy files
COPY . /app
WORKDIR /app

# Permissions fix
RUN chmod +x start.sh

# Ports
EXPOSE 8000

# Start command
CMD ["./start.sh"]
