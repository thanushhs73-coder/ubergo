import sys
import os

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from fastapi import FastAPI, Depends, HTTPException, Form, Body
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database import get_db, init_db
from shared.crud import (
    create_ride, 
    get_rides_for_user, 
    get_user_by_id,
    get_ride_by_id,
    get_user_active_rides
)
from shared.schemas import RideCreate, RideOut
from typing import List, Optional

# Get user_id from environment variable or default
USER_ID = int(os.getenv("USER_ID", "1"))
PORT = int(os.getenv("PORT", "8002"))

app = FastAPI(title=f"UBERGO User Portal")


@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    await init_db()


@app.get("/", response_class=HTMLResponse)
async def get_user_page(db: AsyncSession = Depends(get_db)):
    """Serve the user portal page with Wait & Return feature."""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>UBERGO - Book Your Ride</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            :root {{
                --primary: #6366f1;
                --primary-dark: #4f46e5;
                --secondary: #8b5cf6;
                --success: #10b981;
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
                --gradient-1: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                --gradient-2: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                --gradient-wait: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
            }}
            
            body {{
                font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
                background: var(--bg-dark);
                color: var(--text-primary);
                min-height: 100vh;
            }}
            
            .app-container {{
                max-width: 480px;
                margin: 0 auto;
                padding: 20px;
                min-height: 100vh;
            }}
            
            /* Header */
            .header {{
                text-align: center;
                padding: 30px 0;
            }}
            
            .logo {{
                font-size: 2.5rem;
                font-weight: 800;
                background: var(--gradient-1);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                letter-spacing: -1px;
            }}
            
            .user-badge {{
                display: inline-flex;
                align-items: center;
                gap: 8px;
                background: var(--bg-card);
                padding: 8px 16px;
                border-radius: 20px;
                margin-top: 12px;
                border: 1px solid var(--border);
            }}
            
            .user-badge .icon {{
                width: 24px;
                height: 24px;
                background: var(--gradient-1);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
            }}
            
            .user-badge span {{
                color: var(--text-secondary);
                font-size: 14px;
            }}
            
            .user-badge strong {{
                color: var(--text-primary);
            }}
            
            /* Booking Card */
            .booking-card {{
                background: var(--bg-card);
                border-radius: 24px;
                padding: 24px;
                margin-bottom: 20px;
                border: 1px solid var(--border);
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            }}
            
            .card-title {{
                font-size: 1.25rem;
                font-weight: 600;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .card-title .icon {{
                font-size: 1.5rem;
            }}
            
            /* Input Fields */
            .input-group {{
                position: relative;
                margin-bottom: 16px;
            }}
            
            .input-group .icon {{
                position: absolute;
                left: 16px;
                top: 50%;
                transform: translateY(-50%);
                width: 20px;
                height: 20px;
                border-radius: 50%;
            }}
            
            .input-group .icon.pickup {{
                background: #10b981;
            }}
            
            .input-group .icon.destination {{
                background: #ef4444;
            }}
            
            .input-group input {{
                width: 100%;
                padding: 16px 16px 16px 48px;
                background: var(--bg-input);
                border: 2px solid transparent;
                border-radius: 12px;
                color: var(--text-primary);
                font-size: 16px;
                transition: all 0.3s ease;
            }}
            
            .input-group input:focus {{
                outline: none;
                border-color: var(--primary);
                background: rgba(99, 102, 241, 0.1);
            }}
            
            .input-group input::placeholder {{
                color: var(--text-secondary);
            }}
            
            /* Wait & Return Toggle */
            .wait-return-section {{
                background: linear-gradient(135deg, rgba(249, 115, 22, 0.1) 0%, rgba(234, 88, 12, 0.1) 100%);
                border: 2px solid rgba(249, 115, 22, 0.3);
                border-radius: 16px;
                padding: 20px;
                margin: 20px 0;
                transition: all 0.3s ease;
            }}
            
            .wait-return-section.active {{
                border-color: var(--waiting);
                background: linear-gradient(135deg, rgba(249, 115, 22, 0.2) 0%, rgba(234, 88, 12, 0.2) 100%);
            }}
            
            .wait-return-header {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 12px;
            }}
            
            .wait-return-title {{
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .wait-return-title h3 {{
                font-size: 1rem;
                font-weight: 600;
                color: #f97316;
            }}
            
            .premium-badge {{
                background: var(--gradient-wait);
                color: white;
                font-size: 10px;
                padding: 4px 8px;
                border-radius: 6px;
                font-weight: 700;
                text-transform: uppercase;
            }}
            
            .wait-return-desc {{
                font-size: 13px;
                color: var(--text-secondary);
                line-height: 1.5;
                margin-bottom: 16px;
            }}
            
            /* Toggle Switch */
            .toggle-container {{
                display: flex;
                align-items: center;
                gap: 12px;
            }}
            
            .toggle {{
                position: relative;
                width: 52px;
                height: 28px;
            }}
            
            .toggle input {{
                opacity: 0;
                width: 0;
                height: 0;
            }}
            
            .toggle-slider {{
                position: absolute;
                cursor: pointer;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: var(--bg-input);
                border-radius: 28px;
                transition: 0.3s;
            }}
            
            .toggle-slider:before {{
                position: absolute;
                content: "";
                height: 22px;
                width: 22px;
                left: 3px;
                bottom: 3px;
                background: white;
                border-radius: 50%;
                transition: 0.3s;
            }}
            
            .toggle input:checked + .toggle-slider {{
                background: var(--gradient-wait);
            }}
            
            .toggle input:checked + .toggle-slider:before {{
                transform: translateX(24px);
            }}
            
            /* Time Selector */
            .time-selector {{
                display: none;
                margin-top: 16px;
            }}
            
            .time-selector.visible {{
                display: block;
                animation: slideDown 0.3s ease;
            }}
            
            @keyframes slideDown {{
                from {{
                    opacity: 0;
                    transform: translateY(-10px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            
            .time-selector label {{
                display: block;
                font-size: 13px;
                color: var(--text-secondary);
                margin-bottom: 10px;
            }}
            
            .time-options {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 8px;
            }}
            
            .time-option {{
                background: var(--bg-input);
                border: 2px solid transparent;
                border-radius: 10px;
                padding: 12px 8px;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s ease;
            }}
            
            .time-option:hover {{
                border-color: var(--waiting);
            }}
            
            .time-option.selected {{
                background: var(--gradient-wait);
                border-color: var(--waiting);
            }}
            
            .time-option .mins {{
                font-size: 1.25rem;
                font-weight: 700;
            }}
            
            .time-option .label {{
                font-size: 10px;
                color: var(--text-secondary);
                text-transform: uppercase;
            }}
            
            .time-option.selected .label {{
                color: rgba(255,255,255,0.8);
            }}
            
            /* Premium Info */
            .premium-info {{
                display: none;
                background: rgba(249, 115, 22, 0.1);
                border-radius: 10px;
                padding: 12px;
                margin-top: 16px;
            }}
            
            .premium-info.visible {{
                display: block;
            }}
            
            .premium-row {{
                display: flex;
                justify-content: space-between;
                font-size: 13px;
                margin: 4px 0;
            }}
            
            .premium-row .value {{
                font-weight: 600;
                color: #f97316;
            }}
            
            /* Book Button */
            .book-btn {{
                width: 100%;
                padding: 18px;
                background: var(--gradient-1);
                border: none;
                border-radius: 14px;
                color: white;
                font-size: 1.1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                margin-top: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
            }}
            
            .book-btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 10px 30px rgba(99, 102, 241, 0.4);
            }}
            
            .book-btn:active {{
                transform: translateY(0);
            }}
            
            .book-btn.wait-return {{
                background: var(--gradient-wait);
            }}
            
            .book-btn.wait-return:hover {{
                box-shadow: 0 10px 30px rgba(249, 115, 22, 0.4);
            }}
            
            /* Current Ride Card */
            .ride-card {{
                background: var(--bg-card);
                border-radius: 20px;
                padding: 20px;
                margin-bottom: 20px;
                border: 1px solid var(--border);
                position: relative;
                overflow: hidden;
            }}
            
            .ride-card::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
            }}
            
            .ride-card.pending::before {{
                background: linear-gradient(90deg, #f59e0b, #fbbf24);
            }}
            
            .ride-card.assigned::before {{
                background: linear-gradient(90deg, #3b82f6, #60a5fa);
            }}
            
            .ride-card.accepted::before,
            .ride-card.in_progress::before {{
                background: linear-gradient(90deg, #10b981, #34d399);
            }}
            
            .ride-card.waiting::before {{
                background: linear-gradient(90deg, #f97316, #fb923c);
                animation: pulse-bar 2s infinite;
            }}
            
            .ride-card.returning::before {{
                background: linear-gradient(90deg, #06b6d4, #22d3ee);
            }}
            
            .ride-card.completed::before {{
                background: linear-gradient(90deg, #8b5cf6, #a78bfa);
            }}
            
            @keyframes pulse-bar {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.5; }}
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
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
            }}
            
            .status-pending {{ background: rgba(245, 158, 11, 0.2); color: #fbbf24; }}
            .status-assigned {{ background: rgba(59, 130, 246, 0.2); color: #60a5fa; }}
            .status-accepted {{ background: rgba(16, 185, 129, 0.2); color: #34d399; }}
            .status-in_progress {{ background: rgba(16, 185, 129, 0.2); color: #34d399; }}
            .status-waiting {{ background: rgba(249, 115, 22, 0.2); color: #fb923c; animation: blink 1s infinite; }}
            .status-returning {{ background: rgba(6, 182, 212, 0.2); color: #22d3ee; }}
            .status-completed {{ background: rgba(139, 92, 246, 0.2); color: #a78bfa; }}
            
            @keyframes blink {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.6; }}
            }}
            
            .ride-route {{
                display: flex;
                align-items: stretch;
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
                width: 12px;
                height: 12px;
                border-radius: 50%;
            }}
            
            .route-dot.pickup {{ background: #10b981; }}
            .route-dot.dest {{ background: #ef4444; }}
            
            .route-connector {{
                width: 2px;
                flex: 1;
                background: linear-gradient(180deg, #10b981 0%, #ef4444 100%);
                min-height: 30px;
            }}
            
            .route-details {{
                flex: 1;
            }}
            
            .route-point {{
                margin-bottom: 12px;
            }}
            
            .route-label {{
                font-size: 11px;
                color: var(--text-secondary);
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .route-address {{
                font-size: 15px;
                font-weight: 500;
                margin-top: 2px;
            }}
            
            /* Wait & Return Badge on Ride */
            .wr-badge {{
                display: inline-flex;
                align-items: center;
                gap: 6px;
                background: var(--gradient-wait);
                color: white;
                padding: 6px 12px;
                border-radius: 8px;
                font-size: 12px;
                font-weight: 600;
                margin-bottom: 12px;
            }}
            
            /* Waiting Timer */
            .waiting-timer {{
                background: rgba(249, 115, 22, 0.1);
                border: 1px solid rgba(249, 115, 22, 0.3);
                border-radius: 12px;
                padding: 16px;
                margin: 16px 0;
                text-align: center;
            }}
            
            .timer-label {{
                font-size: 12px;
                color: var(--text-secondary);
                margin-bottom: 8px;
            }}
            
            .timer-value {{
                font-size: 2rem;
                font-weight: 700;
                color: #f97316;
                font-family: 'Courier New', monospace;
            }}
            
            .timer-info {{
                font-size: 12px;
                color: var(--text-secondary);
                margin-top: 8px;
            }}
            
            /* Driver Info */
            .driver-info {{
                background: rgba(99, 102, 241, 0.1);
                border-radius: 12px;
                padding: 12px;
                display: flex;
                align-items: center;
                gap: 12px;
                margin-top: 12px;
            }}
            
            .driver-avatar {{
                width: 40px;
                height: 40px;
                background: var(--gradient-1);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
            }}
            
            .driver-details {{
                flex: 1;
            }}
            
            .driver-name {{
                font-weight: 600;
            }}
            
            .driver-id {{
                font-size: 12px;
                color: var(--text-secondary);
            }}
            
            /* Fare Breakdown */
            .fare-breakdown {{
                background: rgba(139, 92, 246, 0.1);
                border-radius: 12px;
                padding: 16px;
                margin-top: 16px;
            }}
            
            .fare-title {{
                font-size: 14px;
                font-weight: 600;
                margin-bottom: 12px;
                color: var(--secondary);
            }}
            
            .fare-row {{
                display: flex;
                justify-content: space-between;
                font-size: 13px;
                margin: 6px 0;
                color: var(--text-secondary);
            }}
            
            .fare-row.total {{
                border-top: 1px solid var(--border);
                padding-top: 8px;
                margin-top: 8px;
                font-size: 16px;
                font-weight: 700;
                color: var(--text-primary);
            }}
            
            /* Recent Rides */
            .recent-rides {{
                margin-top: 24px;
            }}
            
            .section-title {{
                font-size: 1rem;
                font-weight: 600;
                margin-bottom: 16px;
                color: var(--text-secondary);
            }}
            
            .ride-history-item {{
                background: var(--bg-card);
                border-radius: 12px;
                padding: 14px;
                margin-bottom: 10px;
                border: 1px solid var(--border);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            
            .history-route {{
                font-size: 14px;
            }}
            
            .history-meta {{
                font-size: 12px;
                color: var(--text-secondary);
                margin-top: 4px;
            }}
            
            .history-fare {{
                font-weight: 600;
                color: var(--success);
            }}
            
            /* Message Toast */
            .toast {{
                position: fixed;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
                padding: 14px 24px;
                border-radius: 12px;
                font-size: 14px;
                font-weight: 500;
                z-index: 1000;
                animation: slideUp 0.3s ease;
                display: none;
            }}
            
            .toast.visible {{
                display: block;
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
                from {{
                    opacity: 0;
                    transform: translate(-50%, 20px);
                }}
                to {{
                    opacity: 1;
                    transform: translate(-50%, 0);
                }}
            }}
            
            /* No Rides State */
            .empty-state {{
                text-align: center;
                padding: 40px 20px;
                color: var(--text-secondary);
            }}
            
            .empty-state .icon {{
                font-size: 3rem;
                margin-bottom: 16px;
            }}
        </style>
    </head>
    <body>
        <div class="app-container">
            <!-- Header -->
            <div class="header">
                <div class="logo">UBERGO</div>
                <div class="user-badge">
                    <div class="icon">U</div>
                    <span>User ID: <strong>{USER_ID}</strong></span>
                </div>
            </div>
            
            <!-- Booking Card -->
            <div class="booking-card">
                <div class="card-title">
                    <span class="icon">&#128205;</span>
                    Book Your Ride
                </div>
                
                <form id="bookForm">
                    <div class="input-group">
                        <div class="icon pickup"></div>
                        <input type="text" id="source" placeholder="Pickup location" required>
                    </div>
                    
                    <div class="input-group">
                        <div class="icon destination"></div>
                        <input type="text" id="destination" placeholder="Where to?" required>
                    </div>
                    
                    <!-- Wait & Return Section -->
                    <div class="wait-return-section" id="waitReturnSection">
                        <div class="wait-return-header">
                            <div class="wait-return-title">
                                <h3>Wait & Return</h3>
                                <span class="premium-badge">Premium</span>
                            </div>
                            <label class="toggle">
                                <input type="checkbox" id="waitReturnToggle">
                                <span class="toggle-slider"></span>
                            </label>
                        </div>
                        <p class="wait-return-desc">
                            Driver waits at your destination and brings you back. Perfect for quick errands, hospital visits, or meetings.
                        </p>
                        
                        <div class="time-selector" id="timeSelector">
                            <label>Select expected waiting time:</label>
                            <div class="time-options">
                                <div class="time-option" data-time="15">
                                    <div class="mins">15</div>
                                    <div class="label">mins</div>
                                </div>
                                <div class="time-option" data-time="30">
                                    <div class="mins">30</div>
                                    <div class="label">mins</div>
                                </div>
                                <div class="time-option selected" data-time="45">
                                    <div class="mins">45</div>
                                    <div class="label">mins</div>
                                </div>
                                <div class="time-option" data-time="60">
                                    <div class="mins">60</div>
                                    <div class="label">mins</div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="premium-info" id="premiumInfo">
                            <div class="premium-row">
                                <span>Premium Fee</span>
                                <span class="value">₹50.00</span>
                            </div>
                            <div class="premium-row">
                                <span>Waiting Charge</span>
                                <span class="value">₹2.00/min</span>
                            </div>
                        </div>
                    </div>
                    
                    <button type="submit" class="book-btn" id="bookBtn">
                        <span>&#128663;</span>
                        <span id="bookBtnText">Book Ride</span>
                    </button>
                </form>
            </div>
            
            <!-- Current Ride -->
            <div id="currentRide"></div>
            
            <!-- Recent Rides -->
            <div class="recent-rides">
                <div class="section-title">Recent Rides</div>
                <div id="rideHistory"></div>
            </div>
            
            <!-- Toast Message -->
            <div class="toast" id="toast"></div>
        </div>

        <script>
            const USER_ID = {USER_ID};
            let selectedWaitTime = 45;
            let isWaitReturn = false;
            
            // Toggle Wait & Return
            document.getElementById('waitReturnToggle').addEventListener('change', function() {{
                isWaitReturn = this.checked;
                const section = document.getElementById('waitReturnSection');
                const timeSelector = document.getElementById('timeSelector');
                const premiumInfo = document.getElementById('premiumInfo');
                const bookBtn = document.getElementById('bookBtn');
                const bookBtnText = document.getElementById('bookBtnText');
                
                if (isWaitReturn) {{
                    section.classList.add('active');
                    timeSelector.classList.add('visible');
                    premiumInfo.classList.add('visible');
                    bookBtn.classList.add('wait-return');
                    bookBtnText.textContent = 'Book Wait & Return';
                }} else {{
                    section.classList.remove('active');
                    timeSelector.classList.remove('visible');
                    premiumInfo.classList.remove('visible');
                    bookBtn.classList.remove('wait-return');
                    bookBtnText.textContent = 'Book Ride';
                }}
            }});
            
            // Time Selection
            document.querySelectorAll('.time-option').forEach(option => {{
                option.addEventListener('click', function() {{
                    document.querySelectorAll('.time-option').forEach(o => o.classList.remove('selected'));
                    this.classList.add('selected');
                    selectedWaitTime = parseInt(this.dataset.time);
                }});
            }});
            
            // Book Ride
            document.getElementById('bookForm').addEventListener('submit', async (e) => {{
                e.preventDefault();
                const source = document.getElementById('source').value;
                const destination = document.getElementById('destination').value;
                
                try {{
                    const response = await fetch('/book_ride', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{
                            source: source,
                            destination: destination,
                            is_wait_return: isWaitReturn,
                            wait_time_requested: isWaitReturn ? selectedWaitTime : null
                        }})
                    }});
                    
                    const data = await response.json();
                    
                    if (response.ok) {{
                        const rideType = isWaitReturn ? 'Wait & Return' : '';
                        showToast('success', `Ride booked! ID: ${{data.id}} ${{rideType}}`);
                        document.getElementById('bookForm').reset();
                        document.getElementById('waitReturnToggle').checked = false;
                        document.getElementById('waitReturnToggle').dispatchEvent(new Event('change'));
                        updateRideStatus();
                    }} else {{
                        showToast('error', data.detail || 'Failed to book ride');
                    }}
                }} catch (error) {{
                    showToast('error', error.message);
                }}
            }});
            
            async function updateRideStatus() {{
                try {{
                    const response = await fetch('/ride_status');
                    const rides = await response.json();
                    
                    const activeStatuses = ['PENDING', 'ASSIGNED', 'ACCEPTED', 'IN_PROGRESS', 'WAITING', 'RETURNING'];
                    const activeRides = rides.filter(r => activeStatuses.includes(r.status));
                    const completedRides = rides.filter(r => r.status === 'COMPLETED');
                    
                    // Show active ride
                    if (activeRides.length > 0) {{
                        const ride = activeRides[0];
                        document.getElementById('currentRide').innerHTML = renderRideCard(ride);
                    }} else {{
                        document.getElementById('currentRide').innerHTML = '';
                    }}
                    
                    // Show recent completed rides
                    if (completedRides.length > 0) {{
                        document.getElementById('rideHistory').innerHTML = completedRides.slice(0, 5).map(ride => `
                            <div class="ride-history-item">
                                <div>
                                    <div class="history-route">${{ride.source}} &rarr; ${{ride.destination}}</div>
                                    <div class="history-meta">${{new Date(ride.created_at).toLocaleDateString()}} ${{ride.is_wait_return ? '| Wait & Return' : ''}}</div>
                                </div>
                                <div class="history-fare">${{ride.total_fare > 0 ? '₹' + ride.total_fare.toFixed(2) : '-'}}</div>
                            </div>
                        `).join('');
                    }} else {{
                        document.getElementById('rideHistory').innerHTML = `
                            <div class="empty-state">
                                <div class="icon">&#128663;</div>
                                <p>No rides yet. Book your first ride!</p>
                            </div>
                        `;
                    }}
                }} catch (error) {{
                    console.error('Error fetching ride status:', error);
                }}
            }}
            
            function renderRideCard(ride) {{
                const statusClass = ride.status.toLowerCase();
                const wrBadge = ride.is_wait_return ? `<div class="wr-badge">&#8635; Wait & Return</div>` : '';
                
                let waitingTimer = '';
                if (ride.status === 'WAITING' && ride.wait_started_at) {{
                    const waitStart = new Date(ride.wait_started_at);  // Parse as local time
                    const now = new Date();
                    const waitedSeconds = Math.max(0, Math.floor((now - waitStart) / 1000));  // Ensure non-negative
                    const mins = Math.floor(waitedSeconds / 60);
                    const secs = waitedSeconds % 60;
                    const requested = ride.wait_time_requested || 45;
                    
                    waitingTimer = `
                        <div class="waiting-timer">
                            <div class="timer-label">Waiting Time</div>
                            <div class="timer-value">${{String(mins).padStart(2, '0')}}:${{String(secs).padStart(2, '0')}}</div>
                            <div class="timer-info">Requested: ${{requested}} mins | Charge: ₹2/min</div>
                        </div>
                    `;
                }}
                
                let driverInfo = '';
                if (ride.assigned_driver_id) {{
                    driverInfo = `
                        <div class="driver-info">
                            <div class="driver-avatar">D</div>
                            <div class="driver-details">
                                <div class="driver-name">Driver #${{ride.assigned_driver_id}}</div>
                                <div class="driver-id">Assigned to your ride</div>
                            </div>
                        </div>
                    `;
                }}
                
                let fareBreakdown = '';
                if (ride.status === 'COMPLETED' && ride.is_wait_return) {{
                    fareBreakdown = `
                        <div class="fare-breakdown">
                            <div class="fare-title">Fare Breakdown</div>
                            <div class="fare-row"><span>Base Fare (Outbound)</span><span>₹${{ride.base_fare.toFixed(2)}}</span></div>
                            <div class="fare-row"><span>Waiting Charge</span><span>₹${{ride.waiting_charge.toFixed(2)}}</span></div>
                            <div class="fare-row"><span>Return Fare</span><span>₹${{ride.return_fare.toFixed(2)}}</span></div>
                            <div class="fare-row"><span>Premium Fee</span><span>₹${{ride.premium_fee.toFixed(2)}}</span></div>
                            <div class="fare-row total"><span>Total</span><span>₹${{ride.total_fare.toFixed(2)}}</span></div>
                        </div>
                    `;
                }} else if (ride.status === 'COMPLETED') {{
                    fareBreakdown = `
                        <div class="fare-breakdown">
                            <div class="fare-title">Fare</div>
                            <div class="fare-row total"><span>Total</span><span>₹${{ride.total_fare.toFixed(2)}}</span></div>
                        </div>
                    `;
                }}
                
                return `
                    <div class="ride-card ${{statusClass}}">
                        <div class="ride-header">
                            <span class="ride-id">Ride #${{ride.id}}</span>
                            <span class="ride-status status-${{statusClass}}">${{ride.status.replace('_', ' ')}}</span>
                        </div>
                        
                        ${{wrBadge}}
                        
                        <div class="ride-route">
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
                        
                        ${{waitingTimer}}
                        ${{driverInfo}}
                        ${{fareBreakdown}}
                    </div>
                `;
            }}
            
            function showToast(type, message) {{
                const toast = document.getElementById('toast');
                toast.className = `toast ${{type}} visible`;
                toast.textContent = message;
                setTimeout(() => toast.classList.remove('visible'), 4000);
            }}
            
            // Update every 2 seconds
            setInterval(updateRideStatus, 2000);
            updateRideStatus();
        </script>
    </body>
    </html>
    """
    return html


@app.post("/book_ride", response_model=RideOut)
async def book_ride(
    request: dict = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """Book a new ride with optional Wait & Return."""
    source = request.get("source")
    destination = request.get("destination")
    is_wait_return = request.get("is_wait_return", False)
    wait_time_requested = request.get("wait_time_requested")
    
    if not source or not destination:
        raise HTTPException(status_code=400, detail="Source and destination are required")
    
    # Check if user has an active ride
    active_rides = await get_user_active_rides(db, USER_ID)
    if active_rides:
        raise HTTPException(
            status_code=400, 
            detail=f"You already have an active ride. Please complete it before booking another one."
        )
    
    ride_create = RideCreate(
        user_id=USER_ID,
        user_port=PORT,
        source=source,
        destination=destination,
        is_wait_return=is_wait_return,
        wait_time_requested=wait_time_requested if is_wait_return else None
    )
    ride = await create_ride(db, ride_create)
    return ride


@app.get("/ride_status", response_model=List[RideOut])
async def get_ride_status(db: AsyncSession = Depends(get_db)):
    """Get all rides for this user."""
    rides = await get_rides_for_user(db, USER_ID)
    return rides


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=PORT, env_file=".env")
