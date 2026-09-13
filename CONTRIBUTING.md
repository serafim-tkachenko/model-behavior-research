# Research standards

Start from a question and observable outcome. State competing explanations, simplest baseline, inference-time information, independent units, metric and stopping rule.

Separate development from confirmation. Fit preprocessing and select methods without test data. Preserve failed controls, exclusions and amendments. Output text alone is not an intent label.

Record source/config/input hashes, model/data revisions, seeds, numerical settings, device, runtime and per-example outputs. Preserve immutable execution snapshots. Trace claims to raw records and controls; distinguish regenerated summaries from model reruns.

GPU jobs need a measured pilot before scaling and resumable outputs. Generated code must run only inside the declared isolation boundary. Keep toolkit improvements in SAE Feature Atlas. Internal representations need incremental-value comparisons with behavioral and same-state probe baselines.

Record human decisions and substantive assistance factually.
