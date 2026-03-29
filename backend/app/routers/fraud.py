"""
Fraud Router
Handles fraud alerts, logs, and manual reviews.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from datetime import datetime, timezone

from ..core.database import get_db
from ..core.security import get_current_user, require_role
from ..models.fraud_log import FraudLog
from ..models.transaction import Transaction
from ..schemas.fraud import (
    FraudAlertResponse,
    FraudLogResponse,
    FraudLogListResponse,
    ReviewRequest,
)

router = APIRouter(prefix="/fraud", tags=["Fraud Detection"])


@router.get("/alerts", response_model=list[FraudAlertResponse])
async def get_fraud_alerts(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get recent fraud alerts (HIGH and MEDIUM risk)."""
    query = (
        select(FraudLog)
        .where(FraudLog.risk_category.in_(["HIGH", "MEDIUM"]))
        .order_by(desc(FraudLog.created_at))
        .limit(limit)
    )
    result = await db.execute(query)
    logs = result.scalars().all()
    return [FraudAlertResponse.model_validate(log) for log in logs]


@router.get("/logs", response_model=FraudLogListResponse)
async def get_fraud_logs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    review_status: str = Query(None),
    risk_category: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get paginated fraud logs with optional filters."""
    query = select(FraudLog)

    if review_status:
        query = query.where(FraudLog.review_status == review_status)
    if risk_category:
        query = query.where(FraudLog.risk_category == risk_category)

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    query = query.order_by(desc(FraudLog.created_at))
    query = query.offset((page - 1) * per_page).limit(per_page)

    result = await db.execute(query)
    logs = result.scalars().all()

    return FraudLogListResponse(
        logs=[FraudLogResponse.model_validate(log) for log in logs],
        total=total or 0,
        page=page,
        per_page=per_page,
    )


@router.put("/review/{log_id}")
async def review_fraud_log(
    log_id: int,
    review: ReviewRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role(["admin", "analyst"])),
):
    """
    Manual review of a fraud log entry.
    Updates review status and adds reviewer notes (audit trail).
    """
    fraud_log = await db.get(FraudLog, log_id)
    if not fraud_log:
        raise HTTPException(status_code=404, detail="Fraud log not found")

    fraud_log.review_status = review.review_status
    fraud_log.review_notes = review.review_notes
    fraud_log.reviewed_by_id = int(current_user["sub"])
    fraud_log.reviewed_at = datetime.now(timezone.utc)

    await db.commit()

    return {
        "message": "Review submitted successfully",
        "log_id": log_id,
        "review_status": review.review_status,
    }
