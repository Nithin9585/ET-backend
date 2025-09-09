# Minimal Dockerfile for Railway deployment
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install only essential system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install minimal dependencies
COPY requirements.minimal.txt .
RUN pip install --no-cache-dir -r requirements.minimal.txt \
    && python -m spacy download en_core_web_sm --quiet \
    && pip cache purge

# Copy application files
COPY api/ ./api/
COPY ocr/ ./ocr/
COPY pii_detection/ ./pii_detection/
COPY config/ ./config/

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production
ENV DEBUG=false
ENV OCR_GPU_ENABLED=false
ENV LOG_LEVEL=INFO
ENV MAX_FILE_SIZE=10485760

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8000

# Start the application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
