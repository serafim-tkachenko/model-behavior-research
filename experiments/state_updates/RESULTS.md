# State-update preflight: first results

20 September 2026. Development assay, not a confirmed research finding.

## Decision

Continue only with task calibration. Do not start activation probes or claim a selective memory-update failure. Both models failed at least one snapshot competence control under the working 90% screen. The 4B model is close, but moving the threshold after observing its score would not resolve the ambiguity.

## Measured results

Each model evaluated the same 18 histories in four conditions, producing 72 scored inputs. These are 18 paired units, not 72 independent observations. Both models are pretrained, not instruction-tuned.

| Condition | Gemma 3 1B | Gemma 3 4B |
| --- | --- | --- |
| Initial assignments only | 11/18 | 17/18 |
| Full event history | 14/18 | 15/18 |
| History + generic reminder | 14/18 | 16/18 |
| Exact final assignments (oracle) | 8/18 | 16/18 |

For 1B the reminder fixed two wrong answers and broke two correct answers. For 4B it fixed two and broke one. The net 4B gain is one history; this is not evidence that reminders improve accuracy in a wider population. The oracle provides privileged state and changes length/serialization, so it is not a fair deployable repair baseline.

The unconstrained highest-probability next token was also one of the three answer tokens on all 144 scored inputs. Mean probability mass on the three candidates ranged from about 0.949 to 0.965 across model/condition aggregates. Thus a refusal to emit box letters is not the obvious explanation, but input-template and retrieval effects remain possible.

History scores by subsequent unrelated moves were 6/6, 5/6, 3/6 for 1B and 6/6, 5/6, 4/6 for 4B at lags 0, 4, 12. These are different sampled histories, so this is **not** a paired causal estimate of distraction or delay.

Exact symbolic replay scored 18/18 by construction; ignoring all updates scored 0/18; always answering A scored 6/18. The pilot deliberately changes every target. A last-relevant-event parser solves this direct-assignment task exactly, which limits its practical relevance beyond being a diagnostic assay.

## Execution and verification

The 1B run used approximately 51 seconds for the scoring loop; the 4B run approximately 195 seconds, excluding loading. Both used cached weights on CPU float32 with eight threads. These times are local execution records, not controlled model-speed benchmarks. The 4B process used roughly 18 GB RAM. No paid API, training or GPU allocation was used.

[1B evidence](../../evidence/state_updates/dev_20260920_v1/) and [4B evidence](../../evidence/state_updates/dev_20260920_gemma4b/) include cases, every prompt, answer probabilities, summaries and file hashes. Model revisions and library versions are in each summary. `analyze.py` reconstructs prompts and labels from the simulator and independently recounts predictions; all 144 rows passed these checks. Five simulator/prompt tests passed, and the complete repository suite passed 33 tests.

The 4B run was selected after inspecting the 1B failures and used the same cases. It is a sequential development check, not a held-out replication. The full [protocol](README.md) lists additional limitations and the eventual research question.

## Next bounded step

1. Inspect the two 4B errors on exact final assignments. Use a dedicated lookup-only calibration set, independent of these 18 histories, with balanced queried-object position and all old/new box transitions.
2. Compare the current prose representation against one compact table representation, with worked examples matched to each task. Fix this small comparison before running; do not search an unbounded list of prompts.
3. Only if snapshot retrieval passes the competence screen on a separate calibration check, create paired history variants differing in distractor lag. Include unchanged targets and counterbalance which object is queried.
4. If that calibration still fails, switch to a small instruction-tuned model or stop this assay. Do not buy more compute to compensate for an ambiguous task.

The research target remains whether an observable diagnosis predicts which correction works better than the best fixed correction on fresh cases. This pilot establishes neither that claim nor its novelty. Its useful outcome is identifying the measurement problem before investing in mechanistic analysis.
