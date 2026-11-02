# Results recorded in the supplied notebook (not rerun by reviewer)

| Metric | Logistic regression | LightGBM |
|---|---:|---:|
| Test log loss | 0.1777 | 0.1554 |
| Test ROC AUC | 0.8581 | 0.9068 |
| Risk-ranked test top 10% churn capture | 64.54% | 67.54% |
| Risk-ranked test top 10% lift | 6.45 | 6.75 |

LightGBM best iteration: 1131. Validation log loss 0.1546, AUC 0.9066.

| Test policy | Contacts | Cost | Projected protected value | Projected net |
|---|---:|---:|---:|---:|
| Fill capacity, value-ranked | 18831 | 94155 | 141817.76 | 47662.76 |
| Positive benefit only | 12644 | 63220 | 116880.89 | 53660.89 |

Assumptions: relative churn reduction 10%, cost/contact 5, no incentive/service cost,
30-day-equivalent payment proxy. Figures are in dataset units pending metadata verification.

Value-ranked full-capacity test observed churn-associated value 1430657.27, predicted
1418177.59 (-0.87%). Positive-only observed 1161347.52, predicted 1168808.91 (+0.64%).
Positive-only captured 55.32% of churn-associated value and 55.40% of churners.
Aggregate calibration is not evidence of intervention efficacy or individual accuracy.

Pilot sizes at model-estimated 65.85% control churn: 3327 per arm for 5% relative reduction,
847 per arm for 10%, 218 per arm for 20% (two-sided 5% alpha, 80% power, normal approximation).
Rounding the middle case to 1000/arm is a proposal, not a demonstrated optimum.
