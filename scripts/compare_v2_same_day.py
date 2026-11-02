"""Optional same-day comparison after audit_v2_overlap.py; does not change model inputs."""
from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.common import paths
config, project_paths = paths(ROOT)
raw_dir = project_paths['raw']
audit_path = project_paths['processed'] / 'v2_pre_cutoff_rows_absent_from_original.csv.gz'
if not audit_path.exists():
    raise SystemExit('Run python scripts/audit_v2_overlap.py first.')

# Historical v2 rows identified by the previous audit.
v2_extra = pd.read_csv(
    audit_path
)

keys = ["msno", "transaction_date"]
candidate_dates = pd.MultiIndex.from_frame(v2_extra[keys])
subscriber_ids = set(v2_extra["msno"])
matched_dates = set()
rows_scanned = 0

# Read only subscriber IDs and dates to keep memory use low.
for chunk in pd.read_csv(
    raw_dir / "transactions.csv",
    usecols=keys,
    chunksize=500_000,
):
    relevant = chunk.loc[chunk["msno"].isin(subscriber_ids), keys]

    matched_dates.update(
        candidate_dates.intersection(
            pd.MultiIndex.from_frame(relevant)
        ).tolist()
    )

    rows_scanned += len(chunk)
    if rows_scanned % 5_000_000 == 0:
        print(f"Scanned {rows_scanned:,} original rows...")

same_date = pd.Series(
    [key in matched_dates for key in candidate_dates],
    index=v2_extra.index,
)

summary = pd.DataFrame({
    "category": [
        "Same subscriber/date exists in original",
        "Subscriber/date absent from original",
    ],
    "v2_rows": [
        int(same_date.sum()),
        int((~same_date).sum()),
    ],
    "subscribers": [
        v2_extra.loc[same_date, "msno"].nunique(),
        v2_extra.loc[~same_date, "msno"].nunique(),
    ],
})

print("\nDiagnostic results:")
print(summary.to_string(index=False))
print("\nA subscriber can appear in both categories.")
# Uses v2_extra, same_date, raw_dir, and keys from the previous cell.
same_day_v2 = v2_extra.loc[same_date].copy()

fields = [
    "payment_method_id",
    "payment_plan_days",
    "plan_list_price",
    "actual_amount_paid",
    "is_auto_renew",
    "membership_expire_date",
    "is_cancel",
]

comparisons = []
same_day_ids = set(same_day_v2["msno"])

for chunk in pd.read_csv(
    raw_dir / "transactions.csv",
    usecols=keys + fields,
    chunksize=500_000,
):
    relevant = chunk.loc[chunk["msno"].isin(same_day_ids)]

    paired = same_day_v2.merge(
        relevant,
        on=keys,
        how="inner",
        suffixes=("_v2", "_original"),
    )

    if not paired.empty:
        comparisons.append(paired)

pairs = pd.concat(comparisons, ignore_index=True).drop_duplicates()

differences = pd.DataFrame({
    field: pairs[f"{field}_v2"].ne(pairs[f"{field}_original"])
    for field in fields
})

print(f"Distinct same-day row comparisons: {len(pairs):,}")

print("\nFields that differ:")
print(
    differences.sum()
    .sort_values(ascending=False)
    .rename("comparisons_with_difference")
    .to_string()
)

# Show examples without subscriber identifiers.
example_columns = ["transaction_date"]
for field in fields:
    example_columns.extend([f"{field}_original", f"{field}_v2"])

pairs[example_columns].head(10).to_csv(project_paths['processed'] / 'v2_same_day_examples.csv', index=False)
print('Example field comparisons saved under Data/processed/.')
