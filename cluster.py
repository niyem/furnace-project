"""
Clustering module for furnace efficiency data analysis.

This module provides unsupervised clustering algorithms with automatic
hyperparameter search and comprehensive evaluation metrics:

Algorithms:
- K-Means clustering with automatic K selection
- Gaussian Mixture Models (GMM) with BIC-based selection
- DBSCAN for density-based clustering

Evaluation Metrics:
- Silhouette score (higher is better, range [-1, 1])
- Calinski-Harabasz score (higher is better)
- Davies-Bouldin score (lower is better)

All clustering functions return cluster labels and evaluation metrics
for downstream analysis and visualization.
"""
# cluster.py
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, DBSCAN
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from utils import get_logger

logger = get_logger()

def _scores(X, labels):
    # if only 1 label, metrics fail; guard
    if len(np.unique(labels)) < 2:
        return {"silhouette": np.nan, "calinski_harabasz": np.nan, "davies_bouldin": np.nan}
    return {
        "silhouette": float(silhouette_score(X, labels)),
        "calinski_harabasz": float(calinski_harabasz_score(X, labels)),
        "davies_bouldin": float(davies_bouldin_score(X, labels)),
    }

def _kmeans_search(X, k_range):
    best = None
    for k in k_range:
        km = KMeans(n_clusters=k, n_init=20, random_state=42)
        lab = km.fit_predict(X)
        sc = _scores(X, lab)
        logger.info(f"[KMeans] k={k} -> {sc}")
        # pick by silhouette (desc), break ties by CH (desc), DB (asc)
        key = (np.nan_to_num(sc["silhouette"], nan=-1.0), np.nan_to_num(sc["calinski_harabasz"], nan=-1.0), -np.nan_to_num(sc["davies_bouldin"], nan=1e9))
        if (best is None) or (key > best[0]):
            best = (key, lab, {"k": k, **sc})
    return best[1], best[2]

def _gmm_bic_search(X, k_range, covariance_type="full"):
    best_bic = np.inf; best_res = None
    for k in k_range:
        gmm = GaussianMixture(n_components=k, covariance_type=covariance_type, random_state=42, n_init=5)
        gmm.fit(X)
        labels = gmm.predict(X)
        bic = gmm.bic(X)
        sc = _scores(X, labels)
        logger.info(f"[GMM] k={k} cov={covariance_type} -> BIC={bic:.1f}, {sc}")
        if bic < best_bic:
            best_bic = bic
            best_res = (labels, {"k": k, "bic": float(bic), "covariance_type": covariance_type, **sc})
    return best_res

def _dbscan_fit(X, eps, min_samples):
    db = DBSCAN(eps=eps, min_samples=min_samples)
    labels = db.fit_predict(X)  # -1 = noise
    sc = _scores(X, labels)
    n_cl = len(np.unique(labels[labels!=-1]))
    logger.info(f"[DBSCAN] eps={eps}, min_samples={min_samples} -> clusters={n_cl}, {sc}")
    return labels, {"eps": eps, "min_samples": min_samples, "n_clusters": int(n_cl), **sc}

def cluster(Z: np.ndarray, cfg: dict):
    algo = cfg.get("algorithm", "kmeans").lower()

    if algo == "kmeans":
        k = int(cfg.get("kmeans_k", 3))
        # optional search range
        k_range = cfg.get("kmeans_k_range")
        if k_range:
            labels, info = _kmeans_search(Z, range(int(k_range[0]), int(k_range[1])+1))
            info.update({"algorithm": "kmeans"})
            return labels, None, info
        km = KMeans(n_clusters=k, n_init=20, random_state=42)
        labels = km.fit_predict(Z)
        info = {"algorithm": "kmeans", "k": k, **_scores(Z, labels)}
        return labels, km, info

    elif algo == "gmm":
        kr = cfg.get("gmm_k_range", [2, 8])
        cov = cfg.get("covariance_type", "full")
        labels, info = _gmm_bic_search(Z, range(int(kr[0]), int(kr[1])+1), covariance_type=cov)
        info.update({"algorithm": "gmm"})
        return labels, None, info

    elif algo == "dbscan":
        eps = float(cfg.get("dbscan", {}).get("eps", 0.5))
        ms  = int(cfg.get("dbscan", {}).get("min_samples", 10))
        labels, info = _dbscan_fit(Z, eps, ms)
        info.update({"algorithm": "dbscan"})
        return labels, None, info

    else:
        raise ValueError(f"Unknown clustering algorithm: {algo}")
