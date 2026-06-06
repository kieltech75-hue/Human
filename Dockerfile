FROM python:3.11-slim

WORKDIR /app

# Install system deps for scipy if needed
RUN apt-get update && apt-get install -y --no-install-recommends build-essential gfortran libopenblas-dev liblapack-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Default command runs health check
CMD ["python", "scripts/health_check.py"]
