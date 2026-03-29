"""Transaction Schemas — Pydantic Models"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TransactionCreate(BaseModel):
    amount: float = Field(..., ge=0, description="Transaction amount")
    time: float = Field(default=0.0, description="Seconds elapsed since first transaction")
    v1: float = Field(default=0.0)
    v2: float = Field(default=0.0)
    v3: float = Field(default=0.0)
    v4: float = Field(default=0.0)
    v5: float = Field(default=0.0)
    v6: float = Field(default=0.0)
    v7: float = Field(default=0.0)
    v8: float = Field(default=0.0)
    v9: float = Field(default=0.0)
    v10: float = Field(default=0.0)
    v11: float = Field(default=0.0)
    v12: float = Field(default=0.0)
    v13: float = Field(default=0.0)
    v14: float = Field(default=0.0)
    v15: float = Field(default=0.0)
    v16: float = Field(default=0.0)
    v17: float = Field(default=0.0)
    v18: float = Field(default=0.0)
    v19: float = Field(default=0.0)
    v20: float = Field(default=0.0)
    v21: float = Field(default=0.0)
    v22: float = Field(default=0.0)
    v23: float = Field(default=0.0)
    v24: float = Field(default=0.0)
    v25: float = Field(default=0.0)
    v26: float = Field(default=0.0)
    v27: float = Field(default=0.0)
    v28: float = Field(default=0.0)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "amount": 149.62,
                    "time": 406.0,
                    "v1": -1.35,
                    "v2": 1.19,
                    "v3": 0.27,
                    "v14": -0.51,
                }
            ]
        }
    }


class TransactionResponse(BaseModel):
    id: int
    transaction_id: str
    amount: float
    time: float
    fraud_score: Optional[float] = None
    risk_category: Optional[str] = None
    is_fraud: bool
    is_flagged_for_review: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TransactionListResponse(BaseModel):
    transactions: List[TransactionResponse]
    total: int
    page: int
    per_page: int


class TransactionDetail(TransactionResponse):
    v1: float = 0.0
    v2: float = 0.0
    v3: float = 0.0
    v4: float = 0.0
    v5: float = 0.0
    v6: float = 0.0
    v7: float = 0.0
    v8: float = 0.0
    v9: float = 0.0
    v10: float = 0.0
    v11: float = 0.0
    v12: float = 0.0
    v13: float = 0.0
    v14: float = 0.0
    v15: float = 0.0
    v16: float = 0.0
    v17: float = 0.0
    v18: float = 0.0
    v19: float = 0.0
    v20: float = 0.0
    v21: float = 0.0
    v22: float = 0.0
    v23: float = 0.0
    v24: float = 0.0
    v25: float = 0.0
    v26: float = 0.0
    v27: float = 0.0
    v28: float = 0.0

    model_config = {"from_attributes": True}
