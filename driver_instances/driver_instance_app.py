import sys
import os

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database import get_db, init_db
from shared.crud import (
    list_pending_rides,
    atomic_assign_ride,
    complete_ride,
    get_driver_current_ride,
    get_driver_all_active_rides,
    get_driver_by_id,
    get_ride_by_id,
    accept_ride,
    start_ride,
    arrive_at_destination,
    start_return_trip,
    complete_wait_return_ride
)
from shared.schemas import RideOut
from typing import List, Optional

# Get driver_id from environment variable or default
DRIVER_ID = int(os.getenv("DRIVER_ID", "1"))
PORT = int(os.getenv("PORT", "8901"))

app = FastAPI(title=f"UBERGO Driver Portal")


@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    await init_db()


@app.get("/", response_class=HTMLResponse)
async def get_driver_page(db: AsyncSession = Depends(get_db)):
    """Serve the driver portal page with Wait & Return support."""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>UBERGO Driver - Portal</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            :root {{
                --primary: #10b981;
                --primary-dark: #059669;
                --secondary: #6366f1;
                --warning: #f59e0b;
                --danger: #ef4444;
                --waiting: #f97316;
                --returning: #06b6d4;
                --bg-dark: #0f172a;
                --bg-card: #1e293b;
                --bg-input: #334155;
                --text-primary: #f1f5f9;
                --text-secondary: #94a3b8;
                --border: #475569;
                --gradient-driver: linear-gradient(135deg, #10b981 0%, #059669 100%);
                --gradient-wait: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
                --gradient-return: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
            }}
            
            body {{
                font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
                background: var(--bg-dark);
                color: var(--text-primary);
                min-height: 100vh;
            }}
            
            .app-container {{
                max-width: 520px;
                margin: 0 auto;
                padding: 20px;
                min-height: 100vh;
            }}
            
            /* Header */
            .header {{
                text-align: center;
                padding: 24px 0;
                border-bottom: 1px solid var(--border);
                margin-bottom: 24px;
            }}
            
            .logo {{
                font-size: 2rem;
                font-weight: 800;
                background: var(--gradient-driver);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            
            .driver-badge {{
                display: inline-flex;
                align-items: center;
                gap: 10px;
                background: var(--bg-card);
                padding: 10px 20px;
                border-radius: 25px;
                margin-top: 12px;
                border: 2px solid var(--primary);
            }}
            
            .driver-badge .icon {{
                width: 32px;
                height: 32px;
                background: var(--gradient-driver);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
            }}
            
            .online-dot {{
                width: 10px;
                height: 10px;
                background: var(--primary);
                border-radius: 50%;
                animation: pulse 2s infinite;
            }}
            
            @keyframes pulse {{
                0%, 100% {{ opacity: 1; transform: scale(1); }}
                50% {{ opacity: 0.5; transform: scale(1.2); }}
            }}
            
            /* Section Cards */
            .section-card {{
                background: var(--bg-card);
                border-radius: 20px;
                padding: 20px;
                margin-bottom: 20px;
                border: 1px solid var(--border);
            }}
            
            .section-title {{
                font-size: 1.1rem;
                font-weight: 600;
                margin-bottom: 16px;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .section-title .icon {{
                font-size: 1.3rem;
            }}
            
            .section-title .count {{
                background: var(--primary);
                color: white;
                font-size: 12px;
                padding: 2px 8px;
                border-radius: 10px;
                margin-left: auto;
            }}
            
            /* Active Ride Card */
            .active-ride {{
                background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%);
                border: 2px solid var(--primary);
                border-radius: 16px;
                padding: 20px;
                position: relative;
                overflow: hidden;
            }}
            
            .active-ride.waiting {{
                background: linear-gradient(135deg, rgba(249, 115, 22, 0.15) 0%, rgba(234, 88, 12, 0.15) 100%);
                border-color: var(--waiting);
            }}
            
            .active-ride.returning {{
                background: linear-gradient(135deg, rgba(6, 182, 212, 0.15) 0%, rgba(8, 145, 178, 0.15) 100%);
                border-color: var(--returning);
            }}
            
            .ride-type-badge {{
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 6px 12px;
                border-radius: 8px;
                font-size: 12px;
                font-weight: 600;
                margin-bottom: 12px;
            }}
            
            .badge-standard {{
                background: rgba(99, 102, 241, 0.2);
                color: #818cf8;
            }}
            
            .badge-wait-return {{
                background: var(--gradient-wait);
                color: white;
            }}
            
            .ride-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 16px;
            }}
            
            .ride-id {{
                font-size: 14px;
                color: var(--text-secondary);
            }}
            
            .ride-status {{
                padding: 6px 14px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
            }}
            
            .status-assigned {{ background: rgba(59, 130, 246, 0.2); color: #60a5fa; }}
            .status-accepted {{ background: rgba(16, 185, 129, 0.2); color: #34d399; }}
            .status-in_progress {{ background: rgba(139, 92, 246, 0.2); color: #a78bfa; }}
            .status-waiting {{ background: rgba(249, 115, 22, 0.3); color: #fb923c; animation: blink 1s infinite; }}
            .status-returning {{ background: rgba(6, 182, 212, 0.3); color: #22d3ee; }}
            
            @keyframes blink {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.6; }}
            }}
            
            /* Route Display */
            .route-display {{
                display: flex;
                gap: 12px;
                margin: 16px 0;
            }}
            
            .route-line {{
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 4px;
            }}
            
            .route-dot {{
                width: 14px;
                height: 14px;
                border-radius: 50%;
            }}
            
            .route-dot.pickup {{ background: #10b981; }}
            .route-dot.dest {{ background: #ef4444; }}
            
            .route-connector {{
                width: 2px;
                flex: 1;
                background: linear-gradient(180deg, #10b981 0%, #ef4444 100%);
                min-height: 35px;
            }}
            
            .route-details {{
                flex: 1;
            }}
            
            .route-point {{
                margin-bottom: 14px;
            }}
            
            .route-label {{
                font-size: 11px;
                color: var(--text-secondary);
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .route-address {{
                font-size: 16px;
                font-weight: 500;
                margin-top: 4px;
            }}
            
            /* User Info */
            .user-info {{
                display: flex;
                align-items: center;
                gap: 12px;
                background: rgba(99, 102, 241, 0.1);
                padding: 12px;
                border-radius: 12px;
                margin: 12px 0;
            }}
            
            .user-avatar {{
                width: 44px;
                height: 44px;
                background: linear-gradient(135deg, #6366f1, #8b5cf6);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                font-size: 18px;
            }}
            
            .user-details {{
                flex: 1;
            }}
            
            .user-name {{
                font-weight: 600;
                font-size: 15px;
            }}
            
            .user-id {{
                font-size: 12px;
                color: var(--text-secondary);
            }}
            
            /* Waiting Timer */
            .waiting-section {{
                background: rgba(249, 115, 22, 0.1);
                border: 1px solid rgba(249, 115, 22, 0.3);
                border-radius: 16px;
                padding: 20px;
                margin: 16px 0;
                text-align: center;
            }}
            
            .timer-title {{
                font-size: 13px;
                color: var(--text-secondary);
                margin-bottom: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
            }}
            
            .timer-title .icon {{
                animation: spin 2s linear infinite;
            }}
            
            @keyframes spin {{
                from {{ transform: rotate(0deg); }}
                to {{ transform: rotate(360deg); }}
            }}
            
            .timer-display {{
                font-size: 3rem;
                font-weight: 700;
                color: #f97316;
                font-family: 'Courier New', monospace;
                letter-spacing: 2px;
            }}
            
            .timer-meta {{
                display: flex;
                justify-content: space-around;
                margin-top: 16px;
                padding-top: 16px;
                border-top: 1px solid rgba(249, 115, 22, 0.2);
            }}
            
            .timer-stat {{
                text-align: center;
            }}
            
            .timer-stat-value {{
                font-size: 1.2rem;
                font-weight: 600;
                color: #fb923c;
            }}
            
            .timer-stat-label {{
                font-size: 11px;
                color: var(--text-secondary);
                text-transform: uppercase;
            }}
            
            /* Earnings Preview */
            .earnings-preview {{
                background: rgba(139, 92, 246, 0.1);
                border-radius: 12px;
                padding: 16px;
                margin: 16px 0;
            }}
            
            .earnings-title {{
                font-size: 13px;
                color: var(--secondary);
                font-weight: 600;
                margin-bottom: 12px;
            }}
            
            .earnings-row {{
                display: flex;
                justify-content: space-between;
                font-size: 13px;
                margin: 6px 0;
                color: var(--text-secondary);
            }}
            
            .earnings-row.total {{
                border-top: 1px solid var(--border);
                padding-top: 10px;
                margin-top: 10px;
                font-size: 18px;
                font-weight: 700;
                color: var(--text-primary);
            }}
            
            /* Action Buttons */
            .action-buttons {{
                display: flex;
                flex-direction: column;
                gap: 12px;
                margin-top: 20px;
            }}
            
            .action-btn {{
                width: 100%;
                padding: 16px;
                border: none;
                border-radius: 14px;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
            }}
            
            .btn-accept {{
                background: var(--gradient-driver);
                color: white;
            }}
            
            .btn-start {{
                background: linear-gradient(135deg, #6366f1, #4f46e5);
                color: white;
            }}
            
            .btn-arrive {{
                background: linear-gradient(135deg, #8b5cf6, #7c3aed);
                color: white;
            }}
            
            .btn-wait {{
                background: var(--gradient-wait);
                color: white;
            }}
            
            .btn-return {{
                background: var(--gradient-return);
                color: white;
            }}
            
            .btn-complete {{
                background: linear-gradient(135deg, #10b981, #059669);
                color: white;
            }}
            
            .action-btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
            }}
            
            .action-btn:active {{
                transform: translateY(0);
            }}
            
            /* Pending Rides List */
            .pending-ride {{
                background: var(--bg-input);
                border-radius: 14px;
                padding: 16px;
                margin-bottom: 12px;
                border: 1px solid var(--border);
                transition: all 0.3s ease;
            }}
            
            .pending-ride:hover {{
                border-color: var(--primary);
            }}
            
            .pending-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }}
            
            .pending-id {{
                font-size: 13px;
                color: var(--text-secondary);
            }}
            
            .pending-wr-badge {{
                background: var(--gradient-wait);
                color: white;
                font-size: 10px;
                padding: 4px 8px;
                border-radius: 6px;
                font-weight: 600;
            }}
            
            .pending-route {{
                font-size: 15px;
                margin-bottom: 12px;
            }}
            
            .pending-route .arrow {{
                color: var(--text-secondary);
                margin: 0 8px;
            }}
            
            .pending-meta {{
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            
            .pending-time {{
                font-size: 12px;
                color: var(--text-secondary);
            }}
            
            .btn-accept-small {{
                background: var(--gradient-driver);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 10px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }}
            
            .btn-accept-small:hover {{
                transform: scale(1.05);
            }}
            
            /* Empty State */
            .empty-state {{
                text-align: center;
                padding: 40px 20px;
                color: var(--text-secondary);
            }}
            
            .empty-state .icon {{
                font-size: 3rem;
                margin-bottom: 16px;
                opacity: 0.5;
            }}
            
            /* Toast */
            .toast {{
                position: fixed;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
                padding: 14px 28px;
                border-radius: 12px;
                font-size: 14px;
                font-weight: 500;
                z-index: 1000;
                display: none;
            }}
            
            .toast.visible {{
                display: block;
                animation: slideUp 0.3s ease;
            }}
            
            .toast.success {{
                background: linear-gradient(135deg, #10b981, #059669);
                color: white;
            }}
            
            .toast.error {{
                background: linear-gradient(135deg, #ef4444, #dc2626);
                color: white;
            }}
            
            @keyframes slideUp {{
                from {{ opacity: 0; transform: translate(-50%, 20px); }}
                to {{ opacity: 1; transform: translate(-50%, 0); }}
            }}
        </style>
    </head>
    <body>
        <div class="app-container">
            <!-- Header -->
            <div class="header">
                <div class="logo">UBERGO Driver</div>
                <div class="driver-badge">
                    <div class="icon">D</div>
                    <span>Driver ID: <strong>{DRIVER_ID}</strong></span>
                    <div class="online-dot"></div>
                </div>
            </div>
            
            <!-- Active Ride Section -->
            <div id="activeRideSection"></div>
            
            <!-- Pending Rides Section -->
            <div class="section-card">
                <div class="section-title">
                    <span class="icon">&#128203;</span>
                    Available Rides
                    <span class="count" id="pendingCount">0</span>
                </div>
                <div id="pendingRides">
                    <div class="empty-state">
                        <div class="icon">&#128663;</div>
                        <p>No pending rides at the moment</p>
                    </div>
                </div>
            </div>
            
            <!-- Toast -->
            <div class="toast" id="toast"></div>
        </div>

        <script>
            const DRIVER_ID = {DRIVER_ID};
            
            async function acceptRide(rideId) {{
                try {{
                    const response = await fetch(`/accept_ride/${{rideId}}`, {{ method: 'POST' }});
                    const data = await response.json();
                    
                    if (response.ok) {{
                        showToast('success', `Ride #${{rideId}} accepted!`);
                        updateDashboard();
                    }} else {{
                        showToast('error', data.detail || 'Failed to accept');
                    }}
                }} catch (error) {{
                    showToast('error', error.message);
                }}
            }}
            
            async function startRide(rideId) {{
                try {{
                    const response = await fetch(`/start_ride/${{rideId}}`, {{ method: 'POST' }});
                    if (response.ok) {{
                        showToast('success', 'Ride started! Heading to destination.');
                        updateDashboard();
                    }} else {{
                        const data = await response.json();
                        showToast('error', data.detail || 'Failed to start');
                    }}
                }} catch (error) {{
                    showToast('error', error.message);
                }}
            }}
            
            async function arriveDestination(rideId) {{
                try {{
                    const response = await fetch(`/arrive/${{rideId}}`, {{ method: 'POST' }});
                    if (response.ok) {{
                        showToast('success', 'Arrived at destination!');
                        updateDashboard();
                    }} else {{
                        const data = await response.json();
                        showToast('error', data.detail || 'Failed');
                    }}
                }} catch (error) {{
                    showToast('error', error.message);
                }}
            }}
            
            async function startReturn(rideId) {{
                try {{
                    const response = await fetch(`/start_return/${{rideId}}`, {{ method: 'POST' }});
                    if (response.ok) {{
                        showToast('success', 'Return trip started!');
                        updateDashboard();
                    }} else {{
                        const data = await response.json();
                        showToast('error', data.detail || 'Failed');
                    }}
                }} catch (error) {{
                    showToast('error', error.message);
                }}
            }}
            
            async function completeRide(rideId) {{
                try {{
                    const response = await fetch(`/complete_ride/${{rideId}}`, {{ method: 'POST' }});
                    if (response.ok) {{
                        showToast('success', 'Ride completed!');
                        updateDashboard();
                    }} else {{
                        const data = await response.json();
                        showToast('error', data.detail || 'Failed to complete');
                    }}
                }} catch (error) {{
                    showToast('error', error.message);
                }}
            }}
            
            async function updateDashboard() {{
                try {{
                    // Get active rides
                    const activeResponse = await fetch('/my_rides');
                    const activeRides = activeResponse.ok ? await activeResponse.json() : [];
                    
                    // Get pending rides
                    const pendingResponse = await fetch('/pending_rides');
                    const pendingRides = pendingResponse.ok ? await pendingResponse.json() : [];
                    
                    // Render active ride
                    if (activeRides.length > 0) {{
                        document.getElementById('activeRideSection').innerHTML = renderActiveRide(activeRides[0]);
                    }} else {{
                        document.getElementById('activeRideSection').innerHTML = '';
                    }}
                    
                    // Render pending rides
                    document.getElementById('pendingCount').textContent = pendingRides.length;
                    if (pendingRides.length > 0) {{
                        document.getElementById('pendingRides').innerHTML = pendingRides.map(renderPendingRide).join('');
                    }} else {{
                        document.getElementById('pendingRides').innerHTML = `
                            <div class="empty-state">
                                <div class="icon">&#128663;</div>
                                <p>No pending rides at the moment</p>
                            </div>
                        `;
                    }}
                }} catch (error) {{
                    console.error('Error updating dashboard:', error);
                }}
            }}
            
            function renderActiveRide(ride) {{
                const statusClass = ride.status.toLowerCase();
                const isWaitReturn = ride.is_wait_return;
                
                let statusBadge = '';
                if (isWaitReturn) {{
                    statusBadge = '<div class="ride-type-badge badge-wait-return">&#8635; Wait & Return</div>';
                }} else {{
                    statusBadge = '<div class="ride-type-badge badge-standard">Standard Ride</div>';
                }}
                
                // Waiting Timer
                let waitingSection = '';
                if (ride.status === 'WAITING' && ride.wait_started_at) {{
                    const waitStart = new Date(ride.wait_started_at);  // Parse as local time
                    const now = new Date();
                    const waitedSeconds = Math.max(0, Math.floor((now - waitStart) / 1000));  // Ensure non-negative
                    const mins = Math.floor(waitedSeconds / 60);
                    const secs = waitedSeconds % 60;
                    const requested = ride.wait_time_requested || 45;
                    const charge = (waitedSeconds / 60 * 2).toFixed(2);  // ₹2 per minute
                    
                    waitingSection = `
                        <div class="waiting-section">
                            <div class="timer-title">
                                <span class="icon">&#9200;</span>
                                WAITING FOR CUSTOMER
                            </div>
                            <div class="timer-display">${{String(mins).padStart(2, '0')}}:${{String(secs).padStart(2, '0')}}</div>
                            <div class="timer-meta">
                                <div class="timer-stat">
                                    <div class="timer-stat-value">${{requested}} min</div>
                                    <div class="timer-stat-label">Requested</div>
                                </div>
                                <div class="timer-stat">
                                    <div class="timer-stat-value">₹${{charge}}</div>
                                    <div class="timer-stat-label">Waiting Charge</div>
                                </div>
                            </div>
                        </div>
                    `;
                }}
                
                // Earnings Preview
                let earningsPreview = '';
                if (isWaitReturn && (ride.status === 'WAITING' || ride.status === 'RETURNING')) {{
                    const waitCharge = Math.max(0, ride.waiting_charge || 0);  // Ensure non-negative
                    const returnFareVal = ride.return_fare || ride.base_fare || 50;
                    const premiumFee = ride.premium_fee || 50;
                    const baseFare = ride.base_fare || 50;
                    const total = baseFare + waitCharge + (ride.status === 'RETURNING' ? returnFareVal : 0) + premiumFee;
                    
                    let returnFareRow = '';
                    if (ride.status === 'RETURNING') {{
                        returnFareRow = '<div class="earnings-row"><span>Return Fare</span><span>₹' + returnFareVal.toFixed(2) + '</span></div>';
                    }}
                    
                    earningsPreview = `
                        <div class="earnings-preview">
                            <div class="earnings-title">Estimated Earnings</div>
                            <div class="earnings-row"><span>Outbound Fare</span><span>₹${{baseFare.toFixed(2)}}</span></div>
                            <div class="earnings-row"><span>Waiting Charge</span><span>₹${{waitCharge.toFixed(2)}}</span></div>
                            ${{returnFareRow}}
                            <div class="earnings-row"><span>Premium Fee</span><span>₹${{premiumFee.toFixed(2)}}</span></div>
                            <div class="earnings-row total"><span>Total</span><span>₹${{total.toFixed(2)}}</span></div>
                        </div>
                    `;
                }}
                
                // Action Buttons based on status
                let actionButtons = '';
                switch (ride.status) {{
                    case 'ASSIGNED':
                        actionButtons = `<button class="action-btn btn-accept" onclick="acceptRide(${{ride.id}})">&#10003; Accept This Ride</button>`;
                        break;
                    case 'ACCEPTED':
                        actionButtons = `<button class="action-btn btn-start" onclick="startRide(${{ride.id}})">&#128663; Start Trip - Pickup Customer</button>`;
                        break;
                    case 'IN_PROGRESS':
                        actionButtons = `<button class="action-btn btn-arrive" onclick="arriveDestination(${{ride.id}})">&#128205; Arrived at Destination</button>`;
                        break;
                    case 'WAITING':
                        actionButtons = `<button class="action-btn btn-return" onclick="startReturn(${{ride.id}})">&#8634; Customer Ready - Start Return Trip</button>`;
                        break;
                    case 'RETURNING':
                        actionButtons = `<button class="action-btn btn-complete" onclick="completeRide(${{ride.id}})">&#10003; Complete Ride</button>`;
                        break;
                }}
                
                return `
                    <div class="section-card">
                        <div class="section-title">
                            <span class="icon">&#128663;</span>
                            Current Ride
                        </div>
                        <div class="active-ride ${{statusClass}}">
                            ${{statusBadge}}
                            
                            <div class="ride-header">
                                <span class="ride-id">Ride #${{ride.id}}</span>
                                <span class="ride-status status-${{statusClass}}">${{ride.status.replace('_', ' ')}}</span>
                            </div>
                            
                            <div class="user-info">
                                <div class="user-avatar">U</div>
                                <div class="user-details">
                                    <div class="user-name">User #${{ride.user_id}}</div>
                                    <div class="user-id">Customer</div>
                                </div>
                            </div>
                            
                            <div class="route-display">
                                <div class="route-line">
                                    <div class="route-dot pickup"></div>
                                    <div class="route-connector"></div>
                                    <div class="route-dot dest"></div>
                                </div>
                                <div class="route-details">
                                    <div class="route-point">
                                        <div class="route-label">Pickup</div>
                                        <div class="route-address">${{ride.source}}</div>
                                    </div>
                                    <div class="route-point">
                                        <div class="route-label">Destination</div>
                                        <div class="route-address">${{ride.destination}}</div>
                                    </div>
                                </div>
                            </div>
                            
                            ${{waitingSection}}
                            ${{earningsPreview}}
                            
                            <div class="action-buttons">
                                ${{actionButtons}}
                            </div>
                        </div>
                    </div>
                `;
            }}
            
            function renderPendingRide(ride) {{
                const wrBadge = ride.is_wait_return 
                    ? '<span class="pending-wr-badge">W&R</span>' 
                    : '';
                
                return `
                    <div class="pending-ride">
                        <div class="pending-header">
                            <span class="pending-id">Ride #${{ride.id}}</span>
                            ${{wrBadge}}
                        </div>
                        <div class="pending-route">
                            <strong>${{ride.source}}</strong>
                            <span class="arrow">&rarr;</span>
                            <strong>${{ride.destination}}</strong>
                        </div>
                        <div class="pending-meta">
                            <span class="pending-time">${{new Date(ride.created_at).toLocaleTimeString()}}</span>
                            <button class="btn-accept-small" onclick="acceptRide(${{ride.id}})">Accept</button>
                        </div>
                    </div>
                `;
            }}
            
            function showToast(type, message) {{
                const toast = document.getElementById('toast');
                toast.className = `toast ${{type}} visible`;
                toast.textContent = message;
                setTimeout(() => toast.classList.remove('visible'), 3000);
            }}
            
            // Update every 2 seconds
            setInterval(updateDashboard, 2000);
            updateDashboard();
        </script>
    </body>
    </html>
    """
    return html


@app.get("/pending_rides", response_model=List[RideOut])
async def get_pending_rides(db: AsyncSession = Depends(get_db)):
    """Get all pending rides."""
    rides = await list_pending_rides(db)
    return rides


@app.get("/my_rides", response_model=List[RideOut])
async def get_my_rides(db: AsyncSession = Depends(get_db)):
    """Get all active rides for this driver."""
    rides = await get_driver_all_active_rides(db, DRIVER_ID)
    return rides


@app.get("/current_ride", response_model=Optional[RideOut])
async def get_current_ride(db: AsyncSession = Depends(get_db)):
    """Get the current ride for this driver."""
    ride = await get_driver_current_ride(db, DRIVER_ID)
    return ride


@app.post("/accept_ride/{ride_id}", response_model=RideOut)
async def accept_new_ride(ride_id: int, db: AsyncSession = Depends(get_db)):
    """Accept a ride - either assign a pending ride or accept an assigned ride."""
    ride = await get_ride_by_id(db, ride_id)
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    
    # If ride is PENDING, try to assign it to this driver
    if ride.status == "PENDING":
        success = await atomic_assign_ride(db, ride_id, DRIVER_ID, PORT)
        if not success:
            raise HTTPException(status_code=400, detail="Ride could not be assigned (may have been taken)")
    
    # If ride is ASSIGNED to this driver, accept it
    elif ride.status == "ASSIGNED" and ride.assigned_driver_id == DRIVER_ID:
        success = await accept_ride(db, ride_id)
        if not success:
            raise HTTPException(status_code=400, detail="Could not accept ride")
    
    # If ride is already accepted or in progress for this driver, just return it
    elif ride.assigned_driver_id == DRIVER_ID:
        pass  # Already accepted/in progress
    
    else:
        raise HTTPException(status_code=400, detail="Ride is not available for you")
    
    ride = await get_ride_by_id(db, ride_id)
    return ride


@app.post("/start_ride/{ride_id}", response_model=RideOut)
async def start_trip(ride_id: int, db: AsyncSession = Depends(get_db)):
    """Start a ride (pickup customer, head to destination)."""
    # First accept the ride if it's assigned
    ride = await get_ride_by_id(db, ride_id)
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    
    if ride.status == "ASSIGNED":
        await accept_ride(db, ride_id)
    
    success = await start_ride(db, ride_id)
    if not success:
        raise HTTPException(status_code=400, detail="Could not start ride")
    
    ride = await get_ride_by_id(db, ride_id)
    return ride


@app.post("/arrive/{ride_id}", response_model=RideOut)
async def arrive_at_dest(ride_id: int, db: AsyncSession = Depends(get_db)):
    """Arrive at destination. For Wait & Return, this starts waiting."""
    success = await arrive_at_destination(db, ride_id)
    if not success:
        raise HTTPException(status_code=400, detail="Could not mark arrival")
    
    ride = await get_ride_by_id(db, ride_id)
    return ride


@app.post("/start_return/{ride_id}", response_model=RideOut)
async def start_return_trip_endpoint(ride_id: int, db: AsyncSession = Depends(get_db)):
    """Start return trip for Wait & Return rides."""
    success = await start_return_trip(db, ride_id)
    if not success:
        raise HTTPException(status_code=400, detail="Could not start return trip")
    
    ride = await get_ride_by_id(db, ride_id)
    return ride


@app.post("/complete_ride/{ride_id}", response_model=RideOut)
async def finish_ride(ride_id: int, db: AsyncSession = Depends(get_db)):
    """Complete a ride."""
    ride = await get_ride_by_id(db, ride_id)
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    
    if ride.is_wait_return and ride.status == "RETURNING":
        success = await complete_wait_return_ride(db, ride_id)
    else:
        success = await complete_ride(db, ride_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Could not complete ride")
    
    ride = await get_ride_by_id(db, ride_id)
    return ride


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=PORT, env_file=".env")
