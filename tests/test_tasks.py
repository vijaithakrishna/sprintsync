import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_tasks.db"
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


async def get_token(client: AsyncClient) -> str:
    await client.post("/auth/register", json={
        "email": "taskuser@example.com",
        "password": "pass123"
    })
    res = await client.post("/auth/login", json={
        "email": "taskuser@example.com",
        "password": "pass123"
    })
    return res.json()["access_token"]


@pytest.mark.asyncio
async def test_create_task_happy_path():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        token = await get_token(client)
        response = await client.post(
            "/tasks/",
            json={"title": "Test task", "description": "A test", "status": "todo"},
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test task"
    assert data["status"] == "todo"


@pytest.mark.asyncio
async def test_status_transition_happy_path():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        token = await get_token(client)
        # Create task
        create_res = await client.post(
            "/tasks/",
            json={"title": "Transition task", "status": "todo"},
            headers={"Authorization": f"Bearer {token}"},
        )
        task_id = create_res.json()["id"]

        # Move to in_progress
        response = await client.patch(
            f"/tasks/{task_id}/status",
            json={"status": "in_progress"},
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


@pytest.mark.asyncio
async def test_invalid_status_transition():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        token = await get_token(client)
        create_res = await client.post(
            "/tasks/",
            json={"title": "Skip task", "status": "todo"},
            headers={"Authorization": f"Bearer {token}"},
        )
        task_id = create_res.json()["id"]

        # Try skipping todo ? done (not allowed)
        response = await client.patch(
            f"/tasks/{task_id}/status",
            json={"status": "done"},
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 400