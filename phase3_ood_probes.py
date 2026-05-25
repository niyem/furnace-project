"""
phase3_ood_probes.py — Phase 3 of the cookstove modeling pipeline.

Out-of-distribution (OOD) generalization probes. Three structured holdouts
mirror real operational use cases:

    LOFO  leave-one-format-out
          train on all formats except the held-out one (e.g. train on HS/HM/HL/CS,
          test on CL). Tells us whether the model extrapolates to unseen sizes.

    LOMO  leave-one-material-out
          train on clay only, test on ceramic (or vice versa). Tells us whether
          the Toyola-trained model generalizes to ceramic-core SEQUOIA stoves.

    LOBO  leave-one-brand-out
          hold out one of {Toyola, SEQUOIA-tested, Ghana-MAN, Toyola-Nigeria,
          Prakash} at a time. Tells us cross-manufacturer transfer.

For each (probe, holdout_value, target) cell we train the best Phase 1 / Phase 2
model (Random Forest on the combined-features set) on the remaining stoves and
report R^2 and MAE on the held-out group.

Inputs:
    data/processed/wbt_wide.csv

Outputs (in outputs/phase3/):
    ood_results.csv      per (probe, holdout, target, model) -> n_train, n_test, R^2, MAE
    ood_summary.md       human-readable markdown by probe and target
    phase3.log

Run:
    OMP_NUM_THREADS=1 python3 phase3_ood_probes.py
"""

from __future__ import annotations

import logging
import math
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

warnings.filterwarnings("ignore")

# =============================================================================
# Configuration
# =============================================================================

PROJECT_ROOT = Path("/storage/scratch1/4/nbawana3/furnace-project")
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "wbt_wide.csv"
OUT_DIR = PROJECT_ROOT / "outputs" / "phase3"
OUT_DIR.mkdir(parents=True, exist_ok=True)

LOG_PATH = OUT_DIR / "phase3.log"
logging.basicConfig(
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
    handlers=[logging.FileHandler(LOG_PATH, mode="w"), logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("phase3")

RANDOM_STATE = 42
MIN_TEST_STOVES = 10       # require at least this many held-out stoves to score the cell
MIN_TRAIN_STOVES = 30      # require at least this many training stoves

TARGETS = [
    "eff_cold", "eff_hot", "eff_simmer", "eff_combined",
    "fp_cold", "fp_hot", "fp_simmer",
    "br_cold", "br_hot", "br_simmer",
]

GEOMETRY_NUMERIC = [
    "height_cm", "outside_d_cm", "chamber_d_cm", "chamber_depth_cm",
    "inlet_w_cm", "inlet_h_cm", "inlet_area_cm2", "chamber_volume_cm3",
]
WBT_METRIC_PREFIXES = ["eff", "fp", "br", "sfc", "tboil"]
PHASES = ["cold", "hot", "simmer"]


# =============================================================================
# Data loading + features
# =============================================================================

def load_wide() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df = df[df["replicate_kind"] == "average"].copy()
    eff_cols = [c for c in ("eff_cold", "eff_hot", "eff_simmer") if c in df.columns]
    df["eff_combined"] = df[eff_cols].mean(axis=1, skipna=False)
    df = df.dropna(subset=["src_path"]).copy()
    log.info("loaded %d stoves (one row per stove)", len(df))
    return df


def wbt_features_for(target: str, df: pd.DataFrame) -> list[str]:
    """All WBT metric cols except target's own phase, target itself, and eff_combined."""
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
        if target == "eff_combined" and c.startswith("eff_") and c.split("_")[-1] in PHASES:
            continue
        cols.append(c)
    return cols


def combined_features(target: str, df: pd.DataFrame) -> tuple[list[str], list[str]]:
    geom = [c for c in GEOMETRY_NUMERIC if c in df.columns]
    wbt = wbt_features_for(target, df)
    return geom + wbt, ["material"]


# =============================================================================
# Model factory
# =============================================================================

def make_rf_pipeline(num_cols: list[str], cat_cols: list[str]) -> Pipeline:
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
    est = RandomForestRegressor(
        n_estimators=100, max_depth=None, min_samples_leaf=2,
        n_jobs=1, random_state=RANDOM_STATE,
    )
    return Pipeline([("pre", pre), ("est", est)])


# =============================================================================
# Probe evaluation
# =============================================================================

def evaluate_holdout(df: pd.DataFrame, target: str, hold_col: str, hold_val: str) -> dict | None:
    """Train RF on everything where df[hold_col] != hold_val, test on the rest."""
    sub = df.dropna(subset=[target, hold_col]).copy()
    sub = sub.dropna(subset=GEOMETRY_NUMERIC)  # require geometry for combined features
    if sub.empty:
        return None
    train = sub[sub[hold_col] != hold_val]
    test = sub[sub[hold_col] == hold_val]
    if len(train) < MIN_TRAIN_STOVES or len(test) < MIN_TEST_STOVES:
        return None
    num_cols, cat_cols = combined_features(target, sub)
    pipe = make_rf_pipeline(num_cols, cat_cols)
    pipe.fit(train[num_cols + cat_cols], train[target])
    pred = pipe.predict(test[num_cols + cat_cols])
    return dict(
        n_train=int(len(train)),
        n_test=int(len(test)),
        r2=float(r2_score(test[target], pred)),
        mae=float(mean_absolute_error(test[target], pred)),
        y_test_mean=float(test[target].mean()),
        y_test_std=float(test[target].std()),
    )


def run_probe(df: pd.DataFrame, probe_name: str, hold_col: str) -> pd.DataFrame:
    """Run holdout for every distinct value of df[hold_col]."""
    rows = []
    values = sorted(df[hold_col].dropna().unique().tolist())
    log.info("=== %s probe: %d holdout values from `%s` ===", probe_name, len(values), hold_col)
    for hv in values:
        for target in TARGETS:
            if target not in df.columns:
                continue
            res = evaluate_holdout(df, target, hold_col, hv)
            if res is None:
                continue
            rows.append({
                "probe": probe_name,
                "holdout_col": hold_col,
                "holdout_value": hv,
                "target": target,
                "model": "rf",
                **res,
            })
            log.info("  %s=%s | %s | n_tr=%d n_te=%d | R^2=%+.3f MAE=%.4f",
                     probe_name, hv, target, res["n_train"], res["n_test"],
                     res["r2"], res["mae"])
    return pd.DataFrame(rows)


# =============================================================================
# Reporting
# =============================================================================

def write_md(results: pd.DataFrame, out_path: Path) -> None:
    lines = [
        "# Phase 3: OOD Generalization Probes",
        "",
        "Random Forest on combined features (geometry + cross-phase WBT). Train on all "
        "stoves where the holdout column != held-out value; test on the rest.",
        "",
        "R² < 0 means worse than predicting the train-set mean.",
        "",
    ]
    for probe in sorted(results["probe"].unique()):
        psub = results[results["probe"] == probe]
        lines.append(f"## Probe: {probe}")
        lines.append("")
        for target in sorted(psub["target"].unique()):
            tsub = psub[psub["target"] == target].sort_values("holdout_value")
            lines.append(f"### Target: `{target}`")
            lines.append("")
            lines.append("| Holdout | n_train | n_test | R² | MAE | y_test_mean | y_test_std |")
            lines.append("|---|---:|---:|---:|---:|---:|---:|")
            for _, r in tsub.iterrows():
                lines.append(
                    f"| {r['holdout_value']} | {r['n_train']} | {r['n_test']} | "
                    f"{r['r2']:+.3f} | {r['mae']:.4f} | "
                    f"{r['y_test_mean']:.4f} | {r['y_test_std']:.4f} |"
                )
            lines.append("")
    out_path.write_text("\n".join(lines))


# =============================================================================
# Orchestration
# =============================================================================

def run() -> None:
    df = load_wide()

    all_rows: list[pd.DataFrame] = []

    # LOFO — leave-one-format-out
    df_lofo = df.dropna(subset=["format"]).copy()
    all_rows.append(run_probe(df_lofo, "LOFO", "format"))

    # LOMO — leave-one-material-out (only meaningful if >=2 materials)
    df_lomo = df.dropna(subset=["material"]).copy()
    if df_lomo["material"].nunique() >= 2:
        all_rows.append(run_probe(df_lomo, "LOMO", "material"))

    # LOBO — leave-one-brand-out
    df_lobo = df.dropna(subset=["brand"]).copy()
    all_rows.append(run_probe(df_lobo, "LOBO", "brand"))

    # LOCO — leave-one-campaign-out: tests for campaign-level confounds
    # (operator team, charcoal batch, weather, calibration drift between campaigns).
    df_loco = df.dropna(subset=["campaign"]).copy()
    all_rows.append(run_probe(df_loco, "LOCO", "campaign"))

    results = pd.concat(all_rows, ignore_index=True) if all_rows else pd.DataFrame()
    out_path = OUT_DIR / "ood_results.csv"
    results.to_csv(out_path, index=False)
    log.info("wrote %s (%d rows)", out_path, len(results))

    write_md(results, OUT_DIR / "ood_summary.md")
    log.info("wrote ood_summary.md")

    # Console snapshot per probe
    log.info("\n--- Probe summary (mean R² across holdouts, per target) ---")
    pivot = (
        results.groupby(["probe", "target"])["r2"].agg(["mean", "std", "count"])
        .reset_index()
        .rename(columns={"mean": "r2_mean", "std": "r2_std", "count": "n_cells"})
    )
    log.info("\n%s", pivot.to_string(index=False))


if __name__ == "__main__":
    run()
