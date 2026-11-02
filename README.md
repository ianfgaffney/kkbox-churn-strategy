# KKBox Churn: Revenue & Operations Strategy

**With a fixed retention budget and limited contact capacity, which expiring subscribers should KKBox contact to maximize expected net subscription revenue protected?**

This project connects churn prediction to a retention decision: estimate churn risk, combine it with a subscription-value proxy, and contact subscribers only when the modeled benefit exceeds the contact cost.

In the same-period test cohort, contacting **12,644 subscribers** produced **NTD 53,661 in expected net value after contact costs**, compared with **NTD 47,663** when filling the entire 18,831-contact capacity. That is approximately **12.6% more modeled net value with 32.9% fewer contacts**, assuming a 10% relative reduction in churn and NTD 5 per contact.

**These are scenario estimates, not measured campaign returns or profit.** A randomized experiment is needed to establish an intervention's incremental effect. Under a separate fixed-capacity validation scenario, net value ranged from approximately **−NTD 116,909 to +NTD 266,774** across the tested cost and effectiveness assumptions. This is a sensitivity range, not a confidence interval or a range for the 12,644-contact policy.

## Business decision

Churn probability alone does not determine whether outreach is worthwhile. A high-risk subscriber may have little payment value, and contacting lower-benefit subscribers merely to fill capacity can reduce expected net returns.

The proposed rule is:

```text
Predicted value at risk = churn probability × 30-day-equivalent payment value
Expected net benefit = assumed relative churn reduction × predicted value at risk − contact cost
```

Rank subscribers by expected net benefit, contact only those with positive expected benefit, and stop when capacity is reached. This rule assumes the same intervention effectiveness and contact cost across subscribers; it does not estimate individual treatment effects.

## Results

### Model performance

The campaign cohort contains **941,518 subscribers**, with an observed churn rate of **7.97%**. It was split by subscriber into 60% training, 20% validation, and 20% testing using stratification and a fixed random seed.

| Model | Test log loss ↓ | Test ROC AUC ↑ | Churners captured in highest-risk 10% | Lift over random |
|---|---:|---:|---:|---:|
| Logistic regression | 0.1777 | 0.8578 | 64.49% | 6.45× |
| LightGBM | 0.1554 | 0.9068 | 67.54% | 6.75× |

LightGBM improved both probability accuracy and ranking relative to logistic regression. Evaluation also includes calibration by risk group, lift, and SHAP explanations. The leading SHAP features included auto-renew status, transaction recency, payment method, length of observed transaction history, and plan price. SHAP describes model behavior, not causal effects.

### Retention-policy comparison

The following results use the **188,304-subscriber test cohort**, a maximum capacity of **18,831 contacts**, a **10% assumed relative churn reduction**, and **NTD 5 per contact**.

| Policy | Contacts | Contact cost, NTD | Expected value protected, NTD | Expected net after contact costs, NTD |
|---|---:|---:|---:|---:|
| Fill capacity, ranked by value at risk | 18,831 | 94,155 | 141,818 | 47,663 |
| Contact only when expected benefit exceeds cost | 12,644 | 63,220 | 116,881 | 53,661 |

The positive-benefit policy sacrifices some total coverage while increasing modeled net value. It selects subscribers with predicted value at risk greater than NTD 50 under these assumptions.

| Policy | Share of observed churn-associated value captured | Share of churners captured |
|---|---:|---:|
| Fill capacity, ranked by value at risk | 68.15% | 66.58% |
| Positive-benefit policy | 55.32% | 55.40% |

Observed churn-associated value measures payment-proxy value belonging to subscribers labeled as churners. It is **not** revenue recovered by outreach. Predictions determine selection; observed outcomes are used afterward to evaluate coverage.

### Five descriptive findings

1. **Manual-renew subscribers account for disproportionate churn-associated value.** They make up 11.48% of the campaign cohort but account for 57.95% of churners and 59.96% of churn-associated 30-day-equivalent payment value.
2. **The auto-renew difference persists within 30-day plans.** Churn was 28.55% among manual-renew subscribers versus 3.78% among auto-renew subscribers. This association does not establish the effect of converting a subscriber to auto-renew.
3. **Cancellation status identifies a distinct high-risk group.** Among auto-renew subscribers, churn was 70.78% with a latest cancellation record versus 3.51% without one.
4. **The value definition materially changes the result.** Latest-payment-weighted churn was 19.86%, compared with 8.59% after normalizing payments by plan duration. Longer plans should not automatically be treated as larger monthly revenue streams.
5. **Discount evidence is limited.** Only 690 campaign subscribers fell into the observed positive-payment partial-discount bands. Segment differences do not establish that discounts prevent churn or that a discount policy should be expanded.

## Data and prediction setup

Source: [WSDM – KKBox's Churn Prediction Challenge on Kaggle](https://www.kaggle.com/competitions/kkbox-churn-prediction-challenge/data).

Download the data through Kaggle and follow its applicable access and data-use terms. Raw subscriber data is not included in this repository.

| File | Role |
|---|---|
| `train_v2.csv` | Subscriber IDs and churn outcome labels |
| `transactions.csv` | Transaction features and subscription-state reconstruction |
| `members_v3.csv` | Member attributes and registration information |
| `transactions_v2.csv` | Separate source-comparison diagnostics only; excluded from model inputs |

The prediction cutoff is **February 28, 2017**. The campaign cohort consists of labeled subscribers whose unambiguous latest transaction state has a membership expiry in **March 2017**. The exact correspondence between the supplied label period and this operational prediction setup remains a documentation check; the transaction-file descriptions alone do not establish label alignment.

Kaggle describes `transactions.csv` as covering transactions through February 28 and the refreshed `transactions_v2.csv` as covering transactions through March 31. Features use the original file and enforce the February cutoff.

An audit found 170,132 distinct pre-cutoff v2 rows for labeled subscribers absent as exact rows from the original file, affecting 89,099 subscribers in the original campaign cohort. Most had subscriber/date combinations absent from the original; same-day comparisons also revealed differing expiry dates. These differences do not establish whether the records were additional events, revisions, or available at the prediction cutoff. V2 is therefore retained for diagnostics rather than automatically appended to the baseline. This is a documented source assumption, not a claim that the original file is a complete, verified historical snapshot.

Listening logs are omitted from the baseline project.

## Preparation and features

The original label file contains **970,960 unique subscribers**, with **8.99% churn**. The campaign cohort is a narrower operational subset, not the entire label population.

Preparation includes:

- Preserving subscribers with missing member records and representing missingness explicitly.
- Treating ages outside 1–100 as unknown.
- Parsing dates and masking post-cutoff registration dates when calculating tenure.
- Selecting latest transactions by transaction date; removing exact duplicates among latest-date candidates and flagging unresolved same-day ambiguity.
- Restricting campaign eligibility to unambiguous March expirations. In the original-file baseline, 10,944 subscribers have ambiguous latest states and 2,527 lack transaction history; other exclusions fall outside the expiry window.
- Handling zero-price and zero-duration records explicitly rather than dividing by zero or dropping all zero-payment subscribers.

The model uses 21 features covering subscription terms, payment settings, transaction counts and cancellations, recency, observed history length, tenure, demographics, and missingness. See [the feature dictionary](docs/feature_dictionary.md).

Logistic-regression imputation, scaling, and category encoding are fitted on training data only. LightGBM category definitions also come from training data; validation data determines early stopping. Subscriber IDs and outcome-derived revenue fields are excluded from model inputs.

## Monetary assumptions and sensitivity

All prices, contact costs, and modeled values are in **New Taiwan dollars (NTD)**.

```text
30-day-equivalent payment value = latest actual amount paid × 30 / latest plan days
```

This proxy standardizes historical payments across plan lengths. It is not accounting MRR, customer lifetime value, or a verified next-cycle payment forecast. Zero payments retain zero proxy value; nonpositive plan duration yields unknown value. Two campaign subscribers lack this proxy; none fell in the reported strategy test cohort.

The simulation varies assumed relative churn reduction across **5%, 10%, and 20%**, and contact cost across **NTD 1, 5, and 10**. A 10% relative reduction means preventing 10% of otherwise-occurring churn, not reducing churn by 10 percentage points.

Expected net value subtracts contact costs only. Incentives, service-delivery costs, margins, and longer-term retention are not included. Campaign effectiveness is assumed, not learned from these observational data.

## Recommendations and validation plan

1. **Pilot the positive-benefit targeting rule.** Treat capacity as a maximum, and test whether outreach creates positive incremental value. Randomly assign eligible subscribers to outreach and no-outreach control groups before launching.
2. **Test an auto-renew assistance workflow for manual-renew subscribers.** Use clear consent and an appropriate control group. The observed auto-renew association motivates an experiment; it does not quantify the causal benefit of conversion.
3. **Test discounts selectively before expanding them.** Compare an incentive with otherwise identical outreach without an incentive, including incentive costs in the decision. The descriptive discount groups are too small and confounded to justify broad policy changes.

The experiment-planning calculation estimates approximately **847 subscribers per arm** to detect a 10% relative churn reduction from a 65.85% control churn rate, using 80% power and a two-sided 5% significance level. This is an approximate planning calculation, conditional on that baseline and the chosen population. A practical plan should allow for delivery issues, define the outcome window, and analyze assignment on an intention-to-treat basis. Detecting a churn difference does not automatically establish profitable incremental revenue.

Operations should define contact capacity, consent and contactability, expiry-relative scheduling, and responsibility for delivery and measurement. A payment-failure recovery track would require verified failure events; payment method or churn risk alone does not identify a failed payment. Any later scoring dates require newly constructed features appropriate to those dates.

## Repository guide

| Location | Purpose |
|---|---|
| `notebooks/01_eda_baseline.ipynb` | Data preparation, audits, descriptive metrics, and charts |
| `notebooks/02_features.ipynb` | Feature creation and modeling-table export |
| `notebooks/03_model.ipynb` | Training, validation, testing, calibration, lift, SHAP, and model exports |
| `notebooks/04_strategy_simulation.ipynb` | Targeting comparisons, sensitivity analysis, and experiment sizing |
| `src/` | Reusable data, feature, and strategy functions |
| `scripts/` | Execution, environment capture, and diagnostic utilities |
| `tests/` | Focused pipeline checks |
| `Data/Raw/` | Local input CSVs; excluded from version control |
| `Data/processed/` | Generated intermediate tables; excluded from version control |
| `artifacts/` | Generated models, split assignments, and subscriber predictions |
| `reports/figures/` and `reports/tables/` | Aggregate analysis outputs |
| `docs/` | Feature definitions, review notes, and local execution checklist |
| `config.json` | Data location, cutoff, cohort window, and run settings |

`reports/source_snapshot/` preserves outputs from the original notebook. Use the current rerun exports for final reporting and distinguish them from these archived outputs.

## Reproduce the analysis

1. Download and extract the required CSVs through Kaggle. Place them in `Data/Raw/`, or set `raw_data_dir` in `config.json` to their existing location. Preserve the folder capitalization.
2. From the project root, create and activate a Python environment, then install dependencies:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   ```

3. Select that environment as the notebook kernel. On macOS, LightGBM also requires its OpenMP runtime; the author's installation required `libomp`.
4. Run notebooks **01 → 02 → 03 → 04**, each from a fresh kernel. The notebooks exchange saved tables and predictions, so they do not require shared in-memory variables.
5. Capture the actual installed environment with `scripts/capture_environment.py` and retain the generated version information. See [the local run checklist](docs/local_run_checklist.md) for execution details.

The author reports successfully running all four notebooks locally and confirmed the reported LightGBM test metrics and strategy results. The code review checked preprocessing and source selection; it did not independently rerun the full raw dataset in the review environment. Dependency versions and runtime details are important for reproducing small numerical differences.

The optional `scripts/audit_v2_overlap.py` compares transaction releases and writes diagnostic outputs. It does not append v2 records to the modeling table or retrain the model.

## Limitations and project status

- **Historical case study:** results describe this 2015–2017 dataset, not current KKBox performance.
- **Timing assumptions:** transaction-source availability and member snapshot timing are not fully verifiable from the provided descriptions. Masking future registration dates does not verify the historical availability of other member attributes. Exact label-period alignment remains to be documented.
- **Selected population:** campaign eligibility excludes ambiguous and missing subscription states. Results should not be generalized automatically to all subscribers.
- **Same-period evaluation:** the split measures performance across subscribers in the same period, not performance in a future month. Full-cohort exploratory analysis preceded modeling, and test results have been inspected during project development; the test set should not be presented as an untouched prospective evaluation.
- **Observed, not causal:** churn associations and SHAP explanations do not establish what intervention will change a subscriber's behavior.
- **Assumed economics:** uniform intervention effectiveness and cost simplify the decision. Profitability requires measured incremental outcomes and fuller costs.


