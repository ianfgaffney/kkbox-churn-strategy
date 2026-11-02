# Validation performed during review

- All 45 code cells parse successfully; all four notebooks pass nbformat schema validation.
- Three unit tests pass: cutoff/tie/duplicate chunk invariance; date/boolean/feature checkpoint roundtrip and leakage allowlist; outcome-independent policy selection and missing-value handling.
- Notebooks 01 and 02 executed on constructed raw CSV fixtures, including cross-chunk duplicates, same-day conflicting records, future transactions, absent members, and post-cutoff registration dates.
- Notebook 03 executed with real logistic-regression and LightGBM fitting on 30,000 synthetic subscribers. Models, split identities, category definitions and prediction artifacts were saved.
- Notebook 04 executed in a fresh namespace from those saved synthetic-model predictions, including targeting, scenarios, sample sizing, and plot/table exports.
- The v2 audit passed a constructed exact-overlap/duplicate/future-date fixture.
- Synthetic runs used fresh Python namespaces for each notebook, not a full Jupyter kernel orchestration test. No synthetic metrics are presented as KKBox results.
- Full KKBox data execution and source audit were NOT performed; data was not attached. Runtime and original Mac versions differ. Historical figures in README come from supplied notebook outputs.
- LightGBM 4.7 emitted a deprecation warning for eval_set. That API remains functional and preserves compatibility with the earlier 4.x installation; it was not a training error.

## Review runtime

Python 3.12.14.

```json
{
  "pandas": "2.2.3",
  "numpy": "2.3.5",
  "scikit-learn": "1.8.0",
  "lightgbm": "4.7.0",
  "matplotlib": "3.10.8",
  "joblib": "1.5.3",
  "nbformat": "5.11.1",
  "nbclient": "0.11.0"
}
```

These are review-runtime versions, not the original Mac environment or an exact recommended lockfile.
