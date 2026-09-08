## Why

The project has a stroke prediction dataset (`stroke_dataset.csv`, 4981 rows, 11 columns) but no exploratory data analysis has been performed. Before building any ML pipeline (feature engineering, training, inference), we need to understand the data's structure, quality, distributions, and class imbalance. EDA is the foundational step that informs every downstream ML decision — which features matter, how to handle missing values, whether to resample, and which models are appropriate.

## What Changes

- Create a reproducible EDA script (`backend/ml/eda/eda.py`) using Polars for data manipulation and Seaborn/Matplotlib for visualization.
- Generate and save all analytical outputs to `backend/ml/eda/outputs/`:
  - **Descriptive statistics**: summary stats for numerical and categorical variables, split by target class.
  - **Data quality analysis**: missing values, duplicates, "Unknown" smoking status (~30% of rows), "children" work type quirk.
  - **Visualizations**: distributions, correlations, class imbalance, target relationships — saved as `.png` files.
  - **EDA report**: a structured text/markdown summary of all findings.
- Dataset moved to `backend/ml/data/stroke_dataset.csv` (canonical location within the ML module).
- Add `backend/ml/eda/outputs/` to `.gitignore` (generated artifacts, not source).

## Capabilities

### New Capabilities

None — this is a pure analysis task. No system behavior changes. `skip_specs: true` is set in `.openspec.yaml`.

### Modified Capabilities

None.

## Impact

- **New files**: `backend/ml/eda/eda.py`, `backend/ml/eda/outputs/` (figures, stats, report), `backend/ml/data/stroke_dataset.csv`.
- **Modified files**: `.gitignore` (add `backend/ml/eda/outputs/`).
- **Dependencies**: No new dependencies — Polars, Seaborn, and Matplotlib are already declared in `pyproject.toml`.
- **No API, database, or frontend changes.**
