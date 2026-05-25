"""
regenerate_figures.py — Publication-ready figures for the cookstove manuscript.

Reads cached results from Phases 1–5 plus the cleaned wide-format dataset and
emits LaTeX-ready figures with the following manuscript conventions:

  * No suptitle, no subplot titles (those go in the LaTeX \\caption{...})
  * Panel labels (a), (b), (c), (d) in the upper-left of each subplot, bold
  * A small italic sub-caption below the panel letter for orientation
  * Coverage / R² / interval-width statistics REMOVED from the figure
    (those belong in the LaTeX caption text)
  * Output as BOTH PNG (for preview) and PDF (vector, for \\includegraphics)

All figures saved to outputs/figures_pub/ so there is one canonical location
for everything that goes into the manuscript.

Figures produced:

    fig_efficiency_distributions   KDE overlay of cold / hot / simmer / combined efficiency
    fig_efficiency_boxplots        Boxplot of efficiency phases
    fig_efficiency_violin          Violin plot of efficiency phases
    fig_phase_correlation          Correlation heatmap between phase efficiencies
    fig_efficiency_overview        4-panel summary: (a) KDE (b) box (c) violin (d) corr
    fig_efficiency_by_cohort       Per-format mean ± 95% CI by sale_year (Phase 4)
    fig_phase2_importance          Top-10 permutation importance for 3 representative targets (Phase 2)
    fig_phase3_ood                 OOD R² by probe and target family (Phase 3)
    fig_uq_parity_eff_cold         90% prediction intervals, eff_cold (Phase 5)
    fig_uq_parity_eff_simmer       90% prediction intervals, eff_simmer
    fig_uq_parity_fp_simmer        90% prediction intervals, fp_simmer

Inputs:
    data/processed/wbt_wide.csv
    outputs/phase2/permutation_importance.csv
    outputs/phase3/ood_results.csv
    outputs/phase4/cohort_stats.csv
    outputs/phase5/uq_predictions.csv

Outputs (in outputs/figures_pub/):
    fig_*.png   PNG preview
    fig_*.pdf   PDF for LaTeX inclusion
    regenerate_figures.log

Run:
    python3 regenerate_figures.py
"""

from __future__ import annotations

import logging
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

# =============================================================================
# Configuration
# =============================================================================

PROJECT_ROOT = Path("/storage/scratch1/4/nbawana3/furnace-project")
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "wbt_wide.csv"
PHASE2_PERM = PROJECT_ROOT / "outputs" / "phase2" / "permutation_importance.csv"
PHASE3_OOD = PROJECT_ROOT / "outputs" / "phase3" / "ood_results.csv"
PHASE4_CSV = PROJECT_ROOT / "outputs" / "phase4" / "cohort_stats.csv"
PHASE5_PREDS = PROJECT_ROOT / "outputs" / "phase5" / "uq_predictions.csv"
OUT_DIR = PROJECT_ROOT / "outputs" / "figures_pub"
OUT_DIR.mkdir(parents=True, exist_ok=True)

LOG_PATH = OUT_DIR / "regenerate_figures.log"
logging.basicConfig(
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
    handlers=[logging.FileHandler(LOG_PATH, mode="w"), logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("regen")

plt.rcParams.update({
    # Larger fonts for publication-grade legibility
    "font.size": 12,
    "axes.labelsize": 12,
    "axes.titlesize": 12,
    "xtick.labelsize": 11,
    "ytick.labelsize": 11,
    "legend.fontsize": 10,
    "figure.titlesize": 13,
    # Consistent line thicknesses
    "axes.linewidth": 0.9,
    "lines.linewidth": 1.4,
    "patch.linewidth": 0.6,
    "xtick.major.width": 0.9,
    "ytick.major.width": 0.9,
    # Subtle grid for readability when grid is on
    "grid.linewidth": 0.6,
    "grid.alpha": 0.35,
    # PDF font embedding for cleaner LaTeX inclusion
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

PANEL_LABELS = ["(a)", "(b)", "(c)", "(d)", "(e)", "(f)"]
MIN_PER_COHORT = 3
EFFICIENCY_PHASES = ["cold", "hot", "simmer", "combined"]
PHASE_DISPLAY = {
    "cold": "cold start",
    "hot": "hot start",
    "simmer": "simmer",
    "combined": "combined",
}
# Okabe-Ito colorblind-safe palette (Okabe & Ito; jfly.uni-koeln.de/color/)
# Distinguishable by deuteranopes, protanopes, and tritanopes.
PHASE_COLORS = {
    "cold": "#0072B2",
    "hot": "#D55E00",
    "simmer": "#009E73",
    "combined": "#CC79A7",
}


def add_panel_label(ax, idx: int, sub_caption: str | None = None) -> None:
    """Bold (a), (b), ... in the upper-left, with optional italic sub-caption below."""
    ax.text(
        0.02, 0.98, PANEL_LABELS[idx],
        transform=ax.transAxes, ha="left", va="top",
        fontsize=12, fontweight="bold",
    )
    if sub_caption:
        ax.text(
            0.02, 0.91, sub_caption,
            transform=ax.transAxes, ha="left", va="top",
            fontsize=10, style="italic",
        )


def save_pair(fig, stem: str) -> None:
    """Save a figure as both PNG (preview) and PDF (LaTeX)."""
    png_path = OUT_DIR / f"{stem}.png"
    pdf_path = OUT_DIR / f"{stem}.pdf"
    fig.savefig(png_path, dpi=220, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    log.info("wrote %s and %s", png_path.name, pdf_path.name)


# =============================================================================
# Load wide data and compute efficiency_combined
# =============================================================================

def load_efficiency_phases() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df = df[df["replicate_kind"] == "average"].copy()
    eff_cols = [c for c in ("eff_cold", "eff_hot", "eff_simmer") if c in df.columns]
    df["eff_combined"] = df[eff_cols].mean(axis=1, skipna=False)
    # Convert wide -> long for phase-comparison plots
    rows = []
    for phase in EFFICIENCY_PHASES:
        col = f"eff_{phase}"
        if col not in df.columns:
            continue
        sub = df.dropna(subset=[col])
        for _, r in sub.iterrows():
            rows.append({
                "phase": PHASE_DISPLAY[phase],
                "phase_key": phase,
                "efficiency": float(r[col]),
                "format": r.get("format"),
                "material": r.get("material"),
                "brand": r.get("brand"),
            })
    long_df = pd.DataFrame(rows)
    log.info("loaded %d wide rows; %d long phase observations",
             len(df), len(long_df))
    return long_df


# =============================================================================
# Single-panel descriptive figures (from wide data)
# =============================================================================

def fig_distributions(long_df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    for phase in EFFICIENCY_PHASES:
        d = long_df[long_df["phase_key"] == phase]["efficiency"].values
        if len(d) < 5:
            continue
        # Simple KDE via histogram-with-density + smoothing
        ax.hist(d, bins=40, density=True, alpha=0.45,
                color=PHASE_COLORS[phase], label=PHASE_DISPLAY[phase])
    ax.set_xlabel("Thermal efficiency (fraction)")
    ax.set_ylabel("Density")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", frameon=True)
    fig.tight_layout()
    save_pair(fig, "fig_efficiency_distributions")
    plt.close(fig)


def fig_boxplots(long_df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    order = [PHASE_DISPLAY[p] for p in EFFICIENCY_PHASES]
    data = [long_df[long_df["phase"] == p]["efficiency"].values for p in order]
    bp = ax.boxplot(data, labels=order, patch_artist=True,
                    medianprops=dict(color="black"))
    for patch, phase in zip(bp["boxes"], EFFICIENCY_PHASES):
        patch.set_facecolor(PHASE_COLORS[phase])
        patch.set_alpha(0.55)
    ax.set_xlabel("Operational phase")
    ax.set_ylabel("Thermal efficiency (fraction)")
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    save_pair(fig, "fig_efficiency_boxplots")
    plt.close(fig)


def fig_violin(long_df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    order = [PHASE_DISPLAY[p] for p in EFFICIENCY_PHASES]
    data = [long_df[long_df["phase"] == p]["efficiency"].values for p in order]
    vp = ax.violinplot(data, showmeans=True, showmedians=True)
    for body, phase in zip(vp["bodies"], EFFICIENCY_PHASES):
        body.set_facecolor(PHASE_COLORS[phase])
        body.set_alpha(0.55)
    ax.set_xticks(range(1, len(order) + 1))
    ax.set_xticklabels(order)
    ax.set_xlabel("Operational phase")
    ax.set_ylabel("Thermal efficiency (fraction)")
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    save_pair(fig, "fig_efficiency_violin")
    plt.close(fig)


def fig_phase_correlation() -> None:
    df = pd.read_csv(DATA_PATH)
    df = df[df["replicate_kind"] == "average"].copy()
    eff_cols = [c for c in ("eff_cold", "eff_hot", "eff_simmer") if c in df.columns]
    df["eff_combined"] = df[eff_cols].mean(axis=1, skipna=False)
    cols = ["eff_cold", "eff_hot", "eff_simmer", "eff_combined"]
    cols = [c for c in cols if c in df.columns]
    M = df[cols].dropna().corr()
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    im = ax.imshow(M.values, vmin=-1, vmax=1, cmap="RdBu_r")
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels([c.replace("eff_", "") for c in cols], rotation=0)
    ax.set_yticks(range(len(cols)))
    ax.set_yticklabels([c.replace("eff_", "") for c in cols])
    for i in range(len(cols)):
        for j in range(len(cols)):
            val = M.iloc[i, j]
            ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                    color="white" if abs(val) > 0.6 else "black", fontsize=10)
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Pearson r")
    ax.set_xlabel("Phase efficiency")
    ax.set_ylabel("Phase efficiency")
    fig.tight_layout()
    save_pair(fig, "fig_phase_correlation")
    plt.close(fig)


# =============================================================================
# 4-panel overview (combines distribution / box / violin / correlation)
# =============================================================================

def fig_efficiency_overview(long_df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(11, 8))

    # (a) Distributions
    ax = axes[0, 0]
    for phase in EFFICIENCY_PHASES:
        d = long_df[long_df["phase_key"] == phase]["efficiency"].values
        if len(d) < 5:
            continue
        ax.hist(d, bins=40, density=True, alpha=0.45,
                color=PHASE_COLORS[phase], label=PHASE_DISPLAY[phase])
    ax.set_xlabel("Thermal efficiency (fraction)")
    ax.set_ylabel("Density")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", fontsize=9)
    add_panel_label(ax, 0, "distribution")

    # (b) Boxplot
    ax = axes[0, 1]
    order = [PHASE_DISPLAY[p] for p in EFFICIENCY_PHASES]
    data = [long_df[long_df["phase"] == p]["efficiency"].values for p in order]
    bp = ax.boxplot(data, labels=order, patch_artist=True,
                    medianprops=dict(color="black"))
    for patch, phase in zip(bp["boxes"], EFFICIENCY_PHASES):
        patch.set_facecolor(PHASE_COLORS[phase]); patch.set_alpha(0.55)
    ax.set_ylabel("Efficiency (fraction)")
    ax.grid(True, axis="y", alpha=0.3)
    add_panel_label(ax, 1, "boxplot")

    # (c) Violin
    ax = axes[1, 0]
    vp = ax.violinplot(data, showmeans=True, showmedians=True)
    for body, phase in zip(vp["bodies"], EFFICIENCY_PHASES):
        body.set_facecolor(PHASE_COLORS[phase]); body.set_alpha(0.55)
    ax.set_xticks(range(1, len(order) + 1))
    ax.set_xticklabels(order)
    ax.set_xlabel("Operational phase")
    ax.set_ylabel("Efficiency (fraction)")
    ax.grid(True, axis="y", alpha=0.3)
    add_panel_label(ax, 2, "violin")

    # (d) Correlation
    ax = axes[1, 1]
    df = pd.read_csv(DATA_PATH)
    df = df[df["replicate_kind"] == "average"].copy()
    eff_cols = [c for c in ("eff_cold", "eff_hot", "eff_simmer") if c in df.columns]
    df["eff_combined"] = df[eff_cols].mean(axis=1, skipna=False)
    cols = [c for c in ("eff_cold", "eff_hot", "eff_simmer", "eff_combined") if c in df.columns]
    M = df[cols].dropna().corr()
    im = ax.imshow(M.values, vmin=-1, vmax=1, cmap="RdBu_r")
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels([c.replace("eff_", "") for c in cols])
    ax.set_yticks(range(len(cols)))
    ax.set_yticklabels([c.replace("eff_", "") for c in cols])
    for i in range(len(cols)):
        for j in range(len(cols)):
            v = M.iloc[i, j]
            ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                    color="white" if abs(v) > 0.6 else "black", fontsize=9)
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Pearson r")
    add_panel_label(ax, 3, "phase correlation")

    fig.tight_layout()
    save_pair(fig, "fig_efficiency_overview")
    plt.close(fig)


# =============================================================================
# Phase 4: efficiency by cohort
# =============================================================================

def fig_efficiency_by_cohort() -> None:
    if not PHASE4_CSV.exists():
        log.warning("phase4 cohort_stats.csv not found at %s; skipping", PHASE4_CSV)
        return
    cohort = pd.read_csv(PHASE4_CSV)
    formats_present = sorted(cohort["format"].unique())
    cmap = plt.get_cmap("tab10")
    fmt_color = {f: cmap(i % 10) for i, f in enumerate(formats_present)}

    fig, axes = plt.subplots(2, 2, figsize=(10, 7.2), sharex=True)
    for idx, (ax, phase) in enumerate(zip(axes.ravel(), EFFICIENCY_PHASES)):
        target = f"eff_{phase}"
        sub = cohort[(cohort["target"] == target) & (cohort["n"] >= MIN_PER_COHORT)].copy()
        for fmt in formats_present:
            d = sub[sub["format"] == fmt].sort_values("sale_year")
            if d.empty:
                continue
            ax.errorbar(
                d["sale_year"], d["mean"],
                yerr=[d["mean"] - d["ci_low"], d["ci_high"] - d["mean"]],
                marker="o", capsize=3, label=fmt, color=fmt_color[fmt],
                linewidth=1.2, markersize=5,
            )
        ax.set_ylabel("Thermal efficiency (fraction)")
        ax.grid(True, alpha=0.3)
        add_panel_label(ax, idx, sub_caption=PHASE_DISPLAY[phase])
    for ax in axes[1]:
        ax.set_xlabel("Year of sale / start of service")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center",
               ncol=min(6, len(labels)), bbox_to_anchor=(0.5, -0.02),
               frameon=False)
    fig.tight_layout(rect=[0, 0.03, 1, 1])
    save_pair(fig, "fig_efficiency_by_cohort")
    plt.close(fig)


# =============================================================================
# Phase 5: UQ parity plots
# =============================================================================

def fig_uq_parity(target: str) -> None:
    if not PHASE5_PREDS.exists():
        log.warning("phase5 uq_predictions.csv not found at %s; skipping", PHASE5_PREDS)
        return
    preds = pd.read_csv(PHASE5_PREDS)
    p = preds[preds["target"] == target].copy()
    if p.empty:
        log.warning("no predictions for target=%s; skipping", target)
        return
    methods = [
        ("tree", "tree_lo", "tree_hi", "tree-quantile"),
        ("conformal", "conf_lo", "conf_hi", "split-conformal"),
    ]
    y_min = float(min(p["actual"].min(), p["predicted"].min()))
    y_max = float(max(p["actual"].max(), p["predicted"].max()))
    pad = 0.05 * (y_max - y_min)
    lo_lim = y_min - pad
    hi_lim = y_max + pad

    fig, axes = plt.subplots(1, 2, figsize=(11, 5.2), sharey=True)
    for idx, (ax, (_key, lo_col, hi_col, method_label)) in enumerate(zip(axes, methods)):
        ps = p.sort_values("actual").reset_index(drop=True)
        inside = (ps["actual"] >= ps[lo_col]) & (ps["actual"] <= ps[hi_col])
        yerr_lo = np.clip(ps["predicted"] - ps[lo_col], 0, None)
        yerr_hi = np.clip(ps[hi_col] - ps["predicted"], 0, None)
        ax.errorbar(
            ps["actual"], ps["predicted"],
            yerr=[yerr_lo, yerr_hi],
            fmt="o", ms=3, capsize=2, ecolor="lightgray", elinewidth=0.7,
            color="C0", alpha=0.7, label="inside interval",
        )
        out = ps[~inside]
        ax.scatter(out["actual"], out["predicted"], s=14, color="red",
                   label="outside interval", zorder=3)
        ax.plot([lo_lim, hi_lim], [lo_lim, hi_lim], "k--", lw=0.8, alpha=0.5)
        ax.set_xlim(lo_lim, hi_lim)
        ax.set_ylim(lo_lim, hi_lim)
        ax.set_xlabel(f"Actual {target}")
        if idx == 0:
            ax.set_ylabel(f"Predicted {target}")
        ax.grid(True, alpha=0.3)
        add_panel_label(ax, idx, sub_caption=method_label)
        ax.legend(loc="lower right", frameon=True)
    fig.tight_layout()
    save_pair(fig, f"fig_uq_parity_{target}")
    plt.close(fig)


# =============================================================================
# Phase 2: top-10 permutation importance per representative target
# =============================================================================

GEOM_FEATS = {
    "height_cm", "outside_d_cm", "chamber_d_cm", "chamber_depth_cm",
    "inlet_w_cm", "inlet_h_cm", "inlet_area_cm2", "chamber_volume_cm3",
}
PHYS_ENG_FEATS = {
    "aspect_ratio", "chamber_aspect", "inlet_per_volume",
    "chamber_surface_cm2", "surface_to_volume", "wall_thickness_cm",
}
WBT_PREFIXES = ("eff_", "fp_", "br_", "sfc_", "tboil_")
GROUP_COLOR = {
    "geometry": "#4c72b0",
    "physics": "#55a868",
    "wbt": "#c44e52",
    "categorical": "#8172b2",
    "other": "#999999",
}
GROUP_LEGEND_ORDER = ["geometry", "physics", "wbt", "categorical"]


def classify_feature(name: str) -> str:
    if name in GEOM_FEATS:
        return "geometry"
    if name in PHYS_ENG_FEATS:
        return "physics"
    if name in ("material", "format"):
        return "categorical"
    if any(name.startswith(p) for p in WBT_PREFIXES):
        return "wbt"
    return "other"


def fig_phase2_importance(targets: tuple[str, ...] = ("eff_cold", "fp_simmer", "br_hot"),
                          top_n: int = 10) -> None:
    """Top-n permutation importance for representative targets, side by side."""
    if not PHASE2_PERM.exists():
        log.warning("phase2 permutation_importance.csv not found at %s; skipping", PHASE2_PERM)
        return
    perm = pd.read_csv(PHASE2_PERM)
    available = [t for t in targets if t in perm["target"].unique()]
    if not available:
        log.warning("none of %s present in phase2 perm CSV; skipping", targets)
        return
    n_panels = len(available)
    fig, axes = plt.subplots(1, n_panels, figsize=(4.6 * n_panels, 5.5))
    if n_panels == 1:
        axes = [axes]

    for idx, (ax, target) in enumerate(zip(axes, available)):
        sub = (
            perm[perm["target"] == target]
            .sort_values("imp_mean", ascending=False)
            .head(top_n)
            .iloc[::-1]   # flip so largest is at top of horizontal bar
            .reset_index(drop=True)
        )
        groups = [classify_feature(f) for f in sub["feature"]]
        colors = [GROUP_COLOR.get(g, GROUP_COLOR["other"]) for g in groups]
        y_pos = np.arange(len(sub))
        ax.barh(
            y_pos, sub["imp_mean"],
            xerr=sub["imp_std"], color=colors, edgecolor="black",
            linewidth=0.5, error_kw=dict(ecolor="black", capsize=2, lw=0.7),
        )
        ax.set_yticks(y_pos)
        ax.set_yticklabels(sub["feature"], fontsize=9)
        ax.set_xlabel("Permutation importance (ΔR²)")
        ax.axvline(0, color="black", lw=0.6, alpha=0.5)
        ax.grid(True, axis="x", alpha=0.3)
        add_panel_label(ax, idx, sub_caption=f"target: {target}")

    # Shared legend at the bottom for feature groups
    handles = [
        plt.Rectangle((0, 0), 1, 1, color=GROUP_COLOR[g], label=g)
        for g in GROUP_LEGEND_ORDER
    ]
    fig.legend(
        handles=handles,
        loc="lower center", ncol=len(GROUP_LEGEND_ORDER),
        bbox_to_anchor=(0.5, -0.02), frameon=False,
    )
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    save_pair(fig, "fig_phase2_importance")
    plt.close(fig)


# =============================================================================
# Phase 3: OOD generalization R² by probe and target family
# =============================================================================

def _target_family(t: str) -> str:
    if t.startswith("eff_"):
        return "efficiency"
    if t.startswith("fp_"):
        return "firepower"
    if t.startswith("br_"):
        return "burn rate"
    return "other"


def fig_phase3_ood() -> None:
    """Grouped bars: mean R² across holdouts per (probe, target family, phase)."""
    if not PHASE3_OOD.exists():
        log.warning("phase3 ood_results.csv not found at %s; skipping", PHASE3_OOD)
        return
    ood = pd.read_csv(PHASE3_OOD)
    if ood.empty:
        log.warning("phase3 ood_results.csv is empty; skipping")
        return

    ood = ood.copy()
    ood["family"] = ood["target"].apply(_target_family)
    ood["phase"] = ood["target"].str.split("_").str[-1]
    # eff_combined collapses into "combined" phase; keep but order separately
    phase_order = ["cold", "hot", "simmer", "combined"]
    family_order = ["efficiency", "firepower", "burn rate"]
    # Okabe-Ito palette to match phase colors elsewhere
    family_color = {
        "efficiency": "#0072B2",
        "firepower": "#D55E00",
        "burn rate": "#009E73",
    }

    probes_present = [p for p in ("LOFO", "LOBO", "LOMO", "LOCO") if p in ood["probe"].unique()]
    if not probes_present:
        log.warning("no recognized probe values in ood_results.csv; skipping")
        return
    n_panels = len(probes_present)
    # Slightly taller figure to accommodate three-line x-axis labels (phase, n, MAE/sigma)
    fig, axes = plt.subplots(1, n_panels, figsize=(4.8 * n_panels, 5.6),
                             sharey=True)
    if n_panels == 1:
        axes = [axes]

    # Build a (family, phase) ordering for x-axis labels
    target_order: list[tuple[str, str]] = []
    for fam in family_order:
        for ph in phase_order:
            target_order.append((fam, ph))

    # Hard y-axis clip so a single catastrophic OOD cell does not crush all
    # other bars into a flat line near zero. Bars beyond the floor are drawn
    # to the floor and annotated with their true numeric value.
    Y_FLOOR = -2.0
    Y_CEIL = 1.05

    for idx, (ax, probe) in enumerate(zip(axes, probes_present)):
        psub = ood[ood["probe"] == probe]
        # Aggregate across holdout_value for each (family, phase):
        # - R^2 mean and std across cells
        # - sum of n_test across cells (total held-out stoves)
        # - mean of MAE across cells (raw, in target units)
        # - mean of y_test_std across cells (for unit-free normalized MAE)
        agg = (
            psub.groupby(["family", "phase"])
                .agg(
                    r2_mean=("r2", "mean"),
                    r2_std=("r2", "std"),
                    n_cells=("r2", "count"),
                    n_test_sum=("n_test", "sum"),
                    mae_mean=("mae", "mean"),
                    y_std_mean=("y_test_std", "mean"),
                )
                .reset_index()
        )
        # Filter to only (family, phase) combinations that exist
        x_labels: list[str] = []
        positions: list[float] = []
        for fam_idx, fam in enumerate(family_order):
            fam_rows = agg[agg["family"] == fam]
            phases_here = [ph for ph in phase_order if ph in fam_rows["phase"].values]
            for ph_idx, ph in enumerate(phases_here):
                row = fam_rows[fam_rows["phase"] == ph].iloc[0]
                x = fam_idx * (len(phase_order) + 0.6) + ph_idx
                positions.append(x)
                mean = row["r2_mean"]
                std = row["r2_std"] if not np.isnan(row["r2_std"]) else 0.0
                mae = row["mae_mean"]
                y_std = row["y_std_mean"]
                nmae = (mae / y_std) if (y_std and y_std > 0) else float("nan")
                n_test_total = int(row["n_test_sum"]) if not np.isnan(row["n_test_sum"]) else 0
                # Three-line x-label: phase / n_test sum / normalized MAE (bare number;
                # row meaning given in x-axis title to keep label width within bar width).
                nmae_str = (f"{nmae:.2f}" if not np.isnan(nmae) else "n/a")
                x_labels.append(f"{ph}\nn={n_test_total}\n{nmae_str}")
                # Clip both bar height and error bar to the floor for plotting
                clipped_mean = max(mean, Y_FLOOR)
                lo_err = max(0.0, min(std, clipped_mean - Y_FLOOR))
                hi_err = max(0.0, std) if mean + std <= Y_CEIL else max(0.0, Y_CEIL - clipped_mean)
                ax.bar(
                    x, clipped_mean, width=0.8, color=family_color[fam],
                    edgecolor="black", linewidth=0.5, alpha=0.85,
                    yerr=[[lo_err], [hi_err]],
                    error_kw=dict(ecolor="black", capsize=2, lw=0.7),
                )
                # If the actual mean is below the visible floor, annotate the
                # true R^2 value just above the floor.
                if mean < Y_FLOOR:
                    ax.text(
                        x, Y_FLOOR + 0.05, f"R²={mean:.1f}",
                        ha="center", va="bottom", fontsize=7,
                        color="black", rotation=90,
                        bbox=dict(boxstyle="round,pad=0.15",
                                  fc="white", ec="black", lw=0.4, alpha=0.85),
                    )

        ax.axhline(0, color="black", lw=0.6, alpha=0.6)
        ax.set_ylim(Y_FLOOR, Y_CEIL)
        ax.set_xticks(positions)
        # Smaller font for three-line labels (phase / n / MAE-sigma)
        ax.set_xticklabels(x_labels, rotation=0, fontsize=7.5)
        # Annotate target families along the top of the axes
        for fam_idx, fam in enumerate(family_order):
            fam_rows = agg[agg["family"] == fam]
            phases_here = [ph for ph in phase_order if ph in fam_rows["phase"].values]
            if not phases_here:
                continue
            xs = [fam_idx * (len(phase_order) + 0.6) + i for i in range(len(phases_here))]
            ax.text(
                np.mean(xs), Y_CEIL * 0.97, fam,
                ha="center", va="top", fontsize=9, style="italic",
                color=family_color[fam],
            )
        ax.grid(True, axis="y", alpha=0.3)
        if idx == 0:
            ax.set_ylabel("Out-of-distribution R² (bar height; clipped at -2)")
        ax.set_xlabel("Rows: phase / held-out n / normalized MAE (= MAE / σ_y)")
        add_panel_label(ax, idx, sub_caption=probe)

    # Shared family legend below
    handles = [
        plt.Rectangle((0, 0), 1, 1, color=family_color[f], label=f)
        for f in family_order
    ]
    fig.legend(
        handles=handles, loc="lower center", ncol=len(family_order),
        bbox_to_anchor=(0.5, -0.02), frameon=False,
    )
    # Leave a bit more bottom margin for the three-line x-tick labels
    fig.tight_layout(rect=[0, 0.06, 1, 1])
    save_pair(fig, "fig_phase3_ood")
    plt.close(fig)


# =============================================================================
# Orchestration
# =============================================================================

def main() -> None:
    log.info("--- loading data ---")
    long_df = load_efficiency_phases()

    log.info("--- descriptive efficiency figures (single-panel) ---")
    fig_distributions(long_df)
    fig_boxplots(long_df)
    fig_violin(long_df)
    fig_phase_correlation()

    log.info("--- efficiency overview (4-panel) ---")
    fig_efficiency_overview(long_df)

    log.info("--- Phase 2: permutation importance ---")
    fig_phase2_importance()

    log.info("--- Phase 3: OOD R^2 by probe and target family ---")
    fig_phase3_ood()

    log.info("--- Phase 4: efficiency by cohort ---")
    fig_efficiency_by_cohort()

    log.info("--- Phase 5: UQ parity plots ---")
    for target in ("eff_cold", "eff_simmer", "fp_simmer"):
        fig_uq_parity(target)

    log.info("\nAll figures in %s (PNG preview + PDF for LaTeX)", OUT_DIR)
    log.info("\n=== Suggested LaTeX caption templates ===")
    log.info("\nfig_efficiency_distributions.pdf:")
    log.info("  Probability-density estimate of thermal efficiency across operational phases")
    log.info("  for the full multi-campaign cookstove dataset (n=450 unique stoves).")
    log.info("\nfig_efficiency_boxplots.pdf:")
    log.info("  Distribution of thermal efficiency by operational phase. Boxes show the")
    log.info("  inter-quartile range; whiskers extend to 1.5×IQR; median in black.")
    log.info("\nfig_efficiency_violin.pdf:")
    log.info("  Violin plot of thermal efficiency by phase. White lines mark the mean")
    log.info("  and median; width is proportional to local probability density.")
    log.info("\nfig_phase_correlation.pdf:")
    log.info("  Pearson correlation between phase-level efficiency metrics across the")
    log.info("  450-stove dataset. Cold/hot are strongly positively correlated; simmer")
    log.info("  decouples from high-power phases.")
    log.info("\nfig_efficiency_overview.pdf:")
    log.info("  Four-panel summary of thermal efficiency across phases. (a) Kernel density,")
    log.info("  (b) boxplot, (c) violin, (d) inter-phase Pearson correlation matrix.")
    log.info("\nfig_efficiency_by_cohort.pdf:")
    log.info("  Per-format thermal efficiency by sale-year cohort (mean ± 95% CI).")
    log.info("  Panels: (a) cold start, (b) hot start, (c) simmer, (d) combined.")
    log.info("\nfig_phase2_importance.pdf:")
    log.info("  Top-10 permutation-importance features for three representative targets:")
    log.info("  (a) cold-start efficiency, (b) simmer firepower, (c) hot-start burn rate.")
    log.info("  Bars colored by feature group (geometry, physics-engineered, WBT, categorical);")
    log.info("  error bars show the across-fold standard deviation.")
    log.info("\nfig_phase3_ood.pdf:")
    log.info("  Out-of-distribution R^2 from structured holdouts. Panels: (a) leave-one-format-out,")
    log.info("  (b) leave-one-brand-out, (c) leave-one-material-out. Bars grouped by target")
    log.info("  family (efficiency, firepower, burn rate) and operational phase. Error bars")
    log.info("  show the across-holdout standard deviation; the dashed zero line marks where")
    log.info("  the model is no better than predicting the training-set mean.")
    log.info("\nfig_uq_parity_<target>.pdf:")
    log.info("  Ninety-percent prediction intervals on held-out stoves for <target>.")
    log.info("  (a) Tree-quantile, (b) split-conformal. Coverage and median interval width")
    log.info("  reported in Table N.")


if __name__ == "__main__":
    main()
