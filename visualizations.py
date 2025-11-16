"""
Visualization module for furnace efficiency ML project.

This module provides publication-quality visualization functions for:
- Clustering analysis (PCA, t-SNE, UMAP scatter plots)
- Cluster metrics and statistics
- Regression performance (parity plots, residuals, learning curves)
- Feature importance and model comparisons

All plots are saved to the figures/ directory with consistent styling.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from utils import get_logger

# Try to import UMAP (optional dependency)
try:
    import umap
    HAS_UMAP = True
except ImportError:
    HAS_UMAP = False

logger = get_logger()

# Set publication-quality plot style
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")
plt.rcParams['figure.dpi'] = 200
plt.rcParams['savefig.dpi'] = 200
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9


def ensure_figures_dir(figures_dir: str = 'figures') -> Path:
    """
    Ensure the figures directory exists.

    Parameters
    ----------
    figures_dir : str
        Path to the figures directory.

    Returns
    -------
    Path
        Path object for the figures directory.
    """
    path = Path(figures_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def plot_pca_variance(
    pca_model,
    figures_dir: str = 'figures',
    filename: str = 'pca_variance_explained.png'
) -> None:
    """
    Plot cumulative explained variance ratio for PCA.

    Parameters
    ----------
    pca_model : sklearn.decomposition.PCA
        Fitted PCA model.
    figures_dir : str
        Directory to save the figure.
    filename : str
        Output filename.
    """
    fig_path = ensure_figures_dir(figures_dir)

    explained_var = pca_model.explained_variance_ratio_
    cumulative_var = np.cumsum(explained_var)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    # Individual explained variance
    ax1.bar(range(1, len(explained_var) + 1), explained_var, alpha=0.7)
    ax1.set_xlabel('Principal Component')
    ax1.set_ylabel('Explained Variance Ratio')
    ax1.set_title('Individual Explained Variance by Component')
    ax1.grid(alpha=0.3)

    # Cumulative explained variance
    ax2.plot(range(1, len(cumulative_var) + 1), cumulative_var, 'o-', linewidth=2)
    ax2.axhline(y=0.95, color='r', linestyle='--', label='95% threshold')
    ax2.set_xlabel('Number of Components')
    ax2.set_ylabel('Cumulative Explained Variance')
    ax2.set_title('Cumulative Explained Variance')
    ax2.legend()
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(fig_path / filename, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved PCA variance plot: {fig_path / filename}")


def plot_clustering_results(
    X: np.ndarray,
    labels: np.ndarray,
    method_name: str = 'PCA',
    figures_dir: str = 'figures',
    filename: str = 'clustering_pca.png'
) -> None:
    """
    Plot clustering results in 2D space.

    Parameters
    ----------
    X : np.ndarray
        2D embedding of the data (n_samples, 2).
    labels : np.ndarray
        Cluster labels for each sample.
    method_name : str
        Name of the dimensionality reduction method (for title).
    figures_dir : str
        Directory to save the figure.
    filename : str
        Output filename.
    """
    fig_path = ensure_figures_dir(figures_dir)

    unique_labels = np.unique(labels)
    n_clusters = len(unique_labels[unique_labels >= 0])  # Exclude noise (-1)

    # Use a colormap
    colors = plt.cm.tab10(np.linspace(0, 1, max(10, n_clusters)))

    fig, ax = plt.subplots(figsize=(10, 8))

    for i, label in enumerate(unique_labels):
        if label == -1:
            # Noise points (black)
            color = 'black'
            marker = 'x'
            alpha = 0.3
            label_text = 'Noise'
        else:
            color = colors[label % len(colors)]
            marker = 'o'
            alpha = 0.6
            label_text = f'Cluster {label}'

        mask = labels == label
        ax.scatter(
            X[mask, 0], X[mask, 1],
            c=[color], marker=marker, alpha=alpha,
            s=50, label=label_text, edgecolors='w', linewidth=0.5
        )

    ax.set_xlabel(f'{method_name} Component 1')
    ax.set_ylabel(f'{method_name} Component 2')
    ax.set_title(f'Clustering Results ({method_name} Projection)')
    ax.legend(loc='best', framealpha=0.9)
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(fig_path / filename, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved clustering plot: {fig_path / filename}")


def plot_cluster_metrics(
    metrics: Dict[str, float],
    figures_dir: str = 'figures',
    filename: str = 'cluster_metrics.png'
) -> None:
    """
    Plot clustering evaluation metrics as a bar chart.

    Parameters
    ----------
    metrics : Dict[str, float]
        Dictionary of metric names and values.
    figures_dir : str
        Directory to save the figure.
    filename : str
        Output filename.
    """
    fig_path = ensure_figures_dir(figures_dir)

    # Filter out non-metric keys
    plot_metrics = {k: v for k, v in metrics.items()
                   if k in ['silhouette', 'calinski_harabasz', 'davies_bouldin']
                   and not np.isnan(v)}

    if not plot_metrics:
        logger.warning("No valid clustering metrics to plot")
        return

    fig, ax = plt.subplots(figsize=(8, 5))

    metric_names = list(plot_metrics.keys())
    metric_values = list(plot_metrics.values())

    bars = ax.bar(metric_names, metric_values, alpha=0.7, edgecolor='black')

    # Color code: higher is better for silhouette and calinski_harabasz
    # Lower is better for davies_bouldin
    for i, (name, bar) in enumerate(zip(metric_names, bars)):
        if name == 'davies_bouldin':
            bar.set_color('salmon')
        else:
            bar.set_color('skyblue')

    ax.set_ylabel('Metric Value')
    ax.set_title('Clustering Evaluation Metrics')
    ax.grid(axis='y', alpha=0.3)

    # Rotate x-axis labels
    plt.xticks(rotation=15, ha='right')

    plt.tight_layout()
    plt.savefig(fig_path / filename, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved cluster metrics plot: {fig_path / filename}")


def plot_cluster_sizes(
    labels: np.ndarray,
    figures_dir: str = 'figures',
    filename: str = 'cluster_sizes.png'
) -> None:
    """
    Plot cluster size distribution.

    Parameters
    ----------
    labels : np.ndarray
        Cluster labels for each sample.
    figures_dir : str
        Directory to save the figure.
    filename : str
        Output filename.
    """
    fig_path = ensure_figures_dir(figures_dir)

    unique, counts = np.unique(labels, return_counts=True)

    fig, ax = plt.subplots(figsize=(8, 5))

    # Color noise differently
    colors = ['black' if label == -1 else 'steelblue' for label in unique]
    labels_text = ['Noise' if label == -1 else f'Cluster {label}' for label in unique]

    bars = ax.bar(labels_text, counts, alpha=0.7, edgecolor='black', color=colors)

    ax.set_xlabel('Cluster')
    ax.set_ylabel('Number of Samples')
    ax.set_title('Cluster Size Distribution')
    ax.grid(axis='y', alpha=0.3)

    # Add count labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=9)

    plt.xticks(rotation=15, ha='right')
    plt.tight_layout()
    plt.savefig(fig_path / filename, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved cluster sizes plot: {fig_path / filename}")


def plot_tsne_embedding(
    X: np.ndarray,
    labels: np.ndarray,
    perplexity: int = 30,
    figures_dir: str = 'figures',
    filename: str = 'clustering_tsne.png'
) -> None:
    """
    Compute and plot t-SNE embedding with cluster labels.

    Parameters
    ----------
    X : np.ndarray
        High-dimensional feature array (n_samples, n_features).
    labels : np.ndarray
        Cluster labels for each sample.
    perplexity : int
        t-SNE perplexity parameter.
    figures_dir : str
        Directory to save the figure.
    filename : str
        Output filename.
    """
    logger.info("Computing t-SNE embedding...")

    # Compute t-SNE
    tsne = TSNE(n_components=2, perplexity=perplexity, random_state=42, max_iter=1000)
    X_tsne = tsne.fit_transform(X)

    # Plot using the clustering plot function
    plot_clustering_results(X_tsne, labels, method_name='t-SNE',
                           figures_dir=figures_dir, filename=filename)


def plot_umap_embedding(
    X: np.ndarray,
    labels: np.ndarray,
    n_neighbors: int = 15,
    min_dist: float = 0.1,
    figures_dir: str = 'figures',
    filename: str = 'clustering_umap.png'
) -> None:
    """
    Compute and plot UMAP embedding with cluster labels.

    Parameters
    ----------
    X : np.ndarray
        High-dimensional feature array (n_samples, n_features).
    labels : np.ndarray
        Cluster labels for each sample.
    n_neighbors : int
        UMAP n_neighbors parameter.
    min_dist : float
        UMAP min_dist parameter.
    figures_dir : str
        Directory to save the figure.
    filename : str
        Output filename.
    """
    if not HAS_UMAP:
        logger.warning("UMAP not installed. Skipping UMAP visualization.")
        return

    logger.info("Computing UMAP embedding...")

    # Compute UMAP
    reducer = umap.UMAP(n_neighbors=n_neighbors, min_dist=min_dist,
                        n_components=2, random_state=42)
    X_umap = reducer.fit_transform(X)

    # Plot using the clustering plot function
    plot_clustering_results(X_umap, labels, method_name='UMAP',
                           figures_dir=figures_dir, filename=filename)


def plot_parity(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    target_name: str,
    model_name: str,
    metrics: Optional[Dict[str, float]] = None,
    figures_dir: str = 'figures',
    filename: Optional[str] = None
) -> None:
    """
    Plot predicted vs. true values (parity plot).

    Parameters
    ----------
    y_true : np.ndarray
        True values.
    y_pred : np.ndarray
        Predicted values.
    target_name : str
        Name of the target variable.
    model_name : str
        Name of the model.
    metrics : Optional[Dict[str, float]]
        Performance metrics to display on the plot.
    figures_dir : str
        Directory to save the figure.
    filename : Optional[str]
        Output filename (auto-generated if None).
    """
    fig_path = ensure_figures_dir(figures_dir)

    if filename is None:
        filename = f'parity_{target_name}_{model_name}.png'

    fig, ax = plt.subplots(figsize=(7, 7))

    # Scatter plot
    ax.scatter(y_true, y_pred, alpha=0.5, s=30, edgecolors='k', linewidth=0.5)

    # Perfect prediction line
    min_val = min(y_true.min(), y_pred.min())
    max_val = max(y_true.max(), y_pred.max())
    ax.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Perfect prediction')

    ax.set_xlabel(f'True {target_name}')
    ax.set_ylabel(f'Predicted {target_name}')
    ax.set_title(f'Parity Plot: {target_name} ({model_name})')
    ax.legend()
    ax.grid(alpha=0.3)

    # Add metrics text box
    if metrics:
        textstr = '\n'.join([f'{k.upper()}: {v:.4f}' for k, v in metrics.items()])
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=9,
                verticalalignment='top', bbox=props)

    plt.tight_layout()
    plt.savefig(fig_path / filename, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved parity plot: {fig_path / filename}")


def plot_residuals(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    target_name: str,
    model_name: str,
    figures_dir: str = 'figures',
    filename: Optional[str] = None
) -> None:
    """
    Plot residuals analysis (histogram and residual plot).

    Parameters
    ----------
    y_true : np.ndarray
        True values.
    y_pred : np.ndarray
        Predicted values.
    target_name : str
        Name of the target variable.
    model_name : str
        Name of the model.
    figures_dir : str
        Directory to save the figure.
    filename : Optional[str]
        Output filename (auto-generated if None).
    """
    fig_path = ensure_figures_dir(figures_dir)

    if filename is None:
        filename = f'residuals_{target_name}_{model_name}.png'

    residuals = y_pred - y_true

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Residual histogram
    ax1.hist(residuals, bins=30, alpha=0.7, edgecolor='black')
    ax1.axvline(x=0, color='r', linestyle='--', linewidth=2)
    ax1.set_xlabel('Residual (Predicted - True)')
    ax1.set_ylabel('Frequency')
    ax1.set_title(f'Residual Distribution: {target_name} ({model_name})')
    ax1.grid(alpha=0.3)

    # Add statistics
    mean_res = residuals.mean()
    std_res = residuals.std()
    textstr = f'Mean: {mean_res:.4f}\nStd: {std_res:.4f}'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax1.text(0.05, 0.95, textstr, transform=ax1.transAxes, fontsize=9,
            verticalalignment='top', bbox=props)

    # Residual vs. predicted
    ax2.scatter(y_pred, residuals, alpha=0.5, s=30, edgecolors='k', linewidth=0.5)
    ax2.axhline(y=0, color='r', linestyle='--', linewidth=2)
    ax2.set_xlabel(f'Predicted {target_name}')
    ax2.set_ylabel('Residual')
    ax2.set_title(f'Residual Plot: {target_name} ({model_name})')
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(fig_path / filename, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved residuals plot: {fig_path / filename}")


def plot_model_comparison(
    results: Dict[str, Dict[str, Dict[str, float]]],
    metric: str = 'r2',
    figures_dir: str = 'figures',
    filename: Optional[str] = None
) -> None:
    """
    Plot comparison of models across different targets for a specific metric.

    Parameters
    ----------
    results : Dict[str, Dict[str, Dict[str, float]]]
        Nested dictionary: {model_name: {target_name: {metric: value}}}
    metric : str
        Metric to compare (e.g., 'r2', 'mae', 'rmse').
    figures_dir : str
        Directory to save the figure.
    filename : Optional[str]
        Output filename (auto-generated if None).
    """
    fig_path = ensure_figures_dir(figures_dir)

    if filename is None:
        filename = f'model_comparison_{metric}.png'

    # Reorganize data for plotting
    models = list(results.keys())
    targets = list(next(iter(results.values())).keys())

    # Create a DataFrame for easier plotting
    data = []
    for model in models:
        for target in targets:
            if metric in results[model][target]:
                data.append({
                    'Model': model,
                    'Target': target,
                    'Value': results[model][target][metric]
                })

    df = pd.DataFrame(data)

    if df.empty:
        logger.warning(f"No data available for metric '{metric}'")
        return

    # Create grouped bar chart
    fig, ax = plt.subplots(figsize=(12, 6))

    # Pivot for grouped bar chart
    pivot_df = df.pivot(index='Target', columns='Model', values='Value')
    pivot_df.plot(kind='bar', ax=ax, width=0.8, edgecolor='black', alpha=0.7)

    ax.set_ylabel(metric.upper())
    ax.set_title(f'Model Comparison: {metric.upper()} Across Targets')
    ax.legend(title='Model', loc='best')
    ax.grid(axis='y', alpha=0.3)
    plt.xticks(rotation=45, ha='right')

    plt.tight_layout()
    plt.savefig(fig_path / filename, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved model comparison plot: {fig_path / filename}")


def plot_feature_importance(
    importance_scores: np.ndarray,
    feature_names: List[str],
    model_name: str,
    target_name: str,
    top_n: int = 20,
    figures_dir: str = 'figures',
    filename: Optional[str] = None
) -> None:
    """
    Plot feature importance scores.

    Parameters
    ----------
    importance_scores : np.ndarray
        Feature importance scores.
    feature_names : List[str]
        Names of features.
    model_name : str
        Name of the model.
    target_name : str
        Name of the target variable.
    top_n : int
        Number of top features to display.
    figures_dir : str
        Directory to save the figure.
    filename : Optional[str]
        Output filename (auto-generated if None).
    """
    fig_path = ensure_figures_dir(figures_dir)

    if filename is None:
        filename = f'feature_importance_{target_name}_{model_name}.png'

    # Sort features by importance
    indices = np.argsort(importance_scores)[::-1][:top_n]
    top_features = [feature_names[i] for i in indices]
    top_scores = importance_scores[indices]

    fig, ax = plt.subplots(figsize=(10, max(6, top_n * 0.3)))

    # Horizontal bar chart
    y_pos = np.arange(len(top_features))
    ax.barh(y_pos, top_scores, alpha=0.7, edgecolor='black')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(top_features)
    ax.invert_yaxis()  # Highest importance on top
    ax.set_xlabel('Importance Score')
    ax.set_title(f'Top {top_n} Feature Importances: {target_name} ({model_name})')
    ax.grid(axis='x', alpha=0.3)

    plt.tight_layout()
    plt.savefig(fig_path / filename, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved feature importance plot: {fig_path / filename}")


def create_all_clustering_visualizations(
    X: np.ndarray,
    labels: np.ndarray,
    metrics: Dict[str, float],
    pca_model=None,
    config: Optional[dict] = None,
    figures_dir: str = 'figures'
) -> None:
    """
    Create all clustering visualizations at once.

    Parameters
    ----------
    X : np.ndarray
        Feature array (n_samples, n_features).
    labels : np.ndarray
        Cluster labels.
    metrics : Dict[str, float]
        Clustering metrics.
    pca_model : optional
        Fitted PCA model (if available).
    config : Optional[dict]
        Configuration dictionary for visualization settings.
    figures_dir : str
        Directory to save figures.
    """
    logger.info("Creating clustering visualizations...")

    # PCA plot (use first 2 components)
    if X.shape[1] >= 2:
        plot_clustering_results(X[:, :2], labels, method_name='PCA',
                               figures_dir=figures_dir, filename='clustering_pca.png')

    # PCA variance explained (if model available)
    if pca_model is not None and hasattr(pca_model, 'explained_variance_ratio_'):
        plot_pca_variance(pca_model, figures_dir=figures_dir)

    # Cluster metrics
    plot_cluster_metrics(metrics, figures_dir=figures_dir)

    # Cluster sizes
    plot_cluster_sizes(labels, figures_dir=figures_dir)

    # t-SNE visualization (if enabled in config)
    if config and config.get('visualization', {}).get('create_tsne', True):
        perplexity = config.get('visualization', {}).get('tsne_perplexity', 30)
        plot_tsne_embedding(X, labels, perplexity=perplexity, figures_dir=figures_dir)

    # UMAP visualization (if enabled in config)
    if config and config.get('visualization', {}).get('create_umap', True) and HAS_UMAP:
        n_neighbors = config.get('visualization', {}).get('umap_n_neighbors', 15)
        min_dist = config.get('visualization', {}).get('umap_min_dist', 0.1)
        plot_umap_embedding(X, labels, n_neighbors=n_neighbors, min_dist=min_dist,
                           figures_dir=figures_dir)

    logger.info(f"All clustering visualizations saved to {figures_dir}/")
