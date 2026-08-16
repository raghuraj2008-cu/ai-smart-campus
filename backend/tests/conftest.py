import sys
from pathlib import Path

# Ensure project root is in python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel

from app.core.cache import close_redis
from app.core.config import settings
from app.core.database import get_session
from app.main import app

engine = create_async_engine(settings.DATABASE_URL, echo=False, poolclass=NullPool)
TestingSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Initializes a clean database schema once for the test session."""
    async with engine.begin() as conn:
        await conn.execute(text('DROP TABLE IF EXISTS "complaint" CASCADE;'))
        await conn.execute(text('DROP TABLE IF EXISTS "user" CASCADE;'))
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.execute(text('DROP TABLE IF EXISTS "complaint" CASCADE;'))
        await conn.execute(text('DROP TABLE IF EXISTS "user" CASCADE;'))
    await close_redis()


@pytest_asyncio.fixture(autouse=True)
async def clean_redis_per_test():
    """Ensures Redis connection pool is cleanly recycled per test loop."""
    yield
    await close_redis()


@pytest_asyncio.fixture
async def async_client() -> AsyncClient:
    """Provides an async HTTP client with isolated database sessions."""

    async def override_get_session():
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()