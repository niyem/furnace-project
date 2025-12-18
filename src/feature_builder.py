import pandas as pd
import numpy as np

def build_features(df):
    """
    Constructs the target variable (Average Efficiency) and selects
    predictive features for the model.
    """
    # 1. Create Target Variable (The Average of 3 Phases)
    # We assume _pct columns exist from preprocess step
    df['Avg_ThermalEfficiency'] = (
        df['ThermalEffCold_pct'] + 
        df['ThermalEffHot_pct'] + 
        df['ThermalEffSimmer_pct']
    ) / 3

    # 2. Select Features (Predictors)
    # We exclude specific efficiency metrics to prevent "Data Leakage"
    # (i.e., you can't use Cold Start Efficiency to predict Average Efficiency)
    leakage_cols = [
        'ThermalEffCold', 'ThermalEffHot', 
        'Thermal efficiency(%)  LOW POWER(SIMMER)',
        'ThermalEffCold_pct', 'ThermalEffHot_pct', 'ThermalEffSimmer_pct',
        'Avg_ThermalEfficiency' # The target itself
    ]
    
    # Identify Potential Features:
    # We want physical stove parameters: Firepower, Fuel Consumption, Time to Boil, etc.
    # We filter for numeric columns only.
    feature_candidates = df.select_dtypes(include=[np.number]).drop(columns=leakage_cols, errors='ignore')

    # Remove columns with 0 variance (constant values like 'AvgCO2' if it's always 10)
    features = feature_candidates.loc[:, feature_candidates.std() > 0]
    
    # Remove columns that are just IDs or indices (simple heuristic: correlation with index)
    # For this dataset, we'll keep the physically meaningful ones identified in EDA
    # Key physical features we definitely want:
    priority_features = [
        'FirepowerCold', 'FirepowerHot', 'Firepower(watt)  LOW POWER(SIMMER)',
        'TempCorrSpecificConsumptionCold', 'TempCorrSpecificConsumptionHot',
        'Specific fuel consumption (g/l)  LOW POWER(SIMMER)',
        'FuelMoistWet', 'TimeToBoilCold', 'TimeToBoilHot',
        'BurningRateCold', 'BurningRateHot'
    ]
    
    # Ensure priority features exist in the dataset
    selected_features = [f for f in priority_features if f in df.columns]
    
    # Add any other high-variance numeric features that aren't in the leakage list
    # (Optional: limited to top 20 to avoid overfitting)
    extra_features = [col for col in features.columns if col not in selected_features]
    final_features_list = selected_features + extra_features[:10] # Top 10 extras

    X = df[final_features_list].copy()
    y = df['Avg_ThermalEfficiency'].copy()

    # Combine X and y into one dataframe for the model loader
    model_data = X.copy()
    model_data['TARGET_Avg_Efficiency'] = y

    return model_data, y