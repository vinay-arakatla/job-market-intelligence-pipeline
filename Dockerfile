# Dockerfile for Job Market Intelligence Pipeline

FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories
RUN mkdir -p logs data/raw data/processed airflow

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV AIRFLOW_HOME=/app/airflow

# Expose Airflow port
EXPOSE 8080

# Default command
CMD ["python", "setup.py"]
