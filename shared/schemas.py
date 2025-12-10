from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    name: str


class UserOut(BaseModel):
    id: int
    name: str
    user_port: int
    created_at: datetime

    class Config:
        from_attributes = True


class DriverCreate(BaseModel):
    name: str
    phone: str


class DriverOut(BaseModel):
    id: int
    name: str
    phone: str
    assigned_port: int
    created_at: datetime

    class Config:
        from_attributes = True


class RideCreate(BaseModel):
    user_id: int
    user_port: int
    source: str
    destination: str
    is_wait_return: bool = False
    wait_time_requested: Optional[int] = None  # 15, 30, 45, or 60 minutes


class RideOut(BaseModel):
    id: int
    user_id: int
    user_port: int
    source: str
    destination: str
    status: str
    assigned_driver_id: Optional[int] = None
    assigned_driver_port: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    # Wait & Return fields
    is_wait_return: bool = False
    wait_time_requested: Optional[int] = None
    arrived_at: Optional[datetime] = None
    wait_started_at: Optional[datetime] = None
    return_started_at: Optional[datetime] = None
    
    # Billing fields
    base_fare: float = 0.0
    waiting_charge: float = 0.0
    return_fare: float = 0.0
    premium_fee: float = 0.0
    total_fare: float = 0.0

    class Config:
        from_attributes = True
