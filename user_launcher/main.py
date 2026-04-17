import sys
import os

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database import get_db, init_db
from shared.crud import create_user, list_all_users, get_user_by_id
from shared.schemas import UserCreate, UserOut
from shared.process_manager import spawn_user_instance
from typing import List
import asyncio
import os

app = FastAPI(title="UBERGO User Launcher")


@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    await init_db()


@app.get("/", response_class=HTMLResponse)
async def get_launcher_page():
    """Serve the user launcher page."""
    template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'user_launcher.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


@app.post("/create_user", response_model=UserOut)
async def create_new_user(name: str = Form(...), db: AsyncSession = Depends(get_db)):
    """Create a new user and spawn their FastAPI instance."""
    user_create = UserCreate(name=name)
    user = await create_user(db, user_create)
    
    # Spawn the user instance in background (only in development)
    environment = os.getenv("ENVIRONMENT", "development").lower()
    if environment != "production":
        try:
            spawn_user_instance(user.id, user.user_port)
            # Give it a moment to start
            await asyncio.sleep(1)
        except Exception as e:
            print(f"Error spawning user instance: {e}")
        # Still return the user even if spawn fails
    
    return user


@app.post("/login_user", response_model=UserOut)
async def login_user(user_id: int = Form(...), db: AsyncSession = Depends(get_db)):
    """Login as existing user and get portal access."""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User ID {user_id} not found")
    
    # Ensure user instance is running
    try:
        spawn_user_instance(user.id, user.user_port)
        await asyncio.sleep(1)
    except Exception as e:
        print(f"Instance may already be running: {e}")
    
    return user


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
