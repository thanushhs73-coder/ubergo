# UberGo Deployment Guide: Railway + Vercel

## Part 1: Deploy Backend to Railway

### Step 1: Prepare for Railway Deployment

#### 1.1 Create a `Procfile` (required for Railway)
```
web: uvicorn admin_app.main:app --host 0.0.0.0 --port $PORT
```

#### 1.2 Update `shared/database.py` for environment variables
Railway will provide DATABASE_URL automatically. Ensure your database.py uses:
```python
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:%232005REnu@localhost:5432/ubergo")
```

#### 1.3 Create `.env.example` (for reference - never commit .env)
```
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/ubergo
ENVIRONMENT=production
```

### Step 2: Deploy to Railway.app

1. **Sign Up**: Go to https://railway.app and sign up with GitHub
2. **Create Project**: Click "New Project"
3. **Add Modules**:
   - Click "Add Service" → Select "GitHub Repo"
   - Select your `thanushhs73-coder/ubergo` repository
   - Railway auto-detects Python project

4. **Configure Variables**:
   - Go to "Variables" tab
   - Add `DATABASE_URL` (Railway provides PostgreSQL)
   - Add `PORT=8000`

5. **Add PostgreSQL Database**:
   - Click "Add Database" → "PostgreSQL"
   - Railway creates a PostgreSQL instance automatically
   - DATABASE_URL is auto-populated

6. **Deploy**:
   - Railway auto-deploys on git push
   - Go to "Deployments" tab to watch progress

7. **Get Your Backend URL**:
   - Copy the public URL (e.g., `https://ubergo-backend.railway.app`)
   - This is your **BACKEND_URL** for frontend

---

## Part 2: Deploy Frontend to Vercel

### NOTE: You Need a Frontend First

Your current project only has **FastAPI backend**. You need a **React/Next.js frontend**.

### Option A: Use Next.js (Recommended for Vercel)

#### Step 1: Create a Next.js Frontend Project

```bash
# In your workspace directory
npx create-next-app@latest ubergo-frontend --typescript

# Navigate to frontend
cd ubergo-frontend
```

#### Step 2: Create Frontend API Calls

Create `lib/api.ts`:
```typescript
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export async function createUser(name: string) {
  const response = await fetch(`${BACKEND_URL}/users`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name })
  });
  return response.json();
}

export async function bookRide(userId: number, pickup: string, destination: string) {
  const response = await fetch(`${BACKEND_URL}/rides`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, pickup_location: pickup, destination_location: destination })
  });
  return response.json();
}
```

#### Step 3: Create `.env.local` (for local development)
```
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

#### Step 4: Create Pages

Create `pages/dashboard.tsx` or similar to consume API calls.

#### Step 5: Push Frontend to GitHub

```bash
cd ubergo-frontend
git init
git add .
git commit -m "Initial Next.js frontend for UberGo"
git remote add origin https://github.com/thanushhs73-coder/ubergo-frontend.git
git push -u origin main
```

---

### Option B: Simple React App

```bash
npx create-react-app ubergo-frontend
cd ubergo-frontend
```

Then create a `.env` file:
```
REACT_APP_BACKEND_URL=http://localhost:8000
```

---

### Step 6: Deploy Frontend to Vercel

1. **Sign Up**: Go to https://vercel.com and sign up with GitHub
2. **Import Project**: Click "New Project" → "Import Git Repository"
3. **Select Repository**: Choose your frontend repository
   - If Next.js: Vercel auto-detects settings
   - If React: Ensure build command is `npm run build`

4. **Add Environment Variable**:
   - **Key**: `NEXT_PUBLIC_BACKEND_URL` (for Next.js) or `REACT_APP_BACKEND_URL` (for React)
   - **Value**: Your Railway backend URL (e.g., `https://ubergo-backend.railway.app`)

5. **Deploy**: Click "Deploy"
6. **Get Frontend URL**: Vercel provides a URL like `https://ubergo-frontend.vercel.app`

---

## Part 3: Connect Frontend & Backend

After both are deployed:

1. **Update Backend CORS** in `admin_app/main.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ubergo-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

2. **Update Vercel Environment**: 
   - Go to Vercel Project Settings → Environment
   - Update backend URL to Railway production URL

3. **Test**: Visit your Vercel frontend → should connect to Railway backend

---

## Part 4: Database Migration on Railway

1. **Connect to Railway PostgreSQL**:
```bash
psql postgresql://user:password@host:port/database
```

2. **Run migrations** (if using Alembic):
```bash
alembic upgrade head
```

3. **Or manually run `setup_database.sql`**:
```bash
psql -f setup_database.sql
```

---

## Deployment Checklist

- [ ] Backend deployed to Railway
- [ ] PostgreSQL database created on Railway
- [ ] Frontend created (Next.js recommended)
- [ ] Frontend deployed to Vercel
- [ ] CORS enabled on backend for Vercel domain
- [ ] Environment variables configured on both platforms
- [ ] Backend URL added to Vercel

---

## Useful Links

- **Railway**: https://railway.app/dashboard
- **Vercel**: https://vercel.com/dashboard
- **GitHub**: https://github.com/thanushhs73-coder
- **Backend Logs**: Railway Dashboard → Logs
- **Frontend Logs**: Vercel Dashboard → Deployments → Logs

---

## Troubleshooting

### Backend won't start on Railway
- Check logs in Railway Dashboard
- Verify DATABASE_URL environment variable is set
- Ensure `Procfile` exists

### Frontend can't connect to backend
- Check browser console for CORS errors
- Verify `NEXT_PUBLIC_BACKEND_URL` is set correctly
- Ensure backend CORS allows frontend domain

### Database connection fails
- Check PostgreSQL credentials on Railway
- Verify DATABASE_URL format
- Test connection locally first
