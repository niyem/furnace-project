# Phase 1: Predictability Landscape

Grouped 5-fold CV by stove identity (`src_path`). Mean R² ± std across folds. MAE in target units.

## Target: `br_cold`

| Features | Model | n | n_feat | R² (mean ± std) | MAE (mean ± std) |
|---|---|---:|---:|---|---|
| combined | gbt | 420 | 19 | 0.965 ± 0.014 | 0.7125 ± 0.1026 |
| wbt_other_phase | gbt | 450 | 12 | 0.959 ± 0.014 | 0.7558 ± 0.0801 |
| combined | rf | 420 | 19 | 0.958 ± 0.015 | 0.8310 ± 0.1278 |
| wbt_other_phase | rf | 450 | 12 | 0.958 ± 0.014 | 0.8291 ± 0.0813 |
| combined | ridge | 420 | 19 | 0.926 ± 0.009 | 1.2756 ± 0.0812 |
| wbt_other_phase | ridge | 450 | 12 | 0.926 ± 0.013 | 1.2365 ± 0.1066 |
| geometry | gbt | 420 | 9 | 0.864 ± 0.024 | 1.6880 ± 0.1365 |
| geometry | rf | 420 | 9 | 0.864 ± 0.024 | 1.6882 ± 0.1364 |
| geometry | ridge | 420 | 9 | 0.864 ± 0.024 | 1.6874 ± 0.1343 |

## Target: `br_hot`

| Features | Model | n | n_feat | R² (mean ± std) | MAE (mean ± std) |
|---|---|---:|---:|---|---|
| combined | gbt | 420 | 19 | 0.958 ± 0.013 | 1.1732 ± 0.1431 |
| combined | rf | 420 | 19 | 0.947 ± 0.013 | 1.3996 ± 0.1616 |
| wbt_other_phase | gbt | 450 | 12 | 0.937 ± 0.047 | 1.2352 ± 0.2758 |
| wbt_other_phase | rf | 450 | 12 | 0.932 ± 0.036 | 1.4497 ± 0.2094 |
| combined | ridge | 420 | 19 | 0.914 ± 0.011 | 1.9468 ± 0.2114 |
| wbt_other_phase | ridge | 450 | 12 | 0.914 ± 0.021 | 1.8953 ± 0.2484 |
| geometry | gbt | 420 | 9 | 0.837 ± 0.013 | 2.6350 ± 0.1594 |
| geometry | rf | 420 | 9 | 0.837 ± 0.013 | 2.6352 ± 0.1592 |
| geometry | ridge | 420 | 9 | 0.837 ± 0.014 | 2.6332 ± 0.1591 |

## Target: `br_simmer`

| Features | Model | n | n_feat | R² (mean ± std) | MAE (mean ± std) |
|---|---|---:|---:|---|---|
| combined | gbt | 390 | 20 | 0.968 ± 0.012 | 0.2812 ± 0.0416 |
| wbt_other_phase | gbt | 420 | 13 | 0.968 ± 0.013 | 0.2858 ± 0.0349 |
| wbt_other_phase | rf | 420 | 13 | 0.962 ± 0.016 | 0.3379 ± 0.0625 |
| combined | rf | 390 | 20 | 0.959 ± 0.017 | 0.3502 ± 0.0576 |
| combined | ridge | 390 | 20 | 0.911 ± 0.012 | 0.6452 ± 0.0493 |
| wbt_other_phase | ridge | 420 | 13 | 0.903 ± 0.021 | 0.6927 ± 0.0448 |
| geometry | gbt | 390 | 9 | 0.897 ± 0.015 | 0.6385 ± 0.0605 |
| geometry | rf | 390 | 9 | 0.897 ± 0.015 | 0.6387 ± 0.0617 |
| geometry | ridge | 390 | 9 | 0.897 ± 0.014 | 0.6404 ± 0.0613 |

## Target: `eff_cold`

| Features | Model | n | n_feat | R² (mean ± std) | MAE (mean ± std) |
|---|---|---:|---:|---|---|
| combined | gbt | 420 | 19 | 0.987 ± 0.006 | 0.0022 ± 0.0004 |
| combined | ridge | 420 | 19 | 0.984 ± 0.004 | 0.0028 ± 0.0003 |
| wbt_other_phase | ridge | 450 | 12 | 0.984 ± 0.008 | 0.0027 ± 0.0005 |
| wbt_other_phase | gbt | 450 | 12 | 0.983 ± 0.011 | 0.0024 ± 0.0003 |
| combined | rf | 420 | 19 | 0.983 ± 0.003 | 0.0026 ± 0.0003 |
| wbt_other_phase | rf | 450 | 12 | 0.981 ± 0.009 | 0.0028 ± 0.0004 |
| geometry | gbt | 420 | 9 | 0.041 ± 0.041 | 0.0171 ± 0.0016 |
| geometry | rf | 420 | 9 | 0.041 ± 0.042 | 0.0170 ± 0.0016 |
| geometry | ridge | 420 | 9 | 0.041 ± 0.039 | 0.0171 ± 0.0015 |

## Target: `eff_combined`

| Features | Model | n | n_feat | R² (mean ± std) | MAE (mean ± std) |
|---|---|---:|---:|---|---|
| combined | ridge | 420 | 23 | 1.000 ± 0.000 | 0.0004 ± 0.0000 |
| wbt_other_phase | ridge | 450 | 16 | 1.000 ± 0.000 | 0.0003 ± 0.0000 |
| wbt_other_phase | rf | 450 | 16 | 0.995 ± 0.002 | 0.0017 ± 0.0002 |
| combined | rf | 420 | 23 | 0.994 ± 0.002 | 0.0017 ± 0.0001 |
| combined | gbt | 420 | 23 | 0.987 ± 0.024 | 0.0015 ± 0.0007 |
| wbt_other_phase | gbt | 450 | 16 | 0.987 ± 0.023 | 0.0016 ± 0.0005 |
| geometry | rf | 420 | 9 | 0.012 ± 0.052 | 0.0225 ± 0.0006 |
| geometry | ridge | 420 | 9 | 0.012 ± 0.048 | 0.0227 ± 0.0005 |
| geometry | gbt | 420 | 9 | 0.011 ± 0.054 | 0.0225 ± 0.0006 |

## Target: `eff_hot`

| Features | Model | n | n_feat | R² (mean ± std) | MAE (mean ± std) |
|---|---|---:|---:|---|---|
| wbt_other_phase | gbt | 450 | 12 | 0.987 ± 0.008 | 0.0024 ± 0.0005 |
| combined | gbt | 420 | 19 | 0.986 ± 0.004 | 0.0024 ± 0.0001 |
| combined | ridge | 420 | 19 | 0.985 ± 0.004 | 0.0029 ± 0.0003 |
| wbt_other_phase | ridge | 450 | 12 | 0.984 ± 0.007 | 0.0028 ± 0.0005 |
| combined | rf | 420 | 19 | 0.982 ± 0.005 | 0.0030 ± 0.0003 |
| wbt_other_phase | rf | 450 | 12 | 0.982 ± 0.008 | 0.0030 ± 0.0004 |
| geometry | gbt | 420 | 9 | 0.043 ± 0.044 | 0.0180 ± 0.0019 |
| geometry | rf | 420 | 9 | 0.043 ± 0.044 | 0.0179 ± 0.0019 |
| geometry | ridge | 420 | 9 | 0.043 ± 0.043 | 0.0180 ± 0.0018 |

## Target: `eff_simmer`

| Features | Model | n | n_feat | R² (mean ± std) | MAE (mean ± std) |
|---|---|---:|---:|---|---|
| combined | ridge | 420 | 20 | 1.000 ± 0.000 | 0.0003 ± 0.0000 |
| wbt_other_phase | ridge | 450 | 13 | 1.000 ± 0.000 | 0.0003 ± 0.0000 |
| wbt_other_phase | gbt | 450 | 13 | 0.999 ± 0.001 | 0.0028 ± 0.0008 |
| combined | gbt | 420 | 20 | 0.998 ± 0.001 | 0.0030 ± 0.0009 |
| wbt_other_phase | rf | 450 | 13 | 0.998 ± 0.000 | 0.0043 ± 0.0005 |
| combined | rf | 420 | 20 | 0.997 ± 0.001 | 0.0046 ± 0.0006 |
| geometry | gbt | 420 | 9 | 0.004 ± 0.052 | 0.0825 ± 0.0035 |
| geometry | rf | 420 | 9 | 0.004 ± 0.050 | 0.0819 ± 0.0036 |
| geometry | ridge | 420 | 9 | 0.004 ± 0.049 | 0.0826 ± 0.0036 |

## Target: `fp_cold`

| Features | Model | n | n_feat | R² (mean ± std) | MAE (mean ± std) |
|---|---|---:|---:|---|---|
| combined | gbt | 420 | 19 | 0.965 ± 0.014 | 353.8212 ± 51.1948 |
| wbt_other_phase | gbt | 450 | 12 | 0.959 ± 0.014 | 375.5081 ± 39.7277 |
| combined | rf | 420 | 19 | 0.958 ± 0.015 | 411.9292 ± 63.2570 |
| wbt_other_phase | rf | 450 | 12 | 0.958 ± 0.014 | 411.9756 ± 40.4667 |
| combined | ridge | 420 | 19 | 0.926 ± 0.009 | 633.5453 ± 40.3431 |
| wbt_other_phase | ridge | 450 | 12 | 0.926 ± 0.013 | 614.1309 ± 52.9377 |
| geometry | gbt | 420 | 9 | 0.864 ± 0.024 | 838.3633 ± 67.7859 |
| geometry | rf | 420 | 9 | 0.864 ± 0.024 | 838.4567 ± 67.7251 |
| geometry | ridge | 420 | 9 | 0.864 ± 0.024 | 838.0546 ± 66.6810 |

## Target: `fp_hot`

| Features | Model | n | n_feat | R² (mean ± std) | MAE (mean ± std) |
|---|---|---:|---:|---|---|
| combined | gbt | 420 | 19 | 0.958 ± 0.013 | 582.8055 ± 70.9916 |
| combined | rf | 420 | 19 | 0.947 ± 0.013 | 696.1375 ± 80.1304 |
| wbt_other_phase | gbt | 450 | 12 | 0.936 ± 0.047 | 613.9322 ± 136.5386 |
| wbt_other_phase | rf | 450 | 12 | 0.931 ± 0.035 | 722.3116 ± 103.7681 |
| combined | ridge | 420 | 19 | 0.914 ± 0.011 | 966.8986 ± 105.0196 |
| wbt_other_phase | ridge | 450 | 12 | 0.914 ± 0.021 | 941.3443 ± 123.3799 |
| geometry | gbt | 420 | 9 | 0.837 ± 0.013 | 1308.7265 ± 79.1606 |
| geometry | rf | 420 | 9 | 0.837 ± 0.013 | 1308.8126 ± 79.0894 |
| geometry | ridge | 420 | 9 | 0.837 ± 0.014 | 1307.8187 ± 79.0368 |

## Target: `fp_simmer`

| Features | Model | n | n_feat | R² (mean ± std) | MAE (mean ± std) |
|---|---|---:|---:|---|---|
| combined | gbt | 390 | 20 | 0.968 ± 0.012 | 139.4103 ± 20.5980 |
| wbt_other_phase | gbt | 420 | 13 | 0.968 ± 0.013 | 142.0232 ± 17.2067 |
| wbt_other_phase | rf | 420 | 13 | 0.962 ± 0.016 | 168.1514 ± 31.1297 |
| combined | rf | 390 | 20 | 0.959 ± 0.017 | 174.0127 ± 28.8515 |
| combined | ridge | 390 | 20 | 0.911 ± 0.012 | 320.4316 ± 24.4755 |
| wbt_other_phase | ridge | 420 | 13 | 0.903 ± 0.021 | 344.0416 ± 22.2538 |
| geometry | gbt | 390 | 9 | 0.897 ± 0.015 | 317.1024 ± 30.0697 |
| geometry | rf | 390 | 9 | 0.897 ± 0.015 | 317.2446 ± 30.6259 |
| geometry | ridge | 390 | 9 | 0.897 ± 0.014 | 318.0668 ± 30.4607 |
