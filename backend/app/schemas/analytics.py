from typing import Dict
from pydantic import BaseModel

class CampusAnalyticsResponse(BaseModel):
    total_complaints: int
    by_status: Dict[str, int]
    by_department: Dict[str, int]
    by_priority: Dict[str, int]