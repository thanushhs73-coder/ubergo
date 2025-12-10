import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:%232005REnu@localhost:5432/ubergo")

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# Create async session factory
async_session = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, future=True
)

# Base for declarative models
Base = declarative_base()


async def get_db():
    """Dependency to get DB session in FastAPI."""
    async with async_session() as session:
        yield session


async def init_db():
    """Initialize database tables. Create database if needed."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"Warning: Could not initialize database: {e}")
        print("Make sure PostgreSQL is running and database 'ubergo' exists.")
        pass
