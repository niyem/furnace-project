"""
Data preprocessing module for furnace efficiency ML pipeline.

This module handles data cleaning, feature engineering, and transformation:
- Missing value filtering (columns and rows)
- Data type coercion (handling time formats, numeric conversion)
- Feature imputation (median/mean/mode)
- Feature scaling (StandardScaler or MinMaxScaler)
- Near-constant feature removal
- Duplicate column handling

The preprocessing pipeline ensures clean, numeric feature matrices ready
for dimensionality reduction and machine learning.
"""

import re
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.feature_selection import VarianceThreshold
from utils import get_logger

logger = get_logger()

_TIME_RE = re.compile(r"^\s*\d{1,2}:\d{2}(:\d{2})?\s*$")

def _coerce_column_to_numeric(col: pd.Series) -> pd.Series:
    """
    Coerce a column to numeric:
      - If it looks like time 'HH:MM(:SS)', convert to total seconds
      - Else try to_numeric (handle commas/whitespace)
    """
    s = col.copy()

    sample = s.dropna().astype(str).str.strip()
    if (sample.str.match(_TIME_RE)).any():
        try:
            s_ = s.astype(str).str.strip()
            td = pd.to_timedelta(s_, errors="coerce")
            return td.dt.total_seconds()
        except Exception:
            pass

    try:
        return pd.to_numeric(
            s.astype(str).str.replace(",", "", regex=False).str.strip(),
            errors="coerce"
        )
    except Exception:
        return pd.Series(np.nan, index=s.index)

def _make_unique_columns(cols: pd.Index) -> pd.Index:
    """
    Ensure column names are unique by appending '__1', '__2', ... to repeats.
    LightGBM requires unique feature names.
    """
    seen = {}
    new = []
    for c in cols:
        if c not in seen:
            seen[c] = 0
            new.append(c)
        else:
            seen[c] += 1
            new.append(f"{c}__{seen[c]}")
    return pd.Index(new)

def basic_clean(df: pd.DataFrame, cfg: dict, targets: list | None):
    """
    Cleaning pipeline:
      1) Drop cols/rows with too many NaNs (per cfg thresholds)
      2) Split X (features) and y (targets)
      3) Coerce ALL feature columns to numeric (and targets too) using positional indexing (safe for duplicate names)
      4) Make feature column names unique (prevents LightGBM 'appears more than one time')
      5) Impute features
      6) Optionally remove near-constant features
      7) Scale features
    Returns:
      X_scaled (pd.DataFrame), y (pd.DataFrame or None)
    """
    targets = targets or []
    present_targets = [t for t in targets if t in df.columns]

    # --- Warn on duplicate column names ---
    if df.columns.duplicated().any():
        dup_counts = pd.Series(df.columns[df.columns.duplicated()]).value_counts().to_dict()
        logger.warning(f"Duplicate column names detected (counts include repeats): {dup_counts}")

    # --- 1) Missingness filtering on non-targets ---
    col_keep_threshold = cfg.get("drop_na_threshold_col", 0.6)  # keep if >= 60% present
    row_keep_threshold = cfg.get("drop_na_threshold_row", 0.6)  # keep if >= 60% present

    non_target_cols = [c for c in df.columns if c not in present_targets]
    if non_target_cols:
        miss_frac_cols = df[non_target_cols].isna().mean()
        cols_to_keep = list(miss_frac_cols[miss_frac_cols <= (1 - col_keep_threshold)].index)
    else:
        cols_to_keep = []

    # Always include targets
    cols_final = cols_to_keep + present_targets
    df = df[cols_final].copy()

    # Row filtering based on non-targets only
    non_target_cols = [c for c in df.columns if c not in present_targets]
    if non_target_cols:
        row_miss_frac = df[non_target_cols].isna().mean(axis=1)
        df = df.loc[row_miss_frac <= (1 - row_keep_threshold)].copy()

    # --- 2) Split X / y ---
    y = df[present_targets].copy() if present_targets else None
    X = df.drop(columns=present_targets, errors="ignore").copy()  # ensure targets don't leak into features

    # If targets themselves have duplicate names, keep first occurrence to avoid ambiguity
    if y is not None and y.columns.duplicated().any():
        dup_info = pd.Series(y.columns[y.columns.duplicated()]).value_counts().to_dict()
        logger.warning(f"Dropping duplicate target columns (keeping first occurrence): {dup_info}")
        y = y.loc[:, ~y.columns.duplicated()].copy()

    # --- 3) Coerce features to numeric (positional iteration) ---
    for i in range(X.shape[1]):
        s = X.iloc[:, i]
        if not np.issubdtype(s.dtype, np.number):
            X.iloc[:, i] = _coerce_column_to_numeric(s)

    # Coerce targets too (do NOT impute targets)
    if y is not None and y.shape[1] > 0:
        for j in range(y.shape[1]):
            s = y.iloc[:, j]
            if not np.issubdtype(s.dtype, np.number):
                y.iloc[:, j] = _coerce_column_to_numeric(s)

    # --- 4) Make feature names unique (required by LightGBM) ---
    if X.columns.duplicated().any():
        dup_counts = pd.Series(X.columns[X.columns.duplicated()]).value_counts().to_dict()
        logger.warning(f"Making feature names unique (duplicates found): {dup_counts}")
        X.columns = _make_unique_columns(X.columns)

    # --- 5) Impute features ---
    strategy = cfg.get("impute_strategy", "median")
    imputer = SimpleImputer(strategy=strategy)
    X_imputed = pd.DataFrame(imputer.fit_transform(X), columns=X.columns, index=X.index)

    # --- 6) Remove near-constant features (optional) ---
    if cfg.get("remove_near_constant", True):
        vt = VarianceThreshold(threshold=cfg.get("variance_threshold", 0.0))
        X_imputed = pd.DataFrame(
            vt.fit_transform(X_imputed),
            columns=X_imputed.columns[vt.get_support()],
            index=X_imputed.index
        )

    # --- 7) Scale features ---
    scaler = StandardScaler() if cfg.get("scale", "standard") == "standard" else MinMaxScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X_imputed), columns=X_imputed.columns, index=X_imputed.index)

    logger.info(f"Preprocessed X shape: {X_scaled.shape} ; y shape: {None if y is None else y.shape}")
    return X_scaled, y
