# Feature Dictionary

## Raw geometric features (from STOVE_DIMS)

| Feature | Units | Definition |
|---|---|---|
| `height_cm` | cm | Total stove height |
| `outside_d_cm` | cm | Stove outer diameter |
| `chamber_d_cm` | cm | Combustion-chamber inner diameter |
| `chamber_depth_cm` | cm | Combustion-chamber depth |
| `inlet_w_cm`, `inlet_h_cm` | cm | Air-inlet dimensions |
| `inlet_area_cm2` | cm² | Derived: inlet width × height |
| `chamber_volume_cm3` | cm³ | Derived: π·(d/2)²·depth |

## Physics-engineered features (added in Phase 2)

| Feature | Units | Definition | Physical interpretation |
|---|---|---|---|
| `aspect_ratio` | — | `height_cm / outside_d_cm` | Tall vs. squat geometry. Tall stoves may have better natural-draft pull. |
| `chamber_aspect` | — | `chamber_depth_cm / chamber_d_cm` | Combustion-chamber shape. Affects flame envelope and radiative coupling to the pot. |
| `inlet_per_volume` | cm⁻¹ | `inlet_area_cm2 / chamber_volume_cm3` | Airflow intensity. Higher = more O₂ per unit combustion volume. |
| `chamber_surface_cm2` | cm² | `π·d·depth + π·(d/2)²` | Wall + base surface area of the chamber. Drives radiative + conductive heat loss. |
| `surface_to_volume` | cm⁻¹ | `chamber_surface_cm2 / chamber_volume_cm3` | Loss-vs-storage ratio. Higher = more heat loss per unit fuel-heat-release potential. |
| `wall_thickness_cm` | cm | `(outside_d_cm - chamber_d_cm) / 2` | Clay wall thickness. Proxy for thermal insulation between chamber and ambient. |
