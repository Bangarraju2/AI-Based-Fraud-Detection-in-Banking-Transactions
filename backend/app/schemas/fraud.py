"""Fraud Schemas — Pydantic Models"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class FraudAlertResponse(BaseModel):
    id: int
    transaction_id: int
    prediction_score: float
    risk_category: str
    model_version: Optional[str] = None
    review_status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class FraudLogResponse(BaseModel):
    id: int
    transaction_id: int
    prediction_score: float
    risk_category: str
    model_version: Optional[str] = None
    model_name: Optional[str] = None
    reviewed_by_id: Optional[int] = None
    review_status: str
    review_notes: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class FraudLogListResponse(BaseModel):
    logs: List[FraudLogResponse]
    total: int
    page: int
    per_page: int


class ReviewRequest(BaseModel):
    review_status: str = Field(..., pattern="^(confirmed_fraud|false_positive)$")
    review_notes: Optional[str] = None


class DashboardKPIs(BaseModel):
    total_transactions: int
    total_fraud_detected: int
    fraud_rate: float
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    pending_reviews: int
    avg_fraud_score: float
    transactions_today: int
    fraud_today: int


class FraudTrend(BaseModel):
    date: str
    total_transactions: int
    fraud_count: int
    avg_score: float


class AnalyticsTrends(BaseModel):
    trends: List[FraudTrend]
    risk_distribution: Dict[str, int]
    model_performance: Dict[str, Any]
