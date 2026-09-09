# 🚀 Render Deployment Guide (Optimized for 512MB Free Tier)

This guide walks you through deploying the **Devil's Advocate Panel** (FastAPI Backend + Next.js Frontend) to [Render.com](https://render.com) while staying well within the **512 MB RAM / free tier resource limits**.

---

## ⚡ Key Optimizations Implemented for < 512MB

1. **Standalone Next.js Bundle (`output: 'standalone'`)**:
   - Reduces Next.js production runtime size from **350MB+ down to ~35MB**.
2. **Lean Production Requirements**:
   - Production `requirements.txt` excludes test runners and heavy local embedding models, leveraging cloud Gemini/Groq APIs directly.
   - Uvicorn runs single worker (`--workers 1 --timeout-keep-alive 30`) with minimal memory footprint (~45-65MB RAM).
3. **Optimized Build Context (`.dockerignore`)**:
   - Prevents local `node_modules` and `venv` from bloating the build context.

---

## 🛠️ Step-by-Step Deployment Options on Render

### Option A: Using Render Blueprints (Recommended - 1 Click)

1. Push this repository to GitHub.
2. Go to [Render Dashboard](https://dashboard.render.com) -> Click **"New"** -> Select **"Blueprint"**.
3. Select your `devil-s_advocate_panel` repository.
4. Render will automatically detect [render.yaml](file:///d:/projects/devil's_advocate_panel/render.yaml) and configure both services:
   - **`devils-advocate-backend`** (FastAPI)
   - **`devils-advocate-frontend`** (Next.js)
5. Fill in the Secret Environment Variables in the Render UI:
   - `GEMINI_API_KEY` (Your Google Gemini API Key)
   - `MONGO_DB_URL` (Your MongoDB Atlas connection string)
   - `CLERK_SECRET_KEY` (Your Clerk Secret Key)
   - `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` (Your Clerk Publishable Key)
6. Click **"Apply"**.

---

### Option B: Manual Web Service Setup

#### 1. Backend Web Service
- **Name**: `devils-advocate-backend`
- **Root Directory**: `backend`
- **Environment**: `Python 3`
- **Build Command**: `pip install --no-cache-dir -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1`
- **Health Check Path**: `/health`
- **Environment Variables**:
  ```env
  PORT=8999
  ENVIRONMENT=production
  DEFAULT_LLM_PROVIDER=gemini
  GEMINI_MODEL=gemini-2.5-flash
  GEMINI_API_KEY=your_gemini_api_key
  MONGO_DB_URL=your_mongodb_atlas_url
  MONGODB_DB_NAME=devils_advocate
  CLERK_SECRET_KEY=your_clerk_secret_key
  CORS_ORIGINS=*
  ```

#### 2. Frontend Web Service
- **Name**: `devils-advocate-frontend`
- **Root Directory**: `frontend`
- **Environment**: `Node`
- **Build Command**: `npm ci && npm run build`
- **Start Command**: `npm run start -- -p $PORT`
- **Environment Variables**:
  ```env
  NEXT_PUBLIC_API_URL=https://devils-advocate-backend.onrender.com
  NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
  CLERK_SECRET_KEY=sk_test_...
  ```
