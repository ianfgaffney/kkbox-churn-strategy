"""Exact row-set comparison; does not silently append historical records or rebuild models.

Run from project root: python scripts/audit_v2_overlap.py
Keeps pre-cutoff v2 rows in memory (about 361k in the supplied results), streams v1.
Distinct matching uses all nine fields; a match does not prove publication-time availability.
"""
from pathlib import Path
import sys, json
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.common import paths, load_frame
from src.data import TRANSACTION_COLUMNS, parse_date
config, p = paths(ROOT)
cutoff = int(pd.Timestamp(config['cutoff']).strftime('%Y%m%d'))
old_parts = []
months = pd.Series(dtype='int64')
for chunk in pd.read_csv(p['raw'] / 'transactions_v2.csv', usecols=TRANSACTION_COLUMNS, chunksize=config['chunk_size']):
    dates = parse_date(chunk.transaction_date)
    if dates.isna().any():
        raise ValueError('Invalid v2 transaction dates')
    months = months.add(dates.dt.to_period('M').value_counts(), fill_value=0)
    old_parts.append(chunk.loc[chunk.transaction_date.le(cutoff), TRANSACTION_COLUMNS])
old = pd.concat(old_parts, ignore_index=True)
unique = old.drop_duplicates()
wanted = set(unique.itertuples(index=False, name=None))
ids = set(unique.msno)
matched = set()
for chunk in pd.read_csv(p['raw'] / 'transactions.csv', usecols=TRANSACTION_COLUMNS, chunksize=config['chunk_size']):
    subset = chunk.loc[chunk.msno.isin(ids) & chunk.transaction_date.le(cutoff), TRANSACTION_COLUMNS]
    matched.update(wanted.intersection(subset.itertuples(index=False, name=None)))
unmatched = wanted - matched
new = pd.DataFrame(list(unmatched), columns=TRANSACTION_COLUMNS)
labels = pd.read_csv(p['raw'] / 'train_v2.csv', usecols=['msno'])
new_labeled = new.loc[new.msno.isin(set(labels.msno))].copy()
report = {'pre_cutoff_v2_rows': len(old), 'distinct_pre_cutoff_v2_rows': len(unique),
          'exact_distinct_matches_in_original': len(matched),
          'distinct_rows_absent_from_original': len(unmatched),
          'distinct_labeled_rows_absent_from_original': len(new_labeled),
          'labeled_subscribers_with_absent_rows': int(new_labeled.msno.nunique())}
base_path = p['processed'] / 'subscriber_base.csv.gz'
if base_path.exists():
    base = load_frame(base_path)
    joined = new_labeled.merge(base[['msno','latest_transaction_date','campaign_eligible']], on='msno', validate='many_to_one')
    new_dates = parse_date(joined.transaction_date)
    affects = joined.latest_transaction_date.isna() | new_dates.ge(joined.latest_transaction_date)
    report['subscribers_with_new_rows_at_or_after_selected_latest_or_no_selected_state'] = int(joined.loc[affects, 'msno'].nunique())
    report['campaign_subscribers_with_absent_v2_history_rows'] = int(joined.loc[joined.campaign_eligible, 'msno'].nunique())
new_labeled.to_csv(p['processed'] / 'v2_pre_cutoff_rows_absent_from_original.csv.gz', index=False)
months.sort_index().astype(int).rename('rows').to_csv(p['tables'] / 'v2_month_counts.csv')
(p['tables'] / 'v2_overlap_audit.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
