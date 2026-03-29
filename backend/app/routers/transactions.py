"""
Transactions Router
Handles transaction ingestion, listing, and detail view.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Optional

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.transaction import Transaction
from ..schemas.transaction import (
    TransactionCreate,
    TransactionResponse,
    TransactionListResponse,
    TransactionDetail,
)
from ..services.fraud_service import process_transaction

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction: TransactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Ingest a new transaction and run fraud detection.
    Automatically triggers ML prediction and stores results.
    """
    tx_data = transaction.model_dump()
    result = await process_transaction(db, tx_data)
    return result


@router.get("/", response_model=TransactionListResponse)
async def list_transactions(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    risk_category: Optional[str] = Query(None, pattern="^(LOW|MEDIUM|HIGH)$"),
    is_fraud: Optional[bool] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List transactions with filtering and pagination."""
    query = select(Transaction)

    # Apply filters
    if risk_category:
        query = query.where(Transaction.risk_category == risk_category)
    if is_fraud is not None:
        query = query.where(Transaction.is_fraud == is_fraud)
    if min_amount is not None:
        query = query.where(Transaction.amount >= min_amount)
    if max_amount is not None:
        query = query.where(Transaction.amount <= max_amount)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Paginate
    query = query.order_by(desc(Transaction.created_at))
    query = query.offset((page - 1) * per_page).limit(per_page)

    result = await db.execute(query)
    transactions = result.scalars().all()

    return TransactionListResponse(
        transactions=[TransactionResponse.model_validate(t) for t in transactions],
        total=total or 0,
        page=page,
        per_page=per_page,
    )


@router.get("/{transaction_id}", response_model=TransactionDetail)
async def get_transaction(
    transaction_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get transaction details by transaction UUID."""
    result = await db.execute(
        select(Transaction).where(Transaction.transaction_id == transaction_id)
    )
    transaction = result.scalar_one_or_none()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return TransactionDetail.model_validate(transaction)
