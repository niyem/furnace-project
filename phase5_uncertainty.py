"""
phase5_uncertainty.py — Phase 5 of the cookstove modeling pipeline.

Prediction-interval uncertainty quantification for the best Phase-1 / Phase-2
models. Provides per-stove 90% intervals using two complementary methods,
evaluates empirical coverage out-of-sample, and produces parity plots that
make the interval calibration visible.

Two UQ methods:

  1. RF tree-quantile intervals
       Each tree in a RandomForestRegressor makes its own prediction. We take
       the 5th and 95th percentiles across trees as the lower/upper bounds.
       Asymptotic — not calibrated by construction, but cheap and informative.

  2. Split-conformal intervals
       Hold out a calibration subset from the training fold, train on the rest,
       compute the 0.9-quantile of |residual|, use that as the half-width of a
       symmetric ±q band around point predictions. Distribution-free with a
       formal coverage guarantee.

Targets evaluated (the operationally interesting subset from Phase 1/2):
    eff_cold, eff_hot, eff_simmer, eff_combined,
    fp_cold, fp_simmer, br_cold, br_simmer

Grouped 5-fold CV by stove identity. Aggregate per-target coverage and median
interval width across folds.

Inputs:
    data/processed/wbt_wide.csv

Outputs (in outputs/phase5/):
    uq_coverage.csv          per (target, method, fold) — target_cov, empirical_cov, median_width
    uq_summary.md            human-readable summary
    uq_parity_<target>.png   parity plot with intervals for eff_cold, eff_simmer, fp_simmer
    phase5.log

Requires matplotlib.

Run:
    OMP_NUM_THREADS=1 python3 phase5_uncertainty.py
"""

from __future__ import annotations

import logging
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

# =============================================================================
# Configuration
# =============================================================================

PROJECT_ROOT = Path("/storage/scratch1/4/nbawana3/furnace-project")
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "wbt_wide.csv"
OUT_DIR = PROJECT_ROOT / "outputs" / "phase5"
OUT_DIR.mkdir(parents=True, exist_ok=True)

LOG_PATH = OUT_DIR / "phase5.log"
logging.basicConfig(
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
    handlers=[logging.FileHandler(LOG_PATH, mode="w"), logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("phase5")

RANDOM_STATE = 42
N_SPLITS = 5
TARGET_COVERAGE = 0.90       # 90% prediction intervals
CALIB_FRACTION = 0.20        # share of the train fold reserved for conformal calibration
PLOT_TARGETS = ("eff_cold", "eff_simmer", "fp_simmer")

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
# Data + features
# =============================================================================

def load_wide() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df = df[df["replicate_kind"] == "average"].copy()
    eff_cols = [c for c in ("eff_cold", "eff_hot", "eff_simmer") if c in df.columns]
    df["eff_combined"] = df[eff_cols].mean(axis=1, skipna=False)
    df = df.dropna(subset=["src_path"]).copy()
    log.info("loaded %d stoves", len(df))
    return df


def features_for(target: str, df: pd.DataFrame) -> tuple[list[str], list[str]]:
    """Combined feature set: geometry + cross-phase WBT (matching Phase 1/2 best)."""
    geom = [c for c in GEOMETRY_NUMERIC if c in df.columns]
    target_phase = target.split("_")[-1] if target != "eff_combined" else None
    wbt = []
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
        wbt.append(c)
    return geom + wbt, ["material"]


def filter_for_modeling(df: pd.DataFrame, target: str) -> pd.DataFrame:
    sub = df.dropna(subset=[target]).copy()
    sub = sub.dropna(subset=GEOMETRY_NUMERIC)
    sub = sub.dropna(subset=["src_path"])
    return sub


# =============================================================================
# Model factory
# =============================================================================

def build_pipeline(num_cols: list[str], cat_cols: list[str]) -> Pipeline:
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
        n_estimators=200, max_depth=None, min_samples_leaf=2,
        n_jobs=1, random_state=RANDOM_STATE,
    )
    return Pipeline([("pre", pre), ("est", rf)])


# =============================================================================
# UQ methods
# =============================================================================

def tree_quantile_intervals(pipe: Pipeline, X_test: pd.DataFrame,
                            alpha: float = (1 - TARGET_COVERAGE) / 2) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Get per-tree predictions from a fitted RF and return (lower, median, upper)
    at quantiles (alpha, 0.5, 1-alpha). Returns arrays of length n_test.
    """
    # Apply preprocessing
    pre = pipe.named_steps["pre"]
    rf: RandomForestRegressor = pipe.named_steps["est"]
    X_proc = pre.transform(X_test)
    # Stack per-tree predictions: shape (n_trees, n_test)
    tree_preds = np.vstack([t.predict(X_proc) for t in rf.estimators_])
    lower = np.quantile(tree_preds, alpha, axis=0)
    upper = np.quantile(tree_preds, 1 - alpha, axis=0)
    median = np.quantile(tree_preds, 0.5, axis=0)
    return lower, median, upper


def split_conformal_q(pipe: Pipeline, X_cal: pd.DataFrame, y_cal: np.ndarray,
                      target_cov: float = TARGET_COVERAGE) -> float:
    """
    Compute the split-conformal half-width: the (target_cov)-quantile of
    |y_cal - pred_cal|.
    """
    pred = pipe.predict(X_cal)
    resid = np.abs(y_cal - pred)
    # Use the (n_cal+1)*(1-α)/n_cal-quantile per Romano et al., but for clarity
    # use the simple high-quantile of |residuals|.
    n = len(resid)
    q_idx = int(np.ceil((n + 1) * target_cov)) - 1
    q_idx = max(0, min(n - 1, q_idx))
    q = np.sort(resid)[q_idx]
    return float(q)


def evaluate_cell(df: pd.DataFrame, target: str, fold_seed: int = RANDOM_STATE) -> dict:
    """
    For one (target) run: grouped CV; on each fold split (train, cal) -> conformal,
    also report tree-quantile intervals on the test set.
    """
    sub = filter_for_modeling(df, target)
    num_cols, cat_cols = features_for(target, sub)
    feat_cols = num_cols + cat_cols
    X_all = sub[feat_cols]
    y_all = sub[target].astype(float).values
    groups = sub["src_path"]
    cv = GroupKFold(n_splits=N_SPLITS)

    rng = np.random.default_rng(fold_seed)
    fold_rows = []
    pred_rows = []  # per-stove predictions for plotting

    for fold, (tr, te) in enumerate(cv.split(X_all, y_all, groups), 1):
        # Within-train split: hold out CALIB_FRACTION of stoves (group-aware)
        tr_groups = groups.iloc[tr].unique()
        rng.shuffle(tr_groups)
        n_cal_groups = max(2, int(len(tr_groups) * CALIB_FRACTION))
        cal_groups = set(tr_groups[:n_cal_groups])
        cal_mask = groups.iloc[tr].isin(cal_groups).values
        cal_idx = tr[cal_mask]
        fit_idx = tr[~cal_mask]

        pipe = build_pipeline(num_cols, cat_cols)
        pipe.fit(X_all.iloc[fit_idx], y_all[fit_idx])

        # Test-set point predictions
        y_hat = pipe.predict(X_all.iloc[te])
        r2 = r2_score(y_all[te], y_hat)
        mae = mean_absolute_error(y_all[te], y_hat)

        # Method A: tree-quantile
        ta_lo, ta_med, ta_hi = tree_quantile_intervals(pipe, X_all.iloc[te])
        ta_in = ((y_all[te] >= ta_lo) & (y_all[te] <= ta_hi)).mean()
        ta_width = np.median(ta_hi - ta_lo)

        # Method B: split conformal
        q = split_conformal_q(pipe, X_all.iloc[cal_idx], y_all[cal_idx])
        sc_lo = y_hat - q
        sc_hi = y_hat + q
        sc_in = ((y_all[te] >= sc_lo) & (y_all[te] <= sc_hi)).mean()
        sc_width = float(2 * q)

        fold_rows.append({
            "target": target, "fold": fold,
            "n_fit": int(len(fit_idx)), "n_cal": int(len(cal_idx)), "n_test": int(len(te)),
            "r2": float(r2), "mae": float(mae),
            "target_cov": TARGET_COVERAGE,
            "tree_coverage": float(ta_in),
            "tree_median_width": float(ta_width),
            "conformal_q": q,
            "conformal_coverage": float(sc_in),
            "conformal_width": sc_width,
        })

        # Save per-stove predictions for plotting (only for plot-target folds)
        for i, te_i in enumerate(te):
            pred_rows.append({
                "target": target, "fold": fold,
                "src_path": sub.iloc[te_i]["src_path"],
                "format": sub.iloc[te_i].get("format"),
                "actual": float(y_all[te_i]),
                "predicted": float(y_hat[i]),
                "tree_lo": float(ta_lo[i]),
                "tree_hi": float(ta_hi[i]),
                "conf_lo": float(sc_lo[i]),
                "conf_hi": float(sc_hi[i]),
            })

    folds_df = pd.DataFrame(fold_rows)
    preds_df = pd.DataFrame(pred_rows)
    return {"folds": folds_df, "predictions": preds_df}


# =============================================================================
# Plot
# =============================================================================

def plot_parity_with_intervals(preds: pd.DataFrame, target: str, out_path: Path) -> None:
    """Two-panel parity plot: tree-quantile vs split-conformal intervals."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.2), sharey=True)
    methods = [("tree", "tree_lo", "tree_hi", "Tree-quantile (RF)"),
               ("conformal", "conf_lo", "conf_hi", "Split-conformal")]
    y_min = min(preds["actual"].min(), preds["predicted"].min())
    y_max = max(preds["actual"].max(), preds["predicted"].max())
    pad = 0.05 * (y_max - y_min)
    lo_lim = y_min - pad
    hi_lim = y_max + pad

    for ax, (key, lo_col, hi_col, title) in zip(axes, methods):
        # Sort by actual for cleaner display
        p = preds.sort_values("actual").reset_index(drop=True)
        # Coverage flag
        inside = (p["actual"] >= p[lo_col]) & (p["actual"] <= p[hi_col])
        cov = inside.mean()
        median_width = (p[hi_col] - p[lo_col]).median()
        # Color points by inside/outside
        yerr_lo = np.clip(p["predicted"] - p[lo_col], 0, None)
        yerr_hi = np.clip(p[hi_col] - p["predicted"], 0, None)
        ax.errorbar(
            p["actual"], p["predicted"],
            yerr=[yerr_lo, yerr_hi],
            fmt="o", ms=3, capsize=2, ecolor="lightgray", elinewidth=0.7,
            color="C0", alpha=0.7,
        )
        # Mark outside-interval points in red
        out = p[~inside]
        ax.scatter(out["actual"], out["predicted"], s=14, color="red",
                   label=f"outside interval (n={len(out)})", zorder=3)
        ax.plot([lo_lim, hi_lim], [lo_lim, hi_lim], "k--", lw=0.8, alpha=0.5)
        ax.set_xlim(lo_lim, hi_lim)
        ax.set_ylim(lo_lim, hi_lim)
        ax.set_xlabel(f"Actual {target}")
        ax.set_ylabel(f"Predicted {target}")
        ax.set_title(f"{title}\ncoverage={cov:.0%} (target {TARGET_COVERAGE:.0%}), "
                     f"median width={median_width:.4f}")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper left", fontsize=9)
    fig.suptitle(f"Prediction intervals — `{target}`", fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(out_path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    log.info("wrote %s", out_path)


# =============================================================================
# Reporting
# =============================================================================

def write_md(coverage: pd.DataFrame, out_path: Path) -> None:
    lines = [
        "# Phase 5: Prediction-Interval Uncertainty Quantification",
        "",
        f"Target coverage: **{TARGET_COVERAGE:.0%}**. Random Forest base model "
        "(200 trees) on combined features, grouped 5-fold CV by stove identity. "
        "Calibration set: {:.0%} of each training fold's stoves.".format(CALIB_FRACTION),
        "",
        "Two UQ methods evaluated:",
        "1. **Tree-quantile** — per-tree predictions, take 5th/95th percentile across trees",
        "2. **Split-conformal** — calibrate ±q from held-out residual quantile",
        "",
        "## Aggregate coverage (mean across folds)",
        "",
        "| Target | n_test (mean) | R² | MAE | Tree coverage | Tree width | Conformal coverage | Conformal width |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    by_target = (
        coverage.groupby("target")
        .agg(
            n_test_mean=("n_test", "mean"),
            r2_mean=("r2", "mean"),
            mae_mean=("mae", "mean"),
            tree_cov=("tree_coverage", "mean"),
            tree_width=("tree_median_width", "mean"),
            conf_cov=("conformal_coverage", "mean"),
            conf_width=("conformal_width", "mean"),
        )
        .reset_index()
        .sort_values("r2_mean", ascending=False)
    )
    for _, r in by_target.iterrows():
        lines.append(
            f"| `{r['target']}` | {r['n_test_mean']:.0f} | "
            f"{r['r2_mean']:+.3f} | {r['mae_mean']:.4f} | "
            f"{r['tree_cov']:.1%} | {r['tree_width']:.4f} | "
            f"{r['conf_cov']:.1%} | {r['conf_width']:.4f} |"
        )
    lines.append("")
    lines.append(
        "Tree-quantile intervals are **asymptotic** — they reflect tree-ensemble "
        "disagreement, not formal coverage guarantee. Split-conformal intervals are "
        "**distribution-free** with formal guarantee: empirical coverage should be "
        "close to the target. Wide gaps between empirical and target coverage indicate "
        "miscalibration."
    )
    lines.append("")
    out_path.write_text("\n".join(lines))


# =============================================================================
# Orchestration
# =============================================================================

def run() -> None:
    df = load_wide()
    all_folds = []
    all_preds = []
    for target in TARGETS:
        if target not in df.columns:
            continue
        log.info("=== target: %s ===", target)
        res = evaluate_cell(df, target)
        all_folds.append(res["folds"])
        all_preds.append(res["predictions"])
        # Log per-fold summary
        for _, r in res["folds"].iterrows():
            log.info("  fold %d | R²=%+.3f MAE=%.4f | tree_cov=%.1f%% width=%.4f | "
                     "conf_cov=%.1f%% width=%.4f",
                     r["fold"], r["r2"], r["mae"],
                     r["tree_coverage"] * 100, r["tree_median_width"],
                     r["conformal_coverage"] * 100, r["conformal_width"])

    coverage = pd.concat(all_folds, ignore_index=True)
    preds = pd.concat(all_preds, ignore_index=True)
    coverage.to_csv(OUT_DIR / "uq_coverage.csv", index=False)
    preds.to_csv(OUT_DIR / "uq_predictions.csv", index=False)
    log.info("wrote uq_coverage.csv (%d rows) and uq_predictions.csv (%d rows)",
             len(coverage), len(preds))

    # Plots for the operationally interesting targets
    for tgt in PLOT_TARGETS:
        p = preds[preds["target"] == tgt]
        if not p.empty:
            plot_parity_with_intervals(p, tgt, OUT_DIR / f"uq_parity_{tgt}.png")

    write_md(coverage, OUT_DIR / "uq_summary.md")
    log.info("wrote uq_summary.md")

    # Console aggregate
    by_target = (
        coverage.groupby("target")
        .agg(
            tree_cov=("tree_coverage", "mean"),
            tree_width=("tree_median_width", "mean"),
            conf_cov=("conformal_coverage", "mean"),
            conf_width=("conformal_width", "mean"),
            r2_mean=("r2", "mean"),
        )
        .reset_index()
        .sort_values("r2_mean", ascending=False)
    )
    log.info("\n=== Coverage summary (target = %.0f%%) ===\n%s",
             TARGET_COVERAGE * 100,
             by_target.round(3).to_string(index=False))


if __name__ == "__main__":
    run()
