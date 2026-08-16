import asyncio
from datetime import datetime, timezone
import bcrypt
from sqlmodel import select
from app.core.database import get_session
from app.models.domain import User, UserRole


def hash_password(password: str) -> str:
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def utc_now_naive() -> datetime:
    """Returns offset-naive UTC datetime for PostgreSQL compatibility."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


async def init_db():
    async for db in get_session():
        now = utc_now_naive()

        # Check Admin
        admin_result = await db.execute(
            select(User).where(User.email == "admin@campus.edu")
        )
        admin = admin_result.scalars().first()

        if not admin:
            admin_user = User(
                email="admin@campus.edu",
                hashed_password=hash_password("admin123"),
                full_name="System Admin",
                role=UserRole.ADMIN,
                is_active=True,
                created_at=now,
                updated_at=now,
            )
            db.add(admin_user)
            await db.commit()
            print("--> Created initial Admin user (admin@campus.edu / admin123)")

        # Check Student
        student_result = await db.execute(
            select(User).where(User.email == "student@campus.edu")
        )
        student = student_result.scalars().first()

        if not student:
            student_user = User(
                email="student@campus.edu",
                hashed_password=hash_password("student123"),
                full_name="Jane Doe",
                role=UserRole.STUDENT,
                is_active=True,
                created_at=now,
                updated_at=now,
            )
            db.add(student_user)
            await db.commit()
            print("--> Created initial Student user (student@campus.edu / student123)")

        print("Database initialization complete.")
        break


if __name__ == "__main__":
    asyncio.run(init_db())