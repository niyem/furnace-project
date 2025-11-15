# run_pipeline.py
import os
import sys
import argparse
import subprocess
from pathlib import Path
import shutil
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt  # used for metric bar charts

from config import Config
from data_loader import load_data
from preprocess import basic_clean
from dim_reduce import reduce_dimensions
from cluster import cluster
from regression import train_multi_target
from utils import get_logger, save_json

logger = get_logger()


def _maybe_generate_cluster_figures(cfg_path: str, figures_dir: str) -> None:
    """Try plot_visuals.make_plots, else run plot_visuals.py if present."""
    try:
        from plot_visuals import make_plots  # type: ignore
        make_plots(cfg_path)
        logger.info("Cluster figures generated via plot_visuals.make_plots().")
        return
    except Exception as e:
        logger.debug(f"plot_visuals import path failed: {e}")

    root = Path(__file__).parent
    candidates = [root / "plot_visuals.py", root / "scripts" / "plot_visuals.py"]
    for c in candidates:
        if c.exists():
            try:
                subprocess.run(
                    [sys.executable, str(c), "--config", cfg_path],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                logger.info(f"Cluster figures generated via script: {c}")
                return
            except subprocess.CalledProcessError as se:
                logger.warning(f"plot_visuals.py ran but returned an error:\n{se.stderr}")

    logger.info("Skipping cluster figure generation (plot_visuals not found).")


def _write_metric_bars(reg_results: dict, figures_dir: str) -> None:
    """
    Create metrics_{metric}.png in figures_dir from reg_results:
    { target: {metric: value, ...}, ... }
    """
    if not isinstance(reg_results, dict) or not reg_results:
        return
    Path(figures_dir).mkdir(parents=True, exist_ok=True)

    # collect targets and metric names
    targets = [t for t, v in reg_results.items() if isinstance(v, dict)]
    if not targets:
        return
    metrics = set()
    for t in targets:
        for k, v in reg_results[t].items():
            if isinstance(v, (int, float, np.floating)):
                metrics.add(k)
    metrics = sorted(metrics)
    if not metrics:
        return

    for m in metrics:
        vals = [reg_results[t].get(m, np.nan) for t in targets]
        plt.figure(figsize=(9, 4))
        plt.bar(range(len(targets)), vals)
        plt.xticks(range(len(targets)), targets, rotation=30, ha="right")
        plt.ylabel(m.upper())
        plt.title(f"{m.upper()} by Target")
        plt.tight_layout()
        out = Path(figures_dir) / f"metrics_{m}.png"
        plt.savefig(out, dpi=160)
        plt.close()
    logger.info(f"Wrote metric bar charts to {figures_dir}")


def _harvest_report_images(reports_dir: str, figures_dir: str) -> int:
    """
    Recursively copy all images from reports_dir into figures_dir.
    Handles .png/.jpg/.jpeg/.svg/.pdf and keeps basenames (no subfolders).
    Returns count of files copied.
    """
    src = Path(reports_dir)
    dst = Path(figures_dir)
    dst.mkdir(parents=True, exist_ok=True)
    exts = {".png", ".jpg", ".jpeg", ".svg", ".pdf"}

    if not src.exists():
        logger.info(f"Reports folder not found: {src}")
        return 0

    copied = 0
    for p in src.rglob("*"):
        if p.is_file() and p.suffix.lower() in exts:
            try:
                shutil.copy2(p, dst / p.name)
                copied += 1
            except Exception as e:
                logger.warning(f"Could not copy {p} -> {dst}: {e}")
    logger.info(f"Harvested {copied} figure(s) from {src} into {dst}.")
    return copied


def main(cfg_path: str) -> None:
    cfg = Config(cfg_path)

    # Paths (already resolved to the data drive by Config)
    outputs_dir = cfg["paths"]["outputs"]
    figures_dir = cfg["paths"]["figures"]
    models_dir  = cfg["paths"]["models"]
    reports_dir = cfg["paths"]["reports"]
    for d in (outputs_dir, figures_dir, models_dir, reports_dir):
        os.makedirs(d, exist_ok=True)

    details_dir = os.path.join(reports_dir, "regression_details")
    os.makedirs(details_dir, exist_ok=True)

    # 1) Load
    df = load_data(
        cfg["data"]["path"],
        cfg["data"].get("sheet_name", "Sheet1"),
        cfg["data"].get("index_col"),
    )
    targets = cfg.get("targets", default=[])

    # 2) Preprocess
    X, y = basic_clean(df, cfg["preprocess"], targets)

    # 3) Dimensionality reduction
    Z, dim_info = reduce_dimensions(X, cfg["dim_reduce"])

    # 4) Clustering
    labels, clus_model, clus_summary = cluster(Z, cfg["clustering"])

    # Save clustering outputs for plotting scripts
    emb_cols = [f"Z{i+1}" for i in range(Z.shape[1])]
    out_df = pd.DataFrame(Z, columns=emb_cols, index=X.index)
    out_df["cluster"] = labels
    out_df.to_csv(os.path.join(reports_dir, "embedding_with_clusters.csv"), index=False)

    save_json(
        {"dim_info": dim_info, "cluster_summary": clus_summary},
        os.path.join(reports_dir, "cluster_summary.json"),
    )

    # 5) Regression
    reg_cfg = cfg.get("regression", default={})
    reg_results = {}
    if reg_cfg.get("enabled", True) and (y is not None):
        try:
            y_valid = y.dropna(how="all")
            common_idx = X.index.intersection(y_valid.index)
            reg_results = train_multi_target(
                X.loc[common_idx],
                y.loc[common_idx],
                model_name=reg_cfg.get("model", "lightgbm"),
                test_size=reg_cfg.get("test_size", 0.2),
                random_state=reg_cfg.get("random_state", 42),
                metrics=reg_cfg.get("metrics", ["r2", "mae", "rmse"]),
                save_details_dir=details_dir,
                save_training_curves=reg_cfg.get("save_training_curves", True),
                loss_metric=reg_cfg.get("loss_metric", "l2"),
                early_stopping_rounds=reg_cfg.get("early_stopping_rounds", 100),
                max_estimators=reg_cfg.get("max_estimators", 2000),
            )
        except Exception as e:
            logger.error(f"Regression training failed: {e}")
            reg_results = {"error": str(e)}

    # 6) Save results
    save_json(reg_results, os.path.join(reports_dir, "regression_results.json"))
    logger.info(f"Regression results saved to: {os.path.join(reports_dir, 'regression_results.json')}")

    # 7) Write metric bar charts directly to figures
    _write_metric_bars(reg_results, figures_dir)

    # 8) Recursively mirror every figure from reports → figures
    _harvest_report_images(reports_dir, figures_dir)

    # 9) Generate cluster figures (if plot_visuals exists)
    _maybe_generate_cluster_figures(cfg_path, figures_dir)

    logger.info("Pipeline complete.")
    logger.info(f"Data file: {cfg['data']['path']}")
    logger.info(f"Reports : {reports_dir}")
    logger.info(f"Figures : {figures_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="config.yaml")
    args = parser.parse_args()
    main(args.config)
