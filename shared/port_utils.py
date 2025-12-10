import socket
from sqlalchemy.ext.asyncio import AsyncSession
from shared.models import User, Driver


async def is_port_free(port: int) -> bool:
    """Check if a port is free on the OS level."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return True
        except OSError:
            return False


async def get_free_user_port(db: AsyncSession) -> int:
    """Get the next free user port (8002-8899) that is not in DB."""
    from sqlalchemy import select, func
    
    # Get max port from DB
    result = await db.execute(
        select(func.max(User.user_port)).where(User.user_port >= 8002)
    )
    max_port = result.scalar()
    
    if max_port is None:
        start_port = 8002
    else:
        start_port = max_port + 1
    
    # Find first free port
    for port in range(start_port, 8900):
        if await is_port_free(port):
            return port
    
    return None


async def get_free_driver_port(db: AsyncSession) -> int:
    """Get the next free driver port (8901-8999) that is not in DB."""
    from sqlalchemy import select, func
    
    # Get max port from DB
    result = await db.execute(
        select(func.max(Driver.assigned_port)).where(Driver.assigned_port >= 8901)
    )
    max_port = result.scalar()
    
    if max_port is None:
        start_port = 8901
    else:
        start_port = max_port + 1
    
    # Find first free port
    for port in range(start_port, 9000):
        if await is_port_free(port):
            return port
    
    return None
