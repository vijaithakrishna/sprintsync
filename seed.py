import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal, engine, Base
from app.models.user import User
from app.models.task import Task
from app.routers.auth import hash_password


async def seed():
    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Check if already seeded
        from sqlalchemy import select
        result = await db.execute(select(User).limit(1))
        if result.scalar_one_or_none():
            print("✅ Database already seeded, skipping.")
            return

        print("🌱 Seeding database...")

        # Create admin user
        admin = User(
            email="admin@sprintsync.dev",
            hashed_password=hash_password("admin123"),
            is_admin=True,
        )

        # Create regular users
        alice = User(
            email="alice@sprintsync.dev",
            hashed_password=hash_password("alice123"),
        )
        bob = User(
            email="bob@sprintsync.dev",
            hashed_password=hash_password("bob123"),
        )

        db.add_all([admin, alice, bob])
        await db.flush()

        # Create tasks for alice
        tasks = [
            Task(
                title="Build login page",
                description="Implement secure login with email and password.",
                status="todo",
                total_minutes=0,
                owner_id=alice.id,
            ),
            Task(
                title="Write API docs",
                description="Document all endpoints using Swagger annotations.",
                status="in_progress",
                total_minutes=45,
                owner_id=alice.id,
            ),
            Task(
                title="Set up CI pipeline",
                description="Configure GitHub Actions for automated testing.",
                status="done",
                total_minutes=120,
                owner_id=alice.id,
            ),
            Task(
                title="Deploy to staging",
                description="Deploy the app to Render free tier.",
                status="todo",
                total_minutes=0,
                owner_id=bob.id,
            ),
            Task(
                title="Fix auth bug",
                description="Resolve JWT expiry edge case on mobile clients.",
                status="in_progress",
                total_minutes=30,
                owner_id=bob.id,
            ),
        ]

        db.add_all(tasks)
        await db.commit()
        print("✅ Seeding complete!")
        print("   admin@sprintsync.dev  /  admin123")
        print("   alice@sprintsync.dev  /  alice123")
        print("   bob@sprintsync.dev    /  bob123")


if __name__ == "__main__":
    asyncio.run(seed())