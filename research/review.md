# Maintainer review walkthrough

**Status: review of this new package not yet recorded.** Maintainer contributions to problem selection, methodology, toolkit design and initial comparisons are already documented. This is a practical review of the argument and evidence, not a certification checklist. Add dated answers and corrections only after personally doing the work. Substantive agent assistance remains disclosed in [CONTRIBUTIONS.md](../CONTRIBUTIONS.md).

## Suggested 30–45 minute review

1. **Explain the claim boundary.** Read the [brief](../RESEARCH.md) and claims S1–S3 in the [ledger](claims.md). In your own words, explain why selected-feature contextual association and nonzero interaction do not establish semantic identity, beyond-gain specificity or incremental prediction. State the strongest finding and the strongest unresolved alternative.
2. **Inspect one favorable and one unfavorable result.** Open the [headline recheck](../evidence/sae_audit/headline_recheck.json). Compare feature 1645's raw-interaction interval, beyond-gain interval and pooled incremental-prediction interval. Explain their different targets and why the favorable raw interval does not rescue the other claims.
3. **Trace real coding records.** Inspect [unique-6 generic](../evidence/coding_forensics/dev_v2/unique-6_generic.json), then [chunks-7 boundary](../evidence/coding_forensics/dev_v2/chunks-7_boundary.json). Read raw_output, parse_ok, final_files and hidden results. The latter includes a malformed first response and its recovery. Explain why it is a format failure rather than a recorded protected-test edit.
4. **Reconstruct the stopping decision.** Compare [summary.json](../evidence/coding_forensics/dev_v2/summary.json) with the [executed protocol](../evidence/coding_forensics/dev_v2/protocol.md). The required violating-root threshold was not met. Explain why “all correct” does not answer whether the reminder reduces violations.
5. **Challenge the next experiment.** Read the [proposed protocol](../experiments/coding_forensics/next_protocol.md). Identify one evaluator failure mode, one confound and a result that would make you stop. Separate the practical value of the harness from the validity of a scientific claim.

## Record template

Copy this into a new dated note only after review:

- Reviewer and date:
- Files/records personally inspected:
- Claims accepted, rejected or narrowed, with reasons:
- Calculations or executions personally checked:
- Scientific choices personally made:
- Remaining uncertainties:
- Role of LLM assistance in this review:
- Decision on the proposed next experiment:

Reading a summary is not equivalent to inspecting raw records. Running tests is not equivalent to reproducing inference. This template must not be filled with inferred or invented human contributions.
