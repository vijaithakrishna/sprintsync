import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.config import settings

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_ai.db"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = sessionmaker(
    bind=test_engine, class_=AsyncSession, expire_on_commit=False
)


async def override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_ai_suggest_stub():
    # Force stub mode
    settings.AI_MODE = "stub"

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Register + login
        await client.post("/auth/register", json={
            "email": "aiuser@example.com",
            "password": "aipass123"
        })
        login_res = await client.post("/auth/login", json={
            "email": "aiuser@example.com",
            "password": "aipass123"
        })
        token = login_res.json()["access_token"]

        # Hit /ai/suggest
        response = await client.post(
            "/ai/suggest",
            json={"title": "Build login page"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    data = response.json()
    assert "suggestion" in data
    assert len(data["suggestion"]) > 0
    assert data["model"] == "stub"