import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "state_update_pilot", Path(__file__).with_name("pilot.py")
)
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)


def test_update_only_changes_named_object():
    before = {"key": "A", "coin": "B"}
    assert p.replay(before, [("key", "C"), ("coin", "A")]) == {"key": "C", "coin": "A"}
    assert before == {"key": "A", "coin": "B"}


def test_balanced_targets_and_actual_lag():
    for lag in (0, 4, 12):
        group = [c for c in p.cases() if c["lag"] == lag]
        assert [p.gold_label(c, "history") for c in group].count("A") == 2
        for c in group:
            assert c["initial"][c["target"]] != c["final"][c["target"]]
            assert len(c["events"]) == lag + 1
            assert all(o != c["target"] for o, _ in c["events"][1:])
            assert p.replay(c["initial"], c["events"]) == c["final"]


def test_snapshot_controls_have_correct_labels_and_no_events():
    for c in p.cases():
        initial = p.prompt(c, "initial_snapshot")[len(p.DEMO) :]
        final = p.prompt(c, "final_snapshot_oracle")[len(p.DEMO) :]
        assert "Move " not in initial + final
        assert (
            f"The {c['target']} is in box {p.gold_label(c, 'initial_snapshot')}."
            in initial
        )
        assert f"The {c['target']} is in box {p.gold_label(c, 'history')}." in final


def test_reminder_does_not_reveal_target_location():
    c = p.cases()[0]
    plain = p.prompt(c, "history")
    reminder = p.prompt(c, "history_reminder")
    assert (
        reminder.replace(
            "\nUse the most recent location of the requested object, not its original location.",
            "",
        )
        == plain
    )


def test_invalid_events_fail_and_generation_is_reproducible():
    with pytest.raises(ValueError):
        p.replay({"key": "A"}, [("missing", "B")])
    with pytest.raises(ValueError):
        p.cases(per_lag=4)
    assert p.cases() == p.cases()
    assert p.cases(seed=7) != p.cases()
