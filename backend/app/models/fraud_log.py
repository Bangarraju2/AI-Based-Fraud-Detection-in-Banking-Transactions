"""Fraud Log Model — SQLAlchemy ORM (Audit Trail)"""

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class FraudLog(Base):
    __tablename__ = "fraud_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False, index=True)
    prediction_score = Column(Float, nullable=False)
    risk_category = Column(String(10), nullable=False)
    model_version = Column(String(50), nullable=True)
    model_name = Column(String(50), nullable=True)

    # Review fields
    reviewed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    review_status = Column(String(20), default="pending")  # pending / confirmed_fraud / false_positive
    review_notes = Column(Text, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    transaction = relationship("Transaction", back_populates="fraud_logs")
    reviewer = relationship("User", back_populates="reviewed_logs")

    def __repr__(self):
        return f"<FraudLog(id={self.id}, score={self.prediction_score}, status={self.review_status})>"
