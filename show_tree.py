import os, textwrap

PIPELINE_STEPS = [
    "1) Load data (src/data_loader.py)",
    "2) Preprocess: NA filtering, impute, scale (src/preprocess.py)",
    "3) Dimensionality reduction: PCA/UMAP (src/dim_reduce.py)",
    "4) Clustering: KMeans/DBSCAN + metrics (src/cluster.py)",
    "5) Regression: multi-target models (src/regression.py)",
    "6) Reports saved to outputs/reports",
]

def tree(startpath):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for f in files:
            print(f"{subindent}{f}")

if __name__ == "__main__":
    print("=== Project Tree ===")
    tree(".")
    print("\n=== Execution Steps (DAG) ===")
    for s in PIPELINE_STEPS:
        print(s)
