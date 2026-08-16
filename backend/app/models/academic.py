from typing import Optional
from sqlmodel import SQLModel, Field

class AcademicCourse(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(unique=True, index=True)
    name: str
    department: str
    credits: int = Field(default=3)
    faculty_id: Optional[int] = Field(default=None, foreign_key="user.id")

class ClassSchedule(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    course_id: int = Field(foreign_key="academiccourse.id")
    room_number: str
    day_of_week: str
    start_time: str
    end_time: str