# Evidence archive

Frozen evidence and runtime sources are published in the [evidence release](https://github.com/serafim-tkachenko/model-behavior-research/releases/tag/evidence-2026-09-13). The machine-readable [manifest](manifest.json) records current public archive and part SHA-256 hashes, sizes, member roots and suggested destinations. Files over 1 GiB are split into ordered binary parts.

Download and verify an archive (Python standard library only):

~~~bash
python scripts/download_artifacts.py foundation_layer17_collection.zip
~~~

The command downloads into .release/, verifies every part, reconstructs the ZIP and verifies its full hash. It does not extract files. Inspect archive contents and extract into the documented destination; source bundles belong in separate directories so that historical code cannot overwrite this checkout. See [reproduction](../docs/reproduction.md) and [data licenses](../DATA_SOURCES.md).

| Archive | Bytes | Suggested extraction destination |
|---|---:|---|
| context_intervention_bundle.zip | 988212 | artifacts/extracted/context_intervention_bundle |
| context_intervention_bundle_v2.zip | 987439 | artifacts/extracted/context_intervention_bundle_v2 |
| context_intervention_report.zip | 1377528 | artifacts/extracted/context_intervention_report |
| context_intervention_results.zip | 4018930 | artifacts/extracted/context_intervention_results |
| foundation_analysis.zip | 593524722 | . |
| foundation_colab_bundle.zip | 23344634 | artifacts/extracted/foundation_colab_bundle |
| foundation_final_delta.zip | 118128086 | . |
| foundation_layer17_collection.zip | 2109047516 | data/processed/gemma4b_foundation_v1_l17 |
| foundation_layer22_collection.zip | 2209788512 | data/processed/gemma4b_foundation_v1_l22 |
| foundation_native_residuals.zip | 2108028016 | . |
| foundation_runtime_sources.zip | 529370 | artifacts/extracted/foundation_runtime_sources |
| gemma1b_regimes_positive_analysis_bundle.zip | 120263182 | artifacts/extracted/gemma1b_regimes_positive_analysis_bundle |
| gemma4b_foundation_report.zip | 7891035 | artifacts/extracted/gemma4b_foundation_report |
| geometry_extension.zip | 18917 | artifacts/extracted/geometry_extension |
| phase1_research_report.zip | 6762472 | artifacts/extracted/phase1_research_report |
| sae_feature_atlas_source.zip | 459015 | artifacts/extracted/sae_feature_atlas_source |

The original pre-separation source snapshot is retained in the owner's private context archive because it contains internal handoffs. Its original checksum remains in [archive inspection](archive-inspection.json). Public execution bundles above preserve the frozen runtime sources. Historical reports remain unchanged; [migration.json](migration.json) records the original migration paths and hashes, rather than the current file inventory. Raw model weights are excluded.

Public copies omit internal handoffs and editorial housekeeping. The [documentation change record](public-documentation-changes.json) lists original and public hashes and every changed member. Scientific data, numerical outputs and executable source files are unchanged. Report prose differs only in editorial datelines; PDFs were rebuilt. Each changed archive includes its own documentation manifest. Frozen experiment manifests retain their original execution provenance.
