# KKBox Retention: KPI Dashboard and Operations Specification

## Purpose and scope

Help retention operations decide whom to contact, help analytics determine whether outreach causes incremental retention and value, and help the business decide whether to continue or expand the campaign.

This is a proposed operating specification for a historical portfolio project. It is not a deployed dashboard or evidence of an actual campaign. Owners below are proposed business roles, not actual KKBox assignments. All monetary values are in New Taiwan dollars (NTD).

Historical results, modeled scenarios, and future experimental outcomes must appear in separate panels with explicit labels. Missing live measurements must display “Not collected,” not zero.

## 1. Dashboard layout

| Panel | Main question | Contents |
|---|---|---|
| Business overview | Where is churn-associated value concentrated? | Matured subscriber churn, payment-value-weighted churn, auto-renew share, predicted value at risk, eligible population |
| Weekly delivery | Can we execute the contact plan? | Due queue, weekly and remaining campaign capacity, assigned treatment/control counts, attempts, deliveries, spend, expiring uncontacted subscribers |
| Experiment results | Does outreach create incremental value? | Treatment/control outcomes, absolute and relative churn reductions, incremental saves, incremental payment revenue, costs, uncertainty, opt-outs and complaints |
| Model and data health | Are scores still usable? | Calibration, log loss, lift, score distribution, input missingness, freshness, duplicate assignments and leakage checks |

Filters: expiry cohort, scoring date, model version, policy version, experiment arm, auto-renew status, plan length, payment method, and contact channel. Display numerator, denominator, and cohort maturity alongside rates. Suppress unstable segment conclusions when samples are small; show uncertainty rather than ranking tiny groups as winners.

## 2. Cohort and measurement rules

### Historical baseline

- Prediction cutoff: February 28, 2017.
- Features: original `transactions.csv` through the cutoff, plus member attributes from `members_v3.csv`. `transactions_v2.csv` is used for diagnostics only.
- Target labels: `train_v2.csv`. Exact correspondence between the supplied label period and the operational expiry-cohort definition remains to be documented.
- Campaign population: 941,518 subscribers with an unambiguous latest subscription state expiring in March 2017.
- Strategy test population: 188,304 subscribers. The 18,831-contact cap and 12,644-person positive-benefit list apply to this test population, not the full customer base.
- Historical member-attribute availability is not fully verified. Preserve this limitation in reporting.

### Proposed live pilot

Use one row per subscriber and campaign cycle, with a stable assignment ID. Freeze eligibility, score, baseline value, expiry date, and experiment arm at assignment. Do not remove assigned subscribers from the experiment because delivery fails, their risk changes, or they renew early.

Define churn as failure to renew within 30 days after the frozen baseline expiry date, using a documented event-based renewal rule. Confirm boundary dates, time zone, treatment of cancellations, refunds, extensions, and overlapping plans before enrollment. Do not infer renewal merely from delivery or link clicks.

An outcome cohort is mature only after the full follow-up period and the billing-data ingestion delay have elapsed. Set the delay from observed data latency. Do not treat subscribers still awaiting outcomes as retained or exclude them selectively by arm.

Use a prespecified payment-revenue window of 30 days starting on the frozen baseline expiry date, with identical boundaries for both arms. Measure collected subscription payments less refunds for that window and label it payment revenue, not recognized revenue or monthly recurring revenue. Separately report renewals before expiry and longer-horizon outcomes: the primary window can miss early payments or reflect timing shifts. Finalize the window and refund policy before seeing results.

## 3. Metric definitions

Let `y_i = 1` denote churn, `p_i` the frozen churn probability, and `v_i` the frozen payment-value proxy. Set `v_i = latest actual amount paid × 30 / latest plan days` for positive plan duration. Zero payment remains zero value; nonpositive duration yields unknown value. Show unknown-value coverage separately and exclude unknown values only from value-based metrics.

### Business and planning metrics

| Metric | Definition | Review / proposed owner |
|---|---|---|
| Subscriber churn | Churners / all subscribers with mature outcomes in the stated cohort | Monthly / Analytics |
| Payment-value-weighted churn | `sum(y_i × v_i) / sum(v_i)` among mature, known-value subscribers | Monthly / Analytics and Finance |
| Auto-renew share | Subscribers with auto-renew enabled / subscribers with known auto-renew status at scoring; show unknown count separately | Weekly / Retention Operations |
| Predicted 30-day-equivalent value at risk | `sum(p_i × v_i)` in the current, deduplicated scoring cohort | Weekly / Analytics |
| Expected value protected | `s × sum(p_i × v_i)` for the selected list, where `s` is the assumed relative churn reduction | Planning / Analytics |
| Expected net after contact costs | Expected value protected minus modeled contact costs | Planning / Finance |

Do not label the payment proxy “MRR” or “lost revenue.” Do not sum repeated weekly risk snapshots as if they were independent revenue opportunities. Scenario metrics must display the assumed effectiveness, costs, scoring date, list size, and value horizon.

### Delivery and campaign metrics

| Metric | Definition | Review / proposed owner |
|---|---|---|
| Capacity utilization | Unique subscribers attempted during the week / weekly contact capacity | Weekly / Retention Operations |
| Attempt rate | Assigned treatment subscribers with at least one attempt / all treatment subscribers scheduled by the reporting date | Daily / Retention Operations |
| Delivery rate | Unique treatment subscribers with confirmed delivery / unique treatment subscribers attempted | Daily / Channel Operations |
| Treatment delivery coverage | Unique delivered subscribers / all treatment subscribers scheduled by the reporting date | Weekly / Retention Operations |
| Queue backlog | Eligible, unsent candidates within the outreach window, with expiry dates and expected net benefit | Daily / Retention Operations |
| Spend | Actual billable outreach and incentive costs, including failed attempts when billed | Weekly / Finance |
| Opt-out rate | Unique opt-outs / unique delivered subscribers, within a prespecified observation window | Weekly / Channel Operations |
| Complaint rate | Unique complaints / unique delivered subscribers, within the same defined window | Weekly / Channel Operations |

Capacity measures unique subscribers, while spend must account for every billable attempt. Contact, delivery, response, renewal, and incremental save are different events.

### Experimental impact metrics

Use intention-to-treat analysis: all assigned subscribers remain in their original arm. For a stratified design, estimate differences within the randomization strata and aggregate with prespecified weights representing the eligible pilot population. The formulas below show the simple unstratified form.

Let `n_T` and `n_C` be assigned treatment and control counts with complete follow-up; `q_T` and `q_C` their churn rates; and `r_T` and `r_C` their mean observed payment revenue per assigned subscriber.

| Metric | Definition | Interpretation |
|---|---|---|
| Absolute churn reduction | `q_C − q_T`, reported in percentage points | Primary retention effect |
| Relative churn reduction (“save rate”) | `(q_C − q_T) / q_C` | Compare with the simulation's effectiveness assumption; undefined when control churn is zero |
| Incremental saves | `n_T × (q_C − q_T)` | Estimated additional retained subscribers, not identifiable individual saves |
| Cost per incremental save | Incremental campaign cost / estimated incremental saves | Report “Not meaningful” when estimated saves are zero or negative; retain the signed effect estimate |
| Incremental payment revenue | `n_T × (r_T − r_C)` | Experimental estimate using actual payments in the defined window |
| Net incremental payment value | Incremental payment revenue minus incremental contact and incentive costs | Not profit unless all relevant incremental costs are included |
| Incremental return on campaign cost | Net incremental payment value / incremental campaign cost | Undefined if cost is zero |

If control incurs costs, calculate incremental campaign cost as treatment cost minus control cost scaled to the treatment population. Include paid incentives once; do not double-count discounts already reflected in net payment revenue.

Report confidence intervals for retention and revenue effects. Use subscriber-level uncertainty estimates consistent with the randomization design. Do not declare success from a favorable point estimate, compare only successfully contacted people with controls, or repeatedly test until significance appears. Predefine the analysis date and any sequential monitoring rules.

The observed proportion of contacted subscribers who renew is not an incremental save rate: some would have renewed without outreach.

## 4. Targeting and capacity

The central historical policy assumes `s = 0.10` and contact cost `c = NTD 5`:

```text
expected_net_i = s × p_i × v_i − c
contact candidates with expected_net_i > 0
rank by expected_net_i descending, with subscriber ID as a stable tie-break
stop at the applicable capacity and budget limits
```

The implied value-at-risk threshold is NTD 50. This threshold changes if effectiveness or cost changes; it is not a universally optimal cutoff. The model does not estimate individual treatment effects.

### Capacity illustration, not a measured operational result

For a rollout sized to the historical test population, use an illustrative maximum of **5,000 unique contacts per week** and **18,831 across the campaign**, subject to an outreach budget of **NTD 94,155** at NTD 5 each. The 12,644-person historical positive-benefit list would cost NTD 63,220 if every selected person incurred one such charge.

If evenly distributed across four execution weeks, 12,644 contacts would average 3,161 per week. This is arithmetic, not a schedule derived from expiry dates. Build the actual weekly queue from due dates; a concentrated expiry week can exceed capacity even when the campaign average fits.

Select positive-benefit candidates within the due window, subject to weekly capacity, remaining campaign capacity, and remaining budget. Preserve unused capacity when no qualifying candidates remain. Show how many candidates expire without contact and their modeled value. A capacity or scheduling constraint may change the selected list and economics; do not claim the historical 12,644 contacts are guaranteed deliverable.

For the pilot, a separate proposed allocation is **1,000 treatment and 1,000 control subscribers**, requiring up to NTD 5,000 in contact costs under the one-contact assumption. Controls do not consume outreach capacity. Do not contact all 12,644 selected subscribers while describing the exercise as this smaller pilot.

## 5. Outreach workflow

### Proposed timing

1. **14 days before expiry:** build and validate the upcoming queue, verify contactability, and check for existing campaign enrollment. This is preparation, not an extra contact.
2. **7 days before expiry:** recheck eligibility, calculate features available at that time, freeze the baseline, and randomize pilot participants. Deliver one assigned outreach treatment.
3. **3 days before expiry:** review delivery and outcome-event ingestion. A second contact is not part of the baseline cost model; test it as a separate treatment or include its full cost in a revised policy.
4. **Expiry plus 30 days and ingestion delay:** finalize retention outcomes and conduct the prespecified analysis once the entire relevant cohort has matured.

These timing choices are a proposal, not a schedule validated by the February snapshot. Scoring seven days before each expiry requires new historical feature construction and validation. Do not reuse the reported model metrics as proof of performance under that changed scoring schedule.

### Manual-renew assistance

For eligible manual-renew subscribers assigned to treatment, offer a clear renewal reminder and optional auto-renew enrollment. Record delivery, enrollment, successful renewal, cancellations, opt-outs, and cost. Evaluate incremental renewal and revenue against control; auto-renew enrollment alone is a secondary outcome. Never change renewal settings without subscriber consent.

### Payment-failure recovery

Create a separate low-cost workflow only when a verified billing failure event exists. The current dataset's payment-method and cancellation fields do not establish a failed payment. A future workflow would record failure type, recovery attempts, recovered payments, retry costs, and customer complaints. Coordinate it with retention outreach to prevent duplicate messages and experimental contamination.

### Discount experiment

Keep the initial retention pilot free of discretionary incentives. In a later experiment, compare identical outreach with and without a clearly defined incentive, ideally retaining a no-outreach control. Include the incentive's economic cost and measure incremental value over a common horizon. Observational discount-band churn is not evidence that discounts work or fail.

## 6. Model and data monitoring

| Check | Definition / comparison | Cadence | Response |
|---|---|---|---|
| Calibration | Mean predicted probability versus observed churn by fixed score bands, with counts and uncertainty | Monthly, mature untreated/control cohorts | Investigate systematic error; recalibrate only with suitable independent data |
| Log loss | Mean binary negative log likelihood; compare with the historical benchmark and a constant-probability baseline | Monthly, mature untreated/control cohorts | Investigate deterioration, segment mix, and data changes before retraining |
| Lift and capture | Churn capture and lift in the highest-risk 10%, with sample size | Monthly, mature untreated/control cohorts | Check whether ranking remains useful |
| Score distribution | Quantiles and histogram using fixed bins, segmented by renewal type and plan | Weekly, before intervention | Investigate material changes against an established reference range |
| Input missingness and coverage | Missing/invalid age, unknown tenure, absent histories, ambiguous states, unknown value | Every scoring run | Explain changes; block scoring if required fields or keys fail validation |
| Freshness and time integrity | Data watermark; no transaction after scoring cutoff; timestamp consistency | Every scoring run | Block affected scoring runs and repair inputs |
| Assignment integrity | Unique subscriber/cycle, stable arm, no unintended treatment of controls | Daily during pilot | Investigate and document deviations; preserve original assignment for analysis |

Intervention changes outcomes. Evaluating untreated-risk calibration on treatment outcomes can make an effective campaign look like model overprediction. Keep primary model-health evaluation on controls or comparable untreated populations, and label targeted controls as a selected population. The selected pilot alone cannot establish whole-population model performance.

Set numerical alert thresholds after observing normal variation and sample sizes; they are not estimated by this project. Missing required inputs, post-cutoff records, duplicate assignments, and broken score ranges are immediate validation failures. Review soft drift alerts rather than automatically retraining.

## 7. Data required for implementation

| Dataset | Minimum fields | Availability in this project |
|---|---|---|
| Scoring snapshot | Subscriber/cycle ID, scoring timestamp, model version, frozen features, probability, expiry, value proxy, eligibility and exclusion reasons | Historical features and scores exist; live timestamped snapshot logging is proposed |
| Policy and queue | Policy version, effectiveness/cost assumptions, expected net, rank, capacity, selection and scheduled date | Historical selection exists; live queue logging is proposed |
| Experiment assignment | Experiment ID, subscriber/cycle ID, arm, stratum, assignment timestamp and randomization metadata | Proposed; no experiment was run |
| Delivery events | Assignment ID, channel, attempt/delivery timestamps, billable cost, opt-outs, complaints | Not present; requires campaign instrumentation |
| Billing and outcomes | Payment and refund events, renewal event, frozen outcome horizon, maturity flag | Historical transaction/label data exist; prospective measurement requires validated event semantics and follow-up |

Use access-controlled subscriber-level tables internally and aggregate outputs for the portfolio. Store metric definitions and policy/model versions so reports can be reproduced.

## 8. Review cadence and decisions

- **Daily during delivery - Retention and Channel Operations:** queue integrity, capacity, delivery, spend, complaints, and control contamination.
- **Weekly - Retention Operations and Analytics:** upcoming expiry volumes, remaining budget, uncontacted eligible subscribers, input changes, and delivery coverage. Treat immature outcomes as pending.
- **Monthly or after a complete pilot cohort matures - Analytics and Finance:** causal retention and revenue estimates, uncertainty, incremental costs, calibration, and the decision to continue, revise, or stop.

Expand only when the prespecified experiment supports acceptable incremental economics and operational guardrails. A successful churn test alone does not prove profitable outreach. If results are inconclusive, report that uncertainty and plan any extension before collecting additional evidence.

Related analysis: [strategy simulation](../notebooks/04_strategy_simulation.ipynb), [executive memo](../reports/executive_memo.md), and [project overview](../README.md).
