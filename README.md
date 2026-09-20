# Model Behavior Research

Independent experiments on learned representations and model behavior, by Serafim Tkachenko.

The main study asks whether the context in which an SAE feature activates helps predict what happens when that feature is edited. Selected features did activate in different contexts, but the tested predictors failed a basic comparison: a fit-set mean had lower pooled check error than every fitted model for all three features.

**[Read the study](reports/sae_context_study/report.md)** · [PDF](reports/sae_context_study/report.pdf) · [Prediction results](evidence/sae_prediction/prediction_summary.csv) · [Reproduce](docs/reproduction.md)

## The SAE study

The observational experiment used pretrained Gemma 3 4B and Gemma Scope 2 SAEs on 12,000 documents from FineWeb-Edu and Wikipedia. At layer 17, 14 of 24 selected entries passed the partner-composition test, and 3 passed a separate decoder-orthogonal displacement test. Layer 22 gave 18 and 6. These are results for selected entries, not estimates for the entire dictionary.

The intervention pilot covered three features and 96 feature-prompt cases from 95 duplicate groups. There were only 16 check groups per feature. Context changed some intervention effects, but selective effects beyond scalar gain remained unresolved. The prediction comparison used two diagnostic logit contrasts, not a validated behavioral task.

The [current report](reports/sae_context_study/report.md) puts the failed prediction comparison first and includes the retrospective constant baselines. The [longer report](reports/research_report/report.md) preserves the earlier methods, geometry survey and exploratory analyses.

## Code and evidence

- [SAE Feature Atlas](https://github.com/serafim-tkachenko/sae-feature-atlas) is the separate library for collecting activations, inspecting examples and comparing feature statistics.
- `src/model_behavior_research/scientific/` contains the study-specific sampling, statistics and intervention methods.
- `evidence/sae_prediction/` contains the rechecked per-case prediction errors, baseline comparisons and verification record.
- `reports/` contains the current study and historical reports, tables and figures.
- [Artifact downloads](artifacts/README.md) provide larger data archives, checksums and original runtime sources.

## Run the checks

Python 3.11 is the reference environment.

~~~bash
git clone https://github.com/serafim-tkachenko/model-behavior-research.git
cd model-behavior-research
uv sync --locked
uv run pytest -q
uv run python scripts/build_sae_context_report.py
~~~

Building the report uses committed tables and needs no GPU. Reconstructing those tables from saved inference requires the released intervention archive; rerunning model inference requires model access and a GPU. The [reproduction guide](docs/reproduction.md) separates these paths.

## State-update preflight

A new [development pilot](experiments/state_updates/README.md) checks whether a language model can use updated object locations and whether a generic reminder changes its errors. Exact state snapshots serve as competence controls. [Results and next decision](experiments/state_updates/RESULTS.md). This pilot is separate from the SAE study.

## Other experiments

The [1B study](reports/gemma1b_regimes_positive/scientific_report.md) was an earlier development pilot. A separate [coding-repair feasibility test](experiments/coding_forensics/RESULTS.md) produced 48 compliant repairs and no prohibited test edits, so it could not answer its intended question. The assay was stopped. Neither study adds independent evidence to the three-feature prediction result.

The [research status](research/STATUS.md) records completed work and open decisions. Experimental proposals are not completed results.

Code and original documentation are MIT licensed. See [data sources](DATA_SOURCES.md) for third-party material and [contributing](CONTRIBUTING.md) for development checks.
