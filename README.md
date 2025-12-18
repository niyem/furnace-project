# Furnace Efficiency ML Pipeline

A comprehensive machine learning system for analyzing and predicting furnace/cookstove thermal efficiency from laboratory-collected performance data. This project applies data science techniques to understand how operational parameters (firepower, fuel moisture, boil time, etc.) affect efficiency.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red.svg)](https://pytorch.org/)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Creating a Virtual Environment](#creating-a-virtual-environment)
  - [Activating the Virtual Environment](#activating-the-virtual-environment)
  - [Installing Dependencies](#installing-dependencies)
- [Usage](#usage)
  - [Running the Full Pipeline](#running-the-full-pipeline)
  - [Running Individual Components](#running-individual-components)
- [Pipeline Workflow](#pipeline-workflow)
- [Data Description](#data-description)
- [Model Architecture](#model-architecture)
- [Output Files](#output-files)
- [Configuration](#configuration)
- [License](#license)
- [Author](#author)

---

## Overview

This project provides an end-to-end machine learning pipeline for predicting thermal efficiency of furnaces and cookstoves. It combines:

- **Data Preprocessing**: Cleaning and standardization of raw laboratory data
- **Feature Engineering**: Creation of predictive features while preventing data leakage
- **Unsupervised Learning**: K-Means clustering to identify operational patterns
- **Deep Learning**: PyTorch neural network (FurnaceNet) for efficiency prediction
- **Visualization**: Publication-quality figures for analysis and reporting

---

## Features

- **Modular Architecture**: Separate modules for each pipeline stage
- **Publication-Quality Outputs**: 14+ high-resolution PNG figures (300 DPI)
- **Deep Learning**: PyTorch neural network with batch normalization and dropout
- **Clustering Analysis**: K-Means with PCA visualization
- **Comprehensive Metrics**: R², RMSE, MAE for model evaluation
- **Data Integrity**: Handles missing values, outliers, and data leakage prevention
- **Flexible Data Input**: Supports both Excel (.xlsx) and CSV formats
- **Efficiency Standardization**: Auto-converts decimals (0.25) to percentages (25%)

---

## Project Structure

```
furnace-project/
├── run_all.py                    # Main pipeline entry point (6-step process)
├── analyze_efficiencies.py       # Standalone efficiency statistics analysis
├── requirements.txt              # Python dependencies
├── LICENSE                       # MIT License
├── README.md                     # This file
│
├── src/                          # Source modules
│   ├── __init__.py               # Package initialization
│   ├── preprocess.py             # Data cleaning & preparation
│   ├── feature_builder.py        # Feature engineering & target creation
│   ├── clustering.py             # K-Means clustering (k=5)
│   ├── model_nn.py               # FurnaceNet neural network architecture
│   ├── trainer.py                # Model training with PyTorch
│   ├── evaluator.py              # Model performance metrics
│   └── visualizer.py             # Publication-quality visualizations
│
├── data/
│   ├── raw/                      # Raw input data
│   │   └── Final_Modified.xlsx   # Laboratory test data (~1,056 samples)
│   └── processed/                # Processed outputs
│       ├── cleaned_data.csv      # Output from preprocessing
│       └── model_ready_data.csv  # Output from feature engineering
│
└── outputs/
    ├── figures/                  # Generated visualizations (14+ figures)
    ├── models/                   # Trained model weights
    │   └── furnace_net.pth       # Saved PyTorch model
    └── efficiency_stats/         # Statistical analysis outputs
```

---

## Installation

### Prerequisites

- **Python 3.8 or higher** (Python 3.10+ recommended)
- **pip** (Python package installer)
- **Git** (for cloning the repository)

### Creating a Virtual Environment

A virtual environment isolates project dependencies from your system Python. Follow these steps:

#### On Linux/macOS:

```bash
# Navigate to the project directory
cd furnace-project

# Create a virtual environment named 'venv'
python3 -m venv venv
```

#### On Windows:

```bash
# Navigate to the project directory
cd furnace-project

# Create a virtual environment named 'venv'
python -m venv venv
```

### Activating the Virtual Environment

You must activate the virtual environment before installing dependencies or running the pipeline.

#### On Linux/macOS:

```bash
source venv/bin/activate
```

#### On Windows (Command Prompt):

```bash
venv\Scripts\activate.bat
```

#### On Windows (PowerShell):

```bash
venv\Scripts\Activate.ps1
```

After activation, you should see `(venv)` at the beginning of your terminal prompt:

```
(venv) user@machine:~/furnace-project$
```

### Installing Dependencies

With the virtual environment activated, install all required packages:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs the following key dependencies:

| Package | Version | Purpose |
|---------|---------|---------|
| numpy | >= 1.21.0 | Numerical computing |
| pandas | >= 1.5.0 | Data manipulation |
| scipy | >= 1.7.0 | Scientific computing |
| matplotlib | >= 3.7.0 | Visualization |
| seaborn | >= 0.12.0 | Statistical plots |
| scikit-learn | >= 1.3.0 | Machine learning |
| torch | >= 2.0.0 | Deep learning (PyTorch) |
| umap-learn | >= 0.5.0 | Dimensionality reduction |
| openpyxl | >= 3.0.0 | Excel file support |
| tqdm | >= 4.65.0 | Progress bars |
| pyyaml | >= 6.0 | Configuration files |

### Deactivating the Virtual Environment

When you're done working, deactivate the virtual environment:

```bash
deactivate
```

---

## Usage

### Running the Full Pipeline

Execute the complete 6-step pipeline with a single command:

```bash
# Make sure your virtual environment is activated
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate.bat  # Windows

# Run the full pipeline
python run_all.py
```

**Expected output:**

```
============================================================
        FURNACE EFFICIENCY ML PIPELINE
============================================================

[1/6] Preprocessing data...
      ✓ Cleaned data saved to data/processed/cleaned_data.csv

[2/6] Building features...
      ✓ Model-ready data saved to data/processed/model_ready_data.csv

[3/6] Running clustering analysis...
      ✓ Identified 5 clusters with PCA projection

[4/6] Training neural network...
      Epoch [100/600] - Loss: 0.0234
      Epoch [200/600] - Loss: 0.0156
      ...
      ✓ Model saved to outputs/models/furnace_net.pth

[5/6] Evaluating model...
      R² Score: 0.92
      RMSE: 3.45
      MAE: 2.67

[6/6] Generating visualizations...
      ✓ 14 figures saved to outputs/figures/

============================================================
        PIPELINE COMPLETED SUCCESSFULLY
============================================================
```

### Running Individual Components

You can also run specific parts of the pipeline independently:

#### Efficiency Analysis Only

```bash
python analyze_efficiencies.py
```

This generates statistical summaries and distribution plots for efficiency metrics.

#### Using Source Modules Directly

```python
from src.preprocess import clean_data
from src.feature_builder import build_features
from src.clustering import run_clustering
from src.trainer import train_model
from src.evaluator import evaluate_model
from src.visualizer import generate_all_figures

# Example: Run preprocessing only
df = clean_data('data/raw/Final_Modified.xlsx')
df.to_csv('data/processed/cleaned_data.csv', index=False)
```

---

## Pipeline Workflow

The pipeline executes 6 sequential steps:

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PIPELINE WORKFLOW                            │
└─────────────────────────────────────────────────────────────────────┘

[Step 1] PREPROCESSING
         │
         │  Input:  data/raw/Final_Modified.xlsx
         │  Output: data/processed/cleaned_data.csv
         │
         │  • Load Excel/CSV data
         │  • Handle missing values
         │  • Standardize efficiency to 0-100%
         │  • Rename columns for consistency
         ▼
[Step 2] FEATURE ENGINEERING
         │
         │  Output: data/processed/model_ready_data.csv
         │
         │  • Create target variable (Avg_ThermalEfficiency)
         │  • Select predictive features
         │  • Prevent data leakage
         ▼
[Step 3] CLUSTERING
         │
         │  • K-Means clustering (k=5)
         │  • PCA dimensionality reduction
         │  • Compute elbow statistics
         ▼
[Step 4] DEEP LEARNING
         │
         │  Output: outputs/models/furnace_net.pth
         │
         │  • Train FurnaceNet neural network
         │  • 600 epochs with Adam optimizer
         │  • Learning rate scheduling
         ▼
[Step 5] EVALUATION
         │
         │  • Compute R², RMSE, MAE metrics
         │  • Generate residual analysis
         ▼
[Step 6] VISUALIZATION
         │
         │  Output: outputs/figures/Fig*.png
         │
         │  • Generate 14+ publication-quality figures
         │  • Distribution plots, correlation heatmaps
         │  • Learning curves, cluster visualizations
         ▼
       COMPLETE
```

---

## Data Description

### Input Data

**File**: `data/raw/Final_Modified.xlsx`
- **Samples**: ~1,056 furnace/stove test records
- **Format**: Excel spreadsheet (.xlsx)

### Key Features

| Feature | Description |
|---------|-------------|
| FirepowerCold | Firepower during cold start phase (kW) |
| FirepowerHot | Firepower during hot start phase (kW) |
| FirepowerSimmer | Firepower during simmer phase (kW) |
| ThermalEffCold | Thermal efficiency - cold start (%) |
| ThermalEffHot | Thermal efficiency - hot start (%) |
| ThermalEffSimmer | Thermal efficiency - simmer phase (%) |
| FuelMoistWet | Fuel moisture content - wet basis (%) |
| FuelMoistAcc | Fuel moisture content - as received (%) |
| GrossCalDry | Gross calorific value - dry basis (MJ/kg) |
| TimeToBoilCold | Time to boil - cold start (minutes) |
| TimeToBoilHot | Time to boil - hot start (minutes) |
| BurningRateCold | Fuel burning rate - cold start (g/min) |
| BurningRateHot | Fuel burning rate - hot start (g/min) |

### Target Variable

```
Avg_ThermalEfficiency = (ThermalEffCold + ThermalEffHot + ThermalEffSimmer) / 3
```

---

## Model Architecture

### FurnaceNet Neural Network

```
┌─────────────────────────────────────────┐
│           INPUT LAYER                   │
│         (n_features)                    │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│        HIDDEN LAYER 1                   │
│   Linear(n_features, 128)               │
│   BatchNorm1d(128)                      │
│   ReLU                                  │
│   Dropout(0.2)                          │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│        HIDDEN LAYER 2                   │
│   Linear(128, 64)                       │
│   BatchNorm1d(64)                       │
│   ReLU                                  │
│   Dropout(0.2)                          │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│        HIDDEN LAYER 3                   │
│   Linear(64, 32)                        │
│   BatchNorm1d(32)                       │
│   ReLU                                  │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│          OUTPUT LAYER                   │
│   Linear(32, 1)                         │
│   (Thermal Efficiency Prediction)       │
└─────────────────────────────────────────┘
```

### Training Hyperparameters

| Parameter | Value |
|-----------|-------|
| Epochs | 600 |
| Learning Rate | 0.001 |
| Optimizer | Adam (weight_decay=1e-5) |
| Loss Function | MSE (Mean Squared Error) |
| LR Scheduler | ReduceLROnPlateau (factor=0.5, patience=20) |
| Train/Test Split | 80/20 |
| Dropout Rate | 0.2 |

---

## Output Files

### Generated Figures

| Figure | Description |
|--------|-------------|
| Fig1_Target_Dist.png | Target variable distribution |
| Fig2_Correlation.png | Feature correlation heatmap |
| Fig4_Actual_vs_Pred.png | Actual vs predicted scatter plot |
| Fig5_Residuals.png | Residual error distribution |
| Fig8_Phase_Comparison.png | Efficiency across operational phases |
| Fig10_Learning_Curve.png | Neural network training curves |
| Fig11_Elbow.png | Clustering elbow method |
| Fig12_PCA_Clusters.png | Cluster visualization in 2D PCA space |
| Fig13_Cluster_Efficiency.png | Efficiency distribution by cluster |
| Fig14_Cluster_Firepower.png | Firepower distribution by cluster |

### Model Outputs

| File | Description |
|------|-------------|
| `outputs/models/furnace_net.pth` | Trained PyTorch model weights |
| `outputs/efficiency_stats/efficiency_descriptive_stats.csv` | Statistical summary |

---

## Configuration

### Customizing Paths

Edit `run_all.py` to modify input/output paths:

```python
# Data paths
RAW_FILENAME = 'Final_Modified.xlsx'
RAW_DATA_PATH = 'data/raw/Final_Modified.xlsx'
PROCESSED_DATA_PATH = 'data/processed/cleaned_data.csv'
FINAL_DATA_PATH = 'data/processed/model_ready_data.csv'
MODEL_OUTPUT_DIR = 'outputs/models'
```

### Modifying Hyperparameters

Edit `src/trainer.py` for training configuration:

```python
# Training settings
EPOCHS = 600
LEARNING_RATE = 0.001
WEIGHT_DECAY = 1e-5
TRAIN_TEST_SPLIT = 0.2
```

Edit `src/clustering.py` for clustering settings:

```python
# Clustering settings
N_CLUSTERS = 5  # Based on physical stove types
```

---

## Troubleshooting

### Common Issues

**1. ModuleNotFoundError: No module named 'torch'**

Ensure you have activated the virtual environment and installed requirements:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

**2. FileNotFoundError: data/raw/Final_Modified.xlsx**

Ensure the raw data file exists in the correct location. The pipeline expects the Excel file at `data/raw/Final_Modified.xlsx`.

**3. CUDA/GPU Issues**

If you encounter CUDA errors, the model will automatically fall back to CPU. For explicit CPU usage:

```python
device = torch.device('cpu')
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Author

**Niyem M. Bawana**

- GitHub: [@niyem](https://github.com/niyem)

---

## Acknowledgments

- PyTorch team for the deep learning framework
- scikit-learn team for machine learning utilities
- The cookstove research community for domain expertise
