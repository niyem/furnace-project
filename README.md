# Furnace Efficiency ML Pipeline

A comprehensive machine learning pipeline for analyzing and predicting furnace thermal efficiency based on laboratory-collected performance data.

## Table of Contents

- [Overview](#overview)
- [Scientific Motivation](#scientific-motivation)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Data Description](#data-description)
- [ML Pipeline](#ml-pipeline)
- [Configuration](#configuration)
- [Results](#results)
- [Adding New Data](#adding-new-data)
- [Future Work](#future-work)
- [License](#license)

---

## Overview

This project applies machine learning techniques to understand and predict furnace thermal efficiency from laboratory test data. The pipeline includes:

1. **Data preprocessing** - Cleaning, imputation, and feature scaling
2. **Dimensionality reduction** - PCA for feature compression
3. **Unsupervised clustering** - Identifying furnace performance groups
4. **Supervised regression** - Predicting thermal efficiency with multiple models
5. **Visualization** - Publication-quality plots and analysis

The project is designed for researchers, engineers, and data scientists working on cookstove performance analysis and optimization.

---

## Scientific Motivation

### Problem Statement

Cookstoves and furnaces are critical for energy access in developing regions, but their efficiency varies significantly based on fuel properties, design parameters, and operational conditions. Understanding these relationships is essential for:

- **Energy efficiency optimization** - Reducing fuel consumption
- **Emission reduction** - Lower CO₂ and particulate matter
- **Cost reduction** - Better stove design and fuel selection
- **Performance prediction** - Estimating efficiency for new designs

### Research Questions

1. **Clustering**: Can we identify distinct performance groups among furnaces based on their operational characteristics?
2. **Regression**: What features most strongly predict thermal efficiency?
3. **Model comparison**: Which machine learning model best captures the efficiency relationship?

---

## Project Structure

```
furnace-project/
├── README.md                   # This file
├── LICENSE                     # Project license
├── requirements.txt            # Python dependencies
├── config.yaml                 # Configuration file
│
├── Raw_data/                   # Raw Excel data (gitignored)
│   └── *.xlsx                  # Original test data files
│
├── ml_ready_data.csv           # Processed CSV data
├── ML_DATA_DOCUMENTATION.md    # Data dictionary
│
├── parse_ml_data.py            # Data extraction from Raw_data/
│
├── config.py                   # Configuration loader
├── utils.py                    # Logging and utilities
├── data_loader.py              # Data loading module
├── preprocess.py               # Preprocessing pipeline
├── dim_reduce.py               # Dimensionality reduction (PCA, UMAP, Autoencoder)
├── cluster.py                  # Clustering algorithms (K-Means, GMM, DBSCAN)
├── regression.py               # Multi-model regression
├── visualizations.py           # Visualization functions
├── run_pipeline.py             # Main pipeline orchestrator
│
├── figures/                    # Generated visualizations
│   ├── pca_variance_explained.png
│   ├── clustering_pca.png
│   ├── clustering_tsne.png
│   ├── clustering_umap.png
│   ├── cluster_metrics.png
│   ├── cluster_sizes.png
│   ├── parity_*.png
│   ├── residuals_*.png
│   ├── feature_importance_*.png
│   └── model_comparison_*.png
│
└── outputs/                    # Reports and saved models
    ├── reports/
    │   ├── cluster_summary.json
    │   ├── regression_results.json
    │   └── predictions_*.csv
    └── models/                 # Saved model files
```

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd furnace-project
```

### Step 2: Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Required Packages

- **Core**: `numpy`, `pandas`, `scipy`
- **ML**: `scikit-learn`, `xgboost`, `lightgbm`
- **Visualization**: `matplotlib`, `seaborn`, `umap-learn`
- **Config**: `pyyaml`, `openpyxl`

---

## Usage

### Quick Start

Run the complete pipeline with default settings:

```bash
python run_pipeline.py
```

### Custom Configuration

Specify a custom configuration file:

```bash
python run_pipeline.py --config custom_config.yaml
```

### Step-by-Step Execution

You can also run individual pipeline steps:

```python
from config import Config
from data_loader import load_data
from preprocess import basic_clean

# Load config
cfg = Config('config.yaml')

# Load data
df = load_data(cfg.get('data', 'path'))

# Preprocess
X, y = basic_clean(df, cfg.get('preprocess'), cfg.get('targets'))

# ... continue with clustering, regression, etc.
```

---

## Data Description

### Source

The data comes from controlled laboratory tests of cooking stoves measuring thermal efficiency under different operating conditions:

- **Cold start** - Stove starting from ambient temperature
- **Hot start** - Stove already warmed up
- **Simmer** - Low-power maintenance phase

### Processed Data

`ml_ready_data.csv` contains 33 features derived from raw measurements:

- **Fuel properties**: moisture content, calorific values
- **Operational metrics**: burn rate, firepower, water temperature changes
- **Efficiency metrics**: thermal efficiency (cold, hot, simmer, average)

See `ML_DATA_DOCUMENTATION.md` for complete variable descriptions.

### Target Variables

The pipeline predicts thermal efficiency:

- `thermal_efficiency_cold_start`
- `thermal_efficiency_hot_start`
- `thermal_efficiency_simmer`
- **`average_efficiency`** ← **Primary target** (mean of the three above)

---

## ML Pipeline

### 1. Data Preprocessing

**Module**: `preprocess.py`

- Missing value filtering (columns >60% missing removed)
- Missing value imputation (median strategy)
- Feature scaling (MinMax or Standard scaling)
- Variance-based feature selection
- Duplicate column handling

### 2. Dimensionality Reduction

**Module**: `dim_reduce.py`

- **PCA** (Principal Component Analysis) - Retains 95% variance
- Optional: **UMAP** for non-linear reduction
- Optional: **Autoencoder** for learned embeddings

### 3. Clustering

**Module**: `cluster.py`

**Algorithms**:
- K-Means (with automatic K selection via silhouette score)
- Gaussian Mixture Models (BIC-based selection)
- DBSCAN (density-based clustering)

**Evaluation Metrics**:
- Silhouette score (higher is better, range [-1, 1])
- Calinski-Harabasz score (higher is better)
- Davies-Bouldin score (lower is better)

**Visualizations**:
- PCA scatter plots with cluster colors
- t-SNE projections
- UMAP projections
- Cluster size distributions
- Metric comparisons

### 4. Regression

**Module**: `regression.py`

**Models** (all trained and compared):
1. **Linear Regression** - Baseline model
2. **Random Forest** - Ensemble, non-linear
3. **Gradient Boosting** - Sequential ensemble
4. **XGBoost** - Advanced gradient boosting

**Train/Val/Test Split**: 70% / 10% / 20%

**Performance Metrics**:
- R² (coefficient of determination)
- MAE (Mean Absolute Error)
- MSE (Mean Squared Error)
- RMSE (Root Mean Squared Error)

**Outputs**:
- Model comparison plots
- Parity plots (predicted vs. true)
- Residual analysis
- Feature importance rankings
- Prediction CSVs

---

## Configuration

Edit `config.yaml` to customize the pipeline:

### Data Settings

```yaml
data:
  path: 'ml_ready_data.csv'
  sheet_name: 'Sheet1'  # For Excel files
  index_col: null
```

### Preprocessing

```yaml
preprocess:
  drop_na_threshold_col: 0.6  # Keep columns with ≥60% non-null
  drop_na_threshold_row: 0.6  # Keep rows with ≥60% non-null
  impute_strategy: median     # mean | median | most_frequent
  scale: minmax               # standard | minmax
  remove_near_constant: true
  variance_threshold: 0.0
```

### Clustering

```yaml
clustering:
  algorithm: kmeans           # kmeans | gmm | dbscan
  kmeans_k_range: [2, 8]     # Search range for K
  selection_metric: silhouette
```

### Regression

```yaml
regression:
  enabled: true
  models:
    - linear
    - random_forest
    - xgboost
    - gradient_boost
  test_size: 0.2
  validation_size: 0.1
  metrics: [r2, mae, mse, rmse]
```

### Paths

```yaml
paths:
  outputs: 'outputs'
  figures: 'figures'
  models: 'outputs/models'
  reports: 'outputs/reports'
```

---

## Results

After running the pipeline, results are saved to:

### Visualizations (`figures/`)

- **PCA variance explained** - Scree plot and cumulative variance
- **Clustering visualizations** - PCA, t-SNE, UMAP projections with cluster colors
- **Cluster metrics** - Bar charts of evaluation metrics
- **Cluster sizes** - Distribution of samples per cluster
- **Parity plots** - Predicted vs. true values for each model and target
- **Residual plots** - Histogram and scatter of residuals
- **Feature importance** - Top features for tree-based models
- **Model comparison** - Bar charts comparing model performance

### Reports (`outputs/reports/`)

- `cluster_summary.json` - Clustering metrics and cluster sizes
- `regression_results.json` - All model performances across all targets
- `predictions_*.csv` - Predicted vs. true values for each target/model

### Example Output

```
REGRESSION RESULTS SUMMARY
================================================================================

Model: LINEAR
----------------------------------------
  average_efficiency: R2=0.8523, MAE=0.0234, RMSE=0.0312
  thermal_efficiency_cold_start: R2=0.8401, MAE=0.0251, RMSE=0.0328

Model: RANDOM_FOREST
----------------------------------------
  average_efficiency: R2=0.9123, MAE=0.0156, RMSE=0.0201
  thermal_efficiency_cold_start: R2=0.9034, MAE=0.0178, RMSE=0.0223

Model: XGBOOST
----------------------------------------
  average_efficiency: R2=0.9245, MAE=0.0142, RMSE=0.0185
  thermal_efficiency_cold_start: R2=0.9167, MAE=0.0159, RMSE=0.0203
```

---

## Adding New Data

### Option 1: Add Excel Files to `Raw_data/`

1. Place new `.xlsx` files in `Raw_data/` directory
2. Run the data parser:
   ```bash
   python parse_ml_data.py
   ```
3. This regenerates `ml_ready_data.csv`
4. Run the pipeline as usual:
   ```bash
   python run_pipeline.py
   ```

### Option 2: Use Existing CSV

1. Ensure your CSV has the required columns (see `ML_DATA_DOCUMENTATION.md`)
2. Update `config.yaml`:
   ```yaml
   data:
     path: 'your_data.csv'
   ```
3. Run the pipeline

---

## Future Work

### Model Enhancements

- **Hyperparameter tuning** - Grid search or Bayesian optimization
- **Deep learning models** - Neural networks for efficiency prediction
- **Ensemble methods** - Stacking or blending multiple models
- **Time series analysis** - If temporal data becomes available

### Feature Engineering

- **Interaction terms** - Multiplicative relationships between features
- **Polynomial features** - Non-linear transformations
- **Domain-specific features** - Physics-based derived variables

### Analysis Extensions

- **Sensitivity analysis** - Which features impact efficiency most?
- **Uncertainty quantification** - Prediction confidence intervals
- **Causal inference** - Understanding cause-effect relationships
- **Transfer learning** - Applying models to different stove types

### Deployment

- **Web interface** - Interactive dashboard for predictions
- **API service** - RESTful API for model serving
- **Mobile app** - Field data collection and prediction
- **Real-time monitoring** - IoT integration for live efficiency tracking

---

## License

This project is licensed under the MIT License. See `LICENSE` for details.

---

## Citation

If you use this code or data in your research, please cite:

```bibtex
@misc{furnace_efficiency_ml,
  title={Machine Learning Pipeline for Furnace Efficiency Prediction},
  author={[Your Name/Organization]},
  year={2025},
  url={https://github.com/[your-repo]}
}
```

---

## Contact

For questions, issues, or contributions:

- **Issues**: [GitHub Issues](https://github.com/[your-repo]/issues)
- **Email**: [your-email@domain.com]

---

**Happy modeling! 🔥**
