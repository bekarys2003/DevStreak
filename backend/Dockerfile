# backend/Dockerfile
FROM python:3.11-slim

# 1) Create & switch to /app
WORKDIR /app

# 2) Copy requirements & install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3) Copy in your Django code
COPY . .

# 4) Expose port (for documentation; docker-compose does the real mapping)
EXPOSE 8000

# 5) Default command (you can override in compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
