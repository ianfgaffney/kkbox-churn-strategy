# Local execution

## Setup

Use the repository root as the working directory. Put `train_v2.csv`, `transactions.csv`, and `members_v3.csv` in `Data/Raw/`, or change `raw_data_dir` in `config.json`. The optional audits additionally require `transactions_v2.csv`.

Install `requirements.txt` in a virtual environment and register its kernel:

```bash
python -m ipykernel install --user --name kkbox --display-name "Python (KKBox)"
python scripts/check_notebooks.py
python -m unittest discover -s tests -v
```

On macOS, a missing `libomp.dylib` error from LightGBM requires the OpenMP runtime, available through `brew install libomp`.

## Execute

Select the registered kernel in VS Code. Restart and run each notebook in order, or execute:

```bash
python scripts/run_all.py --kernel kkbox
```

Each notebook uses a fresh kernel and saved intermediate tables. Changes to input data or configuration require rebuilding downstream outputs.

Expected baseline counts: 970,960 labels; 941,518 campaign subscribers; 10,944 ambiguous latest states; 2,527 missing histories; 199 identical latest-state rows removed; 21 model features. Compare generated metrics with the committed aggregate tables. Investigate material differences rather than copying old results into new outputs.

## Optional release diagnostics

These are independent of the four-notebook pipeline:

```bash
python scripts/audit_v2_overlap.py
python scripts/compare_v2_same_day.py
```

The second script consumes the first script's saved unmatched rows. Candidate pairings do not prove transaction identity. Both scripts leave the modeling inputs unchanged.

## Record the environment

Run this using the same interpreter as the notebook kernel:

```bash
python scripts/capture_environment.py
```

The generated `requirements-local-lock.txt` is ignored by default because a local environment can contain unrelated packages or private installation paths. Review it before adding a portable, project-specific environment record. Do not substitute versions from a different machine. Current dependency ranges are not an exact lockfile.

## Outputs and Git

- `Data/processed/`: subscriber base, campaign checkpoint, and modeling table.
- `artifacts/`: model bundles, metadata, split membership, predictions, and selected subscriber lists.
- `reports/tables/` and `reports/figures/`: aggregate results suitable for review.

Keep subscriber-level data, models, and local backups out of Git. Preserve safe aggregate notebook outputs for readers; clear individual records and personal paths before committing. Load only model bundles you created or trust.
