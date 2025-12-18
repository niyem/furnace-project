import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

def run_clustering(df, k=5):  # <--- CHANGED DEFAULT TO 5
    """
    Performs K-Means clustering with k=5 to match physical stove types.
    """
    # 1. Select Features
    cluster_features = [
        'ThermalEffCold_pct', 'ThermalEffHot_pct', 'ThermalEffSimmer_pct',
        'FirepowerCold', 'FirepowerHot', 'Firepower(watt)  LOW POWER(SIMMER)',
        'FuelMoistWet'
    ]
    
    valid_features = [c for c in cluster_features if c in df.columns]
    
    # 2. Scale Data
    X = df[valid_features].fillna(df[valid_features].median())
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 3. Elbow Stats (Still useful to see if 5 is mathematically optimal)
    wcss = []
    for i in range(1, 11):
        km = KMeans(n_clusters=i, init='k-means++', random_state=42, n_init=10)
        km.fit(X_scaled)
        wcss.append(km.inertia_)

    # 4. Apply Clustering with k=5
    print(f"      [Clustering] Forcing k={k} categories...")
    final_km = KMeans(n_clusters=k, init='k-means++', random_state=42, n_init=10)
    cluster_labels = final_km.fit_predict(X_scaled)
    
    # 5. PCA
    pca = PCA(n_components=2)
    pca_components = pca.fit_transform(X_scaled)

    df_out = df.copy()
    df_out['Cluster'] = cluster_labels
    df_out['PCA1'] = pca_components[:, 0]
    df_out['PCA2'] = pca_components[:, 1]
    
    stats = {'wcss': wcss}
    return df_out, stats