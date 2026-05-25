"""
phase2_feature_ablation.py — Phase 2 of the cookstove modeling pipeline.

Builds on Phase 1 by adding physics-engineered features and quantifying the
marginal predictive value of each feature block. Then ranks per-feature
importance via permutation importance (the sklearn-native, model-agnostic
method) for the best (target × model) cells.

Six feature sets are evaluated, with grouped 5-fold CV by stove identity:

    geometry          : raw stove dimensions (8 numeric + material)
    geometry_phys     : geometry + physics-engineered derived features
    wbt_other_phase   : cross-phase WBT measurements (excludes target phase)
    wbt_other_phys    : wbt_other_phase + physics-engineered
    combined          : geometry + wbt_other_phase
    combined_phys     : combined + physics-engineered

Engineered features (combustion-physics motivated):
    aspect_ratio        height_cm / outside_d_cm           tall-vs-squat geometry
    chamber_aspect      chamber_depth_cm / chamber_d_cm    combustion-chamber shape
    inlet_per_volume    inlet_area_cm2 / chamber_volume_cm3 airflow intensity (cm^-1)
    chamber_surface     wall + base cylindrical surface    radiative-loss surface (cm^2)
    surface_to_volume   chamber_surface / chamber_volume   heat-loss vs storage ratio
    wall_thickness      (outside_d - chamber_d) / 2        insulation proxy (cm)

Inputs:
    data/processed/wbt_wide.csv

Outputs (in outputs/phase2/):
    ablation_summary.csv         per (target, feature_set, model) — mean ± std R²/MAE
    ablation_summary.md          formatted markdown by target
    ablation_marginal.csv        ΔR² when each feature block is added
    permutation_importance.csv   per (target, feature, importance_mean, importance_std)
    feature_dictionary.md        documents each engineered feature
    phase2.log

Run:
    OMP_NUM_THREADS=1 python3 phase2_feature_ablation.py
"""

from __future__ import annotations

import logging
import math
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
OUT_DIR = PROJECT_ROOT / "outputs" / "phase2"
OUT_DIR.mkdir(parents=True, exist_ok=True)

LOG_PATH = OUT_DIR / "phase2.log"
logging.basicConfig(
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
    handlers=[logging.FileHandler(LOG_PATH, mode="w"), logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("phase2")

RANDOM_STATE = 42
N_SPLITS = 5

TARGETS = [
    "eff_cold", "eff_hot", "eff_simmer",
    "fp_cold", "fp_hot", "fp_simmer",
    "br_cold", "br_hot", "br_simmer",
    "eff_combined",
]

FEATURE_SETS = [
    "geometry", "geometry_phys",
    "wbt_other_phase", "wbt_other_phys",
    "combined", "combined_phys",
]
MODELS = ["ridge", "rf"]

GEOMETRY_NUMERIC = [
    "height_cm", "outside_d_cm", "chamber_d_cm", "chamber_depth_cm",
    "inlet_w_cm", "inlet_h_cm", "inlet_area_cm2", "chamber_volume_cm3",
]
ENG_NUMERIC = [
    "aspect_ratio", "chamber_aspect", "inlet_per_volume",
    "chamber_surface_cm2", "surface_to_volume", "wall_thickness_cm",
]
WBT_METRIC_PREFIXES = ["eff", "fp", "br", "sfc", "tboil"]
PHASES = ["cold", "hot", "simmer"]


# =============================================================================
# Data loading and feature engineering
# =============================================================================

def load_wide() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    log.info("wide table: %d rows × %d cols", len(df), df.shape[1])
    df = df[df["replicate_kind"] == "average"].copy()
    log.info("'average'-only rows: %d", len(df))
    eff_cols = [c for c in ("eff_cold", "eff_hot", "eff_simmer") if c in df.columns]
    df["eff_combined"] = df[eff_cols].mean(axis=1, skipna=False)
    df = engineer_features(df)
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add physics-derived geometric features. Returns the same df with new columns."""
    h = df["height_cm"]
    od = df["outside_d_cm"]
    cd = df["chamber_d_cm"]
    cdp = df["chamber_depth_cm"]
    ia = df["inlet_area_cm2"]
    cv = df["chamber_volume_cm3"]

    df["aspect_ratio"] = h / od
    df["chamber_aspect"] = cdp / cd
    df["inlet_per_volume"] = ia / cv
    # Cylindrical chamber surface area: side wall + bottom disc.
    df["chamber_surface_cm2"] = math.pi * cd * cdp + math.pi * (cd / 2.0) ** 2
    df["surface_to_volume"] = df["chamber_surface_cm2"] / cv
    df["wall_thickness_cm"] = (od - cd) / 2.0
    return df


# =============================================================================
# Feature-set definitions
# =============================================================================

def _wbt_other_phase_cols(target: str, df: pd.DataFrame) -> list[str]:
    """WBT metric columns excluding target phase and target itself and eff_combined."""
    target_phase = target.split("_")[-1] if target != "eff_combined" else None
    cols = []
    for c in df.columns:
        if not any(c.startswith(p + "_") for p in WBT_METRIC_PREFIXES):
            continue
        if c.endswith("_combined"):
            continue
        if c == target:
            continue
        if target_phase is not None and c.endswith("_" + target_phase):
            continue
        # For eff_combined target, also drop all per-phase eff_* columns
        if target == "eff_combined" and c.startswith("eff_") and c.split("_")[-1] in PHASES:
            continue
        cols.append(c)
    return cols


def features_for(kind: str, target: str, df: pd.DataFrame) -> tuple[list[str], list[str]]:
    """
    Return (numeric_cols, categorical_cols) for the given feature set and target.
    """
    geom = [c for c in GEOMETRY_NUMERIC if c in df.columns]
    eng = [c for c in ENG_NUMERIC if c in df.columns]
    wbt = _wbt_other_phase_cols(target, df)

    if kind == "geometry":
        return geom, ["material"]
    if kind == "geometry_phys":
        return geom + eng, ["material"]
    if kind == "wbt_other_phase":
        return wbt, ["material", "format"]
    if kind == "wbt_other_phys":
        return wbt + eng, ["material", "format"]
    if kind == "combined":
        return geom + wbt, ["material"]
    if kind == "combined_phys":
        return geom + eng + wbt, ["material"]
    raise ValueError(f"unknown feature_set: {kind}")


def filter_for_modeling(df: pd.DataFrame, target: str, kind: str) -> pd.DataFrame:
    """Drop rows missing target or geometry (when geometry is required)."""
    sub = df.dropna(subset=[target]).copy()
    if kind in ("geometry", "geometry_phys", "combined", "combined_phys"):
        sub = sub.dropna(subset=GEOMETRY_NUMERIC)
    sub = sub.dropna(subset=["src_path"])
    return sub


# =============================================================================
# Model factory + CV
# =============================================================================

def make_pipeline(model_name: str, num_cols: list[str], cat_cols: list[str]) -> Pipeline:
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
    if model_name == "ridge":
        est = Ridge(alpha=1.0, random_state=RANDOM_STATE)
    elif model_name == "rf":
        est = RandomForestRegressor(
            n_estimators=100, max_depth=None, min_samples_leaf=2,
            n_jobs=1, random_state=RANDOM_STATE,
        )
    else:
        raise ValueError(f"unknown model: {model_name}")
    return Pipeline([("pre", pre), ("est", est)])


def grouped_cv(df: pd.DataFrame, target: str, num_cols: list[str], cat_cols: list[str],
               model_name: str, n_splits: int = N_SPLITS) -> list[dict]:
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
        ))
    return rows


# =============================================================================
# Permutation importance (averaged across CV folds)
# =============================================================================

def permutation_importance_grouped(
    df: pd.DataFrame, target: str, num_cols: list[str], cat_cols: list[str],
    model_name: str, n_repeats: int = 10, n_splits: int = N_SPLITS,
) -> pd.DataFrame:
    """
    Run grouped CV; on each fold, compute permutation importance on the held-out set
    using the trained pipeline. Aggregate to mean ± std per feature.
    """
    feat_cols = num_cols + cat_cols
    X = df[feat_cols]
    y = df[target]
    groups = df["src_path"]
    cv = GroupKFold(n_splits=n_splits)

    per_fold: list[pd.Series] = []
    for fold, (tr, te) in enumerate(cv.split(X, y, groups), 1):
        pipe = make_pipeline(model_name, num_cols, cat_cols)
        pipe.fit(X.iloc[tr], y.iloc[tr])
        result = permutation_importance(
            pipe, X.iloc[te], y.iloc[te],
            n_repeats=n_repeats, random_state=RANDOM_STATE, scoring="r2",
            n_jobs=1,
        )
        s = pd.Series(result.importances_mean, index=feat_cols, name=f"fold_{fold}")
        per_fold.append(s)
    fold_df = pd.concat(per_fold, axis=1)
    out = pd.DataFrame({
        "feature": fold_df.index,
        "imp_mean": fold_df.mean(axis=1).values,
        "imp_std": fold_df.std(axis=1).values,
    }).sort_values("imp_mean", ascending=False).reset_index(drop=True)
    return out


# =============================================================================
# Reporting
# =============================================================================

def aggregate(rows: list[dict]) -> pd.DataFrame:
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
    for col in ("r2_mean", "r2_std"):
        agg[col] = agg[col].round(3)
    for col in ("mae_mean", "mae_std"):
        agg[col] = agg[col].round(4)
    return agg


def marginal_table(summary: pd.DataFrame) -> pd.DataFrame:
    """
    Compute ΔR² (mean) when each feature block is added. Uses the RF results.
    Pairs:
      geometry → geometry_phys           Δ(physics on top of geometry)
      geometry → combined                Δ(adding WBT on top of geometry)
      wbt_other_phase → wbt_other_phys   Δ(physics on top of WBT)
      combined → combined_phys           Δ(physics on top of combined)
    """
    rows = []
    for target in summary["target"].unique():
        sub = summary[(summary["target"] == target) & (summary["model"] == "rf")]
        ref = {r["features"]: r["r2_mean"] for _, r in sub.iterrows()}
        def diff(a, b):
            if a not in ref or b not in ref:
                return None
            return round(ref[b] - ref[a], 4)
        rows.append({
            "target": target,
            "geom_R2": ref.get("geometry"),
            "geom+phys_R2": ref.get("geometry_phys"),
            "Δ_phys_on_geom": diff("geometry", "geometry_phys"),
            "wbt_R2": ref.get("wbt_other_phase"),
            "wbt+phys_R2": ref.get("wbt_other_phys"),
            "Δ_phys_on_wbt": diff("wbt_other_phase", "wbt_other_phys"),
            "combined_R2": ref.get("combined"),
            "combined+phys_R2": ref.get("combined_phys"),
            "Δ_phys_on_combined": diff("combined", "combined_phys"),
            "Δ_wbt_over_geom": diff("geometry", "combined"),
        })
    return pd.DataFrame(rows)


def write_ablation_md(summary: pd.DataFrame, out_path: Path) -> None:
    lines = [
        "# Phase 2: Feature Ablation",
        "",
        f"Grouped {N_SPLITS}-fold CV by stove identity. Mean R² ± std across folds.",
        "Models: Ridge (regularized linear) and Random Forest (100 trees).",
        "",
    ]
    for target in sorted(summary["target"].unique()):
        sub = summary[summary["target"] == target].sort_values("r2_mean", ascending=False)
        lines.append(f"## Target: `{target}`")
        lines.append("")
        lines.append("| Features | Model | n | n_feat | R² (mean ± std) | MAE (mean ± std) |")
        lines.append("|---|---|---:|---:|---|---|")
        for _, r in sub.iterrows():
            lines.append(
                f"| {r['features']} | {r['model']} | {r['n_total']} | {r['n_features']} | "
                f"{r['r2_mean']:.3f} ± {r['r2_std']:.3f} | "
                f"{r['mae_mean']:.4f} ± {r['mae_std']:.4f} |"
            )
        lines.append("")
    out_path.write_text("\n".join(lines))


def write_feature_dictionary(path: Path) -> None:
    body = """# Feature Dictionary

## Raw geometric features (from STOVE_DIMS)

| Feature | Units | Definition |
|---|---|---|
| `height_cm` | cm | Total stove height |
| `outside_d_cm` | cm | Stove outer diameter |
| `chamber_d_cm` | cm | Combustion-chamber inner diameter |
| `chamber_depth_cm` | cm | Combustion-chamber depth |
| `inlet_w_cm`, `inlet_h_cm` | cm | Air-inlet dimensions |
| `inlet_area_cm2` | cm² | Derived: inlet width × height |
| `chamber_volume_cm3` | cm³ | Derived: π·(d/2)²·depth |

## Physics-engineered features (added in Phase 2)

| Feature | Units | Definition | Physical interpretation |
|---|---|---|---|
| `aspect_ratio` | — | `height_cm / outside_d_cm` | Tall vs. squat geometry. Tall stoves may have better natural-draft pull. |
| `chamber_aspect` | — | `chamber_depth_cm / chamber_d_cm` | Combustion-chamber shape. Affects flame envelope and radiative coupling to the pot. |
| `inlet_per_volume` | cm⁻¹ | `inlet_area_cm2 / chamber_volume_cm3` | Airflow intensity. Higher = more O₂ per unit combustion volume. |
| `chamber_surface_cm2` | cm² | `π·d·depth + π·(d/2)²` | Wall + base surface area of the chamber. Drives radiative + conductive heat loss. |
| `surface_to_volume` | cm⁻¹ | `chamber_surface_cm2 / chamber_volume_cm3` | Loss-vs-storage ratio. Higher = more heat loss per unit fuel-heat-release potential. |
| `wall_thickness_cm` | cm | `(outside_d_cm - chamber_d_cm) / 2` | Clay wall thickness. Proxy for thermal insulation between chamber and ambient. |
"""
    path.write_text(body)


# =============================================================================
# Orchestration
# =============================================================================

def run() -> None:
    df = load_wide()
    df = df.dropna(subset=["src_path"]).copy()
    log.info("modeling on %d stoves total", len(df))

    write_feature_dictionary(OUT_DIR / "feature_dictionary.md")

    all_folds: list[dict] = []
    best_cells: list[dict] = []  # for permutation importance afterwards

    for target in TARGETS:
        if target not in df.columns:
            log.warning("target %s not in data; skipping", target)
            continue
        for fs in FEATURE_SETS:
            sub = filter_for_modeling(df, target, fs)
            num_cols, cat_cols = features_for(fs, target, sub)
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
                        "target": target, "features": fs, "model": model,
                        "n_total": n, "n_features": n_features, **f,
                    })

    summary = aggregate(all_folds)
    summary.to_csv(OUT_DIR / "ablation_summary.csv", index=False)
    log.info("wrote ablation_summary.csv")

    write_ablation_md(summary, OUT_DIR / "ablation_summary.md")
    log.info("wrote ablation_summary.md")

    marginal = marginal_table(summary)
    marginal.to_csv(OUT_DIR / "ablation_marginal.csv", index=False)
    log.info("wrote ablation_marginal.csv")
    log.info("\n--- Marginal R² gains (RF) ---\n%s",
             marginal.to_string(index=False))

    # Pick the best (target, features, model) by mean R² and run permutation importance.
    best_idx = summary.groupby("target")["r2_mean"].idxmax()
    best_rows = summary.loc[best_idx]
    log.info("\n--- Best cell per target ---\n%s",
             best_rows[["target", "features", "model", "r2_mean", "r2_std"]].to_string(index=False))

    perm_rows: list[dict] = []
    for _, row in best_rows.iterrows():
        target = row["target"]
        fs = row["features"]
        model = row["model"]
        log.info("permutation importance: target=%s fs=%s model=%s", target, fs, model)
        sub = filter_for_modeling(df, target, fs)
        num_cols, cat_cols = features_for(fs, target, sub)
        try:
            imp_df = permutation_importance_grouped(sub, target, num_cols, cat_cols, model)
        except Exception as e:
            log.warning("permutation importance failed for %s: %s", target, e)
            continue
        for _, ir in imp_df.iterrows():
            perm_rows.append({
                "target": target, "features": fs, "model": model,
                "feature": ir["feature"],
                "imp_mean": round(float(ir["imp_mean"]), 5),
                "imp_std": round(float(ir["imp_std"]), 5),
            })
        # Log the top 5 features for each target
        top5 = imp_df.head(5)
        log.info("  top features for %s:\n%s", target, top5.to_string(index=False))

    perm_df = pd.DataFrame(perm_rows)
    perm_df.to_csv(OUT_DIR / "permutation_importance.csv", index=False)
    log.info("wrote permutation_importance.csv (%d rows)", len(perm_df))


if __name__ == "__main__":
    run()
