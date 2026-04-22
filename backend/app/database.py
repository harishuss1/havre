"""
database.py — SQLAlchemy async engine, session factory, and Base model.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from .config import settings

# Async engine — psycopg3 driver
engine = create_async_engine(
    settings.database_url,
    echo=settings.is_dev,   # logs SQL in development
    pool_pre_ping=True,     # reconnects if DB went away
    pool_size=5,
    max_overflow=10,
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class all models inherit from
class Base(DeclarativeBase):
    pass


async def get_db():
    """
    FastAPI dependency — yields a DB session and closes it after the request.

    Usage in a router:
        async def my_route(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()