"""Verify saved preflight rows and print descriptive, history-paired counts."""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from pilot import CONDITIONS, cases, gold_label, prompt


def analyze(directory):
    metadata = json.loads((directory / "summary.json").read_text())
    saved_cases = json.loads((directory / "cases.json").read_text())
    generated = cases(metadata["seed"], len(saved_cases) // 3)
    assert json.loads(json.dumps(generated)) == saved_cases
    case_map = {c["id"]: c for c in saved_cases}
    rows = [
        json.loads(line)
        for line in (directory / "predictions.jsonl").read_text().splitlines()
    ]
    keys = [(r["case_id"], r["condition"]) for r in rows]
    assert len(keys) == len(set(keys)) == len(saved_cases) * len(CONDITIONS)
    for row in rows:
        case = case_map[row["case_id"]]
        expected_prompt = prompt(case, row["condition"])
        assert row["prompt"] == expected_prompt
        assert (
            row["prompt_sha256"] == hashlib.sha256(expected_prompt.encode()).hexdigest()
        )
        assert row["gold"] == gold_label(case, row["condition"])
        predicted = max(
            row["candidate_probabilities"], key=row["candidate_probabilities"].get
        )
        assert row["prediction"] == predicted
        assert row["correct"] == (predicted == row["gold"])
        assert row["lag"] == case["lag"]
    output = {
        "model": metadata["model"],
        "histories": len(saved_cases),
        "verified_rows": len(rows),
        "conditions": {},
    }
    for condition in CONDITIONS:
        group = [r for r in rows if r["condition"] == condition]
        output["conditions"][condition] = {
            "correct": sum(r["correct"] for r in group),
            "n": len(group),
            "by_lag": {
                lag: sum(r["correct"] for r in group if r["lag"] == lag)
                for lag in (0, 4, 12)
            },
            "mean_candidate_mass": sum(r["candidate_mass"] for r in group) / len(group),
            "unrestricted_next_tokens": dict(
                Counter(r["unrestricted_next_token"] for r in group)
            ),
        }
    paired = {(r["case_id"], r["condition"]): r for r in rows}
    output["reminder_paired_changes"] = dict(
        Counter(
            ("correct" if paired[(c["id"], "history")]["correct"] else "wrong")
            + "->"
            + (
                "correct"
                if paired[(c["id"], "history_reminder")]["correct"]
                else "wrong"
            )
            for c in saved_cases
        )
    )
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    print(json.dumps(analyze(args.directory), indent=2))
