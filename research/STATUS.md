# Research status

Updated 19 September 2026.

| Study | Status | Result or open decision |
| --- | --- | --- |
| 4B SAE observational study | Completed | Context differences in selected entries; no dictionary-wide or semantic claim. |
| Context interventions | Completed development pilot | Three features, 16 check groups each. Selectivity beyond gain and superiority over PC controls remain unestablished. |
| Decoder-effect prediction | Rechecked with constant baselines | Fit-set mean has lower pooled point-estimate MSE than every fitted predictor for all three features. Constants were added after the original analysis. |
| Signed-response analysis | Exploratory, same saved outputs | Local structure without a demonstrated transferable predictor. |
| 1B SAE study | Archived development work | Historical report retained separately. |
| Coding-repair assay | Stopped | All 48 repairs compliant; intended behavioral contrast absent. |
| Documented coding-task proposal | Preflight only | Five synthetic scorer controls; no model experiment completed. |

The [current report](../reports/sae_context_study/report.md) replaces the longer report as the entry point. Earlier reports, execution records and inference outputs remain unchanged.

## Decisions

- **13 September:** separated the reusable SAE toolkit from study code and evidence; stopped the uninformative coding assay.
- **15 September:** a saved-output audit added zero and fit-mean baselines, exposing the prediction models' poor pooled performance.
- **19 September:** reproduced that comparison in a standalone script and incorporated it into the main report. This is analysis of existing inference, not a new model experiment.

## Open work

A stronger SAE experiment would need a validated behavioral outcome, a small calibrated predictor and new prompt families. World models, memory and representation learning are also being considered for future work. No follow-up direction or sequence is committed, and no GPU experiment is running as part of this rewrite.
