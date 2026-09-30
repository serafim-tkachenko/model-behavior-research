# Snapshot lookup calibration

## Result

The selected **prose** format passes the reserved lookup screen. This supports developing paired history controls as a separate experiment. It does not establish a selective update failure, a memory mechanism or a repair-selection benefit.

| Split | Format | Correct | Accuracy | Wilson 95% reference | Mean candidate mass | Mean input tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Development | prose | 36/36 | 100.0% | 90.4–100.0% | 0.9732 | 211.0 |
| Development | table | 36/36 | 100.0% | 90.4–100.0% | 0.9781 | 163.0 |
| Check | prose | 108/108 | 100.0% | 96.6–100.0% | 0.9738 | 211.0 |
| Check | table | 108/108 | 100.0% | 96.6–100.0% | 0.9785 | 163.0 |

The 90% screen required 33/36 on development and 98/108 on the reserved check.
Both formats were fixed before inference. The saved development decision selected
`prose` before any reserved-case inference; prose was the predetermined
tie-break. The alternative format cannot rescue a failed selected format.

Wilson intervals are descriptive binomial references. These balanced synthetic
cases are not an IID deployment sample, and passing an observed-accuracy gate
does not establish population accuracy above 90%.

On the 108 paired reserved cases: both correct = 108,
prose only correct = 0, table only correct = 0,
both wrong = 0. The two renderings are paired
measurements of a case, not independent observations. No reserved-case errors were observed in either format.

The unrestricted top next token was an answer letter on 288/288
scored prompts. Scoring still measures constrained-choice lookup rather than
free-generation task completion. Different prompt lengths prevent an equal-cost
performance claim. A ceiling result does not establish equivalence of formats.

## What changed from the old pilot

The [old final-snapshot errors](RESULTS.md) were `dev-4-2` and `dev-12-5`.
Both explicitly placed the first-row key in C but selected A. A also happened to
match the old location, which was absent from those prompts: that coincidence
cannot diagnose stale memory. Their A/C probabilities were 0.4114/0.3832 and
0.4490/0.3789.

This comparison retains the old prose body grammar and question, and compares it
with one compact table. Both use identical static-lookup content in the worked
examples instead of the old movement examples. The shared instruction is also
specific to static lookup. Hence the experiment does not isolate which prompt
change affected competence or provide a paired old-versus-new prompt estimate.

There are 36 development and 108 reserved cases, balanced over queried row
position and all nine source/current-box pairs. Target names are balanced.
Every full assignment/query pair is disjoint from the old pilot and across the
new splits, ignoring row order. The source box is hidden design bookkeeping;
only current assignments appear. No history or update operation was tested.
The fixed names, templates and tiny synthetic state space limit generalization.

## Execution and audit

Used cached Gemma 3 4B PT at
`cc012e0a6d0787b4adcc0fa2c4da74402494554d`, CPU float32, eager attention and eight
threads, with Torch 2.14.0+cu130 and Transformers 5.17.0.
The completed run scored 288 prompts in 466.1 seconds,
with 4.6 seconds loading time and 22.76 GiB lifetime
peak RSS. These are local execution records, not controlled speed benchmarks.

The first attempt stopped before any scored prompt because loading peaked above
its conservative 21 GiB lifetime-peak limit. A loading-only diagnostic found
16.73 GiB resident after loading and about 6.31 GiB available. The amended run
checks current resident memory against 21 GiB at prompt boundaries and records
the lifetime peak separately. This amendment was frozen before any model answer;
prompts, cases, model, thresholds and the 900-second scoring cap were unchanged.
Both attempts, original protocols and executed sources are preserved.

Independent prompt parsing recovers every label. The saved-output audit checks
frozen prompt bytes, exact contextual continuation tokenization, probabilities,
predictions, row coverage, selection, decision gates and hashes. All 288
rows passed. This is an agent-assisted implementation, local execution and audit
of saved outputs; it is not independent human replication. No paid API, new
download, training or GPU allocation was used.

## Reproduce

The [protocol](calibration_protocol.md) fixes the design, limits and stopping rule.
The [complete evidence](../../evidence/state_updates/lookup_calibration_v2/) includes
cases, prompts, per-case probabilities, frozen source, selection and verification.
The [zero-row first attempt](../../evidence/state_updates/lookup_calibration_v1/)
records the resource stop. Execution timestamps are retained in the JSON records.

From the repository root in the existing Linux/WSL environment:

```bash
python -m pytest -q tests experiments
python experiments/state_updates/audit_calibration.py evidence/state_updates/lookup_calibration_v2 --tokenizer
HF_HUB_OFFLINE=1 python experiments/state_updates/calibration.py prepare outputs/fresh-lookup-calibration
HF_HUB_OFFLINE=1 python experiments/state_updates/calibration.py run outputs/fresh-lookup-calibration
python experiments/state_updates/audit_calibration.py outputs/fresh-lookup-calibration --tokenizer
```

The first two commands check existing evidence; the last three create a new run
and require the pinned cached model. Never reuse an output directory. The public
rerun uses the same fixed calibration cases, not a new untouched evaluation.
These check outcomes are now observed and must not guide a later test set while
being presented again as untouched evidence. The public
runner may have whitespace formatting changes; the executed source bytes are
preserved in each evidence directory and identified by `freeze.json`.
