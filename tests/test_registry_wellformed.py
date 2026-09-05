"""C1 — registry shape, checked before anything tries to decide entailment from it.

Split deliberately from `predicate-not-expressible`: this rule owns SHAPE (missing keys, an op
that does not exist, values where none belong), and expressibility owns DECIDABILITY (a field
with no finite domain). Conflating them would produce one rule that fires for two unrelated
reasons and tells the author neither.
"""

from __future__ import annotations

import copy

import pytest
from trigger_rules import check_wellformed

BASE = {
    "type_trigger": {
        "formula": "ui.has_ui",
        "predicate": [[{"field": "ui.has_ui", "op": "is_true"}]],
    },
    "angles": [
        {"id": "a1", "trigger": "always"},
        {
            "id": "b1",
            "trigger": "conditional",
            "predicate": [
                [{"field": "domain.audience", "op": "in", "values": ["b2c"]}]
            ],
        },
    ],
}


def _rules(findings):
    return [f.rule for f in findings]


def _mutate(**_):
    return copy.deepcopy(BASE)


def test_the_baseline_is_clean():
    assert check_wellformed(BASE) == []


def test_a_conditional_angle_without_a_predicate_fails():
    reg = _mutate()
    del reg["angles"][1]["predicate"]
    assert "predicate-missing" in _rules(check_wellformed(reg))


def test_an_always_on_angle_carrying_a_predicate_fails():
    reg = _mutate()
    reg["angles"][0]["predicate"] = [[{"field": "ui.has_ui", "op": "is_true"}]]
    assert "predicate-only-on-conditional" in _rules(check_wellformed(reg))


def test_an_unknown_op_fails_and_names_it():
    reg = _mutate()
    reg["angles"][1]["predicate"][0][0]["op"] = "approximately"
    found = check_wellformed(reg)
    assert "atom-unknown-op" in _rules(found)
    assert "approximately" in found[0].message


@pytest.mark.parametrize("op", ["in", "not_in", "eq", "neq", "contains"])
def test_an_op_that_needs_values_fails_without_them(op):
    reg = _mutate()
    reg["angles"][1]["predicate"][0][0] = {"field": "domain.audience", "op": op}
    assert "atom-values-required" in _rules(check_wellformed(reg))


@pytest.mark.parametrize("op", ["is_true", "is_false", "is_absent", "is_present"])
def test_an_op_that_takes_no_values_fails_with_them(op):
    """The MIRROR of the rule above (#34). Values on a valueless op mean the author expected
    something the evaluator will silently ignore."""
    reg = _mutate()
    reg["angles"][1]["predicate"][0][0] = {
        "field": "ui.has_ui",
        "op": op,
        "values": ["yes"],
    }
    assert "atom-values-forbidden" in _rules(check_wellformed(reg))


def test_an_atom_missing_its_field_fails():
    reg = _mutate()
    del reg["angles"][1]["predicate"][0][0]["field"]
    assert "atom-field-required" in _rules(check_wellformed(reg))


def test_a_predicate_that_is_not_a_list_of_conjunctions_fails():
    reg = _mutate()
    reg["angles"][1]["predicate"] = [{"field": "ui.has_ui", "op": "is_true"}]
    assert "predicate-shape" in _rules(check_wellformed(reg))


def test_a_malformed_leg_scope_fails():
    reg = _mutate()
    reg["angles"][1]["leg_scope"] = "because I said so"
    assert "leg-scope-shape" in _rules(check_wellformed(reg))


def test_an_empty_leg_scope_entry_fails():
    """An empty justification silences the rule while recording nothing — worse than no entry."""
    reg = _mutate()
    reg["angles"][1]["leg_scope"] = ["  "]
    assert "leg-scope-shape" in _rules(check_wellformed(reg))


def test_a_type_trigger_without_a_predicate_is_reported_as_out_of_scope_not_broken():
    """`code` and `security` are structurally out of scope; the guard must skip them with a
    reason, not crash on them."""
    reg = _mutate()
    del reg["type_trigger"]
    found = check_wellformed(reg)
    assert _rules(found) == ["registry-out-of-scope"]
    assert found[0].severity == "skip"
