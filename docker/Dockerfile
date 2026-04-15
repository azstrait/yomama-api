FROM python:3.11-slim

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m appuser

WORKDIR /app

# Copy dependencies first for better layering
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

# Copy application code from root context
COPY app ./app
COPY docker/container-run.py ./container-run.py

# Copy default jokes.csv from repo into image
COPY data/jokes.csv ./app/default_jokes.csv

# Entrypoint script
COPY docker/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Default envs
ENV DATA_DIR=/data
ENV PORT=6262
ENV LOG_LEVEL=info
ENV DOWNLOADABLE_JOKES=false
ENV PYTHONUNBUFFERED=1

# Create data dir and set permissions
RUN mkdir -p /data && chown -R appuser:appuser /data /app

EXPOSE 6262

ENTRYPOINT ["/docker-entrypoint.sh"]