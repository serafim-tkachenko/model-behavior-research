"""Independently parse and audit saved lookup calibration evidence; no inference."""

import argparse
import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(directory, check_tokenizer=False):
    summary = json.loads((directory / "summary.json").read_text())
    freeze = json.loads((directory / "freeze.json").read_text())
    assert summary["freeze_sha256"] == digest(directory / "freeze.json")
    for name, expected in json.loads(
        (directory / "artifact_hashes.json").read_text()
    ).items():
        assert digest(directory / name) == expected, name
    for name, expected in freeze["files"].items():
        local = directory / name
        if not local.exists():
            local = Path(__file__).with_name(name)
        assert digest(local) == expected, name
    assert (
        summary["model"],
        summary["revision"],
        summary["device"],
        summary["dtype"],
        summary["threads"],
    ) == (
        "google/gemma-3-4b-pt",
        "cc012e0a6d0787b4adcc0fa2c4da74402494554d",
        "cpu",
        "float32",
        8,
    )
    prepared = {
        (p["case_id"], p["format"]): p
        for p in json.loads((directory / "prepared_prompts.json").read_text())
    }
    cases = {
        c["id"]: c
        for split in ("development", "check")
        for c in json.loads((directory / f"{split}_cases.json").read_text())
    }
    rows = [
        json.loads(line)
        for line in (directory / "predictions.jsonl").read_text().splitlines()
    ]
    tokenizer = None
    if check_tokenizer:
        from transformers import AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(
            summary["model"], revision=summary["revision"], local_files_only=True
        )
    seen = set()
    for row in rows:
        key = row["case_id"], row["format"]
        assert key not in seen
        seen.add(key)
        expected = prepared[key]
        assert row["split"] == expected["split"]
        assert row["prompt"] == expected["prompt"]
        assert (
            row["prompt_sha256"] == hashlib.sha256(row["prompt"].encode()).hexdigest()
        )
        block = row["prompt"].split("\n\n")[-1]
        pattern = (
            r"^The (\w+) is in box ([ABC])\.$"
            if row["format"] == "prose"
            else r"^(\w+) \| ([ABC])$"
        )
        pairs = re.findall(pattern, block, re.MULTILINE)
        target = re.search(
            r"To retrieve the (\w+), which box should you open\?", block
        )[1]
        assert len(pairs) == 4 and len(dict(pairs)) == 4
        assert [list(p) for p in pairs] == cases[row["case_id"]]["assignments"]
        assert target == cases[row["case_id"]]["target"] == row["target"]
        gold = dict(pairs)[target]
        assert row["gold"] == expected["gold"] == gold
        assert pairs[row["query_position"]][0] == target
        probs = row["candidate_probabilities"]
        assert set(probs) == {"A", "B", "C"}
        assert all(math.isfinite(p) and 0 <= p <= 1 for p in probs.values())
        assert math.isclose(sum(probs.values()), row["candidate_mass"], abs_tol=1e-12)
        assert 0 < row["candidate_mass"] <= 1.000001
        chosen = max(("A", "B", "C"), key=probs.get)
        assert row["prediction"] == chosen and row["correct"] == (chosen == gold)
        if tokenizer is not None:
            prefix = tokenizer.encode(row["prompt"])
            assert len(prefix) == row["input_tokens"]
            for label, token in zip(("A", "B", "C"), row["candidate_token_ids"]):
                assert tokenizer.encode(row["prompt"] + " " + label) == prefix + [token]
    dev = [r for r in rows if r["split"] == "development"]
    check = [r for r in rows if r["split"] == "check"]
    assert len(rows) == summary["scored_prompts"]
    counts = {
        style: sum(r["correct"] for r in dev if r["format"] == style)
        for style in ("prose", "table")
    }
    if len(dev) != 72:
        assert (
            summary["decision"]["status"]
            == "stopped_resource_cap_partial_not_a_competence_result"
        )
        return {
            "verified_rows": len(rows),
            "complete": False,
            "decision": summary["decision"],
        }
    eligible = [style for style in ("prose", "table") if counts[style] >= 33]
    selected = max(eligible, key=counts.get) if eligible else None
    decision = json.loads((directory / "development_decision.json").read_text())
    assert (
        decision["selected_format"]
        == selected
        == summary["decision"]["selected_format"]
    )
    assert decision["development_counts"] == counts
    if selected is None:
        assert len(check) == 0
        assert summary["decision"]["status"] == "stop_no_development_format_passed"
    elif len(check) == 216:
        k = sum(r["correct"] for r in check if r["format"] == selected)
        expected = (
            "lookup_screen_passed_history_assay_not_yet_validated"
            if k >= 98
            else "stop_selected_format_failed_reserved_check"
        )
        assert summary["decision"]["status"] == expected
    else:
        assert (
            summary["decision"]["status"]
            == "stopped_resource_cap_partial_not_a_competence_result"
        )
    for split in ("development", "check"):
        for style in ("prose", "table"):
            group = [r for r in rows if r["split"] == split and r["format"] == style]
            if group:
                saved = summary["groups"][split][style]
                assert saved["n"] == len(group) and saved["correct"] == sum(
                    r["correct"] for r in group
                )
    return {
        "verified_rows": len(rows),
        "complete": selected is None or len(check) == 216,
        "tokenization_rechecked": check_tokenizer,
        "development_counts": counts,
        "selected_format": selected,
        "decision": summary["decision"]["status"],
        "check_error_groups": dict(
            Counter(
                f"{r['format']}:position_{r['query_position']}:gold_{r['gold']}"
                for r in check
                if not r["correct"]
            )
        ),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--tokenizer", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(args.directory, args.tokenizer)
    text = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text)
