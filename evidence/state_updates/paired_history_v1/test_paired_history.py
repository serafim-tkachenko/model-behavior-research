"""Verify matched event streams, independent labels, controls and audit sensitivity."""

import copy
from collections import Counter

import audit_paired_history as audit
import paired_history as h
import pytest


def synthetic_rows():
    cases = h.make_cases()
    prepared, rows = [], []
    for case, condition in h.schedule(cases):
        text = h.prompt(case, condition)
        gold = audit.read_prompt(text)[0]
        item = {
            "case_id": case["id"],
            "condition": condition,
            "prompt": text,
            "gold": gold,
        }
        prepared.append(item)
        rows.append(
            {
                **item,
                "target": case["target"],
                "source_box": case["source_box"],
                "changed": case["changed"],
                "query_position": case["query_position"],
                "prediction": gold,
                "correct": True,
                "input_tokens": len(text.split()),
                "candidate_probabilities": {
                    b: 0.8 if b == gold else 0.05 for b in "ABC"
                },
                "candidate_mass": 0.9,
                "candidate_token_ids": [1, 2, 3],
                "prompt_sha256": h.digest(text.encode()),
                "rss_before_prompt_gib": 17,
            }
        )
    return cases, prepared, rows


def test_balanced_disjoint_endpoints_and_reproducibility():
    cases = h.make_cases()
    assert cases == h.make_cases()
    seen = h.observed_signatures()
    for case in cases:
        for stage in ("initial", "final"):
            sig = h.signature(case[stage], case["target"])
            assert sig not in seen
            seen.add(sig)
    assert Counter(c["changed"] for c in cases) == {True: 24, False: 12}
    assert Counter(c["query_position"] for c in cases) == dict.fromkeys(range(4), 9)


def test_replay_and_matching_and_static_prompt_identity():
    cases, prepared, rows = synthetic_rows()
    assert audit.audit_rows(cases, prepared, rows)["audited_rows"] == 216
    for case in cases:
        for condition, stage in (
            ("initial_snapshot", "initial"),
            ("final_snapshot", "final"),
        ):
            assert h.prompt(case, condition) == h.lookup_prompt(
                {"assignments": list(case[stage].items()), "target": case["target"]},
                "prose",
            )
        streams = [h.events(case, f"lag_{lag}") for lag in (0, 4, 12)]
        assert all(
            Counter(map(tuple, s)) == Counter(map(tuple, streams[0])) for s in streams
        )
    for condition in h.CONDITIONS:
        subset = [r for r in rows if r["condition"] == condition]
        assert sum(r["gold"] == "A" for r in subset) == 12
        assert sum(r["gold"] == r["source_box"] for r in subset) == (
            36 if condition == "initial_snapshot" else 12
        )
    for slot in range(6):
        assert Counter(
            item["condition"] for item in prepared[slot::6]
        ) == dict.fromkeys(h.CONDITIONS, 6)


@pytest.mark.parametrize(
    "field,value",
    [
        ("gold", "Z"),
        ("prediction", "Z"),
        ("correct", False),
        ("source_box", "Z"),
        ("candidate_mass", 0.1),
        ("condition", "lag_99"),
        ("input_tokens", 999),
    ],
)
def test_independent_audit_rejects_corruption(field, value):
    cases, prepared, rows = synthetic_rows()
    bad = copy.deepcopy(rows)
    index = next(i for i, r in enumerate(rows) if r["condition"] == "lag_12")
    bad[index][field] = value
    with pytest.raises((AssertionError, KeyError, ValueError)):
        audit.audit_rows(cases, prepared, bad)


def test_control_gate_exact_boundary_and_partial_result():
    _, _, rows = synthetic_rows()
    for condition in h.CONDITIONS[:3]:
        changed = copy.deepcopy(rows)
        indices = [i for i, r in enumerate(rows) if r["condition"] == condition]
        for i in indices[:3]:
            changed[i]["correct"] = False
        assert h.summarize(changed)["status"] == "complete_controls_passed"
        changed[indices[3]]["correct"] = False
        assert h.summarize(changed)["status"] == "complete_control_failure"
    assert h.summarize(rows[:-1])["status"] == "partial_not_a_competence_result"


def test_changed_target_event_counterfactual_changes_answer():
    for case in h.make_cases():
        for condition in ("short_history", "lag_0", "lag_4", "lag_12"):
            new_box = next(b for b in "ABC" if b != case["current_box"])
            text = h.prompt(case, condition)
            altered = text.replace(
                f"The {case['target']} is now in box {case['current_box']}.",
                f"The {case['target']} is now in box {new_box}.",
            )
            assert audit.read_prompt(altered)[0] == new_box
