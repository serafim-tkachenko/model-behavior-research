# Research status and decisions

Updated 13 September 2026. This is a retrospective index except where a proposed next step is explicitly identified. The dates of original execution are preserved in the linked manifests; this page does not backdate registration.

| Workstream | State | Decision and evidence |
|---|---|---|
| 1B SAE development | Archived | Historical pilot; not the primary completed study. [Report](../reports/gemma1b_regimes_positive/scientific_report.md). |
| 4B SAE foundation | Completed observational study | Retain selected-feature contextual findings with their population limits. [Brief](../RESEARCH.md), claims S1–S4 in the [ledger](claims.md). |
| Context intervention and signed reanalysis | Completed development/exploratory work | Stronger selective-mechanism and prediction claims remain unestablished. Do not reuse check groups as fresh confirmation. |
| Synthetic coding repair | Stopped feasibility assay | Behavior gate failed: zero violating roots. Preserve v1 parser failure and v2 outputs; do not scale the assay. [Decision](../experiments/coding_forensics/RESULTS.md). |
| Documented coding-task follow-up | Preflight started; model runs not started | Five synthetic scorer controls completed. Independent outcome evaluator and capability check are still required. [Proposed protocol](../experiments/coding_forensics/next_protocol.md). |
| Maintainer contributions and review | Research direction, methodology and toolkit design confirmed; review of this new package pending | See [contributions](../CONTRIBUTIONS.md). Complete the [walkthrough](review.md) to record specific evidence review and interpretation. |

## Decision record

**13 September — repository separation completed.** Library maintenance belongs to SAE Feature Atlas. This repository owns experiments, reports and evidence. Original report bytes and pre-separation source are preserved. [Migration](../docs/migration.md).

**13 September — preserve the negative development result.** The coding assay lacked the behavior necessary for the intended comparison. More repetitions of the same short tasks would not fix that problem. Reuse its isolation, provenance and paired-input checks, not its outcome as evidence about safety.

**13 September — prepare a reviewer-readable account.** The SAE study is the primary completed study. Coding forensics is a clearly separated feasibility direction. A short brief and evidence ledger explain the result without requiring a reviewer to infer the project from scripts or a long archive.

**13 September — qualify the next environment's scorer.** A source-level audit reproduced five synthetic lexical-scoring cases. Completion must be verified independently in the follow-up; upstream labels remain diagnostics. This preflight does not show that a model exhibits the target behavior.

## Next work, in order

1. Maintainer review of the key scientific distinctions and concrete records in the walkthrough.
2. Implement and validate the independent outcome evaluator for the pinned repository task, including positive and negative controls.
3. Freeze exact prompts, environment, model settings and compute limits before a small capability/behavior pilot.
4. Continue only if the capability and behavioral-contrast gates pass. Otherwise report the result and reconsider the environment or model.
5. Only then formulate counterfactual predictions, reserve new task roots, and compare explanations. Internal representations must add value over specified behavioral baselines before SAE work is justified.

No active GPU job or confirmation run is implied by this plan.
