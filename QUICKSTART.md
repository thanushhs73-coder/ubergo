# UBERGO_B2 Quick Start Guide

## Prerequisites
- Python 3.9+
- PostgreSQL installed and running
- pip (Python package manager)

## Step 1: Create PostgreSQL Database

Open PostgreSQL command line or pgAdmin and run:
```sql
CREATE DATABASE ubergo;
```

Default credentials: `postgres` / `#2005REnu`

If you use different credentials, edit `shared/database.py` and update DATABASE_URL.

## Step 2: Install Dependencies

```bash
cd d:\Uber_Go\UBERGO_B2
pip install -r requirements.txt
```

## Step 3: Start the System

### Option A: Using PowerShell Script (Recommended for Windows)
```bash
.\start_all.ps1
```

### Option B: Using Batch Script
```bash
start_all.bat
```

### Option C: Manual - Open 3 Separate Terminal Windows

**Terminal 1 - Admin Dashboard:**
```bash
cd d:\Uber_Go\UBERGO_B2
python -m uvicorn admin_app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 - User Launcher:**
```bash
cd d:\Uber_Go\UBERGO_B2
python -m uvicorn user_launcher.main:app --host 127.0.0.1 --port 8001 --reload
```

**Terminal 3 - Driver Launcher:**
```bash
cd d:\Uber_Go\UBERGO_B2
python -m uvicorn driver_launcher.main:app --host 127.0.0.1 --port 8900 --reload
```

## Step 4: Access the System

Open your web browser and navigate to:

1. **Admin Dashboard**: http://localhost:8000
   - View all rides, users, drivers
   - See live stats and ride status updates

2. **User Launcher**: http://localhost:8001
   - Create new users
   - Each user gets their own portal on a unique port (8002+)

3. **Driver Launcher**: http://localhost:8900
   - Register as driver
   - Login to your driver portal

## Workflow Example

### 1. Create a User
1. Go to http://localhost:8001
2. Enter your name (e.g., "Alice")
3. Click "Create User"
4. You'll see: "User created on port 8005"
5. Click the link to access your user portal

### 2. Book a Ride
1. On your user portal (http://localhost:8005)
2. Enter pickup location: "Library"
3. Enter destination: "Dining Hall"
4. Click "Book Ride"
5. Status will show as "PENDING"

### 3. Register as Driver
1. Go to http://localhost:8900
2. Enter name (e.g., "Bob") and phone (e.g., "555-1234")
3. Click "Register"
4. You'll see: "Driver registered on port 8901"
5. Click the link to access your driver portal

### 4. Accept a Ride
1. On driver portal (http://localhost:8901)
2. In "Pending Ride Requests" table, you'll see the ride from Alice
3. Click "Accept"
4. Ride status changes to "ASSIGNED"

### 5. Complete the Ride
1. In "Current Ride Assignment" section, see Alice's ride
2. Click "Complete Ride"
3. Ride status changes to "COMPLETED"

### 6. Monitor on Admin Dashboard
1. Go to http://localhost:8000
2. View real-time updates every 3 seconds
3. Switch between tabs: All Rides, Pending, Active, Completed
4. See driver and user lists

## Directory Structure

```
UBERGO_B2/
├── admin_app/
│   ├── __init__.py
│   └── main.py                 # Admin dashboard FastAPI app
├── driver_instances/
│   ├── __init__.py
│   └── driver_instance_app.py  # Template for driver portals
├── driver_launcher/
│   ├── __init__.py
│   └── main.py                 # Driver registration app
├── shared/
│   ├── __init__.py
│   ├── crud.py                 # Database operations
│   ├── database.py             # SQLAlchemy setup
│   ├── models.py               # ORM models
│   ├── port_utils.py           # Port management
│   ├── process_manager.py      # Subprocess spawning
│   └── schemas.py              # Pydantic models
├── templates/
│   ├── __init__.py
│   └── admin.html              # Admin dashboard UI
├── user_instances/
│   ├── __init__.py
│   └── user_instance_app.py    # Template for user portals
├── user_launcher/
│   ├── __init__.py
│   └── main.py                 # User registration app
├── README.md                   # Full documentation
├── requirements.txt            # Python dependencies
├── start_all.bat               # Batch startup script
└── start_all.ps1               # PowerShell startup script
```

## Ports Used

| Service | Port | Range |
|---------|------|-------|
| Admin Dashboard | 8000 | — |
| User Launcher | 8001 | — |
| User Instances | — | 8002–8899 |
| Driver Launcher | 8900 | — |
| Driver Instances | — | 8901–8999 |

## Key Features

✅ **Dynamic Port Allocation**
- Each user/driver gets unique port automatically
- No pre-spawning, only created instances run

✅ **Atomic Ride Assignment**
- Prevents multiple drivers from accepting same ride
- Uses SQL transactions

✅ **Live Updates**
- Polling every 3 seconds
- No WebSockets (kept simple)

✅ **Multi-Instance Architecture**
- Every user has isolated FastAPI server
- Every driver has isolated FastAPI server
- Shared PostgreSQL database

✅ **Admin Monitoring**
- Real-time dashboard
- View all rides, users, drivers
- Filter by status

## Troubleshooting

### Issue: "Address already in use"
**Solution:** The port is already running. Either:
- Kill the existing process
- Wait a few seconds and restart
- Check if another app is using the port

### Issue: "could not connect to server: Connection refused"
**Solution:** PostgreSQL is not running. Start PostgreSQL:
- On Windows: Open Services and start "PostgreSQL"
- On Mac: `brew services start postgresql`
- On Linux: `sudo service postgresql start`

### Issue: "No module named 'shared'"
**Solution:** Make sure you're running from the UBERGO_B2 directory

### Issue: Instance app not starting
**Solution:** Check:
1. Uvicorn is installed: `pip install uvicorn`
2. No port conflict: `netstat -ano | findstr :PORT`
3. Check error logs in terminal window

## Next Steps

1. Test the workflow above
2. Create multiple users and drivers
3. Try accepting rides from different drivers
4. Monitor on admin dashboard
5. Check database with: `SELECT * FROM ride_requests;`

## Support

For issues or questions, check:
- README.md - Full documentation
- Individual app docstrings
- Console output for error messages

Enjoy UBERGO_B2! 🚗
