"""
ML Service Tests — Prediction Validation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_prediction_output():
    """Test that prediction returns expected structure."""
    from app.pipeline.predict import FraudPredictor

    predictor = FraudPredictor()
    predictor.load_model()

    sample = {
        "Time": 406.0,
        "Amount": 149.62,
        "V1": -1.3598,
        "V2": -0.0728,
        "V3": 2.5363,
        "V4": 1.3782,
        "V14": -0.3112,
    }

    result = predictor.predict(sample)

    assert "fraud_probability" in result
    assert "risk_category" in result
    assert "is_fraud" in result
    assert "requires_manual_review" in result
    assert 0.0 <= result["fraud_probability"] <= 1.0
    assert result["risk_category"] in ("LOW", "MEDIUM", "HIGH")
    assert isinstance(result["is_fraud"], bool)


def test_high_risk_transaction():
    """Test that suspicious transaction gets high risk."""
    from app.pipeline.predict import FraudPredictor

    predictor = FraudPredictor()
    predictor.load_model()

    suspicious = {
        "Time": 50000.0,
        "Amount": 4999.99,
        "V1": -5.0,
        "V2": 4.5,
        "V3": -2.0,
        "V4": 4.0,
        "V10": -6.0,
        "V12": -10.0,
        "V14": -15.0,
        "V17": -8.0,
    }

    result = predictor.predict(suspicious)
    assert result["fraud_probability"] > 0.3  # Should flag as suspicious


def test_model_info():
    """Test model info returns metadata."""
    from app.pipeline.predict import FraudPredictor

    predictor = FraudPredictor()
    predictor.load_model()

    info = predictor.get_model_info()
    assert "model_name" in info
    assert "version" in info
    assert "metrics" in info
