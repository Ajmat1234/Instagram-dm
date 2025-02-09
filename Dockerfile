# Ollama base image se shuru karein
FROM docker.io/ollama/ollama:latest

# Package list update karein aur Python aur pip install karein
RUN apt-get update && apt-get install -y python3 python3-pip

# Zaroori Python packages install karein
RUN pip3 install fastapi uvicorn requests

# Default PORT environment variable set karein (agar Railway ya kisi cloud platform me deploy kar rahe hain)
ENV PORT 8000

# FastAPI app ke liye port expose karein
EXPOSE 8000

# Command jo app ko run kare
CMD ["uvicorn", "your_app_name:app", "--host", "0.0.0.0", "--port", "8000"]
