import numpy as np
import pandas as pd

def strategy_frame(predictions):
    """Use saved subscriber-level predictions; unknown value excluded, known zero retained."""
    assert predictions.msno.is_unique and predictions.msno.notna().all()
    frame = predictions[['msno','is_churn','revenue_30d_proxy','predicted_churn_probability']].copy()
    assert frame.predicted_churn_probability.between(0, 1).all()
    frame = frame.dropna(subset=['revenue_30d_proxy']).copy()
    assert frame.revenue_30d_proxy.ge(0).all()
    frame['predicted_value_at_risk'] = frame.predicted_churn_probability * frame.revenue_30d_proxy
    frame['observed_churn_associated_value'] = frame.is_churn * frame.revenue_30d_proxy
    return frame

def select_policy(frame, capacity_fraction=0.1, save_rate=0.1, contact_cost=5.0, positive_only=True):
    """Fixed-cost/no-incentive policy; selection uses no outcomes."""
    if not 0 < capacity_fraction <= 1 or not 0 <= save_rate <= 1 or contact_cost < 0:
        raise ValueError('Invalid policy assumptions')
    ordered = frame.sort_values(['predicted_value_at_risk','msno'], ascending=[False, True])
    if positive_only:
        ordered = ordered.loc[save_rate * ordered.predicted_value_at_risk > contact_cost]
    return ordered.head(int(np.ceil(len(frame) * capacity_fraction)))
