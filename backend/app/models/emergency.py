from typing import Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field

class EmergencyAlert(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    location: str
    description: str
    severity: str = Field(default="CRITICAL")
    reported_by: int = Field(foreign_key="user.id")
    is_resolved: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))