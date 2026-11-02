"""Original-file baseline: cutoff filtering, tie-preserving latest state, and history."""
import pandas as pd

TRANSACTION_COLUMNS = ['msno', 'payment_method_id', 'payment_plan_days',
    'plan_list_price', 'actual_amount_paid', 'is_auto_renew', 'transaction_date',
    'membership_expire_date', 'is_cancel']

def parse_date(series):
    return pd.to_datetime(series.astype('Int64').astype('string'),
                          format='%Y%m%d', errors='coerce')

def clean_members(labels, members, cutoff):
    """Retain all labels; clean fields without imputing unknowns or asserting snapshot timing."""
    assert labels.msno.notna().all() and labels.msno.is_unique
    assert labels.is_churn.notna().all() and labels.is_churn.isin([0, 1]).all()
    assert members.msno.notna().all() and members.msno.is_unique
    base = labels.merge(members, on='msno', how='left', validate='one_to_one', indicator=True)
    base['member_record_missing'] = base['_merge'].eq('left_only')
    base['age_clean'] = base.bd.where(base.bd.between(1, 100))
    base['age_missing_or_invalid'] = base.age_clean.isna()
    base['gender_clean'] = base.gender.fillna('unknown')
    base['registration_date'] = parse_date(base.registration_init_time)
    base['registration_after_cutoff'] = base.registration_date.gt(cutoff)
    base['registration_date_clean'] = base.registration_date.where(~base.registration_after_cutoff)
    base['tenure_days'] = (cutoff - base.registration_date_clean).dt.days
    return base

def scan_transactions(path, ids, cutoff, chunksize=500000):
    """One streaming pass. Count raw records, but deduplicate latest-state candidates only.

    No attempt is made to infer intraday ordering. All distinct same-day candidates
    are retained until ambiguity is classified. Future transaction rows are excluded.
    """
    cutoff_int = int(cutoff.strftime('%Y%m%d'))
    window_start = int((cutoff - pd.Timedelta(days=29)).strftime('%Y%m%d'))
    history = pd.DataFrame()
    latest = pd.DataFrame(columns=TRANSACTION_COLUMNS)
    raw_count = 0
    invalid_dates = 0
    earliest = None
    last_date = None
    for chunk in pd.read_csv(path, usecols=TRANSACTION_COLUMNS, chunksize=chunksize):
        raw_count += len(chunk)
        dates = parse_date(chunk.transaction_date)
        invalid_dates += int(dates.isna().sum())
        if dates.notna().any():
            lo, hi = dates.min(), dates.max()
            earliest = lo if earliest is None else min(earliest, lo)
            last_date = hi if last_date is None else max(last_date, hi)
        if dates.isna().any():
            raise ValueError('Invalid transaction dates; investigate before feature construction')
        relevant = chunk.loc[chunk.msno.isin(ids) & chunk.transaction_date.le(cutoff_int)].copy()
        if relevant.empty:
            continue
        if not relevant.is_cancel.isin([0, 1]).all():
            raise ValueError('Nonbinary cancellation flags')
        relevant['_recent'] = relevant.transaction_date.ge(window_start).astype(int)
        part = relevant.groupby('msno').agg(
            history_transaction_count=('transaction_date', 'size'),
            history_cancel_count=('is_cancel', 'sum'),
            history_first_transaction=('transaction_date', 'min'),
            transaction_count_30d=('_recent', 'sum'))
        history = pd.concat([history, part]).groupby(level=0, sort=False).agg({
            'history_transaction_count': 'sum', 'history_cancel_count': 'sum',
            'history_first_transaction': 'min', 'transaction_count_30d': 'sum'})
        chunk_max = relevant.groupby('msno', sort=False).transaction_date.transform('max')
        candidates = relevant.loc[relevant.transaction_date.eq(chunk_max), TRANSACTION_COLUMNS]
        latest = candidates.copy() if latest.empty else pd.concat([latest, candidates], ignore_index=True)
        maxima = latest.groupby('msno', sort=False).transaction_date.transform('max')
        latest = latest.loc[latest.transaction_date.eq(maxima)].copy()
    if history.empty:
        raise ValueError('No pre-cutoff transactions match supplied labels')
    history['history_first_transaction'] = parse_date(history.history_first_transaction)
    history['history_days_since_first_transaction'] = (cutoff - history.history_first_transaction).dt.days
    for col in ('history_transaction_count', 'history_cancel_count', 'transaction_count_30d'):
        history[col] = history[col].astype('int64')
    distinct = latest.drop_duplicates()
    counts = distinct.groupby('msno').size()
    tied_ids = counts[counts.gt(1)].index
    single = distinct.loc[distinct.msno.isin(counts[counts.eq(1)].index)].copy()
    # Ensure numeric columns retain original numeric types through chunk concatenation.
    for col in TRANSACTION_COLUMNS[1:]:
        single[col] = pd.to_numeric(single[col], errors='raise')
    single = single.rename(columns={c: 'latest_' + c for c in TRANSACTION_COLUMNS if c != 'msno'})
    audit = {'raw_transaction_rows': raw_count, 'earliest_transaction': str(earliest),
             'latest_transaction': str(last_date), 'invalid_transaction_dates': invalid_dates,
             'latest_candidate_rows': len(latest),
             'latest_identical_rows_removed': len(latest) - len(distinct),
             'ambiguous_subscribers': len(tied_ids)}
    return single, tied_ids, history, audit

def build_base(raw_dir, config):
    """Build baseline from train_v2 labels, members snapshot, and original transactions only."""
    cutoff = pd.Timestamp(config['cutoff'])
    labels = pd.read_csv(raw_dir / 'train_v2.csv', dtype={'msno': str})
    ids = set(labels.msno)
    pieces = []
    for chunk in pd.read_csv(raw_dir / 'members_v3.csv', chunksize=config['chunk_size']):
        pieces.append(chunk.loc[chunk.msno.isin(ids)].copy())
    members = pd.concat(pieces, ignore_index=True)
    base = clean_members(labels, members, cutoff)
    latest, tied, history, audit = scan_transactions(
        raw_dir / 'transactions.csv', ids, cutoff, config['chunk_size'])
    base = base.merge(latest, on='msno', how='left', validate='one_to_one')
    base = base.merge(history, left_on='msno', right_index=True, how='left', validate='one_to_one')
    base['transaction_count'] = base.history_transaction_count.fillna(0).astype('int64')
    base['latest_transaction_ambiguous'] = base.msno.isin(tied)
    base['transaction_history_missing'] = base.transaction_count.eq(0)
    for col in ('latest_transaction_date', 'latest_membership_expire_date'):
        base[col] = parse_date(base[col])
    base['days_to_expiry'] = (base.latest_membership_expire_date - cutoff).dt.days
    base['campaign_eligible'] = (
        base.latest_membership_expire_date.between(config['expiry_start'], config['expiry_end'])
        & ~base.latest_transaction_ambiguous & ~base.transaction_history_missing)
    assert base.msno.is_unique and len(base) == len(labels)
    assert base.latest_transaction_date.dropna().le(cutoff).all()
    audit.update({'labeled_subscribers': len(base),
                  'campaign_subscribers': int(base.campaign_eligible.sum()),
                  'missing_history': int(base.transaction_history_missing.sum()),
                  'post_cutoff_registration': int(base.registration_after_cutoff.sum())})
    base.index.name = "row_id"
    return base, audit
