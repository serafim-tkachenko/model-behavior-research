"""Recheck the pilot's decoder-effect prediction task, including constants.

Uses saved inference, not new model runs. Run from the repository root:
    uv run python scripts/check_prediction_baselines.py --archive .release/context_intervention_results.zip
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from model_behavior_research.scientific.intervention_analysis import prediction_checks
from model_behavior_research.scientific.intervention_math import paired_bootstrap


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("evidence/sae_prediction"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    forecasts, interactions = [], []
    max_difference = 0.0
    with zipfile.ZipFile(args.archive) as archive:
        complete = json.loads(archive.read("full_v3/complete.json"))
        for name, digest in complete["files"].items():
            data = archive.read("full_v3/" + name)
            if hashlib.sha256(data).hexdigest() != digest:
                raise ValueError(f"Hash mismatch: {name}")
            record = json.loads(data)
            prompt = record["prompt"]
            common = {
                k: prompt[k]
                for k in ("feature_id", "text_id", "duplicate_group", "source", "split")
            }
            effects = {}
            for row in record["records"]:
                if row["status"] != "ok":
                    raise ValueError(f"Unsuccessful intervention: {name}")
                cells = np.asarray(row["cells"])
                before, after = cells[1] - cells[0], cells[3] - cells[2]
                interaction = after - before
                max_difference = max(
                    max_difference,
                    float(np.max(np.abs(interaction - row["interaction"]))),
                )
                residual = (
                    after - before * (before @ after) / (before @ before)
                    if before @ before > 1e-8
                    else np.array([np.nan])
                )
                interactions.append(
                    dict(
                        common,
                        direction=row["direction"],
                        fraction=row["fraction"],
                        sign=row["sign"],
                        dose=row["dose"],
                        interaction_norm=float(np.linalg.norm(interaction)),
                        beyond_gain_norm=float(np.linalg.norm(residual)),
                    )
                )
                dose = row["dose"]
                if dose in effects:
                    np.testing.assert_allclose(
                        before, effects[dose], rtol=0, atol=1e-12
                    )
                    continue
                effects[dose] = before
                word = re.search(r"[A-Za-z]+$", prompt.get("excerpt", ""))
                forecasts.append(
                    dict(
                        common,
                        dose=dose,
                        effect=before,
                        **{
                            k: record["baseline"][k]
                            for k in ("encoder", "norm", "context")
                        },
                        **{
                            f"pc{i}": v for i, v in enumerate(record["baseline"]["pc8"])
                        },
                        token_pos=prompt["token_pos"],
                        token_id=str(prompt["token_id"]),
                        support=np.log1p(prompt["n_positive_features"]),
                        trailing_digit_count=prompt["trailing_digit_count"],
                        trailing_letter_count=len(word.group()) if word else 0,
                    )
                )

    frame = pd.DataFrame(forecasts)
    fit_groups = set(frame.loc[frame.split == "fit", "duplicate_group"])
    check_groups = set(frame.loc[frame.split == "check", "duplicate_group"])
    if not fit_groups.isdisjoint(check_groups):
        raise ValueError("Fit/check duplicate-group leakage")
    errors = prediction_checks(frame, include_pc_only=True)
    historical = pd.read_csv(
        root / "reports/research_report/tables/pilot_prediction_errors.csv",
        dtype={"duplicate_group": str},
    )
    keys = [
        "feature_id",
        "dose",
        "train_source",
        "model",
        "text_id",
        "duplicate_group",
        "source",
    ]
    compared = historical.merge(
        errors,
        on=keys,
        how="left",
        validate="one_to_one",
        suffixes=("_saved", "_recomputed"),
        indicator=True,
    )
    if not compared._merge.eq("both").all():
        raise ValueError("Some saved prediction errors were not reproduced")
    np.testing.assert_allclose(
        compared.mse_saved, compared.mse_recomputed, rtol=0, atol=1e-12
    )
    constants = []
    for (feature, dose), group in frame.groupby(["feature_id", "dose"]):
        for source in ["pooled", *sorted(group.source.unique())]:
            train, test = group[group.split == "fit"], group[group.split == "check"]
            if source != "pooled":
                train, test = train[train.source == source], test[test.source != source]
            mean = np.stack(train.effect).mean(axis=0)
            for row in test.itertuples():
                for model, prediction in (
                    ("zero", np.zeros_like(mean)),
                    ("fit_mean", mean),
                ):
                    constants.append(
                        {
                            "feature_id": feature,
                            "dose": dose,
                            "train_source": source,
                            "model": model,
                            "text_id": row.text_id,
                            "duplicate_group": row.duplicate_group,
                            "source": row.source,
                            "mse": float(np.mean((row.effect - prediction) ** 2)),
                        }
                    )
    all_errors = pd.concat([errors, pd.DataFrame(constants)], ignore_index=True)
    summary = (
        all_errors.groupby(["feature_id", "train_source", "model"])
        .mse.mean()
        .reset_index()
    )
    measured = pd.DataFrame(interactions)
    pair_keys = [
        "feature_id",
        "text_id",
        "duplicate_group",
        "source",
        "split",
        "fraction",
        "sign",
        "dose",
    ]
    random = (
        measured[measured.direction.str.startswith("random_")]
        .groupby(pair_keys)[["interaction_norm", "beyond_gain_norm"]]
        .mean()
        .reset_index()
    )
    paired = measured[measured.direction == "learned"].merge(
        random, on=pair_keys, suffixes=("", "_random"), validate="one_to_one"
    )
    controls = []
    for feature, group in paired[paired.split == "check"].groupby("feature_id"):
        for metric in ("interaction_norm", "beyond_gain_norm"):
            controls.append(
                dict(
                    feature_id=int(feature),
                    metric=metric,
                    **paired_bootstrap(
                        group[metric] - group[metric + "_random"], group.duplicate_group
                    ),
                )
            )
    args.output.mkdir(parents=True, exist_ok=True)
    all_errors.to_csv(args.output / "prediction_errors.csv", index=False)
    summary.to_csv(args.output / "prediction_summary.csv", index=False)
    pd.DataFrame(controls).to_csv(args.output / "paired_controls.csv", index=False)
    verification = {
        "scope": "Saved-inference reanalysis. Constants added retrospectively; no fresh GPU run.",
        "archive_sha256": hashlib.sha256(args.archive.read_bytes()).hexdigest(),
        "prompt_files_verified": len(complete["files"]),
        "factorial_comparisons": len(measured),
        "duplicate_groups": int(frame.duplicate_group.nunique()),
        "fit_check_groups_disjoint": True,
        "saved_prediction_errors_reproduced": len(compared),
        "max_prediction_error_difference": float(
            abs(compared.mse_saved - compared.mse_recomputed).max()
        ),
        "max_interaction_difference": max_difference,
        "pooled_check_groups_per_feature": frame[frame.split == "check"]
        .groupby("feature_id")
        .duplicate_group.nunique()
        .to_dict(),
    }
    (args.output / "verification.json").write_text(
        json.dumps(verification, indent=2) + "\n"
    )
    print(json.dumps(verification, indent=2))
    print(
        summary[summary.train_source == "pooled"]
        .pivot(index="feature_id", columns="model", values="mse")
        .to_string()
    )


if __name__ == "__main__":
    main()
