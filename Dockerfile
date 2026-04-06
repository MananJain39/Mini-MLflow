FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
COPY setup.py .

# Install python dependencies
RUN pip install --no-cache-dir -e .

COPY . .

# Setting up entrypoint script
RUN chmod +x docker/entrypoint.sh
ENTRYPOINT ["docker/entrypoint.sh"]

EXPOSE 8000
