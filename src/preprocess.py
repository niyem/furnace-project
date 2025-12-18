import pandas as pd
import numpy as np
import os

def clean_data(file_path):
    """
    Reads the raw data (CSV or Excel), handles basic cleaning, and returns a DataFrame.
    """
    print(f"      [Preprocess] Loading file: {file_path}")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Could not find file at: {file_path}")

    # --- MODIFICATION START: Detect file type ---
    if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        try:
            # Reads the first sheet by default. Ensure 'openpyxl' is installed.
            df = pd.read_excel(file_path, engine='openpyxl')
        except ImportError:
            raise ImportError("To read Excel files, you must install openpyxl: pip install openpyxl")
    else:
        # Default to CSV
        df = pd.read_csv(file_path)
    # --- MODIFICATION END ---

    # 1. Drop completely empty columns or rows
    initial_shape = df.shape
    df.dropna(how='all', axis=1, inplace=True)
    df.dropna(how='all', axis=0, inplace=True)

    # 2. Ensure numeric columns are actually numeric
    # List of key columns that must be numeric for the project
    numeric_cols = [
        'ThermalEffCold', 'ThermalEffHot', 'Thermal efficiency(%)  LOW POWER(SIMMER)',
        'FirepowerCold', 'FirepowerHot', 'Firepower(watt)  LOW POWER(SIMMER)',
        'FuelMoistWet', 'TimeToBoilCold', 'TimeToBoilHot',
        'AvgCO2', 'TotalCO'
    ]
    
    for col in numeric_cols:
        if col in df.columns:
            # Force conversion to numeric, turning errors (like strings) into NaN
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # 3. Fill missing values
    # We use the median because it's robust to outliers
    num_df = df.select_dtypes(include=[np.number])
    df[num_df.columns] = num_df.fillna(num_df.median())

    # 4. Standardize Efficiency to Percentage
    # Some datasets have efficiency as 0.18, others as 18.0. We standardize to 0-100 scale.
    # Check if max efficiency < 1.0 (implying decimal notation)
    if 'ThermalEffCold' in df.columns and df['ThermalEffCold'].max() < 1.0:
        # print("      [Info] Converting efficiencies from decimal to percentage...")
        df['ThermalEffCold_pct'] = df['ThermalEffCold'] * 100
        df['ThermalEffHot_pct'] = df['ThermalEffHot'] * 100
        if 'Thermal efficiency(%)  LOW POWER(SIMMER)' in df.columns:
            df['ThermalEffSimmer_pct'] = df['Thermal efficiency(%)  LOW POWER(SIMMER)'] * 100
    else:
        # Already percentages, just rename for consistency
        df['ThermalEffCold_pct'] = df['ThermalEffCold']
        df['ThermalEffHot_pct'] = df['ThermalEffHot']
        if 'Thermal efficiency(%)  LOW POWER(SIMMER)' in df.columns:
            df['ThermalEffSimmer_pct'] = df['Thermal efficiency(%)  LOW POWER(SIMMER)']

    # 5. Handle Column Renaming for easier coding later
    rename_map = {
        'Thermal efficiency(%)  LOW POWER(SIMMER)': 'ThermalEffSimmer',
        'Firepower(watt)  LOW POWER(SIMMER)': 'FirepowerSimmer',
        'Specific fuel consumption (g/l)  LOW POWER(SIMMER)': 'SFC_Simmer',
        'Burning rate(g/min) (COLD START) ': 'BurnRateCold',
        'Burning rate(g/min) (HOT START) ': 'BurnRateHot'
    }
    df.rename(columns=rename_map, inplace=True)

    print(f"      [Preprocess] Cleaned shape: {df.shape} (Dropped {initial_shape[0] - df.shape[0]} empty rows)")
    return df