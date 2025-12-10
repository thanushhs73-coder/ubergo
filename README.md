# UBERGO_B2: Multi-Host Ride-Booking System

A distributed ride-booking system where every user and driver gets their own dedicated FastAPI instance on a unique port. Built for local college demo using PostgreSQL, FastAPI, Jinja2, and dynamic subprocess spawning.

## Architecture Overview

```
UBERGO_B2/
├── admin_app/              # Admin dashboard (Port 8000)
├── user_launcher/          # User registration app (Port 8001)
├── driver_launcher/        # Driver registration app (Port 8900)
├── user_instances/         # Individual user portals (Ports 8002-8899)
├── driver_instances/       # Individual driver portals (Ports 8901-8999)
├── shared/                 # Shared modules (database, models, CRUD, etc.)
├── templates/              # HTML templates
└── requirements.txt        # Dependencies
```

## Port Allocation

- **Admin Dashboard**: 8000
- **User Launcher**: 8001
- **User Instances**: 8002-8899 (one per user)
- **Driver Launcher**: 8900
- **Driver Instances**: 8901-8999 (one per driver)

## Prerequisites

- Python 3.9+
- PostgreSQL running locally
- pip

## Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Database

Create a PostgreSQL database named `ubergo`:

```sql
CREATE DATABASE ubergo;
```

The connection string in the shared modules is:
```
postgresql+asyncpg://postgres:%232005REnu@localhost:5432/ubergo
```

If you need to change credentials, update this in `shared/database.py`:
```python
DATABASE_URL = "postgresql+asyncpg://postgres:PASSWORD@localhost:5432/ubergo"
```

### 3. Create .env file (optional, for environment overrides)

```
DATABASE_URL=postgresql+asyncpg://postgres:%232005REnu@localhost:5432/ubergo
```

## Running the System

You'll need to start apps in separate terminal windows:

### Terminal 1: Admin Dashboard
```bash
cd d:\Uber_Go\UBERGO_B2
python -m uvicorn admin_app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Terminal 2: User Launcher
```bash
cd d:\Uber_Go\UBERGO_B2
python -m uvicorn user_launcher.main:app --host 127.0.0.1 --port 8001 --reload
```

### Terminal 3: Driver Launcher
```bash
cd d:\Uber_Go\UBERGO_B2
python -m uvicorn driver_launcher.main:app --host 127.0.0.1 --port 8900 --reload
```

## Usage

### Admin Dashboard
Navigate to: **http://localhost:8000**

View:
- All rides with status (PENDING, ASSIGNED, ACCEPTED, COMPLETED)
- All registered users
- All registered drivers
- Live stats: total rides, pending rides, active drivers, total users

The dashboard auto-refreshes every 3 seconds.

### Create Users
Navigate to: **http://localhost:8001**

1. Enter a user name
2. Click "Create User"
3. A FastAPI instance is spawned on an available port (8002+)
4. Click the link to access your user portal

### User Portal
User portals are launched dynamically at ports 8002-8899. On your user portal:

1. Enter source and destination
2. Click "Book Ride"
3. View ride status updates (polls every 3 seconds)
4. See pending, assigned, and completed rides

### Register/Login Drivers
Navigate to: **http://localhost:8900**

**Register:**
1. Enter name and phone number
2. Click "Register"
3. A FastAPI instance is spawned on an available port (8901+)
4. Click the link to access your driver portal

**Login:**
1. Enter your phone number
2. Click "Login" to return to your driver portal

### Driver Portal
Driver portals are launched dynamically at ports 8901-8999. On your driver portal:

1. View pending ride requests in a table
2. Click "Accept" to accept a pending ride
3. Your current ride is displayed with "Complete Ride" button
4. Ride status updates poll every 3 seconds

## How It Works

### Database Schema

**users table**
- `id`: User ID (PK)
- `name`: User name
- `user_port`: Assigned port (8002-8899)
- `created_at`: Registration timestamp

**drivers table**
- `id`: Driver ID (PK)
- `name`: Driver name
- `phone`: Phone number (unique)
- `assigned_port`: Assigned port (8901-8999)
- `created_at`: Registration timestamp

**ride_requests table**
- `id`: Ride ID (PK)
- `user_id`: FK to users
- `user_port`: User's port for reference
- `source`: Pickup location
- `destination`: Destination
- `status`: PENDING → ASSIGNED → ACCEPTED → COMPLETED
- `assigned_driver_id`: FK to drivers (nullable)
- `assigned_driver_port`: Driver's port (nullable)
- `created_at`, `updated_at`, `completed_at`: Timestamps

### Key Features

**Per-User/Driver Instances**
- Each user and driver gets their own FastAPI instance
- Isolated HTTP server on unique port
- Reduces system load and provides independence

**Atomic Ride Assignment**
- When a driver accepts a ride, a single SQL UPDATE statement ensures only one driver can accept
- Uses WHERE clause to check current status is PENDING
- Prevents race conditions with multiple drivers

**Polling-Based Updates**
- No WebSockets (kept simple for college demo)
- Frontend polls endpoints every 3 seconds
- All state stored in central PostgreSQL

**Dynamic Port Allocation**
- Ports assigned sequentially as users/drivers register
- Port lookup via database before assignment
- Only created instances run (no pre-spawning)

**Process Management**
- Uses Python `subprocess.Popen()` to spawn new Uvicorn processes
- Each instance runs with its own `USER_ID`, `DRIVER_ID`, and `PORT` env vars
- Processes remain running until manually killed

## API Endpoints

### Admin App (Port 8000)
- `GET /` - Admin dashboard HTML
- `GET /api/rides` - List all rides (JSON)
- `GET /api/drivers` - List all drivers (JSON)
- `GET /api/users` - List all users (JSON)

### User Launcher (Port 8001)
- `GET /` - User registration page HTML
- `POST /create_user` - Create user and spawn instance

### Driver Launcher (Port 8900)
- `GET /` - Driver registration/login page HTML
- `POST /register` - Register driver and spawn instance
- `POST /login` - Lookup driver by phone

### User Instance (Ports 8002-8899)
- `GET /` - User portal HTML
- `POST /book_ride` - Create a new ride request
- `GET /ride_status` - Get all rides for this user

### Driver Instance (Ports 8901-8999)
- `GET /` - Driver portal HTML
- `GET /pending_rides` - List all PENDING rides
- `GET /current_ride` - Get driver's current assigned ride
- `POST /accept_ride/{ride_id}` - Accept a PENDING ride
- `POST /complete_ride/{ride_id}` - Mark ride as COMPLETED

## Shared Modules

**database.py**
- AsyncEngine setup with asyncpg
- AsyncSession factory
- get_db() dependency
- init_db() to create tables

**models.py**
- SQLAlchemy ORM models: User, Driver, RideRequest
- RideStatus enum

**schemas.py**
- Pydantic models for API validation

**crud.py**
- Async CRUD functions
- create_user(), create_driver()
- list_all_users(), list_all_drivers()
- create_ride(), list_pending_rides(), list_all_rides()
- atomic_assign_ride() - Atomic ride assignment
- complete_ride()
- get_driver_current_ride()

**port_utils.py**
- get_free_user_port() - Find next free port 8002-8899
- get_free_driver_port() - Find next free port 8901-8999
- is_port_free() - Check OS-level port availability

**process_manager.py**
- spawn_user_instance(user_id, port) - Launch user Uvicorn process
- spawn_driver_instance(driver_id, port) - Launch driver Uvicorn process

## Troubleshooting

### Port Already in Use
If a port is already in use, try:
- Kill the process on that port
- Restart the app
- Or modify the hardcoded port in the main.py files

### Database Connection Error
- Ensure PostgreSQL is running
- Verify DATABASE_URL in shared/database.py
- Check credentials (default: postgres / #2005REnu)

### Import Errors
- Ensure you're running from the UBERGO_B2 directory
- Check PYTHONPATH includes the project root
- Verify all files are created

### Subprocess Issues (Instance Not Spawning)
- Check that shared/process_manager.py paths are correct
- Ensure Uvicorn is installed (`pip install uvicorn`)
- Check console output for error messages

## Future Enhancements

- WebSocket support for real-time updates
- Authentication/authorization
- Rating system
- Payment integration
- Geolocation and map integration
- SMS notifications
- Mobile app
- Scaling with load balancer
- Persistent process management (supervisor, systemd)

## License

Demo project for educational purposes.
