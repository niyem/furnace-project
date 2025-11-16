"""
Multi-model regression module for furnace efficiency prediction.

This module provides comprehensive regression analysis with multiple model types:
- Linear Regression (baseline)
- Random Forest Regressor
- Gradient Boosting Regressor
- XGBoost Regressor

Features:
- Train/validation/test split
- Multiple performance metrics (R², MAE, MSE, RMSE)
- Residual analysis
- Feature importance extraction
- Model comparison
- Automated visualization generation
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from utils import get_logger, save_json
import visualizations as viz

# Try to import XGBoost (optional but recommended)
try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

logger = get_logger()


def compute_average_efficiency(y: pd.DataFrame) -> pd.DataFrame:
    """
    Compute average efficiency from individual thermal efficiency columns.

    The average efficiency is calculated as the mean of:
    - thermal_efficiency_cold_start
    - thermal_efficiency_hot_start
    - thermal_efficiency_simmer

    Parameters
    ----------
    y : pd.DataFrame
        DataFrame containing the individual thermal efficiency columns.

    Returns
    -------
    pd.DataFrame
        DataFrame with added 'average_efficiency' column.
    """
    required_cols = [
        'thermal_efficiency_cold_start',
        'thermal_efficiency_hot_start',
        'thermal_efficiency_simmer'
    ]

    # Check which columns exist
    available_cols = [col for col in required_cols if col in y.columns]

    if len(available_cols) == 0:
        logger.warning("No thermal efficiency columns found. Cannot compute average_efficiency.")
        return y

    if len(available_cols) < 3:
        logger.warning(f"Only {len(available_cols)}/3 thermal efficiency columns found: {available_cols}")

    # Compute average efficiency
    y_new = y.copy()
    y_new['average_efficiency'] = y_new[available_cols].mean(axis=1)

    logger.info(f"Computed average_efficiency from {len(available_cols)} thermal efficiency columns")
    return y_new


def get_model(model_name: str, random_state: int = 42) -> Any:
    """
    Get a regression model instance by name.

    Parameters
    ----------
    model_name : str
        Name of the model ('linear', 'random_forest', 'gradient_boost', 'xgboost').
    random_state : int
        Random state for reproducibility.

    Returns
    -------
    Any
        Scikit-learn or XGBoost model instance.

    Raises
    ------
    ValueError
        If model_name is unknown or required package is not installed.
    """
    model_name = model_name.lower().strip()

    if model_name == 'linear':
        return LinearRegression()

    elif model_name == 'random_forest':
        return RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=-1
        )

    elif model_name == 'gradient_boost':
        return GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=random_state
        )

    elif model_name == 'xgboost':
        if not HAS_XGBOOST:
            raise ValueError("XGBoost not installed. Use 'pip install xgboost' or choose another model.")
        return xgb.XGBRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            min_child_weight=2,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=random_state,
            n_jobs=-1
        )

    else:
        raise ValueError(f"Unknown model name: '{model_name}'. "
                        f"Choose from: linear, random_forest, gradient_boost, xgboost")


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray, metrics: List[str]) -> Dict[str, float]:
    """
    Compute regression metrics.

    Parameters
    ----------
    y_true : np.ndarray
        True values.
    y_pred : np.ndarray
        Predicted values.
    metrics : List[str]
        List of metric names to compute ('r2', 'mae', 'mse', 'rmse').

    Returns
    -------
    Dict[str, float]
        Dictionary of computed metrics.
    """
    results = {}

    if 'r2' in metrics:
        results['r2'] = float(r2_score(y_true, y_pred))

    if 'mae' in metrics:
        results['mae'] = float(mean_absolute_error(y_true, y_pred))

    if 'mse' in metrics:
        results['mse'] = float(mean_squared_error(y_true, y_pred))

    if 'rmse' in metrics:
        results['rmse'] = float(np.sqrt(mean_squared_error(y_true, y_pred)))

    return results


def get_feature_importance(model: Any, feature_names: List[str]) -> Optional[np.ndarray]:
    """
    Extract feature importance from a trained model.

    Parameters
    ----------
    model : Any
        Trained model.
    feature_names : List[str]
        List of feature names.

    Returns
    -------
    Optional[np.ndarray]
        Feature importance scores, or None if not available.
    """
    # Tree-based models
    if hasattr(model, 'feature_importances_'):
        return model.feature_importances_

    # Linear models (use absolute coefficients as proxy)
    elif hasattr(model, 'coef_'):
        return np.abs(model.coef_)

    else:
        return None


def train_single_target(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    target_name: str,
    model_name: str,
    metrics: List[str],
    figures_dir: str = 'figures',
    random_state: int = 42
) -> Tuple[Any, Dict[str, float], pd.DataFrame]:
    """
    Train a single model for a single target variable.

    Parameters
    ----------
    X_train, X_val, X_test : pd.DataFrame
        Feature matrices for train, validation, and test sets.
    y_train, y_val, y_test : pd.Series
        Target vectors for train, validation, and test sets.
    target_name : str
        Name of the target variable.
    model_name : str
        Name of the model to train.
    metrics : List[str]
        List of metrics to compute.
    figures_dir : str
        Directory to save figures.
    random_state : int
        Random state for reproducibility.

    Returns
    -------
    Tuple[Any, Dict[str, float], pd.DataFrame]
        Trained model, test metrics, and predictions DataFrame.
    """
    logger.info(f"Training {model_name} for target '{target_name}'...")

    # Get model
    model = get_model(model_name, random_state=random_state)

    # Train model
    model.fit(X_train, y_train)

    # Predictions
    y_pred_test = model.predict(X_test)
    y_pred_val = model.predict(X_val)

    # Compute metrics on test set
    test_metrics = compute_metrics(y_test.values, y_pred_test, metrics)

    logger.info(f"  {model_name} | {target_name} | Test metrics: {test_metrics}")

    # Create visualizations
    viz.plot_parity(y_test.values, y_pred_test, target_name, model_name,
                   metrics=test_metrics, figures_dir=figures_dir)

    viz.plot_residuals(y_test.values, y_pred_test, target_name, model_name,
                      figures_dir=figures_dir)

    # Feature importance (if available)
    importance = get_feature_importance(model, X_train.columns.tolist())
    if importance is not None:
        viz.plot_feature_importance(
            importance, X_train.columns.tolist(), model_name, target_name,
            top_n=20, figures_dir=figures_dir
        )

    # Prepare predictions DataFrame
    predictions_df = pd.DataFrame({
        'y_true': y_test.values,
        'y_pred': y_pred_test
    })

    return model, test_metrics, predictions_df


def train_multi_target_multi_model(
    X: pd.DataFrame,
    y: pd.DataFrame,
    model_names: List[str],
    test_size: float = 0.2,
    validation_size: float = 0.1,
    random_state: int = 42,
    metrics: List[str] = ['r2', 'mae', 'mse', 'rmse'],
    figures_dir: str = 'figures',
    reports_dir: str = 'outputs/reports'
) -> Dict[str, Dict[str, Dict[str, float]]]:
    """
    Train multiple models for multiple target variables.

    Parameters
    ----------
    X : pd.DataFrame
        Feature matrix.
    y : pd.DataFrame
        Target matrix (multiple targets as columns).
    model_names : List[str]
        List of model names to train.
    test_size : float
        Proportion of data for test set.
    validation_size : float
        Proportion of training data for validation set.
    random_state : int
        Random state for reproducibility.
    metrics : List[str]
        List of metrics to compute.
    figures_dir : str
        Directory to save figures.
    reports_dir : str
        Directory to save reports.

    Returns
    -------
    Dict[str, Dict[str, Dict[str, float]]]
        Nested dictionary: {model_name: {target_name: {metric: value}}}
    """
    logger.info(f"Starting multi-target multi-model training...")
    logger.info(f"  Models: {model_names}")
    logger.info(f"  Targets: {y.columns.tolist()}")
    logger.info(f"  Data shape: X={X.shape}, y={y.shape}")

    # Ensure output directories exist
    Path(figures_dir).mkdir(parents=True, exist_ok=True)
    Path(reports_dir).mkdir(parents=True, exist_ok=True)

    # First split: train+val vs. test
    X_trainval, X_test, y_trainval, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, shuffle=True
    )

    # Second split: train vs. val
    val_size_adjusted = validation_size / (1 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_trainval, y_trainval, test_size=val_size_adjusted,
        random_state=random_state, shuffle=True
    )

    logger.info(f"Data split: train={len(X_train)}, val={len(X_val)}, test={len(X_test)}")

    # Results structure: {model_name: {target_name: {metric: value}}}
    all_results = {}
    all_models = {}
    all_predictions = {}

    # Train each model for each target
    for model_name in model_names:
        all_results[model_name] = {}
        all_models[model_name] = {}
        all_predictions[model_name] = {}

        for target_col in y.columns:
            # Get target data
            y_train_target = y_train[target_col].dropna()
            y_val_target = y_val[target_col].dropna()
            y_test_target = y_test[target_col].dropna()

            # Align features with non-null targets
            X_train_target = X_train.loc[y_train_target.index]
            X_val_target = X_val.loc[y_val_target.index]
            X_test_target = X_test.loc[y_test_target.index]

            if len(y_train_target) < 10:
                logger.warning(f"Skipping {model_name}/{target_col}: insufficient training data ({len(y_train_target)} samples)")
                continue

            # Train model
            try:
                model, test_metrics, predictions_df = train_single_target(
                    X_train_target, y_train_target,
                    X_val_target, y_val_target,
                    X_test_target, y_test_target,
                    target_col, model_name, metrics,
                    figures_dir=figures_dir,
                    random_state=random_state
                )

                all_results[model_name][target_col] = test_metrics
                all_models[model_name][target_col] = model
                all_predictions[model_name][target_col] = predictions_df

                # Save predictions
                pred_file = Path(reports_dir) / f'predictions_{target_col}_{model_name}.csv'
                predictions_df.to_csv(pred_file, index=False)

            except Exception as e:
                logger.error(f"Failed to train {model_name} for {target_col}: {e}")
                all_results[model_name][target_col] = {'error': str(e)}

    # Save results summary
    results_file = Path(reports_dir) / 'regression_results.json'
    save_json(all_results, results_file)
    logger.info(f"Regression results saved to: {results_file}")

    # Create model comparison plots
    for metric in metrics:
        try:
            viz.plot_model_comparison(all_results, metric=metric, figures_dir=figures_dir)
        except Exception as e:
            logger.warning(f"Failed to create comparison plot for metric '{metric}': {e}")

    logger.info("Multi-target multi-model training complete.")
    return all_results


def find_best_model(
    results: Dict[str, Dict[str, Dict[str, float]]],
    target_name: str,
    metric: str = 'r2',
    higher_is_better: bool = True
) -> Tuple[str, float]:
    """
    Find the best performing model for a given target and metric.

    Parameters
    ----------
    results : Dict[str, Dict[str, Dict[str, float]]]
        Results from train_multi_target_multi_model.
    target_name : str
        Name of the target variable.
    metric : str
        Metric to use for comparison.
    higher_is_better : bool
        Whether higher values of the metric are better.

    Returns
    -------
    Tuple[str, float]
        Name of the best model and its metric value.
    """
    best_model = None
    best_value = -np.inf if higher_is_better else np.inf

    for model_name, targets in results.items():
        if target_name in targets and metric in targets[target_name]:
            value = targets[target_name][metric]

            if higher_is_better:
                if value > best_value:
                    best_value = value
                    best_model = model_name
            else:
                if value < best_value:
                    best_value = value
                    best_model = model_name

    return best_model, best_value


def print_results_summary(results: Dict[str, Dict[str, Dict[str, float]]]) -> None:
    """
    Print a formatted summary of regression results.

    Parameters
    ----------
    results : Dict[str, Dict[str, Dict[str, float]]]
        Results from train_multi_target_multi_model.
    """
    logger.info("\n" + "="*80)
    logger.info("REGRESSION RESULTS SUMMARY")
    logger.info("="*80)

    for model_name, targets in results.items():
        logger.info(f"\nModel: {model_name.upper()}")
        logger.info("-" * 40)

        for target_name, metrics in targets.items():
            if 'error' in metrics:
                logger.info(f"  {target_name}: ERROR - {metrics['error']}")
            else:
                metrics_str = ', '.join([f"{k.upper()}={v:.4f}" for k, v in metrics.items()])
                logger.info(f"  {target_name}: {metrics_str}")

    logger.info("\n" + "="*80)
