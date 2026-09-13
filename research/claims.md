# Claim and evidence ledger

This ledger summarizes existing evidence. It is not a new statistical analysis or a preregistration. Counts refer to the populations below, not the whole model or deployment distribution.

| ID | Claim and status | Evidence | Required limit |
|---|---|---|---|
| S1 | Observational: 14/24 partner and 3/24 orthogonal discoveries at layer 17; 18/24 and 6/24 at layer 22. | [Full methods/report](../reports/research_report/report.md), [saved-table recheck](../evidence/sae_audit/headline_recheck.json), [foundation verification](../reports/gemma4b_foundation_v1/verification.json). | Discovery-selected entries; two source tests and separate multiplicity families. Same model and corpus across layers, not independent model replication. No semantic labeling or prevalence claim. |
| S2 | Development: feature 1645 learned-minus-random raw interaction has a positive descriptive interval; beyond-gain specificity is unresolved. | [Paired controls](../reports/research_report/tables/pilot_paired_control_summary.csv), [recheck](../evidence/sae_audit/headline_recheck.json). | Raw mean 0.00274235, interval [0.00105406, 0.00518035]; beyond-gain mean 0.00135445, interval [-0.00007159, 0.00308077]. Sixteen check groups. Fixed readout coordinates and selected directions; not a new corrected discovery. |
| S3 | Exploratory: no supported feature has a pooled positive PC-only-minus-PC-plus-context prediction-improvement interval. | [Incremental prediction](../reports/research_report/tables/signed_incremental_prediction.csv), [per-case errors](../reports/research_report/tables/signed_incremental_prediction_errors.csv). | Positive improvement would favor adding context. At 1645 the pooled interval is negative; other pooled intervals cross zero. Calibration was fixed, uncertainty excludes refitting it, and existing check data are not fresh confirmation. |
| S4 | Exploratory: signed interactions are predominantly odd in both signs, compatible with mixed curvature. | [Signed coefficients](../reports/research_report/tables/signed_signed_coefficients.csv), [summary](../reports/research_report/tables/signed_signed_summary.csv), [analysis timing and plan](../docs/signed_interaction_analysis.md). | Does not establish convergence at zero dose, pathway mediation, semantic function or transfer. Several summaries were added after earlier outputs were inspected. |
| C1 | Feasibility: 48/48 compliant repairs, zero prohibited test-edit attempts, and failed behavior gate. | [Results and deviations](../experiments/coding_forensics/RESULTS.md), [summary](../evidence/coding_forensics/dev_v2/summary.json), [audit](../evidence/coding_forensics/dev_v2/audit.json), [raw records](../evidence/coding_forensics/dev_v2). | Twenty-four paired roots from three similar families; greedy decoding. No treatment-effect, equivalence, deployment-safety or intent claim. Parser was amended after the aborted v1 run. |
| P1 | Static preflight: upstream lexical scorer labels do not certify completion of the proposed next task. | [Five synthetic controls](../evidence/precommit_reference/scorer_preflight.json), [audit script](../scripts/audit_precommit_reference.py), [upstream scorer](https://github.com/gkroiz/agent-interp-envs/blob/56fd0c11e6cb973b9e1f752ba7c1f35ec3f570bb/environments/precommit_hook/score.py). | Source-inspection-selected fixtures, not model behavior or a measured error rate. Upstream already describes its labels as characterization. No claim of a novel scorer defect or paper invalidation. |

## Units, controls and verification

The observational corpus has 12,000 documents and 4,047,982 eligible positions per layer. The intervention pilot has 96 feature-prompt cases but 95 distinct duplicate groups. Repeated doses and directions improve within-case comparisons; they do not increase the number of independent cases. Check intervals are descriptive and conditional on the selected features and fixed calibration.

The [raw verification record](../reports/research_report/raw_verification.json) checks 96 prompts, 5,376 comparisons, hashes, group separation and numerical constraints. It does not independently reproduce model inference. The coding audit re-executes hidden checks but reuses the executed sandbox evaluator. Read its limitations before calling it independent verification.

## Claims this evidence does not support

- That high and low activation regimes are different semantic meanings.
- That an SAE feature is a reliable causal explanation of a concerning action.
- That the learned context predictor adds reliable generalizable value.
- That coding behavior in this assay diagnoses deception or malign intent.
- That code ownership proves sole scientific authorship or personal review.

New data, changed endpoints and human review should receive new dated records; frozen evidence should not be silently rewritten.
