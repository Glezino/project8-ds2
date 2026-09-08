## Context

The project is a stroke prediction ML pipeline. The dataset (`stroke_dataset.csv`, 4981 rows, 11 columns) has been placed at the project root but no analysis has been done. The `backend/ml/` module is scaffolded (artifacts/, features/, inference/, training/, utils/) but empty. This EDA is the first real ML code in the project.

The ML boundary test (`test_ml_boundary.py`) AST-parses all `*.py` files under `backend/ml/` and forbids imports from `fastapi`, `app.api`, and `app.main`. The EDA script must respect this boundary.

## Goals / Non-Goals

**Goals:**
- Produce a single, reproducible Python script that loads the dataset, analyzes it end-to-end, and saves all outputs.
- Document data quality issues (Unknown smoking status, children work type) as findings, not fix them — EDA is about understanding, not cleaning.
- Generate publication-quality visualizations saved as `.png` files.
- Generate structured statistics saved as `.csv` files.
- Generate a human-readable EDA report as a markdown file.
- Follow existing project conventions (Polars for data, project folder structure).

**Non-Goals:**
- Feature engineering or data transformation — that's a future change.
- Model training or evaluation — that's a future change.
- Interactive exploration (no notebooks, no ipython).
- Imputation or handling of the "Unknown" smoking status — document only.
- Unit tests for the EDA script — outputs are visual/analytical artifacts validated by inspection.

## Decisions

### 1. Single script, not a module

**Decision**: One file `backend/ml/eda/eda.py` with clearly separated sections (load, structure, quality, univariate, bivariate, target, visualizations, report).

**Alternatives considered**:
- Multiple modules (e.g., `quality.py`, `visualizations.py`): Over-engineered for EDA. The script is meant to be run once and produce all outputs. Modularity adds complexity without value at this stage.
- Jupyter notebook: User explicitly rejected — GitHub rendering issues, merge conflicts, hard to version control.

**Rationale**: EDA is inherently exploratory and linear. A single script with section headers is the simplest reproducible format. If it grows beyond ~500 lines, it can be refactored then.

### 2. Data location: `backend/ml/data/`

**Decision**: Move `stroke_dataset.csv` from project root to `backend/ml/data/stroke_dataset.csv`.

**Alternatives considered**:
- Keep at project root: Clutters the root. The `.gitignore` already excludes `data/` and `*.csv`, suggesting `data/` was intended as the canonical location.
- `data/` at project root: Too generic — doesn't communicate that this data belongs to the ML pipeline.

**Rationale**: `backend/ml/data/` is parallel to `backend/ml/artifacts/`, follows the existing folder convention, and keeps ML-related assets together.

### 3. Output location: `backend/ml/eda/outputs/`

**Decision**: All generated artifacts (figures, stats, report) go to `backend/ml/eda/outputs/`, gitignored.

**Structure**:
```
backend/ml/eda/outputs/
├── figures/
│   ├── 01_target_distribution.png
│   ├── 02_numerical_distributions.png
│   ├── 03_categorical_distributions.png
│   ├── 04_correlation_heatmap.png
│   ├── 05_age_vs_stroke.png
│   ├── 06_glucose_vs_stroke.png
│   ├── 07_bmi_vs_stroke.png
│   ├── 08_numerical_by_target.png
│   └── 09_categorical_by_target.png
├── statistics/
│   ├── descriptive_numerical.csv
│   ├── descriptive_categorical.csv
│   ├── target_distribution.csv
│   ├── class_imbalance.csv
│   └── correlation_matrix.csv
└── eda_report.md
```

**Rationale**: Separates source code from generated artifacts. Gitignore keeps the repo clean. Numbering on figures provides natural ordering for the report.

### 4. Polars for analysis, Pandas bridge for plotting

**Decision**: Load and analyze data with Polars. Convert to Pandas only when passing data to Seaborn/Matplotlib for plotting (via `.to_pandas()`).

**Alternatives considered**:
- Pandas throughout: Conflicts with project stack declaration (Polars is the declared DataFrame library).
- Polars-only plotting: Polars has limited native plotting. Seaborn is the declared visualization library and requires Pandas/numpy arrays.

**Rationale**: This is the standard pattern when using Polars with Seaborn. The conversion is a one-liner and happens only at the plotting boundary.

### 5. Figure generation approach

**Decision**: Use Seaborn for statistical plots (distributions, boxplots, heatmaps), Matplotlib for layout/saving. Each figure is a standalone function that receives the DataFrame and saves the result.

**Rationale**: Seaborn handles the statistical complexity; Matplotlib handles the file I/O. Functions are composable and testable independently if needed later.

### 6. EDA report format

**Decision**: Generate `eda_report.md` — a structured markdown file that references the saved figures and statistics. The script writes it programmatically (not hand-edited).

**Rationale**: Markdown is readable in GitHub, diffable, and can be referenced in future design docs. Programmatic generation ensures the report always matches the actual analysis.

## Risks / Trade-offs

- **[Risk] Seaborn/Matplotlib rendering differences across OS** → Mitigation: Use `sns.set_theme(style="whitegrid")` consistently and save at fixed DPI (150). Figures are analytical, not pixel-perfect.
- **[Risk] Script takes too long to run** → Mitigation: Dataset is small (4981 rows). No performance optimization needed. If it grows, Polars handles scale well.
- **[Risk] "Unknown" smoking status misinterpreted** → Mitigation: The report explicitly documents this as missing data, not a real category. No imputation during EDA.
- **[Trade-off] No unit tests** → Accepted. EDA outputs are validated by human inspection. The script itself is the test — if it runs without errors and produces sensible outputs, it's correct.
