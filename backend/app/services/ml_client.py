"""
ML Client Service
HTTP client that communicates with the ML microservice for predictions.
"""

import httpx
import logging
from typing import Dict, Any, Optional
from ..core.config import settings

logger = logging.getLogger(__name__)

ML_PREDICT_URL = f"{settings.ML_SERVICE_URL}/predict"
ML_HEALTH_URL = f"{settings.ML_SERVICE_URL}/health"
ML_MODEL_INFO_URL = f"{settings.ML_SERVICE_URL}/model-info"


async def get_fraud_prediction(transaction_data: Dict[str, float]) -> Dict[str, Any]:
    """
    Send transaction data to ML service and get fraud prediction.
    Falls back to a default response if ML service is unavailable.
    """
    ml_payload = {
        "Time": transaction_data.get("time", 0.0),
        "Amount": transaction_data.get("amount", 0.0),
    }
    for i in range(1, 29):
        ml_payload[f"V{i}"] = transaction_data.get(f"v{i}", 0.0)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(ML_PREDICT_URL, json=ml_payload)
            response.raise_for_status()
            result = response.json()
            logger.info(
                f"ML prediction: score={result.get('fraud_probability')}, "
                f"risk={result.get('risk_category')}"
            )
            return result
    except httpx.ConnectError:
        logger.warning("ML service unavailable. Using fallback prediction.")
        return _fallback_prediction(transaction_data)
    except Exception as e:
        logger.error(f"ML service error: {e}")
        return _fallback_prediction(transaction_data)


def _fallback_prediction(data: Dict[str, float]) -> Dict[str, Any]:
    """Simple rule-based fallback when ML service is down."""
    amount = data.get("amount", 0.0)
    score = min(amount / 5000.0, 0.99) if amount > 1000 else 0.1
    risk = "HIGH" if score > 0.7 else ("MEDIUM" if score > 0.3 else "LOW")
    return {
        "fraud_probability": round(score, 6),
        "is_fraud": score >= 0.5,
        "risk_category": risk,
        "requires_manual_review": risk in ("HIGH", "MEDIUM"),
        "model_version": "fallback",
        "model_name": "rule_based_fallback",
        "feature_importance": {},
        "confidence": round(abs(score - 0.5) * 2, 4),
    }


async def check_ml_health() -> Optional[Dict[str, Any]]:
    """Check ML service health."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(ML_HEALTH_URL)
            return response.json()
    except Exception:
        return None


async def get_model_info() -> Optional[Dict[str, Any]]:
    """Get model metadata from ML service."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(ML_MODEL_INFO_URL)
            return response.json()
    except Exception:
        return None
