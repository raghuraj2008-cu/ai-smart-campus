from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from sqlmodel import Field, SQLModel


def utc_now_naive() -> datetime:
    """Returns current UTC time as an offset-naive datetime for PostgreSQL compatibility."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class UserRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    FACULTY = "FACULTY"
    STUDENT = "STUDENT"
    SECURITY = "SECURITY"


class PriorityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class User(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    full_name: str = Field(nullable=False)
    role: UserRole = Field(default=UserRole.STUDENT)

    uid: Optional[str] = Field(default=None, unique=True)
    university_code: Optional[str] = Field(default=None, index=True)
    department: Optional[str] = Field(default=None)

    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=utc_now_naive)
    updated_at: datetime = Field(default_factory=utc_now_naive)


class Complaint(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(nullable=False)
    description: str = Field(nullable=False)
    location: str = Field(nullable=False)
    category: Optional[str] = Field(default="Unclassified")
    priority: PriorityLevel = Field(default=PriorityLevel.MEDIUM)
    department: Optional[str] = Field(default="General Maintenance")
    status: str = Field(default="Assigned")
    student_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=utc_now_naive)