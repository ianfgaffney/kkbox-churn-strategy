# Methodology and limitations

## Prediction setup

Transaction features use `transactions.csv` through February 28, 2017. The target is the supplied March-period label in `train_v2.csv`. Campaign eligibility requires a latest unambiguous pre-cutoff state with a March expiry. Supplied labels were not independently reconstructed against each selected expiry date; the campaign cohort is a subset of the supplied label population.

The [competition host's explanation](https://www.kaggle.com/competitions/kkbox-churn-prediction-challenge/discussion/43622) defines churn by failure to renew within 30 days after expiry. [Databricks' implementation](https://www.databricks.com/notebooks/churn/1-data-preparation.html) discusses the label periods and the more complicated expiry-window rules. These references support the broad setup, not a subscriber-by-subscriber verification of labels.

## Transaction release choice

Kaggle describes the original file as covering transactions through February 28 and the refreshed v2 file through March 31. The overlap audit found 361,187 pre-cutoff v2 rows without exact original-file matches, including 170,132 rows for labeled subscribers. They affect 89,099 subscribers in the campaign cohort.

Among unmatched labeled v2 rows, 163,881 have subscriber/date combinations absent from the original; 6,251 have same-day original records. The latter produce 38,172 candidate pairings, all with differing expiry dates. These are not proven one-to-one transaction matches. Neither old transaction dates nor field differences establish when values became available. The baseline therefore excludes v2 features rather than automatically combining releases.

Run the optional audit and same-day comparison separately from the modeling pipeline. They do not modify model inputs.

## Missingness and eligibility

The original label population contains 970,960 subscribers. There are 10,944 ambiguous latest states and 2,527 subscribers without original-file history. The March-expiry campaign cohort contains 941,518 subscribers. Exact latest-date duplicates are collapsed for state selection; history features count original records, including duplicates.

Invalid ages are masked. Post-cutoff registrations are masked when deriving tenure, but this does not establish historical availability of the other member fields. Missing or ambiguous states, stale plans, zero payments, and zero-duration plans require explicit coverage reporting rather than automatic interpretation as errors.

## Evaluation

The model uses a 21-feature allowlist that excludes subscriber IDs, labels, and outcome-weighted revenue. Logistic preprocessing and LightGBM category definitions are fitted on training data. Early stopping uses validation data. Predictions are saved with subscriber and row identifiers before strategy evaluation.

Subscribers are split within one period. Full-cohort EDA preceded splitting, and model test results were inspected before policy development was complete. No future-month performance or prospective campaign effectiveness is claimed. SHAP explains model output in log-odds, not causal effects.

## Value and intervention assumptions

All money is in NTD. Actual payment divided by plan days and multiplied by 30 is a standardized historical payment proxy, not recognized revenue, MRR, margin, or guaranteed future revenue. Known zero payments retain zero value; nonpositive plan duration yields unknown normalized value.

Uniform effectiveness and contact cost underpin the scenario rule. Agreement between predicted and observed churn-associated value does not validate an intervention effect. A randomized pilot must measure incremental retention, payment revenue, costs, and guardrails. A churn-powered sample-size calculation does not establish power for economic outcomes.

## Operations

The historical analysis scores once at February 28. The proposed seven-days-before-expiry workflow requires features reconstructed and evaluated at those later scoring dates. Verified payment-failure events and consent/contactability records would be required for operational deployment; the current files do not supply them.
