# Reproduction and provenance

The split separates library maintenance from study claims. The current environment pins SAE Feature Atlas to commit 553b89f4da20145fd92e1e20be192faac6dc8fa8. Install with Python 3.11 and uv:

~~~bash
uv sync --locked
uv run pytest -q
uv run python experiments/coding_forensics/pilot.py --validate
~~~

The lock is the current development environment, not a claim that historical experiments used these package versions. Frozen runtime sources, environment_freeze.txt files, Colab requirements and the original source ZIP preserve historical execution. Exact numerical reproduction should use the recorded runtime and model/data revisions. Namespace changes are described in [migration](migration.md).

## Saved evidence without GPU inference

Reports and their tables are available immediately after cloning. Complete coding pilot outputs are under evidence/coding_forensics. Audit the completed run without loading a model:

~~~bash
uv run python experiments/coding_forensics/audit.py evidence/coding_forensics/dev_v2
~~~

The audit writes summary files beside the run, so compare changes with Git before committing them. The original aborted run is retained separately.

For the SAE studies, download verified ZIPs with scripts/download_artifacts.py; see the [inventory](../artifacts/README.md). For the 4B study, extract the two collection archives into data/processed/gemma4b_foundation_v1_l17 and l22 respectively. Then extract foundation_native_residuals.zip, foundation_analysis.zip and foundation_final_delta.zip at the repository root, in that order. These data archives contain data/ paths. Extract source bundles into separate directories.

~~~bash
uv run python scripts/verify_foundation_artifacts.py
~~~

This recomputes selected integrity and numerical checks and writes reports/gemma4b_foundation_v1/verification.json. It checks saved evidence; it is not a fresh model replication.

For intervention reconstruction, extract context_intervention_results.zip into outputs/context_download_v3. Copy its pilot/ directory to outputs/context_pilot_v3. The full_v3/ directory contains the full executed run; do not pool earlier smoke runs into it. Follow the [combined report reproduction guide](research_report_handoff.md) for verification and signed analysis. Historical report builders use fixed paths and can overwrite report files; run them on a separate checkout if preserving the archive unchanged.

## Fresh GPU experiments

Study design and compute requirements are in [scientific experiment](scientific_experiment.md), [foundation protocol](foundation_protocol.md), and [coding pilot protocol](../experiments/coding_forensics/protocol.md). Obtain gated model access separately. No model weights are distributed.

The Colab notebook clones this repository and installs the study-specific historical requirements plus the pinned toolkit dependency. The local uv.lock is maintained separately. A successful local smoke check does not establish compatibility with every hosted runtime.

The coding pilot needs Linux/WSL, bubblewrap, and the exact cached Qwen model revision declared by its runner. Its validate command checks the synthetic tasks without model inference. Its run command performs inference and sandboxed code evaluation. The observed behavior gate failed; the archived result does not justify scaling the same assay. A follow-up should first improve the behavioral task and freeze its evaluation protocol.

## Verification performed for the split

- Historical reports: all 225 tracked report files copied unchanged from the source commit.
- Toolkit: 34 unit tests, clean environment installation, wheel/source build, and Gemma 3 1B layer-13 SAE smoke check on RTX 3080 Ti with bfloat16 residuals.
- Research: 28 method tests passed in the clean locked environment; the coding harness passed 96 task/control checks. Repository CI repeats package tests and builds.
- Publication checks: archive inventories and SHA-256 hashes; credential-pattern scan of text members and repository source. This is not an independent review of the scientific claims.

See [contribution disclosure](../CONTRIBUTIONS.md) for the role of LLM assistance. Human review, independent annotation and independent replication must be reported only when actually performed.
