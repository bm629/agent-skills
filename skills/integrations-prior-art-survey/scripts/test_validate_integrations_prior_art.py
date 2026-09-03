"""Tests for the integrations prior-art validator and its registry.

Run:  uv run --group dev pytest skills/integrations-prior-art-survey/scripts -q
"""

from __future__ import annotations

import copy
import json
import pathlib
import sys

import pytest
import yaml

HERE = pathlib.Path(__file__).resolve().parent
PKG = HERE.parent
ROOT = PKG.parents[1]
REGISTRY = PKG / "references" / "source-registry.yaml"
SCHEMAS = PKG / "schemas"
FIXTURES = HERE / "fixtures"

sys.path.insert(0, str(ROOT / "tests"))
import trigger_rules  # noqa: E402
from trigger_integrity import load_field_specs  # noqa: E402

SPECS = load_field_specs()


def _registry() -> dict:
    return yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))


def _rules(findings) -> set[str]:
    return {f.rule for f in findings}


# ---------------------------------------------------------------------------------------------
# C1a — the registry's structured predicates
# ---------------------------------------------------------------------------------------------


class TestTriggerIntegrity:
    def test_no_angle_reports_a_fail_severity_finding(self):
        """EC11b, first clause."""
        reg = _registry()
        found = [
            f
            for a in reg["angles"]
            for f in trigger_rules.check_angle(
                (reg.get("type_trigger") or {}).get("predicate"), a, SPECS, reg.get("coherence_axioms") or []
            )
            if f.severity == "fail"
        ]
        assert not found, "\n".join(str(f) for f in found)

    def test_the_run_is_NOT_registry_out_of_scope(self):
        """EC11b's anti-vacuity clause, and it is the half that matters.

        A SKIPPED registry also returns zero `fail`s, so the first clause alone is vacuously
        satisfiable. Asserting the run actually engaged is what makes the first clause mean
        anything.
        """
        reg = _registry()
        skips = {
            f.rule
            for a in reg["angles"]
            for f in trigger_rules.check_angle(
                (reg.get("type_trigger") or {}).get("predicate"), a, SPECS, reg.get("coherence_axioms") or []
            )
            if f.severity == "skip"
        }
        assert "registry-out-of-scope" not in skips, (
            "the trigger-integrity run was SKIPPED, so its zero-fails result proves nothing"
        )

    def test_a_TAUTOLOGICAL_angle_DOES_fail_angle_always_fires(self):
        """The probe that proves the rule, not just the data.

        A test asserting only that today's registry is clean proves nothing about the check. This
        anchors an angle on `integrations.expected`, which the type trigger entails, and requires
        the shared engine to refuse it.
        """
        reg = _registry()
        tautological = copy.deepcopy(reg["angles"][3])  # b1, a conditional angle
        tautological["id"] = "zz-tautology"
        tautological["precondition"] = "integrations.expected"
        tautological["trigger_anchor"] = ["integrations.expected"]
        tautological["predicate"] = [[{"field": "integrations.expected", "op": "is_true"}]]

        found = trigger_rules.check_angle(
            (reg.get("type_trigger") or {}).get("predicate"),
            tautological,
            SPECS,
            reg.get("coherence_axioms") or [],
        )
        assert "angle-always-fires" in _rules(found), (
            "an angle anchored on a field the type trigger entails was accepted; "
            f"got {sorted(_rules(found))}"
        )


class TestFallbackForest:
    """The graph is WALKED, not asserted. Requiring every row to name a fallback in a finite
    graph guarantees a cycle by pigeonhole -- a sibling shipped exactly that."""

    def _edges(self) -> dict[str, str | None]:
        return {s["id"]: s["fallback"] for s in _registry()["sources"]}

    def test_shape_is_23_rows_and_6_terminals(self):
        fb = self._edges()
        assert len(fb) == 23
        assert sorted(k for k, v in fb.items() if v is None) == [
            "apis-guru",
            "ecosystems-packages",
            "mcp-registry-github",
            "nango-providers",
            "standard-webhooks",
            "vendor-docs",
        ]

    def test_no_dangling_fallback(self):
        fb = self._edges()
        assert not [(k, v) for k, v in fb.items() if v is not None and v not in fb]

    def test_no_cycles(self):
        fb = self._edges()

        def cycles(start: str) -> bool:
            seen, node = {start}, start
            while fb.get(node):
                node = fb[node]
                if node in seen:
                    return True
                seen.add(node)
            return False

        assert not [k for k in fb if cycles(k)]

    def test_every_terminal_declares_a_rationale(self):
        """`fallback: null` alone is a hole; null WITH a rationale is a decision."""
        bad = [
            s["id"]
            for s in _registry()["sources"]
            if s["fallback"] is None and not str(s.get("fallback_rationale") or "").strip()
        ]
        assert not bad, f"terminals with no rationale: {bad}"

    def test_this_registry_is_NOT_in_the_shared_guards_KNOWN_CYCLES(self):
        import test_registry_fallback_graph as guard

        assert PKG.name not in getattr(guard, "KNOWN_CYCLES", {}), (
            "this registry is exempted from the shared cycle guard, which is how a cycle ships"
        )


class TestCompleteListingAssignment:
    """The two sets are asserted EQUAL, not eyeballed. A derivation that states a total is only as
    good as its MEMBERSHIP -- the failure it replaces enumerated 18 rows and left five unassigned,
    and a correct-looking total is exactly what hides that."""

    def test_every_row_carries_a_value_and_no_value_names_a_missing_row(self):
        rows = {s["id"] for s in _registry()["sources"]}
        assigned = {s["id"] for s in _registry()["sources"] if "complete_listing" in s}
        assert rows - assigned == set(), f"rows with no complete_listing: {sorted(rows - assigned)}"
        assert assigned - rows == set()

    def test_the_partition_is_12_na_6_false_5_true(self):
        vals = [s["complete_listing"] for s in _registry()["sources"]]
        assert vals.count("n/a") == 12
        assert vals.count(False) == 6
        assert vals.count(True) == 5
        assert len(vals) == 23

    def test_every_value_is_one_of_the_three(self):
        bad = [
            (s["id"], s["complete_listing"])
            for s in _registry()["sources"]
            if s["complete_listing"] not in (True, False, "n/a")
        ]
        assert not bad, bad


class TestRegistryShape:
    def test_every_source_row_carries_the_eleven_required_keys(self):
        required = {
            "id", "url", "url_kind", "access_status", "authority_band", "complete_listing",
            "as_of", "note", "yields", "fallback", "fallback_rationale",
        }
        for s in _registry()["sources"]:
            assert not required - set(s), f"{s['id']} missing {sorted(required - set(s))}"

    def test_every_authority_band_is_one_of_the_four(self):
        bands = {"first-party", "connector-catalog", "aggregator", "community"}
        bad = [(s["id"], s["authority_band"]) for s in _registry()["sources"] if s["authority_band"] not in bands]
        assert not bad, bad

    def test_a_registry_wide_probe_default_ships(self):
        """Without it a row carrying no `probe_method` has no declared method at all, and a
        criterion asserting only "present and non-empty" is satisfied by `probe_method: "yes"`."""
        d = _registry()["probe_default"]
        assert d["method"] == "GET"
        assert "user_agent" in d and str(d.get("note") or "").strip()

    def test_every_angle_source_and_fallback_resolves_to_a_row(self):
        reg = _registry()
        rows = {s["id"] for s in reg["sources"]}
        for a in reg["angles"]:
            assert not set(a["sources"]) - rows, f"{a['id']} names non-rows"
            assert a["fallback"] in rows, f"{a['id']} fallback {a['fallback']!r} is not a row"

    def test_no_always_on_angle_carries_widening_legs(self):
        """`seed-input-not-widening`'s own invariant, at the registry.

        A widening leg is a PREDICATE term and an always-on angle carries no predicate. Nothing
        shipped enforces this -- `predicate-only-on-conditional` fires on the `predicate` key alone
        and `widening_legs` is read by no shared check -- so this package asserts it itself.
        """
        bad = [a["id"] for a in _registry()["angles"] if a["trigger"] == "always" and a["widening_legs"]]
        assert not bad, f"always-on angles carrying widening_legs: {bad}"

    def test_seed_input_is_carried_and_is_not_a_widening_leg(self):
        reg = _registry()
        seeded = {a["id"]: a["seed_input"] for a in reg["angles"] if a["seed_input"]}
        assert seeded == {"a1": "integrations.third_party_list", "a3": "integrations.third_party_list"}
        for a in reg["angles"]:
            assert a["seed_input"] not in (a["widening_legs"] or []), a["id"]

    def test_axis_and_angle_reconcile_in_BOTH_directions(self):
        axes = {"category", "capability", "service", "pattern", "domain-noun", "seed-product"}
        reg = _registry()
        searched = {t for a in reg["angles"] for t in a["applicable_group_types"]}
        assert axes - searched == set(), f"axes no angle searches: {sorted(axes - searched)}"
        assert not [a["id"] for a in reg["angles"] if not a["applicable_group_types"]]

    def test_pattern_is_reachable_only_through_the_conditional_b2(self):
        """The reconciliation's one survivor, stated because it is exactly the kind of thing that
        ships unnoticed: `pattern` is an `absent_types` candidate whenever b2 does not hold."""
        reg = _registry()
        carriers = [a["id"] for a in reg["angles"] if "pattern" in a["applicable_group_types"]]
        assert carriers == ["b2"]
        assert next(a for a in reg["angles"] if a["id"] == "b2")["trigger"] == "conditional"

    def test_the_excluded_block_ships_with_a_status_from_the_three(self):
        statuses = {"excluded-on-terms", "excluded-on-robots", "excluded-on-authority"}
        ex = _registry()["excluded"]
        assert ex
        for e in ex:
            assert e["status"] in statuses, e
            assert str(e.get("evidence") or "").strip()
            assert str(e.get("replacement") or "").strip()

    def test_no_excluded_id_is_also_a_source_row(self):
        reg = _registry()
        rows = {s["id"] for s in reg["sources"]}
        clash = [e["id"] for e in reg["excluded"] if e["id"] in rows]
        assert not clash, f"excluded rows that are also active sources: {clash}"


# ---------------------------------------------------------------------------------------------
# C1 — the clean fixtures validate against their SCHEMA
# ---------------------------------------------------------------------------------------------


class TestCleanFixturesValidateAgainstTheirSchema:
    """NOT "at exit 0" -- the validator does not exist until C2a, and an exit check that needs a
    later task is not a check."""

    @staticmethod
    def _check(schema_name: str, fixture_name: str):
        jsonschema = pytest.importorskip("jsonschema")
        schema = json.loads((SCHEMAS / schema_name).read_text(encoding="utf-8"))
        doc = yaml.safe_load((FIXTURES / fixture_name).read_text(encoding="utf-8"))
        errs = sorted(
            jsonschema.Draft202012Validator(schema).iter_errors(doc), key=lambda e: list(e.path)
        )
        assert not errs, "\n".join(f"{list(e.path)}: {e.message}" for e in errs[:6])

    def test_the_map_fixture(self):
        self._check("integration-vocabulary-map.schema.json", "integration-vocabulary-map.valid.yaml")

    def test_the_search_fixture(self):
        self._check("search-output.schema.json", "search-output.valid.yaml")

    def test_every_registry_row_is_in_exactly_one_of_active_or_skipped(self):
        rows = {s["id"] for s in _registry()["sources"]}
        m = yaml.safe_load((FIXTURES / "integration-vocabulary-map.valid.yaml").read_text())
        active = {a["id"] for a in m["sources"]["active"]}
        skipped = {s["id"] for s in m["sources"]["skipped"]}
        assert not active & skipped
        assert (active | skipped) == rows
