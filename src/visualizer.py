import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os

# Set publication style globally
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['savefig.dpi'] = 300

SAVE_DIR = os.path.join('outputs', 'figures')
os.makedirs(SAVE_DIR, exist_ok=True)

def generate_all_figures(df, history, y_actual, y_pred, cluster_stats):
    """
    Master function to plot Figs 1-14.
    Args:
        df: Main dataframe (with clusters)
        history: Training history dict from trainer.py
        y_actual, y_pred: Test set results
        cluster_stats: Dictionary from clustering.py
    """
    print(f"      [Info] Saving figures to {SAVE_DIR}...")
    
    # --- FIG 1: Target Distribution ---
    plt.figure(figsize=(8, 6))
    sns.histplot(df['Avg_ThermalEfficiency'], kde=True, color='navy')
    plt.title('Fig 1: Distribution of Average Thermal Efficiency')
    plt.xlabel('Efficiency (%)')
    plt.tight_layout()
    plt.savefig(f"{SAVE_DIR}/Fig1_Target_Dist.png")
    plt.close()

    # --- FIG 2: Correlation Matrix ---
    # Select numeric columns relevant to physics
    corr_cols = [
        'Avg_ThermalEfficiency', 'FirepowerCold', 'FirepowerHot', 
        'TempCorrSpecificConsumptionCold', 'FuelMoistWet', 'TimeToBoilCold'
    ]
    # Filter only columns that exist
    valid_corr = [c for c in corr_cols if c in df.columns]
    plt.figure(figsize=(10, 8))
    sns.heatmap(df[valid_corr].corr(), annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Fig 2: Correlation Matrix of Key Features')
    plt.tight_layout()
    plt.savefig(f"{SAVE_DIR}/Fig2_Correlation.png")
    plt.close()

    # --- FIG 3: Feature Importance (Placeholder for NN) ---
    # Since NN doesn't give feature importance easily, we skip or use correlation proxy
    # Here we plot Firepower vs Efficiency as a proxy for "Importance"
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x='FirepowerCold', y='Avg_ThermalEfficiency', data=df, alpha=0.5)
    plt.title('Fig 3: Firepower vs Efficiency (Key Driver)')
    plt.xlabel('Cold Start Firepower (W)')
    plt.ylabel('Efficiency (%)')
    plt.savefig(f"{SAVE_DIR}/Fig3_Feature_Proxy.png")
    plt.close()

    # --- FIG 4: Actual vs Predicted ---
    plt.figure(figsize=(8, 8))
    plt.scatter(y_actual, y_pred, alpha=0.5, color='darkred')
    # Perfect alignment line
    min_val = min(y_actual.min(), y_pred.min())
    max_val = max(y_actual.max(), y_pred.max())
    plt.plot([min_val, max_val], [min_val, max_val], 'k--', lw=2)
    plt.title('Fig 4: Model Performance (Actual vs Predicted)')
    plt.xlabel('Actual Efficiency (%)')
    plt.ylabel('Predicted Efficiency (%)')
    plt.tight_layout()
    plt.savefig(f"{SAVE_DIR}/Fig4_Actual_vs_Pred.png")
    plt.close()

    # --- FIG 5: Residuals ---
    residuals = y_actual.flatten() - y_pred.flatten()
    plt.figure(figsize=(8, 6))
    sns.histplot(residuals, kde=True, color='purple')
    plt.axvline(0, color='red', linestyle='--')
    plt.title('Fig 5: Residual Error Distribution')
    plt.xlabel('Error (Actual - Predicted)')
    plt.savefig(f"{SAVE_DIR}/Fig5_Residuals.png")
    plt.close()

    # --- FIG 6: Top Feature Impact (Simmer) ---
    if 'Firepower(watt)  LOW POWER(SIMMER)' in df.columns:
        plt.figure(figsize=(8, 6))
        sns.regplot(x='Firepower(watt)  LOW POWER(SIMMER)', y='Avg_ThermalEfficiency', 
                    data=df, scatter_kws={'alpha':0.3}, line_kws={'color':'red'})
        plt.title('Fig 6: Impact of Simmer Firepower on Avg Efficiency')
        plt.savefig(f"{SAVE_DIR}/Fig6_Simmer_Impact.png")
        plt.close()

    # --- FIG 7: Efficiency vs Time Tradeoff ---
    if 'TimeToBoilCold' in df.columns:
        plt.figure(figsize=(8, 6))
        sns.scatterplot(x='TimeToBoilCold', y='Avg_ThermalEfficiency', data=df, alpha=0.6)
        plt.title('Fig 7: Efficiency vs Boiling Speed Trade-off')
        plt.xlabel('Time to Boil (min)')
        plt.ylabel('Efficiency (%)')
        plt.savefig(f"{SAVE_DIR}/Fig7_Tradeoff.png")
        plt.close()

    # --- FIG 8: Phase Comparison (Boxplot) ---
    # Create melted DF for boxplot
    melt_cols = ['ThermalEffCold_pct', 'ThermalEffHot_pct', 'ThermalEffSimmer_pct']
    valid_melt = [c for c in melt_cols if c in df.columns]
    if valid_melt:
        melted = pd.melt(df, value_vars=valid_melt, var_name='Phase', value_name='Efficiency')
        plt.figure(figsize=(10, 6))
        sns.boxplot(x='Phase', y='Efficiency', data=melted, palette='Set2')
        plt.title('Fig 8: Efficiency Across Operational Phases')
        plt.savefig(f"{SAVE_DIR}/Fig8_Phase_Comparison.png")
        plt.close()

    # --- FIG 9: Moisture Impact ---
    if 'FuelMoistWet' in df.columns:
        plt.figure(figsize=(8, 6))
        sns.scatterplot(x='FuelMoistWet', y='Avg_ThermalEfficiency', hue='FirepowerCold', data=df)
        plt.title('Fig 9: Fuel Moisture Impact')
        plt.savefig(f"{SAVE_DIR}/Fig9_Moisture_Impact.png")
        plt.close()

    # --- FIG 10: Learning Curve ---
    if history:
        plt.figure(figsize=(8, 6))
        plt.plot(history['train_loss'], label='Train Loss')
        plt.plot(history['val_loss'], label='Val Loss')
        plt.title('Fig 10: Deep Learning Training Curve')
        plt.xlabel('Epochs')
        plt.ylabel('MSE Loss')
        plt.legend()
        plt.yscale('log')
        plt.savefig(f"{SAVE_DIR}/Fig10_Learning_Curve.png")
        plt.close()

    # --- FIG 11: Elbow Method ---
    if cluster_stats and 'wcss' in cluster_stats:
        plt.figure(figsize=(8, 6))
        plt.plot(range(1, 11), cluster_stats['wcss'], marker='o')
        plt.title('Fig 11: Elbow Method for Optimal k')
        plt.xlabel('Number of Clusters')
        plt.ylabel('WCSS')
        plt.savefig(f"{SAVE_DIR}/Fig11_Elbow.png")
        plt.close()

    # --- FIG 12: PCA Clusters ---
    if 'PCA1' in df.columns:
        plt.figure(figsize=(10, 8))
        sns.scatterplot(x='PCA1', y='PCA2', hue='Cluster', data=df, palette='viridis', s=60)
        plt.title('Fig 12: Stove Categories (PCA Projection)')
        plt.savefig(f"{SAVE_DIR}/Fig12_PCA_Clusters.png")
        plt.close()

    # --- FIG 13: Efficiency by Cluster ---
    plt.figure(figsize=(8, 6))
    sns.boxplot(x='Cluster', y='Avg_ThermalEfficiency', data=df, palette='Set3')
    plt.title('Fig 13: Average Efficiency by Stove Category')
    plt.savefig(f"{SAVE_DIR}/Fig13_Cluster_Efficiency.png")
    plt.close()

    # --- FIG 14: Firepower by Cluster ---
    if 'FirepowerCold' in df.columns:
        plt.figure(figsize=(8, 6))
        sns.boxplot(x='Cluster', y='FirepowerCold', data=df, palette='Set3')
        plt.title('Fig 14: Firepower Profile by Stove Category')
        plt.savefig(f"{SAVE_DIR}/Fig14_Cluster_Firepower.png")
        plt.close()