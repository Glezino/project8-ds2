# Model Performance Report — Stroke Prediction

## 1. Training Metrics

| Metric | Value |
|--------|-------|
| accuracy | 0.8999 |
| precision | 0.2597 |
| recall | 0.4061 |
| f1 | 0.3168 |
| roc_auc | 0.8470 |

## 2. Test Metrics

| Metric | Value |
|--------|-------|
| accuracy | 0.8956 |
| precision | 0.1940 |
| recall | 0.2653 |
| f1 | 0.2241 |
| roc_auc | 0.8178 |

## 3. Overfitting Analysis

**Threshold:** 5 percentage points (0.05)
**Overfitting Detected:** Yes ⚠️

| Metric | Train | Test | Difference |
|--------|-------|------|------------|
| accuracy | 0.8999 | 0.8956 | 0.0043 ✅ |
| precision | 0.2597 | 0.1940 | 0.0657 ⚠️ |
| recall | 0.4061 | 0.2653 | 0.1408 ⚠️ |
| f1 | 0.3168 | 0.2241 | 0.0927 ⚠️ |
| roc_auc | 0.8470 | 0.8178 | 0.0292 ✅ |

## 4. Cross-Validation Results (5-fold)

| Metric | Mean | Std |
|--------|------|-----|
| accuracy | 0.6669 | 0.0219 |
| precision | 0.1295 | 0.0045 |
| recall | 0.8427 | 0.0585 |
| f1 | 0.2244 | 0.0077 |
| roc_auc | 0.8220 | 0.0327 |

## 5. Feature Importance (Top 10)

| Rank | Feature | Importance |
|------|---------|------------|
| 1 | age | 0.3207 |
| 2 | ever_married | 0.1698 |
| 3 | hypertension | 0.1140 |
| 4 | avg_glucose_level | 0.0886 |
| 5 | smoking_status | 0.0616 |
| 6 | bmi | 0.0611 |
| 7 | work_type | 0.0521 |
| 8 | heart_disease | 0.0513 |
| 9 | gender | 0.0457 |
| 10 | Residence_type | 0.0350 |

## 6. Confusion Matrix (Test Set)

| | Predicted 0 | Predicted 1 |
|---|---|---|
| Actual 0 | 759 | 54 |
| Actual 1 | 36 | 13 |

## 7. Conclusions

⚠️ **Overfitting detected** - Consider:
- Increasing regularization (reg_alpha, reg_lambda)
- Reducing max_depth
- Increasing min_child_weight
- Using more training data

**Top predictors:**
- age: 0.3207
- ever_married: 0.1698
- hypertension: 0.1140
- avg_glucose_level: 0.0886
- smoking_status: 0.0616