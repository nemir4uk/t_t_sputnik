from contextlib import contextmanager

from src.infrastructure.config import settings
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


ASYNC_DB_URL = (
    f"postgresql+asyncpg://{settings.pg_user}:{settings.pg_pass}"
    f"@{settings.pg_host}:{settings.pg_port}/{settings.pg_db}"
)

SYNC_DB_URL = ASYNC_DB_URL.replace(
    "postgresql+asyncpg",
    "postgresql"
)

sync_engine = create_engine(
    SYNC_DB_URL,
    pool_pre_ping=True,
)

SyncSession = sessionmaker(
    bind=sync_engine,
    autoflush=False,
    autocommit=False,
)

async_engine = create_async_engine(
    ASYNC_DB_URL,
    echo=False,
    pool_size=10,
    max_overflow=20
)

AsyncSessionMain = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_async_session():
    async with AsyncSessionMain() as async_session:
        yield async_session


@contextmanager
def get_sync_session():
    session = SyncSession()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
