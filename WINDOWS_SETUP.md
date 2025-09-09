# Windows Setup Guide

## 🔧 Prerequisites for Windows

### 1. Install Poppler for PDF Processing

**Option A: Using Conda (Recommended)**
```powershell
conda install -c conda-forge poppler
```

**Option B: Manual Installation**
1. Download Poppler for Windows: https://github.com/oschwartz10612/poppler-windows/releases/
2. Extract to `C:\poppler` 
3. Add `C:\poppler\Library\bin` to your PATH environment variable

**Option C: Using Chocolatey**
```powershell
choco install poppler
```

### 2. Install Google Cloud SDK
1. Download from: https://cloud.google.com/sdk/docs/install-windows
2. Run the installer
3. Restart PowerShell/Command Prompt
4. Run: `gcloud init`

### 3. Verify Installation
```powershell
# Check Poppler
pdftoppm -h

# Check gcloud
gcloud --version
```

## 🚀 Windows Deployment Commands

### Using PowerShell
```powershell
# Navigate to project
cd C:\Users\Nithi\OneDrive\Desktop\virtual-2\nesscom\backend-app

# Run Windows deployment script
cmd /c "deploy-gcp.bat cloud-run"

# Or run commands manually
gcloud config set project YOUR_PROJECT_ID
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/ocr-pii-api --file Dockerfile.cloudrun .
gcloud run deploy ocr-pii-api --image gcr.io/YOUR_PROJECT_ID/ocr-pii-api --platform managed --region us-central1 --allow-unauthenticated
```

## 🔍 Troubleshooting Windows Issues

### PDF Processing Error
```
{"error":"EasyOCR failed: Unable to get page count. Is poppler installed and in PATH?"}
```
**Solution**: Install Poppler using one of the methods above.

### Deployment Script Not Found
```powershell
# Use cmd to run batch files
cmd /c "deploy-gcp.bat cloud-run"
```

### Permission Issues
```powershell
# Set execution policy if needed
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
