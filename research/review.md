# Reading the evidence

Start with the [current study](../reports/sae_context_study/report.md). Three comparisons carry its argument:

1. **Context differences.** The selected-feature counts appear in the foundation tables and [headline recheck](../evidence/sae_audit/headline_recheck.json). Check selection and multiplicity before interpreting the counts as prevalence.
2. **Prediction.** Compare all seven rows per feature in the pooled [prediction summary](../evidence/sae_prediction/prediction_summary.csv). The fit-set mean is lower than every fitted model. The [per-case errors](../evidence/sae_prediction/prediction_errors.csv) show what was averaged.
3. **Intervention specificity.** For feature 1645, compare raw interaction with the beyond-gain residual in the [paired controls](../evidence/sae_prediction/paired_controls.csv). The latter interval crosses zero. A larger raw effect does not establish selective control.

The [verification record](../evidence/sae_prediction/verification.json) records reconstruction from saved outputs. To repeat it, follow the [reproduction guide](../docs/reproduction.md). Reconstructing saved results does not rerun inference or provide an independent dataset.

The coding-repair study is separate. Its [results](../experiments/coding_forensics/RESULTS.md) explain why 48 compliant repairs left the proposed reminder comparison unanswered.
