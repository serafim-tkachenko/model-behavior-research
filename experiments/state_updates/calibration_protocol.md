# Snapshot lookup calibration

## Scope and rationale

This bounded calibration asks whether a cached Gemma 3 4B pretrained model can
retrieve an explicitly supplied object location under two fixed renderings.
It does not test updating, memory mechanisms, intervention selection or novelty.

In the preceding 18-history preflight, both wrong final-snapshot answers queried
the first-row key in box C and selected A. Candidate probabilities were
A/C = 0.4114/0.3832 and 0.4490/0.3789. Although A also matched the old location,
that old location was absent from these snapshot prompts: the errors cannot be
attributed to stale memory. Worked examples contained moves while the evaluated
snapshot bodies did not. These observations motivate calibration; they do not
identify the cause of failure.

## Frozen comparison

Compare exactly two formats, `prose` and `table`, on the same cases. Prose retains
the original body grammar and question. The compact table uses `Object | Box`
and four rows. Both have the same lookup-only instruction and three semantically
identical static worked examples, with one answer per box and disjoint example
object names. The examples are rendered in their respective format.

Replacing the old movement demonstrations is a shared intervention. This is
therefore a prose-versus-table comparison within a new static-lookup prompt,
not an isolated estimate of why the old prompt failed. Token lengths may differ;
record them and do not infer an equal-compute benefit from accuracy alone.

Create 36 development cases and 108 reserved check cases. Each split balances
all four queried-object row positions crossed with all nine source/current box
pairs: one or three cases per cell. Targets are balanced across key, coin, ring
and pen. Other locations and object row order are randomized with fixed seeds
730241 and 730249. Reject duplicate `(full assignment, queried object)` pairs
regardless of row order, including every initial and final snapshot from the
original 4B pilot. The check set is also disjoint from development.

Only current assignments and the query enter the model. The source box is hidden
design bookkeeping; a third of cases have source=current, and this is not a
measurement of changed-versus-unchanged tracking. No histories or move events
are supplied. Fixed names and templates limit transfer claims.

## Selection and stopping rules

Freeze code, protocol, exact cases and all prompts by SHA-256 before inference.
Keep a private Git record of that snapshot. This is an internally timestamped
protocol, not an externally preregistered confirmatory study.

1. Score both formats on development. A format must score at least 33/36 to
   pass the existing observed-accuracy screen of 90%.
2. Choose the eligible format with the highest count; choose prose on a tie.
   Persist this choice before any check-set inference. If neither passes,
   stop without scoring the reserved set.
3. If eligible, score both fixed formats on all 108 reserved cases. The already
   selected format must score at least 98/108. Results from the other format
   describe the paired comparison; they cannot rescue a failing selected format.
4. A pass supports developing paired history controls as a separate experiment.
   It establishes neither isolated memory-update errors nor repair-selection
   benefit. A fail stops this calibration; there is no model substitution,
   extra prompt search or new training in this run.

The experimental unit is a snapshot case. Its two formats are paired, not two
independent samples. Report exact counts, errors by queried position and answer,
paired discordance counts, candidate probability mass and token lengths.
Wilson 95% intervals are descriptive binomial references; the balanced synthetic
sample is not an IID deployment sample, so population coverage and population
competence are not asserted. The 90% threshold is a screening rule, not a test
that population accuracy exceeds 90%.

## Runtime and evidence

Use `google/gemma-3-4b-pt` at
`cc012e0a6d0787b4adcc0fa2c4da74402494554d`, cached local files only, CPU float32,
eager attention and eight threads. Use the existing environment without upgrades.
Score exact single-token ` A`, ` B`, ` C` continuations, verifying contextual
tokenization for every prompt. Record full-vocabulary candidate probabilities
and the unrestricted top token. No sampled generation is used.

Maximum: 288 scored prompts, 900 scoring seconds, 21 GiB current resident memory
checked at prompt boundaries. Loading time and process peak RSS are recorded
separately. Exceeding a scoring resource bound stops the run
and preserves partial evidence; it is not interpreted as a competence failure.
No paid API, download, GPU allocation or model training is authorized by this
protocol. Outputs must use a new directory; previous runs are never overwritten.

Before inference, independent prompt parsing must recover every label and tests
must verify balance, semantic disjointness, hidden source-box exclusion and exact
screen boundaries. After inference, recheck prompts against frozen bytes,
reconstruct labels independently, recount decisions and verify saved hashes.
Preserve cases, prompts, probabilities, versions, selection, timings and outputs.

## Resource amendment before any scored prompt

The original run stopped with zero scored prompts because the model-loading
peak reached 22.73 GiB, exceeding a 21 GiB peak-RSS cap. A loading-only diagnostic
measured current resident memory at 16.73 GiB after loading, with about 6.31 GiB
available in WSL. A lifetime peak is unsuitable for detecting subsequent working
memory pressure: it remains high even after temporary loading buffers are freed.

The replacement run checks current resident memory against the same 21 GiB
bound at prompt boundaries and still reports the lifetime peak. The first run,
its original protocol and its zero-row outcome remain preserved. The model,
dtype, prompts, cases, accuracy thresholds and 900-second scoring cap are
unchanged. This amendment is frozen before any model answer has been scored.
