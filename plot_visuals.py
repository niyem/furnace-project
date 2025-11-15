# scripts/plot_visuals.py
import os, sys, argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Resolve project root (works if this file is in project root or scripts/) ---
THIS = os.path.abspath(__file__)
CANDIDATES = [
    os.path.dirname(THIS),                 # current folder
    os.path.dirname(os.path.dirname(THIS)) # parent (project root if we're in scripts/)
]
PROJ_ROOT = None
for p in CANDIDATES:
    if os.path.exists(os.path.join(p, "config.yaml")):
        PROJ_ROOT = p
        break
if PROJ_ROOT is None:
    # fallback to parent
    PROJ_ROOT = os.path.dirname(os.path.dirname(THIS))
sys.path.insert(0, PROJ_ROOT)

# --- Imports (support both flat and src/ layouts) ---
try:
    from src.config import Config
    from src.data_loader import load_data
    from src.preprocess import basic_clean
    from src.dim_reduce import reduce_dimensions
    from src.cluster import cluster
except ModuleNotFoundError:
    from config import Config
    from data_loader import load_data
    from preprocess import basic_clean
    from dim_reduce import reduce_dimensions
    from cluster import cluster

def ensure_outputs(cfg):
    for key in ["outputs", "figures", "models", "reports"]:
        os.makedirs(cfg["paths"][key], exist_ok=True)

def make_plots(cfg_path: str | None):
    cfg = Config(cfg_path or os.path.join(PROJ_ROOT, "config.yaml"))
    ensure_outputs(cfg)

    reports_dir = cfg["paths"]["reports"]
    figdir = cfg["paths"]["figures"]
    os.makedirs(figdir, exist_ok=True)

    emb_path = os.path.join(reports_dir, "embedding_with_clusters.csv")

    # --- Load embedding+labels if present; otherwise recompute quickly ---
    if os.path.exists(emb_path):
        df_emb = pd.read_csv(emb_path)
        z_cols = [c for c in df_emb.columns if c.startswith("Z")]
        if not z_cols:
            raise RuntimeError("No Z* columns found in embedding_with_clusters.csv")
        Z = df_emb[z_cols].values
        labels = df_emb["cluster"].values
    else:
        df = load_data(cfg["data"]["path"],
                       cfg["data"].get("sheet_name", "Sheet1"),
                       cfg["data"].get("index_col"))
        X, y = basic_clean(df, cfg["preprocess"], cfg.get("targets", []))
        Z, _ = reduce_dimensions(X, cfg["dim_reduce"])
        labels, _, _ = cluster(Z, cfg["clustering"])

    # --- Plot 1: colored scatter (uses the first two embedding axes) ---
    uniq = np.unique(labels)
    palette = ['tab:blue','tab:orange','tab:green','tab:red','tab:purple',
               'tab:brown','tab:pink','tab:gray','tab:olive','tab:cyan']
    color_map = {lab: palette[i % len(palette)] for i, lab in enumerate(uniq)}
    if -1 in color_map:
        color_map[-1] = "black"

    plt.figure(figsize=(8, 6))
    for lab in uniq:
        idx = (labels == lab)
        plt.scatter(Z[idx, 0], Z[idx, 1], s=18, alpha=0.85, label=f"Cluster {lab}", c=color_map[lab])
    plt.xlabel("Embedding 1")
    plt.ylabel("Embedding 2")
    plt.title("Furnace data embedding colored by cluster")
    plt.legend(loc="best", fontsize=8, frameon=True)
    scatter_path = os.path.join(figdir, "clusters_scatter.png")
    plt.tight_layout()
    plt.savefig(scatter_path, dpi=160)
    plt.close()

    # --- Plot 2: Cluster sizes ---
    counts = pd.Series(labels).value_counts().sort_index()
    plt.figure(figsize=(7, 4))
    plt.bar([str(k) for k in counts.index], counts.values)
    plt.xlabel("Cluster label")
    plt.ylabel("Count")
    plt.title("Cluster sizes")
    bar_path = os.path.join(figdir, "cluster_sizes.png")
    plt.tight_layout()
    plt.savefig(bar_path, dpi=160)
    plt.close()

    print(f"Saved:\n  {scatter_path}\n  {bar_path}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=str, default=None, help="Path to config.yaml (optional)")
    args = ap.parse_args()
    make_plots(args.config)
