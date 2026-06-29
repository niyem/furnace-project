# Phase 1: Predictability Landscape

Grouped 5-fold CV by stove identity (`src_path`). Mean R² ± std across folds. MAE in target units.

## Target: `br_cold`

| Features | Model | n | n_feat | R² (mean ± std) | MAE (mean ± std) |
|---|---|---:|---:|---|---|
| combined | gbt | 420 | 18 | 0.964 ± 0.015 | 0.7255 ± 0.1058 |
| combined | rf | 420 | 18 | 0.957 ± 0.016 | 0.8323 ± 0.1270 |
| wbt_other_phase | gbt | 450 | 11 | 0.957 ± 0.013 | 0.7777 ± 0.0730 |
| wbt_other_phase | rf | 450 | 11 | 0.957 ± 0.014 | 0.8311 ± 0.0849 |
| combined | ridge | 420 | 18 | 0.926 ± 0.009 | 1.2794 ± 0.0786 |
| wbt_other_phase | ridge | 450 | 11 | 0.925 ± 0.013 | 1.2408 ± 0.1039 |
| geometry | gbt | 420 | 9 | 0.864 ± 0.024 | 1.6880 ± 0.1365 |
| geometry | rf | 420 | 9 | 0.864 ± 0.024 | 1.6882 ± 0.1364 |
| geometry | ridge | 420 | 9 | 0.864 ± 0.024 | 1.6874 ± 0.1343 |

## Target: `br_hot`

| Features | Model | n | n_feat | R² (mean ± std) | MAE (mean ± std) |
|---|---|---:|---:|---|---|
| combined | gbt | 420 | 18 | 0.959 ± 0.012 | 1.1609 ± 0.1443 |
| combined | rf | 420 | 18 | 0.948 ± 0.013 | 1.3988 ± 0.1594 |
| wbt_other_phase | gbt | 450 | 11 | 0.937 ± 0.049 | 1.2539 ± 0.2572 |
| wbt_other_phase | rf | 450 | 11 | 0.932 ± 0.037 | 1.4409 ± 0.2182 |
| wbt_other_phase | ridge | 450 | 11 | 0.912 ± 0.022 | 1.9311 ± 0.2680 |
| combined | ridge | 420 | 18 | 0.911 ± 0.012 | 1.9828 ± 0.2339 |
| geometry | gbt | 420 | 9 | 0.837 ± 0.013 | 2.6350 ± 0.1594 |
| geometry | rf | 420 | 9 | 0.837 ± 0.013 | 2.6352 ± 0.1592 |
| geometry | ridge | 420 | 9 | 0.837 ± 0.014 | 2.6332 ± 0.1591 |

## Target: `br_simmer`

| Features | Model | n | n_feat | R² (mean ± std) | MAE (mean ± std) |
|---|---|---:|---:|---|---|
| wbt_other_phase | gbt | 420 | 12 | 0.968 ± 0.015 | 0.2929 ± 0.0340 |
| combined | gbt | 390 | 19 | 0.966 ± 0.018 | 0.2963 ± 0.0633 |
| wbt_other_phase | rf | 420 | 12 | 0.962 ± 0.017 | 0.3472 ± 0.0514 |
| combined | rf | 390 | 19 | 0.961 ± 0.019 | 0.3553 ± 0.0532 |
| combined | ridge | 390 | 19 | 0.910 ± 0.011 | 0.6600 ± 0.0522 |
| wbt_other_phase | ridge | 420 | 12 | 0.903 ± 0.021 | 0.6932 ± 0.0468 |
| geometry | gbt | 390 | 9 | 0.897 ± 0.015 | 0.6385 ± 0.0605 |
| geometry | rf | 390 | 9 | 0.897 ± 0.015 | 0.6387 ± 0.0617 |
| geometry | ridge | 390 | 9 | 0.897 ± 0.014 | 0.6404 ± 0.0613 |

## Target: `eff_cold`

| Features | Model | n | n_feat | R² (mean ± std) | MAE (mean ± std) |
|---|---|---:|---:|---|---|
| combined | gbt | 420 | 18 | 0.984 ± 0.008 | 0.0024 ± 0.0004 |
| combined | rf | 420 | 18 | 0.982 ± 0.004 | 0.0028 ± 0.0004 |
| wbt_other_phase | gbt | 450 | 11 | 0.979 ± 0.010 | 0.0027 ± 0.0003 |
| wbt_other_phase | rf | 450 | 11 | 0.979 ± 0.008 | 0.0029 ± 0.0004 |
| combined | ridge | 420 | 18 | 0.975 ± 0.007 | 0.0035 ± 0.0004 |
| wbt_other_phase | ridge | 450 | 11 | 0.974 ± 0.012 | 0.0034 ± 0.0006 |
| geometry | gbt | 420 | 9 | 0.041 ± 0.041 | 0.0171 ± 0.0016 |
| geometry | rf | 420 | 9 | 0.041 ± 0.042 | 0.0170 ± 0.0016 |
| geometry | ridge | 420 | 9 | 0.041 ± 0.039 | 0.0171 ± 0.0015 |

## Target: `eff_combined`

| Features | Model | n | n_feat | R² (mean ± std) | MAE (mean ± std) |
|---|---|---:|---:|---|---|
| wbt_other_phase | gbt | 450 | 13 | 0.957 ± 0.017 | 0.0051 ± 0.0005 |
| combined | gbt | 420 | 20 | 0.955 ± 0.018 | 0.0050 ± 0.0004 |
| combined | rf | 420 | 20 | 0.941 ± 0.032 | 0.0056 ± 0.0005 |
| wbt_other_phase | rf | 450 | 13 | 0.935 ± 0.029 | 0.0058 ± 0.0004 |
| wbt_other_phase | ridge | 450 | 13 | 0.794 ± 0.019 | 0.0128 ± 0.0008 |
| combined | ridge | 420 | 20 | 0.785 ± 0.017 | 0.0136 ± 0.0009 |
| geometry | rf | 420 | 9 | 0.012 ± 0.052 | 0.0225 ± 0.0006 |
| geometry | ridge | 420 | 9 | 0.012 ± 0.048 | 0.0227 ± 0.0005 |
| geometry | gbt | 420 | 9 | 0.011 ± 0.054 | 0.0225 ± 0.0006 |

## Target: `eff_hot`

| Features | Model | n | n_feat | R² (mean ± std) | MAE (mean ± std) |
|---|---|---:|---:|---|---|
| combined | gbt | 420 | 18 | 0.984 ± 0.004 | 0.0027 ± 0.0002 |
| wbt_other_phase | gbt | 450 | 11 | 0.984 ± 0.008 | 0.0027 ± 0.0004 |
| combined | rf | 420 | 18 | 0.982 ± 0.005 | 0.0030 ± 0.0003 |
| wbt_other_phase | rf | 450 | 11 | 0.981 ± 0.009 | 0.0030 ± 0.0004 |
| combined | ridge | 420 | 18 | 0.975 ± 0.006 | 0.0038 ± 0.0004 |
| wbt_other_phase | ridge | 450 | 11 | 0.974 ± 0.011 | 0.0037 ± 0.0005 |
| geometry | gbt | 420 | 9 | 0.043 ± 0.044 | 0.0180 ± 0.0019 |
| geometry | rf | 420 | 9 | 0.043 ± 0.044 | 0.0179 ± 0.0019 |
| geometry | ridge | 420 | 9 | 0.043 ± 0.043 | 0.0180 ± 0.0018 |

## Target: `eff_simmer`

| Features | Model | n | n_feat | R² (mean ± std) | MAE (mean ± std) |
|---|---|---:|---:|---|---|
| wbt_other_phase | gbt | 450 | 12 | 0.718 ± 0.076 | 0.0344 ± 0.0042 |
| combined | gbt | 420 | 19 | 0.713 ± 0.083 | 0.0358 ± 0.0054 |
| combined | rf | 420 | 19 | 0.688 ± 0.104 | 0.0353 ± 0.0059 |
| wbt_other_phase | rf | 450 | 12 | 0.686 ± 0.111 | 0.0332 ± 0.0063 |
| wbt_other_phase | ridge | 450 | 12 | 0.521 ± 0.129 | 0.0641 ± 0.0040 |
| combined | ridge | 420 | 19 | 0.518 ± 0.097 | 0.0668 ± 0.0036 |
| geometry | gbt | 420 | 9 | 0.004 ± 0.052 | 0.0825 ± 0.0035 |
| geometry | rf | 420 | 9 | 0.004 ± 0.050 | 0.0819 ± 0.0036 |
| geometry | ridge | 420 | 9 | 0.004 ± 0.049 | 0.0826 ± 0.0036 |

## Target: `fp_cold`

| Features | Model | n | n_feat | R² (mean ± std) | MAE (mean ± std) |
|---|---|---:|---:|---|---|
| combined | gbt | 420 | 18 | 0.964 ± 0.015 | 360.2542 ± 52.3478 |
| combined | rf | 420 | 18 | 0.957 ± 0.016 | 412.5468 ± 63.2159 |
| wbt_other_phase | gbt | 450 | 11 | 0.957 ± 0.013 | 386.2071 ± 36.2303 |
| wbt_other_phase | rf | 450 | 11 | 0.957 ± 0.014 | 413.1649 ± 41.8661 |
| combined | ridge | 420 | 18 | 0.926 ± 0.009 | 635.4562 ± 39.0608 |
| wbt_other_phase | ridge | 450 | 11 | 0.925 ± 0.013 | 616.2454 ± 51.5862 |
| geometry | gbt | 420 | 9 | 0.864 ± 0.024 | 838.3633 ± 67.7859 |
| geometry | rf | 420 | 9 | 0.864 ± 0.024 | 838.4567 ± 67.7251 |
| geometry | ridge | 420 | 9 | 0.864 ± 0.024 | 838.0546 ± 66.6810 |

## Target: `fp_hot`

| Features | Model | n | n_feat | R² (mean ± std) | MAE (mean ± std) |
|---|---|---:|---:|---|---|
| combined | gbt | 420 | 18 | 0.959 ± 0.012 | 575.5448 ± 70.1937 |
| combined | rf | 420 | 18 | 0.948 ± 0.014 | 694.1461 ± 79.8659 |
| wbt_other_phase | gbt | 450 | 11 | 0.937 ± 0.049 | 624.0323 ± 126.4348 |
| wbt_other_phase | rf | 450 | 11 | 0.932 ± 0.036 | 716.0112 ± 109.4317 |
| wbt_other_phase | ridge | 450 | 11 | 0.912 ± 0.022 | 959.0963 ± 133.0825 |
| combined | ridge | 420 | 18 | 0.911 ± 0.012 | 984.8018 ± 116.1543 |
| geometry | gbt | 420 | 9 | 0.837 ± 0.013 | 1308.7265 ± 79.1606 |
| geometry | rf | 420 | 9 | 0.837 ± 0.013 | 1308.8126 ± 79.0894 |
| geometry | ridge | 420 | 9 | 0.837 ± 0.014 | 1307.8187 ± 79.0368 |

## Target: `fp_simmer`

| Features | Model | n | n_feat | R² (mean ± std) | MAE (mean ± std) |
|---|---|---:|---:|---|---|
| wbt_other_phase | gbt | 420 | 12 | 0.968 ± 0.015 | 145.4928 ± 16.9196 |
| combined | gbt | 390 | 19 | 0.966 ± 0.018 | 146.8109 ± 31.6217 |
| wbt_other_phase | rf | 420 | 12 | 0.962 ± 0.017 | 172.8434 ± 24.4204 |
| combined | rf | 390 | 19 | 0.961 ± 0.019 | 177.0997 ± 26.2553 |
| combined | ridge | 390 | 19 | 0.910 ± 0.011 | 327.7807 ± 25.9304 |
| wbt_other_phase | ridge | 420 | 12 | 0.903 ± 0.021 | 344.2813 ± 23.2329 |
| geometry | gbt | 390 | 9 | 0.897 ± 0.015 | 317.1024 ± 30.0697 |
| geometry | rf | 390 | 9 | 0.897 ± 0.015 | 317.2446 ± 30.6259 |
| geometry | ridge | 390 | 9 | 0.897 ± 0.014 | 318.0668 ± 30.4607 |
