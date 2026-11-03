# Validation record

## Full-data results

The author reported successfully executing all four notebooks locally. Committed aggregate tables record LightGBM test log loss 0.155379, ROC AUC 0.906778, and 67.54% top-decile capture. The positive-benefit policy selects 12,644 contacts with modeled net value NTD 53,660.89 under the 10% effectiveness and NTD 5 contact-cost assumptions.

The repository review reconciled these headline figures with the CSV exports. It did not independently rerun the complete raw KKBox dataset. The committed model and strategy notebooks now include saved execution outputs: all 13 model code cells and all 10 strategy code cells have execution counts, with no saved error outputs. Their displayed test metrics and policy results agree with the aggregate CSV exports at the reported precision. Notebook 02 still omits saved outputs. Aggregate results remain available in reports/tables/ and reports/figures/.

## Automated checks

- Three unit tests cover cutoff filtering, cross-chunk duplicates and same-day ambiguity; checkpoint roundtrips and feature exclusions; and outcome-independent selection with unknown and zero value.
- Notebook code cells pass syntax checks. Notebook files also pass schema validation.
- Cleanup validation checks relative documentation links and confirms the main notebooks no longer require the optional v2 audit output or a personal absolute path.
- The automated runner supports an explicit registered kernel name.

These checks do not establish full-data numerical reproducibility, prospective model accuracy, or causal campaign effectiveness.

## Earlier fixture checks

During development, notebooks 01–02 were exercised on constructed raw-data fixtures, and model/strategy code was exercised with synthetic data. Those checks tested pipeline behavior; synthetic metrics are not presented as KKBox results.

## Reproduction limits

The reported local environment used Python 3.9.6, pandas 2.3.3, and NumPy 2.0.2. Other successful local package versions have not yet been published as an exact dependency record. Capture them from that environment using scripts/capture_environment.py. Model outputs can vary with dependency versions, threading, and tie ordering.
