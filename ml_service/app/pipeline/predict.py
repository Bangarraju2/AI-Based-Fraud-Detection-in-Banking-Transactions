"""
Prediction Service
Loads the trained model and provides fraud prediction with risk categorization.
"""

import os
import json
import logging
import numpy as np
import joblib
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "saved_models")


class FraudPredictor:
    """Handles fraud prediction using the trained ML model."""

    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_columns = None
        self.metadata = None
        self._loaded = False

    def load_model(self):
        """Load the trained model, scaler, and metadata."""
        try:
            model_path = os.path.join(MODELS_DIR, "best_model.joblib")
            scaler_path = os.path.join(MODELS_DIR, "scaler.joblib")
            columns_path = os.path.join(MODELS_DIR, "feature_columns.joblib")
            metadata_path = os.path.join(MODELS_DIR, "model_metadata.json")

            if not os.path.exists(model_path):
                logger.warning("No trained model found. Running training pipeline...")
                from .train import train_pipeline
                train_pipeline()

            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            self.feature_columns = joblib.load(columns_path)

            if os.path.exists(metadata_path):
                with open(metadata_path, "r") as f:
                    self.metadata = json.load(f)

            self._loaded = True
            logger.info(f"Model loaded: {self.metadata.get('best_model', 'unknown')} "
                       f"v{self.metadata.get('version', 'unknown')}")

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    def _engineer_features(self, data: Dict[str, float]) -> np.ndarray:
        """Apply the same feature engineering as training pipeline."""
        # Start with basic features
        features = {}

        # V1-V28 features
        for i in range(1, 29):
            features[f"V{i}"] = data.get(f"V{i}", data.get(f"v{i}", 0.0))

        features["Time"] = data.get("Time", data.get("time", 0.0))
        features["Amount"] = data.get("Amount", data.get("amount", 0.0))

        # Engineered features (must match training pipeline)
        time_val = features["Time"]
        amount_val = features["Amount"]

        features["Hour"] = int(time_val / 3600) % 24
        features["Is_Night"] = 1 if (features["Hour"] >= 22 or features["Hour"] <= 5) else 0
        features["Amount_Log"] = np.log1p(amount_val)
        features["Amount_Bin"] = min(int(amount_val / 50), 9)  # Simplified binning
        features["V1_V2_Interaction"] = features["V1"] * features["V2"]
        features["V3_V4_Interaction"] = features["V3"] * features["V4"]

        key_vals = [features[f"V{i}"] for i in [1, 2, 3, 4, 10, 12, 14, 17]]
        features["Key_Features_Mean"] = np.mean(key_vals)
        features["Key_Features_Std"] = np.std(key_vals)

        # Build feature vector in correct order
        feature_vector = [features.get(col, 0.0) for col in self.feature_columns]
        return np.array(feature_vector).reshape(1, -1)

    def _categorize_risk(self, probability: float) -> str:
        """Categorize fraud risk based on probability threshold."""
        if probability >= 0.7:
            return "HIGH"
        elif probability >= 0.3:
            return "MEDIUM"
        else:
            return "LOW"

    def predict(self, transaction_data: Dict[str, float]) -> Dict[str, Any]:
        """
        Make fraud prediction for a single transaction.
        Returns probability score, risk category, and feature importance.
        """
        if not self._loaded:
            self.load_model()

        # Engineer features and scale
        features = self._engineer_features(transaction_data)
        features_scaled = self.scaler.transform(features)

        # Predict
        fraud_probability = float(self.model.predict_proba(features_scaled)[0][1])
        is_fraud = fraud_probability >= 0.5
        risk_category = self._categorize_risk(fraud_probability)

        # Get feature importance (from metadata)
        importance = {}
        if self.metadata and "metrics" in self.metadata:
            importance = self.metadata["metrics"].get("feature_importance", {})

        result = {
            "fraud_probability": round(fraud_probability, 6),
            "is_fraud": is_fraud,
            "risk_category": risk_category,
            "requires_manual_review": risk_category in ("HIGH", "MEDIUM"),
            "model_version": self.metadata.get("version", "unknown") if self.metadata else "unknown",
            "model_name": self.metadata.get("best_model", "unknown") if self.metadata else "unknown",
            "feature_importance": dict(list(importance.items())[:10]),
            "confidence": round(abs(fraud_probability - 0.5) * 2, 4),
        }

        logger.info(
            f"Prediction: prob={result['fraud_probability']}, "
            f"risk={result['risk_category']}, "
            f"amount={transaction_data.get('Amount', 'N/A')}"
        )

        return result

    def get_model_info(self) -> Dict[str, Any]:
        """Return model metadata and performance metrics."""
        if not self._loaded:
            self.load_model()

        return {
            "model_name": self.metadata.get("best_model", "unknown"),
            "version": self.metadata.get("version", "unknown"),
            "metrics": self.metadata.get("metrics", {}),
            "n_features": self.metadata.get("n_features", 0),
            "trained_at": self.metadata.get("trained_at", "unknown"),
            "all_model_results": self.metadata.get("all_results", {}),
        }


# Singleton instance
predictor = FraudPredictor()
