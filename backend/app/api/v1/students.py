from fastapi import APIRouter, Depends
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/students", tags=["Students"])

@router.get("/profile")
async def student_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "uid": current_user.uid,
        "email": current_user.email,
        "department": current_user.department,
        "role": current_user.role
    }