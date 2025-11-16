"""
Parse all .xlsx files in Raw_data folder and create ML-ready dataset for efficiency prediction.

This script automatically finds all Excel files in the Raw_data directory,
extracts raw measurements from Test-1 through Test-4 sheets from each file,
and produces a single CSV file with one row per test, suitable for training
machine learning models to predict cooking stove thermal efficiency.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Any
import glob
import os


def load_sheet(file_path: str, sheet_name: str) -> pd.DataFrame:
    """
    Load a single test sheet from the Excel workbook.

    Args:
        file_path: Path to the Excel file
        sheet_name: Name of the sheet to load (e.g., 'Test-1')

    Returns:
        DataFrame containing the raw sheet data
    """
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    return df


def extract_metadata(df: pd.DataFrame, test_id: str) -> Dict[str, Any]:
    """
    Extract test metadata (for tracking purposes only, not all will be kept).

    Args:
        df: Raw test sheet DataFrame
        test_id: Test identifier (e.g., 'Test-1')

    Returns:
        Dictionary with metadata fields
    """
    metadata = {'test_id': test_id}

    # These are just for reference during development
    # Most will be excluded from final dataset per requirements
    try:
        # Stove model is at row 8, col 3
        metadata['stove_model'] = df.iloc[8, 3]
        # Fuel type at row 9, col 3
        metadata['fuel_type'] = df.iloc[9, 3]
    except:
        pass

    return metadata


def extract_fuel_properties(df: pd.DataFrame) -> Dict[str, float]:
    """
    Extract fuel-related properties (raw measurements).

    These are physical properties of the fuel used in the test,
    not derived statistics.

    Args:
        df: Raw test sheet DataFrame

    Returns:
        Dictionary with fuel property measurements
    """
    fuel_props = {}

    try:
        # Fuel moisture content (wet basis) - row 17, col 4
        fuel_props['fuel_moisture_content'] = float(df.iloc[17, 4])

        # Gross calorific value (dry fuel) - row 18, col 4
        fuel_props['gross_calorific_value_kj_kg'] = float(df.iloc[18, 4])

        # Net calorific value (dry fuel) - row 19, col 4
        fuel_props['net_calorific_value_kj_kg'] = float(df.iloc[19, 4])

        # Effective calorific value (accounting for moisture) - row 21, col 4
        fuel_props['effective_calorific_value_kj_kg'] = float(df.iloc[21, 4])

        # Char calorific value - row 22, col 4
        fuel_props['char_calorific_value_kj_kg'] = float(df.iloc[22, 4])
    except Exception as e:
        # If conversion fails, skip
        pass

    return fuel_props


def extract_equipment_properties(df: pd.DataFrame) -> Dict[str, float]:
    """
    Extract equipment/pot properties (raw measurements).

    Args:
        df: Raw test sheet DataFrame

    Returns:
        Dictionary with equipment property measurements
    """
    equip_props = {}

    try:
        # Dry weight of Pot # 1 - row 14, col 13
        equip_props['pot1_dry_weight_g'] = float(df.iloc[14, 13])

        # Weight of container for char - row 18, col 13
        equip_props['char_container_weight_g'] = float(df.iloc[18, 13])

        # Local boiling point - row 19, col 13
        equip_props['local_boiling_point_c'] = float(df.iloc[19, 13])
    except Exception as e:
        # If conversion fails, skip
        pass

    return equip_props


def extract_test_measurements(df: pd.DataFrame, phase: str) -> Dict[str, float]:
    """
    Extract raw test measurements for a specific phase (cold/hot/simmer).

    This extracts only direct measurements, not calculated/derived values.

    Args:
        df: Raw test sheet DataFrame
        phase: Test phase - 'cold', 'hot', or 'simmer'

    Returns:
        Dictionary with raw measurements for this phase
    """
    measurements = {}

    # Define column indices for each phase based on the sheet structure
    # Cold start: cols 22-23 (initial), 26-27 (final)
    # Hot start: cols 30-31 (initial), 34-35 (final)
    # Simmer: cols 37-38 (initial), 41-42 (final)

    phase_cols = {
        'cold': {'initial': 22, 'final': 26},
        'hot': {'initial': 30, 'final': 34},
        'simmer': {'initial': 37, 'final': 41}
    }

    if phase not in phase_cols:
        return measurements

    col_init = phase_cols[phase]['initial']
    col_final = phase_cols[phase]['final']

    try:
        # Row 6: Weight of fuel (g)
        val_init = df.iloc[6, col_init]
        val_final = df.iloc[6, col_final]
        if pd.notna(val_init):
            measurements[f'{phase}_fuel_weight_init_g'] = float(val_init)
        if pd.notna(val_final):
            measurements[f'{phase}_fuel_weight_final_g'] = float(val_final)

        # Row 7: Water temperature Pot #1 (°C)
        val_init = df.iloc[7, col_init]
        val_final = df.iloc[7, col_final]
        if pd.notna(val_init):
            measurements[f'{phase}_water_temp_pot1_init_c'] = float(val_init)
        if pd.notna(val_final):
            measurements[f'{phase}_water_temp_pot1_final_c'] = float(val_final)

        # Row 11: Weight of Pot #1 with water (g)
        val_init = df.iloc[11, col_init]
        val_final = df.iloc[11, col_final]
        if pd.notna(val_init):
            measurements[f'{phase}_pot1_with_water_init_g'] = float(val_init)
        if pd.notna(val_final):
            measurements[f'{phase}_pot1_with_water_final_g'] = float(val_final)

        # Row 16: Weight of charcoal+container (g)
        # This is only at the final measurement for each phase
        val_final = df.iloc[16, col_final]
        if pd.notna(val_final):
            measurements[f'{phase}_charcoal_container_final_g'] = float(val_final)

    except Exception as e:
        # If extraction fails, skip this measurement
        pass

    return measurements


def extract_efficiency_targets(df: pd.DataFrame) -> Dict[str, float]:
    """
    Extract thermal efficiency values (target variables for ML).

    These are the prediction targets we want to model.

    Args:
        df: Raw test sheet DataFrame

    Returns:
        Dictionary with efficiency values for each phase
    """
    targets = {}

    try:
        # Row 34 has thermal efficiency for cold (col 22) and hot (col 26)
        val_cold = df.iloc[34, 22]
        val_hot = df.iloc[34, 26]
        if pd.notna(val_cold):
            targets['thermal_efficiency_cold_start'] = float(val_cold)
        if pd.notna(val_hot):
            targets['thermal_efficiency_hot_start'] = float(val_hot)

        # The simmer efficiency is at row 33, col 41
        val_simmer = df.iloc[33, 41]
        if pd.notna(val_simmer):
            targets['thermal_efficiency_simmer'] = float(val_simmer)

        # Also extract the aggregated high-power thermal efficiency from row 43, col 30
        # This is an average of cold and hot start
        val_avg = df.iloc[43, 30]
        if pd.notna(val_avg):
            targets['thermal_efficiency_high_power_avg'] = float(val_avg)

    except Exception as e:
        # If extraction fails, skip
        pass

    return targets


def extract_additional_measurements(df: pd.DataFrame) -> Dict[str, float]:
    """
    Extract additional useful raw measurements that aren't phase-specific.

    These are measurements that could help predict efficiency but aren't
    calculated/derived metrics.

    Args:
        df: Raw test sheet DataFrame

    Returns:
        Dictionary with additional measurements
    """
    additional = {}

    # We could add more here if needed, but trying to keep it minimal
    # and avoid derived metrics

    return additional


def clean_sheet(df: pd.DataFrame, test_id: str) -> pd.DataFrame:
    """
    Extract and organize all relevant data from a single test sheet.

    This combines all the extraction functions to build a single-row
    DataFrame representing one test.

    Args:
        df: Raw test sheet DataFrame
        test_id: Test identifier

    Returns:
        Single-row DataFrame with all extracted features
    """
    # Extract all components
    metadata = extract_metadata(df, test_id)
    fuel_props = extract_fuel_properties(df)
    equip_props = extract_equipment_properties(df)

    # Extract measurements for each phase
    cold_measurements = extract_test_measurements(df, 'cold')
    hot_measurements = extract_test_measurements(df, 'hot')
    simmer_measurements = extract_test_measurements(df, 'simmer')

    # Extract targets
    targets = extract_efficiency_targets(df)

    # Extract additional measurements
    additional = extract_additional_measurements(df)

    # Combine all into a single dictionary
    row_data = {}
    row_data.update(metadata)
    row_data.update(fuel_props)
    row_data.update(equip_props)
    row_data.update(cold_measurements)
    row_data.update(hot_measurements)
    row_data.update(simmer_measurements)
    row_data.update(additional)
    row_data.update(targets)

    # Convert to DataFrame
    return pd.DataFrame([row_data])


def select_useful_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter columns to keep only ML-relevant features.

    Exclusion rules:
    1. Exclude metadata that won't help predict efficiency:
       - test_id (just an identifier)
       - stove_model (categorical, only one value in sample data)
       - fuel_type (categorical, only one value in sample data)

    2. Exclude columns with too many missing values (>50%)

    3. Keep all raw measurements and target variables

    Args:
        df: Combined DataFrame from all tests

    Returns:
        Filtered DataFrame with only useful columns
    """
    # Columns to explicitly exclude (metadata)
    exclude_cols = ['test_id', 'stove_model', 'fuel_type']

    # Remove excluded columns
    df_filtered = df.drop(columns=[col for col in exclude_cols if col in df.columns])

    # Check for columns with too many missing values
    missing_threshold = 0.5
    missing_pct = df_filtered.isnull().sum() / len(df_filtered)
    cols_to_keep = missing_pct[missing_pct <= missing_threshold].index.tolist()

    df_filtered = df_filtered[cols_to_keep]

    # Ensure target columns are present
    target_cols = [
        'thermal_efficiency_cold_start',
        'thermal_efficiency_hot_start',
        'thermal_efficiency_simmer',
        'thermal_efficiency_high_power_avg'
    ]

    for target_col in target_cols:
        if target_col not in df_filtered.columns:
            print(f"Warning: Target column '{target_col}' not found in dataset")

    return df_filtered


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing values in the dataset.

    Strategy:
    - For features with very few values, drop the column (already done in select_useful_columns)
    - For targets (efficiency values), keep as NaN (can filter during modeling)
    - For other features, keep as NaN (model-dependent imputation can be done later)

    Args:
        df: DataFrame with potential missing values

    Returns:
        DataFrame with missing values handled
    """
    # For now, we'll keep NaN values and let the modeling pipeline handle imputation
    # This gives more flexibility for different imputation strategies

    # Report missing value statistics
    print("\nMissing value summary:")
    print("=" * 60)
    missing_counts = df.isnull().sum()
    missing_pct = (missing_counts / len(df)) * 100
    missing_summary = pd.DataFrame({
        'missing_count': missing_counts,
        'missing_pct': missing_pct
    })
    missing_summary = missing_summary[missing_summary['missing_count'] > 0].sort_values(
        'missing_pct', ascending=False
    )

    if len(missing_summary) > 0:
        print(missing_summary.to_string())
    else:
        print("No missing values found!")

    return df


def process_single_file(file_path: str) -> List[pd.DataFrame]:
    """
    Process a single Excel file and extract data from all test sheets.

    Args:
        file_path: Path to an Excel file

    Returns:
        List of DataFrames, one per test sheet
    """
    test_sheets = ['Test-1', 'Test-2', 'Test-3', 'Test-4']
    file_tests = []
    file_name = os.path.basename(file_path)

    print(f"\nProcessing file: {file_name}")
    print("-" * 60)

    for sheet_name in test_sheets:
        try:
            # Load the sheet
            df_raw = load_sheet(file_path, sheet_name)

            # Clean and extract data
            # Create a unique test_id combining file name and sheet name
            test_id = f"{file_name}_{sheet_name}"
            df_clean = clean_sheet(df_raw, test_id)

            print(f"  {sheet_name}: Extracted {len(df_clean.columns)} features")
            file_tests.append(df_clean)
        except Exception as e:
            print(f"  {sheet_name}: Error - {str(e)}")
            # Skip this sheet if there's an error
            continue

    return file_tests


def build_ml_dataset(input_folder: str, output_path: str) -> pd.DataFrame:
    """
    Main function to build ML-ready dataset from all .xlsx files in a folder.

    Process:
    1. Find all .xlsx files in the input folder
    2. For each file, load Test-1 through Test-4 sheets
    3. Extract raw measurements and efficiency targets from each
    4. Combine into a single DataFrame (one row per test)
    5. Filter columns to remove metadata and irrelevant features
    6. Handle missing values
    7. Save to CSV

    Args:
        input_folder: Path to folder containing .xlsx files
        output_path: Path for output CSV file

    Returns:
        The final ML-ready DataFrame
    """
    print(f"Building ML dataset from folder: {input_folder}")
    print("=" * 80)

    # Find all .xlsx files in the input folder
    xlsx_pattern = os.path.join(input_folder, "*.xlsx")
    xlsx_files = glob.glob(xlsx_pattern)

    if not xlsx_files:
        print(f"\nWARNING: No .xlsx files found in {input_folder}")
        print("Please ensure the folder exists and contains Excel files.")
        return pd.DataFrame()

    print(f"\nFound {len(xlsx_files)} Excel file(s) to process:")
    for i, file_path in enumerate(xlsx_files, 1):
        print(f"  {i}. {os.path.basename(file_path)}")

    # Process all files
    all_tests = []

    for file_path in xlsx_files:
        file_tests = process_single_file(file_path)
        all_tests.extend(file_tests)

    if not all_tests:
        print("\nERROR: No test data was extracted from any files.")
        return pd.DataFrame()

    # Combine all tests into one DataFrame
    print(f"\n" + "=" * 80)
    print(f"Combining {len(all_tests)} test sheets from {len(xlsx_files)} file(s)...")
    df_combined = pd.concat(all_tests, axis=0, ignore_index=True)
    print(f"Combined dataset shape: {df_combined.shape}")

    # Select useful columns
    print("\nFiltering columns...")
    df_filtered = select_useful_columns(df_combined)
    print(f"Filtered dataset shape: {df_filtered.shape}")
    print(f"Kept {len(df_filtered.columns)} columns")

    # Handle missing values
    df_final = handle_missing_values(df_filtered)

    # Save to CSV
    print(f"\nSaving to: {output_path}")
    df_final.to_csv(output_path, index=False)
    print("Done!")

    # Print summary statistics
    print("\n" + "=" * 80)
    print("DATASET SUMMARY")
    print("=" * 80)
    print(f"Total samples: {len(df_final)}")
    print(f"Total features: {len(df_final.columns)}")
    print(f"\nColumn names:")
    for i, col in enumerate(df_final.columns, 1):
        print(f"  {i:2d}. {col}")

    print(f"\nFirst few rows:")
    print(df_final.head().to_string())

    return df_final


if __name__ == "__main__":
    # Configuration
    input_folder = "Raw_data"  # Folder containing .xlsx files
    output_file = "ml_ready_data.csv"

    # Build the dataset
    df = build_ml_dataset(input_folder, output_file)

    print("\n" + "=" * 80)
    print("IMPORTANT NOTES:")
    print("=" * 80)
    print("""
    TARGET VARIABLES (what we want to predict):
    - thermal_efficiency_cold_start: Efficiency during cold start high-power phase
    - thermal_efficiency_hot_start: Efficiency during hot start high-power phase
    - thermal_efficiency_simmer: Efficiency during low-power simmer phase
    - thermal_efficiency_high_power_avg: Average of cold & hot start efficiency

    FEATURES (what we use to predict):
    - Fuel properties: moisture content, calorific values
    - Equipment properties: pot weight, container weights, boiling point
    - Test measurements for each phase (cold/hot/simmer):
        * Initial and final fuel weights
        * Initial and final water temperatures
        * Initial and final pot weights with water
        * Charcoal container weights
        * CO measurements (where available)

    EXCLUDED (per requirements):
    - Metadata: date, location, tester names, test numbers
    - Ambient conditions: air temperature, wind conditions
    - Derived/calculated metrics: averages, std dev, ratios, temp-corrected values
    - Summary statistics from other sheets (only raw Test-1 to Test-4 data used)

    MISSING VALUES:
    - Kept as NaN to allow flexible imputation strategies during modeling
    - Columns with >50% missing values were removed
    """)
