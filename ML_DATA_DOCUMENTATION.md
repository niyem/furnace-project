# ML-Ready Data Parsing Documentation

## Overview

This document explains the parsing logic, column selection rules, and assumptions made when converting `sample_data.xlsx` into the machine-learning-ready dataset `ml_ready_data.csv`.

## Script: `parse_ml_data.py`

The script reads Test-1 through Test-4 sheets from the Excel workbook and produces a single CSV file with 4 rows (one per test) and 33 features.

## Execution

```bash
python parse_ml_data.py
```

This generates `ml_ready_data.csv` in the same directory.

---

## Target Variables (What We Predict)

The dataset includes **4 efficiency metrics** as target variables:

1. **`thermal_efficiency_cold_start`** - Thermal efficiency during cold start high-power phase (~21%)
2. **`thermal_efficiency_hot_start`** - Thermal efficiency during hot start high-power phase (~21%)
3. **`thermal_efficiency_simmer`** - Thermal efficiency during low-power simmer phase (~54%)
4. **`thermal_efficiency_high_power_avg`** - Average of cold and hot start efficiencies (~21%)

### Data Sources for Targets:
- Located in Test sheets at specific cell positions
- **Cold/Hot efficiency**: Row 34, Columns 22 (cold) and 26 (hot)
- **Simmer efficiency**: Row 33, Column 41
- **High-power average**: Row 43, Column 30

---

## Feature Variables (Predictors)

### 1. Fuel Properties (5 features)
Raw physical properties of the charcoal fuel used:

| Feature | Description | Typical Value | Sheet Location |
|---------|-------------|---------------|----------------|
| `fuel_moisture_content` | Moisture content (wet basis) | 0.08752 (8.75%) | Row 17, Col 4 |
| `gross_calorific_value_kj_kg` | Gross calorific value of dry fuel | 31000 kJ/kg | Row 18, Col 4 |
| `net_calorific_value_kj_kg` | Net calorific value of dry fuel | 29800 kJ/kg | Row 19, Col 4 |
| `effective_calorific_value_kj_kg` | Effective value accounting for moisture | ~26970 kJ/kg | Row 21, Col 4 |
| `char_calorific_value_kj_kg` | Calorific value of char | 29800 kJ/kg | Row 22, Col 4 |

### 2. Equipment Properties (3 features)
Properties of the testing equipment:

| Feature | Description | Typical Value | Sheet Location |
|---------|-------------|---------------|----------------|
| `pot1_dry_weight_g` | Dry weight of Pot #1 | 814 g | Row 14, Col 13 |
| `char_container_weight_g` | Weight of container for char | 828 g | Row 18, Col 13 |
| `local_boiling_point_c` | Local boiling point of water | 99.5 °C | Row 19, Col 13 |

### 3. Test Measurements (24 features, 8 per phase)

For each of the three test phases (cold start, hot start, simmer), we extract:

| Feature Pattern | Description | Sheet Columns |
|----------------|-------------|---------------|
| `{phase}_fuel_weight_init_g` | Initial fuel weight | Cold: 22, Hot: 30, Simmer: 37 |
| `{phase}_fuel_weight_final_g` | Final fuel weight | Cold: 26, Hot: 34, Simmer: 41 |
| `{phase}_water_temp_pot1_init_c` | Initial water temperature | Cold: 22, Hot: 30, Simmer: 37 |
| `{phase}_water_temp_pot1_final_c` | Final water temperature | Cold: 26, Hot: 34, Simmer: 41 |
| `{phase}_pot1_with_water_init_g` | Initial pot+water weight | Cold: 22, Hot: 30, Simmer: 37 |
| `{phase}_pot1_with_water_final_g` | Final pot+water weight | Cold: 26, Hot: 34, Simmer: 41 |
| `{phase}_charcoal_container_final_g` | Final charcoal+container weight | Cold: 26, Hot: 34, Simmer: 41 |

**Sheet Row Locations:**
- Fuel weight: Row 6
- Water temperature: Row 7
- Pot with water: Row 11
- Charcoal container: Row 16

**Column Layout:**
- **Cold Start**: Initial (col 22), Final (col 26)
- **Hot Start**: Initial (col 30), Final (col 34)
- **Simmer**: Initial (col 37), Final (col 41)

---

## Exclusion Rules

### What Was Excluded and Why

#### 1. **Metadata** (Not useful for prediction)
- `test_id` - Just an identifier
- `stove_model` - Categorical with only one value ("ASUTO")
- `fuel_type` - Categorical with only one value ("Charcoal")
- Date, location, tester names - Contextual information unlikely to affect stove physics

#### 2. **Ambient Conditions** (Per user requirements)
- `air_temperature` - Ambient air temperature (33°C)
- `wind_conditions` - Wind level indicator

#### 3. **Derived/Calculated Metrics** (Per user requirements)
Excluded all columns containing:
- Averages, means, standard deviations
- Ratios (e.g., turn-down ratio)
- Temperature-corrected values (e.g., temp-corrected time to boil, temp-corrected specific consumption)
- Burning rates, firepower, specific fuel consumption (calculated from raw measurements)
- All metrics from sheets other than Test-1 to Test-4 (Results, IWA Summary, etc.)

#### 4. **Time Measurements**
- Excluded timestamps as they're arbitrary relative to the test day
- If needed, could extract time deltas (duration) in future versions

#### 5. **Emissions Data**
- CO, CO2, PM measurements had many missing values (NaN)
- Only occasionally recorded in cold start phase
- Excluded due to >50% missingness threshold

#### 6. **Multi-Pot Measurements**
- Only Pot #1 was used in these tests
- Pot #2, #3, #4 measurements were all NaN
- Excluded due to 100% missingness

---

## Heuristics for Column Selection

### 1. **Detecting Derived Columns**
The script uses keyword matching to identify derived metrics:
- Column names or cell values containing: `average`, `avg`, `mean`, `std`, `standard deviation`, `cov`, `covariance`, `ratio`, `corrected`, `specific`, `rate`
- These are flagged as calculated metrics and excluded

### 2. **Missing Value Threshold**
- Columns with >50% missing values across the 4 tests are automatically dropped
- This threshold can be adjusted in `select_useful_columns()` function
- Current dataset has 0% missing values after filtering

### 3. **Raw Measurement Priority**
- Direct physical measurements are prioritized
- Initial and final states are kept (allows model to learn deltas if needed)
- Physical properties of fuel and equipment are retained

---

## Data Sheet Structure

### Test-1 to Test-4 Layout

Each Test sheet (77 rows × 43 columns) has the following structure:

```
Rows 0-3:   Headers and instructions
Rows 4-9:   Qualitative metadata (tester, date, location, stove, fuel)
Rows 10-22: Initial test conditions (fuel properties, equipment specs)
Rows 23-29: Notes sections
Rows 30-39: Calculated metrics (efficiency, burning rate, firepower, etc.)
Rows 40-49: IWA performance metrics
Rows 50-76: Additional notes and empty rows

Columns 0-19:  Left section (metadata, initial conditions)
Columns 20-29: Cold start measurements
Columns 30-36: Hot start measurements
Columns 37-42: Simmer measurements
```

### Why Other Sheets Were Ignored

- **Results**: Contains manually processed averages, std dev, COV
- **IWA Summary**: Summary statistics and derived tier ratings
- **Fuel Moisture, Calorific values, RRT data**: Support sheets with alternative calculations
- **General Information, Test Entry**: Metadata sheets
- **Lists, Catalog Import Data**: Reference data not specific to these tests

Only Test-1 through Test-4 contain the **raw experimental measurements** needed for ML.

---

## Handling Column Name Inconsistencies

### Observations:
- All 4 test sheets have identical structure (77×43)
- Column positions are consistent across sheets
- Same test protocol was followed for all 4 replicates

### Strategy:
- Use fixed row/column indices for extraction
- Column names in output CSV are standardized descriptive names
- If test structure changes, indices would need updating

---

## Missing Values Strategy

### Current Approach:
- Missing values are kept as NaN in the output CSV
- This allows flexibility for different imputation strategies during modeling
- Common strategies:
  - Median/mean imputation for fuel properties
  - Forward-fill or interpolation for sequential measurements
  - Drop samples with missing targets

### Why Not Impute in the Parser:
- Different ML models may benefit from different imputation methods
- Some models (tree-based) can handle NaN natively
- User may want to experiment with imputation as a hyperparameter

---

## Data Quality Notes

### Consistency:
- All 4 tests used the same fuel (moisture = 0.08752)
- Same pot (weight = 814 g)
- Same equipment setup
- Only test-specific measurements vary

### Variation Across Tests:
- Efficiency metrics vary by ~1-2% across replicates
- Initial water temperatures vary (29-31°C)
- Fuel amounts vary slightly (test preparation variation)

### Completeness:
- **No missing values** in the final 33-feature dataset
- All critical measurements successfully extracted
- 4 complete test replicates

---

## Example Usage

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

# Load the dataset
df = pd.read_csv('ml_ready_data.csv')

# Separate features and targets
target_cols = [
    'thermal_efficiency_cold_start',
    'thermal_efficiency_hot_start',
    'thermal_efficiency_simmer',
    'thermal_efficiency_high_power_avg'
]
X = df.drop(columns=target_cols)
y = df[target_cols]

# For single-target prediction (e.g., cold start efficiency)
y_cold = df['thermal_efficiency_cold_start']

# Example: Predict cold start efficiency
model = RandomForestRegressor(random_state=42)
# Note: With only 4 samples, consider LOOCV or expand dataset first
```

---

## Recommendations for Future Improvements

### 1. **Expand Dataset**
- Current dataset has only 4 samples - insufficient for robust ML
- Collect more test replicates
- Include tests with different:
  - Stove models
  - Fuel types
  - Fuel moisture levels
  - Ambient conditions

### 2. **Feature Engineering**
Potential derived features to add:
- Fuel consumed (initial - final weight)
- Water evaporated (initial - final pot weight)
- Temperature rise (final - initial water temp)
- Test duration (if timestamps extracted)
- Energy input (fuel consumed × calorific value)
- Energy output (water heated × specific heat × temp rise)

### 3. **Emissions Data**
- Standardize emissions measurement across all tests
- Include CO, CO2, PM as features if collected consistently

### 4. **Time-Series Features**
- If continuous measurements are available, extract:
  - Rate of temperature change
  - Rate of fuel consumption
  - Time to reach boiling

---

## Column Reference Guide

### Final Dataset Columns (33 total)

#### Fuel Properties (5)
1. fuel_moisture_content
2. gross_calorific_value_kj_kg
3. net_calorific_value_kj_kg
4. effective_calorific_value_kj_kg
5. char_calorific_value_kj_kg

#### Equipment (3)
6. pot1_dry_weight_g
7. char_container_weight_g
8. local_boiling_point_c

#### Cold Start (7)
9. cold_fuel_weight_init_g
10. cold_fuel_weight_final_g
11. cold_water_temp_pot1_init_c
12. cold_water_temp_pot1_final_c
13. cold_pot1_with_water_init_g
14. cold_pot1_with_water_final_g
15. cold_charcoal_container_final_g

#### Hot Start (7)
16. hot_fuel_weight_init_g
17. hot_fuel_weight_final_g
18. hot_water_temp_pot1_init_c
19. hot_water_temp_pot1_final_c
20. hot_pot1_with_water_init_g
21. hot_pot1_with_water_final_g
22. hot_charcoal_container_final_g

#### Simmer (7)
23. simmer_fuel_weight_init_g
24. simmer_fuel_weight_final_g
25. simmer_water_temp_pot1_init_c
26. simmer_water_temp_pot1_final_c
27. simmer_pot1_with_water_init_g
28. simmer_pot1_with_water_final_g
29. simmer_charcoal_container_final_g

#### Targets (4)
30. thermal_efficiency_cold_start
31. thermal_efficiency_hot_start
32. thermal_efficiency_simmer
33. thermal_efficiency_high_power_avg

---

## Contact & Support

For questions about this parsing logic or to report issues:
- Check the inline comments in `parse_ml_data.py`
- Review this documentation
- Verify Excel sheet structure hasn't changed

**Last Updated**: November 2024
