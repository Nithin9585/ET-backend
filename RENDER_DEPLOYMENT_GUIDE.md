# 🚀 Render.com Deployment Guide - Step by Step

## Step 1: Prepare Your Repository ✅
Your repository is ready! We just pushed the full Dockerfile that includes:
- ✅ EasyOCR for text extraction
- ✅ Presidio for PII detection  
- ✅ spaCy for NLP processing
- ✅ FastAPI web framework
- ✅ All dependencies configured

## Step 2: Sign Up for Render.com

1. **Go to**: https://render.com
2. **Click**: "Get Started for Free"
3. **Sign up with GitHub** (recommended - easier integration)
4. **Authorize Render** to access your GitHub repositories

## Step 3: Create New Web Service

1. **Click**: "New +" button (top right)
2. **Select**: "Web Service"
3. **Connect Repository**:
   - Choose "Build and deploy from a Git repository"
   - Click "Connect" next to your GitHub account
   - Find and select your repository: `ET-backend` or `OCR-MODEL`
   - Click "Connect"

## Step 4: Configure Service Settings

### Basic Settings:
- **Name**: `ocr-pii-api` (or any name you prefer)
- **Region**: `Ohio (US East)` (recommended for speed)
- **Branch**: `main`
- **Root Directory**: Leave empty (uses root)

### Build Settings:
- **Environment**: `Docker`
- **Build Command**: Leave empty (uses Dockerfile)
- **Start Command**: Leave empty (uses Dockerfile CMD)

### Advanced Settings:
- **Plan**: `Free` (select this!)
- **Auto-Deploy**: `Yes` (deploys on new commits)

## Step 5: Environment Variables (Optional)

If you want to add your Gemini API key for LLM validation:
1. **Scroll down** to "Environment Variables"
2. **Add**:
   - Key: `GEMINI_API_KEY`
   - Value: `your-actual-api-key-here`

## Step 6: Deploy!

1. **Click**: "Create Web Service"
2. **Wait**: Render will start building your Docker image
3. **Monitor**: You'll see the build logs in real-time

Expected build time: 5-10 minutes (downloading OCR dependencies)

## Step 7: Get Your Live URL

Once deployed, you'll get a URL like:
`https://ocr-pii-api-xxxx.onrender.com`

## Step 8: Test Your API

### Health Check:
```bash
curl https://your-app-name.onrender.com/health
```

### Upload Test:
```bash
curl -X POST "https://your-app-name.onrender.com/process_document" \
  -F "file=@your-test-image.jpg"
```

### API Documentation:
Visit: `https://your-app-name.onrender.com/docs`

## 🎉 You're Live!

Your full OCR PII Detection API is now running on Render.com for FREE!

## Important Notes:

### ⚠️ Cold Starts:
- Free tier spins down after 15 minutes of inactivity
- First request after spin-down takes ~30-60 seconds
- Subsequent requests are fast

### 💡 Keep Alive Trick:
To minimize cold starts, you can ping your API every 10 minutes:
```bash
# Set up a cron job or use uptimerobot.com (free)
curl https://your-app-name.onrender.com/health
```

### 🔄 Auto-Deployment:
- Every time you push to `main` branch, Render automatically rebuilds and deploys
- No manual deployment needed!

## Next Steps:

1. **Test thoroughly** with different image types
2. **Add monitoring** (uptimerobot.com is free)
3. **Consider upgrading** to paid plan ($7/month) for always-on service
4. **Add custom domain** (available on free tier!)

## Troubleshooting:

If build fails:
1. Check build logs in Render dashboard
2. Ensure your GitHub repository is public or Render has access
3. Verify Dockerfile is in repository root

## 🎯 Your API Endpoints:

- **Health**: `GET /health`
- **Process Document**: `POST /process_document` 
- **API Docs**: `GET /docs`
- **Root**: `GET /`

Congratulations! Your OCR API is now live and accessible worldwide! 🌍
