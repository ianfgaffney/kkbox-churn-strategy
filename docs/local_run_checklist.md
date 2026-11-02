# Local execution checklist

1. Extract the project into a separate folder. Leave the original notebook and raw data intact.
2. Edit config.json: set raw_data_dir to your existing folder, e.g.
   /Users/iangaffney/Desktop/Internship!/KKbox/Data/Raw
   (Forward slashes in JSON need no escaping.) This is the only machine-specific edit.
3. Select the working Python environment in VS Code. Do not reinstall existing packages
   unnecessarily. requirements.txt records known versions and proposed compatibility ranges,
   not a tested exact lock. The prior Python 3.9 environment is retained for reproduction,
   not recommended as a long-term supported environment. Homebrew libomp is a Mac prerequisite
   if LightGBM cannot import. No additional shap package is needed.
4. From the extracted project root run:
   python scripts/check_notebooks.py
   python -m unittest discover -s tests -v
5. Run notebooks 01, 02, 03, 04 in order, each from a fresh kernel. Either use VS Code's
   Restart Kernel and Run All for each, or install nbformat/nbclient and run
   python scripts/run_all.py using a registered python3 kernel for this environment.
   Data/config changes require rebuilding downstream notebooks; stale checkpoints are not valid.
6. Compare EDA: 970960 labels, 941518 campaign subscribers, 10944 ambiguous subscribers,
   2527 no-history subscribers, 199 identical latest-state rows removed. Feature matrix
   should be (941518, 21). Investigate count differences before interpreting model scores.
7. Check full-data results against reports/source_snapshot/source_results.md. Tiny differences
   from dependency versions, threading, or deterministic tie ordering are possible. Material
   differences require investigation; do not copy old output over new results.
8. Run python scripts/audit_v2_overlap.py; inspect reports/tables/v2_overlap_audit.json.
   Send that JSON and any failures back for review. Do not automatically append late-released
   historical records without a data-availability rationale.
9. Run python scripts/capture_environment.py from the notebook's actual interpreter;
   inspect the lockfile before committing. Check artifacts/metadata.json versions.
10. Read docs/review.md and close or disclose each limitation. Currency, source rules, label
    timing, and definition of available-at-cutoff remain required documentation work.
11. Before GitHub: keep Data/ and artifacts/ ignored; clear notebook outputs containing
    subscriber IDs, paths, or raw rows. Aggregate CSVs and charts may be published only in
    accordance with Kaggle terms. No GitHub repository was created by this review.

## Files generated on your Mac
- Data/processed/subscriber_base.csv.gz, campaign_eda_checkpoint.csv.gz, modeling_table.csv.gz
- artifacts/logistic_pipeline.joblib, lightgbm_bundle.joblib, lightgbm.txt, metadata.json
- artifacts/split_membership.csv.gz and validation/test_predictions.csv.gz
- reports/tables/*.csv and reports/figures/*.png

Only load joblib model bundles that you created or trust. CSV checkpoints preserve dates,
flags and row IDs through the supplied loader. The original exploration checkpoint lacked
later history features; use notebook 02's modeling_table for modeling.
