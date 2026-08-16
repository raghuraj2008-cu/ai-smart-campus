from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr
from app.models.domain import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: Optional[UserRole] = UserRole.STUDENT
    uid: Optional[str] = None
    university_code: Optional[str] = None
    department: Optional[str] = None


class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    uid: Optional[str] = None
    university_code: Optional[str] = None
    department: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenResponse(Token):
    pass