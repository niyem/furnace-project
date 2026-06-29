"""
phase1_predictability.py — Phase 1 of the cookstove modeling pipeline.

Establishes a predictability landscape: for each
    (target × feature_set × model_family) combination,
report cross-validated R^2 (mean ± std) and MAE using grouped K-fold by stove.

The script is intentionally self-contained but organized into clear sections so
later phases (feature ablation, OOD generalization, physics features, uncertainty
quantification) can be added by reusing the same helpers.

Inputs:
    data/processed/wbt_wide.csv  (produced by preprocess_wbt.py)

Outputs (in outputs/phase1/):
    results_folds.csv   one row per (target, features, model, fold)
    summary.csv         aggregated mean±std per (target, features, model)
    summary.md          human-readable markdown table
    phase1.log          run log

Run:
    python3 phase1_predictability.py
"""

from __future__ import annotations

import logging
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

warnings.filterwarnings("ignore")

# =============================================================================
# Configuration
# =============================================================================

PROJECT_ROOT = Path("/storage/scratch1/4/nbawana3/furnace-project")
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "wbt_wide.csv"
OUT_DIR = PROJECT_ROOT / "outputs" / "phase1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

LOG_PATH = OUT_DIR / "phase1.log"
logging.basicConfig(
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
    handlers=[logging.FileHandler(LOG_PATH, mode="w"), logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("phase1")

RANDOM_STATE = 42
N_SPLITS = 5

# The 9 regression targets we evaluate. Combined-efficiency target is added in main().
TARGETS = [
    "eff_cold", "eff_hot", "eff_simmer",
    "fp_cold", "fp_hot", "fp_simmer",
    "br_cold", "br_hot", "br_simmer",
]

FEATURE_SETS = ["geometry", "wbt_other_phase", "combined"]
MODELS = ["ridge", "gbt", "rf"]

# Geometric features available for the 5 Toyola HxC formats only.
GEOMETRY_NUMERIC = [
    "height_cm", "outside_d_cm", "chamber_d_cm", "chamber_depth_cm",
    "inlet_w_cm", "inlet_h_cm", "inlet_area_cm2", "chamber_volume_cm3",
]
# WBT-derived per-phase metric columns. Constructed dynamically from the data.
WBT_METRIC_PREFIXES = ["eff", "fp", "br", "sfc", "tboil"]
PHASES = ["cold", "hot", "simmer"]


# =============================================================================
# Data loading
# =============================================================================

def load_wide() -> pd.DataFrame:
    """Load wbt_wide.csv and restrict to one row per stove (replicate_kind='average')."""
    df = pd.read_csv(DATA_PATH)
    log.info("wide table: %d rows × %d cols", len(df), df.shape[1])
    df = df[df["replicate_kind"] == "average"].copy()
    log.info("after 'average'-only filter: %d rows", len(df))

    # Derive combined-efficiency target (mean of three phases when all are present).
    eff_cols = [c for c in ("eff_cold", "eff_hot", "eff_simmer") if c in df.columns]
    df["eff_combined"] = df[eff_cols].mean(axis=1, skipna=False)
    return df


# =============================================================================
# Feature-set definitions
# =============================================================================

def features_for(kind: str, target: str, df: pd.DataFrame) -> tuple[list[str], list[str]]:
    """
    Return (numeric_cols, categorical_cols) for the given feature set and target.

    Feature sets:
      - "geometry": stove design features only (pre-test). Available for HxC formats.
      - "wbt_other_phase": all WBT-derived metrics EXCEPT those of the target's own phase.
      - "combined": union of the above two.
    """
    target_phase = target.split("_")[-1] if target != "eff_combined" else None

    if kind == "geometry":
        nums = [c for c in GEOMETRY_NUMERIC if c in df.columns]
        return nums, ["material"]

    # WBT metric columns present in the data
    metric_cols = [
        c for c in df.columns
        if any(c.startswith(p + "_") for p in WBT_METRIC_PREFIXES)
    ]
    # Drop the target itself, derived *_combined columns, same-phase WBT cols, and
    # (for the eff_combined target) the per-phase efficiency columns it averages.
    def _keep(col: str) -> bool:
        if col == target:
            return False
        if col.endswith("_combined"):
            return False
        if target_phase is not None and col.endswith("_" + target_phase):
            return False
        if target == "eff_combined" and col.startswith("eff_") and col.split("_")[-1] in PHASES:
            return False
        return True
    wbt_nums = [c for c in metric_cols if _keep(c)]

    if kind == "wbt_other_phase":
        return wbt_nums, ["material", "format"]

    if kind == "combined":
        geom_nums = [c for c in GEOMETRY_NUMERIC if c in df.columns]
        return geom_nums + wbt_nums, ["material"]

    raise ValueError(f"unknown feature_set: {kind}")


def filter_for_modeling(df: pd.DataFrame, target: str, num_cols: list[str], cat_cols: list[str],
                        require_geometry: bool) -> pd.DataFrame:
    """Drop rows missing the target or (optionally) the geometry features."""
    sub = df.dropna(subset=[target]).copy()
    if require_geometry:
        sub = sub.dropna(subset=GEOMETRY_NUMERIC)
    # Drop rows with missing src_path (group key)
    sub = sub.dropna(subset=["src_path"])
    return sub


# =============================================================================
# Model factory
# =============================================================================

def make_pipeline(model_name: str, num_cols: list[str], cat_cols: list[str]) -> Pipeline:
    """Build a preprocessing + estimator sklearn Pipeline."""
    num_pipe = Pipeline([
        ("imp", SimpleImputer(strategy="median")),
        ("sc", StandardScaler()),
    ])
    cat_pipe = Pipeline([
        ("imp", SimpleImputer(strategy="constant", fill_value="unknown")),
        ("oh", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    pre = ColumnTransformer([
        ("num", num_pipe, num_cols),
        ("cat", cat_pipe, cat_cols),
    ])
    if model_name == "ridge":
        est = Ridge(alpha=1.0, random_state=RANDOM_STATE)
    elif model_name == "gbt":
        est = HistGradientBoostingRegressor(
            max_iter=300, max_depth=6, learning_rate=0.05,
            min_samples_leaf=10, random_state=RANDOM_STATE,
        )
    elif model_name == "rf":
        est = RandomForestRegressor(
            n_estimators=300, max_depth=None, min_samples_leaf=2,
            n_jobs=-1, random_state=RANDOM_STATE,
        )
    else:
        raise ValueError(f"unknown model: {model_name}")
    return Pipeline([("pre", pre), ("est", est)])


# =============================================================================
# Cross-validation harness
# =============================================================================

def grouped_cv(df: pd.DataFrame, target: str, num_cols: list[str], cat_cols: list[str],
               model_name: str, n_splits: int = N_SPLITS) -> list[dict]:
    """Run grouped K-fold CV; return per-fold metric dicts."""
    feat_cols = num_cols + cat_cols
    X = df[feat_cols]
    y = df[target]
    groups = df["src_path"]
    cv = GroupKFold(n_splits=n_splits)
    rows = []
    for fold, (tr, te) in enumerate(cv.split(X, y, groups), 1):
        pipe = make_pipeline(model_name, num_cols, cat_cols)
        pipe.fit(X.iloc[tr], y.iloc[tr])
        pred = pipe.predict(X.iloc[te])
        rows.append(dict(
            fold=fold,
            n_train=int(len(tr)),
            n_test=int(len(te)),
            r2=float(r2_score(y.iloc[te], pred)),
            mae=float(mean_absolute_error(y.iloc[te], pred)),
            y_test_mean=float(y.iloc[te].mean()),
            y_test_std=float(y.iloc[te].std()),
        ))
    return rows


# =============================================================================
# Reporting
# =============================================================================

def aggregate(rows: list[dict]) -> pd.DataFrame:
    """Aggregate per-fold rows to mean ± std per (target, features, model)."""
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    agg = (
        df.groupby(["target", "features", "model"])
          .agg(
              n_total=("n_total", "first"),
              r2_mean=("r2", "mean"),
              r2_std=("r2", "std"),
              mae_mean=("mae", "mean"),
              mae_std=("mae", "std"),
              n_features=("n_features", "first"),
          )
          .reset_index()
    )
    agg["r2_mean"] = agg["r2_mean"].round(3)
    agg["r2_std"] = agg["r2_std"].round(3)
    agg["mae_mean"] = agg["mae_mean"].round(4)
    agg["mae_std"] = agg["mae_std"].round(4)
    return agg


def write_markdown(summary: pd.DataFrame, out_path: Path) -> None:
    """Write a human-readable markdown summary table grouped by target."""
    lines = [
        "# Phase 1: Predictability Landscape",
        "",
        f"Grouped {N_SPLITS}-fold CV by stove identity (`src_path`). "
        f"Mean R² ± std across folds. MAE in target units.",
        "",
    ]
    for target in sorted(summary["target"].unique()):
        sub = summary[summary["target"] == target].sort_values(["r2_mean"], ascending=False)
        lines.append(f"## Target: `{target}`")
        lines.append("")
        lines.append("| Features | Model | n | n_feat | R² (mean ± std) | MAE (mean ± std) |")
        lines.append("|---|---|---:|---:|---|---|")
        for _, row in sub.iterrows():
            lines.append(
                f"| {row['features']} | {row['model']} | {row['n_total']} | {row['n_features']} | "
                f"{row['r2_mean']:.3f} ± {row['r2_std']:.3f} | "
                f"{row['mae_mean']:.4f} ± {row['mae_std']:.4f} |"
            )
        lines.append("")
    out_path.write_text("\n".join(lines))


# =============================================================================
# Orchestration
# =============================================================================

def run() -> None:
    df = load_wide()
    # Use only rows whose stove identity is known
    df = df.dropna(subset=["src_path"]).copy()
    log.info("modeling on %d stoves total", len(df))

    all_folds: list[dict] = []
    targets = TARGETS + ["eff_combined"]
    for target in targets:
        if target not in df.columns:
            log.warning("target %s not in data; skipping", target)
            continue
        for fs in FEATURE_SETS:
            num_cols, cat_cols = features_for(fs, target, df)
            require_geom = fs in ("geometry", "combined")
            sub = filter_for_modeling(df, target, num_cols, cat_cols, require_geometry=require_geom)
            n = len(sub)
            if n < N_SPLITS * 2:
                log.warning("[%s|%s] only %d stoves, skipping", target, fs, n)
                continue
            n_features = len(num_cols) + len(cat_cols)
            log.info("[%s|%s] n=%d, n_feat=%d", target, fs, n, n_features)
            for model in MODELS:
                folds = grouped_cv(sub, target, num_cols, cat_cols, model)
                for f in folds:
                    all_folds.append({
                        "target": target,
                        "features": fs,
                        "model": model,
                        "n_total": n,
                        "n_features": n_features,
                        **f,
                    })

    folds_df = pd.DataFrame(all_folds)
    folds_path = OUT_DIR / "results_folds.csv"
    folds_df.to_csv(folds_path, index=False)
    log.info("wrote %s (%d rows)", folds_path, len(folds_df))

    summary = aggregate(all_folds)
    summary_csv = OUT_DIR / "summary.csv"
    summary.to_csv(summary_csv, index=False)
    log.info("wrote %s", summary_csv)

    summary_md = OUT_DIR / "summary.md"
    write_markdown(summary, summary_md)
    log.info("wrote %s", summary_md)

    # Console snapshot
    log.info("\n--- Top 10 (target × features × model) by mean R² ---")
    top = summary.sort_values("r2_mean", ascending=False).head(10)
    log.info("\n%s", top.to_string(index=False))

    log.info("\n--- Best feature_set per target (by mean R²) ---")
    best = summary.sort_values("r2_mean", ascending=False).groupby("target").head(1)
    log.info("\n%s", best.to_string(index=False))


if __name__ == "__main__":
    run()
