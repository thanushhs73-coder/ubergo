from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class RideStatus(str, Enum):
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    ACCEPTED = "ACCEPTED"
    COMPLETED = "COMPLETED"

# User Schemas
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    user_port: int = Field(..., gt=0, lt=65536)

class UserResponse(BaseModel):
    id: int
    name: str
    user_port: int
    created_at: datetime

    class Config:
        from_attributes = True

# Driver Schemas
class DriverCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    phone: str = Field(..., min_length=10, max_length=20)
    assigned_port: int = Field(..., gt=0, lt=65536)

class DriverResponse(BaseModel):
    id: int
    name: str
    phone: str
    assigned_port: int
    created_at: datetime

    class Config:
        from_attributes = True

# Ride Request Schemas
class RideRequestCreate(BaseModel):
    user_id: int
    user_port: int
    source: str = Field(..., min_length=1, max_length=255)
    destination: str = Field(..., min_length=1, max_length=255)

class RideRequestUpdate(BaseModel):
    status: Optional[RideStatus] = None
    assigned_driver_id: Optional[int] = None
    assigned_driver_port: Optional[int] = None
    completed_at: Optional[datetime] = None

class RideRequestResponse(BaseModel):
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

    class Config:
        from_attributes = True

class RideRequestListResponse(BaseModel):
    total: int
    rides: list[RideRequestResponse]
