# regression.py
from __future__ import annotations
from pathlib import Path
from typing import Dict, Iterable, List
import numpy as np
import pandas as pd

# plotting
import matplotlib.pyplot as plt

# models & tools
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

# Try LightGBM if the user selected it
try:
    import lightgbm as lgb
    _HAS_LGB = True
except Exception:
    _HAS_LGB = False


# ---------------------
# small plotting helpers
# ---------------------
def _ensure_dir(p: str | Path) -> Path:
    p = Path(p)
    p.mkdir(parents=True, exist_ok=True)
    return p

def _plot_parity(y_true, y_pred, outpath: Path, title: str):
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    plt.figure(figsize=(5,5))
    plt.scatter(y_true, y_pred, s=8, alpha=0.5)
    lo = float(np.nanmin([y_true.min(), y_pred.min()]))
    hi = float(np.nanmax([y_true.max(), y_pred.max()]))
    if not np.isfinite(lo) or not np.isfinite(hi):
        lo, hi = 0.0, 1.0
    plt.plot([lo, hi], [lo, hi])
    plt.xlabel("True"); plt.ylabel("Predicted")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(outpath, dpi=160); plt.close()

def _plot_residual_hist(residuals, outpath: Path, title: str):
    residuals = np.asarray(residuals, dtype=float)
    plt.figure(figsize=(5,4))
    plt.hist(residuals, bins=30)
    plt.xlabel("Residual (true - pred)"); plt.ylabel("Count")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(outpath, dpi=160); plt.close()

def _plot_learning_curve(model, outpath: Path, title: str):
    curve = getattr(model, "loss_curve_", None)
    if curve is None or len(curve) == 0:
        return
    plt.figure(figsize=(7,4))
    plt.plot(range(1, len(curve)+1), curve)
    plt.xlabel("Epoch"); plt.ylabel("Loss")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(outpath, dpi=160); plt.close()


# ---------------------
# main trainer
# ---------------------
def train_multi_target(
    X: pd.DataFrame,
    y: pd.DataFrame,
    model_name: str = "mlp",                 # "mlp" | "lightgbm"
    test_size: float = 0.2,
    random_state: int = 42,
    metrics: Iterable[str] = ("r2","mae","rmse"),
    save_details_dir: str | Path | None = None,
    save_training_curves: bool = True,
    loss_metric: str = "l2",                 # unused here, kept for API compat
    early_stopping_rounds: int = 100,        # used if lightgbm
    max_estimators: int = 2000,              # used if lightgbm
    **kwargs
) -> Dict[str, Dict[str, float]]:
    """
    Trains one regressor per target column in y and returns a metrics dict:
      { target: {"r2":..., "mae":..., "rmse":...}, ... }

    Also writes, for each target:
      - <reports>/regression_details/<Target>_predictions.csv
      - <reports>/regression_details/parity_<Target>.png
      - <reports>/regression_details/residuals_<Target>.png
      - <reports>/regression_details/curve_<Target>.png (MLP only)
    """
    rng = np.random.RandomState(random_state)
    details_dir = _ensure_dir(save_details_dir) if save_details_dir else None

    # Train/valid split (same split for all targets so indices align)
    X_tr, X_te, idx_tr, idx_te = train_test_split(
        X, np.arange(len(X)), test_size=test_size, random_state=random_state, shuffle=True
    )

    results: Dict[str, Dict[str, float]] = {}

    for target in y.columns:
        y_all = y[target].astype(float)
        y_tr = y_all.iloc[idx_tr]
        y_te = y_all.iloc[idx_te]

        # Choose model
        if model_name.lower() == "mlp":
            model = MLPRegressor(
                hidden_layer_sizes=(256,128),
                activation="relu",
                solver="adam",
                alpha=0.0001,
                learning_rate_init=1e-3,
                max_iter=400,
                random_state=random_state,
                early_stopping=True,
                n_iter_no_change=40,
                verbose=False,
            )
            model.fit(X_tr, y_tr)
        elif model_name.lower() == "lightgbm":
            if not _HAS_LGB:
                raise RuntimeError("LightGBM not installed. Use model_name='mlp' or install lightgbm.")
            dtrain = lgb.Dataset(X_tr, label=y_tr)
            dvalid = lgb.Dataset(X_te, label=y_te, reference=dtrain)
            params = dict(
                objective="regression",
                metric="rmse",
                learning_rate=0.05,
                num_leaves=31,
                feature_fraction=0.9,
                bagging_fraction=0.8,
                bagging_freq=1,
                verbose=-1,
                seed=random_state,
            )
            model = lgb.train(
                params,
                dtrain,
                num_boost_round=max_estimators,
                valid_sets=[dvalid],
                valid_names=["valid"],
                early_stopping_rounds=early_stopping_rounds,
                verbose_eval=False,
            )
        else:
            raise ValueError(f"Unknown model_name='{model_name}'")

        # Predict & metrics
        y_pred = model.predict(X_te)
        r2  = float(r2_score(y_te, y_pred))
        mae = float(mean_absolute_error(y_te, y_pred))
        rmse = float(np.sqrt(mean_squared_error(y_te, y_pred)))

        res = {}
        if "r2" in metrics:   res["r2"] = r2
        if "mae" in metrics:  res["mae"] = mae
        if "rmse" in metrics: res["rmse"] = rmse
        results[target] = res

        # Save artifacts
        if details_dir is not None:
            # predictions CSV
            pd.DataFrame({"y_true": y_te.values, "y_pred": y_pred}).to_csv(
                details_dir / f"{target}_predictions.csv", index=False
            )
            # plots
            _plot_parity(y_te, y_pred, details_dir / f"parity_{target}.png", f"Parity: {target}")
            _plot_residual_hist(y_te.values - y_pred, details_dir / f"residuals_{target}.png", f"Residuals: {target}")
            if save_training_curves and model_name.lower() == "mlp":
                _plot_learning_curve(model, details_dir / f"curve_{target}.png", f"Learning curve: {target}")

    return results
