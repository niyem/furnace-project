# Code Review: Excel Parser for sample_data.xlsx

## Executive Summary

The code is **well-structured and mostly correct**, but has several issues that would prevent it from working properly with the actual `sample_data.xlsx` file. The main problems are:

1. ❌ **Critical**: File extension mismatch (.xls vs .xlsx)
2. ❌ **Critical**: Metadata extraction has incorrect row indices
3. ⚠️ **Major**: Hardcoded cell references are fragile
4. ⚠️ **Major**: Silent error handling hides problems
5. ⚠️ **Minor**: Some extracted values may be calculated/derived rather than raw

## Detailed Analysis

### 1. File Extension Mismatch ❌

**Issue**: Code references both `.xls` and `.xlsx` inconsistently:
- Docstring says "Parse sample_data.xlsx"
- Question asks about "sample_data.xls"
- Actual file is `sample_data.xlsx`

**Impact**: While `pd.read_excel()` handles both formats, this confusion could cause issues if the wrong file is provided.

**Recommendation**:
```python
# Add validation
if not file_path.endswith(('.xls', '.xlsx')):
    raise ValueError(f"Expected Excel file, got: {file_path}")
```

---

### 2. Incorrect Metadata Extraction ❌

**Issue**: The metadata extraction has wrong row indices:

```python
# Current code (INCORRECT):
metadata['stove_model'] = df.iloc[8, 3]  # Actually extracts Location: "Lomé-Togo"
metadata['fuel_type'] = df.iloc[9, 3]    # Correct: "Charcoal"
```

**Actual Excel structure**:
- Row 8, Col 3 = Location ("Lomé-Togo")
- Row 9, Col 3 = Stove type/model ("ASUTO")
- Row 10, Col 3 = Type of fuel ("Charcoal")

**Verified values**:
```
Row 8: Location = Lomé-Togo
Row 9: Stove type/model = ASUTO
Row 10: Type of fuel = Charcoal
```

**Fix**:
```python
metadata['stove_model'] = df.iloc[9, 3]   # Row 9, not 8
metadata['fuel_type'] = df.iloc[10, 3]    # Row 10, not 9
```

---

### 3. Hardcoded Cell References ⚠️

**Issue**: The code uses many hardcoded row/column indices like:
```python
fuel_props['fuel_moisture_content'] = float(df.iloc[17, 4])
equip_props['pot1_dry_weight_g'] = float(df.iloc[14, 13])
```

**Why it's fragile**:
- If Excel template changes even slightly, code breaks completely
- No validation that we're reading the expected cell
- Difficult to maintain and debug

**Better approach**:
```python
def find_cell_by_label(df, label, search_col=1, value_col=3):
    """Find a value by searching for its row label."""
    for idx, val in enumerate(df.iloc[:, search_col]):
        if val and label.lower() in str(val).lower():
            return df.iloc[idx, value_col]
    return None

# Usage:
fuel_moisture = find_cell_by_label(df, "Fuel moisture content", search_col=1, value_col=4)
```

---

### 4. Silent Error Handling ⚠️

**Issue**: All extraction functions use bare `except` with `pass`:

```python
try:
    metadata['stove_model'] = df.iloc[8, 3]
    metadata['fuel_type'] = df.iloc[9, 3]
except:
    pass  # Silently fails - you'll never know there was a problem!
```

**Problems**:
- Hides bugs (like the incorrect row index above)
- Makes debugging very difficult
- Data quality issues go unnoticed

**Better approach**:
```python
import logging

try:
    metadata['stove_model'] = df.iloc[9, 3]
    metadata['fuel_type'] = df.iloc[10, 3]
except Exception as e:
    logging.warning(f"Failed to extract metadata from {test_id}: {e}")
    # Or raise if critical
```

---

### 5. Verification of Key Extractions ✅

I verified the main data extraction points against the actual Excel file:

| Data Point | Code | Actual Value | Status |
|------------|------|--------------|--------|
| Fuel moisture | `df.iloc[17, 4]` | 0.08752 | ✅ Correct |
| Gross calorific | `df.iloc[18, 4]` | 31000 | ✅ Correct |
| Pot 1 weight | `df.iloc[14, 13]` | 814 | ✅ Correct |
| Cold fuel init | `df.iloc[6, 22]` | 590 | ✅ Correct |
| Cold fuel final | `df.iloc[6, 26]` | 332 | ✅ Correct |
| Hot fuel init | `df.iloc[6, 30]` | 764 | ✅ Correct |
| Hot fuel final | `df.iloc[6, 34]` | 498 | ✅ Correct |
| Simmer fuel init | `df.iloc[6, 37]` | 498 | ✅ Correct |
| Simmer fuel final | `df.iloc[6, 41]` | 274 | ✅ Correct |
| Cold efficiency | `df.iloc[34, 22]` | 0.2116 | ✅ Correct |
| Hot efficiency | `df.iloc[34, 26]` | 0.2139 | ✅ Correct |
| Simmer efficiency | `df.iloc[33, 41]` | 0.5427 | ✅ Correct |
| Avg high power | `df.iloc[43, 30]` | 0.2128 | ✅ Correct |

**Good news**: Most data extraction is correct! ✅

---

### 6. Potential Derived Metrics Issue ⚠️

**Issue**: Some extracted values might be calculated rather than raw:

```python
# Row 43, col 30 - "High Power Thermal Efficiency"
targets['thermal_efficiency_high_power_avg'] = float(val_avg)
```

This is marked as an average of cold and hot start, which makes it a **derived metric**. The docstring says to exclude "Derived/calculated metrics: averages, std dev, ratios".

**Recommendation**: Decide if this is a legitimate target variable or should be excluded per the stated requirements.

---

### 7. Code Structure ✅

**Strengths**:
- ✅ Well-organized with clear function separation
- ✅ Good docstrings explaining each function's purpose
- ✅ Logical flow from extraction → cleaning → combining
- ✅ Reasonable missing value strategy
- ✅ Good use of type hints

**Suggestions**:
- Add input validation (file exists, sheets exist)
- Add more detailed logging
- Consider making cell references configurable (config file or constants)

---

### 8. Testing Recommendation 🧪

**Critical**: Run the parser and validate output:

```bash
python excel_parser.py
```

Then verify:
1. Are all 4 tests extracted?
2. Do values match manual inspection of Excel?
3. Are target variables present and correct?
4. How many features are kept after filtering?

---

## Summary of Required Fixes

### Must Fix (Critical):
1. Fix metadata row indices:
   - `stove_model`: row 8 → row 9
   - `fuel_type`: row 9 → row 10

### Should Fix (Major):
2. Improve error handling - at minimum log warnings
3. Add validation that expected sheets exist
4. Consider making cell references more robust

### Nice to Have:
5. Add unit tests for extraction functions
6. Make cell references configurable
7. Add progress indicators for processing
8. Validate extracted data ranges (e.g., efficiency should be 0-100%)

---

## Overall Assessment

**Rating**: ⭐⭐⭐ (3/5)

**Pros**:
- Most cell references are correct
- Clean, readable code structure
- Thoughtful approach to feature selection
- Good documentation

**Cons**:
- Critical bug in metadata extraction
- Fragile hardcoded cell references
- Poor error handling
- No validation or testing

**Recommendation**:
✅ **Fix the metadata bug and improve error handling**, then the code should work adequately for the current Excel format. For production use, consider making it more robust with dynamic cell lookups and better validation.

---

## Quick Test

Here's a quick test you can run to validate the parser:

```python
# Test the parser
df = build_ml_dataset('sample_data.xlsx', 'ml_ready_data.csv')

# Verify key values from Test-1
assert df.loc[0, 'fuel_moisture_content'] == 0.08752, "Fuel moisture mismatch"
assert df.loc[0, 'cold_fuel_weight_init_g'] == 590, "Cold fuel init mismatch"
assert abs(df.loc[0, 'thermal_efficiency_cold_start'] - 0.2116) < 0.001, "Cold eff mismatch"

print("✅ All validations passed!")
```
