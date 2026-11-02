# KKBox Retention Strategy

Executive memo | Ian Gaffney | Historical portfolio analysis

### Recommendation

**Pilot a retention campaign that contacts subscribers only when expected benefit exceeds outreach cost, subject to contact capacity.** In a historical test cohort of 188,304 subscribers, this policy selects 12,644 people. Assuming a 10% relative reduction in churn and NTD 5 per contact, it produces approximately **NTD 53,661 in expected net value after contact costs: 12.6% more modeled net value with 32.9% fewer contacts** than filling the 18,831-contact capacity.

These are simulated outcomes based on a standardized payment-value proxy, not measured campaign returns or profit. The next step is a randomized pilot, not immediate rollout.

### Business problem

A retention team must decide whom to contact with limited resources. Churn probability identifies likely cancellations but does not account for subscriber value or intervention cost. This analysis combines churn probability with 30-day-equivalent payment value to identify contacts whose modeled benefits exceed costs.

### Three findings

**1. Risk is concentrated.** LightGBM achieved test ROC AUC of 0.9068 and log loss of 0.1554. The highest-risk 10% captured 67.54% of churners, approximately 6.75 times random targeting. Calibration checks were also conducted because economic decisions depend on probability estimates, not ranking alone.

**2. Manual-renew subscribers account for disproportionate value associated with churn.** They represent 11.48% of the campaign cohort but 59.96% of observed churn-associated standardized payment value. Within 30-day plans, churn was 28.55% for manual-renew subscribers versus 3.78% for auto-renew subscribers. This motivates an experiment; it does not establish the effect of converting users to auto-renew.

**3. Filling capacity can reduce expected net value.** Under the central assumptions, some subscribers within the highest-value 10% have expected benefits below the contact cost. Excluding them reduces total expected value protected but increases expected net value.

| Test-cohort scenario | Fill capacity | Positive-benefit |
| --- | --- | --- |
| Contacts | 18,831 | 12,644 |
| Contact cost (NTD) | 94,155 | 63,220 |
| Expected value protected (NTD) | 141,818 | 116,881 |
| Expected net after contact costs (NTD) | 47,663 | 53,661 |

### Proposed actions

**Retention targeting:** test the positive-benefit policy against a randomized no-outreach control. **Auto-renew assistance:** test a consent-based enrollment workflow for eligible manual-renew subscribers. **Discounts:** test incentives against otherwise identical outreach without incentives before expanding discounts; observed partial-discount groups are too small and confounded to establish effectiveness.


---

## Economics and validation

KKBox Retention Strategy | Implementation proposal

### Method and assumptions

The analysis starts with 970,960 labeled subscribers. The operational cohort includes 941,518 with an unambiguous latest subscription state expiring in March 2017. Transaction features use the original file and dates on or before February 28, 2017. Logistic regression is the baseline; LightGBM is the main model. Subscribers are split 60%/20%/20% into training, validation, and testing within the same historical period.

**Expected net benefit = churn probability × payment-value proxy × assumed relative churn reduction − contact cost.** The proxy is latest actual payment ÷ plan days × 30. It standardizes plan lengths; it is not accounting MRR, lifetime value, or a verified next-payment forecast.

All monetary figures are in **New Taiwan dollars (NTD)**. The central scenario assumes 10% of otherwise-occurring churn is prevented, equal effectiveness across subscribers, and NTD 5 per contact. Incentives, service-delivery costs, and other incremental costs are excluded.

### Sensitivity and break-even

For the **fixed 12,644-person test list**, holding contact cost at NTD 5:

| Assumed relative churn reduction | Expected net after contact costs |
| --- | --- |
| 5% | −NTD 4,780 |
| 10% | NTD 53,661 |
| 20% | NTD 170,542 |

The fixed list breaks even at approximately **5.41% relative churn reduction**, before additional costs. This range reflects assumptions, not statistical uncertainty. The list was selected under the 10% assumption; reselecting it under different assumptions would produce different results.

### Pilot and operating plan

Randomize eligible subscribers to outreach or no-outreach control before delivery, stratifying by risk and auto-renew status. An illustrative calculation requires about **847 subscribers per arm** to detect a 10% relative churn reduction from 65.85% control churn, at 80% power and a two-sided 5% significance level. **1,000 per arm** is a starting proposal, subject to confirming the population and delivery assumptions. Detecting a churn difference alone does not establish profitable incremental revenue.

Use one clearly defined treatment initially. Schedule outreach before expiry, prevent duplicates, and verify consent and contactability. Rescoring closer to expiry requires features reconstructed for that date. Evaluate after the renewal grace period using intention-to-treat comparisons and a common revenue follow-up window.

Retention operations should review delivery weekly. Analytics should evaluate completed outcome cohorts, calibration, incremental renewal and revenue, contact and incentive costs, and cost per incremental save. Monitor complaints and opt-outs. Scale only if measured incremental value supports the economics.

### Risks and interpretation

This is a historical method demonstration, not evidence of current KKBox performance. Evaluation is within-period rather than a future-month test; test results have been inspected during development. Historical availability of member attributes is not fully verified. The later transaction release is excluded because availability of its historical-dated records at the cutoff is unclear. Exact alignment of the supplied label period with the operational prediction setup remains to be documented.

**The model predicts churn, not responsiveness to outreach.** Intervention effectiveness must be established experimentally.

Source: Kaggle, WSDM - KKBox’s Churn Prediction Challenge; project notebook outputs.
https://www.kaggle.com/competitions/kkbox-churn-prediction-challenge/data
