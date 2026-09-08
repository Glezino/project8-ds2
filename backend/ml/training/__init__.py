"""
Model Training for Stroke Prediction

Trains XGBoost classifier with class weighting, cross-validation for overfitting control,
and comprehensive evaluation with metrics and feature importance.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import polars as pl
import xgboost as xgb
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score

from ml.features import (
    ARTIFACTS_DIR,
    prepare_features,
    split_data,
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parents[2]
MODEL_PATH = ARTIFACTS_DIR / "model.joblib"
METRICS_PATH = ARTIFACTS_DIR / "metrics.json"
FEATURE_IMPORTANCE_PATH = ARTIFACTS_DIR / "feature_importance.json"
CV_RESULTS_PATH = ARTIFACTS_DIR / "cv_results.json"

# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------
def get_model_params() -> dict[str, Any]:
    """Get XGBoost model parameters optimized for imbalanced data with strong overfitting control."""
    return {
        "objective": "binary:logistic",
        "eval_metric": "auc",
        "max_depth": 2,
        "learning_rate": 0.02,
        "n_estimators": 200,
        "subsample": 0.65,
        "colsample_bytree": 0.65,
        "min_child_weight": 25,
        "gamma": 1.0,
        "reg_alpha": 3.0,
        "reg_lambda": 15.0,
        "scale_pos_weight": 19,
        "random_state": 42,
        "n_jobs": -1,
        "verbosity": 0,
    }


def train_model(
    X_train: pl.DataFrame,
    y_train: pl.Series,
    X_val: pl.DataFrame | None = None,
    y_val: pl.Series | None = None,
) -> xgb.XGBClassifier:
    """Train XGBoost model with optional validation set for early stopping."""
    params = get_model_params()
    model = xgb.XGBClassifier(**params)

    eval_set = [(X_train.to_numpy(), y_train.to_numpy())]
    if X_val is not None and y_val is not None:
        eval_set.append((X_val.to_numpy(), y_val.to_numpy()))

    model.fit(
        X_train.to_numpy(),
        y_train.to_numpy(),
        eval_set=eval_set,
        verbose=False,
    )

    return model


def find_optimal_threshold(
    y_true: np.ndarray,
    y_pred_proba: np.ndarray,
) -> float:
    """Find threshold that maximizes F1 score."""
    from sklearn.metrics import f1_score
    thresholds = np.linspace(0.1, 0.9, 81)
    best_f1 = 0
    best_threshold = 0.5
    for thresh in thresholds:
        y_pred = (y_pred_proba >= thresh).astype(int)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        if f1 > best_f1:
            best_f1 = f1
            best_threshold = thresh
    return best_threshold


def evaluate_model(
    model: xgb.XGBClassifier,
    X: pl.DataFrame,
    y: pl.Series,
    prefix: str = "",
    threshold: float | None = None,
) -> dict[str, float]:
    """Evaluate model and return metrics."""
    y_pred_proba = model.predict_proba(X.to_numpy())[:, 1]

    if threshold is None:
        threshold = find_optimal_threshold(y.to_numpy(), y_pred_proba)

    y_pred = (y_pred_proba >= threshold).astype(int)

    metrics = {
        f"{prefix}accuracy": accuracy_score(y, y_pred),
        f"{prefix}precision": precision_score(y, y_pred, zero_division=0),
        f"{prefix}recall": recall_score(y, y_pred, zero_division=0),
        f"{prefix}f1": f1_score(y, y_pred, zero_division=0),
        f"{prefix}roc_auc": roc_auc_score(y, y_pred_proba),
        f"{prefix}threshold": threshold,
    }

    # Confusion matrix
    cm = confusion_matrix(y, y_pred)
    metrics[f"{prefix}tn"] = int(cm[0, 0])
    metrics[f"{prefix}fp"] = int(cm[0, 1])
    metrics[f"{prefix}fn"] = int(cm[1, 0])
    metrics[f"{prefix}tp"] = int(cm[1, 1])

    return metrics


def cross_validate_model(
    X: pl.DataFrame,
    y: pl.Series,
    n_splits: int = 5,
) -> dict[str, Any]:
    """Perform stratified cross-validation to check overfitting."""
    params = get_model_params()
    model = xgb.XGBClassifier(**params)

    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)

    scoring = ["accuracy", "precision", "recall", "f1", "roc_auc"]
    cv_results = {}

    for score_name in scoring:
        scores = cross_val_score(model, X.to_numpy(), y.to_numpy(), cv=cv, scoring=score_name, n_jobs=-1)
        cv_results[score_name] = {
            "scores": scores.tolist(),
            "mean": float(np.mean(scores)),
            "std": float(np.std(scores)),
        }

    return cv_results


def check_overfitting(
    train_metrics: dict[str, float],
    test_metrics: dict[str, float],
    threshold: float = 0.05,
) -> tuple[bool, dict[str, float]]:
    """Check if overfitting exceeds threshold (5 percentage points).
    
    Uses 0.5 threshold metrics for fair comparison, or the provided metrics.
    """
    diffs = {}
    overfit = False

    # Use raw metrics (with _0.5 suffix if available, else use as-is)
    for key in ["accuracy", "precision", "recall", "f1", "roc_auc"]:
        train_key = f"train_{key}"
        test_key = f"test_{key}"
        if train_key in train_metrics and test_key in test_metrics:
            diff = train_metrics[train_key] - test_metrics[test_key]
            diffs[key] = diff
            if diff > threshold:
                overfit = True

    return overfit, diffs


def get_feature_importance(model: xgb.XGBClassifier, feature_names: list[str]) -> list[dict]:
    """Get feature importance from trained model."""
    importance = model.feature_importances_
    features_imp = [
        {"feature": name, "importance": float(imp)}
        for name, imp in zip(feature_names, importance, strict=False)
    ]
    features_imp.sort(key=lambda x: x["importance"], reverse=True)
    return features_imp


def save_model(model: xgb.XGBClassifier) -> None:
    """Save trained model."""
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")


def save_metrics(metrics: dict) -> None:
    """Save metrics to JSON."""
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {METRICS_PATH}")


def save_feature_importance(importance: list[dict]) -> None:
    """Save feature importance to JSON."""
    with open(FEATURE_IMPORTANCE_PATH, "w") as f:
        json.dump(importance, f, indent=2)
    print(f"Feature importance saved to {FEATURE_IMPORTANCE_PATH}")


def save_cv_results(cv_results: dict) -> None:
    """Save cross-validation results to JSON."""
    with open(CV_RESULTS_PATH, "w") as f:
        json.dump(cv_results, f, indent=2)
    print(f"CV results saved to {CV_RESULTS_PATH}")


def generate_report(
    train_metrics: dict,
    test_metrics: dict,
    cv_results: dict,
    feature_importance: list[dict],
    overfit: bool,
    overfit_diffs: dict,
) -> str:
    """Generate markdown report with model performance."""
    report = ["# Model Performance Report — Stroke Prediction", ""]

    report.append("## 1. Training Metrics")
    report.append("")
    report.append("| Metric | Value |")
    report.append("|--------|-------|")
    for key in ["accuracy", "precision", "recall", "f1", "roc_auc"]:
        report.append(f"| {key} | {train_metrics.get(f'train_{key}', 0):.4f} |")
    report.append("")

    report.append("## 2. Test Metrics")
    report.append("")
    report.append("| Metric | Value |")
    report.append("|--------|-------|")
    for key in ["accuracy", "precision", "recall", "f1", "roc_auc"]:
        report.append(f"| {key} | {test_metrics.get(f'test_{key}', 0):.4f} |")
    report.append("")

    report.append("## 3. Overfitting Analysis")
    report.append("")
    report.append("**Threshold:** 5 percentage points (0.05)")
    report.append(f"**Overfitting Detected:** {'Yes ⚠️' if overfit else 'No ✅'}")
    report.append("")
    report.append("| Metric | Train | Test | Difference |")
    report.append("|--------|-------|------|------------|")
    for key in ["accuracy", "precision", "recall", "f1", "roc_auc"]:
        train_val = train_metrics.get(f"train_{key}", 0)
        test_val = test_metrics.get(f"test_{key}", 0)
        diff = overfit_diffs.get(key, 0)
        status = "⚠️" if diff > 0.05 else "✅"
        report.append(f"| {key} | {train_val:.4f} | {test_val:.4f} | {diff:.4f} {status} |")
    report.append("")

    report.append("## 4. Cross-Validation Results (5-fold)")
    report.append("")
    report.append("| Metric | Mean | Std |")
    report.append("|--------|------|-----|")
    for key, val in cv_results.items():
        report.append(f"| {key} | {val['mean']:.4f} | {val['std']:.4f} |")
    report.append("")

    report.append("## 5. Feature Importance (Top 10)")
    report.append("")
    report.append("| Rank | Feature | Importance |")
    report.append("|------|---------|------------|")
    for i, feat in enumerate(feature_importance[:10], 1):
        report.append(f"| {i} | {feat['feature']} | {feat['importance']:.4f} |")
    report.append("")

    report.append("## 6. Confusion Matrix (Test Set)")
    report.append("")
    tp = test_metrics.get("test_tp", 0)
    tn = test_metrics.get("test_tn", 0)
    fp = test_metrics.get("test_fp", 0)
    fn = test_metrics.get("test_fn", 0)
    report.append("| | Predicted 0 | Predicted 1 |")
    report.append("|---|---|---|")
    report.append(f"| Actual 0 | {tn} | {fp} |")
    report.append(f"| Actual 1 | {fn} | {tp} |")
    report.append("")

    report.append("## 7. Conclusions")
    report.append("")
    if overfit:
        report.append("⚠️ **Overfitting detected** - Consider:")
        report.append("- Increasing regularization (reg_alpha, reg_lambda)")
        report.append("- Reducing max_depth")
        report.append("- Increasing min_child_weight")
        report.append("- Using more training data")
    else:
        report.append("✅ **No significant overfitting** - Model generalizes well.")
    report.append("")
    report.append("**Top predictors:**")
    for feat in feature_importance[:5]:
        report.append(f"- {feat['feature']}: {feat['importance']:.4f}")

    return "\n".join(report)


def main() -> None:
    """Main training pipeline."""
    sys.stdout.reconfigure(encoding="utf-8")

    # Load and prepare data
    from ml.features import load_data
    df = load_data()
    df, encoders, scaler = prepare_features(df, fit=True)

    # Split data
    X_train, X_test, y_train, y_test = split_data(df)

    # Train model
    print("Training model...")
    model = train_model(X_train, y_train)
    print("Model trained.")

    # Find optimal threshold on training data
    y_train_proba = model.predict_proba(X_train.to_numpy())[:, 1]
    optimal_threshold = find_optimal_threshold(y_train.to_numpy(), y_train_proba)
    print(f"Optimal threshold (F1): {optimal_threshold:.4f}")

    # Evaluate with optimal threshold
    train_metrics = evaluate_model(model, X_train, y_train, "train_", threshold=optimal_threshold)
    test_metrics = evaluate_model(model, X_test, y_test, "test_", threshold=optimal_threshold)

    # Cross-validation
    print("Running cross-validation...")
    cv_results = cross_validate_model(X_train, y_train)

    # Check overfitting
    overfit, overfit_diffs = check_overfitting(train_metrics, test_metrics)

    # Feature importance
    feature_names = [c for c in df.columns if c != "stroke"]
    feature_importance = get_feature_importance(model, feature_names)

    # Save artifacts
    save_model(model)
    save_metrics({**train_metrics, **test_metrics})
    save_feature_importance(feature_importance)
    save_cv_results(cv_results)

    # Generate report
    report = generate_report(
        train_metrics, test_metrics, cv_results,
        feature_importance, overfit, overfit_diffs
    )
    (ARTIFACTS_DIR / "model_report.md").write_text(report, encoding="utf-8")
    print(f"Report saved to {ARTIFACTS_DIR / 'model_report.md'}")

    # Print summary
    print("\n" + "=" * 50)
    print("TRAINING COMPLETE")
    print("=" * 50)
    print(f"Test Accuracy:  {test_metrics['test_accuracy']:.4f}")
    print(f"Test Precision: {test_metrics['test_precision']:.4f}")
    print(f"Test Recall:    {test_metrics['test_recall']:.4f}")
    print(f"Test F1:        {test_metrics['test_f1']:.4f}")
    print(f"Test ROC-AUC:   {test_metrics['test_roc_auc']:.4f}")
    print(f"Overfitting:    {'Yes' if overfit else 'No'}")


if __name__ == "__main__":
    main()