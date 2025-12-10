"""
Instance Recovery Module
Handles restart/recovery of user and driver instances after server reboot
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from shared.crud import list_all_users, list_all_drivers
from shared.process_manager import spawn_user_instance, spawn_driver_instance
import logging

logger = logging.getLogger(__name__)


async def spawn_all_user_instances(db: AsyncSession):
    """
    Spawn instances for all registered users.
    Called on admin app startup to recover user portals.
    """
    try:
        users = await list_all_users(db)
        if not users:
            logger.info("No users to recover")
            return
        
        logger.info(f"Spawning instances for {len(users)} users...")
        
        for user in users:
            try:
                logger.info(f"Spawning user instance: User #{user.id} on port {user.user_port}")
                spawn_user_instance(user.id, user.user_port)
                # Space out spawning to avoid overwhelming system
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"Failed to spawn user #{user.id}: {e}")
                continue
        
        logger.info(f"User instance recovery complete")
        
    except Exception as e:
        logger.error(f"Error in spawn_all_user_instances: {e}")


async def spawn_all_driver_instances(db: AsyncSession):
    """
    Spawn instances for all registered drivers.
    Called on admin app startup to recover driver portals.
    """
    try:
        drivers = await list_all_drivers(db)
        if not drivers:
            logger.info("No drivers to recover")
            return
        
        logger.info(f"Spawning instances for {len(drivers)} drivers...")
        
        for driver in drivers:
            try:
                logger.info(f"Spawning driver instance: Driver #{driver.id} on port {driver.assigned_port}")
                spawn_driver_instance(driver.id, driver.assigned_port)
                # Space out spawning to avoid overwhelming system
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"Failed to spawn driver #{driver.id}: {e}")
                continue
        
        logger.info(f"Driver instance recovery complete")
        
    except Exception as e:
        logger.error(f"Error in spawn_all_driver_instances: {e}")
