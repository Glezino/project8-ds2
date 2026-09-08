"""
Feature Engineering for Stroke Prediction

Handles data preprocessing, encoding, scaling, and train/test splitting.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import polars as pl
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT_DIR / "ml" / "data" / "stroke_dataset.csv"
ARTIFACTS_DIR = ROOT_DIR / "ml" / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
NUMERICAL_COLS = ["age", "avg_glucose_level", "bmi", "hypertension", "heart_disease"]
CATEGORICAL_COLS = ["gender", "ever_married", "work_type", "Residence_type", "smoking_status"]
TARGET_COL = "stroke"
ID_COL = "id" if "id" in pl.read_csv(DATA_PATH, n_rows=1).columns else None


def load_data() -> pl.DataFrame:
    """Load the stroke dataset."""
    df = pl.read_csv(DATA_PATH)
    print(f"Loaded {df.height} rows, {df.width} columns")
    return df


def clean_data(df: pl.DataFrame) -> pl.DataFrame:
    """Clean the dataset: handle 'Unknown' smoking status, drop ID if present."""
    df = df.clone()

    # Replace "Unknown" in smoking_status with "never smoked" (most frequent)
    # or treat as separate category - we'll use "never smoked" as default
    df = df.with_columns(
        pl.when(pl.col("smoking_status") == "Unknown")
        .then(pl.lit("never smoked"))
        .otherwise(pl.col("smoking_status"))
        .alias("smoking_status")
    )

    # Drop ID column if exists
    if ID_COL and ID_COL in df.columns:
        df = df.drop(ID_COL)

    # Drop 'children' work_type rows (pediatric, very low stroke rate)
    df = df.filter(pl.col("work_type") != "children")

    print(f"After cleaning: {df.height} rows")
    return df


def encode_categorical(
    df: pl.DataFrame, encoders: dict | None = None, fit: bool = True
) -> tuple[pl.DataFrame, dict]:
    """Encode categorical columns using LabelEncoder."""
    df = df.clone()
    encoders = encoders or {}

    for col in CATEGORICAL_COLS:
        if col not in df.columns:
            continue

        if fit:
            le = LabelEncoder()
            # Fit on all possible values including unseen
            le.fit(df[col].to_list())
            encoders[col] = le
        else:
            le = encoders.get(col)
            if le is None:
                raise ValueError(f"No encoder found for column {col}")

        # Transform
        df = df.with_columns(
            pl.Series(col, le.transform(df[col].to_list())).alias(col)
        )

    return df, encoders


def scale_numerical(
    df: pl.DataFrame, scaler: StandardScaler | None = None, fit: bool = True
) -> tuple[pl.DataFrame, StandardScaler]:
    """Scale numerical columns using StandardScaler."""
    df = df.clone()

    if fit:
        scaler = StandardScaler()
        scaler.fit(df.select(NUMERICAL_COLS).to_numpy())
    elif scaler is None:
        raise ValueError("Scaler required when fit=False")

    scaled_data = scaler.transform(df.select(NUMERICAL_COLS).to_numpy())
    scaled_df = pl.DataFrame(scaled_data, schema=NUMERICAL_COLS)

    # Replace numerical columns with scaled versions
    df = df.drop(NUMERICAL_COLS).hstack(scaled_df)

    return df, scaler


def prepare_features(
    df: pl.DataFrame,
    encoders: dict | None = None,
    scaler: StandardScaler | None = None,
    fit: bool = True,
) -> tuple[pl.DataFrame, dict, StandardScaler]:
    """Full feature preparation pipeline."""
    df = clean_data(df)
    df, encoders = encode_categorical(df, encoders, fit)
    df, scaler = scale_numerical(df, scaler, fit)
    return df, encoders, scaler


def split_data(
    df: pl.DataFrame,
    test_size: float = 0.2,
    random_state: int = 42,
) -> tuple[pl.DataFrame, pl.DataFrame, pl.Series, pl.Series]:
    """Stratified train/test split."""
    X = df.drop(TARGET_COL)
    y = df[TARGET_COL]

    X_train, X_test, y_train, y_test = train_test_split(
        X.to_numpy(),
        y.to_numpy(),
        test_size=test_size,
        random_state=random_state,
        stratify=y.to_numpy(),
    )

    # Convert back to polars
    X_train_df = pl.DataFrame(X_train, schema=X.columns)
    X_test_df = pl.DataFrame(X_test, schema=X.columns)
    y_train_series = pl.Series(TARGET_COL, y_train)
    y_test_series = pl.Series(TARGET_COL, y_test)

    print(f"Train: {X_train_df.height} samples, Test: {X_test_df.height} samples")
    print(f"Train class distribution: {y_train_series.value_counts().to_dict()}")
    print(f"Test class distribution: {y_test_series.value_counts().to_dict()}")

    return X_train_df, X_test_df, y_train_series, y_test_series


def save_artifacts(encoders: dict, scaler: StandardScaler, feature_names: list[str]) -> None:
    """Save preprocessing artifacts."""
    joblib.dump(encoders, ARTIFACTS_DIR / "encoders.joblib")
    joblib.dump(scaler, ARTIFACTS_DIR / "scaler.joblib")
    with open(ARTIFACTS_DIR / "feature_names.json", "w") as f:
        json.dump(feature_names, f)
    print(f"Artifacts saved to {ARTIFACTS_DIR}")


def load_artifacts() -> tuple[dict, StandardScaler, list[str]]:
    """Load preprocessing artifacts."""
    encoders = joblib.load(ARTIFACTS_DIR / "encoders.joblib")
    scaler = joblib.load(ARTIFACTS_DIR / "scaler.joblib")
    with open(ARTIFACTS_DIR / "feature_names.json") as f:
        feature_names = json.load(f)
    return encoders, scaler, feature_names


def main() -> None:
    """Run feature engineering pipeline and save artifacts."""
    sys.stdout.reconfigure(encoding="utf-8")

    df = load_data()
    df, encoders, scaler = prepare_features(df, fit=True)

    # Save feature names (all columns except target)
    feature_names = [c for c in df.columns if c != TARGET_COL]

    save_artifacts(encoders, scaler, feature_names)

    print("Feature engineering complete.")


if __name__ == "__main__":
    main()