"""Controls for disjoint data, prompt information, labels and decision gates."""

import importlib.util
import re
from collections import Counter
from copy import deepcopy
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "lookup_calibration", Path(__file__).with_name("calibration.py")
)
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


def independently_read_prompt(text, style):
    block = text.split("\n\n")[-1]
    if style == "prose":
        pairs = re.findall(r"^The (\w+) is in box ([ABC])\.$", block, re.MULTILINE)
    else:
        pairs = re.findall(r"^(\w+) \| ([ABC])$", block, re.MULTILINE)
    target = re.search(r"To retrieve the (\w+), which box should you open\?", block)[1]
    assert len(pairs) == 4
    return dict(pairs)[target], pairs, target


def test_balance_and_disjoint_semantic_cases():
    splits = c.make_cases()
    seen = c.old_signatures()
    for split, repetitions in (("development", 1), ("check", 3)):
        data = splits[split]
        assert len(data) == 36 * repetitions
        counts = Counter(
            (x["query_position"], x["source_box"], x["current_box"]) for x in data
        )
        assert len(counts) == 36 and set(counts.values()) == {repetitions}
        assert set(Counter(x["target"] for x in data).values()) == {9 * repetitions}
        for case in data:
            assert c.signature(case) not in seen
            seen.add(c.signature(case))
            assert case["assignments"][case["query_position"]] == [
                case["target"],
                case["current_box"],
            ]
    assert splits == c.make_cases()


def test_symbolic_reader_recovers_labels_in_both_formats():
    for cases in c.make_cases().values():
        for case in cases:
            recovered = [
                independently_read_prompt(c.prompt(case, style), style)
                for style in c.FORMATS
            ]
            assert recovered[0] == recovered[1]
            assert recovered[0][0] == case["current_box"]


def test_known_counterexample_and_hidden_source_box():
    case = {
        "assignments": [["key", "C"], ["coin", "B"], ["ring", "A"], ["pen", "C"]],
        "target": "key",
        "source_box": "A",
    }
    for style in c.FORMATS:
        text = c.prompt(case, style)
        assert independently_read_prompt(text, style)[0] == "C"
        changed = deepcopy(case)
        changed["source_box"] = "B"
        assert c.prompt(changed, style) == text
        changed["assignments"][0][1] = "B"
        assert independently_read_prompt(c.prompt(changed, style), style)[0] == "B"


@pytest.mark.parametrize(
    "counts,n,expected",
    [
        ({"prose": 32, "table": 32}, 36, None),
        ({"prose": 33, "table": 32}, 36, "prose"),
        ({"prose": 33, "table": 34}, 36, "table"),
        ({"prose": 36, "table": 36}, 36, "prose"),
        ({"prose": 97, "table": 97}, 108, None),
        ({"prose": 98, "table": 97}, 108, "prose"),
    ],
)
def test_exact_screen_and_prespecified_tie_break(counts, n, expected):
    assert c.choose_format(counts, n) == expected


def test_descriptive_interval_reference_values():
    low, high = c.wilson(36, 36)
    assert low == pytest.approx(0.903581, abs=1e-6)
    assert high == pytest.approx(1.0)
    low, high = c.wilson(0, 36)
    assert low == pytest.approx(0.0)
    assert high == pytest.approx(0.096419, abs=1e-6)
