"""Development-only state-update assay; exact simulator and local model preflight."""

import argparse
import hashlib
import json
import random
import time
from collections import Counter
from pathlib import Path

BOXES = ("A", "B", "C")
OBJECTS = ("key", "coin", "ring", "pen")
CONDITIONS = (
    "initial_snapshot",
    "history",
    "history_reminder",
    "final_snapshot_oracle",
)
REVISION = "fcf18a2a879aab110ca39f8bffbccd5d49d8eb29"
DEMO = """Track where objects are. Several objects may share a box. A move changes only the named object's location. Answer with the box letter only.

The apple is in box A. The cup is in box B.
Move the apple to box C.
To retrieve the apple, which box should you open?
Answer: C

The hat is in box C. The ball is in box A.
Move the hat to box B.
To retrieve the ball, which box should you open?
Answer: A

The book is in box A. The sock is in box C.
Move the book to box B.
To retrieve the book, which box should you open?
Answer: B

"""


def replay(initial, events):
    state = dict(initial)
    for obj, box in events:
        if obj not in state or box not in BOXES:
            raise ValueError("Invalid event")
        state[obj] = box
    return state


def cases(seed=20260920, per_lag=6):
    if per_lag < 3 or per_lag % 3:
        raise ValueError("per_lag must be a positive multiple of three")
    rng = random.Random(seed)
    result = []
    for lag in (0, 4, 12):
        for i in range(per_lag):
            target = rng.choice(OBJECTS)
            gold = BOXES[i % 3]
            initial = {obj: rng.choice(BOXES) for obj in OBJECTS}
            initial[target] = BOXES[(i + 1) % 3]
            events = [(target, gold)]
            for _ in range(lag):
                obj = rng.choice([o for o in OBJECTS if o != target])
                current = replay(initial, events)[obj]
                dest = rng.choice([b for b in BOXES if b != current])
                events.append((obj, dest))
            result.append(
                {
                    "id": f"dev-{lag}-{i}",
                    "target": target,
                    "initial": initial,
                    "events": events,
                    "final": replay(initial, events),
                    "lag": lag,
                }
            )
    return result


def prompt(case, condition):
    if condition not in CONDITIONS:
        raise ValueError(condition)
    state = case["final"] if condition == "final_snapshot_oracle" else case["initial"]
    body = "\n".join(f"The {o} is in box {b}." for o, b in state.items())
    if condition.startswith("history"):
        body += "\n" + "\n".join(f"Move the {o} to box {b}." for o, b in case["events"])
    if condition == "history_reminder":
        body += "\nUse the most recent location of the requested object, not its original location."
    return (
        DEMO
        + body
        + f"\nTo retrieve the {case['target']}, which box should you open?\nAnswer:"
    )


def gold_label(case, condition):
    state = case["initial"] if condition == "initial_snapshot" else case["final"]
    return state[case["target"]]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--per-lag", type=int, default=6)
    parser.add_argument("--seed", type=int, default=20260920)
    parser.add_argument(
        "--model", action="store_true", help="Run cached Gemma 3 1B PT on CPU"
    )
    parser.add_argument("--threads", type=int, default=8)
    parser.add_argument("--model-size", choices=("1b", "4b"), default="1b")
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Use a new directory to preserve previous outputs")
    args.output.mkdir(parents=True)
    data = cases(args.seed, args.per_lag)
    (args.output / "cases.json").write_text(json.dumps(data, indent=2) + "\n")
    baseline = {
        "exact_replay": 1.0,
        "ignore_updates": sum(
            c["initial"][c["target"]] == c["final"][c["target"]] for c in data
        )
        / len(data),
        "always_A": sum(c["final"][c["target"]] == "A" for c in data) / len(data),
    }
    print(json.dumps({"cases": len(data), "symbolic_controls": baseline}), flush=True)
    if not args.model:
        return
    import torch
    import transformers
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        Gemma3ForConditionalGeneration,
    )

    torch.set_num_threads(args.threads)
    model_name = f"google/gemma-3-{args.model_size}-pt"
    revision = (
        REVISION
        if args.model_size == "1b"
        else "cc012e0a6d0787b4adcc0fa2c4da74402494554d"
    )
    model_class = (
        AutoModelForCausalLM
        if args.model_size == "1b"
        else Gemma3ForConditionalGeneration
    )
    tokenizer = AutoTokenizer.from_pretrained(
        model_name, revision=revision, local_files_only=True
    )
    model = model_class.from_pretrained(
        model_name,
        revision=revision,
        local_files_only=True,
        dtype=torch.float32,
        attn_implementation="eager",
    ).eval()
    # Score the exact single-token continuations of this answer prefix; never
    # assume that standalone tokenization equals contextual continuation.
    labels = [" " + b for b in BOXES]
    rows = []
    start = time.monotonic()
    with (args.output / "predictions.jsonl").open("w") as out:
        for case in data:
            for condition in CONDITIONS:
                text = prompt(case, condition)
                prefix = tokenizer.encode(text)
                continuations = [tokenizer.encode(text + label) for label in labels]
                if any(ids[:-1] != prefix for ids in continuations):
                    raise ValueError(
                        "Answer labels must be exact single-token continuations"
                    )
                token_ids = [ids[-1] for ids in continuations]
                inputs = tokenizer(text, return_tensors="pt")
                with torch.inference_mode():
                    logits = (
                        model(**inputs, logits_to_keep=1, use_cache=False)
                        .logits[0, -1]
                        .float()
                    )
                probs = logits.softmax(-1)[token_ids].tolist()
                chosen = BOXES[max(range(3), key=probs.__getitem__)]
                gold = gold_label(case, condition)
                row = {
                    "case_id": case["id"],
                    "lag": case["lag"],
                    "condition": condition,
                    "gold": gold,
                    "prediction": chosen,
                    "correct": chosen == gold,
                    "stale": (
                        condition != "initial_snapshot"
                        and chosen == case["initial"][case["target"]]
                    ),
                    "candidate_probabilities": dict(zip(BOXES, probs)),
                    "candidate_mass": sum(probs),
                    "unrestricted_next_token": tokenizer.decode([int(logits.argmax())]),
                    "input_tokens": len(prefix),
                    "prompt": text,
                    "prompt_sha256": hashlib.sha256(text.encode()).hexdigest(),
                }
                rows.append(row)
                out.write(json.dumps(row) + "\n")
                out.flush()
            print(
                f"Completed {case['id']} ({time.monotonic() - start:.1f}s)", flush=True
            )
    summary = []
    for condition in CONDITIONS:
        for lag in (0, 4, 12):
            group = [r for r in rows if r["condition"] == condition and r["lag"] == lag]
            summary.append(
                {
                    "condition": condition,
                    "lag": lag,
                    "n": len(group),
                    "correct": sum(r["correct"] for r in group),
                    "stale": sum(r["stale"] for r in group),
                    "predictions": dict(Counter(r["prediction"] for r in group)),
                    "mean_candidate_mass": sum(r["candidate_mass"] for r in group)
                    / len(group),
                }
            )
    result = {
        "status": "development_preflight_not_confirmatory",
        "model": model_name,
        "revision": revision,
        "dtype": "float32",
        "device": "cpu",
        "torch": torch.__version__,
        "transformers": transformers.__version__,
        "seed": args.seed,
        "seconds": time.monotonic() - start,
        "symbolic_controls": baseline,
        "groups": summary,
    }
    (args.output / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
