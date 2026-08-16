from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.domain import PriorityLevel


class ComplaintCreate(BaseModel):
    title: str
    description: str
    location: str
    category: Optional[str] = "Unclassified"
    priority: Optional[PriorityLevel] = PriorityLevel.MEDIUM
    department: Optional[str] = "General Maintenance"


class ComplaintUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[PriorityLevel] = None
    department: Optional[str] = None
    status: Optional[str] = None


class ComplaintStatusUpdate(BaseModel):
    status: str
    model_config = ConfigDict(from_attributes=True)


class ComplaintResponse(BaseModel):
    id: int
    title: str
    description: str
    location: str
    category: Optional[str]
    priority: PriorityLevel
    department: Optional[str]
    status: str
    student_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)