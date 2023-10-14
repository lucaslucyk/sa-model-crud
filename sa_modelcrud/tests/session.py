from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker
)
from .config import DB_URI, DB_URI_ASYNC


# async sqlite session
async_engine: AsyncEngine = create_async_engine(
    DB_URI_ASYNC,
    future=True,
    connect_args={"check_same_thread": False}
)

AsyncSessionLocal: AsyncSession = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# sqlite session
engine = create_engine(
    DB_URI, future=True, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(expire_on_commit=False, bind=engine)

