"""
phase1d_lightgbm.py
-------------------
Robustness check: re-run Phase 1 with a histogram-binned gradient-boosted
decision-tree estimator (HistGradientBoostingRegressor, same algorithm family
as LightGBM and XGBoost) alongside Ridge and Random Forest, on the combined
feature set and the same 5-fold grouped CV protocol.

Addresses reviewer critique 3.1 (ML stack is simple). The goal is to show that
the in-distribution conclusions of Section 5.1 are not artifacts of choosing
Random Forest, but hold under a modern gradient-boosted decision-tree estimator.

Outputs:
    outputs/phase1d/lightgbm_summary.csv     per-target R^2 and MAE
    outputs/phase1d/three_way_comparison.csv Ridge vs RF vs GBT
    outputs/phase1d/three_way_table.tex      LaTeX-ready table

Run:
    OMP_NUM_THREADS=1 python3 phase1d_lightgbm.py
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

sys.path.insert(0, str(Path(__file__).parent))
from phase1_predictability import (
    DATA_PATH,
    N_SPLITS,
    features_for,
    filter_for_modeling,
)

PROJECT_ROOT = Path("/storage/scratch1/4/nbawana3/furnace-project")
OUT_DIR = PROJECT_ROOT / "outputs" / "phase1d"
OUT_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
    handlers=[
        logging.FileHandler(OUT_DIR / "lightgbm.log", mode="w"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("phase1d")

TARGETS = [
    "eff_cold", "eff_hot", "eff_simmer", "eff_combined",
    "fp_cold", "fp_hot", "fp_simmer",
    "br_cold", "br_hot", "br_simmer",
]
FEATURE_SET = "combined"


def make_gbt_pipeline(num_cols, cat_cols):
    """Standard preprocessing + HistGradientBoostingRegressor with conservative defaults."""
    pre = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), num_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
        ],
        remainder="drop",
    )
    gbt = HistGradientBoostingRegressor(
        max_iter=200,
        learning_rate=0.05,
        max_leaf_nodes=31,
        min_samples_leaf=5,
        l2_regularization=0.0,
        random_state=0,
    )
    return Pipeline([("pre", pre), ("gbt", gbt)])


def grouped_cv_gbt(sub, target, num_cols, cat_cols):
    feature_cols = num_cols + cat_cols
    X = sub[feature_cols].copy()
    y = sub[target].to_numpy()
    groups = sub["src_path"].to_numpy()
    cv = GroupKFold(n_splits=N_SPLITS)
    r2s = []
    maes = []
    for train_idx, test_idx in cv.split(X, y, groups):
        pipe = make_gbt_pipeline(num_cols, cat_cols)
        pipe.fit(X.iloc[train_idx], y[train_idx])
        y_pred = pipe.predict(X.iloc[test_idx])
        r2s.append(r2_score(y[test_idx], y_pred))
        maes.append(mean_absolute_error(y[test_idx], y_pred))
    return r2s, maes


def main():
    log.info("loading %s", DATA_PATH)
    df = pd.read_csv(DATA_PATH)
    df = df[df["replicate_kind"] == "average"].copy()

    records = []
    for target in TARGETS:
        if target not in df.columns:
            log.warning("target %s missing; skipping", target)
            continue
        num_cols, cat_cols = features_for(FEATURE_SET, target, df)
        require_geom = FEATURE_SET in ("geometry", "combined")
        sub = filter_for_modeling(df, target, num_cols, cat_cols, require_geometry=require_geom)
        if len(sub) < N_SPLITS * 2:
            log.warning("target %s has only %d rows after filtering; skipping", target, len(sub))
            continue
        r2s, maes = grouped_cv_gbt(sub, target, num_cols, cat_cols)
        rec = {
            "target": target,
            "n_total": len(sub),
            "r2_mean": float(np.mean(r2s)),
            "r2_std": float(np.std(r2s, ddof=1)),
            "mae_mean": float(np.mean(maes)),
            "mae_std": float(np.std(maes, ddof=1)),
        }
        records.append(rec)
        log.info("%s | n=%d | R2=%.4f +- %.4f | MAE=%.4f",
                 target, len(sub), rec["r2_mean"], rec["r2_std"], rec["mae_mean"])

    gbt_summary = pd.DataFrame(records)
    gbt_summary.to_csv(OUT_DIR / "lightgbm_summary.csv", index=False)
    log.info("wrote %s", OUT_DIR / "lightgbm_summary.csv")

    # Pull Ridge and RF numbers from existing phase1 summary for side-by-side comparison
    p1 = pd.read_csv(PROJECT_ROOT / "outputs" / "phase1" / "summary.csv")
    p1c = p1[p1["features"] == "combined"].copy()

    rows = []
    for target in TARGETS:
        if target not in gbt_summary["target"].values:
            continue
        ridge = p1c[(p1c["target"] == target) & (p1c["model"] == "ridge")]
        rf = p1c[(p1c["target"] == target) & (p1c["model"] == "rf")]
        gbt_row = gbt_summary[gbt_summary["target"] == target].iloc[0]
        rows.append({
            "target": target,
            "n_total": gbt_row["n_total"],
            "r2_ridge": float(ridge["r2_mean"].iloc[0]) if len(ridge) else float("nan"),
            "r2_rf": float(rf["r2_mean"].iloc[0]) if len(rf) else float("nan"),
            "r2_gbt": gbt_row["r2_mean"],
        })

    cmp = pd.DataFrame(rows)
    cmp.to_csv(OUT_DIR / "three_way_comparison.csv", index=False)
    log.info("wrote %s", OUT_DIR / "three_way_comparison.csv")

    pretty = {
        "eff_cold": "Cold-start efficiency",
        "eff_hot": "Hot-start efficiency",
        "eff_simmer": "Simmer-phase efficiency",
        "eff_combined": "Combined-phase efficiency",
        "fp_cold": "Cold-start firepower",
        "fp_hot": "Hot-start firepower",
        "fp_simmer": "Simmer firepower",
        "br_cold": "Cold-start burn rate",
        "br_hot": "Hot-start burn rate",
        "br_simmer": "Simmer burn rate",
    }
    lines = []
    lines.append("% Auto-generated by phase1d_lightgbm.py")
    lines.append("\\begin{tabular}{lrrrr}")
    lines.append("\\toprule")
    lines.append("Target & $n$ & $R^2$ (Ridge) & $R^2$ (RF) & $R^2$ (HGBT) \\\\")
    lines.append("\\midrule")
    for _, r in cmp.iterrows():
        name = pretty.get(r["target"], r["target"]).replace("_", "\\_")
        lines.append(f"{name} & {int(r['n_total'])} & {r['r2_ridge']:.3f} & {r['r2_rf']:.3f} & {r['r2_gbt']:.3f} \\\\")
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    (OUT_DIR / "three_way_table.tex").write_text("\n".join(lines), encoding="utf-8")
    log.info("wrote %s", OUT_DIR / "three_way_table.tex")

    log.info("--- Summary across targets ---")
    log.info("Ridge mean R2 = %.3f", cmp["r2_ridge"].mean())
    log.info("RF    mean R2 = %.3f", cmp["r2_rf"].mean())
    log.info("HGBT  mean R2 = %.3f", cmp["r2_gbt"].mean())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
