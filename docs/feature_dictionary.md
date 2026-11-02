# Feature dictionary

All monetary fields remain in original dataset units. Latest means latest transaction date before or on cutoff, with all distinct same-day ties excluded from campaign eligibility.

| Feature | Definition |
|---|---|
| latest_payment_plan_days | Nominal plan duration in latest unambiguous record |
| latest_plan_list_price | Latest recorded list price |
| latest_actual_amount_paid | Latest recorded payment |
| days_to_expiry | Recorded expiry minus fixed cutoff, in days |
| days_since_latest_transaction | Cutoff minus latest known transaction date |
| history_transaction_count | Original-file record count through cutoff; duplicates retained |
| history_cancel_count | Sum of is_cancel through cutoff |
| history_days_since_first_transaction | Cutoff minus earliest observed transaction; left-censored at data start |
| transaction_count_30d | Records in inclusive January 30–February 28 window |
| tenure_days | Cutoff minus registration date; missing/future dates masked |
| age_clean | Reported age retained only in [1,100] |
| discount_depth | 1 - actual/list; undefined at list<=0, negative when actual>list |
| latest_payment_method_id | Categorical code, no verified name mapping |
| latest_is_auto_renew | Latest recorded auto-renew flag |
| latest_is_cancel | Latest recorded cancellation flag |
| city | Member city code, snapshot availability unverified |
| registered_via | Registration channel code |
| gender_clean | Member gender; unknown category for missing |
| member_record_missing | No member row matched |
| age_missing_or_invalid | No usable age |
| recency_exceeds_plan | Elapsed time since transaction exceeds nominal duration; diagnostic, not proven error |

`msno`, `is_churn`, future transactions, raw dates, and observed churn-weighted revenue are excluded from model inputs. Stored labels are used only for fitting/evaluation. Native SHAP explains model predictions in log-odds, not causal effects.
