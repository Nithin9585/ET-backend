# Google Cloud Platform Deployment Guide

## 🚀 Quick Setup

### Prerequisites
1. **Google Cloud Account**: Create at [cloud.google.com](https://cloud.google.com)
2. **Google Cloud SDK**: Download from [cloud.google.com/sdk](https://cloud.google.com/sdk/docs/install)
3. **Project Setup**: Create a new GCP project

### Initial Setup
```bash
# Install Google Cloud SDK
# Follow installation guide for your OS

# Login to Google Cloud
gcloud auth login

# Set your project ID
gcloud config set project YOUR_PROJECT_ID

# Enable billing (required for deployment)
# Go to: https://console.cloud.google.com/billing
```

## 🏗️ Deployment Options

### Option 1: Cloud Run (Recommended)
**Best for**: Scalable, containerized applications with automatic scaling

```bash
# Deploy using the script (Linux/Mac)
chmod +x deploy-gcp.sh
./deploy-gcp.sh cloud-run

# Deploy using Windows script (PowerShell)
cmd /c "deploy-gcp.bat cloud-run"

# Or deploy manually
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/ocr-pii-api --file Dockerfile.cloudrun .
gcloud run deploy ocr-pii-api --image gcr.io/YOUR_PROJECT_ID/ocr-pii-api --platform managed --region us-central1 --allow-unauthenticated
```

**Features:**
- ✅ Automatic scaling (0 to N instances)
- ✅ Pay-per-request pricing
- ✅ Full Docker support
- ✅ Custom domains
- ✅ HTTPS by default

### Option 2: App Engine
**Best for**: Simpler deployment with managed infrastructure

```bash
# Deploy using the script
./deploy-gcp.sh app-engine

# Or deploy manually
gcloud app deploy app.yaml
```

**Features:**
- ✅ Fully managed platform
- ✅ Built-in monitoring
- ✅ Easy configuration
- ✅ Version management

## 🔐 Environment Variables & Secrets

### Using Secret Manager (Recommended)
```bash
# Create secrets
gcloud secrets create gemini-api-key --data-file=-
# Enter your API key when prompted

# Grant access to your service
gcloud secrets add-iam-policy-binding gemini-api-key \
    --member="serviceAccount:YOUR_SERVICE_ACCOUNT@YOUR_PROJECT.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### Update Configuration
```bash
# For Cloud Run - set environment variables
gcloud run services update ocr-pii-api \
    --set-env-vars "GEMINI_API_KEY=your-api-key-here" \
    --region us-central1
```

## 📊 Monitoring & Logging

### Cloud Monitoring
- **Metrics**: Automatic collection of CPU, memory, requests
- **Alerts**: Set up alerts for errors or high latency
- **Dashboards**: Create custom dashboards

### Cloud Logging
- **Structured Logs**: Your app logs are automatically collected
- **Log Explorer**: Search and filter logs
- **Log-based Metrics**: Create metrics from log data

### Access Logs
```bash
# View logs
gcloud logs read "resource.type=cloud_run_revision" --limit 50

# Stream logs in real-time
gcloud logs tail "resource.type=cloud_run_revision"
```

## 🔧 Configuration Examples

### app.yaml (App Engine)
```yaml
runtime: python312
env_variables:
  GEMINI_API_KEY: "your-api-key"
  OCR_GPU_ENABLED: "false"
automatic_scaling:
  min_instances: 1
  max_instances: 10
```

### Cloud Run Environment Variables
```bash
gcloud run services update ocr-pii-api \
    --set-env-vars "ENVIRONMENT=production,DEBUG=false,GEMINI_API_KEY=your-key" \
    --region us-central1
```

## 💰 Cost Optimization

### Cloud Run Pricing
- **CPU**: $0.000024 per vCPU-second
- **Memory**: $0.0000025 per GiB-second
- **Requests**: $0.40 per million requests
- **Free Tier**: 2 million requests/month

### App Engine Pricing
- **Standard Environment**: $0.05-$0.10 per hour
- **Free Tier**: 28 hours/day

### Cost-Saving Tips
1. **Set appropriate memory/CPU limits**
2. **Use minimum instances = 0 for Cloud Run**
3. **Implement request caching**
4. **Monitor usage with Cloud Billing**

## 🚀 Custom Domain

### Set up Custom Domain
```bash
# Map custom domain
gcloud run domain-mappings create --service ocr-pii-api --domain api.yourdomain.com --region us-central1

# Add DNS records as instructed by Google Cloud
```

## 🧪 Testing Production Deployment

### Health Check
```bash
curl https://your-service-url/health
```

### API Test
```bash
curl -X POST "https://your-service-url/process_document" \
  -H "accept: application/json" \
  -F "file=@test-image.jpg"
```

### Load Testing
```bash
# Install Apache Bench
apt-get install apache2-utils

# Run load test
ab -n 1000 -c 10 https://your-service-url/health
```

## 🔍 Troubleshooting

### Common Issues
1. **Build Failures**: Check `requirements.txt` and Dockerfile
2. **Memory Issues**: Increase memory allocation
3. **Timeout Issues**: Increase timeout settings
4. **API Key Issues**: Verify Secret Manager setup

### Debug Commands
```bash
# Check service status
gcloud run services describe ocr-pii-api --region us-central1

# View recent logs
gcloud logs read "resource.type=cloud_run_revision" --limit 10

# Check build logs
gcloud builds list --limit 5
```

## 📋 Deployment Checklist

- [ ] GCP project created and billing enabled
- [ ] Google Cloud SDK installed and authenticated
- [ ] Project ID updated in deployment scripts
- [ ] API keys stored in Secret Manager
- [ ] Service deployed successfully
- [ ] Health check endpoint responding
- [ ] API documentation accessible
- [ ] Custom domain configured (optional)
- [ ] Monitoring and alerts set up
- [ ] Cost limits configured

## 🎯 Next Steps

1. **Set up CI/CD** with Cloud Build triggers
2. **Configure monitoring** and alerting
3. **Implement caching** for better performance
4. **Set up staging environment**
5. **Configure backup strategies**
