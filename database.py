from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

# Database connection string
DATABASE_URL = "postgresql+psycopg2://postgres:#2005REnu@localhost:5432/ubergo"

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()

# Enum for ride status
class RideStatus(str, enum.Enum):
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    ACCEPTED = "ACCEPTED"
    COMPLETED = "COMPLETED"

# Database Models
class Driver(Base):
    __tablename__ = "drivers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    assigned_port = Column(Integer, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    rides = relationship("RideRequest", back_populates="assigned_driver")
    
    def __repr__(self):
        return f"<Driver(id={self.id}, name={self.name}, phone={self.phone})>"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    user_port = Column(Integer, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    rides = relationship("RideRequest", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, name={self.name})>"

class RideRequest(Base):
    __tablename__ = "ride_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    user_port = Column(Integer, nullable=False)
    source = Column(String(255), nullable=False)
    destination = Column(String(255), nullable=False)
    status = Column(String(20), default=RideStatus.PENDING, nullable=False, index=True)
    assigned_driver_id = Column(Integer, ForeignKey("drivers.id", ondelete="SET NULL"), nullable=True, index=True)
    assigned_driver_port = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="rides")
    assigned_driver = relationship("Driver", back_populates="rides")
    
    def __repr__(self):
        return f"<RideRequest(id={self.id}, user_id={self.user_id}, status={self.status})>"

# Dependency function for getting database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
