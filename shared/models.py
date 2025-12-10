from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from shared.database import Base


# Ride status constants (using strings for database compatibility)
class RideStatus:
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    ACCEPTED = "ACCEPTED"
    IN_PROGRESS = "IN_PROGRESS"      # Driver picked up user, going to destination
    WAITING = "WAITING"               # Wait & Return: Driver waiting at destination
    RETURNING = "RETURNING"           # Wait & Return: Return trip in progress
    COMPLETED = "COMPLETED"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    user_port = Column(Integer, unique=True, index=True)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    rides = relationship("RideRequest", back_populates="user")


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    phone = Column(String, unique=True, index=True)
    assigned_port = Column(Integer, unique=True, index=True)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    rides = relationship("RideRequest", back_populates="driver")


class RideRequest(Base):
    __tablename__ = "ride_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    user_port = Column(Integer, index=True)
    source = Column(String)
    destination = Column(String)
    status = Column(String, default=RideStatus.PENDING, index=True)
    assigned_driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=True, index=True)
    assigned_driver_port = Column(Integer, nullable=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    # Wait & Return Feature Fields
    is_wait_return = Column(Boolean, default=False)           # Is this a Wait & Return ride?
    wait_time_requested = Column(Integer, nullable=True)      # Requested wait time in minutes (15/30/45/60)
    arrived_at = Column(DateTime, nullable=True)              # When driver arrived at destination
    wait_started_at = Column(DateTime, nullable=True)         # When waiting period started
    return_started_at = Column(DateTime, nullable=True)       # When return trip started
    
    # Billing fields (in currency units)
    base_fare = Column(Float, default=0.0)                    # Base fare for outbound trip
    waiting_charge = Column(Float, default=0.0)               # Charge for waiting time
    return_fare = Column(Float, default=0.0)                  # Fare for return trip
    premium_fee = Column(Float, default=0.0)                  # Premium fee for Wait & Return service
    total_fare = Column(Float, default=0.0)                   # Total bill

    # Relationships
    user = relationship("User", back_populates="rides")
    driver = relationship("Driver", back_populates="rides")
