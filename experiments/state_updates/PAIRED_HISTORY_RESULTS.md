# Paired history controls

## Result

All snapshot and single-update controls were perfect (36/36 each), as were the matched lag-0 and lag-4 histories. When all 12 distractors followed the target statement, accuracy fell to 32/36. All 4 errors occurred on changed targets. The observed discordant pairs are behavioral evidence within this fixed prompt family. They do not identify a memory mechanism or establish that a learned diagnosis would outperform a fixed correction.

| Condition | All cases | Changed target | Unchanged target | Input tokens | Mean A/B/C probability mass |
| --- | ---: | ---: | ---: | ---: | ---: |
| Initial snapshot | 36/36 | 24/24 | 12/12 | 211–211 | 0.9755 |
| Final snapshot | 36/36 | 24/24 | 12/12 | 211–211 | 0.9714 |
| Single target statement | 36/36 | 24/24 | 12/12 | 233–233 | 0.9517 |
| 12 distractors; target last (lag 0) | 36/36 | 24/24 | 12/12 | 341–341 | 0.9389 |
| 12 distractors; target followed by 4 | 36/36 | 24/24 | 12/12 | 341–341 | 0.9415 |
| 12 distractors; target first (lag 12) | 32/36 | 20/24 | 12/12 | 341–341 | 0.9452 |

The three controls required at least 33/36 each; all passed. The primary paired
contrast uses the 24 changed-target cases. Comparing lag 0 with lag 12:
both correct = 20, correct only at lag 0 = 4, correct only at lag 12 = 0,
both wrong = 0. The observed accuracy difference (lag 0 minus lag 12) is
16.67 percentage points. The 12 unchanged-target pairs are
reported separately in the saved summary. Repeated conditions are measurements
of the same case, not 216 independent histories. No population or significance
claim follows from these small, balanced synthetic groups.

The unrestricted highest-probability next token was an answer letter on
216/216 prompts. The accuracy metric is still constrained choice, not
free-generation task completion.

## Matched comparison

The three long histories have identical initial states, final states, target
answers, distractor sequences and event multisets within each base case. Only
the target statement's insertion point changes. Actual tokenizer lengths were
checked equal before model inference and independently rechecked afterward.
Thus this comparison removes the length confound of the original unpaired lag
groups. Recency, absolute position and relative position still move together.

There are 36 base histories: all nine initial/final target-box transitions at
each of four initial query positions, with each object queried nine times.
Twenty-four targets change box; twelve receive a restatement of their existing
location. Other objects make 12 actual moves. The short-history condition
contains only the target statement and is a competence control; its comparison
with long histories changes length and distractor exposure.

The calibrated prose instruction and three static examples are retained.
History blocks explicitly ask for the latest location. Every initial and final
state-query endpoint is disjoint from all earlier preflight and lookup-calibration
endpoints and from every other new endpoint, ignoring assignment order. This
does not make the shared names, templates or small state space out of distribution.
The outputs are now observed and cannot serve as untouched evidence for later
adaptive development.

The independent symbolic reader solves every prompt by replaying location
statements. Always-A gives 12/36 per condition; ignoring updates gives 36/36
initial snapshots and 12/36 histories. These check the assay, not method novelty.

## Error cases

| Case | Condition | Target | Initial box | Gold | Prediction | Candidate mass |
| --- | --- | --- | --- | --- | --- | ---: |
| paired-000 | lag_12 | coin | B | C | B | 0.9473 |
| paired-020 | lag_12 | key | B | A | B | 0.9528 |
| paired-022 | lag_12 | ring | A | B | A | 0.9505 |
| paired-028 | lag_12 | ring | C | A | C | 0.9397 |

All 4 errors selected the target's initial box. The winning probabilities were 0.4182, 0.4474, 0.4247, 0.3889; the corresponding correct-box probabilities were 0.3961, 0.3862, 0.3799, 0.3512. These are probabilities over the full vocabulary, not renormalized A/B/C scores.

An old-location answer is only an error category on changed targets. On an
unchanged target it is correct, and on either group it does not by itself
establish a stale-memory mechanism. Exact final snapshots provide privileged
state information and are diagnostic controls, not deployable corrections.

## Execution and verification

The [protocol](paired_history_protocol.md), cases, schedule, prompt bytes, source
and audit were frozen before this inference run. Freeze SHA256:
`45fca001f0804a79afb67cbf4cc0c9dea660559a48ef213d8e8c6bc9d54bf013`. This was a workflow freeze, not external preregistration.
No prompt selection, model sweep, parameter fitting or automatic retry occurred.

Cached Gemma 3 4B PT at `cc012e0a6d0787b4adcc0fa2c4da74402494554d` ran on CPU float32
with eager attention and eight threads, Torch 2.14.0+cu130 and Transformers
5.17.0. The 216 prompts took 477.2 scoring seconds;
loading/tokenizer preparation took 5.2 seconds. Maximum recorded
current RSS at scoring boundaries was 17.15 GiB;
lifetime peak RSS was 22.73 GiB. These are local runtime records,
not controlled speed benchmarks. The 1,200-second scoring and 21 GiB current-RSS
limits were respected. Loading peak is recorded separately from that guard.

All 54 repository tests passed; targeted Ruff checks passed. The saved-output
audit independently replayed all 216 prompt labels and verified endpoint
exclusions, pairing, schedules, token IDs and lengths, probabilities, predictions,
source hashes, summary counts and control gates. Seven deliberate corruption
types are rejected by the audit tests. This is an agent-assisted implementation
and audit, not independent human replication. No paid inference, model download,
training or GPU allocation was used.

## Reproduce

The [evidence bundle](../../evidence/state_updates/paired_history_v1/) contains
the frozen sources, exclusions, full prompts, predictions, summary and audit.
Execution timestamps are retained as provenance in JSON records.

```bash
python -m pytest -q tests experiments
HF_HUB_OFFLINE=1 python experiments/state_updates/audit_paired_history.py evidence/state_updates/paired_history_v1 --tokenizer
```

See the [protocol](paired_history_protocol.md) for a new bounded run. Rerunning
these fixed cases is a reproduction, not a fresh evaluation sample. The earlier
[lookup calibration](CALIBRATION_RESULTS.md) and [original preflight](RESULTS.md)
remain preserved as distinct experiments.
