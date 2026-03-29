"""
ML Service — FastAPI Application
Serves fraud prediction endpoints for the main backend.
"""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from .pipeline.predict import predictor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model on startup."""
    logger.info("Loading ML model...")
    predictor.load_model()
    logger.info("ML model loaded successfully!")
    yield
    logger.info("ML Service shutting down.")


app = FastAPI(
    title="FraudShield ML Service",
    description="Machine Learning microservice for real-time fraud detection in banking transactions.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Request/Response Schemas ─────────────────────

class TransactionInput(BaseModel):
    """Input schema for fraud prediction."""
    Time: float = Field(default=0.0, description="Seconds elapsed since first transaction")
    Amount: float = Field(..., ge=0, description="Transaction amount")
    V1: float = Field(default=0.0)
    V2: float = Field(default=0.0)
    V3: float = Field(default=0.0)
    V4: float = Field(default=0.0)
    V5: float = Field(default=0.0)
    V6: float = Field(default=0.0)
    V7: float = Field(default=0.0)
    V8: float = Field(default=0.0)
    V9: float = Field(default=0.0)
    V10: float = Field(default=0.0)
    V11: float = Field(default=0.0)
    V12: float = Field(default=0.0)
    V13: float = Field(default=0.0)
    V14: float = Field(default=0.0)
    V15: float = Field(default=0.0)
    V16: float = Field(default=0.0)
    V17: float = Field(default=0.0)
    V18: float = Field(default=0.0)
    V19: float = Field(default=0.0)
    V20: float = Field(default=0.0)
    V21: float = Field(default=0.0)
    V22: float = Field(default=0.0)
    V23: float = Field(default=0.0)
    V24: float = Field(default=0.0)
    V25: float = Field(default=0.0)
    V26: float = Field(default=0.0)
    V27: float = Field(default=0.0)
    V28: float = Field(default=0.0)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "Time": 406.0,
                    "Amount": 250.50,
                    "V1": -1.35,
                    "V2": 1.19,
                    "V3": 0.27,
                    "V4": 0.17,
                    "V14": -0.51,
                }
            ]
        }
    }


class PredictionResponse(BaseModel):
    """Response schema for fraud prediction."""
    fraud_probability: float
    is_fraud: bool
    risk_category: str
    requires_manual_review: bool
    model_version: str
    model_name: str
    feature_importance: Dict[str, float]
    confidence: float


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    model_loaded: bool
    model_version: Optional[str] = None


class ModelInfoResponse(BaseModel):
    """Model information response."""
    model_name: str
    version: str
    metrics: Dict[str, Any]
    n_features: int
    trained_at: str
    all_model_results: Dict[str, Any]


# ─── Endpoints ────────────────────────────────────

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        service="FraudShield ML Service",
        model_loaded=predictor._loaded,
        model_version=predictor.metadata.get("version") if predictor.metadata else None,
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict_fraud(transaction: TransactionInput):
    """
    Predict fraud probability for a banking transaction.

    Returns:
    - **fraud_probability**: Score between 0.0 and 1.0
    - **risk_category**: LOW / MEDIUM / HIGH
    - **requires_manual_review**: Flag for analyst review
    - **feature_importance**: Top contributing features
    """
    try:
        data = transaction.model_dump()
        result = predictor.predict(data)
        return PredictionResponse(**result)
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.get("/model-info", response_model=ModelInfoResponse, tags=["Model"])
async def get_model_info():
    """Get information about the currently loaded model."""
    try:
        info = predictor.get_model_info()
        return ModelInfoResponse(**info)
    except Exception as e:
        logger.error(f"Model info error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/retrain", tags=["MLOps"])
async def retrain_model():
    """
    Trigger model retraining pipeline.
    In production, this would be handled by a job scheduler.
    """
    try:
        from .pipeline.train import train_pipeline
        metadata = train_pipeline()
        predictor.load_model()  # Reload updated model
        return {
            "status": "success",
            "message": "Model retrained and reloaded",
            "new_version": metadata["version"],
            "best_model": metadata["best_model"],
            "metrics": metadata["metrics"],
        }
    except Exception as e:
        logger.error(f"Retraining error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
