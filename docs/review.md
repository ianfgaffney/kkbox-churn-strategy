# Review of the uploaded 01_eda_baseline.ipynb

## Scope and evidence
Reviewed all 60 cells: 54 code cells and 6 Markdown cells (see validation report for computed counts).
The notebook has saved executed outputs and no saved error outputs. This is evidence of
prior execution, not proof of a fresh-kernel run. No raw CSVs or fitted model objects were
attached. Reported full-data metrics come from source outputs, not a rerun here.

## What was already sound
- Explicit 21-feature allowlist excludes IDs, labels, and churn-weighted revenue.
- Logistic preprocessing fit only on training; category definitions learned from training.
- Stratified disjoint user splits and early stopping using validation, not test.
- Transactions used in latest-state/history features restricted to the fixed cutoff.
- Same-day distinct records classified as ambiguous rather than arbitrarily ordered.
- Save-rate assumptions and modeled net revenue distinguished from observed outcomes.

## Reproducibility repairs in the reviewed project
- Four notebooks have explicit disk handoffs and complete imports. Independent kernels.
- One config replaces the personal absolute path; outputs stay inside project directory.
- One streaming pass consolidates latest-state selection, counts, cancellation history,
  first observation, and recent counts. History counts still include original duplicates.
- Raw-record counting is now explicitly cutoff-filtered, not dependent on source max date.
- Row IDs and subscriber IDs survive checkpoints. Prediction tables include both, target,
  value, and probability; strategy uses saved records rather than positional cross-notebook joins.
- Model bundle, native LightGBM file, category definitions, split membership, environment
  metadata, score tables, metrics, gains curve, calibration and scenario charts are exported.
- Original outputs are cleared from refactored notebooks; aggregate historical plot evidence
  is separately labeled. No personal path, credentials, or original subscriber examples are packaged.
- Requirements distinguish reported pandas/numpy versions from unverified dependency ranges.

## Unresolved methodological issues (not silently fixed)
1. **Label/cohort alignment:** train_v2 supplied labels must be checked against official
   eligibility and renewal-gap labeling logic. The chosen March-expiry intersection is a
   subset of supplied labels, not necessarily the entire deployable subscriber universe.
   Keep results provisional until the rationale is documented; don't recompute labels ad hoc.
2. **Snapshot availability:** a pre-cutoff transaction date does not prove every attached
   expiry/account field was recorded then. members_v3 has later registrations. Only tenure
   is masked for future registrations; original demographic fields remain to preserve the
   historical baseline. A prospective claim requires historical snapshots. Add an ablation
   without member features on training/validation if needed, but do not tune on exposed test.
3. **v2 coverage:** only three original-history-missing IDs were recovered in earlier checks.
   That does not establish equivalence for existing subscribers. Run audit_v2_overlap.py
   to measure exact pre-cutoff row overlap and affected labeled users. Later-published old
   records cannot automatically be assumed available at the scoring date.
4. **Latest-state ambiguity/exclusions:** 10,944 ties remain unresolved; the 941,518-person
   campaign cohort excludes them, older expirations and missing history. Report coverage.
   Expiry dates such as 1970 and recency exceeding plan length were observed; some were
   excluded by cohort selection, others retained and flagged. No universal correction is justified.
5. **Evaluation:** EDA used full cohort labels before splitting; subscribers were randomly
   split within one period. Test model metrics were inspected before policy development was
   finished, although policy selection used validation. The test should not be described as a
   pristine prospective policy trial. Future-month validation remains outstanding.
6. **Valuation:** actual_amount_paid / plan_days * 30 is a standardized historical billing
   proxy. It is not MRR, margin, cash lost, or guaranteed next-cycle revenue. Zero payments
   get zero weight; zero-day plans have unknown normalized value. Stale plans and promotions
   may misstate future value. Verify original NTD denomination from official metadata before
   replacing the current 'dataset units' labels; never interpret contact cost 5 as USD.
7. **Interventions:** uniform 10% relative reduction in otherwise-occurring churn is assumed.
   Costs 1/5/10 are illustrative, no incentive or service cost is included. Aggregate probability
   agreement does not validate effect size, individual calibration, or segment economics.
   Positive-only selection improves modeled net mechanically under these assumptions.
8. **Experiment:** normal-approximation sample sizes concern churn, not economic superiority;
   no non-delivery inflation is applied. ITT effect is across everyone assigned outreach.
   A real revenue outcome needs a prespecified common horizon and recognition convention.
9. **Operations:** current score is a single February 28 snapshot. Seven-day-before-expiry
   scoring, weekly refreshes, payment-failure detection and recovery are proposals, not tested features.

## Recommended publication gate
Complete fresh-kernel local execution, version capture, source audit, documentation of
label/currency definitions, and review of proxy/eligibility sensitivities before presenting
results as final. Exposed test data must not guide further tuning. A true new holdout requires
new chronological data, not another random split of already explored records.
