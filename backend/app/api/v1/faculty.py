from fastapi import APIRouter, Depends
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/faculty", tags=["Faculty"])

@router.get("/dashboard")
async def faculty_dashboard(current_user: User = Depends(get_current_user)):
    return {
        "faculty_name": current_user.full_name,
        "department": current_user.department,
        "assigned_classes": [],
        "pending_notices": []
    }