# Migration provenance

Separated from SAE Feature Atlas on 13 September 2026. The [migration manifest](../artifacts/migration.json) records the source revision, maps every imported tracked file and gives original and initially migrated SHA-256 values. Subsequent documentation updates are ordinary Git changes.

Historical reports were copied byte-for-byte. The [original source snapshot](../artifacts/historical/original-source.zip) preserves the pre-separation tracked tree and original namespace. Release execution bundles preserve runtime sources separately.

Active imports are `model_behavior_research.scientific`. Reusable functionality comes from a revision-pinned SAE Feature Atlas dependency. Rebuilt outputs must record the new revision and must not silently overwrite historical reports. Private planning, career/application materials, authentication state and model caches are excluded.
