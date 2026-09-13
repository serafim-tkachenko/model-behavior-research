# Evidence archive

Frozen original archives are published in the [evidence release](https://github.com/serafim-tkachenko/model-behavior-research/releases/tag/evidence-2026-09-13). The machine-readable [manifest](manifest.json) records complete archive and part SHA-256 hashes, sizes, member roots and suggested destinations. Files over 1 GiB are split into ordered binary parts.

Download and verify an archive (Python standard library only):

~~~bash
python scripts/download_artifacts.py foundation_layer17_collection.zip
~~~

The command downloads into .release/, verifies every part, reconstructs the ZIP and verifies its full hash. It does not extract files. Inspect archive contents and extract into the documented destination; source bundles belong in separate directories so that historical code cannot overwrite this checkout. See [reproduction](../docs/reproduction.md) and [data licenses](../DATA_SOURCES.md).

| Archive | Bytes | Suggested extraction destination |
|---|---:|---|
| context_intervention_bundle.zip | 987462 | artifacts/extracted/context_intervention_bundle |
| context_intervention_bundle_v2.zip | 986685 | artifacts/extracted/context_intervention_bundle_v2 |
| context_intervention_report.zip | 1377528 | artifacts/extracted/context_intervention_report |
| context_intervention_results.zip | 4018930 | artifacts/extracted/context_intervention_results |
| foundation_analysis.zip | 593524722 | . |
| foundation_colab_bundle.zip | 23344144 | artifacts/extracted/foundation_colab_bundle |
| foundation_final_delta.zip | 118128086 | . |
| foundation_layer17_collection.zip | 2109047516 | data/processed/gemma4b_foundation_v1_l17 |
| foundation_layer22_collection.zip | 2209788512 | data/processed/gemma4b_foundation_v1_l22 |
| foundation_native_residuals.zip | 2108028016 | . |
| foundation_runtime_sources.zip | 528985 | artifacts/extracted/foundation_runtime_sources |
| gemma1b_regimes_positive_analysis_bundle.zip | 120264994 | artifacts/extracted/gemma1b_regimes_positive_analysis_bundle |
| gemma4b_foundation_report.zip | 7890771 | artifacts/extracted/gemma4b_foundation_report |
| geometry_extension.zip | 18917 | artifacts/extracted/geometry_extension |
| phase1_research_report.zip | 6716127 | artifacts/extracted/phase1_research_report |
| sae_feature_atlas_source.zip | 458535 | artifacts/extracted/sae_feature_atlas_source |

The [original source snapshot](historical/original-source.zip) preserves the complete tracked tree before separation. Its checksum is in [archive inspection](archive-inspection.json). Historical reports were copied unchanged; [migration.json](migration.json) records source paths and hashes. Raw model weights and personal research planning are excluded.
