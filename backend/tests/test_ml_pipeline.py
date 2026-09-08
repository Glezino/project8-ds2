"""
Tests for ML Pipeline
"""

import json
from pathlib import Path

import joblib
import numpy as np
import polars as pl
import pytest

from ml.features import (
    ARTIFACTS_DIR,
    CATEGORICAL_COLS,
    NUMERICAL_COLS,
    TARGET_COL,
    clean_data,
    encode_categorical,
    load_data,
    prepare_features,
    scale_numerical,
    split_data,
)
from ml.inference import predict, validate_input


class TestDataLoading:
    def test_load_data(self):
        df = load_data()
        assert df.height == 4981
        assert df.width == 11
        assert "stroke" in df.columns
        assert TARGET_COL in df.columns


class TestDataCleaning:
    def test_clean_data_removes_children(self):
        df = load_data()
        initial_rows = df.height
        df_clean = clean_data(df)
        assert df_clean.height < initial_rows
        assert "children" not in df_clean["work_type"].unique()

    def test_clean_data_handles_unknown_smoking(self):
        df = load_data()
        df_clean = clean_data(df)
        assert "Unknown" not in df_clean["smoking_status"].unique()

    def test_clean_data_drops_id(self):
        df = load_data()
        df_clean = clean_data(df)
        assert "id" not in df_clean.columns


class TestEncoding:
    def test_encode_categorical_fit(self):
        df = load_data()
        df_clean = clean_data(df)
        df_encoded, encoders = encode_categorical(df_clean, fit=True)
        
        for col in CATEGORICAL_COLS:
            assert col in encoders
            # Check all values are numeric
            assert df_encoded[col].dtype in [pl.Int64, pl.Int32]

    def test_encode_categorical_transform(self):
        df = load_data()
        df_clean = clean_data(df)
        df_encoded, encoders = encode_categorical(df_clean, fit=True)
        df_encoded2, _ = encode_categorical(df_clean, encoders, fit=False)
        
        assert df_encoded.equals(df_encoded2)


class TestScaling:
    def test_scale_numerical_fit(self):
        df = load_data()
        df_clean = clean_data(df)
        df_scaled, scaler = scale_numerical(df_clean, fit=True)
        
        for col in NUMERICAL_COLS:
            # Check mean ~0, std ~1
            mean = df_scaled[col].mean()
            std = df_scaled[col].std()
            assert abs(mean) < 0.1
            assert abs(std - 1.0) < 0.1

    def test_scale_numerical_transform(self):
        df = load_data()
        df_clean = clean_data(df)
        df_scaled, scaler = scale_numerical(df_clean, fit=True)
        df_scaled2, _ = scale_numerical(df_clean, scaler, fit=False)
        
        assert df_scaled.equals(df_scaled2)


class TestFeaturePreparation:
    def test_prepare_features(self):
        df = load_data()
        df_prepared, encoders, scaler = prepare_features(df, fit=True)
        
        # Check all columns are numeric
        for col in df_prepared.columns:
            assert df_prepared[col].dtype in [pl.Int64, pl.Int32, pl.Float64, pl.Float32]
        
        # Check target is preserved
        assert TARGET_COL in df_prepared.columns

    def test_prepare_features_returns_correct_shape(self):
        df = load_data()
        df_prepared, _, _ = prepare_features(df, fit=True)
        
        # After cleaning: removed children (673 rows) = 4308 rows
        assert df_prepared.height == 4308
        # Features: 10 original + target = 11 columns
        assert df_prepared.width == 11


class TestDataSplit:
    def test_split_data_stratified(self):
        df = load_data()
        df_prepared, _, _ = prepare_features(df, fit=True)
        
        X_train, X_test, y_train, y_test = split_data(df_prepared)
        
        assert X_train.height == 3446
        assert X_test.height == 862
        assert len(y_train) == 3446
        assert len(y_test) == 862
        
        # Check stratification - both should have similar class ratios
        train_ratio = (y_train == 1).sum() / len(y_train)
        test_ratio = (y_test == 1).sum() / len(y_test)
        assert abs(train_ratio - test_ratio) < 0.02


class TestInference:
    def test_validate_input_valid(self):
        data = {
            "gender": "Male",
            "age": 65,
            "hypertension": 1,
            "heart_disease": 0,
            "ever_married": "Yes",
            "work_type": "Private",
            "Residence_type": "Urban",
            "avg_glucose_level": 120,
            "bmi": 28,
            "smoking_status": "formerly smoked",
        }
        valid, msg = validate_input(data)
        assert valid
        assert msg == "Valid"

    def test_validate_input_missing_field(self):
        data = {
            "gender": "Male",
            "age": 65,
            # missing hypertension
        }
        valid, msg = validate_input(data)
        assert not valid
        assert "Missing required field" in msg

    def test_validate_input_invalid_value(self):
        data = {
            "gender": "Invalid",
            "age": 65,
            "hypertension": 1,
            "heart_disease": 0,
            "ever_married": "Yes",
            "work_type": "Private",
            "Residence_type": "Urban",
            "avg_glucose_level": 120,
            "bmi": 28,
            "smoking_status": "formerly smoked",
        }
        valid, msg = validate_input(data)
        assert not valid
        assert "Invalid value" in msg

    def test_predict_returns_dict(self):
        data = {
            "gender": "Male",
            "age": 65,
            "hypertension": 1,
            "heart_disease": 0,
            "ever_married": "Yes",
            "work_type": "Private",
            "Residence_type": "Urban",
            "avg_glucose_level": 120,
            "bmi": 28,
            "smoking_status": "formerly smoked",
        }
        result = predict(data)
        
        assert isinstance(result, dict)
        assert "stroke_risk" in result
        assert "probability" in result
        assert "threshold" in result
        assert "risk_level" in result
        assert isinstance(result["stroke_risk"], bool)
        assert 0 <= result["probability"] <= 1
        assert result["risk_level"] in ["HIGH", "LOW"]

    def test_predict_high_risk_patient(self):
        data = {
            "gender": "Male",
            "age": 75,
            "hypertension": 1,
            "heart_disease": 1,
            "ever_married": "Yes",
            "work_type": "Private",
            "Residence_type": "Urban",
            "avg_glucose_level": 200,
            "bmi": 32,
            "smoking_status": "smokes",
        }
        result = predict(data)
        # High risk patient should have high probability
        assert result["probability"] > 0.5

    def test_predict_low_risk_patient(self):
        data = {
            "gender": "Female",
            "age": 30,
            "hypertension": 0,
            "heart_disease": 0,
            "ever_married": "No",
            "work_type": "Private",
            "Residence_type": "Rural",
            "avg_glucose_level": 85,
            "bmi": 22,
            "smoking_status": "never smoked",
        }
        result = predict(data)
        # Low risk patient should have low probability
        assert result["probability"] < 0.5


class TestModelArtifacts:
    def test_model_exists(self):
        assert (ARTIFACTS_DIR / "model.joblib").exists()

    def test_encoders_exist(self):
        assert (ARTIFACTS_DIR / "encoders.joblib").exists()

    def test_scaler_exists(self):
        assert (ARTIFACTS_DIR / "scaler.joblib").exists()

    def test_feature_names_exist(self):
        assert (ARTIFACTS_DIR / "feature_names.json").exists()

    def test_metrics_exist(self):
        assert (ARTIFACTS_DIR / "metrics.json").exists()

    def test_feature_importance_exists(self):
        assert (ARTIFACTS_DIR / "feature_importance.json").exists()

    def test_model_can_load_and_predict(self):
        model = joblib.load(ARTIFACTS_DIR / "model.joblib")
        assert model is not None
        
        # Test prediction
        X_test = np.random.rand(1, 10)
        proba = model.predict_proba(X_test)[0, 1]
        assert 0 <= proba <= 1


class TestMetrics:
    def test_metrics_structure(self):
        with open(ARTIFACTS_DIR / "metrics.json") as f:
            metrics = json.load(f)
        
        required_keys = [
            "train_accuracy", "train_precision", "train_recall", "train_f1", "train_roc_auc",
            "test_accuracy", "test_precision", "test_recall", "test_f1", "test_roc_auc",
            "train_threshold",
        ]
        for key in required_keys:
            assert key in metrics, f"Missing key: {key}"

    def test_overfitting_threshold(self):
        with open(ARTIFACTS_DIR / "metrics.json") as f:
            metrics = json.load(f)
        
        # Check that accuracy difference is within 5%
        acc_diff = metrics["train_accuracy"] - metrics["test_accuracy"]
        assert acc_diff < 0.05, f"Accuracy overfitting: {acc_diff:.4f} > 0.05"
        
        # Check ROC-AUC difference is within 5%
        auc_diff = metrics["train_roc_auc"] - metrics["test_roc_auc"]
        assert auc_diff < 0.05, f"ROC-AUC overfitting: {auc_diff:.4f} > 0.05"

    def test_feature_importance_structure(self):
        with open(ARTIFACTS_DIR / "feature_importance.json") as f:
            importance = json.load(f)
        
        assert isinstance(importance, list)
        assert len(importance) == 10
        for item in importance:
            assert "feature" in item
            assert "importance" in item
            assert isinstance(item["importance"], (int, float))
            assert item["importance"] >= 0
        
        # Check sorted descending
        importances = [item["importance"] for item in importance]
        assert importances == sorted(importances, reverse=True)


class TestEDAOutputs:
    def test_eda_report_exists(self):
        assert (Path(__file__).parent.parent / "ml/eda/outputs/eda_report.md").exists()

    def test_eda_figures_exist(self):
        fig_dir = Path(__file__).parent.parent / "ml/eda/outputs/figures"
        expected_figures = [
            "01_target_distribution.png",
            "02_numerical_distributions.png",
            "03_categorical_distributions.png",
            "04_correlation_heatmap.png",
            "05_age_vs_stroke.png",
            "06_glucose_vs_stroke.png",
            "07_bmi_vs_stroke.png",
            "08_numerical_by_target.png",
            "09_categorical_by_target.png",
        ]
        for fig in expected_figures:
            assert (fig_dir / fig).exists(), f"Missing figure: {fig}"

    def test_eda_statistics_exist(self):
        stat_dir = Path(__file__).parent.parent / "ml/eda/outputs/statistics"
        expected_stats = [
            "descriptive_numerical.csv",
            "descriptive_categorical.csv",
            "target_distribution.csv",
            "class_imbalance.csv",
            "correlation_matrix.csv",
        ]
        for stat in expected_stats:
            assert (stat_dir / stat).exists(), f"Missing statistic: {stat}"


class TestModelReport:
    def test_model_report_exists(self):
        assert (ARTIFACTS_DIR / "model_report.md").exists()

    def test_model_report_content(self):
        report = (ARTIFACTS_DIR / "model_report.md").read_text(encoding="utf-8")
        assert "Model Performance Report" in report
        assert "Training Metrics" in report
        assert "Test Metrics" in report
        assert "Overfitting Analysis" in report
        assert "Cross-Validation Results" in report
        assert "Feature Importance" in report
        assert "Confusion Matrix" in report
        assert "Conclusions" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])