# Phase 5: Prediction-Interval Uncertainty Quantification

Target coverage: **90%**. Random Forest base model (200 trees) on combined features, grouped 5-fold CV by stove identity. Calibration set: 20% of each training fold's stoves.

Two UQ methods evaluated:
1. **Tree-quantile** — per-tree predictions, take 5th/95th percentile across trees
2. **Split-conformal** — calibrate ±q from held-out residual quantile

## Aggregate coverage (mean across folds)

| Target | n_test (mean) | R² | MAE | Tree coverage | Tree width | Conformal coverage | Conformal width |
|---|---:|---:|---:|---:|---:|---:|---:|
| `eff_cold` | 84 | +0.977 | 0.0031 | 83.1% | 0.0101 | 90.0% | 0.0180 |
| `eff_hot` | 84 | +0.977 | 0.0034 | 84.3% | 0.0106 | 92.9% | 0.0213 |
| `fp_simmer` | 78 | +0.957 | 188.7211 | 85.4% | 396.5483 | 91.3% | 1184.1333 |
| `br_simmer` | 78 | +0.957 | 0.3818 | 84.6% | 0.7886 | 90.5% | 2.3697 |
| `fp_cold` | 84 | +0.946 | 461.4283 | 81.9% | 1526.8412 | 90.7% | 2261.5226 |
| `br_cold` | 84 | +0.946 | 0.9304 | 81.9% | 3.0670 | 90.7% | 4.6393 |
| `eff_combined` | 84 | +0.941 | 0.0060 | 86.9% | 0.0242 | 90.2% | 0.0307 |
| `br_hot` | 84 | +0.939 | 1.5274 | 81.4% | 4.6538 | 92.4% | 8.6278 |
| `fp_hot` | 84 | +0.938 | 761.5678 | 81.2% | 2316.8579 | 92.9% | 4343.4811 |
| `eff_simmer` | 84 | +0.669 | 0.0390 | 90.7% | 0.0782 | 92.4% | 0.2478 |

Tree-quantile intervals are **asymptotic** — they reflect tree-ensemble disagreement, not formal coverage guarantee. Split-conformal intervals are **distribution-free** with formal guarantee: empirical coverage should be close to the target. Wide gaps between empirical and target coverage indicate miscalibration.
