# data_loader.py
from pathlib import Path
import re
import pandas as pd
from utils import get_logger

logger = get_logger()

# ---- Map actual Excel headers → canonical names used in config/pipeline ----
COLUMN_ALIASES = {
    "Burning rate(g/min) (COLD START)": "BurnRateColdStart",
    "Burning rate(g/min) (HOT START)":  "BurnRateHotStart",
    "FirepowerColdStart":               "FirepowerColdStart",
    "FirepowerHotStart":                "FirepowerHotStart",
    "ThermalEffColdStart":              "ThermalEffColdStart",
    "ThermalEffHotStart":               "ThermalEffHotStart",
    "TempCorrSpecificConsumptionCold":  "TempCorrSpecificConsumptionCold",
    # If your sheet uses SpecificFuelConsumptionSimmer, normalize it to the column your pipeline expects:
    "SpecificFuelConsumptionSimmer":    "TempCorrSpecificConsumptionCold",
}

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Apply aliases and a safe normalization so headers match pipeline expectations."""
    # 1) apply direct aliases (exact match)
    df = df.rename(columns=COLUMN_ALIASES)

    # 2) fallback normalization: strip spaces/symbols and compact
    def clean(c: str) -> str:
        c = str(c).strip()
        c = re.sub(r"\s+", " ", c)
        c = c.replace("/", " per ")
        c = c.replace("%", "pct")
        c = re.sub(r"[()]", "", c)
        c = c.replace(" ", "")
        return c

    new_cols = {c: COLUMN_ALIASES.get(c, clean(c)) for c in df.columns}
    return df.rename(columns=new_cols)

def load_data(path: str, sheet_name='Sheet1', index_col=None) -> pd.DataFrame:
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
