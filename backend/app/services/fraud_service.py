"""
Fraud Detection Service
Orchestrates fraud detection: calls ML service, caches results, logs to DB.
"""

import hashlib
import json
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..models.transaction import Transaction
from ..models.fraud_log import FraudLog
from .ml_client import get_fraud_prediction
from .cache_service import cache_prediction, get_cached_prediction

logger = logging.getLogger(__name__)

# WebSocket connections for real-time alerts
active_connections = []


def _generate_transaction_hash(data: Dict[str, Any]) -> str:
    """Generate a unique hash for cache lookup."""
    key_data = json.dumps(
        {k: round(v, 4) if isinstance(v, float) else v for k, v in sorted(data.items())},
        sort_keys=True,
    )
    return hashlib.sha256(key_data.encode()).hexdigest()[:32]


async def process_transaction(
    db: AsyncSession,
    transaction_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Process a new transaction:
    1. Check cache
    2. Get ML prediction
    3. Save transaction to DB
    4. Create fraud log
    5. Broadcast alert if high risk
    """
    tx_hash = _generate_transaction_hash(transaction_data)

    # Check cache first
    cached = await get_cached_prediction(tx_hash)
    if cached:
        prediction = cached
        logger.info(f"Using cached prediction for hash {tx_hash[:8]}")
    else:
        prediction = await get_fraud_prediction(transaction_data)
        await cache_prediction(tx_hash, prediction)

    # Create Transaction record
    transaction = Transaction(
        transaction_id=str(uuid.uuid4()),
        amount=transaction_data.get("amount", 0.0),
        time=transaction_data.get("time", 0.0),
        fraud_score=prediction["fraud_probability"],
        risk_category=prediction["risk_category"],
        is_fraud=prediction["is_fraud"],
        is_flagged_for_review=prediction["requires_manual_review"],
        **{f"v{i}": transaction_data.get(f"v{i}", 0.0) for i in range(1, 29)},
    )
    db.add(transaction)
    await db.flush()

    # Create Fraud Log entry
    fraud_log = FraudLog(
        transaction_id=transaction.id,
        prediction_score=prediction["fraud_probability"],
        risk_category=prediction["risk_category"],
        model_version=prediction.get("model_version", "unknown"),
        model_name=prediction.get("model_name", "unknown"),
        review_status="pending" if prediction["requires_manual_review"] else "auto_cleared",
    )
    db.add(fraud_log)
    await db.commit()

    # Broadcast real-time alert for dashboard update
    await broadcast_alert({
        "type": "new_transaction",
        "transaction_id": transaction.transaction_id,
        "amount": transaction.amount,
        "risk_category": transaction.risk_category,
        "fraud_score": transaction.fraud_score,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    # Broadcast specialized fraud_alert if HIGH risk
    if prediction["risk_category"] == "HIGH":
        alert_data = {
            "type": "fraud_alert",
            "transaction_id": transaction.transaction_id,
            "amount": transaction.amount,
            "fraud_score": prediction["fraud_probability"],
            "risk_category": prediction["risk_category"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await broadcast_alert(alert_data)

    return {
        "transaction_id": transaction.transaction_id,
        "amount": transaction.amount,
        "fraud_score": prediction["fraud_probability"],
        "risk_category": prediction["risk_category"],
        "is_fraud": prediction["is_fraud"],
        "requires_manual_review": prediction["requires_manual_review"],
        "model_version": prediction.get("model_version"),
        "feature_importance": prediction.get("feature_importance", {}),
        "confidence": prediction.get("confidence", 0.0),
    }


async def broadcast_alert(alert_data: Dict[str, Any]):
    """Send real-time alert to all connected WebSocket clients."""
    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_json(alert_data)
        except Exception:
            disconnected.append(connection)
    for conn in disconnected:
        active_connections.remove(conn)


async def get_dashboard_kpis(db: AsyncSession) -> Dict[str, Any]:
    """Calculate dashboard KPI metrics."""
    from datetime import date

    today = datetime.now(timezone.utc).date()

    total = await db.scalar(select(func.count(Transaction.id)))
    total_fraud = await db.scalar(
        select(func.count(Transaction.id)).where(Transaction.is_fraud == True)
    )
    high_risk = await db.scalar(
        select(func.count(Transaction.id)).where(Transaction.risk_category == "HIGH")
    )
    medium_risk = await db.scalar(
        select(func.count(Transaction.id)).where(Transaction.risk_category == "MEDIUM")
    )
    low_risk = await db.scalar(
        select(func.count(Transaction.id)).where(Transaction.risk_category == "LOW")
    )
    pending = await db.scalar(
        select(func.count(FraudLog.id)).where(FraudLog.review_status == "pending")
    )
    avg_score = await db.scalar(
        select(func.avg(Transaction.fraud_score)).where(Transaction.fraud_score.isnot(None))
    )

    return {
        "total_transactions": total or 0,
        "total_fraud_detected": total_fraud or 0,
        "fraud_rate": round((total_fraud or 0) / max(total or 1, 1) * 100, 2),
        "high_risk_count": high_risk or 0,
        "medium_risk_count": medium_risk or 0,
        "low_risk_count": low_risk or 0,
        "pending_reviews": pending or 0,
        "avg_fraud_score": round(avg_score or 0.0, 4),
        "transactions_today": 0,  # Simplified
        "fraud_today": 0,
    }
