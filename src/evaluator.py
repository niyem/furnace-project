import numpy as np
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

def evaluate_model(y_actual, y_pred):
    """
    Calculates regression metrics.
    """
    # Ensure inputs are 1D arrays
    y_true = np.array(y_actual).flatten()
    y_p = np.array(y_pred).flatten()
    
    # Calculate Metrics
    r2 = r2_score(y_true, y_p)
    mse = mean_squared_error(y_true, y_p)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_p)
    
    # Calculate Residuals
    residuals = y_true - y_p
    
    metrics = {
        'R2': r2,
        'RMSE': rmse,
        'MAE': mae
    }
    
    return metrics, residuals