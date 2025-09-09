# Optimized Dockerfile for Railway deployment
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies in one layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    poppler-utils \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Copy and install Python dependencies first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && python -m spacy download en_core_web_sm \
    && rm -rf ~/.cache/pip

# Copy only necessary application files
COPY api/ ./api/
COPY ocr/ ./ocr/
COPY pii_detection/ ./pii_detection/
COPY config/ ./config/
COPY start_server.py .

# Create production environment file
RUN echo "ENVIRONMENT=production" > .env && \
    echo "DEBUG=false" >> .env && \
    echo "OCR_GPU_ENABLED=false" >> .env && \
    echo "LOG_LEVEL=INFO" >> .env && \
    echo "MAX_FILE_SIZE=10485760" >> .env && \
    echo "ALLOWED_EXTENSIONS=jpg,jpeg,png,pdf,tiff,bmp" >> .env

# Create necessary directories and set permissions
RUN mkdir -p logs models \
    && chmod -R 755 /app

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Expose port (Railway uses dynamic PORT)
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=2 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Start the application with uvicorn directly (faster startup)
CMD uvicorn api.main:app --host 0.0.0.0 --port $PORT --workers 1
