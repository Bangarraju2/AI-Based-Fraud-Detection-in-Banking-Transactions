"""
Model Training Pipeline
Trains and compares Logistic Regression, Random Forest, and XGBoost.
Selects best model based on ROC-AUC and saves it.
"""

import os
import json
import logging
import numpy as np
import joblib
from datetime import datetime
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (
    classification_report,
    roc_auc_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)
from typing import Dict, Any

from .data_preprocessing import load_or_generate_data, preprocess_data

logger = logging.getLogger(__name__)

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "saved_models")


def get_models() -> Dict[str, Any]:
    """Return dictionary of models to train."""
    return {
        "logistic_regression": LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=42,
            C=0.1,
            solver="lbfgs",
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ),
        "xgboost": XGBClassifier(
            n_estimators=300,
            max_depth=8,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=5,
            random_state=42,
            eval_metric="logloss",
            use_label_encoder=False,
        ),
    }


def evaluate_model(model, X_test, y_test, model_name: str) -> Dict[str, float]:
    """Evaluate a trained model and return metrics."""
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    metrics = {
        "model_name": model_name,
        "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
        "recall": round(recall_score(y_test, y_pred, zero_division=0), 4),
        "f1_score": round(f1_score(y_test, y_pred, zero_division=0), 4),
        "roc_auc": round(roc_auc_score(y_test, y_proba), 4),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
    }

    logger.info(f"\n{'='*50}")
    logger.info(f"Model: {model_name}")
    logger.info(f"Precision: {metrics['precision']}")
    logger.info(f"Recall:    {metrics['recall']}")
    logger.info(f"F1 Score:  {metrics['f1_score']}")
    logger.info(f"ROC-AUC:   {metrics['roc_auc']}")
    logger.info(f"\n{classification_report(y_test, y_pred, zero_division=0)}")

    return metrics


def get_feature_importance(model, feature_columns: list, model_name: str) -> Dict[str, float]:
    """Extract feature importance from trained model."""
    importances = {}

    if hasattr(model, "feature_importances_"):
        imp = model.feature_importances_
        sorted_idx = np.argsort(imp)[::-1][:15]  # Top 15
        for idx in sorted_idx:
            importances[feature_columns[idx]] = round(float(imp[idx]), 6)
    elif hasattr(model, "coef_"):
        imp = np.abs(model.coef_[0])
        sorted_idx = np.argsort(imp)[::-1][:15]
        for idx in sorted_idx:
            importances[feature_columns[idx]] = round(float(imp[idx]), 6)

    return importances


def train_pipeline() -> Dict[str, Any]:
    """
    Full training pipeline:
    1. Load/generate data
    2. Preprocess & apply SMOTE
    3. Train all models
    4. Evaluate & compare
    5. Save best model
    """
    logging.basicConfig(level=logging.INFO)
    os.makedirs(MODELS_DIR, exist_ok=True)

    logger.info("Starting training pipeline...")

    # Load and preprocess data
    df = load_or_generate_data()
    X_train, X_test, y_train, y_test, scaler, feature_columns = preprocess_data(df)

    # Train and evaluate all models
    models = get_models()
    results = {}
    trained_models = {}

    for name, model in models.items():
        logger.info(f"\nTraining {name}...")
        model.fit(X_train, y_train)
        metrics = evaluate_model(model, X_test, y_test, name)
        importance = get_feature_importance(model, feature_columns, name)
        metrics["feature_importance"] = importance
        results[name] = metrics
        trained_models[name] = model

    # Select best model based on ROC-AUC
    best_name = max(results, key=lambda x: results[x]["roc_auc"])
    best_model = trained_models[best_name]
    best_metrics = results[best_name]

    logger.info(f"\n{'='*50}")
    logger.info(f"BEST MODEL: {best_name} (ROC-AUC: {best_metrics['roc_auc']})")
    logger.info(f"{'='*50}")

    # Save best model, scaler, and metadata
    model_version = datetime.now().strftime("%Y%m%d_%H%M%S")

    joblib.dump(best_model, os.path.join(MODELS_DIR, "best_model.joblib"))
    joblib.dump(scaler, os.path.join(MODELS_DIR, "scaler.joblib"))
    joblib.dump(feature_columns, os.path.join(MODELS_DIR, "feature_columns.joblib"))

    # Save model metadata
    metadata = {
        "best_model": best_name,
        "version": model_version,
        "metrics": best_metrics,
        "all_results": results,
        "feature_columns": feature_columns,
        "n_features": len(feature_columns),
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "trained_at": datetime.now().isoformat(),
    }

    with open(os.path.join(MODELS_DIR, "model_metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"Model saved to {MODELS_DIR}")
    return metadata


if __name__ == "__main__":
    train_pipeline()
