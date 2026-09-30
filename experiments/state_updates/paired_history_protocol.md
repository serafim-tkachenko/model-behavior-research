# Paired history assay

## Question and fixed design

Does moving a target's latest location statement earlier in an otherwise identical event stream reduce constrained-choice accuracy? This bounded behavioral assay follows the successful snapshot lookup calibration. It tests event order at matched length, not an isolated memory mechanism, practical repair method or selector.

Use the previously selected prose prompt, its three static demonstrations, the same cached Gemma 3 4B PT revision `cc012e0a6d0787b4adcc0fa2c4da74402494554d`, CPU float32, eager attention, eight threads and exact contextual A/B/C next-token scoring. History blocks add only an explicit chronological-update heading and location statements. No new demonstrations, prompt selection, parameter fitting or model comparison occur in this assay.

Generate 36 base cases using seed 730301: one per query position (four) by initial target box (three) by final target box (three). Each object is queried nine times. Thus 24 targets change box and 12 retain their box. The latter receive an explicit restatement of their location; they are not a no-target-event condition. Answer labels, source boxes and query positions are balanced. Object identity is marginally balanced, not fully crossed with transitions.

Each case contains an initial state, one target location statement and 12 actual moves of other objects. Other-object moves never touch the target. Retain their exact sequence in all long histories. Insert the target statement with 0, 4 or 12 distractors following it. These variants have the same initial state, event multiset, distractor order, final state and target answer. Verify exact tokenizer lengths match before inference. Moving the target statement changes its absolute and relative position together with recency; these factors are not separated.

Six conditions per case:

| Condition | Input | Correct answer |
| --- | --- | --- |
| `initial_snapshot` | Initial assignments in calibrated prose | Initial target box |
| `final_snapshot` | Exact final assignments, no events | Final target box |
| `short_history` | Initial assignments and one target statement | Final target box |
| `lag_0` | All 12 distractors, then target statement | Final target box |
| `lag_4` | Eight distractors, target statement, four distractors | Final target box |
| `lag_12` | Target statement, then all 12 distractors | Final target box |

The two snapshots are privileged diagnostic controls. The short history tests basic application of one statement; comparing it with a long history changes length and distractor exposure. The primary contrast is `lag_0` versus `lag_12` within the 24 changed-target cases. Report unchanged targets separately; on these cases the old box is also the correct box, so an old-location prediction cannot diagnose stale-state behavior. `lag_4`, query-position and label breakdowns are secondary descriptions, not extra confirmatory tests.

Exclude every initial/final state-query pair observed in the original 4B preflight and every state-query pair from the completed lookup calibration, ignoring assignment order. New initial and final endpoint pairs must also be mutually disjoint. Same vocabulary/templates remain in use: this is not out-of-distribution generalization. The fixed cases are an assay sample, not an IID population sample or an untouched test set for later adaptive development.

## Decisions, evidence and bounds

Freeze code, tests, independent audit, protocol, exclusions, cases, prompts and schedule before any new model predictions. Preserve the freeze in private research context before running. This is a within-workflow freeze, not external preregistration. Each condition occupies each within-case serial position six times through cyclic rotation. No outputs are used to select another prompt or repeat a run.

Score all 216 prompts even if a control performs poorly, subject to the resource bounds. Each of the three controls (`initial_snapshot`, `final_snapshot`, `short_history`) must reach at least 33/36 for the overall control screen to pass. Also report changed and unchanged subsets; an overall pass does not establish uniform competence. A control failure prevents interpreting long-history errors as an isolated update/retention problem. Report exact paired discordant counts for the primary contrast, the accuracy difference and all error cases. No statistical significance threshold or population claim is specified. A ceiling result does not establish equivalence and does not justify automatically increasing difficulty.

An old-box error on a changed target is a descriptive error category, not proof of a stale-memory mechanism. The exact symbolic replay/last-relevant-statement baseline must solve all conditions; always-A gives 12/36 per condition. Ignoring updates answers 36/36 initial snapshots and 12/36 histories, demonstrating why unchanged cases must be separated.

Bound: 216 scored prompts, 1,200 scoring seconds, current process RSS at prompt boundaries at most 21 GiB. Transient loading peak is recorded separately; it does not trip the current-RSS gate. A cap stop is a partial resource result, not a competence failure. Use only cached weights, no API inference, training, GPU allocation or automatic retry. Save exact prompts, contextual token IDs, full-vocabulary candidate probabilities and their mass, unrestricted next token, current RSS and runtime versions. Audit evidence against an independent text parser and frozen hashes before reporting.

## Reproduction

From the repository root with the cached model and matching dependencies:

```bash
python -m pytest -q experiments/state_updates/test_paired_history.py
python experiments/state_updates/paired_history.py prepare /tmp/paired-history-new
HF_HUB_OFFLINE=1 python experiments/state_updates/paired_history.py run /tmp/paired-history-new
HF_HUB_OFFLINE=1 python experiments/state_updates/audit_paired_history.py /tmp/paired-history-new --tokenizer
```

Use a new output directory. The `prepare` step freezes the current files; preserve that freeze before `run`. The executed source is also copied into each evidence directory.
