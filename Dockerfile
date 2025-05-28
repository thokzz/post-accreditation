FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including curl for health checks
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads/signatures uploads/software_proofs uploads/floor_plans uploads/general
RUN mkdir -p app/static/css app/static/js app/static/images
RUN mkdir -p instance

# Copy and make startup script executable
COPY startup.sh /app/startup.sh
RUN chmod +x /app/startup.sh

# Set environment variables
ENV FLASK_APP=run.py
ENV PYTHONPATH=/app

# Create a non-root user and set permissions
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app/static

USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Use startup script as the default command
CMD ["/app/startup.sh"]
