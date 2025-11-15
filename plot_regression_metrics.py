# plot_regression_metrics.py
"""
Robust plotting:
- Reads outputs/reports/regression_results.json
- Handles dict-of-dicts (targets -> metrics) OR flat dict
- Plots bars for metrics per target
- Plots learning curves from regression_details/curves (LightGBM & MLP)
- Plots parity + residual histograms from regression_details/preds
"""

import os, json, glob
import pandas as pd
import matplotlib.pyplot as plt

def _find_root():
    here = os.path.abspath(os.path.dirname(__file__))
    candidates = [
        here,
        os.path.dirname(here),  # if script is in ./scripts
    ]
    for c in candidates:
        rp = os.path.join(c, "outputs", "reports", "regression_results.json")
        if os.path.isfile(rp):
            return c, rp
    # fallback assume current dir is root
    return here, os.path.join(here, "outputs", "reports", "regression_results.json")

ROOT, RES_PATH = _find_root()
FIG_DIR = os.path.join(ROOT, "outputs", "figures")
REP_DIR = os.path.join(ROOT, "outputs", "reports")
DET_DIR = os.path.join(REP_DIR, "regression_details")
CURVES_DIR = os.path.join(DET_DIR, "curves")
PREDS_DIR  = os.path.join(DET_DIR, "preds")

os.makedirs(FIG_DIR, exist_ok=True)

print(f"[info] Using ROOT = {ROOT}")
print(f"[info] Expecting results at = {RES_PATH}")

if not os.path.isfile(RES_PATH):
    print(f"[warn] {RES_PATH} not found. Make sure the pipeline wrote it.")
    raise SystemExit(1)

# ----------------------
# 1) metrics bar charts
# ----------------------
with open(RES_PATH, "r", encoding="utf-8") as f:
    results = json.load(f)

# Normalize to DataFrame:
# - dict-of-dicts: ok
# - flat dict: wrap as single row
if isinstance(results, dict):
    nested = any(isinstance(v, dict) for v in results.values())
    if nested:
        df = pd.DataFrame(results).T  # targets x metrics
    else:
        df = pd.DataFrame([results], index=["overall"])
else:
    # list of dicts with "target" keys?
    try:
        df = pd.DataFrame(results)
        if "target" in df.columns:
            df = df.set_index("target")
    except Exception:
        print("[warn] regression_results.json has unexpected format; skipping metric bars.")
        df = None

if df is not None and not df.empty:
    print(f"[info] Loaded metrics for {len(df)} targets: {list(df.index)}")
    for metric in df.columns:
        try:
            ax = df[metric].astype(float).sort_values(ascending=False).plot(kind="bar", figsize=(10, 4))
            ax.set_ylabel(metric.upper())
            ax.set_title(f"Regression metric: {metric.upper()}")
            plt.tight_layout()
            out = os.path.join(FIG_DIR, f"metrics_{metric}.png")
            plt.savefig(out, dpi=200); plt.close()
            print(f"[saved] {out}")
        except Exception as e:
            print(f"[warn] skipping metric '{metric}': {e}")

# ----------------------
# 2) learning curves
# ----------------------
curve_files = sorted(glob.glob(os.path.join(CURVES_DIR, "*_learning_curve.csv")))
for f in curve_files:
    tgt = os.path.basename(f).replace("_learning_curve.csv", "")
    c = pd.read_csv(f)

    if "iteration" not in c.columns:
        print(f"[warn] curve '{f}' has no 'iteration' column; skipping.")
        continue

    # plot all columns except iteration
    value_cols = [col for col in c.columns if col != "iteration"]
    plt.figure(figsize=(9, 5))
    for col in value_cols:
        plt.plot(c["iteration"], c[col], label=col)
    plt.xlabel("Iteration / Epoch")
    plt.ylabel("Loss / Metric")
    plt.title(f"Learning curve: {tgt}")
    plt.legend()
    plt.tight_layout()
    out = os.path.join(FIG_DIR, f"curve_{tgt}.png")
    plt.savefig(out, dpi=200); plt.close()
    print(f"[saved] {out}")

# ----------------------
# 3) parity + residuals
# ----------------------
pred_files = sorted(glob.glob(os.path.join(PREDS_DIR, "*_pred_vs_true.csv")))
for f in pred_files:
    tgt = os.path.basename(f).replace("_pred_vs_true.csv", "")
    d = pd.read_csv(f)
    if not {"y_true", "y_pred"}.issubset(d.columns):
        print(f"[warn] preds '{f}' missing y_true/y_pred; skipping.")
        continue

    # parity
    plt.figure(figsize=(5, 5))
    plt.scatter(d["y_true"], d["y_pred"], s=15, alpha=0.7)
    lo = min(d["y_true"].min(), d["y_pred"].min())
    hi = max(d["y_true"].max(), d["y_pred"].max())
    plt.plot([lo, hi], [lo, hi])
    plt.xlabel(f"True {tgt}")
    plt.ylabel(f"Pred {tgt}")
    plt.title(f"Predicted vs True: {tgt}")
    plt.tight_layout()
    out = os.path.join(FIG_DIR, f"parity_{tgt}.png")
    plt.savefig(out, dpi=200); plt.close()
    print(f"[saved] {out}")

    # residuals
    resid = d["y_pred"] - d["y_true"]
    plt.figure(figsize=(6, 4))
    plt.hist(resid, bins=30, alpha=0.9)
    plt.xlabel("Residual (pred - true)")
    plt.ylabel("Count")
    plt.title(f"Residuals: {tgt}")
    plt.tight_layout()
    out = os.path.join(FIG_DIR, f"residuals_{tgt}.png")
    plt.savefig(out, dpi=200); plt.close()
    print(f"[saved] {out}")

print(f"[done] Plots saved in: {FIG_DIR}")
