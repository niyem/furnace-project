"""
phase4_years_in_service.py — Phase 4 of the cookstove modeling pipeline.

Two complementary analyses around years-in-service:

  1. Years-in-service regression
     Target:   years_in_service = campaign_year − sale_year
     Features: WBT measurements + stove geometry
     Question: given an undocumented stove's WBT readings, can we estimate how
               long it has been in operation? MAE in years tells us.

  2. Cross-sectional cohort visualization
     For each format, plot mean efficiency (cold / hot / simmer / combined) by
     sale_year, with 95% CI error bars. Reveals visually whether stoves of the
     same size show performance drift across manufacturing-year cohorts.

`campaign_year` is parsed from the top-level campaign folder name (e.g.
"Rapport Toyola 2018" → 2018), which is more reliable than the General
Information's "Test Year" field (sometimes incorrectly filled with sale year).

Inputs:
    data/processed/wbt_wide.csv

Outputs (in outputs/phase4/):
    cohort_stats.csv              per (format, sale_year, target) — n, mean, std, 95% CI
    yis_regression_summary.csv    per (model, features) — MAE in years
    yis_regression_folds.csv      per-fold MAE
    efficiency_by_cohort.png      4-panel: cold / hot / simmer / combined efficiency
    yis_summary.md                human-readable narrative + tables
    phase4.log

Requires matplotlib (install user-site if missing):
    python3 -m pip install --user matplotlib

Run:
    OMP_NUM_THREADS=1 python3 phase4_years_in_service.py
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
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from scipy import stats

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

# =============================================================================
# Configuration
# =============================================================================

PROJECT_ROOT = Path("/storage/scratch1/4/nbawana3/furnace-project")
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "wbt_wide.csv"
OUT_DIR = PROJECT_ROOT / "outputs" / "phase4"
OUT_DIR.mkdir(parents=True, exist_ok=True)

LOG_PATH = OUT_DIR / "phase4.log"
logging.basicConfig(
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
    handlers=[logging.FileHandler(LOG_PATH, mode="w"), logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("phase4")

RANDOM_STATE = 42
N_SPLITS = 5
MIN_PER_COHORT = 3  # require at least this many stoves per (format, sale_year) cell to plot

EFFICIENCY_PHASES = ["cold", "hot", "simmer", "combined"]
GEOMETRY_NUMERIC = [
    "height_cm", "outside_d_cm", "chamber_d_cm", "chamber_depth_cm",
    "inlet_w_cm", "inlet_h_cm", "inlet_area_cm2", "chamber_volume_cm3",
]
WBT_METRIC_PREFIXES = ["eff", "fp", "br", "sfc", "tboil"]


# =============================================================================
# Data loading + campaign_year derivation
# =============================================================================

YEAR_RE = re.compile(r"(20\d{2})")


def derive_campaign_year(campaign: object) -> int | None:
    """Pull the first 4-digit year from the campaign folder name."""
    if campaign is None or (isinstance(campaign, float) and np.isnan(campaign)):
        return None
    m = YEAR_RE.search(str(campaign))
    return int(m.group(1)) if m else None


def load_wide() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df = df[df["replicate_kind"] == "average"].copy()
    eff_cols = [c for c in ("eff_cold", "eff_hot", "eff_simmer") if c in df.columns]
    df["eff_combined"] = df[eff_cols].mean(axis=1, skipna=False)
    df = df.dropna(subset=["src_path"]).copy()
    df["campaign_year"] = df["campaign"].apply(derive_campaign_year)

    # Years-in-service = campaign_year - sale_year (only where both known)
    mask = df["sale_year"].notna() & df["campaign_year"].notna()
    df.loc[mask, "years_in_service"] = (
        df.loc[mask, "campaign_year"].astype(int) - df.loc[mask, "sale_year"].astype(int)
    )
    log.info("loaded %d stoves", len(df))
    log.info("sale_year coverage: %d / %d", df["sale_year"].notna().sum(), len(df))
    log.info("campaign_year coverage: %d / %d",
             df["campaign_year"].notna().sum(), len(df))
    log.info("years_in_service derivable: %d stoves",
             df["years_in_service"].notna().sum())
    return df


# =============================================================================
# Cohort descriptive stats per (format, sale_year, target)
# =============================================================================

def cohort_stats(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    sub = df.dropna(subset=["format", "sale_year"]).copy()
    sub["sale_year"] = sub["sale_year"].astype(int)
    for target in [f"eff_{p}" for p in EFFICIENCY_PHASES]:
        if target not in sub.columns:
            continue
        grp = sub.dropna(subset=[target]).groupby(["format", "sale_year"])[target]
        for (fmt, yr), s in grp:
            n = int(len(s))
            if n < 2:
                continue
            m = float(s.mean())
            sd = float(s.std(ddof=1))
            sem = sd / np.sqrt(n)
            t_crit = float(stats.t.ppf(0.975, df=n - 1))
            rows.append(dict(
                target=target, format=fmt, sale_year=yr,
                n=n,
                mean=round(m, 5),
                std=round(sd, 5),
                sem=round(sem, 5),
                ci_low=round(m - t_crit * sem, 5),
                ci_high=round(m + t_crit * sem, 5),
            ))
    return pd.DataFrame(rows)


# =============================================================================
# Predicting years_in_service from features
# =============================================================================

def features_for_yis(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    """All WBT-derived metric cols + geometry. No leakage of sale/campaign year."""
    geom = [c for c in GEOMETRY_NUMERIC if c in df.columns]
    wbt = [c for c in df.columns
           if any(c.startswith(p + "_") for p in WBT_METRIC_PREFIXES)
           and not c.endswith("_combined")]
    return geom + wbt, ["material", "format"]


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
        raise ValueError(model_name)
    return Pipeline([("pre", pre), ("est", est)])


def yis_regression(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Train Ridge and RF to predict years_in_service. Grouped 5-fold CV by stove.
    Returns (per-fold table, summary table with mean ± std).
    """
    sub = df.dropna(subset=["years_in_service"]).copy()
    sub = sub.dropna(subset=GEOMETRY_NUMERIC)
    if len(sub) < N_SPLITS * 2:
        log.warning("not enough rows with years_in_service: %d", len(sub))
        return pd.DataFrame(), pd.DataFrame()
    num_cols, cat_cols = features_for_yis(sub)
    log.info("years_in_service modeling on %d stoves, %d features",
             len(sub), len(num_cols) + len(cat_cols))
    y = sub["years_in_service"].astype(float).values
    log.info("  years_in_service range: %d–%d, mean=%.2f, std=%.2f",
             int(y.min()), int(y.max()), y.mean(), y.std())

    folds_rows = []
    cv = GroupKFold(n_splits=N_SPLITS)
    groups = sub["src_path"]
    for model_name in ("ridge", "rf"):
        for fold, (tr, te) in enumerate(cv.split(sub[num_cols + cat_cols], y, groups), 1):
            pipe = make_pipeline(model_name, num_cols, cat_cols)
            pipe.fit(sub.iloc[tr][num_cols + cat_cols], y[tr])
            pred = pipe.predict(sub.iloc[te][num_cols + cat_cols])
            folds_rows.append({
                "model": model_name, "fold": fold,
                "n_train": int(len(tr)), "n_test": int(len(te)),
                "mae_years": float(mean_absolute_error(y[te], pred)),
                "r2": float(r2_score(y[te], pred)),
                "y_test_mean": float(y[te].mean()),
                "y_test_std": float(y[te].std()),
            })
    folds_df = pd.DataFrame(folds_rows)
    summary = (
        folds_df.groupby("model")
        .agg(
            n_total=("n_test", lambda s: int(s.sum())),
            mae_mean=("mae_years", "mean"),
            mae_std=("mae_years", "std"),
            r2_mean=("r2", "mean"),
            r2_std=("r2", "std"),
        )
        .reset_index()
    )
    for c in ("mae_mean", "mae_std"):
        summary[c] = summary[c].round(3)
    for c in ("r2_mean", "r2_std"):
        summary[c] = summary[c].round(3)
    return folds_df, summary


# =============================================================================
# Visualization
# =============================================================================

def plot_efficiency_by_cohort(df: pd.DataFrame, cohort: pd.DataFrame, out_path: Path) -> None:
    """
    4-panel figure: eff_cold / eff_hot / eff_simmer / eff_combined vs sale_year,
    one line per format, mean ± 95% CI from the cohort table.
    """
    formats_present = sorted(cohort["format"].unique())
    cmap = plt.get_cmap("tab10")
    fmt_color = {f: cmap(i % 10) for i, f in enumerate(formats_present)}
    fig, axes = plt.subplots(2, 2, figsize=(11, 8), sharex=True)
    for ax, phase in zip(axes.ravel(), EFFICIENCY_PHASES):
        target = f"eff_{phase}"
        sub = cohort[(cohort["target"] == target) & (cohort["n"] >= MIN_PER_COHORT)].copy()
        if sub.empty:
            ax.set_title(f"{phase} — no cohorts with n≥{MIN_PER_COHORT}")
            continue
        for fmt in formats_present:
            d = sub[sub["format"] == fmt].sort_values("sale_year")
            if d.empty:
                continue
            ax.errorbar(
                d["sale_year"], d["mean"],
                yerr=[d["mean"] - d["ci_low"], d["ci_high"] - d["mean"]],
                marker="o", capsize=3, label=fmt, color=fmt_color[fmt],
            )
        ax.set_title(f"Thermal efficiency — {phase}")
        ax.set_ylabel("Efficiency (fraction)")
        ax.grid(True, alpha=0.3)
    for ax in axes[1]:
        ax.set_xlabel("Year of sale / start of service")
    # Legend on the first subplot
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=min(6, len(labels)), bbox_to_anchor=(0.5, -0.02))
    fig.suptitle("Per-format efficiency by sale-year cohort (mean ± 95% CI)", fontsize=13)
    fig.tight_layout(rect=[0, 0.03, 1, 0.96])
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    log.info("wrote %s", out_path)


# =============================================================================
# Reporting
# =============================================================================

def write_md(yis_summary: pd.DataFrame, cohort: pd.DataFrame, out_path: Path) -> None:
    lines = [
        "# Phase 4: Years in Service and Cohort Analysis",
        "",
        "**Years in service** = `campaign_year − sale_year`. `sale_year` is parsed from "
        "Toyola HxC filenames (`HS2014N1.xlsx` → 2014). `campaign_year` is parsed from "
        "the campaign folder name (`Rapport Toyola 2018` → 2018). Both available for the "
        "Toyola HxC subset of the dataset.",
        "",
        "## 1. Can WBT data + geometry predict years in service?",
        "",
        "Random Forest and Ridge, grouped 5-fold CV by stove identity. MAE is in years.",
        "If MAE is close to the standard deviation of `years_in_service`, the model is "
        "essentially predicting the dataset mean — it has no real signal.",
        "",
        "| Model | n_total | MAE (years, mean ± std) | R² (mean ± std) |",
        "|---|---:|---|---|",
    ]
    for _, r in yis_summary.iterrows():
        lines.append(
            f"| {r['model']} | {r['n_total']} | "
            f"{r['mae_mean']:.3f} ± {r['mae_std']:.3f} | "
            f"{r['r2_mean']:+.3f} ± {r['r2_std']:.3f} |"
        )
    lines.append("")
    lines.append("## 2. Per-cohort efficiency table")
    lines.append("")
    lines.append("Mean ± 95% CI per (format × sale_year) for each efficiency phase. "
                 "See `cohort_stats.csv` for the full table; below is the combined-efficiency subset.")
    lines.append("")
    eff_c = cohort[cohort["target"] == "eff_combined"].sort_values(["format", "sale_year"])
    if eff_c.empty:
        lines.append("(no eff_combined cohort rows)")
    else:
        lines.append("| Format | Sale year | n | Mean | 95% CI |")
        lines.append("|---|---:|---:|---:|---|")
        for _, r in eff_c.iterrows():
            lines.append(
                f"| {r['format']} | {r['sale_year']} | {r['n']} | "
                f"{r['mean']:.4f} | [{r['ci_low']:.4f}, {r['ci_high']:.4f}] |"
            )
    lines.append("")
    lines.append("## 3. Visualization")
    lines.append("")
    lines.append("![Efficiency by cohort](efficiency_by_cohort.png)")
    lines.append("")
    out_path.write_text("\n".join(lines))


# =============================================================================
# Orchestration
# =============================================================================

def run() -> None:
    df = load_wide()

    # Show a few sanity-check rows: sale_year, campaign_year, years_in_service
    sanity = df.dropna(subset=["sale_year", "campaign_year"]).sample(
        n=min(8, df["years_in_service"].notna().sum()), random_state=RANDOM_STATE
    )
    log.info("\nSanity check — random rows of (sale_year, campaign, campaign_year, years_in_service):")
    log.info("\n%s", sanity[["sale_year", "campaign", "campaign_year", "years_in_service"]].to_string(index=False))

    cohort = cohort_stats(df)
    cohort.to_csv(OUT_DIR / "cohort_stats.csv", index=False)
    log.info("wrote cohort_stats.csv (%d rows)", len(cohort))

    folds_df, yis_summary = yis_regression(df)
    if not folds_df.empty:
        folds_df.to_csv(OUT_DIR / "yis_regression_folds.csv", index=False)
        yis_summary.to_csv(OUT_DIR / "yis_regression_summary.csv", index=False)
        log.info("wrote yis_regression_summary.csv:\n%s", yis_summary.to_string(index=False))

    plot_efficiency_by_cohort(df, cohort, OUT_DIR / "efficiency_by_cohort.png")

    write_md(yis_summary, cohort, OUT_DIR / "yis_summary.md")
    log.info("wrote yis_summary.md")


if __name__ == "__main__":
    run()
