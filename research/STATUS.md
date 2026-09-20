# Research status

Updated 20 September 2026.

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

## Current development direction

On 20 September, started a bounded [state-update preflight](../experiments/state_updates/README.md): can model errors and the effects of simple corrections be measured before studying internal mechanisms? The initial assay uses cached Gemma models, an exact simulator and four paired prompt conditions. It is development work, not a new confirmed scientific result. See the [pilot results](../experiments/state_updates/RESULTS.md).

## Open work

A stronger SAE experiment would need a validated behavioral outcome, a small calibrated predictor and new prompt families. The active short-term direction is state updates and memory, with a competence gate before mechanistic analysis. World-model planning remains an alternative. No new SAE or EGNN GPU training is committed.
