# PII Backend - Intelligent Document Processing API

A production-ready FastAPI backend service for OCR processing, signature detection, PII identification, and image recognition with AI-powered validation.



https://github.com/user-attachments/assets/470d9c8a-50f3-401c-b9bd-7127d91a12e5



## 🎯 Features

- 📄 **OCR Processing** - Extract text from documents and PDFs using EasyOCR
- 🖼️ **Image Detection** - Detect and locate pictures/objects within documents using YOLO
- ✍️ **Signature Detection** - Identify signatures using custom YOLO models
- 🛡️ **PII Detection** - Find and classify personally identifiable information
- 🤖 **AI Validation** - LLM-powered validation using Google Gemini
- 🌍 **Multi-language Support** - OCR in multiple languages
- 🔒 **Privacy-First** - Configurable LLM usage (off by default)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)
- Google Gemini API key (optional, for LLM features)

### Installation

1. **Clone and setup**
   ```bash
   cd backend-app
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

3. **Configure environment**
   ```bash
   cp .env.production .env
   # Edit .env with your settings
   ```

4. **Start server**
   ```bash
   python start_server.py
   ```

### Docker Deployment (Recommended)
```bash
# Build and run
docker-compose up -d

# Check health
curl http://localhost:8000/health
```

## 📖 API Documentation

### Endpoints
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Process Document**: `POST /process_document`

### Process Document Example
```bash
curl -X POST "http://localhost:8000/process_document" \
  -F "file=@document.jpg" \
  -F "use_llm=false"
```

### Response Format
```json
{
  "ocr": {
    "pages": [
      {
        "page_number": 1,
        "blocks": [
          {
            "text": "Sample text",
            "confidence": 0.95,
            "position": {
              "top_left": [100, 150],
              "top_right": [200, 150],
              "bottom_right": [200, 200],
              "bottom_left": [100, 200]
            }
          }
        ]
      }
    ]
  },
  "signatures": [
    {
      "bbox": {"x1": 100, "y1": 150, "x2": 200, "y2": 200},
      "confidence": 0.85
    }
  ],
  "pii_detection": [
    {
      "type": "PERSON",
      "value": "John Doe",
      "confidence": 0.9,
      "bbox": {"x1": 100, "y1": 150, "x2": 200, "y2": 200}
    }
  ],
  "detected_images": [
    {
      "page_number": 1,
      "images": [
        {
          "type": "person",
          "confidence": 0.85,
          "position": {
            "top_left": [100, 150],
            "top_right": [200, 150],
            "bottom_right": [200, 250],
            "bottom_left": [100, 250]
          }
        }
      ]
    }
  ]
}
```

## 🏗️ Architecture

```
backend-app/
├── api/
│   └── main.py              # FastAPI endpoints & routing
├── ocr/
│   ├── processor.py         # OCR + image detection
│   └── processor_stream.py  # Streaming OCR
├── pii_detection/
│   ├── detector.py          # PII entity detection
│   ├── models.py           # Data models
│   ├── bbox_mapper.py      # Coordinate mapping
│   ├── indian_recognizers.py # India-specific PII
│   └── llm_validator.py    # AI validation
├── pipeline/
│   └── orchestrator.py     # Processing coordination
├── config/
│   ├── settings.py         # Configuration
│   └── logging.py          # Logging setup
├── models/                 # ML model storage
├── logs/                   # Application logs
└── tests/                  # Test files
```

## ⚙️ Configuration

### Environment Variables
```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional
OCR_GPU_ENABLED=false
MAX_FILE_SIZE=10485760
DEBUG=false
LOG_LEVEL=INFO
```

### Model Configuration
- **OCR**: EasyOCR with CPU/GPU support
- **Signature Detection**: `detector_yolo_1cls.pt` (custom YOLO model)
- **Image Detection**: YOLOv8n (auto-downloaded)
- **PII Detection**: Presidio + custom recognizers

## 🚢 Deployment Options

### Railway
```bash
# Deploy to Railway
railway login
railway link
railway up
```

### Google Cloud Run
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/pii-backend
gcloud run deploy --image gcr.io/PROJECT_ID/pii-backend --platform managed
```

### Render
```bash
# Deploy using render.yaml configuration
# Push to GitHub and connect to Render
```

### Heroku
```bash
# Deploy to Heroku
heroku create your-app-name
git push heroku main
```

## 🧪 Testing

### Run Tests
```bash
python -m pytest tests/
```

### Test Image Detection
```bash
python test_image_detection.py
```

### Manual Testing
```bash
# Test OCR
curl -X POST "http://localhost:8000/process_document" \
  -F "file=@test_image.jpg"

# Test with LLM validation
curl -X POST "http://localhost:8000/process_document" \
  -F "file=@test_image.jpg" \
  -F "use_llm=true"
```

## 🔒 Security & Privacy

- **LLM Usage**: Disabled by default, requires explicit activation
- **File Validation**: Strict file type and size validation
- **CORS Protection**: Configurable CORS policies
- **Input Sanitization**: Comprehensive input validation
- **Error Handling**: Secure error messages (no sensitive data leakage)

## 📊 Performance

- **Model Caching**: Intelligent caching for YOLO and EasyOCR models
- **Memory Management**: Automatic garbage collection and cleanup
- **Concurrent Processing**: Async FastAPI for high throughput
- **Resource Limits**: Configurable memory and processing limits

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Set Python path
   export PYTHONPATH=.
   python pipeline/orchestrator.py
   ```

2. **GPU Issues**
   ```bash
   # Disable GPU if issues occur
   export OCR_GPU_ENABLED=false
   ```

3. **Memory Issues**
   ```bash
   # Reduce concurrent processing
   export MAX_WORKERS=1
   ```

### Pipeline Usage
```bash
# Method 1: Set PYTHONPATH (Windows PowerShell)
$env:PYTHONPATH = '.'
python pipeline/orchestrator.py <image_path> [llm_api_key]

# Method 2: Use Python -m
python -m pipeline.orchestrator <image_path> [llm_api_key]
```

### Logs
```bash
# Check application logs
tail -f logs/app.log

# Docker logs
docker logs container_name
```
