# Phase 2: Feature Ablation

Grouped 5-fold CV by stove identity. Mean R² ± std across folds.
Models: Ridge (regularized linear) and Random Forest (100 trees).

## Target: `br_cold`

| Features | Model | n | n_feat | R² (mean ± std) | MAE (mean ± std) |
|---|---|---:|---:|---|---|
| wbt_other_phase | rf | 450 | 11 | 0.957 ± 0.014 | 0.8375 ± 0.0914 |
| wbt_other_phys | rf | 450 | 17 | 0.957 ± 0.014 | 0.8394 ± 0.0925 |
| combined | rf | 420 | 18 | 0.956 ± 0.015 | 0.8369 ± 0.1191 |
| combined_phys | rf | 420 | 24 | 0.956 ± 0.015 | 0.8395 ± 0.1147 |
| wbt_other_phys | ridge | 450 | 17 | 0.928 ± 0.013 | 1.2249 ± 0.1070 |
| combined | ridge | 420 | 18 | 0.926 ± 0.009 | 1.2794 ± 0.0786 |
| combined_phys | ridge | 420 | 24 | 0.926 ± 0.008 | 1.2772 ± 0.0807 |
| wbt_other_phase | ridge | 450 | 11 | 0.925 ± 0.013 | 1.2408 ± 0.1039 |
| geometry_phys | ridge | 420 | 15 | 0.864 ± 0.024 | 1.6881 ± 0.1362 |
| geometry_phys | rf | 420 | 15 | 0.864 ± 0.024 | 1.6888 ± 0.1372 |
| geometry | ridge | 420 | 9 | 0.864 ± 0.024 | 1.6874 ± 0.1343 |
| geometry | rf | 420 | 9 | 0.864 ± 0.024 | 1.6888 ± 0.1372 |

## Target: `br_hot`

| Features | Model | n | n_feat | R² (mean ± std) | MAE (mean ± std) |
|---|---|---:|---:|---|---|
| combined | rf | 420 | 18 | 0.948 ± 0.013 | 1.3985 ± 0.1595 |
| combined_phys | rf | 420 | 24 | 0.948 ± 0.013 | 1.3968 ± 0.1607 |
| wbt_other_phys | rf | 450 | 17 | 0.933 ± 0.034 | 1.4433 ± 0.2004 |
| wbt_other_phase | rf | 450 | 11 | 0.932 ± 0.035 | 1.4435 ± 0.1999 |
| wbt_other_phase | ridge | 450 | 11 | 0.912 ± 0.022 | 1.9311 ± 0.2680 |
| combined | ridge | 420 | 18 | 0.911 ± 0.012 | 1.9828 ± 0.2339 |
| combined_phys | ridge | 420 | 24 | 0.911 ± 0.012 | 1.9849 ± 0.2356 |
| wbt_other_phys | ridge | 450 | 17 | 0.911 ± 0.022 | 1.9380 ± 0.2716 |
| geometry_phys | ridge | 420 | 15 | 0.837 ± 0.013 | 2.6346 ± 0.1596 |
| geometry | ridge | 420 | 9 | 0.837 ± 0.014 | 2.6332 ± 0.1591 |
| geometry_phys | rf | 420 | 15 | 0.836 ± 0.013 | 2.6367 ± 0.1549 |
| geometry | rf | 420 | 9 | 0.836 ± 0.013 | 2.6367 ± 0.1549 |

## Target: `br_simmer`

| Features | Model | n | n_feat | R² (mean ± std) | MAE (mean ± std) |
|---|---|---:|---:|---|---|
| combined | rf | 390 | 19 | 0.961 ± 0.019 | 0.3567 ± 0.0559 |
| combined_phys | rf | 390 | 25 | 0.961 ± 0.019 | 0.3566 ± 0.0565 |
| wbt_other_phys | rf | 420 | 18 | 0.961 ± 0.019 | 0.3457 ± 0.0528 |
| wbt_other_phase | rf | 420 | 12 | 0.960 ± 0.019 | 0.3532 ± 0.0526 |
| wbt_other_phys | ridge | 420 | 18 | 0.912 ± 0.024 | 0.6242 ± 0.0542 |
| combined_phys | ridge | 390 | 25 | 0.911 ± 0.012 | 0.6484 ± 0.0556 |
| combined | ridge | 390 | 19 | 0.910 ± 0.011 | 0.6600 ± 0.0522 |
| wbt_other_phase | ridge | 420 | 12 | 0.903 ± 0.021 | 0.6932 ± 0.0468 |
| geometry_phys | ridge | 390 | 15 | 0.897 ± 0.014 | 0.6385 ± 0.0603 |
| geometry_phys | rf | 390 | 15 | 0.897 ± 0.015 | 0.6390 ± 0.0628 |
| geometry | ridge | 390 | 9 | 0.897 ± 0.014 | 0.6404 ± 0.0613 |
| geometry | rf | 390 | 9 | 0.897 ± 0.015 | 0.6390 ± 0.0628 |

## Target: `eff_cold`

| Features | Model | n | n_feat | R² (mean ± std) | MAE (mean ± std) |
|---|---|---:|---:|---|---|
| combined | rf | 420 | 18 | 0.983 ± 0.004 | 0.0028 ± 0.0003 |
| combined_phys | rf | 420 | 24 | 0.982 ± 0.004 | 0.0028 ± 0.0004 |
| wbt_other_phase | rf | 450 | 11 | 0.979 ± 0.008 | 0.0028 ± 0.0004 |
| wbt_other_phys | rf | 450 | 17 | 0.979 ± 0.009 | 0.0028 ± 0.0004 |
| combined_phys | ridge | 420 | 24 | 0.975 ± 0.007 | 0.0035 ± 0.0004 |
| combined | ridge | 420 | 18 | 0.975 ± 0.007 | 0.0035 ± 0.0004 |
| wbt_other_phys | ridge | 450 | 17 | 0.974 ± 0.013 | 0.0034 ± 0.0006 |
| wbt_other_phase | ridge | 450 | 11 | 0.974 ± 0.012 | 0.0034 ± 0.0006 |
| geometry_phys | rf | 420 | 15 | 0.042 ± 0.042 | 0.0168 ± 0.0016 |
| geometry | rf | 420 | 9 | 0.042 ± 0.042 | 0.0168 ± 0.0016 |
| geometry_phys | ridge | 420 | 15 | 0.041 ± 0.040 | 0.0171 ± 0.0016 |
| geometry | ridge | 420 | 9 | 0.041 ± 0.039 | 0.0171 ± 0.0015 |

## Target: `eff_combined`

| Features | Model | n | n_feat | R² (mean ± std) | MAE (mean ± std) |
|---|---|---:|---:|---|---|
| combined_phys | rf | 420 | 26 | 0.943 ± 0.030 | 0.0056 ± 0.0002 |
| combined | rf | 420 | 20 | 0.941 ± 0.033 | 0.0056 ± 0.0004 |
| wbt_other_phase | rf | 450 | 13 | 0.934 ± 0.029 | 0.0058 ± 0.0005 |
| wbt_other_phys | rf | 450 | 19 | 0.933 ± 0.031 | 0.0058 ± 0.0005 |
| wbt_other_phys | ridge | 450 | 19 | 0.794 ± 0.023 | 0.0128 ± 0.0009 |
| wbt_other_phase | ridge | 450 | 13 | 0.794 ± 0.019 | 0.0128 ± 0.0008 |
| combined_phys | ridge | 420 | 26 | 0.785 ± 0.017 | 0.0135 ± 0.0008 |
| combined | ridge | 420 | 20 | 0.785 ± 0.017 | 0.0136 ± 0.0009 |
| geometry_phys | rf | 420 | 15 | 0.013 ± 0.051 | 0.0224 ± 0.0006 |
| geometry | rf | 420 | 9 | 0.013 ± 0.051 | 0.0224 ± 0.0006 |
| geometry_phys | ridge | 420 | 15 | 0.012 ± 0.054 | 0.0225 ± 0.0006 |
| geometry | ridge | 420 | 9 | 0.012 ± 0.048 | 0.0227 ± 0.0005 |

## Target: `eff_hot`

| Features | Model | n | n_feat | R² (mean ± std) | MAE (mean ± std) |
|---|---|---:|---:|---|---|
| combined | rf | 420 | 18 | 0.981 ± 0.005 | 0.0030 ± 0.0003 |
| combined_phys | rf | 420 | 24 | 0.981 ± 0.006 | 0.0031 ± 0.0003 |
| wbt_other_phase | rf | 450 | 11 | 0.981 ± 0.009 | 0.0030 ± 0.0004 |
| wbt_other_phys | rf | 450 | 17 | 0.981 ± 0.009 | 0.0030 ± 0.0004 |
| combined_phys | ridge | 420 | 24 | 0.975 ± 0.006 | 0.0038 ± 0.0004 |
| combined | ridge | 420 | 18 | 0.975 ± 0.006 | 0.0038 ± 0.0004 |
| wbt_other_phys | ridge | 450 | 17 | 0.974 ± 0.011 | 0.0037 ± 0.0005 |
| wbt_other_phase | ridge | 450 | 11 | 0.974 ± 0.011 | 0.0037 ± 0.0005 |
| geometry_phys | rf | 420 | 15 | 0.044 ± 0.045 | 0.0178 ± 0.0019 |
| geometry | rf | 420 | 9 | 0.044 ± 0.045 | 0.0178 ± 0.0019 |
| geometry_phys | ridge | 420 | 15 | 0.043 ± 0.043 | 0.0180 ± 0.0019 |
| geometry | ridge | 420 | 9 | 0.043 ± 0.043 | 0.0180 ± 0.0018 |

## Target: `eff_simmer`

| Features | Model | n | n_feat | R² (mean ± std) | MAE (mean ± std) |
|---|---|---:|---:|---|---|
| combined_phys | rf | 420 | 25 | 0.687 ± 0.119 | 0.0353 ± 0.0057 |
| combined | rf | 420 | 19 | 0.684 ± 0.113 | 0.0359 ± 0.0059 |
| wbt_other_phys | rf | 450 | 18 | 0.683 ± 0.117 | 0.0331 ± 0.0061 |
| wbt_other_phase | rf | 450 | 12 | 0.680 ± 0.103 | 0.0337 ± 0.0058 |
| wbt_other_phase | ridge | 450 | 12 | 0.521 ± 0.129 | 0.0641 ± 0.0040 |
| wbt_other_phys | ridge | 450 | 18 | 0.520 ± 0.129 | 0.0643 ± 0.0042 |
| combined | ridge | 420 | 19 | 0.518 ± 0.097 | 0.0668 ± 0.0036 |
| combined_phys | ridge | 420 | 25 | 0.517 ± 0.097 | 0.0673 ± 0.0037 |
| geometry_phys | rf | 420 | 15 | 0.006 ± 0.049 | 0.0811 ± 0.0035 |
| geometry | rf | 420 | 9 | 0.006 ± 0.049 | 0.0811 ± 0.0035 |
| geometry_phys | ridge | 420 | 15 | 0.004 ± 0.052 | 0.0825 ± 0.0035 |
| geometry | ridge | 420 | 9 | 0.004 ± 0.049 | 0.0826 ± 0.0036 |

## Target: `fp_cold`

| Features | Model | n | n_feat | R² (mean ± std) | MAE (mean ± std) |
|---|---|---:|---:|---|---|
| combined | rf | 420 | 18 | 0.957 ± 0.015 | 416.4071 ± 59.0830 |
| combined_phys | rf | 420 | 24 | 0.957 ± 0.015 | 415.2306 ± 60.3634 |
| wbt_other_phase | rf | 450 | 11 | 0.957 ± 0.014 | 416.5021 ± 44.3450 |
| wbt_other_phys | rf | 450 | 17 | 0.957 ± 0.014 | 416.7094 ± 44.8570 |
| wbt_other_phys | ridge | 450 | 17 | 0.928 ± 0.013 | 608.3751 ± 53.1461 |
| combined | ridge | 420 | 18 | 0.926 ± 0.009 | 635.4562 ± 39.0608 |
| combined_phys | ridge | 420 | 24 | 0.926 ± 0.008 | 634.3270 ± 40.0773 |
| wbt_other_phase | ridge | 450 | 11 | 0.925 ± 0.013 | 616.2454 ± 51.5862 |
| geometry_phys | ridge | 420 | 15 | 0.864 ± 0.024 | 838.3993 ± 67.6635 |
| geometry_phys | rf | 420 | 15 | 0.864 ± 0.024 | 838.7820 ± 68.1373 |
| geometry | ridge | 420 | 9 | 0.864 ± 0.024 | 838.0546 ± 66.6810 |
| geometry | rf | 420 | 9 | 0.864 ± 0.024 | 838.7820 ± 68.1373 |

## Target: `fp_hot`

| Features | Model | n | n_feat | R² (mean ± std) | MAE (mean ± std) |
|---|---|---:|---:|---|---|
| combined_phys | rf | 420 | 24 | 0.948 ± 0.013 | 694.9565 ± 79.7363 |
| combined | rf | 420 | 18 | 0.947 ± 0.013 | 695.4878 ± 80.2980 |
| wbt_other_phase | rf | 450 | 11 | 0.933 ± 0.034 | 715.8151 ± 99.4574 |
| wbt_other_phys | rf | 450 | 17 | 0.932 ± 0.034 | 717.9441 ± 97.1567 |
| wbt_other_phase | ridge | 450 | 11 | 0.912 ± 0.022 | 959.0963 ± 133.0825 |
| combined | ridge | 420 | 18 | 0.911 ± 0.012 | 984.8018 ± 116.1543 |
| combined_phys | ridge | 420 | 24 | 0.911 ± 0.012 | 985.8484 ± 116.9928 |
| wbt_other_phys | ridge | 450 | 17 | 0.911 ± 0.022 | 962.5562 ± 134.9043 |
| geometry_phys | ridge | 420 | 15 | 0.837 ± 0.013 | 1308.5139 ± 79.2506 |
| geometry | ridge | 420 | 9 | 0.837 ± 0.014 | 1307.8187 ± 79.0368 |
| geometry_phys | rf | 420 | 15 | 0.836 ± 0.013 | 1309.5376 ± 76.9448 |
| geometry | rf | 420 | 9 | 0.836 ± 0.013 | 1309.5376 ± 76.9448 |

## Target: `fp_simmer`

| Features | Model | n | n_feat | R² (mean ± std) | MAE (mean ± std) |
|---|---|---:|---:|---|---|
| combined_phys | rf | 390 | 25 | 0.962 ± 0.020 | 175.9859 ± 27.9305 |
| combined | rf | 390 | 19 | 0.961 ± 0.019 | 178.1145 ± 27.5865 |
| wbt_other_phys | rf | 420 | 18 | 0.961 ± 0.019 | 171.3600 ± 25.2853 |
| wbt_other_phase | rf | 420 | 12 | 0.960 ± 0.019 | 177.1384 ± 24.8614 |
| wbt_other_phys | ridge | 420 | 18 | 0.912 ± 0.024 | 310.0408 ± 26.9248 |
| combined_phys | ridge | 390 | 25 | 0.911 ± 0.012 | 322.0176 ± 27.6186 |
| combined | ridge | 390 | 19 | 0.910 ± 0.011 | 327.7807 ± 25.9304 |
| wbt_other_phase | ridge | 420 | 12 | 0.903 ± 0.021 | 344.2813 ± 23.2329 |
| geometry_phys | ridge | 390 | 15 | 0.897 ± 0.014 | 317.1333 ± 29.9290 |
| geometry_phys | rf | 390 | 15 | 0.897 ± 0.015 | 317.3698 ± 31.2032 |
| geometry | ridge | 390 | 9 | 0.897 ± 0.014 | 318.0668 ± 30.4607 |
| geometry | rf | 390 | 9 | 0.897 ± 0.015 | 317.3698 ± 31.2032 |
