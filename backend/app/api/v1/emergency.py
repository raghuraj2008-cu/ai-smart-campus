from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.models.emergency import EmergencyAlert
from app.models.user import User
from app.api.deps import get_current_user
from app.websocket.connection_manager import ws_manager

router = APIRouter(prefix="/emergency", tags=["Emergency"])

class EmergencyCreate(BaseModel):
    title: str
    location: str
    description: str

@router.post("/trigger", status_code=status.HTTP_201_CREATED)
async def trigger_emergency(
    payload: EmergencyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    alert = EmergencyAlert(
        title=payload.title,
        location=payload.location,
        description=payload.description,
        reported_by=current_user.id
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)

    # Broadcast emergency to security & admin roles
    broadcast_data = {
        "event": "EMERGENCY_ALERT",
        "target_role": "SECURITY",
        "data": {
            "id": alert.id,
            "title": alert.title,
            "location": alert.location,
            "severity": alert.severity
        }
    }
    await ws_manager.publish_redis_event("campus_alerts", broadcast_data)

    return {"status": "ALERT_DISPATCHED", "alert_id": alert.id}