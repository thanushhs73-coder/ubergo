from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from datetime import datetime
from shared.models import User, Driver, RideRequest, RideStatus
from shared.schemas import UserCreate, DriverCreate, RideCreate


async def get_next_free_user_port(db: AsyncSession) -> int:
    """Get the next free port in user range 8002-8899."""
    result = await db.execute(
        select(func.max(User.user_port)).where(User.user_port >= 8002).where(User.user_port <= 8899)
    )
    max_port = result.scalar()
    if max_port is None:
        return 8002
    return max_port + 1 if max_port < 8899 else None


async def get_next_free_driver_port(db: AsyncSession) -> int:
    """Get the next free port in driver range 8901-8999."""
    result = await db.execute(
        select(func.max(Driver.assigned_port)).where(Driver.assigned_port >= 8901).where(Driver.assigned_port <= 8999)
    )
    max_port = result.scalar()
    if max_port is None:
        return 8901
    return max_port + 1 if max_port < 8999 else None


async def create_user(db: AsyncSession, user_create: UserCreate) -> User:
    """Create a new user and assign a port."""
    port = await get_next_free_user_port(db)
    db_user = User(name=user_create.name, user_port=port)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def create_driver(db: AsyncSession, driver_create: DriverCreate) -> Driver:
    """Create a new driver and assign a port."""
    port = await get_next_free_driver_port(db)
    db_driver = Driver(name=driver_create.name, phone=driver_create.phone, assigned_port=port)
    db.add(db_driver)
    await db.commit()
    await db.refresh(db_driver)
    return db_driver


async def list_all_users(db: AsyncSession):
    """List all users."""
    result = await db.execute(select(User))
    return result.scalars().all()


async def list_all_drivers(db: AsyncSession):
    """List all drivers."""
    result = await db.execute(select(Driver))
    return result.scalars().all()


async def get_driver_by_phone(db: AsyncSession, phone: str):
    """Get driver by phone number."""
    result = await db.execute(select(Driver).where(Driver.phone == phone))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int):
    """Get user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_driver_by_id(db: AsyncSession, driver_id: int):
    """Get driver by ID."""
    result = await db.execute(select(Driver).where(Driver.id == driver_id))
    return result.scalar_one_or_none()


async def create_ride(db: AsyncSession, ride_create: RideCreate) -> RideRequest:
    """Create a new ride request."""
    # Calculate premium fee if Wait & Return
    premium_fee = 50.0 if ride_create.is_wait_return else 0.0
    
    db_ride = RideRequest(
        user_id=ride_create.user_id,
        user_port=ride_create.user_port,
        source=ride_create.source,
        destination=ride_create.destination,
        status=RideStatus.PENDING,
        is_wait_return=ride_create.is_wait_return,
        wait_time_requested=ride_create.wait_time_requested,
        premium_fee=premium_fee
    )
    db.add(db_ride)
    await db.commit()
    await db.refresh(db_ride)
    return db_ride


async def list_pending_rides(db: AsyncSession):
    """List all pending rides."""
    result = await db.execute(select(RideRequest).where(RideRequest.status == RideStatus.PENDING))
    return result.scalars().all()


async def list_all_rides(db: AsyncSession):
    """List all rides."""
    result = await db.execute(select(RideRequest).order_by(RideRequest.id.desc()))
    return result.scalars().all()


async def get_ride_by_id(db: AsyncSession, ride_id: int):
    """Get ride by ID."""
    result = await db.execute(select(RideRequest).where(RideRequest.id == ride_id))
    return result.scalar_one_or_none()


async def get_rides_for_user(db: AsyncSession, user_id: int):
    """Get all rides for a specific user."""
    result = await db.execute(select(RideRequest).where(RideRequest.user_id == user_id).order_by(RideRequest.id.desc()))
    return result.scalars().all()


async def atomic_assign_ride(db: AsyncSession, ride_id: int, driver_id: int, driver_port: int) -> bool:
    """Atomically assign a ride to a driver. Returns True if successful.
    Prevents assigning multiple rides to the same driver.
    """
    # First check if driver already has an active ride
    existing = await db.execute(
        select(RideRequest).where(
            RideRequest.assigned_driver_id == driver_id
        ).where(
            RideRequest.status.in_([RideStatus.ASSIGNED, RideStatus.ACCEPTED])
        )
    )
    if existing.scalar_one_or_none():
        return False  # Driver already has an active ride
    
    stmt = (
        update(RideRequest)
        .where(RideRequest.id == ride_id)
        .where(RideRequest.status == RideStatus.PENDING)
        .values(
            assigned_driver_id=driver_id,
            assigned_driver_port=driver_port,
            status=RideStatus.ASSIGNED,
            updated_at=func.now()
        )
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


async def accept_ride(db: AsyncSession, ride_id: int) -> bool:
    """Accept an assigned ride (change status to ACCEPTED)."""
    stmt = (
        update(RideRequest)
        .where(RideRequest.id == ride_id)
        .where(RideRequest.status == RideStatus.ASSIGNED)
        .values(status=RideStatus.ACCEPTED, updated_at=func.now())
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


async def complete_ride(db: AsyncSession, ride_id: int) -> bool:
    """Complete a ride."""
    stmt = (
        update(RideRequest)
        .where(RideRequest.id == ride_id)
        .values(status=RideStatus.COMPLETED, completed_at=func.now(), updated_at=func.now())
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


async def get_driver_current_ride(db: AsyncSession, driver_id: int):
    """Get current (assigned or accepted) ride for a driver."""
    result = await db.execute(
        select(RideRequest).where(
            RideRequest.assigned_driver_id == driver_id
        ).where(
            RideRequest.status.in_([RideStatus.ASSIGNED, RideStatus.ACCEPTED, RideStatus.IN_PROGRESS, RideStatus.WAITING, RideStatus.RETURNING])
        ).order_by(RideRequest.id.desc())
    )
    return result.scalar_one_or_none()


async def get_driver_all_active_rides(db: AsyncSession, driver_id: int):
    """Get all active rides assigned to a driver (for cleanup/display)."""
    result = await db.execute(
        select(RideRequest).where(
            RideRequest.assigned_driver_id == driver_id
        ).where(
            RideRequest.status.in_([RideStatus.ASSIGNED, RideStatus.ACCEPTED, RideStatus.IN_PROGRESS, RideStatus.WAITING, RideStatus.RETURNING])
        ).order_by(RideRequest.id.desc())
    )
    return result.scalars().all()


async def get_user_active_rides(db: AsyncSession, user_id: int):
    """Get all active (not completed) rides for a user."""
    result = await db.execute(
        select(RideRequest).where(
            RideRequest.user_id == user_id
        ).where(
            RideRequest.status.in_([RideStatus.PENDING, RideStatus.ASSIGNED, RideStatus.ACCEPTED, RideStatus.IN_PROGRESS, RideStatus.WAITING, RideStatus.RETURNING])
        )
    )
    return result.scalars().all()


# ============== WAIT & RETURN OPERATIONS ==============

async def start_ride(db: AsyncSession, ride_id: int) -> bool:
    """Start a ride (driver picked up user, heading to destination)."""
    ride = await get_ride_by_id(db, ride_id)
    if not ride:
        return False
    
    # Calculate base fare (₹50 base fare in Indian Rupees)
    base_fare = 50.0
    
    stmt = (
        update(RideRequest)
        .where(RideRequest.id == ride_id)
        .where(RideRequest.status == RideStatus.ACCEPTED)
        .values(
            status=RideStatus.IN_PROGRESS,
            base_fare=base_fare,
            updated_at=func.now()
        )
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


async def arrive_at_destination(db: AsyncSession, ride_id: int) -> bool:
    """Driver arrived at destination. For Wait & Return rides, this starts waiting."""
    ride = await get_ride_by_id(db, ride_id)
    if not ride:
        return False
    
    if ride.is_wait_return:
        # Start waiting mode
        stmt = (
            update(RideRequest)
            .where(RideRequest.id == ride_id)
            .where(RideRequest.status == RideStatus.IN_PROGRESS)
            .values(
                status=RideStatus.WAITING,
                arrived_at=func.now(),
                wait_started_at=func.now(),
                updated_at=func.now()
            )
        )
    else:
        # Regular ride - complete it
        total = ride.base_fare
        stmt = (
            update(RideRequest)
            .where(RideRequest.id == ride_id)
            .where(RideRequest.status == RideStatus.IN_PROGRESS)
            .values(
                status=RideStatus.COMPLETED,
                arrived_at=func.now(),
                total_fare=total,
                completed_at=func.now(),
                updated_at=func.now()
            )
        )
    
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


async def start_return_trip(db: AsyncSession, ride_id: int) -> bool:
    """Start the return trip for Wait & Return rides."""
    ride = await get_ride_by_id(db, ride_id)
    if not ride or not ride.is_wait_return:
        return False
    
    # Calculate waiting charge (₹2 per minute waited)
    waiting_minutes = 0
    if ride.wait_started_at:
        from datetime import datetime
        now = datetime.now()  # Use local time since db stores local time
        # Make sure wait_started_at is timezone naive for comparison
        wait_start = ride.wait_started_at.replace(tzinfo=None) if ride.wait_started_at.tzinfo else ride.wait_started_at
        waiting_minutes = max(0, (now - wait_start).total_seconds() / 60)  # Ensure non-negative
    
    waiting_charge = round(waiting_minutes * 2.0, 2)  # ₹2 per minute
    return_fare = ride.base_fare  # Same as outbound fare
    
    stmt = (
        update(RideRequest)
        .where(RideRequest.id == ride_id)
        .where(RideRequest.status == RideStatus.WAITING)
        .values(
            status=RideStatus.RETURNING,
            return_started_at=func.now(),
            waiting_charge=waiting_charge,
            return_fare=return_fare,
            updated_at=func.now()
        )
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


async def complete_wait_return_ride(db: AsyncSession, ride_id: int) -> bool:
    """Complete a Wait & Return ride with final billing."""
    ride = await get_ride_by_id(db, ride_id)
    if not ride:
        return False
    
    # Calculate total fare
    total_fare = ride.base_fare + ride.waiting_charge + ride.return_fare + ride.premium_fee
    
    stmt = (
        update(RideRequest)
        .where(RideRequest.id == ride_id)
        .where(RideRequest.status == RideStatus.RETURNING)
        .values(
            status=RideStatus.COMPLETED,
            total_fare=total_fare,
            completed_at=func.now(),
            updated_at=func.now()
        )
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0
