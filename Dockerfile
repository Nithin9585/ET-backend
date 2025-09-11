# Minimal Dockerfile for Railway deployment - using stable base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies for OpenCV and computer vision
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    curl \
    wget \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    libegl1-mesa-dev \
    libgles2-mesa-dev \
    libxrandr2 \
    libxinerama1 \
    libxcursor1 \
    libxi6 \
    fonts-dejavu-core \
    fonts-dejavu-extra \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install all dependencies from requirements.txt (Python 3.10 compatible)
RUN pip install --no-cache-dir -r requirements.txt \
    && python -m spacy download en_core_web_sm --quiet \
    && pip cache purge


# Copy application files
COPY api/ ./api/
COPY ocr/ ./ocr/
COPY pii_detection/ ./pii_detection/
COPY config/ ./config/
COPY models/ ./models/

# Download spaCy large model for PII detection
RUN python -m spacy download en_core_web_lg

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production
ENV DEBUG=false
ENV OCR_GPU_ENABLED=false
ENV LOG_LEVEL=INFO
ENV MAX_FILE_SIZE=10485760
# OpenCV headless mode
ENV OPENCV_IO_ENABLE_OPENEXR=0
ENV OPENCV_IO_ENABLE_JASPER=0
ENV QT_QPA_PLATFORM=offscreen

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8080
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]