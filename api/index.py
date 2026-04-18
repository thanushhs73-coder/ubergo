import sys
import os
from pathlib import Path

# Add parent directory to path
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import your FastAPI app
from admin_app.main import app as admin_app

# Create a wrapper app for Vercel
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the admin app
app.mount("/api", admin_app)

# Health check endpoint
@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "ubergo-api"}

# Root endpoint
@app.get("/")
async def root():
    return {"message": "UberGo API on Vercel", "version": "1.0"}
