## 1. Setup and Data Placement

- [x] 1.1 Create `backend/ml/data/` and `backend/ml/eda/` directories. Move `stroke_dataset.csv` from project root to `backend/ml/data/stroke_dataset.csv`. Verify the file exists at the new location and the original is removed.
- [x] 1.2 Add `backend/ml/eda/outputs/` to `.gitignore`. Verify with `git status` that the pattern is recognized (no untracked outputs folder).

## 2. EDA Script — Data Loading and Structure

- [x] 2.1 Create `backend/ml/eda/eda.py` with Polars import and CSV loading from `backend/ml/data/stroke_dataset.csv`. Print shape and schema. Verify script runs without errors: `python backend/ml/eda/eda.py` (partial — will fail at later sections until they exist, so wrap unimplemented sections in `if False:` or guard with try/except initially).

## 3. EDA Script — Data Quality Analysis

- [x] 3.1 Add missing values analysis: count nulls per column, print summary. Add duplicate analysis: count exact duplicate rows. Add "Unknown" smoking status analysis: count rows where `smoking_status == "Unknown"`, calculate percentage. Verify output printed to stdout with correct counts (0 nulls, 0 duplicates, ~1500 Unknown smoking rows).

## 4. EDA Script — Numerical Variable Analysis

- [x] 4.1 Add descriptive statistics for numerical columns (`age`, `avg_glucose_level`, `bmi`, `hypertension`, `heart_disease`): mean, std, min, max, quartiles. Split by target class (`stroke` == 0 vs 1). Save to `backend/ml/eda/outputs/statistics/descriptive_numerical.csv`. Verify CSV exists and contains expected columns and rows.

## 5. EDA Script — Categorical Variable Analysis

- [x] 5.1 Add value counts for categorical columns (`gender`, `ever_married`, `work_type`, `Residence_type`, `smoking_status`). Save to `backend/ml/eda/outputs/statistics/descriptive_categorical.csv`. Verify CSV exists with correct category counts.

## 6. EDA Script — Target and Class Imbalance

- [x] 6.1 Add target variable (`stroke`) distribution analysis: count and percentage for each class. Calculate imbalance ratio. Save to `backend/ml/eda/outputs/statistics/target_distribution.csv` and `class_imbalance.csv`. Verify CSVs exist and show ~95%/5% split.

## 7. EDA Script — Correlation Analysis

- [x] 7.1 Add correlation matrix for numerical features. Save to `backend/ml/eda/outputs/statistics/correlation_matrix.csv`. Verify CSV exists with pairwise correlations.

## 8. EDA Script — Visualizations

- [x] 8.1 Add visualization functions using Seaborn/Matplotlib. Generate and save all 9 figures: target distribution (bar), numerical distributions (histograms), categorical distributions (countplots), correlation heatmap, age vs stroke (boxplot), glucose vs stroke (boxplot), bmi vs stroke (boxplot), numerical distributions by target (paired histograms), categorical proportions by target (stacked/grouped barplots). Verify all 9 PNG files exist in `backend/ml/eda/outputs/figures/` and are non-empty.

## 9. EDA Script — Report Generation

- [x] 9.1 Add markdown report generation: write `backend/ml/eda/outputs/eda_report.md` with structured sections referencing all statistics and figures. Verify the report is valid markdown, contains all section headers, and references all generated figures/stats.

## 10. End-to-End Verification

- [x] 10.1 Run `python backend/ml/eda/eda.py` end-to-end. Verify all outputs are generated without errors: 9 figures, 5 statistics CSVs, 1 report. Run `make test` to confirm `test_ml_boundary.py` still passes (EDA script has no forbidden imports). Run `make lint` to confirm no lint errors.
