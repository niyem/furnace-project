"""
phase1c_hyperparam_sensitivity.py
---------------------------------
Random-Forest hyperparameter sensitivity sweep for the cookstove manuscript.

Addresses reviewer critique 3.2: "no hyperparameter sensitivity analysis."
Sweep grid:
  n_estimators     in (50, 100, 200, 500)
  max_depth        in (None, 10, 20)
  min_samples_leaf in (1, 2, 5)

Total = 4 * 3 * 3 = 36 combinations. Each combination is fit with the
same 5-fold GroupKFold-by-stove-identity protocol as Phase 1. Reuses the
combined feature set (geometry + cross-phase WBT) and the eff_cold target
as a representative case. Reports mean and std R^2 across folds for each
combination, writes outputs/phase1c/hyperparam_sweep.csv plus a small
LaTeX-ready table fragment for the manuscript.

Run:
    OMP_NUM_THREADS=1 python3 phase1c_hyperparam_sensitivity.py
"""
from __future__ import annotations

import logging
import sys
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Reuse the Phase 1 feature_for and filter_for_modeling helpers
sys.path.insert(0, str(Path(__file__).parent))
from phase1_predictability import (
    DATA_PATH,
    N_SPLITS,
    features_for,
    filter_for_modeling,
)

PROJECT_ROOT = Path("/storage/scratch1/4/nbawana3/furnace-project")
OUT_DIR = PROJECT_ROOT / "outputs" / "phase1c"
OUT_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
    handlers=[
        logging.FileHandler(OUT_DIR / "hyperparam_sweep.log", mode="w"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("phase1c")

TARGET = "eff_cold"
FEATURE_SET = "combined"

N_ESTIMATORS_GRID = (50, 100, 200, 500)
MAX_DEPTH_GRID = (None, 10, 20)
MIN_SAMPLES_LEAF_GRID = (1, 2, 5)


def make_pipeline(num_cols: list[str], cat_cols: list[str],
                  n_estimators: int, max_depth, min_samples_leaf: int) -> Pipeline:
    """Standard preprocessing + Random Forest with the requested hyperparameters."""
    pre = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), num_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
        ],
        remainder="drop",
    )
    rf = RandomForestRegressor(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_leaf=min_samples_leaf,
        n_jobs=1,
        random_state=0,
    )
    return Pipeline([("pre", pre), ("rf", rf)])


def grouped_cv_score(sub: pd.DataFrame, target: str, num_cols: list[str],
                     cat_cols: list[str], n_estimators: int, max_depth,
                     min_samples_leaf: int, n_splits: int = N_SPLITS) -> list[float]:
    """Return per-fold R^2 under GroupKFold by stove identity."""
    feature_cols = num_cols + cat_cols
    X = sub[feature_cols].copy()
    y = sub[target].to_numpy()
    groups = sub["src_path"].to_numpy()
    cv = GroupKFold(n_splits=n_splits)
    r2s: list[float] = []
    maes: list[float] = []
    for train_idx, test_idx in cv.split(X, y, groups):
        pipe = make_pipeline(num_cols, cat_cols, n_estimators, max_depth, min_samples_leaf)
        pipe.fit(X.iloc[train_idx], y[train_idx])
        y_pred = pipe.predict(X.iloc[test_idx])
        r2s.append(r2_score(y[test_idx], y_pred))
        maes.append(mean_absolute_error(y[test_idx], y_pred))
    return r2s, maes


def main() -> int:
    log.info("loading %s", DATA_PATH)
    df = pd.read_csv(DATA_PATH)
    num_cols, cat_cols = features_for(FEATURE_SET, TARGET, df)
    require_geom = FEATURE_SET in ("geometry", "combined")
    sub = filter_for_modeling(df, TARGET, num_cols, cat_cols, require_geometry=require_geom)
    log.info("target=%s feature_set=%s n=%d n_num=%d n_cat=%d",
             TARGET, FEATURE_SET, len(sub), len(num_cols), len(cat_cols))

    grid = list(product(N_ESTIMATORS_GRID, MAX_DEPTH_GRID, MIN_SAMPLES_LEAF_GRID))
    log.info("sweeping %d combinations", len(grid))

    records: list[dict] = []
    for idx, (n_est, max_d, min_leaf) in enumerate(grid, start=1):
        r2s, maes = grouped_cv_score(sub, TARGET, num_cols, cat_cols,
                                     n_est, max_d, min_leaf)
        rec = {
            "n_estimators": n_est,
            "max_depth": "None" if max_d is None else int(max_d),
            "min_samples_leaf": min_leaf,
            "r2_mean": float(np.mean(r2s)),
            "r2_std": float(np.std(r2s, ddof=1)),
            "mae_mean": float(np.mean(maes)),
            "mae_std": float(np.std(maes, ddof=1)),
        }
        records.append(rec)
        log.info("[%2d/%d] n_est=%3d max_depth=%s min_leaf=%d -> R2=%.4f +- %.4f",
                 idx, len(grid), n_est, rec["max_depth"], min_leaf,
                 rec["r2_mean"], rec["r2_std"])

    res = pd.DataFrame(records)
    csv_path = OUT_DIR / "hyperparam_sweep.csv"
    res.to_csv(csv_path, index=False)
    log.info("wrote %s", csv_path)

    # Marginal effect summaries
    log.info("--- Marginal effects ---")
    for col in ("n_estimators", "max_depth", "min_samples_leaf"):
        margin = res.groupby(col)["r2_mean"].agg(["mean", "std", "min", "max"]).round(4)
        log.info("%s:\n%s", col, margin.to_string())

    overall = (res["r2_mean"].max(), res["r2_mean"].min(),
               res["r2_mean"].mean(), res["r2_mean"].std())
    log.info("overall R^2 across %d combinations: max=%.4f min=%.4f mean=%.4f std=%.4f",
             len(res), *overall)

    # LaTeX-ready table fragment: rows indexed by min_samples_leaf, columns by n_estimators,
    # one block per max_depth so the structure is compact.
    tex_lines = []
    tex_lines.append("% Auto-generated by phase1c_hyperparam_sensitivity.py")
    tex_lines.append("\\begin{tabular}{lrrrrr}")
    tex_lines.append("\\toprule")
    tex_lines.append("max\\_depth & min\\_samples\\_leaf & " +
                     " & ".join([f"n\\_est={n}" for n in N_ESTIMATORS_GRID]) + " \\\\")
    tex_lines.append("\\midrule")
    for max_d in MAX_DEPTH_GRID:
        for min_leaf in MIN_SAMPLES_LEAF_GRID:
            row_vals = []
            for n_est in N_ESTIMATORS_GRID:
                rec = res[(res["n_estimators"] == n_est) &
                          (res["max_depth"] == ("None" if max_d is None else int(max_d))) &
                          (res["min_samples_leaf"] == min_leaf)].iloc[0]
                row_vals.append(f"{rec['r2_mean']:.3f}")
            tex_lines.append(f"{'None' if max_d is None else int(max_d)} & {min_leaf} & " +
                             " & ".join(row_vals) + " \\\\")
        tex_lines.append("\\midrule")
    tex_lines[-1] = "\\bottomrule"  # replace last midrule with bottomrule
    tex_lines.append("\\end{tabular}")
    tex_path = OUT_DIR / "hyperparam_sweep_table.tex"
    tex_path.write_text("\n".join(tex_lines), encoding="utf-8")
    log.info("wrote %s", tex_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
