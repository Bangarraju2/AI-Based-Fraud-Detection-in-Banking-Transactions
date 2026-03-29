"""
Data Preprocessing & Feature Engineering Pipeline
Generates synthetic credit card fraud data and prepares it for training.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
from typing import Tuple
import logging
import os

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")


def generate_synthetic_data(n_samples: int = 50000, fraud_ratio: float = 0.017) -> pd.DataFrame:
    """
    Generate synthetic credit card transaction data mimicking the Kaggle dataset.
    Features V1-V28 (PCA components), Time, Amount, and Class (fraud label).
    """
    np.random.seed(42)
    n_fraud = int(n_samples * fraud_ratio)
    n_legit = n_samples - n_fraud

    # Legitimate transactions
    legit_features = np.random.randn(n_legit, 28) * 1.5
    legit_time = np.sort(np.random.uniform(0, 172800, n_legit))
    legit_amount = np.abs(np.random.lognormal(mean=3.5, sigma=1.5, size=n_legit))
    legit_labels = np.zeros(n_legit)

    # Fraudulent transactions — different distribution
    fraud_features = np.random.randn(n_fraud, 28) * 3.0
    fraud_features[:, 0] -= 3.0   # V1 shift (common in real fraud data)
    fraud_features[:, 1] += 2.5   # V2 shift
    fraud_features[:, 3] += 2.0   # V4 shift
    fraud_features[:, 9] -= 2.5   # V10 shift
    fraud_features[:, 11] += 3.0  # V12 shift
    fraud_features[:, 13] -= 2.0  # V14 shift
    fraud_features[:, 16] -= 2.5  # V17 shift
    fraud_time = np.sort(np.random.uniform(0, 172800, n_fraud))
    fraud_amount = np.abs(np.random.lognormal(mean=5.0, sigma=2.0, size=n_fraud))
    fraud_labels = np.ones(n_fraud)

    # Combine
    features = np.vstack([legit_features, fraud_features])
    time_col = np.concatenate([legit_time, fraud_time])
    amount_col = np.concatenate([legit_amount, fraud_amount])
    labels = np.concatenate([legit_labels, fraud_labels])

    # Build DataFrame
    columns = [f"V{i}" for i in range(1, 29)]
    df = pd.DataFrame(features, columns=columns)
    df.insert(0, "Time", time_col)
    df["Amount"] = amount_col
    df["Class"] = labels.astype(int)

    # Shuffle
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    logger.info(f"Generated {len(df)} transactions: {n_legit} legit, {n_fraud} fraud ({fraud_ratio*100:.1f}%)")
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Apply feature engineering to raw transaction data."""
    df = df.copy()

    # Time-based features
    df["Hour"] = (df["Time"] / 3600).astype(int) % 24
    df["Is_Night"] = ((df["Hour"] >= 22) | (df["Hour"] <= 5)).astype(int)

    # Amount-based features
    df["Amount_Log"] = np.log1p(df["Amount"])
    df["Amount_Bin"] = pd.qcut(df["Amount"], q=10, labels=False, duplicates="drop")

    # Interaction features
    df["V1_V2_Interaction"] = df["V1"] * df["V2"]
    df["V3_V4_Interaction"] = df["V3"] * df["V4"]

    # Statistical features on key components
    key_features = ["V1", "V2", "V3", "V4", "V10", "V12", "V14", "V17"]
    df["Key_Features_Mean"] = df[key_features].mean(axis=1)
    df["Key_Features_Std"] = df[key_features].std(axis=1)

    logger.info(f"Feature engineering complete. Total features: {len(df.columns) - 1}")
    return df


def preprocess_data(
    df: pd.DataFrame,
    apply_smote: bool = True
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, StandardScaler, list]:
    """
    Full preprocessing pipeline:
    1. Feature engineering
    2. Train/test split
    3. Scaling
    4. SMOTE oversampling (on training set only)
    """
    from sklearn.model_selection import train_test_split

    # Apply feature engineering
    df = engineer_features(df)

    # Separate features and target
    feature_columns = [c for c in df.columns if c != "Class"]
    X = df[feature_columns].values
    y = df["Class"].values

    # Train/test split (stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Scale features
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    logger.info(f"Before SMOTE — Train: {len(X_train)}, Fraud: {int(y_train.sum())}")

    # Apply SMOTE on training data only
    if apply_smote:
        smote = SMOTE(random_state=42, sampling_strategy=0.5)
        X_train, y_train = smote.fit_resample(X_train, y_train)
        logger.info(f"After SMOTE  — Train: {len(X_train)}, Fraud: {int(y_train.sum())}")

    return X_train, X_test, y_train, y_test, scaler, feature_columns


def load_or_generate_data() -> pd.DataFrame:
    """Load dataset from file or generate synthetic data."""
    os.makedirs(DATA_DIR, exist_ok=True)
    data_path = os.path.join(DATA_DIR, "creditcard.csv")

    if os.path.exists(data_path):
        logger.info(f"Loading existing dataset from {data_path}")
        return pd.read_csv(data_path)
    else:
        logger.info("No dataset found. Generating synthetic data...")
        df = generate_synthetic_data()
        df.to_csv(data_path, index=False)
        logger.info(f"Saved synthetic dataset to {data_path}")
        return df
