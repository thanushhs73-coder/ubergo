import sys
import os

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database import get_db, init_db, async_session
from shared.crud import list_all_rides, list_all_drivers, list_all_users
from shared.schemas import RideOut, DriverOut, UserOut
from instance_recovery import spawn_all_user_instances, spawn_all_driver_instances
import asyncio
from typing import List

app = FastAPI(title="UBERGO Admin Dashboard")


@app.on_event("startup")
async def startup():
    """Initialize database and recover instances on startup."""
    await init_db()
    
    # Only spawn instances in development/local mode
    # Skip in production (Railway/Vercel) as they only support single process
    environment = os.getenv("ENVIRONMENT", "development").lower()
    if environment != "production":
        async with async_session() as db:
            await spawn_all_user_instances(db)
            await spawn_all_driver_instances(db)


@app.get("/", response_class=HTMLResponse)
async def get_admin_page():
    """Serve the admin dashboard."""
    admin_template_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "templates",
        "admin.html"
    )
    with open(admin_template_path, "r", encoding='utf-8') as f:
        return f.read()


@app.get("/api/rides", response_model=List[RideOut])
async def get_rides(db: AsyncSession = Depends(get_db)):
    """Get all rides with their current status."""
    rides = await list_all_rides(db)
    return rides


@app.get("/api/drivers", response_model=List[DriverOut])
async def get_drivers(db: AsyncSession = Depends(get_db)):
    """Get all drivers."""
    drivers = await list_all_drivers(db)
    return drivers


@app.get("/api/users", response_model=List[UserOut])
async def get_users(db: AsyncSession = Depends(get_db)):
    """Get all users."""
    users = await list_all_users(db)
    return users


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
