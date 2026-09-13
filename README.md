# Model Behavior Research

Empirical studies of model representations, interventions and coding-assistant behavior. This repository contains questions, methods, code, evidence and limitations. The reusable library lives in [SAE Feature Atlas](https://github.com/serafim-tkachenko/sae-feature-atlas).

## Start here

Read the [research brief](RESEARCH.md) for the question, methods, results and limits. Then inspect the [claim ledger](research/claims.md), [research status](research/STATUS.md), and [review walkthrough](research/review.md). The [proposed next experiment](experiments/coding_forensics/next_protocol.md) is separate from completed results.

## Studies and current answers

| Study | Evidence | Current conclusion |
|---|---|---|
| SAE context and interventions | [Combined report](reports/research_report/report.md) · [PDF](reports/research_report/report.pdf) | Selected entries show contextual organization. Selective effects beyond gain and incremental prediction remain unestablished. |
| 4B foundation | [Report](reports/gemma4b_foundation_v1/scientific_report.pdf) · [protocol](docs/foundation_protocol.md) | Separate partner and orthogonal tests on two layers of one model; not dictionary-wide prevalence or semantic validation. |
| 1B development study | [Report](reports/gemma1b_regimes_positive/scientific_report.md) | Pilot evidence with limited robustness; retained as a historical snapshot. |
| Coding repair boundaries | [Results](experiments/coding_forensics/RESULTS.md) · [protocol](experiments/coding_forensics/protocol.md) | 48/48 compliant repairs, no prohibited test edits. Behavior gate failed; the synthetic assay was stopped. |

Original reports are unchanged. Existing intervention data remain development material for stronger claims. No independent semantic mechanism, general safety guarantee or model intent is established.

## Reproduce

Python 3.11 is the reference environment.

~~~bash
git clone https://github.com/serafim-tkachenko/model-behavior-research.git
cd model-behavior-research
uv sync --locked
uv run pytest -q
~~~

The [reproduction guide](docs/reproduction.md) distinguishes saved-output analysis from fresh GPU experiments. The [artifact inventory](artifacts/README.md) gives release downloads, SHA-256 hashes and extraction destinations. Large archives are release assets, not Git objects. Obtain model weights separately.

The coding pilot's complete small outputs, including the aborted run, are under [evidence/coding_forensics](evidence/coding_forensics). The [SAE audit](evidence/sae_audit) checks saved provenance and selected headlines; it is not a fresh GPU replication.

## Repository map

- `research/`: claim ledger, decisions and review workflow.
- `src/model_behavior_research/scientific/`: study-specific SAE methods.
- `experiments/`: configurations, coding pilot and results.
- `scripts/` and `notebooks/`: orchestration and report builders.
- `reports/`: historical reports, figures, tables and appendices.
- `tests/`: experimental-method regression tests.
- `artifacts/`: inventory, migration provenance and original source snapshot.
- `evidence/`: small verified outputs.

Read [research standards](CONTRIBUTING.md), [migration](docs/migration.md), [data attribution](DATA_SOURCES.md) and [contribution disclosure](CONTRIBUTIONS.md). Original code and author-written documentation are MIT licensed. Third-party data, quoted passages and model weights retain their own licenses.

This is a research archive and working study repository, not a production deployment system.
