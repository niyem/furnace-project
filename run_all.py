import os
import sys
import pandas as pd
import warnings

# Suppress fragmentation warnings
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)

# Import custom modules from the src folder
from src.preprocess import clean_data
from src.feature_builder import build_features
from src.clustering import run_clustering
from src.trainer import train_model
from src.evaluator import evaluate_model
from src.visualizer import generate_all_figures

# ==========================================
# CONFIGURATION & PATHS
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data Paths
RAW_FILENAME = 'Final_Modified.xlsx' 
RAW_DATA_PATH = os.path.join(BASE_DIR, 'data', 'raw', RAW_FILENAME)

# Output Paths
PROCESSED_DATA_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'cleaned_data.csv')
FINAL_DATA_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'model_ready_data.csv')
MODEL_OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs', 'models')
MODEL_PATH = os.path.join(MODEL_OUTPUT_DIR, 'furnace_net.pth')

def main():
    print("===================================================")
    print("      FURNACE-PROJECT: END-TO-END PIPELINE")
    print("===================================================")

    # --- CHECK DIRECTORIES ---
    os.makedirs(os.path.join(BASE_DIR, 'data', 'processed'), exist_ok=True)
    os.makedirs(MODEL_OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, 'outputs', 'figures'), exist_ok=True)

    # --- STEP 1: PREPROCESSING ---
    print(f"\n[1/6] Preprocessing Data...")
    if not os.path.exists(RAW_DATA_PATH):
        print(f"[ERROR] Raw data file not found at: {RAW_DATA_PATH}")
        sys.exit(1)

    # df_clean contains ALL columns (good for visualization)
    df_clean = clean_data(RAW_DATA_PATH)
    df_clean.to_csv(PROCESSED_DATA_PATH, index=False)
    print(f"      -> Data cleaned and saved to {PROCESSED_DATA_PATH}")

    # --- STEP 2: FEATURE ENGINEERING ---
    print(f"\n[2/6] Building Features & Target...")
    # df_model contains ONLY columns for the Neural Net (good for training)
    df_model, target = build_features(df_clean)
    df_model.to_csv(FINAL_DATA_PATH, index=False)
    print(f"      -> Feature set created. Shape: {df_model.shape}")

    # --- STEP 3: CLUSTERING ---
    print(f"\n[3/6] Running Clustering Analysis...")
    df_clustered, cluster_stats = run_clustering(df_model)
    print(f"      -> Stoves categorized into {len(set(df_clustered['Cluster']))} clusters.")

    # --- STEP 4: DEEP LEARNING ---
    print(f"\n[4/6] Training Neural Network...")
    history = train_model(FINAL_DATA_PATH, MODEL_PATH)
    print(f"      -> Model saved to {MODEL_PATH}")

    # --- STEP 5: EVALUATION ---
    print(f"\n[5/6] Evaluating Model Performance...")
    metrics, residuals = evaluate_model(history['y_actual'], history['y_pred'])
    print(f"      R² Score: {metrics['R2']:.4f}")
    print(f"      RMSE:     {metrics['RMSE']:.4f}")

    # --- STEP 6: VISUALIZATION (THE FIX IS HERE) ---
    print(f"\n[6/6] Generating Publication Figures...")
    
    # CRITICAL FIX: Merge the Clustering results back into the Original Full Dataset
    # This ensures the Visualizer has access to ALL columns (Efficiency, Moisture, etc.)
    # AND the new Cluster IDs.
    df_viz = df_clean.copy()
    
    # 1. Add Cluster info
    df_viz['Cluster'] = df_clustered['Cluster']
    df_viz['PCA1'] = df_clustered['PCA1']
    df_viz['PCA2'] = df_clustered['PCA2']
    
    # 2. Ensure the Target column name matches what Visualizer expects
    # We recalculate it here to be 100% sure it exists in the Viz dataframe
    df_viz['Avg_ThermalEfficiency'] = (
        df_viz['ThermalEffCold_pct'] + 
        df_viz['ThermalEffHot_pct'] + 
        df_viz['ThermalEffSimmer_pct']
    ) / 3

    generate_all_figures(
        df=df_viz,                  # Passing the RICH dataframe
        history=history, 
        y_actual=history['y_actual'], 
        y_pred=history['y_pred'], 
        cluster_stats=cluster_stats
    )

    print("\n===================================================")
    print(f"[DONE] Pipeline Finished Successfully.")
    print(f"       All figures are saved in: outputs/figures/")
    print("===================================================")

if __name__ == "__main__":
    main()