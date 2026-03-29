"""
Analytics Router
Provides dashboard KPIs and fraud trend data.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..core.security import get_current_user
from ..schemas.fraud import DashboardKPIs, AnalyticsTrends
from ..services.fraud_service import get_dashboard_kpis
from ..services.ml_client import get_model_info

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard", response_model=DashboardKPIs)
async def dashboard_kpis(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get dashboard KPI summary metrics."""
    kpis = await get_dashboard_kpis(db)
    return DashboardKPIs(**kpis)


@router.get("/trends", response_model=AnalyticsTrends)
async def fraud_trends(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get fraud trend data for charts."""
    from sqlalchemy import select, func
    from ..models.transaction import Transaction
    import random

    # Generate sample trend data (in production, aggregate from DB)
    trends = []
    for i in range(30):
        day = f"2024-{12 if i < 20 else 1:02d}-{(i % 28) + 1:02d}"
        total = random.randint(100, 500)
        fraud = random.randint(2, 25)
        trends.append({
            "date": day,
            "total_transactions": total,
            "fraud_count": fraud,
            "avg_score": round(random.uniform(0.05, 0.4), 4),
        })

    # Risk distribution from DB
    from sqlalchemy import case
    high = await db.scalar(
        select(func.count(Transaction.id)).where(Transaction.risk_category == "HIGH")
    ) or 0
    medium = await db.scalar(
        select(func.count(Transaction.id)).where(Transaction.risk_category == "MEDIUM")
    ) or 0
    low = await db.scalar(
        select(func.count(Transaction.id)).where(Transaction.risk_category == "LOW")
    ) or 0

    # Model performance from ML service
    model_info = await get_model_info() or {
        "model_name": "unknown",
        "version": "unknown",
        "metrics": {},
    }

    return AnalyticsTrends(
        trends=trends,
        risk_distribution={"HIGH": high, "MEDIUM": medium, "LOW": low},
        model_performance=model_info,
    )
