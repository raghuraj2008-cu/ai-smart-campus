from enum import Enum
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field

class UserRole(str, Enum):
    STUDENT = "student"
    ADMIN = "admin"
    FACULTY = "faculty"
    STAFF = "staff"

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    full_name: str = Field(nullable=False)
    role: UserRole = Field(default=UserRole.STUDENT)
    is_active: bool = Field(default=True)
    uid: Optional[str] = Field(default=None)
    university_code: Optional[str] = Field(default=None)
    department: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))