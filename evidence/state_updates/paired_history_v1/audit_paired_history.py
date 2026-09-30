"""Independent prompt replay and evidence checks; no generator label helpers."""

import argparse
import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path

CONDITIONS = (
    "initial_snapshot",
    "final_snapshot",
    "short_history",
    "lag_0",
    "lag_4",
    "lag_12",
)


def read_prompt(text):
    block = text.split("\n\n")[-1]
    initial = re.findall(r"^The (\w+) is in box ([ABC])\.$", block, re.MULTILINE)
    updates = re.findall(r"^The (\w+) is now in box ([ABC])\.$", block, re.MULTILINE)
    target = re.findall(r"To retrieve the (\w+), which box should you open\?", block)
    assert len(initial) == 4 and len(dict(initial)) == 4 and len(target) == 1
    state = dict(initial)
    for obj, box in updates:
        assert obj in state
        state[obj] = box
    return state[target[0]], initial, updates, target[0]


def audit_rows(cases, prepared, rows, tokenizer=None):
    assert len(cases) == 36 and len(prepared) == len(rows) == 216
    assert len({c["id"] for c in cases}) == 36
    assert Counter(
        (c["query_position"], c["source_box"], c["current_box"]) for c in cases
    ) == Counter((p, a, b) for p in range(4) for a in "ABC" for b in "ABC")
    assert Counter(c["target"] for c in cases) == Counter(
        dict.fromkeys(("key", "coin", "ring", "pen"), 9)
    )
    by_id = {c["id"]: c for c in cases}
    seen = set()
    for i, (item, row) in enumerate(zip(prepared, rows)):
        key = (row["case_id"], row["condition"])
        assert key not in seen
        seen.add(key)
        case = by_id[row["case_id"]]
        condition = row["condition"]
        assert condition == CONDITIONS[(i % 6 + i // 6) % 6]
        assert row["case_id"] == cases[i // 6]["id"]
        assert all(
            row[k] == item[k] for k in ("case_id", "condition", "prompt", "gold")
        )
        assert (
            hashlib.sha256(row["prompt"].encode()).hexdigest() == row["prompt_sha256"]
        )
        recovered, facts, updates, target = read_prompt(row["prompt"])
        assert recovered == row["gold"] and target == row["target"] == case["target"]
        assert facts[case["query_position"]][0] == target
        assert row["query_position"] == case["query_position"]
        assert row["source_box"] == case["initial"][target] == case["source_box"]
        assert (
            row["changed"]
            == case["changed"]
            == (case["source_box"] != case["current_box"])
        )
        expected_state = (
            case["final"] if condition == "final_snapshot" else case["initial"]
        )
        assert facts == list(expected_state.items())
        target_events = [j for j, (obj, _) in enumerate(updates) if obj == target]
        if condition.endswith("snapshot"):
            assert updates == []
        else:
            assert (
                len(target_events) == 1
                and updates[target_events[0]][1] == case["current_box"]
            )
            distractors = [list(e) for e in updates if e[0] != target]
            if condition == "short_history":
                assert len(updates) == 1
            else:
                assert len(updates) == 13 and distractors == case["distractors"]
                assert len(updates) - target_events[0] - 1 == int(
                    condition.split("_")[1]
                )
                state = dict(facts)
                for obj, box in updates:
                    if obj != target:
                        assert state[obj] != box
                    state[obj] = box
                assert state == case["final"]
        probs = row["candidate_probabilities"]
        assert set(probs) == set("ABC")
        assert all(math.isfinite(p) and 0 <= p <= 1 for p in probs.values())
        assert math.isclose(sum(probs.values()), row["candidate_mass"], abs_tol=1e-7)
        assert 0 <= row["candidate_mass"] <= 1.000001
        assert row["prediction"] == max("ABC", key=probs.get)
        assert row["correct"] == (row["prediction"] == recovered)
        assert len(set(row["candidate_token_ids"])) == 3
        assert 0 < row["rss_before_prompt_gib"] <= 21
        if tokenizer:
            prefix = tokenizer.encode(row["prompt"])
            assert len(prefix) == row["input_tokens"]
            for box, token_id in zip("ABC", row["candidate_token_ids"]):
                assert tokenizer.encode(row["prompt"] + " " + box) == prefix + [
                    token_id
                ]
    for case in cases:
        matched = [
            r
            for r in rows
            if r["case_id"] == case["id"] and r["condition"].startswith("lag_")
        ]
        assert len(matched) == 3 and len({r["input_tokens"] for r in matched}) == 1
    return {
        "audited_rows": len(rows),
        "paired_cases": len(cases),
        "tokenizer_verified": tokenizer is not None,
    }


def audit(directory, use_tokenizer=False):
    for manifest in ("freeze.json", "artifact_hashes.json"):
        data = json.loads((directory / manifest).read_text())
        hashes = data["files"] if manifest == "freeze.json" else data
        for name, expected in hashes.items():
            assert (
                hashlib.sha256((directory / name).read_bytes()).hexdigest() == expected
            ), name
    freeze = json.loads((directory / "freeze.json").read_text())
    tokenizer = None
    if use_tokenizer:
        from transformers import AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(
            freeze["model"], revision=freeze["revision"], local_files_only=True
        )
    cases = json.loads((directory / "cases.json").read_text())
    excluded = json.loads((directory / "excluded_snapshots.json").read_text())
    seen = {(tuple(tuple(p) for p in pairs), target) for pairs, target in excluded}
    for case in cases:
        for stage in ("initial", "final"):
            key = (tuple(sorted(case[stage].items())), case["target"])
            assert key not in seen
            seen.add(key)
    prepared = json.loads((directory / "prepared_prompts.json").read_text())
    rows = [
        json.loads(line)
        for line in (directory / "predictions.jsonl").read_text().splitlines()
    ]
    result = audit_rows(cases, prepared, rows, tokenizer)
    summary = json.loads((directory / "summary.json").read_text())
    assert (
        summary["freeze_sha256"]
        == hashlib.sha256((directory / "freeze.json").read_bytes()).hexdigest()
    )
    assert summary["scored_prompts"] == 216 and summary["stop_reason"] is None
    for name in ("model", "revision", "device", "dtype", "threads"):
        assert summary[name] == freeze[name]
    for condition in CONDITIONS:
        group = [r for r in rows if r["condition"] == condition]
        saved = summary["groups"][condition]
        assert saved["n"] == len(group) == 36
        assert saved["correct"] == sum(r["correct"] for r in group)
        for field, values in (
            ("changed", (False, True)),
            ("query_position", range(4)),
            ("gold", "ABC"),
        ):
            for value in values:
                sub = [r for r in group if r[field] == value]
                assert saved[f"by_{field}"][str(value)] == {
                    "n": len(sub),
                    "correct": sum(r["correct"] for r in sub),
                }
        assert saved["old_location_errors_changed_only"] == sum(
            r["changed"] and not r["correct"] and r["prediction"] == r["source_box"]
            for r in group
            if condition != "initial_snapshot"
        )
        assert saved["input_token_range"] == [
            min(r["input_tokens"] for r in group),
            max(r["input_tokens"] for r in group),
        ]
        assert math.isclose(
            saved["mean_candidate_mass"], sum(r["candidate_mass"] for r in group) / 36
        )
    indexed = {(r["case_id"], r["condition"]): r for r in rows}
    for changed in (False, True):
        counts = Counter()
        for case in cases:
            if case["changed"] == changed:
                a, b = (
                    indexed[case["id"], condition]["correct"]
                    for condition in ("lag_0", "lag_12")
                )
                counts[f"lag0_{int(a)}_lag12_{int(b)}"] += 1
        assert dict(counts) == summary["paired_lag0_lag12_by_changed"][str(changed)]
    controls_pass = all(summary["groups"][c]["correct"] >= 33 for c in CONDITIONS[:3])
    assert summary["status"] == (
        "complete_controls_passed" if controls_pass else "complete_control_failure"
    )
    return {
        **result,
        "status": "passed",
        "endpoint_exclusion_verified": True,
        "summary_verified": True,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--tokenizer", action="store_true")
    args = parser.parse_args()
    print(json.dumps(audit(args.directory, args.tokenizer), indent=2))
