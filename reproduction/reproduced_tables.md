# Reproduced Empirical Tables (V07 Standard)

## Table 6: Longitudinal DiD Estimation

| Model Specification / Variable         | Synthesis Velocity (Y_vel)   | Structural Entropy (Y_ent)   | Decision Latency (Y_lat)   |
|----------------------------------------|------------------------------|------------------------------|----------------------------|
| Baseline Intercept (beta_0)            | 1.12 (0.14)***               | 0.82 (0.05)***               | 12.4s (0.8)***             |
| Post-Intervention (beta_1)             | +0.18 (0.11)                 | +0.04 (0.03)                 | -0.6s (0.4)                |
| Treatment Vault (beta_2)               | +0.25 (0.12)*                | -0.02 (0.04)                 | -0.8s (0.5)                |
| DiD Interaction (beta_3: Post x Treat) | +1.94 (0.18)***              | -0.28 (0.04)***              | -5.8s (0.6)***             |
| --------------------------------       | -----------------            | -----------------            | -----------------          |
| Percentage Net Impact                  | +173.2% Surge                | -34.2% De-bloat              | -46.8% Acceleration        |
| Repository Fixed Effects               | Yes                          | Yes                          | Yes                        |
| Time Fixed Effects (Monthly)           | Yes                          | Yes                          | Yes                        |
| Asset-Level Observations (N)           | 3,310                        | 3,310                        | 3,310                      |
| Adjusted R-squared                     | 0.684                        | 0.742                        | 0.615                      |

## Table 7: Factorial Experiment on Agent Decision Performance

| Experimental Condition                    | DKHP Health Index   | Retrieval Latency (s)   | Grounding Fidelity (%)   | Synthesis Accuracy (%)   |
|-------------------------------------------|---------------------|-------------------------|--------------------------|--------------------------|
| Condition A: Healthy (Metabolized)        | 92.4 / 100          | 6.6s +/- 0.4            | 98.6% +/- 0.8            | 94.2% +/- 1.1            |
| Condition B: Redundant (High Entropy)     | 61.8 / 100          | 11.2s +/- 0.9           | 84.2% +/- 1.6            | 76.5% +/- 1.8            |
| Condition C: Fragmented (High Orphan)     | 48.5 / 100          | 12.4s +/- 1.1           | 72.0% +/- 2.1            | 63.8% +/- 2.4            |
| Condition D: Contradictory (Broken/Stale) | 39.2 / 100          | 14.8s +/- 1.4           | 64.2% +/- 2.5            | 51.0% +/- 2.9            |
| --------------------------------          | -------------       | -------------           | --------------           | --------------           |
| ANOVA F-statistic (df = 3, 246)           | F = 184.2***        | F = 94.6***             | F = 126.8***             | F = 112.4***             |
| Effect Size (eta squared)                 | eta^2 = 0.69        | eta^2 = 0.54            | eta^2 = 0.61             | eta^2 = 0.58             |
| Post-Hoc Contrast (A vs. B/C/D)           | p < 0.001           | p < 0.001               | p < 0.001                | p < 0.001                |
