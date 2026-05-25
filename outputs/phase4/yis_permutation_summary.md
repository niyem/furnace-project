# Phase 4b: Years-in-Service Permutation Importance

Trained Random Forest to predict `years_in_service` with grouped 5-fold CV by stove.
Permutation importance computed on each held-out fold with 10 repeats; aggregated.

## Aggregated importance by feature group

If `wbt` group dominates → the model relies on functional signals (efficiency, firepower, burn rate, etc.) that could plausibly drift with wear → supports **real degradation** interpretation.

If `geometry` group dominates → geometry doesn't change with age, so the model is identifying format×year cohorts rather than wear → supports **cohort confound** interpretation.

| Group | Total importance | n features | Top single importance |
|---|---:|---:|---:|
| wbt | 0.9699 | 14 | 0.2242 |
| categorical | 0.0367 | 2 | 0.0367 |
| geometry | 0.0023 | 8 | 0.0006 |

## Top 15 features

| Rank | Feature | Group | Importance (mean ± std) |
|---:|---|---|---|
| 1 | `sfc_cold` | wbt | 0.2242 ± 0.0581 |
| 2 | `sfc_simmer` | wbt | 0.1733 ± 0.0165 |
| 3 | `eff_hot` | wbt | 0.1448 ± 0.0275 |
| 4 | `eff_cold` | wbt | 0.0805 ± 0.0170 |
| 5 | `eff_simmer` | wbt | 0.0740 ± 0.0123 |
| 6 | `tboil_hot` | wbt | 0.0530 ± 0.0117 |
| 7 | `sfc_hot` | wbt | 0.0502 ± 0.0191 |
| 8 | `format` | categorical | 0.0367 ± 0.0265 |
| 9 | `fp_simmer` | wbt | 0.0326 ± 0.0149 |
| 10 | `br_simmer` | wbt | 0.0276 ± 0.0144 |
| 11 | `tboil_cold` | wbt | 0.0254 ± 0.0106 |
| 12 | `fp_cold` | wbt | 0.0241 ± 0.0061 |
| 13 | `br_cold` | wbt | 0.0236 ± 0.0137 |
| 14 | `br_hot` | wbt | 0.0201 ± 0.0097 |
| 15 | `fp_hot` | wbt | 0.0167 ± 0.0037 |
