"""B2-B5 — the four rules, and the shapes that made each of them necessary.

Each test names the defect behind it (playbook #47: a rule enters with a recorded origin).
The two v1 cases are kept deliberately: an earlier design compared per-field value sets and was
unsound in BOTH directions, so the false negative it missed and the false positive it invented
are regression tests, not hypotheticals.
"""

from __future__ import annotations

from typing import ClassVar

from trigger_integrity import load_field_specs
from trigger_rules import RULES, check_angle

SPECS = load_field_specs()

# ui.complexity != none implies ui.has_ui — without it, an incoherent map (has_ui false with
# complexity complex) is a witness and user_research b2 escapes detection.
AXIOM = {
    "when": [{"field": "ui.complexity", "op": "not_in", "values": ["none"]}],
    "then": [{"field": "ui.has_ui", "op": "is_true"}],
    "because": "a project with UI complexity above none has a UI",
}

VISUAL_TRIGGER = [[{"field": "ui.has_ui", "op": "is_true"}]]
UR_TRIGGER = [
    [
        {"field": "ui.has_ui", "op": "is_true"},
        {"field": "domain.audience", "op": "in", "values": ["b2c", "b2b2c"]},
    ],
    [{"field": "ui.complexity", "op": "in", "values": ["complex", "consumer-grade"]}],
]
SCALE_TRIGGER = [
    [{"field": "scale.concurrency", "op": "in", "values": ["high", "extreme"]}],
    [{"field": "scale.real_time", "op": "in", "values": ["near", "hard"]}],
    [{"field": "scale.availability_target", "op": "in", "values": ["99.99", "99.999"]}],
    [
        {
            "field": "scale.geo_distribution",
            "op": "in",
            "values": ["multi-region", "global", "edge"],
        }
    ],
    [{"field": "scale.data_volume", "op": "in", "values": ["large", "extreme"]}],
]
INTEGRATIONS_TRIGGER = [
    [
        {"field": "integrations.expected", "op": "is_true"},
        {
            "field": "integrations.complexity",
            "op": "in",
            "values": ["moderate", "complex"],
        },
    ]
]


def _angle(aid, predicate, **kw):
    return {"id": aid, "trigger": "conditional", "predicate": predicate, **kw}


def _rules(findings):
    return [f.rule for f in findings]


class TestAxiomsUnsatisfiable:
    """B2 — a check whose failure mode is 'everything fails' must prove its own premise."""

    #: Genuinely unsatisfiable: an empty `when` is unconditional, so these two demand both
    #: truth values of one field at once. A one-sided axiom is NOT contradictory — an earlier
    #: draft of this test used `when has_ui THEN not has_ui`, which is satisfied vacuously by
    #: has_ui = false, and the engine was right to accept it.
    CONTRADICTORY: ClassVar[list] = [
        {
            "when": [],
            "then": [{"field": "ui.has_ui", "op": "is_true"}],
            "because": "must",
        },
        {
            "when": [],
            "then": [{"field": "ui.has_ui", "op": "is_false"}],
            "because": "must not",
        },
    ]

    def test_a_contradictory_axiom_set_fires(self):
        found = check_angle(
            VISUAL_TRIGGER, _angle("b1", VISUAL_TRIGGER), SPECS, self.CONTRADICTORY
        )
        assert _rules(found) == ["axioms-unsatisfiable"]

    def test_it_suppresses_every_other_rule(self):
        """Otherwise a single bad axiom reports every angle as always-firing — the whole gate
        becomes noise and the real signal is buried. b3 restates its trigger, so it WOULD
        report always-fires if the precheck did not short-circuit."""
        found = check_angle(
            VISUAL_TRIGGER, _angle("b3", VISUAL_TRIGGER), SPECS, self.CONTRADICTORY
        )
        assert _rules(found) == ["axioms-unsatisfiable"]

    def test_the_real_axiom_is_satisfiable(self):
        found = check_angle(
            UR_TRIGGER,
            _angle(
                "b1",
                [[{"field": "archetype.primary", "op": "eq", "values": ["web-app"]}]],
            ),
            SPECS,
            [AXIOM],
        )
        assert "axioms-unsatisfiable" not in _rules(found)


class TestAngleAlwaysFires:
    """B3 — playbook #53. Origin: visual b3."""

    def test_l2_visual_b3_fires(self):
        b3 = _angle(
            "b3",
            [
                [
                    {
                        "field": "ui.accessibility.required_level",
                        "op": "in",
                        "values": ["A", "AA", "AAA"],
                    }
                ],
                [{"field": "ui.has_ui", "op": "is_true"}],
            ],
        )
        assert "angle-always-fires" in _rules(
            check_angle(VISUAL_TRIGGER, b3, SPECS, [AXIOM])
        )

    def test_l3_user_research_b2_fires_ONLY_with_the_axiom(self):
        """The control that proves the axiom is load-bearing rather than decorative."""
        b2 = _angle(
            "b2",
            [
                [
                    {
                        "field": "ui.accessibility.required_level",
                        "op": "in",
                        "values": ["A", "AA", "AAA"],
                    }
                ],
                [
                    {"field": "ui.has_ui", "op": "is_true"},
                    {"field": "ui.accessibility.required_level", "op": "is_absent"},
                ],
            ],
        )
        assert "angle-always-fires" in _rules(
            check_angle(UR_TRIGGER, b2, SPECS, [AXIOM])
        )
        assert "angle-always-fires" not in _rules(
            check_angle(UR_TRIGGER, b2, SPECS, [])
        )

    def test_v1s_false_NEGATIVE_is_closed(self):
        """A scale angle whose predicate copies the five-way trigger verbatim. v1 passed it —
        `guarantees` was empty for a disjunctive trigger, so there was nothing to compare."""
        copycat = _angle("b9", [list(c) for c in SCALE_TRIGGER])
        assert "angle-always-fires" in _rules(
            check_angle(SCALE_TRIGGER, copycat, SPECS, [])
        )

    def test_v1s_false_POSITIVE_is_not_reproduced(self):
        """`expected = true AND archetype.primary = library-sdk` is genuinely gated. v1 rejected
        it because expected's only value-set equalled what the trigger guarantees — and the
        shipped contract REQUIRES naming that field as an anchor, so it was unavoidable."""
        gated = _angle(
            "b1",
            [
                [
                    {"field": "integrations.expected", "op": "is_true"},
                    {
                        "field": "archetype.primary",
                        "op": "eq",
                        "values": ["library-sdk"],
                    },
                ]
            ],
        )
        assert _rules(check_angle(INTEGRATIONS_TRIGGER, gated, SPECS, [])) == []

    def test_an_angle_narrower_than_the_trigger_is_clean(self):
        narrow = _angle(
            "b2",
            [[{"field": "integrations.complexity", "op": "eq", "values": ["complex"]}]],
        )
        assert _rules(check_angle(INTEGRATIONS_TRIGGER, narrow, SPECS, [])) == []


class TestLegNeverFires:
    """B4 — pairwise, and REPORTED rather than failed. Origin: user_research b5."""

    def test_l4_user_research_b5_reports_the_dead_pair(self):
        b5 = _angle(
            "b5",
            [
                [{"field": "domain.audience", "op": "eq", "values": ["developer"]}],
                [
                    {
                        "field": "archetype.primary",
                        "op": "in",
                        "values": ["cli-tool", "library-sdk", "api-service"],
                    }
                ],
            ],
        )
        found = check_angle(UR_TRIGGER, b5, SPECS, [AXIOM])
        assert "leg-never-fires" in _rules(found)
        assert "(0, 0)" in found[0].message

    def test_it_reports_rather_than_fails(self):
        """A dead pair is often a legitimately leg-scoped angle; the rule cannot tell which and
        says so. Measured: three of five plausible scale angles fire, all legitimate."""
        scoped = _angle(
            "b7", [[{"field": "scale.real_time", "op": "eq", "values": ["none"]}]]
        )
        found = check_angle(SCALE_TRIGGER, scoped, SPECS, [])
        assert [f.severity for f in found] == ["report"]

    def test_a_leg_scope_justification_silences_it(self):
        scoped = _angle(
            "b7",
            [[{"field": "scale.real_time", "op": "eq", "values": ["none"]}]],
            leg_scope=[
                "high-concurrency batch systems are not real-time; leg 1 is the cohort"
            ],
        )
        assert _rules(check_angle(SCALE_TRIGGER, scoped, SPECS, [])) == []

    def test_every_pair_dead_escalates(self):
        dead = _angle("bX", [[{"field": "ui.has_ui", "op": "is_false"}]])
        found = check_angle(UR_TRIGGER, dead, SPECS, [AXIOM])
        assert "leg-never-fires" in _rules(found)
        assert "never fire" in found[0].message

    def test_a_genuinely_gated_angle_reports_nothing(self):
        ok = _angle(
            "b4",
            [[{"field": "archetype.primary", "op": "eq", "values": ["mobile-app"]}]],
        )
        assert _rules(check_angle(UR_TRIGGER, ok, SPECS, [AXIOM])) == []


class TestPredicateNotExpressible:
    """B5 — refuse rather than guess. A free boolean for EVERY non-enumerable field would
    silently weaken every rule, a typo'd field name included."""

    def test_an_atom_over_a_property_less_object_is_refused(self):
        a = _angle("b1", [[{"field": "regulatory.health", "op": "is_present"}]])
        assert "predicate-not-expressible" in _rules(
            check_angle(UR_TRIGGER, a, SPECS, [])
        )

    def test_an_unknown_field_is_refused(self):
        a = _angle("b1", [[{"field": "ui.has_iu", "op": "is_true"}]])
        assert "predicate-not-expressible" in _rules(
            check_angle(UR_TRIGGER, a, SPECS, [])
        )

    def test_contains_over_an_enum_less_array_IS_expressible(self):
        """Three shipped angles do exactly this. v2 called it 'not a live case' and was wrong."""
        a = _angle(
            "b1",
            [
                [
                    {
                        "field": "archetype.secondary",
                        "op": "contains",
                        "values": ["cli-tool", "api-service"],
                    }
                ]
            ],
        )
        assert "predicate-not-expressible" not in _rules(
            check_angle(UR_TRIGGER, a, SPECS, [])
        )


def test_every_rule_has_a_recorded_origin_defect():
    """Playbook #47 — no defect, no rule. That field is what stops a regression suite quietly
    becoming a style guide."""
    assert RULES
    for rule_id, origin in RULES.items():
        assert origin, rule_id
