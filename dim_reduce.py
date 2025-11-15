# dim_reduce.py
from __future__ import annotations

import numpy as np
import pandas as pd

from sklearn.decomposition import PCA
from utils import get_logger

logger = get_logger()

# Optional deps
try:
    import umap  # umap-learn
    _HAS_UMAP = True
except Exception:
    _HAS_UMAP = False

try:
    import torch
    import torch.nn as nn
    from torch.utils.data import TensorDataset, DataLoader
    _HAS_TORCH = True
except Exception:
    _HAS_TORCH = False


# =========================================================
# -------------------- Autoencoder ------------------------
# =========================================================

class _MLPEncoder(nn.Module):
    def __init__(self, in_dim: int, hidden: list[int], latent: int, dropout: float = 0.0):
        super().__init__()
        layers = []
        d = in_dim
        for h in hidden:
            layers += [nn.Linear(d, h), nn.ReLU(), nn.Dropout(dropout)]
            d = h
        layers += [nn.Linear(d, latent)]
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)


class _MLPDecoder(nn.Module):
    def __init__(self, latent: int, hidden: list[int], out_dim: int, dropout: float = 0.0):
        super().__init__()
        layers = []
        d = latent
        for h in reversed(hidden):
            layers += [nn.Linear(d, h), nn.ReLU(), nn.Dropout(dropout)]
            d = h
        layers += [nn.Linear(d, out_dim)]
        self.net = nn.Sequential(*layers)

    def forward(self, z):
        return self.net(z)


def _fit_autoencoder(X_np: np.ndarray, cfg: dict):
    if not _HAS_TORCH:
        raise RuntimeError(
            "Autoencoder selected but PyTorch is not installed. "
            "Install torch/torchvision or switch method."
        )

    device = "cuda" if torch.cuda.is_available() else "cpu"
    latent = int(cfg.get("n_components", 8))
    ae_cfg = cfg.get("ae", {}) or {}

    hidden   = list(ae_cfg.get("hidden", [128, 64]))
    epochs   = int(ae_cfg.get("epochs", 300))
    batch_sz = int(ae_cfg.get("batch_size", 64))
    lr       = float(ae_cfg.get("lr", 1e-3))
    dropout  = float(ae_cfg.get("dropout", 0.0))
    patience = int(ae_cfg.get("patience", 30))

    x = torch.tensor(X_np, dtype=torch.float32)
    ds = TensorDataset(x)
    dl = DataLoader(ds, batch_size=batch_sz, shuffle=True)

    enc = _MLPEncoder(X_np.shape[1], hidden, latent, dropout).to(device)
    dec = _MLPDecoder(latent, hidden, X_np.shape[1], dropout).to(device)

    params = list(enc.parameters()) + list(dec.parameters())
    opt = torch.optim.Adam(params, lr=lr, weight_decay=1e-5)
    loss_fn = nn.MSELoss()

    best = float("inf")
    wait = 0
    best_state = None

    for ep in range(epochs):
        enc.train(); dec.train()
        run = 0.0
        for (xb,) in dl:
            xb = xb.to(device)
            opt.zero_grad()
            z = enc(xb)
            xr = dec(z)
            loss = loss_fn(xr, xb)
            loss.backward()
            opt.step()
            run += loss.item() * xb.size(0)

        epoch_loss = run / len(ds)
        if ep % 10 == 0:
            logger.info(f"[AE] epoch {ep:04d}  recon_mse={epoch_loss:.6f}")

        if epoch_loss < best - 1e-6:
            best = epoch_loss
            wait = 0
            best_state = (enc.state_dict(), dec.state_dict())
        else:
            wait += 1
            if wait >= patience:
                logger.info(f"[AE] early stop @ {ep}  best recon_mse={best:.6f}")
                break

    if best_state is not None:
        enc.load_state_dict(best_state[0])

    enc.eval()
    with torch.no_grad():
        Z = enc(torch.tensor(X_np, dtype=torch.float32).to(device)).cpu().numpy()

    info = {"method": "autoencoder", "latent": latent, "recon_mse": float(best)}
    return Z, info


# =========================================================
# ------------------------ UMAP ---------------------------
# =========================================================

def _fit_umap(X_np: np.ndarray, cfg: dict):
    if not _HAS_UMAP:
        raise RuntimeError(
            "UMAP selected but umap-learn is not installed. "
            "pip install umap-learn or switch method."
        )
    params = cfg.get("umap", {}) or {}
    n_neighbors = int(params.get("n_neighbors", 15))
    min_dist    = float(params.get("min_dist", 0.1))
    metric      = str(params.get("metric", "euclidean"))
    n_components = int(cfg.get("n_components", 2))

    reducer = umap.UMAP(
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        metric=metric,
        n_components=n_components,
        random_state=42,
    )
    Z = reducer.fit_transform(X_np)
    info = {
        "method": "umap",
        "n_components": int(n_components),
        "n_neighbors": n_neighbors,
        "min_dist": min_dist,
        "metric": metric,
    }
    return Z, info


# =========================================================
# ------------------------- PCA ---------------------------
# =========================================================

def _fit_pca(X_np: np.ndarray, cfg: dict):
    n_comp_cfg = cfg.get("n_components", 10)
    whiten = bool(cfg.get("pca_whiten", False))

    # n_components can be an int (k) or a float (0<val<=1) for variance ratio like 0.95
    if isinstance(n_comp_cfg, float):
        if not (0 < n_comp_cfg <= 1.0):
            raise ValueError("PCA n_components float must be in (0, 1].")
        n_components = n_comp_cfg
    elif isinstance(n_comp_cfg, (int, np.integer)):
        n_components = int(n_comp_cfg)
    else:
        raise ValueError("PCA n_components must be int or float in (0,1].")

    pca = PCA(n_components=n_components, whiten=whiten, random_state=42)
    Z = pca.fit_transform(X_np)

    evr = pca.explained_variance_ratio_
    logger.info(f"PCA explained variance (first 5): {np.round(evr[:5], 6)}")
    if isinstance(n_components, float):
        logger.info(f"PCA kept {Z.shape[1]} components explaining "
                    f"{evr.sum():.4f} total variance.")

    info = {
        "method": "pca",
        "n_components_kept": int(Z.shape[1]),
        "whiten": whiten,
        "explained_variance_ratio": evr.tolist(),
        "explained_variance_cum": float(evr.sum()),
    }
    return Z, info


# =========================================================
# --------------------- Public API ------------------------
# =========================================================

def reduce_dimensions(X: pd.DataFrame, cfg: dict):
    """
    Reduce dimensions of features X according to cfg, returning:
        Z: np.ndarray (n_samples, n_latent)
        info: dict with method-specific metadata
    cfg supports:
      method: "pca" | "umap" | "autoencoder"
      n_components: int or float (for PCA 0<val<=1), default 10
      pca_whiten: bool
      umap: {n_neighbors, min_dist, metric}
      ae:   {hidden, epochs, batch_size, lr, dropout, patience}
    """
    method = str(cfg.get("method", "pca")).lower()

    # Ensure float32 numpy (preprocess already scaled/imputed)
    X_np = X.values.astype("float32", copy=False)

    if method == "pca":
        Z, info = _fit_pca(X_np, cfg)
    elif method == "umap":
        Z, info = _fit_umap(X_np, cfg)
    elif method == "autoencoder":
        Z, info = _fit_autoencoder(X_np, cfg)
    else:
        raise ValueError(f"Unknown dim_reduce method: {method}")

    logger.info(f"Dimensionality reduction [{info['method']}]: X {X.shape} -> Z {Z.shape}")
    return Z, info
