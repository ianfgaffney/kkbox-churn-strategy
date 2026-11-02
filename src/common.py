import json
from pathlib import Path
import pandas as pd

def paths(root):
    """Resolve project paths using one editable config, with no personal path in code."""
    root = Path(root)
    config = json.loads((root / 'config.json').read_text())
    raw = Path(config['raw_data_dir']).expanduser()
    if not raw.is_absolute():
        raw = root / raw
    p = {'raw': raw, 'processed': root / 'Data' / 'processed',
         'figures': root / 'reports' / 'figures', 'tables': root / 'reports' / 'tables',
         'artifacts': root / 'artifacts'}
    for key in ('processed', 'figures', 'tables', 'artifacts'):
        p[key].mkdir(parents=True, exist_ok=True)
    return config, p

def save_frame(frame, path):
    """Persist row identity separately from subscriber identity for exact split recreation."""
    frame.to_csv(path, index=True, index_label='row_id', compression='infer')

def load_frame(path):
    """Read checkpoints and explicitly restore dates and boolean fields."""
    frame = pd.read_csv(path, index_col='row_id', dtype={'msno': str})
    for col in ('latest_transaction_date', 'latest_membership_expire_date',
                'registration_date', 'registration_date_clean', 'history_first_transaction'):
        if col in frame:
            frame[col] = pd.to_datetime(frame[col], errors='raise')
    for col in ('campaign_eligible', 'latest_transaction_ambiguous',
                'transaction_history_missing', 'member_record_missing',
                'registration_after_cutoff', 'age_missing_or_invalid', 'recency_exceeds_plan'):
        if col in frame:
            if frame[col].isna().any():
                raise ValueError('Missing boolean flag: ' + col)
            mapped = frame[col].astype(str).str.lower().map({'true': True, 'false': False})
            if mapped.isna().any():
                raise ValueError('Invalid boolean flag: ' + col)
            frame[col] = mapped.astype(bool)
    assert frame.index.is_unique
    if 'msno' in frame:
        assert frame.msno.notna().all() and frame.msno.is_unique
    return frame
