import csv
import io
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
    status,
)
from fastapi.responses import StreamingResponse
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.api.v1.websockets import manager
from app.ai.llm_categorizer import analyze_complaint_llm
from app.core.cache import invalidate_cache
from app.core.database import get_session
from app.models.domain import Complaint, User, UserRole
from app.schemas.complaint import (
    ComplaintCreate,
    ComplaintResponse,
    ComplaintStatusUpdate,
)
from app.services.email import send_status_update_email

router = APIRouter(prefix="/complaints", tags=["Complaints"])

ANALYTICS_CACHE_KEY = "campus:analytics:summary"


@router.get("/", response_model=List[ComplaintResponse])
async def get_complaints(
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(50, ge=1, le=100, description="Max number of records to return"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    department: Optional[str] = Query(None, description="Filter by department"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve paginated complaints.
    Admins & Super Admins view all complaints; students view only their own.
    """
    statement = select(Complaint)

    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        statement = statement.where(Complaint.student_id == current_user.id)

    if status_filter:
        statement = statement.where(Complaint.status == status_filter)
    if department:
        statement = statement.where(Complaint.department == department)

    statement = statement.order_by(Complaint.created_at.desc()).offset(skip).limit(limit)

    result = await session.execute(statement)
    return result.scalars().all()


@router.get("/export/csv")
async def export_complaints_csv(
    start_date: Optional[datetime] = Query(None, description="Filter complaints created after (UTC)"),
    end_date: Optional[datetime] = Query(None, description="Filter complaints created before (UTC)"),
    department: Optional[str] = Query(None, description="Filter by department"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])),
):
    """
    Streams a downloadable CSV report of complaints matching filter criteria (Admin only).
    """
    filters = []
    if start_date:
        filters.append(Complaint.created_at >= start_date)
    if end_date:
        filters.append(Complaint.created_at <= end_date)
    if department:
        filters.append(Complaint.department == department)
    if status_filter:
        filters.append(Complaint.status == status_filter)

    query = select(Complaint).where(*filters).order_by(Complaint.created_at.desc())
    result = await session.execute(query)
    complaints = result.scalars().all()

    def generate_csv():
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "ID",
            "Title",
            "Category",
            "Priority",
            "Department",
            "Status",
            "Location",
            "Student ID",
            "Created At (UTC)",
        ])
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)

        for item in complaints:
            writer.writerow([
                item.id,
                item.title,
                item.category,
                item.priority.value if hasattr(item.priority, "value") else str(item.priority),
                item.department,
                item.status,
                item.location,
                item.student_id,
                item.created_at.isoformat() if item.created_at else "",
            ])
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)

    filename = f"campus_complaints_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        generate_csv(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.post("/", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
async def create_complaint(
    payload: ComplaintCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Create a new complaint, enrich with AI triage, invalidate cache, and broadcast creation."""
    # 1. Run AI analysis on the submitted title and description
    ai_insights = await analyze_complaint_llm(payload.title, payload.description)

    # 2. Extract payload fields and merge AI results + authenticated student ID
    complaint_dict = payload.model_dump()
    complaint_dict.update({
        "category": ai_insights.get("category", "Unclassified"),
        "priority": ai_insights.get("priority", "MEDIUM"),
        "department": ai_insights.get("department", "General Maintenance"),
        "student_id": current_user.id,
    })

    # 3. Save complaint to database
    complaint = Complaint(**complaint_dict)
    session.add(complaint)
    await session.commit()
    await session.refresh(complaint)

    # 4. Invalidate analytics cache
    await invalidate_cache(ANALYTICS_CACHE_KEY)

    # 5. Send real-time update to all connected clients
    await manager.broadcast({
        "event": "COMPLAINT_CREATED",
        "data": {
            "id": complaint.id,
            "title": complaint.title,
            "category": complaint.category,
            "priority": complaint.priority,
            "department": complaint.department,
            "status": complaint.status,
            "reasoning": ai_insights.get("reasoning"),
        },
    })

    return complaint


@router.patch("/{complaint_id}/status", response_model=ComplaintResponse)
async def update_complaint_status(
    complaint_id: int,
    payload: ComplaintStatusUpdate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])),
):
    """Update complaint status, invalidate cache, broadcast WS event, and send background email notification."""
    result = await session.execute(select(Complaint).where(Complaint.id == complaint_id))
    complaint = result.scalars().first()

    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found",
        )

    # 1. Update status in database
    complaint.status = payload.status
    session.add(complaint)
    await session.commit()
    await session.refresh(complaint)

    # 2. Invalidate analytics cache
    await invalidate_cache(ANALYTICS_CACHE_KEY)

    # 3. Broadcast status change event to connected clients
    await manager.broadcast({
        "event": "COMPLAINT_STATUS_UPDATED",
        "data": {
            "id": complaint.id,
            "title": complaint.title,
            "status": complaint.status,
            "department": complaint.department,
        },
    })

    # 4. Dispatch background email notification to the student
    student_res = await session.execute(select(User).where(User.id == complaint.student_id))
    student = student_res.scalars().first()

    if student and student.email:
        background_tasks.add_task(
            send_status_update_email,
            to_email=student.email,
            complaint_title=complaint.title,
            new_status=complaint.status,
            department=complaint.department or "General Maintenance",
        )

    return complaint