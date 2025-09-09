@echo off
REM Google Cloud Deployment Script for Windows
REM Usage: deploy-gcp.bat [app-engine|cloud-run]

setlocal EnableDelayedExpansion

REM Configuration
set PROJECT_ID=pii-frontend
set REGION=us-central1
set SERVICE_NAME=ocr-pii-api
set IMAGE_NAME=gcr.io/%PROJECT_ID%/%SERVICE_NAME%

echo 🚀 Starting Google Cloud Deployment

REM Check if gcloud is installed
gcloud --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Google Cloud SDK not found. Please install it first.
    echo Visit: https://cloud.google.com/sdk/docs/install
    exit /b 1
)

REM Check deployment type
set DEPLOYMENT_TYPE=%1
if "%DEPLOYMENT_TYPE%"=="" set DEPLOYMENT_TYPE=cloud-run

if "%DEPLOYMENT_TYPE%"=="app-engine" (
    echo 📦 Deploying to App Engine...
    
    REM Set project
    gcloud config set project %PROJECT_ID%
    
    REM Deploy to App Engine
    gcloud app deploy app.yaml --quiet
    
    echo ✅ Deployed to App Engine successfully!
    
) else if "%DEPLOYMENT_TYPE%"=="cloud-run" (
    echo 🏗️ Deploying to Cloud Run...
    
    REM Set project
    gcloud config set project %PROJECT_ID%
    
    REM Enable required APIs
    echo 🔧 Enabling required APIs...
    gcloud services enable cloudbuild.googleapis.com
    gcloud services enable run.googleapis.com
    gcloud services enable containerregistry.googleapis.com
    
    REM Build the image
    echo 🔨 Building Docker image...
    gcloud builds submit --tag %IMAGE_NAME% --file Dockerfile.cloudrun .
    
    REM Deploy to Cloud Run
    echo 🚀 Deploying to Cloud Run...
    gcloud run deploy %SERVICE_NAME% ^
        --image %IMAGE_NAME% ^
        --platform managed ^
        --region %REGION% ^
        --allow-unauthenticated ^
        --memory 4Gi ^
        --cpu 2 ^
        --timeout 300 ^
        --max-instances 10 ^
        --set-env-vars "ENVIRONMENT=production,DEBUG=false,OCR_GPU_ENABLED=false" ^
        --port 8080
    
    echo ✅ Deployed to Cloud Run successfully!
    
) else (
    echo ❌ Invalid deployment type. Use 'app-engine' or 'cloud-run'
    exit /b 1
)

echo 🎉 Deployment completed successfully!
echo 📚 Check your Google Cloud Console for the service URL
echo ❤️ Health check endpoint: /health

pause
