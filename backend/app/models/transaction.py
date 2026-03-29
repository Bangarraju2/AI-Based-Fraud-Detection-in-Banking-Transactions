"""Transaction Model — SQLAlchemy ORM"""

from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String(64), unique=True, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    time = Column(Float, nullable=False)

    # PCA features V1-V28
    v1 = Column(Float, default=0.0)
    v2 = Column(Float, default=0.0)
    v3 = Column(Float, default=0.0)
    v4 = Column(Float, default=0.0)
    v5 = Column(Float, default=0.0)
    v6 = Column(Float, default=0.0)
    v7 = Column(Float, default=0.0)
    v8 = Column(Float, default=0.0)
    v9 = Column(Float, default=0.0)
    v10 = Column(Float, default=0.0)
    v11 = Column(Float, default=0.0)
    v12 = Column(Float, default=0.0)
    v13 = Column(Float, default=0.0)
    v14 = Column(Float, default=0.0)
    v15 = Column(Float, default=0.0)
    v16 = Column(Float, default=0.0)
    v17 = Column(Float, default=0.0)
    v18 = Column(Float, default=0.0)
    v19 = Column(Float, default=0.0)
    v20 = Column(Float, default=0.0)
    v21 = Column(Float, default=0.0)
    v22 = Column(Float, default=0.0)
    v23 = Column(Float, default=0.0)
    v24 = Column(Float, default=0.0)
    v25 = Column(Float, default=0.0)
    v26 = Column(Float, default=0.0)
    v27 = Column(Float, default=0.0)
    v28 = Column(Float, default=0.0)

    # Prediction results
    fraud_score = Column(Float, nullable=True)
    risk_category = Column(String(10), nullable=True)  # LOW / MEDIUM / HIGH
    is_fraud = Column(Boolean, default=False)
    is_flagged_for_review = Column(Boolean, default=False)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    fraud_logs = relationship("FraudLog", back_populates="transaction", lazy="selectin")

    # Performance indexes
    __table_args__ = (
        Index("idx_transactions_fraud_score", "fraud_score"),
        Index("idx_transactions_risk_category", "risk_category"),
        Index("idx_transactions_created_at", "created_at"),
        Index("idx_transactions_is_fraud", "is_fraud"),
    )

    def __repr__(self):
        return f"<Transaction(id={self.id}, amount={self.amount}, risk={self.risk_category})>"
