# Minimal Dockerfile for Railway deployment - using stable base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install only essential system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install minimal dependencies directly
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    "uvicorn[standard]==0.24.0" \
    python-multipart==0.0.6 \
    python-dotenv==1.0.0 \
    pydantic-settings==2.0.3 \
    pdf2image==1.17.0 \
    pillow==10.1.0 \
    numpy==1.24.3 \
    opencv-python-headless==4.8.1.78 \
    easyocr==1.7.0 \
    presidio-analyzer==2.2.33 \
    spacy==3.7.2 \
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
