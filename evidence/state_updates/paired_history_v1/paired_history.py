"""Frozen paired event-order assay using the calibrated prose prompt."""

import argparse
import json
import math
import random
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from calibration import (
    BOXES,
    MODEL,
    OBJECTS,
    REVISION,
    current_rss_gib,
    digest,
    dumps,
)
from calibration import (
    prompt as lookup_prompt,
)

ROOT = Path(__file__).resolve().parents[2]
SEED = 730301
CONDITIONS = (
    "initial_snapshot",
    "final_snapshot",
    "short_history",
    "lag_0",
    "lag_4",
    "lag_12",
)


def signature(state, target):
    return tuple(sorted(state.items())), target


def observed_signatures():
    seen = set()
    old = ROOT / "evidence/state_updates/dev_20260920_gemma4b/cases.json"
    for case in json.loads(old.read_text()):
        for stage in ("initial", "final"):
            seen.add(signature(case[stage], case["target"]))
    for split in ("development", "check"):
        path = ROOT / f"evidence/state_updates/lookup_calibration_v2/{split}_cases.json"
        for case in json.loads(path.read_text()):
            seen.add(signature(dict(case["assignments"]), case["target"]))
    return seen


def make_cases():
    rng = random.Random(SEED)
    cells = [(p, a, b) for p in range(4) for a in BOXES for b in BOXES]
    rng.shuffle(cells)
    targets = list(OBJECTS) * 9
    rng.shuffle(targets)
    used = observed_signatures()
    cases = []
    for i, ((position, source, destination), target) in enumerate(zip(cells, targets)):
        for _ in range(100000):
            others = [o for o in OBJECTS if o != target]
            rng.shuffle(others)
            order = others[:position] + [target] + others[position:]
            initial = {o: source if o == target else rng.choice(BOXES) for o in order}
            state = initial.copy()
            distractors = []
            for _ in range(12):
                obj = rng.choice(others)
                box = rng.choice([b for b in BOXES if b != state[obj]])
                distractors.append([obj, box])
                state[obj] = box
            state[target] = destination
            a, b = signature(initial, target), signature(state, target)
            if a != b and a not in used and b not in used:
                break
        else:
            raise RuntimeError("Could not generate disjoint endpoints")
        used.update((a, b))
        cases.append(
            {
                "id": f"paired-{i:03d}",
                "target": target,
                "query_position": position,
                "source_box": source,
                "current_box": destination,
                "changed": source != destination,
                "initial": initial,
                "final": state,
                "distractors": distractors,
            }
        )
    return cases


def events(case, condition):
    update = [case["target"], case["current_box"]]
    if condition == "short_history":
        return [update]
    if condition.startswith("lag_"):
        insertion = 12 - int(condition.split("_")[1])
        return (
            case["distractors"][:insertion] + [update] + case["distractors"][insertion:]
        )
    if condition in ("initial_snapshot", "final_snapshot"):
        return []
    raise ValueError(condition)


def prompt(case, condition):
    state = case["final"] if condition == "final_snapshot" else case["initial"]
    text = lookup_prompt(
        {"assignments": list(state.items()), "target": case["target"]}, "prose"
    )
    updates = events(case, condition)
    if updates:
        question = (
            f"\nTo retrieve the {case['target']}, which box should you open?\nAnswer:"
        )
        text = text.removesuffix(question)
        text += "\nUpdates in order; use the latest location for each object:\n"
        text += "\n".join(f"The {o} is now in box {b}." for o, b in updates)
        text += question
    return text


def gold(case, condition):
    return (
        case["source_box"] if condition == "initial_snapshot" else case["current_box"]
    )


def schedule(cases):
    # Latin rotation: each condition occupies each serial position six times.
    return [
        (c, condition)
        for i, c in enumerate(cases)
        for condition in CONDITIONS[i % 6 :] + CONDITIONS[: i % 6]
    ]


def summarize(rows):
    groups = {}
    for condition in CONDITIONS:
        selected = [r for r in rows if r["condition"] == condition]
        group = {"correct": sum(r["correct"] for r in selected), "n": len(selected)}
        for field, values in (
            ("changed", (False, True)),
            ("query_position", range(4)),
            ("gold", BOXES),
        ):
            group[f"by_{field}"] = {
                str(v): {
                    "correct": sum(r["correct"] for r in selected if r[field] == v),
                    "n": sum(r[field] == v for r in selected),
                }
                for v in values
            }
        group["old_location_errors_changed_only"] = sum(
            r["changed"] and not r["correct"] and r["prediction"] == r["source_box"]
            for r in selected
            if condition != "initial_snapshot"
        )
        if selected:
            group["input_token_range"] = [
                min(r["input_tokens"] for r in selected),
                max(r["input_tokens"] for r in selected),
            ]
            group["mean_candidate_mass"] = sum(
                r["candidate_mass"] for r in selected
            ) / len(selected)
        groups[condition] = group
    pairs = {}
    indexed = {(r["case_id"], r["condition"]): r for r in rows}
    for changed in (False, True):
        counts = Counter()
        for r in rows:
            if r["condition"] != "lag_0" or r["changed"] != changed:
                continue
            delayed = indexed.get((r["case_id"], "lag_12"))
            if delayed:
                counts[f"lag0_{int(r['correct'])}_lag12_{int(delayed['correct'])}"] += 1
        pairs[str(changed)] = dict(counts)
    complete = len(rows) == 216 and len(indexed) == 216
    controls = ("initial_snapshot", "final_snapshot", "short_history")
    passed = complete and all(groups[c]["correct"] >= 33 for c in controls)
    return {
        "groups": groups,
        "paired_lag0_lag12_by_changed": pairs,
        "status": "complete_controls_passed"
        if passed
        else "complete_control_failure"
        if complete
        else "partial_not_a_competence_result",
    }


def prepare(directory):
    directory.mkdir(parents=True, exist_ok=False)
    cases = make_cases()
    (directory / "cases.json").write_text(dumps(cases))
    (directory / "excluded_snapshots.json").write_text(
        dumps(sorted(observed_signatures()))
    )
    prepared = [
        {
            "case_id": c["id"],
            "condition": condition,
            "prompt": prompt(c, condition),
            "gold": gold(c, condition),
        }
        for c, condition in schedule(cases)
    ]
    (directory / "prepared_prompts.json").write_text(dumps(prepared))
    for name in (
        "paired_history.py",
        "paired_history_protocol.md",
        "test_paired_history.py",
        "audit_paired_history.py",
        "calibration.py",
    ):
        (directory / name).write_bytes(Path(__file__).with_name(name).read_bytes())
    freeze = {
        "status": "frozen_before_inference_not_external_preregistration",
        "created_at_utc": datetime.now(UTC).isoformat(),
        "seed": SEED,
        "model": MODEL,
        "revision": REVISION,
        "device": "cpu",
        "dtype": "float32",
        "threads": 8,
        "max_scored_prompts": 216,
        "max_scoring_seconds": 1200,
        "max_scoring_rss_gib": 21,
        "memory_check": "current_RSS_at_prompt_boundaries; peak_reported_separately",
        "files": {
            p.name: digest(p.read_bytes()) for p in directory.iterdir() if p.is_file()
        },
    }
    (directory / "freeze.json").write_text(dumps(freeze))
    print(
        dumps(
            {
                "freeze_sha256": digest((directory / "freeze.json").read_bytes()),
                "cases": len(cases),
                "prompts": len(prepared),
            }
        )
    )


def run(directory):
    import resource

    import torch
    import transformers
    from transformers import AutoTokenizer, Gemma3ForConditionalGeneration

    freeze = json.loads((directory / "freeze.json").read_text())
    for name, expected in freeze["files"].items():
        assert digest((directory / name).read_bytes()) == expected, name
        if name.endswith(".py"):
            assert digest(Path(__file__).with_name(name).read_bytes()) == expected, name
    assert not (directory / "predictions.jsonl").exists(), "Refusing to overwrite a run"
    cases = json.loads((directory / "cases.json").read_text())
    prepared = json.loads((directory / "prepared_prompts.json").read_text())
    torch.set_num_threads(8)
    started = time.monotonic()
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL, revision=REVISION, local_files_only=True
    )
    # Verify actual token lengths, not just word counts, before model inference.
    lengths = {
        (r["case_id"], r["condition"]): len(tokenizer.encode(r["prompt"]))
        for r in prepared
    }
    for case in cases:
        assert len({lengths[case["id"], c] for c in ("lag_0", "lag_4", "lag_12")}) == 1
    model = Gemma3ForConditionalGeneration.from_pretrained(
        MODEL,
        revision=REVISION,
        local_files_only=True,
        dtype=torch.float32,
        attn_implementation="eager",
    ).eval()
    loaded = time.monotonic()
    rows = []
    stop_reason = None
    with (directory / "predictions.jsonl").open("x") as output:
        for (case, condition), item in zip(schedule(cases), prepared):
            rss = current_rss_gib()
            if time.monotonic() - loaded > 1200 or rss > 21:
                stop_reason = "prompt_boundary_resource_cap"
                break
            text = prompt(case, condition)
            assert item == {
                "case_id": case["id"],
                "condition": condition,
                "prompt": text,
                "gold": gold(case, condition),
            }
            prefix = tokenizer.encode(text)
            continuation = [tokenizer.encode(text + " " + b) for b in BOXES]
            assert all(
                ids[:-1] == prefix and len(ids) == len(prefix) + 1
                for ids in continuation
            )
            token_ids = [ids[-1] for ids in continuation]
            assert len(set(token_ids)) == 3
            with torch.inference_mode():
                logits = (
                    model(
                        **tokenizer(text, return_tensors="pt"),
                        logits_to_keep=1,
                        use_cache=False,
                    )
                    .logits[0, -1]
                    .float()
                )
            probabilities = logits.softmax(-1)[token_ids].tolist()
            assert all(math.isfinite(p) for p in probabilities)
            chosen = BOXES[max(range(3), key=probabilities.__getitem__)]
            row = {
                "case_id": case["id"],
                "condition": condition,
                "target": case["target"],
                "query_position": case["query_position"],
                "source_box": case["source_box"],
                "changed": case["changed"],
                "gold": gold(case, condition),
                "prediction": chosen,
                "correct": chosen == gold(case, condition),
                "candidate_probabilities": dict(zip(BOXES, probabilities)),
                "candidate_mass": sum(probabilities),
                "candidate_token_ids": token_ids,
                "unrestricted_next_token": tokenizer.decode([int(logits.argmax())]),
                "input_tokens": len(prefix),
                "prompt": text,
                "prompt_sha256": digest(text.encode()),
                "rss_before_prompt_gib": rss,
            }
            rows.append(row)
            output.write(json.dumps(row) + "\n")
            output.flush()
            if len(rows) % 12 == 0:
                print(
                    f"{len(rows)}/216 prompts; {time.monotonic() - loaded:.1f}s",
                    flush=True,
                )
    summary = {
        **summarize(rows),
        "model": MODEL,
        "revision": REVISION,
        "torch": torch.__version__,
        "transformers": transformers.__version__,
        "device": "cpu",
        "dtype": "float32",
        "threads": 8,
        "load_seconds": loaded - started,
        "scoring_seconds": time.monotonic() - loaded,
        "peak_rss_gib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20,
        "completed_at_utc": datetime.now(UTC).isoformat(),
        "stop_reason": stop_reason,
        "freeze_sha256": digest((directory / "freeze.json").read_bytes()),
        "scored_prompts": len(rows),
    }
    (directory / "summary.json").write_text(dumps(summary))
    (directory / "artifact_hashes.json").write_text(
        dumps(
            {
                p.name: digest(p.read_bytes())
                for p in directory.iterdir()
                if p.is_file() and p.name != "artifact_hashes.json"
            }
        )
    )
    print(dumps(summary), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "run"))
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    (prepare if args.action == "prepare" else run)(args.directory)
