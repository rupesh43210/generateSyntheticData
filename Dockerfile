# Lightweight Dockerfile for PII Generator (no SQL Server support)
FROM python:3.11-slim

# Install basic dependencies
RUN apt-get update && apt-get install -y \
    curl \
    unixodbc \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -g 1000 piiuser && \
    useradd -r -u 1000 -g piiuser piiuser

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir flask-socketio python-socketio

# Copy application code
COPY --chown=piiuser:piiuser . /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_APP=web_app.py \
    OUTPUT_MODE=file

# Create necessary directories
RUN mkdir -p /app/logs /app/output /app/data/cache && \
    chown -R piiuser:piiuser /app

# Install the package in development mode
RUN pip install -e .

# Copy and set permissions for entrypoint script
COPY --chown=piiuser:piiuser docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Switch to non-root user
USER piiuser

# Expose ports
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5001/api/system/status || exit 1

# Set entrypoint - temporarily bypassed for testing
# ENTRYPOINT ["docker-entrypoint.sh"]

# Default command - using docker web app
CMD ["python", "web_app_docker.py"]