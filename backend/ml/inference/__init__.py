"""
Inference Module for Stroke Prediction

Provides CLI and programmatic interface for making predictions
using the trained model and preprocessing artifacts.
"""

from __future__ import annotations

import sys
from typing import Any

import joblib
import numpy as np
import polars as pl
import xgboost as xgb

from ml.features import (
    ARTIFACTS_DIR,
    clean_data,
    encode_categorical,
    load_artifacts,
    scale_numerical,
)

# ---------------------------------------------------------------------------
# Load artifacts
# ---------------------------------------------------------------------------
_model: xgb.XGBClassifier | None = None
_encoders: dict | None = None
_scaler: Any | None = None
_feature_names: list[str] | None = None
_threshold: float = 0.5


def load_model_artifacts() -> None:
    """Load model and preprocessing artifacts."""
    global _model, _encoders, _scaler, _feature_names, _threshold

    _model = joblib.load(ARTIFACTS_DIR / "model.joblib")
    _encoders, _scaler, _feature_names = load_artifacts()

    # Load optimal threshold from metrics
    import json
    with open(ARTIFACTS_DIR / "metrics.json") as f:
        metrics = json.load(f)
    _threshold = metrics.get("train_threshold", 0.5)

    print(f"Model loaded. Threshold: {_threshold:.4f}")


def preprocess_input(data: dict[str, Any]) -> np.ndarray:
    """Preprocess a single input dictionary for prediction."""
    # Convert to DataFrame
    df = pl.DataFrame([data])

    # Clean
    df = clean_data(df)

    # Encode categorical
    df, _ = encode_categorical(df, _encoders, fit=False)

    # Scale numerical
    df, _ = scale_numerical(df, _scaler, fit=False)

    # Ensure column order matches training
    df = df.select(_feature_names)

    return df.to_numpy()


def predict(data: dict[str, Any]) -> dict[str, Any]:
    """Make a prediction for a single patient."""
    if _model is None:
        load_model_artifacts()

    X = preprocess_input(data)
    proba = _model.predict_proba(X)[0, 1]
    prediction = int(proba >= _threshold)

    return {
        "stroke_risk": bool(prediction),
        "probability": float(proba),
        "threshold": _threshold,
        "risk_level": "HIGH" if prediction else "LOW",
    }


def predict_batch(data_list: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Make predictions for multiple patients."""
    if _model is None:
        load_model_artifacts()

    results = []
    for data in data_list:
        results.append(predict(data))
    return results


def validate_input(data: dict[str, Any]) -> tuple[bool, str]:
    """Validate input data has required fields."""
    required_fields = {
        "gender": ["Male", "Female", "Other"],
        "age": (0, 120),
        "hypertension": [0, 1],
        "heart_disease": [0, 1],
        "ever_married": ["Yes", "No"],
        "work_type": ["Private", "Self-employed", "Govt_job", "children", "Never_worked"],
        "Residence_type": ["Urban", "Rural"],
        "avg_glucose_level": (0, 400),
        "bmi": (0, 60),
        "smoking_status": ["never smoked", "formerly smoked", "smokes", "Unknown"],
    }

    for field, valid_values in required_fields.items():
        if field not in data:
            return False, f"Missing required field: {field}"

        value = data[field]
        if isinstance(valid_values, list):
            if value not in valid_values:
                return False, f"Invalid value for {field}: {value}. Must be one of {valid_values}"
        elif isinstance(valid_values, tuple):
            min_val, max_val = valid_values
            if not isinstance(value, (int, float)) or value < min_val or value > max_val:
                return False, (
                    f"Invalid value for {field}: {value}. "
                    f"Must be between {min_val} and {max_val}"
                )

    return True, "Valid"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def cli() -> None:
    """Command-line interface for stroke prediction."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Stroke Risk Prediction CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m ml.inference --gender Male --age 65 --hypertension 1 --heart_disease 0 \\
      --ever_married Yes --work_type Private --Residence_type Urban \\
      --avg_glucose_level 120 --bmi 28 --smoking_status "formerly smoked"

  python -m ml.inference --json '{"gender": "Male", "age": 65, ...}'
        """
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--json", type=str, help="JSON string with patient data")
    input_group.add_argument("--file", type=str, help="JSON file with patient data")

    # Individual fields
    parser.add_argument("--gender", choices=["Male", "Female", "Other"], help="Gender")
    parser.add_argument("--age", type=float, help="Age")
    parser.add_argument("--hypertension", type=int, choices=[0, 1], help="Hypertension (0/1)")
    parser.add_argument("--heart_disease", type=int, choices=[0, 1], help="Heart disease (0/1)")
    parser.add_argument("--ever_married", choices=["Yes", "No"], help="Ever married")
    parser.add_argument(
        "--work_type",
        choices=["Private", "Self-employed", "Govt_job", "children", "Never_worked"],
        help="Work type",
    )
    parser.add_argument("--Residence_type", choices=["Urban", "Rural"], help="Residence type")
    parser.add_argument("--avg_glucose_level", type=float, help="Average glucose level")
    parser.add_argument("--bmi", type=float, help="BMI")
    parser.add_argument(
        "--smoking_status",
        choices=["never smoked", "formerly smoked", "smokes", "Unknown"],
        help="Smoking status",
    )

    # Output options
    parser.add_argument("--output", choices=["json", "text"], default="text", help="Output format")
    parser.add_argument("--threshold", type=float, help="Override decision threshold")

    args = parser.parse_args()

    # Build input data
    if args.json:
        import json
        data = json.loads(args.json)
    elif args.file:
        import json
        with open(args.file) as f:
            data = json.load(f)
    else:
        data = {
            "gender": args.gender,
            "age": args.age,
            "hypertension": args.hypertension,
            "heart_disease": args.heart_disease,
            "ever_married": args.ever_married,
            "work_type": args.work_type,
            "Residence_type": args.Residence_type,
            "avg_glucose_level": args.avg_glucose_level,
            "bmi": args.bmi,
            "smoking_status": args.smoking_status,
        }

    # Validate
    valid, msg = validate_input(data)
    if not valid:
        print(f"Error: {msg}", file=sys.stderr)
        sys.exit(1)

    # Override threshold if provided
    global _threshold
    if args.threshold is not None:
        _threshold = args.threshold

    # Predict
    result = predict(data)

    # Output
    if args.output == "json":
        import json
        print(json.dumps(result, indent=2))
    else:
        print("\n" + "=" * 40)
        print("STROKE RISK PREDICTION")
        print("=" * 40)
        print(f"Risk Level:     {result['risk_level']}")
        print(f"Probability:    {result['probability']:.2%}")
        print(f"Threshold:      {result['threshold']:.2f}")
        print("=" * 40)
        print("\nInterpretation:")
        if result["stroke_risk"]:
            print("⚠️  HIGH RISK: Patient shows elevated risk factors for stroke.")
            print("   Recommendation: Consult healthcare provider for evaluation.")
        else:
            print("✅ LOW RISK: Patient does not show elevated stroke risk based on inputs.")
            print("   Recommendation: Maintain healthy lifestyle and regular check-ups.")


if __name__ == "__main__":
    cli()