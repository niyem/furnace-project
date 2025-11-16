"""
Main pipeline orchestrator for furnace efficiency ML project.

This script coordinates the complete machine learning pipeline:
1. Data loading (from ml_ready_data.csv or Excel)
2. Preprocessing (cleaning, imputation, scaling)
3. Dimensionality reduction (PCA)
4. Clustering analysis (K-Means, GMM, or DBSCAN)
5. Regression modeling (multiple models: Linear, RF, GB, XGBoost)
6. Visualization generation (all plots saved to figures/)
7. Results reporting (JSON summaries and metrics)

Usage:
    python run_pipeline.py --config config.yaml
"""

import argparse
from pathlib import Path
import numpy as np
import pandas as pd

from config import Config
from data_loader import load_data
from preprocess import basic_clean
from dim_reduce import reduce_dimensions
from cluster import cluster
from regression import compute_average_efficiency, train_multi_target_multi_model, print_results_summary
from utils import get_logger, save_json
import visualizations as viz

logger = get_logger()


def main(cfg_path: str = 'config.yaml') -> None:
    """
    Run the complete ML pipeline.

    Parameters
    ----------
    cfg_path : str
        Path to the configuration YAML file.
    """
    logger.info("="*80)
    logger.info("FURNACE EFFICIENCY ML PIPELINE")
    logger.info("="*80)

    # Load configuration
    cfg = Config(cfg_path)
    logger.info(f"Configuration loaded from: {cfg_path}")

    # Get paths
    data_path = cfg.get('data', 'path')
    sheet_name = cfg.get('data', 'sheet_name', default='Sheet1')
    index_col = cfg.get('data', 'index_col')
    figures_dir = cfg.get('paths', 'figures', default='figures')
    reports_dir = cfg.get('paths', 'reports', default='outputs/reports')

    # Ensure directories exist
    Path(figures_dir).mkdir(parents=True, exist_ok=True)
    Path(reports_dir).mkdir(parents=True, exist_ok=True)

    # ========================================================================
    # STEP 1: Load Data
    # ========================================================================
    logger.info("\n" + "-"*80)
    logger.info("STEP 1: Loading data")
    logger.info("-"*80)

    df = load_data(data_path, sheet_name, index_col)
    logger.info(f"Data loaded: {df.shape[0]} rows, {df.shape[1]} columns")

    # ========================================================================
    # STEP 2: Preprocessing
    # ========================================================================
    logger.info("\n" + "-"*80)
    logger.info("STEP 2: Preprocessing")
    logger.info("-"*80)

    targets_config = cfg.get('targets', default=[])
    preprocess_config = cfg.get('preprocess', default={})

    X, y = basic_clean(df, preprocess_config, targets_config)
    logger.info(f"Preprocessing complete: X={X.shape}, y={y.shape if y is not None else None}")

    # Compute average efficiency if we have the individual thermal efficiency columns
    if y is not None:
        y = compute_average_efficiency(y)
        logger.info(f"Targets after computing average_efficiency: {y.columns.tolist()}")

    # ========================================================================
    # STEP 3: Dimensionality Reduction
    # ========================================================================
    logger.info("\n" + "-"*80)
    logger.info("STEP 3: Dimensionality reduction")
    logger.info("-"*80)

    dim_reduce_config = cfg.get('dim_reduce', default={})
    Z, dim_info = reduce_dimensions(X, dim_reduce_config)
    logger.info(f"Dimensionality reduction complete: {X.shape[1]} → {Z.shape[1]} dimensions")

    # Save PCA variance plot if using PCA
    if dim_info.get('method') == 'pca':
        from sklearn.decomposition import PCA
        pca_model = PCA(n_components=dim_reduce_config.get('n_components', 0.95), random_state=42)
        pca_model.fit(X.values)
        viz.plot_pca_variance(pca_model, figures_dir=figures_dir)

    # ========================================================================
    # STEP 4: Clustering
    # ========================================================================
    logger.info("\n" + "-"*80)
    logger.info("STEP 4: Clustering analysis")
    logger.info("-"*80)

    clustering_config = cfg.get('clustering', default={})
    labels, cluster_model, cluster_metrics = cluster(Z, clustering_config)

    n_clusters = len(np.unique(labels[labels >= 0]))
    logger.info(f"Clustering complete: {n_clusters} clusters identified")
    logger.info(f"Cluster metrics: {cluster_metrics}")

    # Save clustering results
    cluster_results = {
        'n_clusters': n_clusters,
        'algorithm': cluster_metrics.get('algorithm', 'unknown'),
        'metrics': cluster_metrics,
        'cluster_sizes': {int(k): int(v) for k, v in zip(*np.unique(labels, return_counts=True))}
    }
    save_json(cluster_results, Path(reports_dir) / 'cluster_summary.json')

    # Generate clustering visualizations
    logger.info("Generating clustering visualizations...")
    viz.create_all_clustering_visualizations(
        X.values, labels, cluster_metrics,
        pca_model=pca_model if dim_info.get('method') == 'pca' else None,
        config=cfg.cfg,
        figures_dir=figures_dir
    )

    # ========================================================================
    # STEP 5: Regression Modeling
    # ========================================================================
    logger.info("\n" + "-"*80)
    logger.info("STEP 5: Regression modeling")
    logger.info("-"*80)

    regression_config = cfg.get('regression', default={})

    if regression_config.get('enabled', True) and y is not None:
        # Get model names
        model_names = regression_config.get('models', ['linear', 'random_forest', 'gradient_boost', 'xgboost'])
        test_size = regression_config.get('test_size', 0.2)
        validation_size = regression_config.get('validation_size', 0.1)
        random_state = regression_config.get('random_state', 42)
        metrics = regression_config.get('metrics', ['r2', 'mae', 'mse', 'rmse'])

        # Filter out targets with too many missing values
        y_valid = y.dropna(axis=1, thresh=int(0.5 * len(y)))  # Keep columns with at least 50% non-null
        logger.info(f"Valid targets for regression: {y_valid.columns.tolist()}")

        # Align features with valid targets
        common_idx = X.index.intersection(y_valid.index)
        X_reg = X.loc[common_idx]
        y_reg = y_valid.loc[common_idx]

        logger.info(f"Training {len(model_names)} models on {len(y_reg.columns)} targets...")

        # Train all models
        regression_results = train_multi_target_multi_model(
            X_reg, y_reg,
            model_names=model_names,
            test_size=test_size,
            validation_size=validation_size,
            random_state=random_state,
            metrics=metrics,
            figures_dir=figures_dir,
            reports_dir=reports_dir
        )

        # Print summary
        print_results_summary(regression_results)

    else:
        logger.info("Regression disabled or no target variables available.")
        regression_results = {}

    # ========================================================================
    # Pipeline Complete
    # ========================================================================
    logger.info("\n" + "="*80)
    logger.info("PIPELINE COMPLETE")
    logger.info("="*80)
    logger.info(f"Outputs saved to:")
    logger.info(f"  - Figures: {figures_dir}/")
    logger.info(f"  - Reports: {reports_dir}/")
    logger.info("="*80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the furnace efficiency ML pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )

    args = parser.parse_args()
    main(args.config)
