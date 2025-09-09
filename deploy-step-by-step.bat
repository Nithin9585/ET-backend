@echo off
echo 🚀 Google Cloud Deployment - Step by Step

echo Step 1: Set your project
gcloud config set project pii-frontend

echo Step 2: Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

echo Step 3: Build the Docker image
gcloud builds submit --tag gcr.io/pii-frontend/ocr-pii-api --file Dockerfile.cloudrun .

echo Step 4: Deploy to Cloud Run
gcloud run deploy ocr-pii-api ^
    --image gcr.io/pii-frontend/ocr-pii-api ^
    --platform managed ^
    --region us-central1 ^
    --allow-unauthenticated ^
    --memory 4Gi ^
    --cpu 2 ^
    --timeout 300 ^
    --max-instances 10 ^
    --set-env-vars "ENVIRONMENT=production,DEBUG=false,OCR_GPU_ENABLED=false" ^
    --port 8080

echo ✅ Deployment completed!
echo 📚 Your API will be available at the URL shown above
echo ❤️ Test with: /health endpoint

pause
