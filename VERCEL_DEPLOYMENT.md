# UberGo on Vercel - Deployment Guide

## Project Structure

```
ubergo/
├── frontend/              # Next.js React frontend
├── api/                   # Python API routes
├── admin_app/            # FastAPI admin app
├── user_launcher/        # FastAPI user launcher
├── driver_launcher/      # FastAPI driver launcher
├── shared/               # Shared modules
├── vercel.json           # Vercel configuration
└── requirements.txt      # Python dependencies
```

## Deployment Steps

### Step 1: Create PostgreSQL Database

You need a PostgreSQL database (Vercel doesn't include one):

**Option A: Use Railway PostgreSQL**
- Go to https://railway.app
- Create a new PostgreSQL database
- Copy the connection string

**Option B: Use Supabase**
- Go to https://supabase.com
- Create a project and database
- Copy the connection string

**Option C: Use any managed PostgreSQL**
- AWS RDS, Azure Database, etc.

### Step 2: Deploy to Vercel

1. **Push to GitHub**: Ensure your code is on GitHub
   ```bash
   git add .
   git commit -m "Add Vercel monorepo structure"
   git push
   ```

2. **Go to Vercel**: https://vercel.com/dashboard

3. **Import Project**:
   - Click "Add New" → "Project"
   - Select your `ubergo` repository
   - Vercel auto-detects Next.js + Python

4. **Configure Environment Variables**:
   - Click "Environment Variables"
   - Add these variables:
     ```
     DATABASE_URL=postgresql+asyncpg://...
     ENVIRONMENT=production
     NEXT_PUBLIC_API_URL=https://your-deployment.vercel.app/api
     ```

5. **Deploy**:
   - Click "Deploy"
   - Wait 2-3 minutes for deployment

### Step 3: Access Your App

Once deployed:
- **Frontend**: https://your-deployment.vercel.app
- **API Health**: https://your-deployment.vercel.app/api/health
- **Admin**: https://your-deployment.vercel.app/admin

## Troubleshooting

### API 404 Errors
- Ensure `DATABASE_URL` is set correctly
- Verify PostgreSQL is accessible

### Import Errors
- Check that all Python dependencies are in `requirements.txt`
- Vercel runs `pip install -r requirements.txt` during build

### Cold Start Issues
- First request to API may be slow (serverless)
- Subsequent requests will be faster

## Local Development

### Run Everything Locally

```bash
# Terminal 1 - Frontend
cd frontend
npm install
npm run dev    # Runs on http://localhost:3000

# Terminal 2 - Backend API
uvicorn api.index:app --reload --host 0.0.0.0 --port 8000
```

Access:
- Frontend: http://localhost:3000
- API: http://localhost:8000/api/health

## Project URLs

After deployment on Vercel:
- **Main Site**: https://your-deployment.vercel.app
- **GitHub**: https://github.com/thanushhs73-coder/ubergo
- **Vercel Dashboard**: https://vercel.com/dashboard

## Environment Variables Checklist

- [ ] `DATABASE_URL` - PostgreSQL connection string
- [ ] `ENVIRONMENT` - Set to `production`
- [ ] `NEXT_PUBLIC_API_URL` - Your Vercel deployment URL + `/api`

## Next Steps

1. Create PostgreSQL database
2. Get `DATABASE_URL` from your database provider
3. Deploy to Vercel with environment variables
4. Test the API: `/api/health` endpoint
5. Build out the frontend pages as needed
