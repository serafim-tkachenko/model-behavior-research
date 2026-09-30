"""Frozen, lookup-only prompt calibration using the cached 4B preflight model."""

import argparse
import hashlib
import json
import math
import random
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

BOXES = ("A", "B", "C")
OBJECTS = ("key", "coin", "ring", "pen")
FORMATS = ("prose", "table")
MODEL = "google/gemma-3-4b-pt"
REVISION = "cc012e0a6d0787b4adcc0fa2c4da74402494554d"
SEEDS = {"development": 730241, "check": 730249}
ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT / "evidence/state_updates/dev_20260920_gemma4b"
INSTRUCTION = (
    "Read the object locations. Several objects may share a box. "
    "Answer with the box letter only.\n\n"
)
DEMOS = (
    {
        "assignments": [["apple", "C"], ["cup", "B"], ["sock", "A"], ["ball", "B"]],
        "target": "apple",
    },
    {
        "assignments": [["apple", "B"], ["cup", "C"], ["sock", "A"], ["ball", "C"]],
        "target": "sock",
    },
    {
        "assignments": [["apple", "A"], ["cup", "C"], ["sock", "A"], ["ball", "B"]],
        "target": "ball",
    },
)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def current_rss_gib():
    """Resident footprint at prompt boundaries, distinct from peak loading RSS."""
    for line in Path("/proc/self/status").read_text().splitlines():
        if line.startswith("VmRSS:"):
            return int(line.split()[1]) / 2**20
    raise RuntimeError("The fixed Linux/WSL runtime must expose current RSS")


def dumps(data):
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def signature(case):
    return tuple(sorted(tuple(pair) for pair in case["assignments"])), case["target"]


def old_signatures():
    result = set()
    for case in json.loads((OLD / "cases.json").read_text()):
        for state in ("initial", "final"):
            result.add((tuple(sorted(case[state].items())), case["target"]))
    return result


def make_cases():
    """Balance positions and all nine source/current-box cells in each split.

    The source box is hidden bookkeeping for future assay design, not a model
    input or an observed event. This experiment measures static lookup only.
    """
    used = old_signatures()
    splits = {}
    for split, repeats in (("development", 1), ("check", 3)):
        rng = random.Random(SEEDS[split])
        cells = [
            (position, source, current)
            for _ in range(repeats)
            for position in range(4)
            for source in BOXES
            for current in BOXES
        ]
        rng.shuffle(cells)
        targets = list(OBJECTS) * (len(cells) // 4)
        rng.shuffle(targets)
        cases = []
        for i, ((position, source, current), target) in enumerate(zip(cells, targets)):
            for _ in range(10000):
                other = [o for o in OBJECTS if o != target]
                rng.shuffle(other)
                order = other[:position] + [target] + other[position:]
                assignments = [
                    [o, current if o == target else rng.choice(BOXES)] for o in order
                ]
                case = {
                    "id": f"{split}-{i:03d}",
                    "split": split,
                    "assignments": assignments,
                    "target": target,
                    "query_position": position,
                    "source_box": source,
                    "current_box": current,
                }
                if signature(case) not in used:
                    break
            else:
                raise RuntimeError("Could not draw a disjoint snapshot")
            used.add(signature(case))
            cases.append(case)
        splits[split] = cases
    return splits


def render(case, style):
    if style == "prose":
        body = "\n".join(f"The {o} is in box {b}." for o, b in case["assignments"])
    elif style == "table":
        body = "Object | Box\n" + "\n".join(
            f"{o} | {b}" for o, b in case["assignments"]
        )
    else:
        raise ValueError(style)
    return (
        body
        + f"\nTo retrieve the {case['target']}, which box should you open?\nAnswer:"
    )


def prompt(case, style):
    examples = "\n\n".join(
        render(demo, style) + " " + dict(demo["assignments"])[demo["target"]]
        for demo in DEMOS
    )
    return INSTRUCTION + examples + "\n\n" + render(case, style)


def choose_format(counts, n):
    # Integer arithmetic preserves the exact >=90% screen; prose wins a tie.
    eligible = [f for f in FORMATS if counts[f] * 10 >= n * 9]
    return max(eligible, key=lambda f: counts[f]) if eligible else None


def wilson(k, n):
    z = 1.959963984540054
    p = k / n
    scale = 1 + z * z / n
    center = (p + z * z / (2 * n)) / scale
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / scale
    return [center - half, center + half]


def summarize(rows):
    result = {}
    for split in ("development", "check"):
        result[split] = {}
        for style in FORMATS:
            group = [r for r in rows if r["split"] == split and r["format"] == style]
            if not group:
                continue
            k, n = sum(r["correct"] for r in group), len(group)
            result[split][style] = {
                "correct": k,
                "n": n,
                "accuracy": k / n,
                "wilson_95_descriptive": wilson(k, n),
                "mean_candidate_mass": sum(r["candidate_mass"] for r in group) / n,
                "mean_input_tokens": sum(r["input_tokens"] for r in group) / n,
                "by_query_position": {
                    str(pos): {
                        "correct": sum(
                            r["correct"] for r in group if r["query_position"] == pos
                        ),
                        "n": sum(r["query_position"] == pos for r in group),
                    }
                    for pos in range(4)
                },
                "by_label": {
                    b: {
                        "correct": sum(r["correct"] for r in group if r["gold"] == b),
                        "n": sum(r["gold"] == b for r in group),
                    }
                    for b in BOXES
                },
            }
        if result[split]:
            pairs = {}
            for row in rows:
                if row["split"] == split:
                    pairs.setdefault(row["case_id"], {})[row["format"]] = row["correct"]
            result[split]["paired_outcomes"] = dict(
                Counter(
                    f"prose_{int(p['prose'])}_table_{int(p['table'])}"
                    for p in pairs.values()
                    if set(p) == set(FORMATS)
                )
            )
    return result


def prepare(directory):
    directory.mkdir(parents=True, exist_ok=False)
    splits = make_cases()
    for split, data in splits.items():
        (directory / f"{split}_cases.json").write_text(dumps(data))
    prepared = [
        {
            "split": split,
            "case_id": c["id"],
            "format": style,
            "prompt": prompt(c, style),
            "gold": dict(c["assignments"])[c["target"]],
        }
        for split, cases in splits.items()
        for c in cases
        for style in FORMATS
    ]
    (directory / "prepared_prompts.json").write_text(dumps(prepared))
    paths = [
        Path(__file__),
        Path(__file__).with_name("calibration_protocol.md"),
        Path(__file__).with_name("test_calibration.py"),
    ]
    hashes = {p.name: digest(p.read_bytes()) for p in paths}
    for p in paths[:2]:
        (directory / p.name).write_bytes(p.read_bytes())
    hashes.update(
        {p.name: digest(p.read_bytes()) for p in directory.iterdir() if p.is_file()}
    )
    freeze = {
        "status": "frozen_before_calibration_inference_not_external_preregistration",
        "created_at_utc": datetime.now(UTC).isoformat(),
        "model": MODEL,
        "revision": REVISION,
        "seeds": SEEDS,
        "files": hashes,
        "max_scored_prompts": 288,
        "device": "cpu",
        "dtype": "float32",
        "threads": 8,
        "max_scoring_seconds": 900,
        "max_scoring_rss_gib": 21,
        "memory_check": "current_RSS_at_prompt_boundaries; loading_peak_recorded_separately",
    }
    (directory / "freeze.json").write_text(dumps(freeze))
    print(
        dumps(
            {
                "freeze_sha256": digest((directory / "freeze.json").read_bytes()),
                "cases": {k: len(v) for k, v in splits.items()},
            }
        )
    )


def run(directory):
    import resource

    import torch
    import transformers
    from transformers import AutoTokenizer, Gemma3ForConditionalGeneration

    freeze = json.loads((directory / "freeze.json").read_text())
    assert digest(Path(__file__).read_bytes()) == freeze["files"]["calibration.py"]
    for name, expected in freeze["files"].items():
        path = (
            directory / name
            if (directory / name).exists()
            else Path(__file__).with_name(name)
        )
        assert digest(path.read_bytes()) == expected, name
    if (directory / "predictions.jsonl").exists():
        raise FileExistsError("This frozen run already has predictions")
    torch.set_num_threads(8)
    started = time.monotonic()
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL, revision=REVISION, local_files_only=True
    )
    model = Gemma3ForConditionalGeneration.from_pretrained(
        MODEL,
        revision=REVISION,
        local_files_only=True,
        dtype=torch.float32,
        attn_implementation="eager",
    ).eval()
    loaded = time.monotonic()
    rows, decision = [], {"selected_format": None, "status": "running"}
    stop = False
    with (directory / "predictions.jsonl").open("x") as out:
        for split in ("development", "check"):
            cases = json.loads((directory / f"{split}_cases.json").read_text())
            for i, case in enumerate(cases):
                # Alternate order to avoid aligning every format with runtime order.
                styles = FORMATS if i % 2 == 0 else tuple(reversed(FORMATS))
                for style in styles:
                    if (
                        time.monotonic() - loaded > 900
                        or current_rss_gib() > 21
                    ):
                        stop = True
                        decision["status"] = (
                            "stopped_resource_cap_partial_not_a_competence_result"
                        )
                        break
                    text = prompt(case, style)
                    prefix = tokenizer.encode(text)
                    continuation = [tokenizer.encode(text + " " + b) for b in BOXES]
                    if any(
                        ids[:-1] != prefix or len(ids) != len(prefix) + 1
                        for ids in continuation
                    ):
                        raise ValueError(
                            "Answer tokens are not exact contextual continuations"
                        )
                    token_ids = [ids[-1] for ids in continuation]
                    if len(set(token_ids)) != 3:
                        raise ValueError("Answer labels must have distinct token IDs")
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
                    if not all(math.isfinite(p) for p in probabilities):
                        raise ValueError("Nonfinite model output")
                    chosen = BOXES[max(range(3), key=probabilities.__getitem__)]
                    gold = dict(case["assignments"])[case["target"]]
                    row = {
                        "case_id": case["id"],
                        "split": split,
                        "format": style,
                        "query_position": case["query_position"],
                        "target": case["target"],
                        "gold": gold,
                        "prediction": chosen,
                        "correct": chosen == gold,
                        "candidate_probabilities": dict(zip(BOXES, probabilities)),
                        "candidate_mass": sum(probabilities),
                        "candidate_token_ids": token_ids,
                        "unrestricted_next_token": tokenizer.decode(
                            [int(logits.argmax())]
                        ),
                        "input_tokens": len(prefix),
                        "prompt": text,
                        "prompt_sha256": digest(text.encode()),
                    }
                    rows.append(row)
                    out.write(json.dumps(row) + "\n")
                    out.flush()
                if stop:
                    break
                if (i + 1) % 6 == 0:
                    print(
                        f"{split}: {i + 1}/{len(cases)} cases; {time.monotonic() - loaded:.1f}s",
                        flush=True,
                    )
            if stop:
                break
            if split == "development":
                counts = {
                    f: sum(r["correct"] for r in rows if r["format"] == f)
                    for f in FORMATS
                }
                selected = choose_format(counts, len(cases))
                decision = {
                    "selected_format": selected,
                    "development_counts": counts,
                    "development_n": len(cases),
                    "selected_at_utc": datetime.now(UTC).isoformat(),
                    "status": "check_pending"
                    if selected
                    else "stop_no_development_format_passed",
                }
                (directory / "development_decision.json").write_text(dumps(decision))
                print(dumps(decision), flush=True)
                if selected is None:
                    break
            else:
                selected_rows = [
                    r
                    for r in rows
                    if r["split"] == "check"
                    and r["format"] == decision["selected_format"]
                ]
                k = sum(r["correct"] for r in selected_rows)
                decision["status"] = (
                    "lookup_screen_passed_history_assay_not_yet_validated"
                    if k * 10 >= len(cases) * 9
                    else "stop_selected_format_failed_reserved_check"
                )
    summary = {
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
        "freeze_sha256": digest((directory / "freeze.json").read_bytes()),
        "decision": decision,
        "groups": summarize(rows),
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
