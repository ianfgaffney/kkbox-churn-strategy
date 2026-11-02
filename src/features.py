import numpy as np
import pandas as pd
NUMERIC_FEATURES = [
    "latest_payment_plan_days",
    "latest_plan_list_price",
    "latest_actual_amount_paid",
    "days_to_expiry",
    "days_since_latest_transaction",
    "history_transaction_count",
    "history_cancel_count",
    "history_days_since_first_transaction",
    "transaction_count_30d",
    "tenure_days",
    "age_clean",
    "discount_depth"
]

CATEGORICAL_FEATURES = [
    "latest_payment_method_id",
    "latest_is_auto_renew",
    "latest_is_cancel",
    "city",
    "registered_via",
    "gender_clean",
    "member_record_missing",
    "age_missing_or_invalid",
    "recency_exceeds_plan"
]


def add_features(campaign, cutoff):
    """Add only pre-cutoff features and a payment proxy; no outcome-weighted fields."""
    frame = campaign.copy()
    frame['discount_depth'] = 1 - frame.latest_actual_amount_paid / frame.latest_plan_list_price.where(frame.latest_plan_list_price.gt(0))
    frame['revenue_30d_proxy'] = frame.latest_actual_amount_paid / frame.latest_payment_plan_days.where(frame.latest_payment_plan_days.gt(0)) * 30
    frame['days_since_latest_transaction'] = (cutoff - frame.latest_transaction_date).dt.days
    frame['recency_exceeds_plan'] = frame.days_since_latest_transaction.gt(frame.latest_payment_plan_days)
    assert frame.msno.notna().all() and frame.msno.is_unique
    assert frame.latest_transaction_date.le(cutoff).all()
    for col in ('history_transaction_count', 'history_cancel_count', 'transaction_count_30d', 'history_days_since_first_transaction'):
        assert frame[col].notna().all(), col
        assert frame[col].ge(0).all(), col
    assert frame.transaction_count_30d.le(frame.history_transaction_count).all()
    return frame.drop(columns=['churned_revenue_30d_proxy'], errors='ignore')

def model_inputs(frame):
    """An explicit allowlist prevents outcome-derived values and IDs entering the model."""
    X = frame[NUMERIC_FEATURES + CATEGORICAL_FEATURES].copy()
    for col in CATEGORICAL_FEATURES:
        # Stable encoding across CSV round trips: numeric codes stay float strings.
        if col in ('latest_payment_method_id','latest_is_auto_renew','latest_is_cancel','city','registered_via'):
            X[col] = pd.to_numeric(X[col], errors='raise').astype(float)
        X[col] = X[col].astype('string').fillna('Unknown').astype(str)
    assert not np.isinf(X[NUMERIC_FEATURES].to_numpy(dtype=float)).any()
    y = frame.is_churn.astype('int64')
    assert y.isin([0, 1]).all()
    return X, y
