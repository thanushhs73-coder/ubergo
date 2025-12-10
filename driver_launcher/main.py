import sys
import os

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database import get_db, init_db
from shared.crud import create_driver, get_driver_by_phone, get_driver_by_id
from shared.schemas import DriverCreate, DriverOut
from shared.process_manager import spawn_driver_instance
import asyncio
import os

app = FastAPI(title="UBERGO Driver Launcher")


@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    await init_db()


@app.get("/", response_class=HTMLResponse)
async def get_launcher_page():
    """Serve the driver launcher page."""
    template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'driver_launcher.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


@app.post("/register", response_model=DriverOut)
async def register_driver(name: str = Form(...), phone: str = Form(...), db: AsyncSession = Depends(get_db)):
    """Register a new driver and spawn their FastAPI instance."""
    # Check if phone already exists
    existing_driver = await get_driver_by_phone(db, phone)
    if existing_driver:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    driver_create = DriverCreate(name=name, phone=phone)
    driver = await create_driver(db, driver_create)
    
    # Spawn the driver instance in background
    try:
        spawn_driver_instance(driver.id, driver.assigned_port)
        # Give it a moment to start
        await asyncio.sleep(1)
    except Exception as e:
        print(f"Error spawning driver instance: {e}")
        # Still return the driver even if spawn fails
    
    return driver


@app.post("/login", response_model=DriverOut)
async def login_driver(phone: str = Form(...), db: AsyncSession = Depends(get_db)):
    """Login driver by phone and return their info."""
    driver = await get_driver_by_phone(db, phone)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found. Please register first.")
    
    # Auto-spawn instance in case it's not running
    try:
        spawn_driver_instance(driver.id, driver.assigned_port)
        await asyncio.sleep(1)
    except Exception as e:
        print(f"Instance may already be running: {e}")
    
    return driver


@app.post("/login_by_id", response_model=DriverOut)
async def login_driver_by_id(driver_id: int = Form(...), db: AsyncSession = Depends(get_db)):
    """Login driver by ID and return their info."""
    driver = await get_driver_by_id(db, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail=f"Driver ID {driver_id} not found.")
    
    # Auto-spawn instance in case it's not running
    try:
        spawn_driver_instance(driver.id, driver.assigned_port)
        await asyncio.sleep(1)
    except Exception as e:
        print(f"Instance may already be running: {e}")
    
    return driver


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8900)
