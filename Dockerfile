# Environment variable $PORT ko set karna
ENV PORT 8000

CMD ["uvicorn", "your_app_name:app", "--host", "0.0.0.0", "--port", "$PORT"]
