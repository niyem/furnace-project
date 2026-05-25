"""
phase4b_yis_permutation.py — Permutation importance for the years_in_service model.

Runs grouped 5-fold CV training a Random Forest to predict years_in_service
(= campaign_year − sale_year) from WBT + geometry features. On each held-out
fold, computes permutation importance with 10 repeats. Aggregates mean ± std
importance per feature.

Disambiguates:
  - If WBT-derived features (eff_*, fp_*, br_*, sfc_*, tboil_*) dominate the
    ranking → the model is using functional signals that could plausibly drift
    with wear. Supports the "real degradation" interpretation.
  - If geometry features (height, chamber_*, inlet_*) dominate → geometry
    doesn't change with age, so the model is identifying format×year cohorts.
    Supports the "cohort confound" interpretation.

Inputs:
    data/processed/wbt_wide.csv

Outputs (in outputs/phase4/):
    yis_permutation_importance.csv   per-feature mean ± std across folds, sorted
    yis_permutation_summary.md       formatted markdown
    yis_permutation.log

Run:
    OMP_NUM_THREADS=1 python3 phase4b_yis_permutation.py
"""

from __future__ import annotations

import logging
import re
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

warnings.filterwarnings("ignore")

PROJECT_ROOT = Path("/storage/scratch1/4/nbawana3/furnace-project")
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "wbt_wide.csv"
OUT_DIR = PROJECT_ROOT / "outputs" / "phase4"
OUT_DIR.mkdir(parents=True, exist_ok=True)

LOG_PATH = OUT_DIR / "yis_permutation.log"
logging.basicConfig(
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
    handlers=[logging.FileHandler(LOG_PATH, mode="w"), logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("phase4b")

RANDOM_STATE = 42
N_SPLITS = 5
N_REPEATS = 10

GEOMETRY_NUMERIC = [
    "height_cm", "outside_d_cm", "chamber_d_cm", "chamber_depth_cm",
    "inlet_w_cm", "inlet_h_cm", "inlet_area_cm2", "chamber_volume_cm3",
]
WBT_METRIC_PREFIXES = ["eff", "fp", "br", "sfc", "tboil"]


def feature_group(feature: str) -> str:
    """Classify a feature into geometry / wbt / categorical."""
    if feature in GEOMETRY_NUMERIC:
        return "geometry"
    if feature in ("material", "format"):
        return "categorical"
    for p in WBT_METRIC_PREFIXES:
        if feature.startswith(p + "_"):
            return "wbt"
    return "other"


YEAR_RE = re.compile(r"(20\d{2})")


def derive_campaign_year(campaign: object) -> int | None:
    if campaign is None or (isinstance(campaign, float) and np.isnan(campaign)):
        return None
    m = YEAR_RE.search(str(campaign))
    return int(m.group(1)) if m else None


def main() -> None:
    df = pd.read_csv(DATA_PATH)
    df = df[df["replicate_kind"] == "average"].copy()
    df = df.dropna(subset=["src_path"]).copy()
    df["campaign_year"] = df["campaign"].apply(derive_campaign_year)

    mask = df["sale_year"].notna() & df["campaign_year"].notna()
    df.loc[mask, "years_in_service"] = (
        df.loc[mask, "campaign_year"].astype(int) - df.loc[mask, "sale_year"].astype(int)
    )
    sub = df.dropna(subset=["years_in_service"]).copy()
    sub = sub.dropna(subset=GEOMETRY_NUMERIC)
    log.info("modeling years_in_service on %d stoves", len(sub))

    # Build feature lists (same as Phase 4 yis_regression)
    geom = [c for c in GEOMETRY_NUMERIC if c in sub.columns]
    wbt = [c for c in sub.columns
           if any(c.startswith(p + "_") for p in WBT_METRIC_PREFIXES)
           and not c.endswith("_combined")]
    num_cols = geom + wbt
    cat_cols = ["material", "format"]
    feat_cols = num_cols + cat_cols
    log.info("features: %d numeric + %d categorical = %d total",
             len(num_cols), len(cat_cols), len(feat_cols))

    X = sub[feat_cols]
    y = sub["years_in_service"].astype(float).values
    groups = sub["src_path"]

    cv = GroupKFold(n_splits=N_SPLITS)
    per_fold: list[pd.Series] = []
    for fold, (tr, te) in enumerate(cv.split(X, y, groups), 1):
        log.info("fold %d/%d — fitting RF + permutation importance",
                 fold, N_SPLITS)
        pre = ColumnTransformer([
            ("num", Pipeline([
                ("imp", SimpleImputer(strategy="median")),
                ("sc", StandardScaler()),
            ]), num_cols),
            ("cat", Pipeline([
                ("imp", SimpleImputer(strategy="constant", fill_value="unknown")),
                ("oh", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
            ]), cat_cols),
        ])
        rf = RandomForestRegressor(
            n_estimators=100, max_depth=None, min_samples_leaf=2,
            n_jobs=1, random_state=RANDOM_STATE,
        )
        pipe = Pipeline([("pre", pre), ("est", rf)])
        pipe.fit(X.iloc[tr], y[tr])
        result = permutation_importance(
            pipe, X.iloc[te], y[te],
            n_repeats=N_REPEATS, random_state=RANDOM_STATE, scoring="r2",
            n_jobs=1,
        )
        per_fold.append(pd.Series(result.importances_mean, index=feat_cols, name=f"fold_{fold}"))

    fold_df = pd.concat(per_fold, axis=1)
    imp_df = pd.DataFrame({
        "feature": fold_df.index,
        "group": [feature_group(f) for f in fold_df.index],
        "imp_mean": fold_df.mean(axis=1).values,
        "imp_std": fold_df.std(axis=1).values,
    }).sort_values("imp_mean", ascending=False).reset_index(drop=True)

    # Aggregate by group
    by_group = (
        imp_df.groupby("group")["imp_mean"]
        .agg(total="sum", n="count", top_feature_imp="max")
        .reset_index()
        .sort_values("total", ascending=False)
    )

    log.info("\n=== Top 15 features by mean permutation importance ===")
    log.info("\n%s", imp_df.head(15).to_string(index=False))
    log.info("\n=== Aggregated by feature group ===")
    log.info("\n%s", by_group.to_string(index=False))

    imp_df.to_csv(OUT_DIR / "yis_permutation_importance.csv", index=False)
    by_group.to_csv(OUT_DIR / "yis_permutation_by_group.csv", index=False)

    # Markdown summary
    md_lines = [
        "# Phase 4b: Years-in-Service Permutation Importance",
        "",
        "Trained Random Forest to predict `years_in_service` with grouped 5-fold CV by stove.",
        "Permutation importance computed on each held-out fold with 10 repeats; aggregated.",
        "",
        "## Aggregated importance by feature group",
        "",
        "If `wbt` group dominates → the model relies on functional signals (efficiency, firepower, "
        "burn rate, etc.) that could plausibly drift with wear → supports **real degradation** "
        "interpretation.",
        "",
        "If `geometry` group dominates → geometry doesn't change with age, so the model is "
        "identifying format×year cohorts rather than wear → supports **cohort confound** "
        "interpretation.",
        "",
        "| Group | Total importance | n features | Top single importance |",
        "|---|---:|---:|---:|",
    ]
    for _, r in by_group.iterrows():
        md_lines.append(
            f"| {r['group']} | {r['total']:.4f} | {r['n']} | {r['top_feature_imp']:.4f} |"
        )
    md_lines.append("")
    md_lines.append("## Top 15 features")
    md_lines.append("")
    md_lines.append("| Rank | Feature | Group | Importance (mean ± std) |")
    md_lines.append("|---:|---|---|---|")
    for i, r in imp_df.head(15).iterrows():
        md_lines.append(
            f"| {i+1} | `{r['feature']}` | {r['group']} | "
            f"{r['imp_mean']:.4f} ± {r['imp_std']:.4f} |"
        )
    md_lines.append("")
    (OUT_DIR / "yis_permutation_summary.md").write_text("\n".join(md_lines))
    log.info("wrote yis_permutation_summary.md")


if __name__ == "__main__":
    main()
