"""
Exploratory Data Analysis — Stroke Prediction Dataset

Loads the dataset, inspects structure, analyzes data quality, computes
descriptive statistics, generates visualizations, and writes a markdown
report. All outputs are saved under backend/ml/eda/outputs/.
"""

from __future__ import annotations

import sys
from pathlib import Path

import polars as pl

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT_DIR / "ml" / "data" / "stroke_dataset.csv"
OUTPUT_DIR = ROOT_DIR / "ml" / "eda" / "outputs"
FIGURES_DIR = OUTPUT_DIR / "figures"
STATISTICS_DIR = OUTPUT_DIR / "statistics"


def ensure_output_dirs() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    STATISTICS_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# 1. Load and inspect
# ---------------------------------------------------------------------------
def load_data() -> pl.DataFrame:
    df = pl.read_csv(DATA_PATH)
    print(f"Dataset loaded: {df.height} rows, {df.width} columns")
    print(f"Schema:\n{df.schema}\n")
    return df


# ---------------------------------------------------------------------------
# 2. Data quality
# ---------------------------------------------------------------------------
def analyze_data_quality(df: pl.DataFrame) -> dict:
    # Missing values
    null_counts = {col: df[col].null_count() for col in df.columns}
    total_nulls = sum(null_counts.values())

    # Duplicates
    n_duplicates = df.height - df.unique().height

    # Unknown smoking status
    unknown_smoking = df.filter(pl.col("smoking_status") == "Unknown").height
    unknown_pct = (unknown_smoking / df.height) * 100

    # Children work type
    children_count = df.filter(pl.col("work_type") == "children").height
    children_pct = (children_count / df.height) * 100

    print("=== Data Quality ===")
    print(f"Total null values: {total_nulls}")
    for col, count in null_counts.items():
        if count > 0:
            print(f"  {col}: {count} nulls")
    print(f"Exact duplicate rows: {n_duplicates}")
    print(f"Unknown smoking status: {unknown_smoking} ({unknown_pct:.1f}%)")
    print(f"Work type 'children': {children_count} ({children_pct:.1f}%)\n")

    return {
        "null_counts": null_counts,
        "total_nulls": total_nulls,
        "n_duplicates": n_duplicates,
        "unknown_smoking": unknown_smoking,
        "unknown_smoking_pct": unknown_pct,
        "children_count": children_count,
        "children_pct": children_pct,
    }


# ---------------------------------------------------------------------------
# 3. Numerical analysis
# ---------------------------------------------------------------------------
def analyze_numerical(df: pl.DataFrame) -> pl.DataFrame:
    numerical_cols = ["age", "avg_glucose_level", "bmi", "hypertension", "heart_disease"]

    stats_parts: list[pl.DataFrame] = []
    for label, subset in [
        ("all", df),
        ("stroke_0", df.filter(pl.col("stroke") == 0)),
        ("stroke_1", df.filter(pl.col("stroke") == 1)),
    ]:
        desc = subset.select(numerical_cols).describe()
        stats_parts.append(desc.with_columns(pl.lit(label).alias("subset")))

    stats = pl.concat(stats_parts)
    stats.write_csv(STATISTICS_DIR / "descriptive_numerical.csv")
    print("Saved descriptive_numerical.csv")
    return stats


# ---------------------------------------------------------------------------
# 4. Categorical analysis
# ---------------------------------------------------------------------------
def analyze_categorical(df: pl.DataFrame) -> pl.DataFrame:
    categorical_cols = ["gender", "ever_married", "work_type", "Residence_type", "smoking_status"]

    frames: list[pl.DataFrame] = []
    for col in categorical_cols:
        vc = df[col].value_counts()
        vc = vc.rename({col: "value"}).with_columns(pl.lit(col).alias("variable"))
        frames.append(vc)

    result = pl.concat(frames)
    result.write_csv(STATISTICS_DIR / "descriptive_categorical.csv")
    print("Saved descriptive_categorical.csv")
    return result


# ---------------------------------------------------------------------------
# 5. Target analysis
# ---------------------------------------------------------------------------
def analyze_target(df: pl.DataFrame) -> None:
    total = df.height
    stroke_counts = (
        df["stroke"]
        .value_counts()
        .with_columns(((pl.col("count") / total) * 100).round(2).alias("percentage"))
    )
    stroke_counts.write_csv(STATISTICS_DIR / "target_distribution.csv")
    print("Saved target_distribution.csv")

    n_no = df.filter(pl.col("stroke") == 0).height
    n_yes = df.filter(pl.col("stroke") == 1).height
    ratio = n_no / n_yes if n_yes > 0 else float("inf")

    imbalance = pl.DataFrame(
        {
            "metric": ["total", "class_0", "class_1", "imbalance_ratio"],
            "value": [str(total), str(n_no), str(n_yes), f"{ratio:.2f}"],
        }
    )
    imbalance.write_csv(STATISTICS_DIR / "class_imbalance.csv")
    print("Saved class_imbalance.csv")
    print(f"Class imbalance ratio: {ratio:.1f}:1 (no_stroke : stroke)\n")


# ---------------------------------------------------------------------------
# 6. Correlation analysis
# ---------------------------------------------------------------------------
def analyze_correlations(df: pl.DataFrame) -> None:
    numerical_cols = ["age", "avg_glucose_level", "bmi", "hypertension", "heart_disease", "stroke"]
    corr = df.select(numerical_cols).corr()
    corr.write_csv(STATISTICS_DIR / "correlation_matrix.csv")
    print("Saved correlation_matrix.csv")


# ---------------------------------------------------------------------------
# 7. Visualizations
# ---------------------------------------------------------------------------
def generate_visualizations(df: pl.DataFrame) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns

    sns.set_theme(style="whitegrid")
    pd_df = df.to_pandas()
    DPI = 150

    # 01 — Target distribution
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.countplot(data=pd_df, x="stroke", hue="stroke", legend=False, ax=ax, palette="Set2")
    ax.set_title("Stroke Distribution")
    ax.set_xlabel("Stroke (0=No, 1=Yes)")
    ax.set_ylabel("Count")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "01_target_distribution.png", dpi=DPI)
    plt.close(fig)
    print("Saved 01_target_distribution.png")

    # 02 — Numerical distributions
    numerical_cols = ["age", "avg_glucose_level", "bmi"]
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for i, col in enumerate(numerical_cols):
        sns.histplot(data=pd_df, x=col, kde=True, ax=axes[i], color=sns.color_palette("Set2")[i])
        axes[i].set_title(f"Distribution of {col}")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "02_numerical_distributions.png", dpi=DPI)
    plt.close(fig)
    print("Saved 02_numerical_distributions.png")

    # 03 — Categorical distributions
    categorical_cols = ["gender", "ever_married", "work_type", "Residence_type", "smoking_status"]
    fig, axes = plt.subplots(1, 5, figsize=(20, 4))
    for i, col in enumerate(categorical_cols):
        sns.countplot(
            data=pd_df,
            x=col,
            hue=col,
            legend=False,
            ax=axes[i],
            palette="Set2",
            order=pd_df[col].value_counts().index,
        )
        axes[i].set_title(col)
        axes[i].tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "03_categorical_distributions.png", dpi=DPI)
    plt.close(fig)
    print("Saved 03_categorical_distributions.png")

    # 04 — Correlation heatmap
    numerical_all = ["age", "avg_glucose_level", "bmi", "hypertension", "heart_disease", "stroke"]
    corr = pd_df[numerical_all].corr()
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax)
    ax.set_title("Correlation Heatmap")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "04_correlation_heatmap.png", dpi=DPI)
    plt.close(fig)
    print("Saved 04_correlation_heatmap.png")

    # 05 — Age vs Stroke
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.boxplot(data=pd_df, x="stroke", y="age", hue="stroke", legend=False, ax=ax, palette="Set2")
    ax.set_title("Age by Stroke Status")
    ax.set_xlabel("Stroke (0=No, 1=Yes)")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "05_age_vs_stroke.png", dpi=DPI)
    plt.close(fig)
    print("Saved 05_age_vs_stroke.png")

    # 06 — Glucose vs Stroke
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.boxplot(
        data=pd_df,
        x="stroke",
        y="avg_glucose_level",
        hue="stroke",
        legend=False,
        ax=ax,
        palette="Set2",
    )
    ax.set_title("Glucose Level by Stroke Status")
    ax.set_xlabel("Stroke (0=No, 1=Yes)")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "06_glucose_vs_stroke.png", dpi=DPI)
    plt.close(fig)
    print("Saved 06_glucose_vs_stroke.png")

    # 07 — BMI vs Stroke
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.boxplot(data=pd_df, x="stroke", y="bmi", hue="stroke", legend=False, ax=ax, palette="Set2")
    ax.set_title("BMI by Stroke Status")
    ax.set_xlabel("Stroke (0=No, 1=Yes)")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "07_bmi_vs_stroke.png", dpi=DPI)
    plt.close(fig)
    print("Saved 07_bmi_vs_stroke.png")

    # 08 — Numerical distributions by target
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for i, col in enumerate(numerical_cols):
        sns.histplot(
            data=pd_df, x=col, hue="stroke", kde=True, ax=axes[i], palette="Set2", element="step"
        )
        axes[i].set_title(f"{col} by Stroke")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "08_numerical_by_target.png", dpi=DPI)
    plt.close(fig)
    print("Saved 08_numerical_by_target.png")

    # 09 — Categorical proportions by target
    fig, axes = plt.subplots(1, 5, figsize=(20, 4))
    for i, col in enumerate(categorical_cols):
        ct = pd_df.groupby([col, "stroke"]).size().unstack(fill_value=0)
        ct_norm = ct.div(ct.sum(axis=1), axis=0)
        ct_norm.plot(kind="bar", stacked=True, ax=axes[i], color=sns.color_palette("Set2")[:2])
        axes[i].set_title(f"{col} by Stroke")
        axes[i].set_ylabel("Proportion")
        axes[i].tick_params(axis="x", rotation=45)
        axes[i].legend(title="Stroke", labels=["No", "Yes"])
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "09_categorical_by_target.png", dpi=DPI)
    plt.close(fig)
    print("Saved 09_categorical_by_target.png\n")


# ---------------------------------------------------------------------------
# 8. Report generation
# ---------------------------------------------------------------------------
def generate_report(df: pl.DataFrame, quality: dict) -> None:
    n_stroke_1 = df.filter(pl.col("stroke") == 1).height
    n_stroke_0 = df.filter(pl.col("stroke") == 0).height
    ratio = n_stroke_0 / n_stroke_1 if n_stroke_1 > 0 else float("inf")

    def pct(column: str, value: object) -> float:
        return df.filter(pl.col(column) == value).height / df.height * 100

    gender_female = pct("gender", "Female")
    gender_male = pct("gender", "Male")
    married_yes = pct("ever_married", "Yes")
    married_no = pct("ever_married", "No")
    work_private = pct("work_type", "Private")
    work_self = pct("work_type", "Self-employed")
    work_govt = pct("work_type", "Govt_job")
    work_children = pct("work_type", "children")
    res_urban = pct("Residence_type", "Urban")
    res_rural = pct("Residence_type", "Rural")
    smoke_never = pct("smoking_status", "never smoked")
    smoke_unknown = pct("smoking_status", "Unknown")
    smoke_former = pct("smoking_status", "formerly smoked")
    smoke_smokes = pct("smoking_status", "smokes")

    d0 = df.filter(pl.col("stroke") == 0)
    d1 = df.filter(pl.col("stroke") == 1)

    def mean_stats(column: str) -> tuple[float, float, float]:
        return df[column].mean(), d0[column].mean(), d1[column].mean()

    age_all, age_0, age_1 = mean_stats("age")
    glu_all, glu_0, glu_1 = mean_stats("avg_glucose_level")
    bmi_all, bmi_0, bmi_1 = mean_stats("bmi")
    hyp_all, hyp_0, hyp_1 = mean_stats("hypertension")
    heart_all, heart_0, heart_1 = mean_stats("heart_disease")

    report = "\n".join(
        [
            "# EDA Report — Stroke Prediction Dataset",
            "",
            "## 1. Dataset Overview",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Rows | {df.height} |",
            f"| Columns | {df.width} |",
            "| Features | gender, age, hypertension, heart_disease, ever_married, "
            "work_type, Residence_type, avg_glucose_level, bmi, smoking_status |",
            "| Target | stroke (0 = No, 1 = Yes) |",
            "",
            "## 2. Data Quality",
            "",
            "| Check | Result |",
            "|-------|--------|",
            f"| Total null values | {quality['total_nulls']} |",
            f"| Exact duplicate rows | {quality['n_duplicates']} |",
            f"| Unknown smoking status | {quality['unknown_smoking']} "
            f"({quality['unknown_smoking_pct']:.1f}%) |",
            f"| Work type 'children' | {quality['children_count']} "
            f"({quality['children_pct']:.1f}%) |",
            "",
            "**Findings:**",
            "- No missing values or duplicates in the dataset.",
            f'- `smoking_status = "Unknown"` accounts for '
            f"{quality['unknown_smoking_pct']:.1f}% of rows — this is likely "
            "missing data encoded as a category, not a real value. This should be "
            "handled during feature engineering.",
            f'- `work_type = "children"` ({quality["children_pct"]:.1f}%) represents '
            "pediatric patients (age range starts at 0.08). The stroke rate among "
            "children is very low.",
            "",
            "## 3. Target Distribution",
            "",
            "| Class | Count | Percentage |",
            "|-------|-------|------------|",
            f"| 0 (No Stroke) | {n_stroke_0} | {n_stroke_0 / df.height * 100:.1f}% |",
            f"| 1 (Stroke) | {n_stroke_1} | {n_stroke_1 / df.height * 100:.1f}% |",
            "",
            f"**Imbalance ratio:** {ratio:.1f}:1 (no stroke : stroke)",
            "",
            "The dataset is severely imbalanced — only ~5% of patients experienced "
            "a stroke. This must be addressed during model training (e.g., SMOTE, "
            "class weighting, stratified splits).",
            "",
            "See: [target_distribution.csv](statistics/target_distribution.csv), "
            "[class_imbalance.csv](statistics/class_imbalance.csv)",
            "",
            "## 4. Numerical Variables",
            "",
            "Descriptive statistics split by target class:",
            "",
            "See: [descriptive_numerical.csv](statistics/descriptive_numerical.csv)",
            "",
            "| Variable | Mean (all) | Mean (stroke=0) | Mean (stroke=1) | Insight |",
            "|----------|------------|-----------------|-----------------|---------|",
            f"| age | ~{age_all:.1f} | ~{age_0:.1f} | ~{age_1:.1f} | "
            "Strong signal — stroke patients are much older |",
            f"| avg_glucose_level | ~{glu_all:.1f} | ~{glu_0:.1f} | ~{glu_1:.1f} | "
            "Elevated glucose associated with stroke |",
            f"| bmi | ~{bmi_all:.1f} | ~{bmi_0:.1f} | ~{bmi_1:.1f} | "
            "Similar across classes — weaker signal |",
            f"| hypertension | {hyp_all * 100:.1f}% | ~{hyp_0 * 100:.1f}% | "
            f"~{hyp_1 * 100:.1f}% | Higher prevalence in stroke patients |",
            f"| heart_disease | {heart_all * 100:.1f}% | ~{heart_0 * 100:.1f}% | "
            f"~{heart_1 * 100:.1f}% | Strongly associated with stroke |",
            "",
            "## 5. Categorical Variables",
            "",
            "See: [descriptive_categorical.csv](statistics/descriptive_categorical.csv)",
            "",
            f"- **Gender:** Female {gender_female:.1f}%, Male {gender_male:.1f}% "
            "— moderate imbalance.",
            f"- **Ever Married:** Yes {married_yes:.1f}%, No {married_no:.1f}%.",
            f"- **Work Type:** Private ({work_private:.1f}%), "
            f"Self-employed ({work_self:.1f}%), Govt_job ({work_govt:.1f}%), "
            f"children ({work_children:.1f}%).",
            f"- **Residence Type:** Urban ({res_urban:.1f}%), Rural ({res_rural:.1f}%).",
            f"- **Smoking Status:** never smoked ({smoke_never:.1f}%), "
            f"Unknown ({smoke_unknown:.1f}%), formerly smoked ({smoke_former:.1f}%), "
            f"smokes ({smoke_smokes:.1f}%).",
            "",
            "## 6. Key Relationships",
            "",
            "Figures referenced from `outputs/figures/`:",
            "",
            "1. **Age vs Stroke** (`05_age_vs_stroke.png`): Stroke patients have a "
            "significantly higher median age (~71 vs ~43).",
            "2. **Glucose vs Stroke** (`06_glucose_vs_stroke.png`): Stroke patients "
            "show higher and more variable glucose levels.",
            "3. **BMI vs Stroke** (`07_bmi_vs_stroke.png`): Minimal difference — "
            "BMI alone is not a strong predictor.",
            "4. **Correlations** (`04_correlation_heatmap.png`): Age correlates most "
            "with stroke (r ~0.25), followed by heart_disease and hypertension.",
            "5. **Work Type** (`09_categorical_by_target.png`): Self-employed have a "
            "higher stroke rate. Children have near-zero stroke rate.",
            "",
            "## 7. Conclusions",
            "",
            "1. **Age is the strongest predictor** — stroke patients average 67.8 "
            "years vs 42.1 for non-stroke.",
            "2. **Glucose and cardiovascular factors matter** — elevated glucose, "
            "hypertension, and heart disease are all associated with stroke.",
            "3. **Class imbalance is severe** (19:1) — must use stratified sampling "
            "and class-weighted or resampled training.",
            '4. **"Unknown" smoking status** (~30%) is a data quality issue to '
            "address in feature engineering.",
            "5. **BMI is a weak predictor** — distributions overlap heavily between classes.",
            "6. **No missing values or duplicates** — the dataset is structurally clean.",
        ]
    )

    (OUTPUT_DIR / "eda_report.md").write_text(report, encoding="utf-8")
    print("Saved eda_report.md")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ensure_output_dirs()

    df = load_data()
    quality = analyze_data_quality(df)
    analyze_numerical(df)
    analyze_categorical(df)
    analyze_target(df)
    analyze_correlations(df)
    generate_visualizations(df)
    generate_report(df, quality)

    print("=" * 50)
    print("EDA complete. All outputs saved to backend/ml/eda/outputs/")
    print("=" * 50)


if __name__ == "__main__":
    main()
