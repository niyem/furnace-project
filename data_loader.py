"""
Data loading module for furnace efficiency project.

This module handles loading data from Excel or CSV files and normalizes
column names to ensure consistency across the pipeline.
"""

from pathlib import Path
import re
import pandas as pd
from utils import get_logger

logger = get_logger()

# Map actual Excel headers to canonical names used in config/pipeline
COLUMN_ALIASES = {
    "Burning rate(g/min) (COLD START)": "BurnRateColdStart",
    "Burning rate(g/min) (HOT START)":  "BurnRateHotStart",
    "FirepowerColdStart":               "FirepowerColdStart",
    "FirepowerHotStart":                "FirepowerHotStart",
    "ThermalEffColdStart":              "ThermalEffColdStart",
    "ThermalEffHotStart":               "ThermalEffHotStart",
    "TempCorrSpecificConsumptionCold":  "TempCorrSpecificConsumptionCold",
    "SpecificFuelConsumptionSimmer":    "TempCorrSpecificConsumptionCold",
}


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names to match pipeline expectations.

    Applies two-step normalization:
    1. Direct aliasing for known column names
    2. Fallback normalization: strip spaces, remove symbols, compact

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame with potentially inconsistent column names.

    Returns
    -------
    pd.DataFrame
        DataFrame with normalized column names.

    Examples
    --------
    >>> df = pd.DataFrame({'Burning rate(g/min) (COLD START)': [1, 2, 3]})
    >>> normalized_df = normalize_columns(df)
    >>> 'BurnRateColdStart' in normalized_df.columns
    True
    """
    # 1) Apply direct aliases (exact match)
    df = df.rename(columns=COLUMN_ALIASES)

    # 2) Fallback normalization: strip spaces/symbols and compact
    def clean(c: str) -> str:
        """Clean a single column name."""
        c = str(c).strip()
        c = re.sub(r"\s+", " ", c)  # Normalize whitespace
        c = c.replace("/", " per ")
        c = c.replace("%", "pct")
        c = re.sub(r"[()]", "", c)  # Remove parentheses
        c = c.replace(" ", "")  # Remove all spaces
        return c

    new_cols = {c: COLUMN_ALIASES.get(c, clean(c)) for c in df.columns}
    return df.rename(columns=new_cols)


def load_data(path: str, sheet_name: str = 'Sheet1', index_col=None) -> pd.DataFrame:
    """
    Load data from Excel or CSV file with column normalization.

    Supports both Excel (.xlsx, .xls) and CSV (.csv) formats.
    Automatically normalizes column names for pipeline consistency.

    Parameters
    ----------
    path : str
        Path to the data file.
    sheet_name : str, optional
        Sheet name for Excel files, by default 'Sheet1'.
    index_col : int or str, optional
        Column to use as index, by default None.

    Returns
    -------
    pd.DataFrame
        Loaded and normalized DataFrame.

    Raises
    ------
    FileNotFoundError
        If the data file doesn't exist.
    ValueError
        If the file type is unsupported or sheet name is invalid.

    Examples
    --------
    >>> df = load_data('ml_ready_data.csv')
    >>> df.shape
    (200, 33)
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Data file not found: {p}")

    logger.info(f"Loading data from {p}")

    if path.lower().endswith(('.xlsx', '.xls')):
        # Optional safety: verify the sheet exists
        xl = pd.ExcelFile(path)
        if sheet_name not in xl.sheet_names:
            raise ValueError(f"Sheet '{sheet_name}' not found. Available: {xl.sheet_names}")
        df = pd.read_excel(path, sheet_name=sheet_name)
    elif path.lower().endswith('.csv'):
        df = pd.read_csv(path, index_col=index_col)
    else:
        raise ValueError("Unsupported file type. Use .xlsx or .csv")

    df = normalize_columns(df)
    logger.info(f"Loaded shape: {df.shape}")
    logger.info(f"Columns (normalized) sample: {list(df.columns)[:12]} ...")
    return df
