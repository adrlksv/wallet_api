from typing import AsyncGenerator

import pytest_asyncio

from httpx import (
    AsyncClient, 
    ASGITransport,
)

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine,
)
from sqlalchemy.pool import NullPool

from app.main import create_app
from app.db.db_helper import db_helper
from app.db.models.base import Base
from app.core.config import settings


@pytest_asyncio.fixture(scope="session")
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(
        settings.test_db_url,
        echo=False,
        poolclass=NullPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def clean_tables(test_engine: AsyncEngine):
    yield
    async with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    async with async_sessionmaker(
        bind=test_engine,
        expire_on_commit=False,
    )() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(test_engine: AsyncEngine) -> AsyncGenerator[AsyncClient, None]:
    app = create_app()
    
    async def override_session():
        async with async_sessionmaker(
            bind=test_engine,
            expire_on_commit=False,
        )() as session:
            yield session
    
    app.dependency_overrides[db_helper.session_getter] = override_session
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()
