"""B1 — the atom evaluator and the domain model it enumerates over.

The whole entailment check rests on two things being right: what an atom means when its field
is ABSENT, and which fields can even be absent. Both were found the hard way.

The governing convention is `classification-schema.md:72` — "Absent input ⇒ not-in-set ⇒ that
disjunct is false". The subtle half is that this makes a NEGATED atom false too: a naive reading
has `not_in` vacuously TRUE on a missing field, which is the opposite of the convention and would
mask a dead angle. Only `is_absent` may be true on ABSENT.
"""

from __future__ import annotations

import dataclasses

import pytest
from trigger_integrity import ABSENT, FieldSpec, evaluate, load_field_specs

#: (op, values, present_value, expected_on_present, expected_on_absent)
_CASES = [
    ("in", ["high", "extreme"], "high", True, False),
    ("in", ["high", "extreme"], "low", False, False),
    ("not_in", ["none"], "hard", True, False),
    ("not_in", ["none"], "none", False, False),
    ("eq", ["b2c"], "b2c", True, False),
    ("eq", ["b2c"], "b2b", False, False),
    ("neq", ["none"], "marketplace", True, False),
    ("neq", ["none"], "none", False, False),
    ("is_true", None, True, True, False),
    ("is_true", None, False, False, False),
    ("is_false", None, False, True, False),
    ("is_false", None, True, False, False),
    ("is_present", None, "anything", True, False),
    ("is_absent", None, "anything", False, True),
    ("contains", ["cli-tool"], ["cli-tool", "api-service"], True, False),
    ("contains", ["cli-tool"], ["mobile-app"], False, False),
]


@pytest.mark.parametrize(("op", "values", "present", "on_present", "on_absent"), _CASES)
def test_every_op_on_a_present_and_an_absent_field(
    op, values, present, on_present, on_absent
):
    atom = {"field": "f", "op": op}
    if values is not None:
        atom["values"] = values
    assert evaluate(atom, {"f": present}) is on_present, "present"
    assert evaluate(atom, {"f": ABSENT}) is on_absent, "absent"


def test_only_is_absent_is_ever_true_on_a_missing_field():
    """The rule stated as a population claim rather than case by case, so a tenth op added later
    without thinking about ABSENT shows up here."""
    ops = {c[0] for c in _CASES}
    true_on_absent = {
        op
        for op in ops
        if evaluate({"field": "f", "op": op, "values": ["x"]}, {"f": ABSENT}) is True
    }
    assert true_on_absent == {"is_absent"}


def test_an_unknown_op_is_refused_rather_than_guessed():
    with pytest.raises(ValueError, match="unknown op"):
        evaluate({"field": "f", "op": "approximately", "values": ["x"]}, {"f": "x"})


class TestDomainModel:
    def test_a_required_field_cannot_be_absent(self):
        specs = load_field_specs()
        for path in ("ui.has_ui", "scale.concurrency", "business.platform.type"):
            assert specs[path].required, path
            assert ABSENT not in specs[path].domain, path

    def test_an_optional_field_carries_absent_in_its_domain(self):
        specs = load_field_specs()
        spec = specs["ui.accessibility.required_level"]
        assert not spec.required
        assert ABSENT in spec.domain
        assert set(spec.domain) == {"A", "AA", "AAA", ABSENT}

    def test_a_boolean_domain_is_both_truth_values(self):
        specs = load_field_specs()
        assert set(specs["ui.has_ui"].domain) == {True, False}

    def test_an_enum_domain_is_exactly_the_schema_enum(self):
        specs = load_field_specs()
        assert set(specs["domain.audience"].domain) == {
            "b2c",
            "b2b",
            "b2b2c",
            "developer",
            "internal",
        }

    def test_an_enum_less_array_is_not_enumerable(self):
        """`archetype.secondary` is {"type":"array","items":{"type":"string"}} — three shipped
        angles predicate on it with `contains`, and it has no finite domain."""
        specs = load_field_specs()
        spec = specs["archetype.secondary"]
        assert spec.is_array
        assert not spec.enumerable

    def test_a_property_less_object_is_not_enumerable(self):
        """25 of these exist; no computable trigger can rest on one."""
        specs = load_field_specs()
        assert not specs["regulatory.health"].enumerable

    def test_the_required_leaves_are_exactly_the_fourteen(self):
        """The set playbook #41 got wrong. Derived here, never transcribed."""
        specs = load_field_specs()
        required = {
            p
            for p, s in specs.items()
            if s.required and not p.startswith("prior_art_triggers.")
        }
        assert required == {
            "archetype.primary",
            "domain.audience",
            "regulatory.applies",
            "scale.concurrency",
            "scale.real_time",
            "scale.availability_target",
            "scale.geo_distribution",
            "scale.data_volume",
            "integrations.expected",
            "integrations.complexity",
            "ui.has_ui",
            "ui.complexity",
            "data_ml.ml_involvement",
            "business.platform.type",
        }

    def test_field_spec_is_immutable(self):
        with pytest.raises(dataclasses.FrozenInstanceError):
            FieldSpec(
                path="x", required=True, domain=(), enumerable=False, is_array=False
            ).path = "y"
