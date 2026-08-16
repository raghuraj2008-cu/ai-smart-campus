from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_role
from app.core.database import get_session
from app.core.cache import get_cached_json, set_cached_json
from app.models.domain import Complaint, User, UserRole
from app.schemas.analytics import CampusAnalyticsResponse

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary", response_model=CampusAnalyticsResponse)
async def get_complaint_summary(
    start_date: Optional[datetime] = Query(
        None, description="Filter complaints created after this timestamp (UTC ISO format)"
    ),
    end_date: Optional[datetime] = Query(
        None, description="Filter complaints created before this timestamp (UTC ISO format)"
    ),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])),
):
    """
    Returns aggregated campus complaint statistics with optional date filtering (Admin only).
    Checks Redis cache with a dynamic key; falls back to DB aggregation and updates cache.
    """
    # 1. Dynamic Cache Key based on query params
    start_str = start_date.isoformat() if start_date else "all"
    end_str = end_date.isoformat() if end_date else "all"
    cache_key = f"campus:analytics:summary:{start_str}:{end_str}"

    cached_data = await get_cached_json(cache_key)
    if cached_data:
        return CampusAnalyticsResponse(**cached_data)

    # 2. Build Base Date Filter
    base_filter = []
    if start_date:
        base_filter.append(Complaint.created_at >= start_date)
    if end_date:
        base_filter.append(Complaint.created_at <= end_date)

    # 3. Database Aggregations with Filters
    total_query = select(func.count(Complaint.id)).where(*base_filter)
    total_result = await session.execute(total_query)
    total_complaints = total_result.scalar_one_or_none() or 0

    status_query = (
        select(Complaint.status, func.count(Complaint.id))
        .where(*base_filter)
        .group_by(Complaint.status)
    )
    status_result = await session.execute(status_query)
    by_status = {status: count for status, count in status_result.all()}

    dept_query = (
        select(
            func.coalesce(Complaint.department, "General"),
            func.count(Complaint.id),
        )
        .where(*base_filter)
        .group_by(Complaint.department)
    )
    dept_result = await session.execute(dept_query)
    by_department = {dept: count for dept, count in dept_result.all()}

    priority_query = (
        select(Complaint.priority, func.count(Complaint.id))
        .where(*base_filter)
        .group_by(Complaint.priority)
    )
    priority_result = await session.execute(priority_query)
    by_priority = {
        (p.value if hasattr(p, "value") else str(p)): count
        for p, count in priority_result.all()
    }

    response_data = CampusAnalyticsResponse(
        total_complaints=total_complaints,
        by_status=by_status,
        by_department=by_department,
        by_priority=by_priority,
    )

    # 4. Store result in Redis (TTL: 5 minutes)
    await set_cached_json(cache_key, response_data.model_dump(), expire_seconds=300)

    return response_data