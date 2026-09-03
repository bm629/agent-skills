"""Tests for the integrations prior-art validator and its registry.

Run:  uv run --group dev pytest skills/integrations-prior-art-survey/scripts -q
"""

from __future__ import annotations

import copy
import os
import json
import re
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


# ---------------------------------------------------------------------------------------------
# C2a — the validator: registry integrity and the EXIT CONTRACT
# ---------------------------------------------------------------------------------------------

import importlib.util  # noqa: E402
import subprocess  # noqa: E402

SCRIPT = HERE / "validate_integrations_prior_art.py"


def _load_validator():
    spec = importlib.util.spec_from_file_location("v_integrations", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["v_integrations"] = mod
    spec.loader.exec_module(mod)
    return mod


V = pytest.importorskip("v_integrations") if False else None  # placeholder, see fixture below


@pytest.fixture(scope="module")
def val():
    return _load_validator()


def _reg_rules(mod, doc) -> set[str]:
    return {line.split(":", 1)[0].removeprefix("FAIL ").strip() for line in mod.registry_failures(doc)}


class TestRegistryIntegrityRulesFire:
    """Each rule on its OWN mutation of the shipped registry."""

    def test_yields_declared(self, val):
        d = _registry()
        del d["sources"][0]["yields"]
        assert "yields-declared" in _reg_rules(val, d)

    def test_complete_listing_declared(self, val):
        d = _registry()
        del d["sources"][2]["complete_listing"]
        assert "complete-listing-declared" in _reg_rules(val, d)

    def test_authority_band_known_on_a_missing_band(self, val):
        d = _registry()
        del d["sources"][1]["authority_band"]
        assert "authority-band-known" in _reg_rules(val, d)

    def test_authority_band_known_on_a_band_outside_the_four(self, val):
        d = _registry()
        d["sources"][1]["authority_band"] = "semi-official"
        assert "authority-band-known" in _reg_rules(val, d)

    def test_probe_method_shape(self, val):
        d = _registry()
        d["sources"][4]["probe_method"] = "yes"
        assert "probe-method-shape" in _reg_rules(val, d)

    def test_terminal_needs_rationale(self, val):
        d = _registry()
        t = next(s for s in d["sources"] if s["fallback"] is None)
        t["fallback_rationale"] = "  "
        assert "terminal-needs-rationale" in _reg_rules(val, d)

    def test_fallback_unresolvable(self, val):
        d = _registry()
        d["sources"][1]["fallback"] = "no-such-row"
        assert "fallback-unresolvable" in _reg_rules(val, d)

    def test_fallback_cycle(self, val):
        d = _registry()
        by = {s["id"]: s for s in d["sources"]}
        by["n8n-nodes"]["fallback"] = "activepieces-pieces"
        by["activepieces-pieces"]["fallback"] = "n8n-nodes"
        assert "fallback-cycle" in _reg_rules(val, d)

    def test_seed_input_not_widening(self, val):
        """This package's OWN guard. `predicate-only-on-conditional` fires on the `predicate` key
        alone and `widening_legs` is read by no shared check, so an always-on angle carrying one
        loads clean and emits nothing."""
        d = _registry()
        a1 = next(a for a in d["angles"] if a["id"] == "a1")
        a1["widening_legs"] = ["integrations.third_party_list"]
        assert "seed-input-not-widening" in _reg_rules(val, d)

    def test_the_registry_wide_probe_default_is_asserted_present(self, val):
        d = _registry()
        del d["probe_default"]
        assert "probe-method-shape" in _reg_rules(val, d)

    def test_the_SHIPPED_registry_emits_nothing(self, val):
        """The mirror for every rule above: they fire on a mutation and are silent on the real
        thing. Without this the suite cannot tell a working rule from one that always fires."""
        assert val.registry_failures(_registry()) == []


class TestExitContract:
    """The exit CLASS is tested per rule, not in aggregate."""

    @staticmethod
    def _run(*args: str) -> int:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args], capture_output=True, text=True
        ).returncode

    def test_a_clean_map_exits_0(self):
        assert self._run("keyword-map", str(FIXTURES / "integration-vocabulary-map.valid.yaml")) == 0

    def test_a_clean_search_exits_0(self):
        assert (
            self._run(
                "search",
                str(FIXTURES / "search-output.valid.yaml"),
                "--keyword-map",
                str(FIXTURES / "integration-vocabulary-map.valid.yaml"),
            )
            == 0
        )

    def test_an_unreadable_input_is_exit_2(self, tmp_path):
        assert self._run("keyword-map", str(tmp_path / "nope.yaml")) == 2

    def test_an_unusable_keyword_map_is_exit_2(self, tmp_path):
        bad = tmp_path / "bad.yaml"
        bad.write_text("[1, 2, 3]\n")
        assert (
            self._run(
                "search", str(FIXTURES / "search-output.valid.yaml"), "--keyword-map", str(bad)
            )
            == 2
        )

    def test_a_SCHEMA_invalid_artifact_is_exit_1_not_2(self, tmp_path):
        """`schema` is the AUTHOR's to fix, so it is exit 1 -- unlike the four input-class faults.
        The shipped precedent agrees (`validate_regulatory_prior_art.py:435`)."""
        doc = yaml.safe_load((FIXTURES / "integration-vocabulary-map.valid.yaml").read_text())
        del doc["meta"]["classification"]
        p = tmp_path / "m.yaml"
        p.write_text(yaml.safe_dump(doc))
        assert self._run("keyword-map", str(p)) == 1

    def test_the_EXIT_2_SET_is_DERIVED_from_registry_failures_not_hand_copied(self, val):
        """An earlier version compared the constant to a hand-copied literal of the same strings --
        two copies of one list, so a rule added to `registry_failures` and left out of the constant
        kept every test green. The set is now derived from the function's own AST."""
        import ast

        tree = ast.parse(_SRC)
        fn = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == "registry_failures")
        emitted = {
            n.args[0].value
            for n in ast.walk(fn)
            if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "_fail"
            and n.args and isinstance(n.args[0], ast.Constant)
        }
        assert val.EXIT2_REGISTRY_RULES == emitted, {
            "emitted but not in the exit-2 set": sorted(emitted - val.EXIT2_REGISTRY_RULES),
            "in the set but emitted by nothing": sorted(val.EXIT2_REGISTRY_RULES - emitted),
        }

    def test_every_exit_2_registry_rule_is_actually_emitted_by_registry_failures(self, val):
        """A rule in the exit-2 set that nothing emits is a class with no members."""
        import re as _re

        src = SCRIPT.read_text(encoding="utf-8")
        emitted = set(_re.findall(r'_fail\(\s*"([a-z][a-z0-9-]+)"', src))
        assert val.EXIT2_REGISTRY_RULES <= emitted, val.EXIT2_REGISTRY_RULES - emitted

    def test_a_broken_registry_is_exit_2_through_MAIN(self, tmp_path, monkeypatch):
        """Through main(), not by calling the function -- the exit class is main's to decide."""
        d = _registry()
        del d["sources"][0]["yields"]
        broken = tmp_path / "source-registry.yaml"
        broken.write_text(yaml.safe_dump(d))
        r = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "keyword-map",
                str(FIXTURES / "integration-vocabulary-map.valid.yaml"),
            ],
            capture_output=True,
            text=True,
            env={**os.environ, "INTEGRATIONS_REGISTRY": str(broken)},
        )
        assert r.returncode == 2, r.stdout
        assert "yields-declared" in r.stdout


class TestNarrowMirrorsForThisTasksNeedRules:
    """EC2's `need ⊆ narrow`: every membership/threshold rule this task owns carries an explicit
    NARROW mirror, because those are exactly the rules a clean fixture sitting far from the
    boundary cannot exercise."""

    def test_authority_band_known_does_not_fire_on_a_legal_band(self, val):
        d = _registry()
        d["sources"][1]["authority_band"] = "community"
        assert "authority-band-known" not in _reg_rules(val, d)

    def test_complete_listing_declared_does_not_fire_on_a_legal_na(self, val):
        d = _registry()
        d["sources"][0]["complete_listing"] = "n/a"
        assert "complete-listing-declared" not in _reg_rules(val, d)

    def test_yields_declared_does_not_fire_on_a_present_yield(self, val):
        d = _registry()
        d["sources"][0]["yields"] = "one row"
        assert "yields-declared" not in _reg_rules(val, d)

    def test_probe_method_shape_does_not_fire_on_a_legal_override(self, val):
        d = _registry()
        d["sources"][4]["probe_method"] = {"method": "GET", "headers": {}, "user_agent": "default", "note": "x"}
        assert "probe-method-shape" not in _reg_rules(val, d)

    def test_terminal_needs_rationale_does_not_fire_on_a_NON_terminal(self, val):
        d = _registry()
        row = next(s for s in d["sources"] if s["fallback"] is not None)
        row["fallback_rationale"] = "  "
        assert "terminal-needs-rationale" not in _reg_rules(val, d)

    def test_fallback_cycle_does_not_fire_on_the_acyclic_forest(self, val):
        assert "fallback-cycle" not in _reg_rules(val, _registry())

    def test_fallback_unresolvable_does_not_fire_on_a_resolvable_edge(self, val):
        d = _registry()
        d["sources"][1]["fallback"] = "nango-providers"
        assert "fallback-unresolvable" not in _reg_rules(val, d)

    def test_seed_input_not_widening_does_not_fire_on_a_CONDITIONAL_angles_widening_leg(self, val):
        """The narrow half: b1 legitimately carries a widening leg, and the rule must not touch it."""
        d = _registry()
        b1 = next(a for a in d["angles"] if a["id"] == "b1")
        assert b1["widening_legs"], "fixture assumption: b1 carries a widening leg"
        assert "seed-input-not-widening" not in _reg_rules(val, d)


# ---------------------------------------------------------------------------------------------
# C2b — the validator: MAP rules
# ---------------------------------------------------------------------------------------------


def _map() -> dict:
    return yaml.safe_load((FIXTURES / "integration-vocabulary-map.valid.yaml").read_text())


def _map_rules(mod, doc) -> set[str]:
    return {ln.split(":", 1)[0].removeprefix("FAIL ").strip() for ln in mod.validate_keyword_map(doc, _registry())}


class TestMapRulesFire:
    def test_the_CLEAN_map_emits_nothing(self, val):
        assert val.validate_keyword_map(_map(), _registry()) == []

    def test_group_id_unique(self, val):
        d = _map()
        d["groups"].append(dict(d["groups"][0]))
        assert "group-id-unique" in _map_rules(val, d)

    def test_group_type_accounted(self, val):
        d = _map()
        d["groups"] = [g for g in d["groups"] if g["type"] != "pattern"]
        assert "group-type-accounted" in _map_rules(val, d)

    def test_group_type_accounted_is_SILENT_when_the_axis_is_declared_absent(self, val):
        """The narrow mirror: an axis with no group is legal when the map SAYS so."""
        d = _map()
        d["groups"] = [g for g in d["groups"] if g["type"] != "pattern"]
        d["scope_guard"]["absent_types"] = ["pattern"]
        assert "group-type-accounted" not in _map_rules(val, d)

    def test_expansion_floor_fires_on_a_thin_category_group(self, val):
        d = _map()
        next(g for g in d["groups"] if g["type"] == "category")["expansions"] = ["one"]
        assert "expansion-floor" in _map_rules(val, d)

    def test_expansion_floor_does_NOT_apply_to_service_or_seed_product(self, val):
        """Exactly the four axes §2.1 names -- the canonical on the other two is a proper noun the
        corpus spells once, and applying the floor there would demand invented spellings."""
        d = _map()
        for g in d["groups"]:
            if g["type"] in ("service", "seed-product"):
                g["expansions"] = []
        assert "expansion-floor" not in _map_rules(val, d)

    def test_expansion_cap(self, val):
        d = _map()
        g = d["groups"][0]
        g["expansion_cap"] = 1
        assert "expansion-cap" in _map_rules(val, d)

    def test_negative_terms_required_on_category_and_domain_noun(self, val):
        for axis in ("category", "domain-noun"):
            d = _map()
            next(g for g in d["groups"] if g["type"] == axis)["negative_terms"] = []
            assert "negative-terms-required" in _map_rules(val, d), axis

    def test_negative_terms_NOT_required_on_the_other_four_axes(self, val):
        d = _map()
        for g in d["groups"]:
            if g["type"] not in ("category", "domain-noun"):
                g.pop("negative_terms", None)
        assert "negative-terms-required" not in _map_rules(val, d)

    def test_term_sited_once_when_the_owner_does_not_carry_the_term(self, val):
        d = _map()
        d["scope_guard"]["shared_terms"][0]["owner"] = "g-cap-notify"
        assert "term-sited-once" in _map_rules(val, d)

    def test_angle_verdict_complete(self, val):
        d = _map()
        d["angle_applicability"] = d["angle_applicability"][:-1]
        assert "angle-verdict-complete" in _map_rules(val, d)

    def test_angle_verdict_unique(self, val):
        d = _map()
        d["angle_applicability"].append(dict(d["angle_applicability"][0]))
        assert "angle-verdict-unique" in _map_rules(val, d)

    def test_applicability_angle_unknown(self, val):
        d = _map()
        d["angle_applicability"][0]["angle_id"] = "b9"
        assert "applicability-angle-unknown" in _map_rules(val, d)

    def test_always_on_angle_holds(self, val):
        d = _map()
        next(v for v in d["angle_applicability"] if v["angle_id"] == "a1")["holds"] = False
        assert "always-on-angle-holds" in _map_rules(val, d)

    def test_probe_record(self, val):
        d = _map()
        d["probe"]["note"] = "   "
        assert "probe-record" in _map_rules(val, d)

    def test_source_unaccounted_when_a_row_is_in_neither(self, val):
        d = _map()
        d["sources"]["active"] = d["sources"]["active"][:-1]
        assert "source-unaccounted" in _map_rules(val, d)

    def test_source_unaccounted_when_a_row_is_in_BOTH(self, val):
        d = _map()
        d["sources"]["skipped"].append({"id": d["sources"]["active"][0]["id"],
                                        "cause_class": "refused", "cause": "x"})
        assert "source-unaccounted" in _map_rules(val, d)

    def test_skipped_source_cause(self, val):
        d = _map()
        d["sources"]["skipped"][0]["cause"] = "  "
        assert "skipped-source-cause" in _map_rules(val, d)

    def test_skipped_source_still_carried(self, val):
        """A row skipped as `no-holding-angle` while an angle that HOLDS carries it."""
        d = _map()
        row = next(s for s in d["sources"]["skipped"] if s["cause_class"] == "no-holding-angle")
        next(v for v in d["angle_applicability"] if v["angle_id"] == "b5")["holds"] = True
        assert "skipped-source-still-carried" in _map_rules(val, d), row["id"]

    def test_skipped_source_still_carried_is_SILENT_on_a_refused_row(self, val):
        """The narrow half: `refused` is about the CHANNEL, not about which angles hold, so a
        holding angle carrying a refused row is correct rather than contradictory."""
        d = _map()
        assert "skipped-source-still-carried" not in _map_rules(val, d)

    def test_sanitization_cause(self, val):
        d = _map()
        next(a for a in d["sources"]["active"] if a["sanitization"]["status"] != "clean")["sanitization"]["cause"] = None
        assert "sanitization-cause" in _map_rules(val, d)

    def test_sanitization_cause_is_SILENT_on_clean(self, val):
        d = _map()
        for a in d["sources"]["active"]:
            a["sanitization"] = {"status": "clean", "cause": None}
        assert "sanitization-cause" not in _map_rules(val, d)

    def test_forbidden_source_not_active(self, val):
        d = _map()
        d["sources"]["active"].append({
            "id": "rapidapi-hub", "as_of": "2026-09-03", "access_status": "open",
            "sanitization": {"status": "clean", "cause": None}})
        assert "forbidden-source-not-active" in _map_rules(val, d)

    def test_EC9_deleting_a_verdict_fails_for_an_ALWAYS_ON_and_a_CONDITIONAL_angle(self, val):
        """EC9 requires BOTH mutations, not one."""
        for aid in ("a1", "b3"):
            d = _map()
            d["angle_applicability"] = [v for v in d["angle_applicability"] if v["angle_id"] != aid]
            assert "angle-verdict-complete" in _map_rules(val, d), aid
        assert val.validate_keyword_map(_map(), _registry()) == []


# ---------------------------------------------------------------------------------------------
# C2c — the validator: the 2-D COVERAGE rules
# ---------------------------------------------------------------------------------------------


def _search() -> dict:
    return yaml.safe_load((FIXTURES / "search-output.valid.yaml").read_text())


def _s_rules(mod, doc) -> set[str]:
    return {
        ln.split(":", 1)[0].removeprefix("FAIL ").strip()
        for ln in mod.validate_search(doc, _registry(), _map())
    }


class TestCoverageRulesFire:
    def test_the_CLEAN_search_output_emits_nothing(self, val):
        assert val.validate_search(_search(), _registry(), _map()) == []

    def test_angle_unknown_fires_and_RETURNS_EARLY(self, val):
        """An unknown angle is exit 1 from both sites and that is deliberate: a wrong meta.angle_id
        is a fault IN the artifact, and its author can fix it. The EARLY RETURN is the point --
        nothing below may compare against an empty contract."""
        d = _search()
        d["meta"]["angle_id"] = "zz"
        lines = val.validate_search(d, _registry(), _map())
        assert len(lines) == 1 and "angle-unknown" in lines[0], lines

    def test_cell_pair_unique(self, val):
        d = _search()
        d["coverage"].append(dict(d["coverage"][0]))
        assert "cell-pair-unique" in _s_rules(val, d)

    def test_cell_group_known(self, val):
        d = _search()
        d["coverage"][0]["group_id"] = "g-nope"
        assert "cell-group-known" in _s_rules(val, d)

    def test_cell_source_known(self, val):
        d = _search()
        d["coverage"][0]["source_id"] = "nope"
        assert "cell-source-known" in _s_rules(val, d)

    def test_cell_source_excluded(self, val):
        d = _search()
        d["coverage"][0]["source_id"] = "rapidapi-hub"
        assert "cell-source-excluded" in _s_rules(val, d)

    def test_cell_in_applicable_set(self, val):
        d = _search()
        d["coverage"][0]["source_id"] = "apis-guru"  # a2's source, not a1's
        assert "cell-in-applicable-set" in _s_rules(val, d)

    def test_reached_needs_counts(self, val):
        d = _search()
        del d["coverage"][0]["kept"]
        assert "reached-needs-counts" in _s_rules(val, d)

    def test_count_frame_required(self, val):
        d = _search()
        d["coverage"][0]["count_frame"] = None
        assert "count-frame-required" in _s_rules(val, d)

    def test_count_frame_NOT_required_on_a_zero(self, val):
        """The narrow half: a zero has nothing to frame."""
        d = _search()
        c = d["coverage"][0]
        c["returned"] = 0
        c["kept"] = 0
        c["count_frame"] = None
        d["candidates"] = [x for x in d["candidates"] if x["found_by"] != f"{c['group_id']}/{c['source_id']}"]
        d["unadmitted"] = [x for x in d["unadmitted"] if x["found_by"] != f"{c['group_id']}/{c['source_id']}"]
        assert "count-frame-required" not in _s_rules(val, d)

    def test_status_needs_cause(self, val):
        d = _search()
        c = d["coverage"][0]
        c["status"] = "unreachable"
        c["returned"] = 0
        c["kept"] = 0
        c["cause"] = None
        assert "status-needs-cause" in _s_rules(val, d)

    def test_coverage_unreached_has_count(self, val):
        d = _search()
        c = d["coverage"][0]
        c["status"] = "gated"
        c["cause"] = "401 at the catalog"
        assert "coverage-unreached-has-count" in _s_rules(val, d)

    def test_cell_sanitization_cause(self, val):
        d = _search()
        d["coverage"][0]["sanitization"] = {"status": "modified", "cause": None}
        assert "cell-sanitization-cause" in _s_rules(val, d)

    def test_fallback_used_shape_refuses_a_BARE_id(self, val):
        d = _search()
        d["coverage"][0]["fallback_used"] = "nango-providers"
        assert "fallback-used-shape" in _s_rules(val, d)

    def test_fallback_used_unknown(self, val):
        d = _search()
        d["coverage"][0]["fallback_used"] = "row:no-such-row"
        assert "fallback-used-unknown" in _s_rules(val, d)

    def test_fallback_declared_compares_the_PARSED_TARGET(self, val):
        """Three siblings compare the RAW token and would reject every legal value of this field.
        This type follows ml: the prefix is parsed and the TARGET is checked against the level's
        own declaration."""
        d = _search()
        c = next(c for c in d["coverage"] if c["source_id"] == "n8n-nodes")
        c["fallback_used"] = "row:apis-guru"  # n8n-nodes declares nango-providers
        assert "fallback-declared" in _s_rules(val, d)

    def test_fallback_declared_ACCEPTS_the_declared_row_level_route(self, val):
        d = _search()
        c = next(c for c in d["coverage"] if c["source_id"] == "n8n-nodes")
        c["fallback_used"] = "row:nango-providers"
        assert "fallback-declared" not in _s_rules(val, d)

    def test_fallback_declared_ACCEPTS_the_declared_angle_level_route(self, val):
        d = _search()
        d["coverage"][0]["fallback_used"] = "angle:nango-providers"  # a1's declared fallback
        assert "fallback-declared" not in _s_rules(val, d)

    def test_coverage_complete(self, val):
        d = _search()
        dropped = d["coverage"].pop()
        key = f"{dropped['group_id']}/{dropped['source_id']}"
        d["candidates"] = [x for x in d["candidates"] if x["found_by"] != key]
        d["unadmitted"] = [x for x in d["unadmitted"] if x["found_by"] != key]
        assert "coverage-complete" in _s_rules(val, d)

    def test_row_cell_unknown(self, val):
        d = _search()
        d["candidates"][0]["found_by"] = "g-cat-scheduling/apis-guru"
        assert "row-cell-unknown" in _s_rules(val, d)

    def test_rows_cite_an_unreached_cell(self, val):
        d = _search()
        key = d["candidates"][0]["found_by"]
        g, s = key.split("/")
        c = next(c for c in d["coverage"] if c["group_id"] == g and c["source_id"] == s)
        c["status"] = "unreachable"
        c["returned"] = 0
        c["cause"] = "503 from the catalog"
        assert "rows-cite-an-unreached-cell" in _s_rules(val, d)


class TestOwedSetUsesAllThreeTerms:
    """EC3. Dropping any one term changes the grid, and the exemplar's real numbers say by how much."""

    def test_the_exemplar_owes_exactly_25_cells(self, val):
        reg, m = _registry(), _map()
        a1 = next(a for a in reg["angles"] if a["id"] == "a1")
        assert len(val._owed_cells(a1, m)) == 25

    def test_dropping_the_angles_OWN_source_list_INFLATES_the_grid(self, val):
        """5 groups x 5 of a1's active sources = 25. Without the second term every angle would owe
        every ACTIVE row -- 5 x 19 = 95, nearly four times the real obligation."""
        reg, m = _registry(), _map()
        a1 = next(a for a in reg["angles"] if a["id"] == "a1")
        types = set(a1["applicable_group_types"])
        groups = [g["id"] for g in m["groups"] if g["type"] in types]
        active = {a["id"] for a in m["sources"]["active"]}
        assert len(groups) * len(active) == 95
        assert len(val._owed_cells(a1, m)) == 25

    def test_dropping_the_maps_ACTIVE_set_owes_a_row_this_run_never_had(self, val):
        """a1 carries six sources; the map SKIPPED make-integrations-sitemap, so the sixth is not
        owed. Without the third term the angle would owe a cell against a dead channel."""
        reg, m = _registry(), _map()
        a1 = next(a for a in reg["angles"] if a["id"] == "a1")
        owed = val._owed_cells(a1, m)
        assert len(a1["sources"]) == 6
        assert not [k for k in owed if k[1] == "make-integrations-sitemap"]


# ---------------------------------------------------------------------------------------------
# C2d — counts, bound, outcome and candidates
# ---------------------------------------------------------------------------------------------


class TestOutcomeDecidesWhatIsOwed:
    def test_ran_requires_coverage(self, val):
        d = _search()
        d["coverage"] = []
        d["candidates"] = []
        d["unadmitted"] = []
        d["retrieval_summary"]["status_counts"] = {"reached": 0}
        assert "ran-requires-coverage" in _s_rules(val, d)

    def test_ran_attempted_nothing(self, val):
        d = _search()
        for c in d["coverage"]:
            c["status"] = "not-attempted"
            c["returned"] = 0
            c["kept"] = 0
            c["cause"] = "the angle was descoped mid-run"
        d["candidates"] = []
        d["unadmitted"] = []
        assert "ran-attempted-nothing" in _s_rules(val, d)

    def test_bound_required_on_ran(self, val):
        d = _search()
        del d["bound"]
        assert "bound-required" in _s_rules(val, d)

    def test_bound_is_NOT_required_on_not_run_or_vacated(self, val):
        """`bound` is owed on `ran` ALONE -- an angle that did not run bounded nothing."""
        for outcome, extra in (("not_run", {"not_run": {"map_verdict": "b5 does not hold"}}),
                               ("vacated", {"vacated": {"cause": "every channel refused"}})):
            d = _search()
            d["outcome"] = outcome
            d.pop("bound")
            d["candidates"] = []
            d["unadmitted"] = []
            if outcome == "not_run":
                d["coverage"] = []
                d.pop("retrieval_summary")
            else:
                for c in d["coverage"]:
                    c["status"] = "unreachable"
                    c["returned"] = 0
                    c["kept"] = 0
                    c["cause"] = "503"
                d["retrieval_summary"] = {"status_counts": {"unreachable": 25},
                                          "degraded_sources": [{"source_id": s, "status": "unreachable", "note": None}
                                                               for s in sorted({c["source_id"] for c in d["coverage"]})]}
            d.update(extra)
            assert "bound-required" not in _s_rules(val, d), outcome

    def test_summary_required(self, val):
        d = _search()
        del d["retrieval_summary"]
        assert "summary-required" in _s_rules(val, d)

    def test_unrun_angle_has_cells_and_candidates(self, val):
        d = _search()
        d["outcome"] = "not_run"
        d["not_run"] = {"map_verdict": "ruled out"}
        r = _s_rules(val, d)
        assert "unrun-angle-has-cells" in r
        assert "unrun-angle-has-candidates" in r

    def test_vacated_not_empty(self, val):
        d = _search()
        d["outcome"] = "vacated"
        d["vacated"] = {"cause": "every channel refused"}
        assert "vacated-not-empty" in _s_rules(val, d)


class TestBoundRules:
    def test_cap_matches_registry(self, val):
        d = _search()
        d["bound"]["cap"] = 7
        assert "cap-matches-registry" in _s_rules(val, d)

    def test_cap_respected_keys_off_the_REGISTRYS_cap(self, val):
        """Lowering the ARTIFACT's cap is a transcription defect, not a licence to carry more. The
        enforcement reads the registry, so a mis-transcribed cap cannot raise its own ceiling."""
        d, reg = _search(), _registry()
        next(a for a in reg["angles"] if a["id"] == "a1")["cap"] = 2
        d["bound"]["cap"] = 2
        r = {ln.split(":", 1)[0].removeprefix("FAIL ").strip() for ln in val.validate_search(d, reg, _map())}
        assert "cap-respected" in r

    def test_cap_respected_counts_CARRIED_rows_not_candidates_alone(self, val):
        """`cap` bounds candidates PLUS unadmitted. Counting candidates alone let an artifact carry
        unlimited unadmitted rows past its budget."""
        d, reg = _search(), _registry()
        n = len(d["candidates"]) + len(d["unadmitted"])
        next(a for a in reg["angles"] if a["id"] == "a1")["cap"] = n - 1
        d["bound"]["cap"] = n - 1
        r = {ln.split(":", 1)[0].removeprefix("FAIL ").strip() for ln in val.validate_search(d, reg, _map())}
        assert "cap-respected" in r

    def test_bound_hit_consistent_refuses_a_hit_with_no_cap(self, val):
        d = _search()
        d["bound"]["cap"] = None
        d["bound"]["hit"] = True
        d["bound"]["dropped_note"] = "x"
        assert "bound-hit-consistent" in _s_rules(val, d)

    def test_bound_hit_needs_note(self, val):
        d = _search()
        d["bound"]["hit"] = True
        assert "bound-hit-needs-note" in _s_rules(val, d)

    def test_ordering_matches_registry(self, val):
        d = _search()
        d["bound"]["ordering"] = "alphabetical"
        assert "ordering-matches-registry" in _s_rules(val, d)

    def test_ordering_deviation_is_ACCEPTED_when_stated(self, val):
        d = _search()
        d["bound"]["ordering"] = "alphabetical"
        d["bound"]["ordering_deviation"] = "the catalog's category rank was not exposed on this run"
        assert "ordering-matches-registry" not in _s_rules(val, d)

    def test_ordering_deviation_contradicts(self, val):
        d = _search()
        d["bound"]["ordering_deviation"] = "we deviated"
        assert "ordering-deviation-contradicts" in _s_rules(val, d)

    def test_bound_cap_null_is_legal_ONLY_where_the_REGISTRY_declares_it(self, val):
        """An earlier docstring said "a3 may resolve to no cap binds" -- a3 declares cap: 60, and
        NO angle in this registry declares a null. The claim was false and it blessed a real defect:
        a null cap skipped both cap rules, so 206 candidates against a declared cap of 90 produced
        zero findings. Null is legal only as a faithful transcription of a null."""
        d, reg = _search(), _registry()
        d["bound"]["cap"] = None
        d["bound"]["hit"] = False
        # against the SHIPPED registry, where a1 declares 90, a null is a transcription failure
        assert "cap-matches-registry" in {
            ln.split(":", 1)[0].removeprefix("FAIL ").strip()
            for ln in val.validate_search(d, reg, _map())}
        # and legal only where the registry declares one
        next(a for a in reg["angles"] if a["id"] == "a1")["cap"] = None
        assert val.validate_search(d, reg, _map()) == []


class TestSummaryAndCandidates:
    def test_summary_reconciles(self, val):
        d = _search()
        d["retrieval_summary"]["status_counts"] = {"reached": 1}
        assert "summary-reconciles" in _s_rules(val, d)

    def test_degraded_source_recorded(self, val):
        d = _search()
        c = d["coverage"][0]
        c["status"] = "rate-limited"
        c["returned"] = 0
        c["kept"] = 0
        c["cause"] = "429"
        d["candidates"] = [x for x in d["candidates"] if x["found_by"] != f"{c['group_id']}/{c['source_id']}"]
        d["unadmitted"] = [x for x in d["unadmitted"] if x["found_by"] != f"{c['group_id']}/{c['source_id']}"]
        assert "degraded-source-recorded" in _s_rules(val, d)

    def test_kept_exceeds_returned(self, val):
        d = _search()
        c = next(c for c in d["coverage"] if c["kept"] > 0)
        c["returned"] = 0
        assert "kept-exceeds-returned" in _s_rules(val, d)

    def test_kept_matches_rows_reconciles_candidates_PLUS_unadmitted(self, val):
        d = _search()
        d["coverage"][0]["kept"] = 99
        assert "kept-matches-rows" in _s_rules(val, d)

    def test_candidate_id_unique(self, val):
        d = _search()
        d["candidates"].append(dict(d["candidates"][0]))
        assert "candidate-id-unique" in _s_rules(val, d)

    def test_candidate_group_known(self, val):
        d = _search()
        d["candidates"][0]["found_by"] = "g-nope/nango-providers"
        assert "candidate-group-known" in _s_rules(val, d)

    def test_locator_resolvable(self, val):
        d = _search()
        d["candidates"][0]["locator"] = "see the register"
        assert "locator-resolvable" in _s_rules(val, d)

    def test_locator_resolvable_ACCEPTS_an_absolute_url(self, val):
        d = _search()
        d["candidates"][0]["locator"] = "http://example.com/x"
        assert "locator-resolvable" not in _s_rules(val, d)


class TestPresentOn:
    def test_present_on_source_known(self, val):
        d = _search()
        d["candidates"][0]["present_on"] = ["apis-guru"]
        assert "present-on-source-known" in _s_rules(val, d)

    def test_present_on_needs_reached_cell(self, val):
        """A member that is a legal a1 registry row but sits in the map's skipped[] -- so it has no
        REACHED cell in this artifact. Registry membership alone leaves the presence numerator
        unfalsifiable."""
        d = _search()
        c = d["candidates"][0]
        c["present_on"] = [*c["present_on"], "make-integrations-sitemap"]
        r = _s_rules(val, d)
        assert "present-on-needs-reached-cell" in r
        assert "present-on-source-known" not in r, "it IS a row a1 carries; only the cell is missing"

    def test_present_on_found_by_included(self, val):
        d = _search()
        c = d["candidates"][0]
        own = c["found_by"].split("/")[1]
        c["present_on"] = [m for m in c["present_on"] if m != own]
        assert "present-on-found-by-included" in _s_rules(val, d)

    def test_present_on_is_a1s_ALONE(self, val):
        d = _search()
        d["meta"]["angle_id"] = "b4"
        reg = _registry()
        b4 = next(a for a in reg["angles"] if a["id"] == "b4")
        b4["sources"] = list({c["source_id"] for c in d["coverage"]})
        b4["applicable_group_types"] = ["category", "capability", "domain-noun", "service"]
        assert "present-on-a1-only" in {
            ln.split(":", 1)[0].removeprefix("FAIL ").strip()
            for ln in val.validate_search(d, reg, _map())
        }


class TestEC3aTheProductOfBoundStates:
    """SIX combinations, not eight. `cap: null` forces `hit: false`, so the two
    (uncapped x truncated) cells are illegal by construction.

    Seven rules read `bound`, and a sibling shipped THREE separate defects where
    individually-correct rules left one combination with no writable form. Testing rules one at a
    time cannot see it."""

    @staticmethod
    def _build(capped: bool, deviated: bool, truncated: bool):
        d = _search()
        reg = _registry()
        a1 = next(a for a in reg["angles"] if a["id"] == "a1")
        b = d["bound"]
        if capped:
            b["cap"] = a1["cap"]
        else:
            b["cap"] = None
            a1["cap"] = None
        b["hit"] = truncated
        b["dropped_note"] = "12 rows below the cap, re-applicable by the stated ordering" if truncated else None
        if deviated:
            b["ordering"] = "alphabetical by provider"
            b["ordering_deviation"] = "the catalog's category rank was not exposed on this run"
        return d, reg

    @pytest.mark.parametrize(
        "capped,deviated,truncated",
        [(True, False, False), (True, False, True), (True, True, False),
         (True, True, True), (False, False, False), (False, True, False)],
    )
    def test_every_LEGAL_combination_validates_clean_TOGETHER(self, val, capped, deviated, truncated):
        d, reg = self._build(capped, deviated, truncated)
        assert val.validate_search(d, reg, _map()) == [], (capped, deviated, truncated)

    @pytest.mark.parametrize("deviated", [False, True])
    def test_the_two_UNCAPPED_TRUNCATED_cells_are_illegal_by_construction(self, val, deviated):
        d, reg = self._build(capped=False, deviated=deviated, truncated=True)
        assert "bound-hit-consistent" in {
            ln.split(":", 1)[0].removeprefix("FAIL ").strip()
            for ln in val.validate_search(d, reg, _map())
        }


# ---------------------------------------------------------------------------------------------
# C2e — the id grammars and record_filename
# ---------------------------------------------------------------------------------------------


class TestIdGrammars:
    @pytest.mark.parametrize("bad", ["Stripe.com", "https://stripe.com", "stripe.com/api",
                                     "stripe.com:443", "u@stripe.com", "localhost", "stripe.c0m"])
    def test_host_id_grammar_refuses(self, val, bad):
        d = _search()
        c = d["candidates"][0]
        c["item_id"] = bad
        c["id_class"] = "host"
        assert "host-id-grammar" in _s_rules(val, d), bad

    @pytest.mark.parametrize("ok", ["stripe.com", "firebase.google.com", "a-b.co.uk"])
    def test_host_id_grammar_ACCEPTS(self, val, ok):
        d = _search()
        c = d["candidates"][0]
        c["item_id"] = ok
        c["id_class"] = "host"
        c["present_on"] = c["present_on"]
        assert "host-id-grammar" not in _s_rules(val, d), ok

    @pytest.mark.parametrize("bad", ["NODOMAIN-a b", "NODOMAIN-a/b", "NODOMAIN-", "nodomain-x"])
    def test_nodomain_id_grammar_refuses(self, val, bad):
        d = _search()
        c = d["candidates"][-1]
        c["item_id"] = bad
        c["id_class"] = "nodomain"
        assert "nodomain-id-grammar" in _s_rules(val, d), bad

    def test_nodomain_id_grammar_ACCEPTS_the_EC7_counterexample(self, val):
        """The charset pin must still admit an id ending in `--<12 hex>`: the ENDING is what keeps
        record_filename's hash branch reachable."""
        d = _search()
        c = d["candidates"][-1]
        c["item_id"] = "NODOMAIN-acme--0123456789ab"
        c["id_class"] = "nodomain"
        assert "nodomain-id-grammar" not in _s_rules(val, d)

    def test_id_class_matches_id_both_directions(self, val):
        d = _search()
        d["candidates"][0]["id_class"] = "nodomain"
        assert "id-class-matches-id" in _s_rules(val, d)
        # The reverse direction is CONSTRUCTED, not read off a fixture position: the clean
        # fixture is measured from live catalogs and no public catalog carries a service whose
        # only home is a reserved name, so planting one to satisfy this test would fabricate the
        # very thing the fixture exists to avoid.
        d = _search()
        d["candidates"][-1]["item_id"] = "NODOMAIN-acme-internal"
        assert d["candidates"][-1]["id_class"] == "host"
        assert "id-class-matches-id" in _s_rules(val, d)


class TestRecordFilename:
    def test_a_safe_id_takes_the_IDENTITY_branch(self, val):
        assert val.record_filename("stripe.com") == "stripe.com"

    def test_the_HASH_branch_is_reachable_and_the_counterexample_is_CONSTRUCTIVE(self, val):
        """EC7. The identity branch has TWO conditions, not one: the safe charset AND the
        anti-fixed-point guard. `NODOMAIN-acme--0123456789ab` satisfies nodomain-id-grammar, matches
        the safe charset, and ends in `--<12 hex>` -- so it takes the HASH branch."""
        got = val.record_filename("NODOMAIN-acme--0123456789ab")
        assert got != "NODOMAIN-acme--0123456789ab"
        assert val._HASHED_STEM.search(got)

    def test_the_CROSS_BRANCH_collision_test(self, val):
        """The two branches must not meet: a hashed id and an identity id cannot produce one name."""
        a = val.record_filename("NODOMAIN-acme--0123456789ab")
        b = val.record_filename("NODOMAIN-acme")
        assert a != b

    def test_the_IDEMPOTENCE_mirror(self, val):
        """f(f(x)) == f(x) for an already-safe id. The sibling added this after a first version
        wrongly demanded the opposite of four correct inputs."""
        for i in ("stripe.com", "NODOMAIN-acme"):
            assert val.record_filename(val.record_filename(i)) == val.record_filename(i)

    def test_no_id_under_THIS_TYPES_grammar_reaches_the_branch_by_the_CHARSET_test(self, val):
        """A property over generated inputs, not a live example. Every host id and every
        NODOMAIN-<slug> is filename-safe, so the sanitizing branch is reached only through the
        anti-fixed-point guard."""
        for i in ("stripe.com", "firebase.google.com", "a-b.co.uk", "NODOMAIN-acme",
                  "NODOMAIN-a.b_c-d", "NODOMAIN-acme--0123456789ab"):
            assert val._SAFE_STEM.fullmatch(i), i


# ---------------------------------------------------------------------------------------------
# C2f — this type's own judgement-adjacent rules
# ---------------------------------------------------------------------------------------------


class TestOasAuthVocabulary:
    def test_oas_auth_vocabulary_refuses_a_non_null_outsider(self, val):
        d = _search()
        d["candidates"][0]["auth_scheme"] = "oauth3"
        assert "oas-auth-vocabulary" in _s_rules(val, d)

    def test_oas_auth_vocabulary_does_NOT_refuse_null(self, val):
        """`null` is the recorded value for a catalog auth_mode with no OAS member, so refusing it
        would refuse the very rows §3.5 mandates."""
        d = _search()
        c = d["candidates"][0]
        c["auth_scheme"] = None
        c["oauth_flow"] = None
        c["http_scheme"] = None
        assert "oas-auth-vocabulary" not in _s_rules(val, d)

    def test_oauth_flow_needs_oauth2(self, val):
        d = _search()
        c = d["candidates"][0]
        c["auth_scheme"] = "apiKey"
        c["oauth_flow"] = "authorizationCode"
        assert "oauth-flow-needs-oauth2" in _s_rules(val, d)

    def test_http_scheme_needs_http(self, val):
        d = _search()
        c = d["candidates"][0]
        c["http_scheme"] = "Bearer"  # against oauth2
        assert "http-scheme-needs-http" in _s_rules(val, d)

    @staticmethod
    def _an_http_candidate(d):
        """The clean fixture is MEASURED and none of the four vendors it found documents an OAS
        `http` scheme in prose, so this case is constructed. Planting a Basic-auth service to make
        the fixture carry one would fabricate the very thing the fixture exists to avoid."""
        c = d["candidates"][0]
        c["auth_scheme"], c["oauth_flow"] = "http", None
        return c

    def test_http_scheme_vocabulary_is_CASE_INSENSITIVE(self, val):
        """Real descriptors overwhelmingly write `scheme: bearer`. A JSON Schema enum is exact-match
        and would refuse it before this rule ran, leaving a correctly transcribed descriptor with no
        legal writing -- which is why the field carries a description and no enum."""
        d = _search()
        self._an_http_candidate(d)["http_scheme"] = "bearer"
        assert "http-scheme-vocabulary" not in _s_rules(val, d)

    def test_http_scheme_vocabulary_refuses_an_outsider(self, val):
        d = _search()
        self._an_http_candidate(d)["http_scheme"] = "SuperAuth"
        assert "http-scheme-vocabulary" in _s_rules(val, d)

    def test_the_auth_mode_map_covers_all_NINE_catalog_values(self, val):
        """Two prose sites said "three of the nine map to null" while the constant mapped FIVE, and
        the constant's keys disagreed with the design on four of nine. The count is now DERIVED
        from the table, and the table is shipped in prose."""
        m = val.AUTH_MODE_TO_OAS
        assert len(m) == 9
        assert set(m) == {"API_KEY", "OAUTH2", "OAUTH2_CC", "BASIC", "JWT",
                          "OAUTH1", "TWO_STEP", "MCP_OAUTH2", "NONE"}
        assert set(v for v in m.values() if v) <= set(val.OAS_AUTH_SCHEMES)

    def test_the_NULL_mapping_count_is_DERIVED_not_typed(self, val):
        assert val.AUTH_MODES_MAPPING_TO_NULL == tuple(
            k for k, v in val.AUTH_MODE_TO_OAS.items() if v is None)
        assert len(val.AUTH_MODES_MAPPING_TO_NULL) == 4

    def test_an_UNMAPPED_catalog_value_takes_the_same_treatment_as_the_four(self, val):
        """A value the map does not carry records `null`, exactly as the mapped-to-null ones do --
        forcing it into the nearest-looking member would assert a scheme the service does not offer."""
        assert val.AUTH_MODE_TO_OAS.get("SOME_NEW_MODE") is None


class TestEnumerated:
    def test_enumerated_required_on_a_LISTING_row(self, val):
        d = _search()
        del d["coverage"][0]["enumerated"]
        assert "enumerated-required" in _s_rules(val, d)

    def test_enumerated_is_NOT_asked_of_an_na_row(self, val):
        """A cell against a first-party page is asked nothing: requiring an enumeration verdict
        there would demand an answer to a question that does not apply."""
        reg = _registry()
        next(s for s in reg["sources"] if s["id"] == "n8n-nodes")["complete_listing"] = "n/a"
        d = _search()
        for c in d["coverage"]:
            if c["source_id"] == "n8n-nodes":
                del c["enumerated"]
        r = {ln.split(":", 1)[0].removeprefix("FAIL ").strip() for ln in val.validate_search(d, reg, _map())}
        assert "enumerated-required" not in r
        # THE mirror that matters, and the one an earlier version put on the wrong fixture: the
        # rule must be SILENT on the legal ABSENT state, which only exists once a row is n/a.
        # Asserted here rather than against the clean fixture, whose a1 corpus has no n/a row --
        # a mirror whose precondition is unreachable passes against a broken validator.
        assert "enumerated-absent-on-na" not in r

    def test_enumerated_absent_on_na_refuses_ANY_value(self, val):
        """Both true AND false: `false` there asserts a bounded walk of something that is not a
        listing, as meaningless as `true`. Half-enforcing the absent state leaves the meaningless
        value legal."""
        reg = _registry()
        next(s for s in reg["sources"] if s["id"] == "n8n-nodes")["complete_listing"] = "n/a"
        for value in (True, False):
            d = _search()
            for c in d["coverage"]:
                if c["source_id"] == "n8n-nodes":
                    c["enumerated"] = value
            r = {ln.split(":", 1)[0].removeprefix("FAIL ").strip() for ln in val.validate_search(d, reg, _map())}
            assert "enumerated-absent-on-na" in r, value

    def test_enumerated_zero_is_a_claim_refuses_true_on_a_BOUNDED_row(self, val):
        d = _search()
        c = next(c for c in d["coverage"] if c["source_id"] == "zapier-apps-sitemap")
        c["enumerated"] = True
        assert "enumerated-zero-is-a-claim" in _s_rules(val, d)

    def test_enumerated_zero_is_a_claim_fires_WHATEVER_returned_is(self, val):
        """The claim is about the WALK, not the count."""
        for returned in (0, 40):
            d = _search()
            c = next(c for c in d["coverage"] if c["source_id"] == "zapier-apps-sitemap")
            c["enumerated"] = True
            c["returned"] = returned
            if returned == 0:
                c["kept"] = 0
                key = f"{c['group_id']}/{c['source_id']}"
                d["candidates"] = [x for x in d["candidates"] if x["found_by"] != key]
                d["unadmitted"] = [x for x in d["unadmitted"] if x["found_by"] != key]
            assert "enumerated-zero-is-a-claim" in _s_rules(val, d), returned


class TestAuthorityBandIsARegistryRuleNotAJoin:
    def test_a_candidate_found_in_a_CATALOG_may_carry_first_party_authority(self, val):
        """The join an earlier design would have made refuses exactly this type's primary evidence
        pattern: discovered in a connector catalog, corroborated at the vendor's own page."""
        d = _search()
        c = next(x for x in d["candidates"] if x["source_authority"] == "first-party")
        assert c["found_by"].split("/")[1] == "nango-providers"
        assert c["locator"].startswith("https://"), c["locator"]
        assert val.validate_search(d, _registry(), _map()) == []


# ---------------------------------------------------------------------------------------------
# C2g — CLI reachability and the exported constant
# ---------------------------------------------------------------------------------------------


class TestCliReachability:
    """Tested THROUGH main(), not by calling the functions directly."""

    def test_both_subcommands_are_reachable_from_main(self, val):
        assert val.main(["keyword-map", str(FIXTURES / "integration-vocabulary-map.valid.yaml")]) == 0
        assert (
            val.main([
                "search", str(FIXTURES / "search-output.valid.yaml"),
                "--keyword-map", str(FIXTURES / "integration-vocabulary-map.valid.yaml"),
            ])
            == 0
        )

    def test_a_finding_returns_1_through_main(self, val, tmp_path, capsys):
        d = _map()
        d["probe"]["note"] = "   "
        p = tmp_path / "m.yaml"
        p.write_text(yaml.safe_dump(d))
        assert val.main(["keyword-map", str(p)]) == 1
        assert "probe-record" in capsys.readouterr().out


class TestTheExportedConstantRUNS:
    """EC9a's second half. The shared root guard SKIPS silently unless the validator exists AND
    exports REQUIRED_CAPABILITY_FIELDS -- and a skip reads exactly like a pass."""

    def test_the_constant_is_exported(self, val):
        assert isinstance(val.REQUIRED_CAPABILITY_FIELDS, tuple)
        assert val.REQUIRED_CAPABILITY_FIELDS

    def test_the_root_guards_constant_check_does_NOT_skip_for_this_package(self):
        from trigger_integrity import load_field_specs

        derived = {p for p, s in load_field_specs().items() if s.required and not p.startswith("prior_art_triggers.")}
        mod = _load_validator()
        assert derived <= set(mod.REQUIRED_CAPABILITY_FIELDS), sorted(derived - set(mod.REQUIRED_CAPABILITY_FIELDS))


# ---------------------------------------------------------------------------------------------
# C2h — the mirror sweep, and no unreachable code
# ---------------------------------------------------------------------------------------------

import ast  # noqa: E402
import re as _re  # noqa: E402

_SRC = SCRIPT.read_text(encoding="utf-8")
_TESTS = pathlib.Path(__file__).read_text(encoding="utf-8")

#: Every rule id the validator can emit, DERIVED from the source rather than transcribed.
SHIPPED_RULES = frozenset(_re.findall(r'_fail\(\s*"([a-z][a-z0-9-]+)"', _SRC))

#: EC2's `need`: every rule with a VALUE-LEVEL boundary the clean fixture's values sit AWAY from.
#: Hand-argued and PARTITIONED against NOT_NEEDED -- three stated criteria failed to derive it, so
#: the build asserts the partition instead of a predicate and a rule added later cannot inherit a
#: side.
NEED = frozenset({
    "host-id-grammar", "nodomain-id-grammar", "id-class-matches-id", "oas-auth-vocabulary",
    "oauth-flow-needs-oauth2", "http-scheme-needs-http", "http-scheme-vocabulary",
    "authority-band-known", "enumerated-required", "enumerated-zero-is-a-claim",
    "enumerated-absent-on-na", "yields-declared", "complete-listing-declared",
    "applicability-angle-unknown", "present-on-source-known", "present-on-needs-reached-cell",
    "present-on-found-by-included", "seed-input-not-widening", "cell-source-known",
    "cell-group-known", "cell-in-applicable-set", "angle-unknown", "fallback-unresolvable",
    "fallback-used-unknown", "fallback-used-shape", "cell-source-excluded", "row-cell-unknown",
    "cap-matches-registry", "cap-respected", "kept-exceeds-returned", "expansion-floor",
    "expansion-cap", "count-frame-required", "negative-terms-required", "status-needs-cause",
    "candidate-group-known", "always-on-angle-holds", "cell-sanitization-cause",
    "sanitization-cause", "probe-record", "source-unaccounted", "probe-method-shape",
    "fallback-cycle", "locator-resolvable", "skipped-source-still-carried",
    "ordering-matches-registry", "kept-matches-rows", "skipped-source-cause",
    "terminal-needs-rationale", "fallback-declared", "forbidden-source-not-active",
    "rows-cite-an-unreached-cell", "outcome-block-required", "unrun-angle-has-cells",
    "unrun-angle-has-candidates", "vacated-not-empty", "ran-requires-coverage",
    "ran-attempted-nothing", "coverage-unreached-has-count", "present-on-a1-only",
    "found-by-precedence", "group-term-unqueried", "cell-source-skipped",
})

#: The complement, each with its reason. The clean fixture already sits ON the boundary of these,
#: which is exactly why they need no narrow mirror.
NOT_NEEDED = {
    "registry-unreadable": "an input-class fault: the document could not be read at all",
    "dependency-missing": "an input-class fault: the package, not the artifact",
    "input": "an input-class fault: the file could not be read",
    "keyword-map-invalid": "an input-class fault: the caller's map",
    "schema": "the schema owns it, and it runs first with an early return",
    "schema-unavailable": "a PACKAGE fault: the schema file did not load at all, which the artifact's author cannot repair. Exit 2, unlike `schema`",
    "group-id-unique": "uniqueness over a populated set; the clean fixture exercises it",
    "candidate-id-unique": "uniqueness over a populated set",
    "cell-pair-unique": "uniqueness over a populated set",
    "term-sited-once": "uniqueness over a populated set",
    "angle-verdict-complete": "completeness over the owed set; the clean map exercises it",
    "angle-verdict-unique": "uniqueness over a populated set",
    "group-type-accounted": "completeness over the axis set; the clean map exercises it",
    "coverage-complete": "completeness over the owed grid; the clean fixture exercises it",
    "reached-needs-counts": "presence on a state the clean fixture is already in",
    "bound-required": "presence on a state the clean fixture is already in",
    "summary-required": "presence on a state the clean fixture is already in",
    "summary-reconciles": "a reconciliation a clean summary performs by construction",
    "bound-hit-consistent": "a combination EC3a's product matrix validates directly",
    "bound-hit-needs-note": "covered by EC3a's (capped x truncated) combination, which validates a hit:true artifact carrying a dropped_note clean -- the mirror a NEED member would add",
    "ordering-deviation-contradicts": "a contradiction the clean fixture cannot express",
    "degraded-source-recorded": "derived from the finished coverage list",
}


class TestTheMirrorSweep:
    """The newest sibling's THREE assertions, not the older pair. `regulatory` replaced the `ml`
    sweep after finding that its `mirrored` credited a whole test class off one `== []`, which made
    `negatives - mirrored` empty by construction and the guard unable to fail."""

    #: Emitted by the SHARED trigger engine, not by this validator. Asserted here because C1a
    #: proves the engine refuses a tautological angle, and that assertion reads identically to a
    #: negative for a rule of our own.
    SHARED_ENGINE_RULES = frozenset({"angle-always-fires", "registry-out-of-scope"})

    #: Matches an assertion against a RULE SET, inline or pre-computed, and nothing else. Two
    #: earlier versions were wrong in opposite directions: the first required an inline
    #: `_s_rules(...)` call and could not see a mirror asserted against a variable -- a sweep
    #: reporting green off its own blind spot; the second matched any `assert "x" in ...` and
    #: swept up ordinary membership assertions like `assert "nango-providers" in c["present_on"]`.
    _RULE_ASSERT = r'assert "([a-z][a-z0-9-]+)" {neg}in (?:_s_rules|_map_rules|_reg_rules|_rules|r\b|rules\b)'

    @classmethod
    def _negatives(cls) -> set[str]:
        return set(_re.findall(cls._RULE_ASSERT.format(neg=""), _TESTS)) - cls.SHARED_ENGINE_RULES

    @classmethod
    def _mirrored(cls) -> set[str]:
        return set(_re.findall(cls._RULE_ASSERT.format(neg="not "), _TESTS)) - cls.SHARED_ENGINE_RULES

    def test_every_NEGATIVE_names_a_rule_the_validator_emits(self):
        assert self._negatives() <= SHIPPED_RULES, sorted(self._negatives() - SHIPPED_RULES)

    def test_every_MIRROR_names_a_rule_the_validator_emits(self):
        assert self._mirrored() <= SHIPPED_RULES, sorted(self._mirrored() - SHIPPED_RULES)

    def test_every_NEED_rule_carries_an_explicit_NARROW_mirror(self):
        missing = NEED - self._mirrored()
        assert not missing, f"NEED rules with no narrow mirror: {sorted(missing)}"

    def test_NEED_and_NOT_NEEDED_PARTITION_every_shipped_rule(self):
        """The no-fourth-case discipline. A rule added later cannot inherit a side: someone has to
        put it in one and say why."""
        both = NEED & set(NOT_NEEDED)
        assert not both, f"in both halves: {sorted(both)}"
        union = NEED | set(NOT_NEEDED)
        assert union == SHIPPED_RULES, {
            "shipped but in neither half": sorted(SHIPPED_RULES - union),
            "claimed but never emitted": sorted(union - SHIPPED_RULES),
        }

    def test_every_NOT_NEEDED_member_states_a_reason(self):
        assert all(str(v).strip() for v in NOT_NEEDED.values())


class TestNoUnreachableCode:
    def test_no_rule_sits_below_an_early_return(self):
        """A rule under an unconditional return is a rule that never fires. This walks the AST of
        every function and flags a `_fail` that follows a top-level `return` in the same block."""
        tree = ast.parse(_SRC)
        offenders: list[str] = []
        for fn in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
            seen_return = False
            for stmt in fn.body:
                if seen_return:
                    for sub in ast.walk(stmt):
                        if isinstance(sub, ast.Call) and getattr(sub.func, "id", "") == "_fail":
                            offenders.append(f"{fn.name}:{sub.lineno}")
                if isinstance(stmt, ast.Return):
                    seen_return = True
        assert not offenders, offenders

    def test_every_shipped_rule_is_reachable_by_SOME_test(self):
        """A rule nothing exercises is a rule nobody knows works.

        The NEED frozenset and the NOT_NEEDED dict list every shipped rule as a literal, and the
        partition test guarantees they do -- so scraping the whole file credited five rules as
        "exercised" purely by their own membership entry. Those two blocks are cut out first.
        """
        # Cut the three MEMBERSHIP literals only, each by its own opening and its own closing
        # line, so nothing else is swallowed. An earlier version cut to the next "\n}" from a
        # marker that also appears in a test body, and removed most of the file -- a guard that
        # over-cuts fails loudly, which is the safe direction, but it is still wrong.
        body = _TESTS
        for opener, closer in (("NEED = frozenset({", "\n})\n"),
                               ("NOT_NEEDED = {", "\n}\n"),
                               ("UNREADABLE = frozenset({", "\n})\n")):
            start = body.find(opener)
            if start == -1:
                continue
            end = body.find(closer, start)
            assert end != -1, opener
            body = body[:start] + body[end + len(closer):]
        assert "def test_" in body and len(body) > len(_TESTS) * 0.5, "the cut removed too much"
        # Both forms a test names a rule in: the bare id, and inside a `FAIL <id>:` prefix match.
        exercised = (set(_re.findall(r'"([a-z][a-z0-9-]+)"', body))
                     | set(_re.findall(r'FAIL ([a-z][a-z0-9-]+):', body)))
        dead = SHIPPED_RULES - exercised
        assert not dead, f"emitted but named by no test outside the membership blocks: {sorted(dead)}"


class TestTheNarrowMirrorsTheSweepDemands:
    """One NARROW mirror per NEED rule: the rule is SILENT on the nearest legal value. A clean
    fixture sitting far from a boundary cannot exercise it, which is the whole reason EC2 asks."""

    # ---- map-side -----------------------------------------------------------------------
    def test_probe_record_silent_on_a_stated_note(self, val):
        d = _map()
        d["probe"]["note"] = "three requests, all reached"
        assert "probe-record" not in _map_rules(val, d)

    def test_expansion_cap_silent_at_the_cap(self, val):
        d = _map()
        g = d["groups"][0]
        g["expansion_cap"] = len(g["expansions"])
        assert "expansion-cap" not in _map_rules(val, d)

    def test_always_on_angle_holds_silent_on_a_CONDITIONAL_false(self, val):
        d = _map()
        assert not next(v for v in d["angle_applicability"] if v["angle_id"] == "b5")["holds"]
        assert "always-on-angle-holds" not in _map_rules(val, d)

    def test_applicability_angle_unknown_silent_on_a_declared_angle(self, val):
        assert "applicability-angle-unknown" not in _map_rules(val, _map())

    def test_source_unaccounted_silent_on_a_complete_partition(self, val):
        assert "source-unaccounted" not in _map_rules(val, _map())

    def test_skipped_source_cause_silent_on_a_stated_cause(self, val):
        assert "skipped-source-cause" not in _map_rules(val, _map())

    def test_forbidden_source_not_active_silent_when_no_excluded_row_is_active(self, val):
        assert "forbidden-source-not-active" not in _map_rules(val, _map())

    # ---- coverage-side ------------------------------------------------------------------
    def test_angle_unknown_silent_on_a_declared_angle(self, val):
        assert "angle-unknown" not in _s_rules(val, _search())

    def test_cell_group_known_silent_on_a_declared_group(self, val):
        assert "cell-group-known" not in _s_rules(val, _search())

    def test_cell_source_known_silent_on_a_registry_row(self, val):
        assert "cell-source-known" not in _s_rules(val, _search())

    def test_cell_source_excluded_silent_on_a_non_excluded_row(self, val):
        assert "cell-source-excluded" not in _s_rules(val, _search())

    def test_cell_in_applicable_set_silent_on_the_angles_own_source(self, val):
        assert "cell-in-applicable-set" not in _s_rules(val, _search())

    def test_status_needs_cause_silent_on_reached(self, val):
        assert "status-needs-cause" not in _s_rules(val, _search())

    def test_cell_sanitization_cause_silent_on_clean(self, val):
        assert "cell-sanitization-cause" not in _s_rules(val, _search())

    def test_fallback_used_shape_silent_on_null(self, val):
        assert "fallback-used-shape" not in _s_rules(val, _search())

    def test_fallback_used_unknown_silent_on_a_real_row(self, val):
        d = _search()
        d["coverage"][0]["fallback_used"] = "angle:nango-providers"
        assert "fallback-used-unknown" not in _s_rules(val, d)

    def test_row_cell_unknown_silent_on_a_recorded_cell(self, val):
        assert "row-cell-unknown" not in _s_rules(val, _search())

    def test_rows_cite_an_unreached_cell_silent_when_the_cell_reached(self, val):
        assert "rows-cite-an-unreached-cell" not in _s_rules(val, _search())

    def test_kept_exceeds_returned_silent_when_kept_is_below_returned(self, val):
        assert "kept-exceeds-returned" not in _s_rules(val, _search())

    def test_kept_matches_rows_silent_when_it_reconciles(self, val):
        assert "kept-matches-rows" not in _s_rules(val, _search())

    def test_cap_matches_registry_silent_on_the_transcribed_cap(self, val):
        assert "cap-matches-registry" not in _s_rules(val, _search())

    def test_cap_respected_silent_below_the_cap(self, val):
        assert "cap-respected" not in _s_rules(val, _search())

    def test_candidate_group_known_silent_on_a_declared_group(self, val):
        assert "candidate-group-known" not in _s_rules(val, _search())

    # ---- this type's own ----------------------------------------------------------------
    def test_id_class_matches_id_silent_when_they_agree(self, val):
        assert "id-class-matches-id" not in _s_rules(val, _search())

    def test_oauth_flow_needs_oauth2_silent_on_an_oauth2_scheme(self, val):
        assert "oauth-flow-needs-oauth2" not in _s_rules(val, _search())

    def test_http_scheme_needs_http_silent_on_an_http_scheme(self, val):
        assert "http-scheme-needs-http" not in _s_rules(val, _search())

    def test_enumerated_required_silent_when_stated(self, val):
        assert "enumerated-required" not in _s_rules(val, _search())

    def test_enumerated_zero_is_a_claim_silent_on_false_over_a_bounded_row(self, val):
        d = _search()
        c = next(c for c in d["coverage"] if c["source_id"] == "zapier-apps-sitemap")
        assert c["enumerated"] is False
        assert "enumerated-zero-is-a-claim" not in _s_rules(val, d)

    def test_enumerated_absent_on_na_silent_when_no_row_is_na(self, val):
        """Weak by construction -- the clean a1 corpus contains no `n/a` row, so this proves only
        that the rule does not fire at random. The real mirror is in TestEnumerated, against a
        fixture where the absent state is actually reachable."""
        assert "enumerated-absent-on-na" not in _s_rules(val, _search())

    def test_present_on_rules_silent_on_the_clean_a1_artifact(self, val):
        r = _s_rules(val, _search())
        assert "present-on-a1-only" not in r
        assert "present-on-source-known" not in r
        assert "present-on-needs-reached-cell" not in r
        assert "present-on-found-by-included" not in r

    # ---- the OUTCOME family: the clean fixture is `ran`, so it sits AWAY from all of these --
    @staticmethod
    def _not_run() -> dict:
        d = _search()
        d["outcome"] = "not_run"
        d["not_run"] = {"map_verdict": "b5 does not hold: ml_involvement is none"}
        d["coverage"] = []
        d["candidates"] = []
        d["unadmitted"] = []
        d.pop("bound", None)
        d.pop("retrieval_summary", None)
        return d

    @staticmethod
    def _vacated() -> dict:
        d = _search()
        d["outcome"] = "vacated"
        d["vacated"] = {"cause": "every catalog refused on this run"}
        d["candidates"] = []
        d["unadmitted"] = []
        d.pop("bound", None)
        for c in d["coverage"]:
            c["status"] = "unreachable"
            c["returned"] = 0
            c["kept"] = 0
            c["cause"] = "503 from the catalog"
            c.pop("enumerated", None)
        d["retrieval_summary"] = {
            "status_counts": {"unreachable": len(d["coverage"])},
            "degraded_sources": [
                {"source_id": s, "status": "unreachable", "note": None}
                for s in sorted({c["source_id"] for c in d["coverage"]})
            ],
        }
        return d

    def test_a_LEGAL_not_run_artifact_validates_clean(self, val):
        assert val.validate_search(self._not_run(), _registry(), _map()) == []

    def test_a_LEGAL_vacated_artifact_validates_clean(self, val):
        assert val.validate_search(self._vacated(), _registry(), _map()) == []

    def test_outcome_block_required_silent_when_the_block_is_there(self, val):
        assert "outcome-block-required" not in _s_rules(val, self._not_run())
        assert "outcome-block-required" not in _s_rules(val, self._vacated())

    def test_unrun_angle_rules_silent_on_a_legal_not_run(self, val):
        r = _s_rules(val, self._not_run())
        assert "unrun-angle-has-cells" not in r
        assert "unrun-angle-has-candidates" not in r

    def test_vacated_not_empty_silent_on_a_legal_vacated(self, val):
        assert "vacated-not-empty" not in _s_rules(val, self._vacated())

    def test_ran_rules_silent_on_the_clean_ran_artifact(self, val):
        r = _s_rules(val, _search())
        assert "ran-requires-coverage" not in r
        assert "ran-attempted-nothing" not in r

    def test_coverage_unreached_has_count_silent_on_a_zero_returned(self, val):
        assert "coverage-unreached-has-count" not in _s_rules(val, self._vacated())


# ---------------------------------------------------------------------------------------------
# C3 / C6 — the angle references, and the prose-vs-registry guards in BOTH directions
# ---------------------------------------------------------------------------------------------

ANGLE_DIR = PKG / "references" / "angles"


def _angle_docs() -> dict[str, str]:
    return {p.stem: p.read_text(encoding="utf-8") for p in sorted(ANGLE_DIR.glob("*.md"))}


class TestAngleReferences:
    def test_one_file_per_registry_angle_and_no_others(self):
        assert set(_angle_docs()) == {a["id"] for a in _registry()["angles"]}

    def test_each_states_its_cap_ordering_sources_and_axes_EXACTLY_as_the_registry_does(self):
        """C6, the angle->registry direction."""
        docs = _angle_docs()
        for a in _registry()["angles"]:
            d = docs[a["id"]]
            assert f"**Cap: `{a['cap']}`.**" in d, a["id"]
            assert a["ordering_signal"] in d, a["id"]
            for s in a["sources"]:
                assert f"`{s}`" in d, (a["id"], s)
            for t in a["applicable_group_types"]:
                assert f"**`{t}`**" in d, (a["id"], t)
            assert f"**Fallback: `{a['fallback']}`.**" in d, a["id"]

    def test_no_angle_doc_names_a_source_the_registry_LACKS(self):
        """The registry->prose direction. Running only the other one is how #34's defect ships."""
        rows = {s["id"] for s in _registry()["sources"]}
        known = rows | {a["id"] for a in _registry()["angles"]}
        for aid, d in _angle_docs().items():
            for tok in _re.findall(r"`([a-z][a-z0-9-]{4,})`", d):
                if tok in known or "." in tok or tok in {
                    "present_on", "found_by", "complete_listing", "bound", "ordering",
                    "ordering_deviation", "outcome", "vacated", "not_run", "holds",
                    "additionalProperties", "integration_pattern", "category", "capability",
                    "service", "pattern", "domain-noun", "seed-product", "always-on-angle-holds",
                    "candidates", "protocol",
                }:
                    continue
                assert not tok.endswith("-providers"), (aid, tok)

    def test_every_registry_SOURCE_is_reached_by_at_least_one_angle_doc(self):
        """An orphan source cannot ship unused. Spec §2.1 requires every one of the 23 rows to land
        in active[] or skipped[], so a row no angle carries has no way to be either."""
        rows = {s["id"] for s in _registry()["sources"]}
        carried = {s for a in _registry()["angles"] for s in a["sources"]}
        assert rows - carried == set(), f"registry rows no angle carries: {sorted(rows - carried)}"

    def test_each_states_the_no_sibling_dependency_resolution_IN_ITS_OWN_WORDS(self):
        for aid, d in _angle_docs().items():
            assert "## No sibling dependency" in d, aid
            assert "DISCOVERS from wave 0" in d, aid

    def test_no_angle_doc_cites_a_LETTERED_LOCK_as_authority(self):
        """A lettered lock is not a definition: citing L-7 tells a reader nothing they can check."""
        for aid, d in _angle_docs().items():
            assert not _re.search(r"\bL-\d+\b", d), aid

    def test_a1_and_a2_state_their_required_subtopics_and_b3_states_data_residency(self):
        docs = _angle_docs()
        assert "integration CATEGORIES" in docs["a1"]
        assert "integration PATTERNS" in docs["a2"]
        assert "DATA-RESIDENCY" in docs["b3"]

    def test_b2_records_the_webhook_surface_as_a_WIDENER_not_a_fold(self):
        """§6.1's fourth coverage, which is not a fold at all. Dropping it is the deferral §20
        names, and no other task owns it."""
        d = _angle_docs()["b2"]
        assert "predicate_omits" in d
        assert "WIDENER" in d
        assert "a widener is not a fold" in d

    def test_every_ALWAYS_ON_doc_says_it_cannot_fail_to_hold(self):
        for aid in ("a1", "a2", "a3"):
            assert "ALWAYS-ON" in _angle_docs()[aid], aid

    def test_every_CONDITIONAL_doc_states_its_precondition_in_BOTH_directions(self):
        docs = _angle_docs()
        for a in _registry()["angles"]:
            if a["trigger"] != "conditional":
                continue
            d = docs[a["id"]]
            assert "**It holds when:**" in d, a["id"]
            assert "**It does NOT hold when**" in d, a["id"]


# ---------------------------------------------------------------------------------------------
# C5 — the producer SKILL.md
# ---------------------------------------------------------------------------------------------

SKILL = PKG / "SKILL.md"


def _skill() -> str:
    return SKILL.read_text(encoding="utf-8")


class TestProducerSkill:
    def test_both_procedures_are_numbered_with_no_duplicate_step_number(self):
        nums = [int(n) for n in _re.findall(r"^(\d+)\. ", _skill(), _re.M)]
        assert nums == sorted(nums)
        assert len(nums) == len(set(nums)), "duplicate step number"
        assert nums[0] == 1 and nums[-1] == len(nums)

    def test_every_field_the_schemas_REQUIRE_is_instructed_by_a_step(self):
        text = _skill()
        for name in ("integration-vocabulary-map", "search-output"):
            sch = json.loads((SCHEMAS / f"{name}.schema.json").read_text())
            for f in sch.get("required", []):
                assert f in text, (name, f)

    def test_the_artifact_FILENAMES_are_stated(self):
        t = _skill()
        assert "integration-vocabulary-map.yaml" in t
        assert "search-output-<angle_id>.yaml" in t

    def test_the_STANDING_security_finding_is_carried_with_posture_not_count(self):
        """§9. A count goes stale the moment the corpus moves and invites a reader to treat a
        smaller number as an improvement."""
        t = _skill()
        assert "STANDING security finding" in t
        assert "POSTURE, never a count" in t

    def test_the_producer_is_SELF_SUFFICIENT(self):
        """A suite test, not a one-off grep. Three shipped producers carry the first phrasing and
        spec §4 forbids it (#58); the POSITIVE assertion is made too, because a pair of negatives is
        satisfied by a SKILL.md that never mentions the boundary at all."""
        t = _skill()
        assert "the conditions win" not in t
        assert "single source of the quality bar" not in t
        assert "This skill states every duty itself" in t

    def test_the_frontmatter_description_fits_the_1024_char_cap(self):
        """A platform hard limit that fails at INSTALL, not at review."""
        m = _re.search(r"^description: >\n((?:  .*\n)+)", _skill(), _re.M)
        assert m, "no folded description"
        desc = " ".join(line.strip() for line in m.group(1).splitlines())
        assert len(desc) <= 1024, len(desc)

    def test_the_frontmatter_carries_the_five_extension_targets(self):
        t = _skill()
        for ext in ("claude", "codex", "copilot", "cursor", "gemini"):
            assert f"  {ext}: {{}}" in t, ext

    def test_every_reference_file_the_skill_names_EXISTS(self):
        """A skill pointing at a file that is not there is a skill that cannot be followed."""
        for rel in _re.findall(r"`(references/[^`]+)`", _skill()):
            if "{" in rel or "<" in rel:
                continue
            assert (PKG / rel).exists(), rel

    def test_the_admission_test_states_BOTH_conjuncts_and_the_carve_out(self):
        t = _skill()
        assert "BOTH conjuncts" in t
        assert "does NOT test whether a public API exists" in t


# ---------------------------------------------------------------------------------------------
# C7 / C7a / C7b / C7c — the reviewing twin, and the guards over the pair
# ---------------------------------------------------------------------------------------------

REVIEWER = PKG.parent / "reviewing-integrations-prior-art-survey"


def _conditions() -> str:
    return (REVIEWER / "references" / "conditions.md").read_text(encoding="utf-8")


class TestReviewingTwin:
    def test_the_package_ships_its_four_parts(self):
        for rel in ("SKILL.md", "references/conditions.md", "references/sources.md",
                    "references/fixtures/README.md"):
            assert (REVIEWER / rel).exists(), rel

    def test_the_evidence_table_carries_all_EIGHT_sources(self):
        t = (REVIEWER / "SKILL.md").read_text(encoding="utf-8")
        assert "**EIGHT sources," in t
        for s in ("the artifact under review", "the vocabulary map", "SCOPE and CLASSIFICATION",
                  "schemas/*.json", "source-registry.yaml", "angles/<angle>.md",
                  # the two C9 and C13 cannot be discharged without
                  "absent-input-policy.md", "category-vocabulary.md"):
            assert s in t, s

    def test_the_three_PRODUCER_package_paths_are_QUALIFIED_and_RESOLVE(self):
        """Three of the six sources are files the producer ships, not this package. Written bare
        they read as paths in the reviewing package, where they do not exist -- and a reviewer
        cannot open what it cannot find."""
        t = (REVIEWER / "SKILL.md").read_text(encoding="utf-8")
        for rel in ("integrations-prior-art-survey/schemas/*.json",
                    "integrations-prior-art-survey/references/source-registry.yaml",
                    "integrations-prior-art-survey/references/angles/<angle>.md"):
            assert rel in t, rel
        assert (PKG / "schemas").is_dir()
        assert (PKG / "references/source-registry.yaml").exists()
        assert (PKG / "references/angles/a1.md").exists()

    def test_the_seeded_category_vocabulary_SHIPS(self):
        """Four sites judged against it and none shipped it: a list required by four readers and
        written for none is a check nobody can run."""
        f = PKG / "references" / "category-vocabulary.md"
        assert f.exists()
        t = f.read_text(encoding="utf-8")
        assert "payments" in t and "payment" in t
        # The tie-break, asserted in the direction BOTH specs decide: the join with the capability
        # map is what `category` exists for, so the upstream spelling is what gets recorded. An
        # earlier version of this assertion pinned the wrong half and made the error durable.
        assert "the UPSTREAM spelling wins" in t
        assert "identity" in t and "data_providers" in t   # transcribed, not invented
        assert "ats" in t and "mcp" in t and "iam" in t    # the three the measurement names
        assert "integrations-prior-art-survey/references/category-vocabulary.md" in _conditions()

    def test_the_verdict_grammar_emits_exactly_one_approve_or_revise(self):
        t = (REVIEWER / "SKILL.md").read_text(encoding="utf-8")
        assert t.count("VERDICT: approve") == 1
        assert t.count("VERDICT: revise") == 1

    def test_the_reviewers_description_fits_the_1024_char_cap(self):
        m = _re.search(r"^description: >\n((?:  .*\n)+)", (REVIEWER / "SKILL.md").read_text(), _re.M)
        assert m
        assert len(" ".join(x.strip() for x in m.group(1).splitlines())) <= 1024

    def test_conditions_cover_every_area_spec_10_names(self):
        c = _conditions()
        for area in ("canonical terms", "six-axis coverage", "verbatim", "enumerated",
                     "OBSERVABLE", "four-band authority", "vendor-host", "OAS and IANA vocabularies",
                     "claim-versus-quote", "admission test", "capability coverage",
                     "present_on", "sanitization", "PROPORTIONATE"):
            assert area in c, area

    def test_the_two_conditions_the_producer_DELEGATES_by_name_are_present(self):
        """§2.3 delegates the two-conjunct admission test and §2.1 the capability-coverage second
        pass. An earlier design delegated both and listed neither."""
        c = _conditions()
        assert "two-conjunct admission test" in c
        assert "second pass" in c

    def test_the_carve_out_is_stated_where_the_admission_condition_is(self):
        assert "does NOT test whether a public API exists" in _conditions()


class TestC7aTheConditionsHalfOfTheMechanicalGuards:
    def test_every_rule_id_a_condition_names_is_one_the_validator_EMITS(self):
        named = set(_re.findall(r"`([a-z][a-z0-9-]+)`", _conditions()))
        cited = {n for n in named if "-" in n and n in SHIPPED_RULES}
        phantom = {n for n in named if n.count("-") >= 2 and n not in SHIPPED_RULES
                   and n not in {"first-party", "connector-catalog", "search-result",
                                 "no-first-party-home", "no-retrievable-corpus-row",
                                 "duplicate-of", "keyword-map", "source-registry.yaml",
                                 "integration-vocabulary-map", "search-output", "capability-map.yaml"}}
        assert not phantom, f"conditions cite rule ids the validator does not emit: {sorted(phantom)}"
        assert len(cited) >= 15, f"only {len(cited)} rules disclaimed; the conditions should name what they do NOT own"

    def test_no_condition_names_as_its_own_gap_something_the_validator_ALREADY_refuses(self):
        """A condition claiming to own what a rule enforces costs the author a cycle on noise."""
        # Split on the shipped `**C<n> — ...**` heading, which is what the shared count guard
        # reads. An earlier version split on `## ` and, after the headings changed format, treated
        # the whole file as ONE block -- a guard that stops partitioning stops checking.
        c = _conditions()
        blocks = _re.split(r"\n\*\*C\d+ — ", c)
        assert len(blocks) >= 18, f"the condition splitter found {len(blocks) - 1} blocks"
        for block in blocks:
            if "*No rule owns this" in block or "no rule owns it" in block.lower():
                ids = {n for n in _re.findall(r"`([a-z][a-z0-9-]+)`", block) if n in SHIPPED_RULES}
                assert not ids, f"a 'no rule owns this' block cites shipped rules: {sorted(ids)}"


class TestC7bEveryJudgedFieldCarriesADescription:
    def test_every_field_a_condition_names_as_evidence_carries_a_schema_description(self):
        schemas = {
            n: json.loads((SCHEMAS / f"{n}.schema.json").read_text())
            for n in ("integration-vocabulary-map", "search-output")
        }

        def described(node, name):
            if isinstance(node, dict):
                props = node.get("properties") or {}
                if name in props and str(props[name].get("description") or "").strip():
                    return True
                return any(described(v, name) for v in node.values() if isinstance(v, (dict, list)))
            if isinstance(node, list):
                return any(described(v, name) for v in node)
            return False

        judged = {"source_authority", "category", "homepage", "evidence_quote", "claim",
                  "present_on", "enumerated", "fallback_used", "count_frame", "kept",
                  "auth_scheme", "oauth_flow", "http_scheme", "classification"}
        for f in sorted(judged):
            assert any(described(s, f) for s in schemas.values()), f


class TestC7cThePortabilityGuard:
    """EC6. Its file list is GLOB-DERIVED with a count floor, and it states what it does not glob --
    a hand-listed population is how #58's defect ships."""

    FORBIDDEN = ("/home/", "C:\\", "~/", "localhost:", "127.0.0.1", "/Users/", "/tmp/")
    ALLOW = ("references/", "schemas/", "scripts/")

    #: The ONE file excluded, and why: this module declares the forbidden tokens as DATA in
    #: FORBIDDEN above, so globbing it makes the guard fail on its own definition. It is also not
    #: something an agent reads as guidance. The exclusion is asserted to be exactly this file, so
    #: it cannot quietly grow into an escape hatch.
    EXCLUDED = ("test_validate_integrations_prior_art.py",)

    def _corpus(self) -> list[pathlib.Path]:
        files = [
            p for p in list(PKG.rglob("*.md")) + list(PKG.rglob("*.yaml"))
            + list(PKG.rglob("*.json")) + list(PKG.rglob("*.py"))
            + list(REVIEWER.rglob("*.md")) + list(REVIEWER.rglob("*.yaml"))
            if p.name not in self.EXCLUDED
        ]
        return sorted(files)

    def test_the_exclusion_is_exactly_ONE_named_file(self):
        assert self.EXCLUDED == ("test_validate_integrations_prior_art.py",)
        assert not [p for p in self._corpus() if p.name in self.EXCLUDED]

    def test_the_globbed_population_meets_its_FLOOR(self):
        """It does NOT glob: anything outside these two packages, and any non-text asset. A guard
        whose population silently shrinks to nothing reports green."""
        files = self._corpus()
        assert len(files) >= 24, f"only {len(files)} files globbed; the population has shrunk"

    def test_no_absolute_or_machine_local_path_appears_in_anything_an_agent_READS(self):
        offenders: list[str] = []
        for p in self._corpus():
            text = p.read_text(encoding="utf-8", errors="replace").lower()
            for bad in self.FORBIDDEN:
                if bad.lower() in text:
                    offenders.append(f"{p.relative_to(PKG.parent)}: {bad}")
        assert not offenders, offenders

    def test_the_allowlist_is_proven_in_BOTH_directions(self):
        """A path an agent must follow resolves package-relative, and the allowlist is not empty."""
        assert self.ALLOW
        for rel in self.ALLOW:
            assert (PKG / rel).exists(), rel


class TestTheReviewersFixturesAreByteIdentical:
    """Two shipped packages guard exactly this drift: the fixture's reading is the one that
    propagates, and a drifted copy calibrates the reviewer against an artifact the gate refuses."""

    def test_byte_identical_to_the_producers(self):
        for name in ("integration-vocabulary-map.valid.yaml", "search-output.valid.yaml"):
            a = (FIXTURES / name).read_bytes()
            b = (REVIEWER / "references" / "fixtures" / name).read_bytes()
            assert a == b, name

    def test_the_reviewers_copies_still_return_NOTHING_from_the_producers_validator(self, val):
        d = REVIEWER / "references" / "fixtures"
        m = yaml.safe_load((d / "integration-vocabulary-map.valid.yaml").read_text())
        s = yaml.safe_load((d / "search-output.valid.yaml").read_text())
        assert val.validate_keyword_map(m, _registry()) == []
        assert val.validate_search(s, _registry(), m) == []

    def test_NO_planted_fixture_is_copied_into_the_reviewer(self):
        """A reviewer that has seen the answer key is not a blind reviewer."""
        assert not list((REVIEWER / "references" / "fixtures").glob("**/planted*"))


# ---------------------------------------------------------------------------------------------
# C6 — schema-vs-prose and prose-vs-registry
# ---------------------------------------------------------------------------------------------

PROSE = sorted(
    [p for p in PKG.rglob("*.md") if "fixtures" not in p.parts]
    + [p for p in REVIEWER.rglob("*.md") if "fixtures" not in p.parts]
)


def _prose_text() -> str:
    """Fenced code blocks STRIPPED: a field shown only in an example is not instructed."""
    out = []
    for p in PROSE:
        out.append(_re.sub(r"```.*?```", "", p.read_text(encoding="utf-8"), flags=_re.S))
    return "\n".join(out)


def _schema_vocabulary() -> set[str]:
    """Every field NAME and every enum/const VALUE both schemas admit.

    Prose legitimately names a VALUE as well as a field -- `payments`, `reached`, `conditional`.
    An earlier version listed only property names and had to grow an example-term allowlist one
    failure at a time, which is a guard being widened to fit rather than one being right.
    """
    names: set[str] = set()

    def walk(node):
        if isinstance(node, dict):
            for k, v in (node.get("properties") or {}).items():
                names.add(k)
                walk(v)
            for v in node.get("enum") or []:
                if isinstance(v, str):
                    names.add(v)
            if isinstance(node.get("const"), str):
                names.add(node["const"])
            for key in ("items", "then", "if"):
                if key in node:
                    walk(node[key])
            for key in ("allOf", "anyOf", "oneOf"):
                for sub in node.get(key) or []:
                    walk(sub)
            for sub in (node.get("$defs") or {}).values():
                walk(sub)
        elif isinstance(node, list):
            for sub in node:
                walk(sub)

    for n in ("integration-vocabulary-map", "search-output"):
        walk(json.loads((SCHEMAS / f"{n}.schema.json").read_text()))
    return names


class TestProseVsSchemaAndRegistry:
    def test_no_prose_names_a_FIELD_the_schemas_lack(self):
        known = _schema_vocabulary() | {
            "id", "url", "url_kind", "as_of", "note", "yields", "fallback", "fallback_rationale",
            "probe_method", "authority_band", "complete_listing", "access_status", "status",
            "evidence", "replacement", "cap", "cap_rationale", "ordering_signal", "trigger",
            "precondition", "predicate", "trigger_anchor", "widening_legs", "predicate_omits",
            "seed_input", "mechanism", "sources", "applicable_group_types", "type_trigger",
            "coherence_axioms", "probe_default", "registry_version", "updated", "name",
            "required_subtopics", "excluded", "formula", "source", "method", "headers",
            "user_agent", "servers", "protocol", "auth_mode", "description", "docs",
            # Snake_case VALUES quoted from upstream vocabularies, not fields of ours: the
            # classification keys this type's `category` seed is transcribed from, and the
            # classification leaf that seeds a1/a3.
            "data_providers", "third_party_list", "knowledge_base",
            # Catalog ENTRY NAMES quoted as examples of each row's name shape, not fields.
            "acuity_scheduling", "ez_texting",
        }
        #: Only SNAKE_CASE tokens are treated as field claims. A single backticked English word in
        #: prose is a VALUE, a vocabulary term or an example -- `payments`, `reached`, `approve` --
        #: and an earlier version that checked every token had to grow an allowlist one failure at
        #: a time, which is a guard being widened to fit rather than one being right. A field this
        #: contract could invent and the schemas could lack would be written snake_case.
        text = _prose_text()
        claimed = {t for t in _re.findall(r"`([a-z][a-z0-9_]*)`", text) if "_" in t}
        unknown = claimed - known
        assert not unknown, f"prose names fields no schema or registry carries: {sorted(unknown)}"

    def test_no_prose_names_a_SOURCE_ID_the_registry_lacks(self):
        reg = _registry()
        rows = {s["id"] for s in reg["sources"]} | {e["id"] for e in reg["excluded"]}
        text = _prose_text()
        suspects = {t for t in _re.findall(r"`([a-z][a-z0-9]+(?:-[a-z0-9]+){1,3})`", text)
                    if t.endswith(("-providers", "-pieces", "-nodes", "-components", "-sitemap",
                                   "-guru", "-apis", "-github", "-official", "-network",
                                   "-packages", "-downloads", "-webhooks", "-spec", "-docs",
                                   "-center", "-pages", "-openapi", "-hub", "-api"))}
        assert suspects <= rows, f"prose names source ids the registry lacks: {sorted(suspects - rows)}"


# ---------------------------------------------------------------------------------------------
# C8 — the planted fixtures, and the diff guard
# ---------------------------------------------------------------------------------------------

PLANTED = FIXTURES / "planted"

#: THE ANSWER KEY. It lives here and never beside the fixtures, so a blind reviewer dispatched
#: against them cannot read what it is meant to find.
ANSWER_KEY = {
    "map-01.yaml": "C1 — `canonical` takes the CATALOG's spelling over the upstream one "
                   "(`payment`, which Nango writes on 38 rows and `payments` on none). The term "
                   "searches WELL, which is what makes it shape-legal and wrong: a candidate "
                   "recorded under the catalog's spelling cannot be joined to the capability that "
                   "motivated the survey, which is the whole reason the field exists.",
    "search-01.yaml": "C5 — three catalogs that WERE walked completely are recorded "
                      "`enumerated: false`, so a real absence reads as an unknown. The note even "
                      "explains a different row's bounded traversal, which makes it read as "
                      "deliberate.",
    "search-02.yaml": "C10 — the `claim` exceeds its `evidence_quote`: the quote establishes OAuth "
                      "2.0 and the claim adds webhook push notifications for every event type.",
    "search-03.yaml": "C15 — `bound.hit` is true and the `dropped_note` says nothing a reader "
                      "could re-apply: 'rows below the cap were not recorded' names no ordering "
                      "position and no dropped row.",
}


class TestPlantedFixtures:
    def test_there_are_four_and_the_answer_key_covers_each(self):
        files = {p.name for p in PLANTED.glob("*.yaml")}
        assert files == set(ANSWER_KEY)

    def test_every_planted_fixture_PASSES_the_deterministic_gate(self, val):
        """A planted defect the validator catches tests the VALIDATOR, not the reviewer."""
        m = yaml.safe_load((PLANTED / "map-01.yaml").read_text())
        assert val.validate_keyword_map(m, _registry()) == []
        clean_map = _map()
        for name in ("search-01.yaml", "search-02.yaml", "search-03.yaml"):
            d = yaml.safe_load((PLANTED / name).read_text())
            assert val.validate_search(d, _registry(), clean_map) == [], name

    def test_each_differs_from_the_CLEAN_fixture_only_in_its_plant(self):
        """A fixture that drifted in a second place tests two things and calibrates neither.

        Compared STRUCTURALLY, on leaf paths -- the planted files are re-dumped, so a textual diff
        counts formatting and reports a change everywhere. A guard measuring the serializer is a
        guard measuring nothing.
        """

        def leaves(node, path=()):
            if isinstance(node, dict):
                for k, v in node.items():
                    yield from leaves(v, (*path, k))
            elif isinstance(node, list):
                for i, v in enumerate(node):
                    yield from leaves(v, (*path, i))
            else:
                yield path, node

        def differing(a: dict, b: dict) -> list:
            la, lb = dict(leaves(a)), dict(leaves(b))
            return sorted({k for k in set(la) | set(lb) if la.get(k) != lb.get(k)})

        # Asserted by the KIND of leaf that moved, not by a count: one plant may touch many cells
        # (search-01's does -- three catalogs across five groups is fifteen), and a count alone
        # cannot tell fifteen instances of one defect from fifteen different ones.
        def kinds(a: dict, b: dict) -> set[str]:
            la, lb = dict(leaves(a)), dict(leaves(b))
            return {str(k[-1]) for k in set(la) | set(lb) if la.get(k) != lb.get(k)}

        got = kinds(_map(), yaml.safe_load((PLANTED / "map-01.yaml").read_text()))
        assert {k for k in got if not k.isdigit()} <= {"canonical"}, sorted(got)
        expected = {
            "search-01.yaml": {"enumerated"},   # the plant: completely-walked catalogs called bounded
            "search-02.yaml": {"claim"},        # the plant: a claim exceeding its quote
            "search-03.yaml": {"hit", "dropped_note"},  # the plant: a hit with an unusable note
        }
        for name, allowed in expected.items():
            got = kinds(_search(), yaml.safe_load((PLANTED / name).read_text()))
            note_index = {k for k in got if isinstance(k, str) and k.isdigit()} | {"1", "2", "3"}
            assert got - allowed - note_index <= {"notes"}, (name, sorted(got - allowed))

    def test_the_answer_key_is_NOT_beside_the_fixtures(self):
        readme = (PLANTED / "README.md").read_text()
        for condition in ("C1 —", "C5 —", "C10 —", "C15 —"):
            assert condition not in readme
        assert "answer key is NOT here" in readme


# ---------------------------------------------------------------------------------------------
# C8c — the build contract §9c fixture-integrity sweep, over ALL fixtures
# ---------------------------------------------------------------------------------------------


class TestC8cFixtureIntegrity:
    """Runs BEFORE any reviewer is dispatched. Its whole job is to stop a ~70k-token blind run
    being spent on a broken fixture. NOT an exit criterion -- EC9b(d) is C8's, a different check."""

    def _search_fixtures(self) -> dict[str, dict]:
        out = {"search-output.valid.yaml": _search()}
        for p in sorted(PLANTED.glob("search-*.yaml")):
            out[p.name] = yaml.safe_load(p.read_text())
        return out

    def test_no_ACTIVE_source_the_angle_carries_is_without_a_cell(self):
        reg, m = _registry(), _map()
        active = {a["id"] for a in m["sources"]["active"]}
        for name, d in self._search_fixtures().items():
            angle = next(a for a in reg["angles"] if a["id"] == d["meta"]["angle_id"])
            owed = {s for s in angle["sources"] if s in active}
            got = {c["source_id"] for c in d["coverage"]}
            assert owed <= got, (name, sorted(owed - got))

    def test_no_cell_names_a_source_OUTSIDE_the_angles_corpus(self):
        reg = _registry()
        for name, d in self._search_fixtures().items():
            angle = next(a for a in reg["angles"] if a["id"] == d["meta"]["angle_id"])
            for c in d["coverage"]:
                assert c["source_id"] in angle["sources"], (name, c["source_id"])

    def test_no_fallback_left_NO_TRACE(self):
        """A walked fallback with no cell is indistinguishable from one never walked."""
        for name, d in self._search_fixtures().items():
            walked = {str(c["fallback_used"]).split(":", 1)[1]
                      for c in d["coverage"] if c.get("fallback_used")}
            cells = {c["source_id"] for c in d["coverage"]}
            assert walked <= cells, (name, sorted(walked - cells))

    def test_no_KEPT_ZERO_without_a_stated_cause_or_a_real_zero(self):
        """kept: 0 on a reached cell that returned rows is a silent drop."""
        for name, d in self._search_fixtures().items():
            for c in d["coverage"]:
                if c.get("kept") == 0 and c.get("status") == "reached" and c.get("returned"):
                    assert c.get("count_frame"), (name, c["group_id"], c["source_id"])

    def test_the_MAP_fixtures_put_every_registry_row_in_exactly_one_bucket(self):
        rows = {s["id"] for s in _registry()["sources"]}
        for p in [FIXTURES / "integration-vocabulary-map.valid.yaml", PLANTED / "map-01.yaml"]:
            m = yaml.safe_load(p.read_text())
            a = {x["id"] for x in m["sources"]["active"]}
            s = {x["id"] for x in m["sources"]["skipped"]}
            assert not a & s and (a | s) == rows, p.name


# ---------------------------------------------------------------------------------------------
# C8d — the per-package FIELD sweep (EC9c)
# ---------------------------------------------------------------------------------------------

#: A block is CONSTRAINED by any of these nine keywords, or by any of the three CONTAINER legs:
#: `properties`, `required`, or an `items` that is itself constrained. Stating only the nine is a
#: builder's trap -- every object field would classify as loose.
_CONSTRAINTS = frozenset({"enum", "const", "pattern", "$ref", "minimum", "maximum",
                          "minItems", "minProperties", "format"})

#: Loose in a schema and read by NO rule. DERIVED from the schemas once, at build, then FROZEN --
#: recomputing it from the same predicate at test time makes the assertion `X == X`.
UNREADABLE = frozenset({
    # transcribed identity, with no in-artifact counterpart to join against
    "name", "docs_url",
    # judged by a named §10 condition, and by nothing else
    "homepage",         # the two-conjunct admission test §2.3 delegates
    "evidence_quote",   # the claim-versus-quote boundary
    "claim",            # the other half of that boundary
    "category",         # a frozen-but-EXTENSIBLE vocabulary, so no rule can close it
    "map_verdict",      # quoted from the map: judged, never matched
    # free prose, unmatchable by a rule by construction
    "notes", "reason", "assumptions",
    # external pointers with no in-artifact counterpart
    "scope_ref", "borrowed_from",
    # the capability-coverage record. The set-difference is the COORDINATOR's -- nothing in this
    # validator can see capability-map.yaml
    "item",
    # provenance, transcribed for a later wave. Named ONE BY ONE, never as `provenance.*`: the
    # guard computes orphans over field NAMES, under which a glob matches nothing
    "nango_slug", "apisguru_key", "mcp_name", "sdk_purl",
})


class TestC8dTheFieldSweep:
    def _blocks(self) -> dict[str, list[dict]]:
        out: dict[str, list[dict]] = {}

        def walk(node):
            if isinstance(node, dict):
                for k, v in (node.get("properties") or {}).items():
                    out.setdefault(k, []).append(v if isinstance(v, dict) else {})
                    walk(v)
                for key in ("items", "then", "if"):
                    if key in node:
                        walk(node[key])
                for key in ("allOf", "anyOf", "oneOf"):
                    for sub in node.get(key) or []:
                        walk(sub)
                for sub in (node.get("$defs") or {}).values():
                    walk(sub)
            elif isinstance(node, list):
                for sub in node:
                    walk(sub)

        for n in ("integration-vocabulary-map", "search-output"):
            walk(json.loads((SCHEMAS / f"{n}.schema.json").read_text()))
        return out

    @staticmethod
    def _constrained(block: dict) -> bool:
        if any(k in block for k in _CONSTRAINTS):
            return True
        if "properties" in block or "required" in block:
            return True
        items = block.get("items")
        return isinstance(items, dict) and TestC8dTheFieldSweep._constrained(items)

    def test_loose_minus_read_EQUALS_the_exemption_set(self):
        """The shipped shape. Every field is constrained, or loose-and-read, or loose-and-unread --
        there is no fourth case, so nothing can fall between. Classified per (name, BLOCK) pair,
        because a name constrained in ONE branch would otherwise read as constrained everywhere
        while its loose occurrence is swept by nothing."""
        reads = set(_re.findall(r"""(?:\.get\(|\[)["']([a-z_][a-z0-9_]*)["']""", _SRC))
        loose = {n for n, blocks in self._blocks().items()
                 if not all(self._constrained(b) for b in blocks)}
        assert loose - reads == UNREADABLE, {
            "loose in a schema and read by no rule": sorted(loose - reads - UNREADABLE),
            "exempted as unreadable and now read": sorted(UNREADABLE - (loose - reads)),
        }

    def test_the_sweeps_INPUT_is_the_validator_and_never_the_test_module(self):
        """A `scripts/*.py` sweep would also read THIS module, whose subscripts into the fixture
        documents credit an exempt field as READ and break the equality from the other side."""
        assert SCRIPT.name.startswith("validate_")
        assert "test_" not in SCRIPT.name

    def test_every_field_a_REVIEWER_judges_carries_a_schema_description(self):
        blocks = self._blocks()
        for f in ("source_authority", "category", "homepage", "evidence_quote", "claim",
                  "present_on", "enumerated", "fallback_used", "kept", "count_frame"):
            assert any(str(b.get("description") or "").strip() for b in blocks[f]), f


# ---------------------------------------------------------------------------------------------
# C8b — the invariants the CLEAN blind run found broken, now asserted rather than eyeballed
# ---------------------------------------------------------------------------------------------


class TestTheCleanFixtureIsINTERNALLY_COHERENT:
    """A blind reviewer derived two real defects from this fixture's own arithmetic, with no fetch.
    Every one of these is that derivation, made mechanical."""

    def test_every_row_with_a_nango_slug_lists_nango_providers_in_present_on(self):
        """The self-contradiction that made the incompleteness provable: a slug transcribed FROM a
        catalog, on a row that does not record membership OF that catalog."""
        for c in _search()["candidates"]:
            if c["provenance"]["nango_slug"]:
                assert "nango-providers" in c["present_on"], c["item_id"]

    def test_every_SEED_service_the_map_names_has_a_recorded_outcome(self):
        """A service named in `integrations.third_party_list`, queried in every catalog and
        returning rows, must be admitted or unadmitted. Silently dropping it records neither."""
        d, m = _search(), _map()
        seeds = set(m["meta"]["classification"]["integrations"]["third_party_list"])
        recorded = {c["provenance"]["nango_slug"] for c in d["candidates"]} | {
            u["item_id"] for u in d["unadmitted"]}
        assert seeds <= recorded, sorted(seeds - recorded)

    def test_no_claim_asserts_what_its_own_quote_does_not_carry(self):
        """C10, made checkable for the two assertions every row makes."""
        for c in _search()["candidates"]:
            q, cl = c["evidence_quote"].lower(), c["claim"].lower()
            if "rest api" in cl:
                assert "rest" in q, c["item_id"]
            if "authorization code" in cl:
                assert "authorization code" in q, c["item_id"]

    def test_every_unadmitted_rows_FIELDS_agree_with_its_stated_reason(self):
        """A row that resolved no first-party home cannot carry a host-shaped id; one that DID
        resolve a home records it."""
        for u in _search()["unadmitted"]:
            if u["reason_class"] == "no-first-party-home":
                assert u["homepage"] is None, u["item_id"]
                assert u["item_id"].startswith("NODOMAIN-"), u["item_id"]
            if u["reason_class"] == "no-retrievable-corpus-row":
                assert u["homepage"], u["item_id"]

    def test_every_cells_returned_is_at_least_the_membership_it_records(self):
        """A cell cannot return fewer rows than the services recording presence on it."""
        d = _search()
        need: dict[tuple[str, str], int] = {}
        for c in d["candidates"]:
            g = c["found_by"].split("/")[0]
            for src in c["present_on"]:
                need[(g, src)] = need.get((g, src), 0) + 1
        for c in d["coverage"]:
            k = (c["group_id"], c["source_id"])
            assert c["returned"] >= need.get(k, 0), (k, c["returned"], need.get(k))

    def test_a_shared_term_is_queried_only_under_its_declared_OWNER(self):
        d, m = _search(), _map()
        owners = {st["term"]: st["owner"] for st in m["scope_guard"]["shared_terms"]}
        for c in d["coverage"]:
            for q in c["queries"]:
                term = q.split(" in:")[0]
                if term in owners:
                    assert owners[term] == c["group_id"], (term, c["group_id"])


class TestTheInputClassRulesAreExercisedBY_NAME:
    """The reachability guard found these seven exercised only by exit CODE. An exit code is not a
    rule id: two rules routed to the same code are indistinguishable to a caller grepping for one."""

    @staticmethod
    def _out(*args: str, env: dict | None = None) -> str:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args], capture_output=True, text=True,
            env={**os.environ, **(env or {})},
        ).stdout

    def test_input_names_itself(self, tmp_path):
        assert "FAIL input:" in self._out("keyword-map", str(tmp_path / "nope.yaml"))

    def test_keyword_map_invalid_names_itself(self, tmp_path):
        bad = tmp_path / "bad.yaml"
        bad.write_text("[1, 2, 3]\n")
        out = self._out("search", str(FIXTURES / "search-output.valid.yaml"), "--keyword-map", str(bad))
        assert "FAIL keyword-map-invalid:" in out

    def test_keyword_map_invalid_on_a_NON_MAPPING_names_itself(self, tmp_path):
        """The branch an earlier version had inside validate_search, where it was unreachable AND
        would have returned 1 for a rule main() routes to 2."""
        bad = tmp_path / "scalar.yaml"
        bad.write_text("just a string\n")
        out = self._out("search", str(FIXTURES / "search-output.valid.yaml"), "--keyword-map", str(bad))
        assert "FAIL keyword-map-invalid:" in out

    def test_registry_unreadable_names_itself(self, tmp_path):
        broken = tmp_path / "registry.yaml"
        broken.write_text("[]\n")
        out = self._out("keyword-map", str(FIXTURES / "integration-vocabulary-map.valid.yaml"),
                        env={"INTEGRATIONS_REGISTRY": str(broken)})
        assert "FAIL registry-unreadable:" in out

    def test_schema_names_itself_on_an_artifact_the_schema_refuses(self, tmp_path):
        doc = yaml.safe_load((FIXTURES / "integration-vocabulary-map.valid.yaml").read_text())
        del doc["meta"]["classification"]
        p = tmp_path / "m.yaml"
        p.write_text(yaml.safe_dump(doc))
        assert "FAIL schema:" in self._out("keyword-map", str(p))

    def test_schema_unavailable_names_itself_and_is_EXIT_2(self, tmp_path, monkeypatch, val):
        """A schema FILE that does not load is a package fault the artifact's author cannot repair,
        so it must not wear the id that means "your artifact is wrong"."""
        monkeypatch.setattr(val, "SCHEMAS", tmp_path)
        lines = val.validate_keyword_map(_map(), _registry())
        assert any(ln.startswith("FAIL schema-unavailable:") for ln in lines), lines
        assert "schema-unavailable" in val.EXIT2_PACKAGE_RULES

    def test_dependency_missing_names_itself(self, val, monkeypatch, capsys):
        monkeypatch.setattr(val, "_MISSING_DEPENDENCY", "yaml")
        assert val.main(["keyword-map", "x.yaml"]) == 2
        assert "FAIL dependency-missing:" in capsys.readouterr().out

    def test_outcome_block_required_names_itself_on_BOTH_outcomes(self, val):
        for outcome, block in (("not_run", "not_run"), ("vacated", "vacated")):
            d = _search()
            d["outcome"] = outcome
            d.pop(block, None)
            d["candidates"] = []
            d["unadmitted"] = []
            d.pop("bound", None)
            if outcome == "not_run":
                d["coverage"] = []
                d.pop("retrieval_summary", None)
            assert "outcome-block-required" in _s_rules(val, d), outcome


class TestTheRulesTheFIRST_PROSE_CYCLE_Demanded:
    """Three invariants the guides stated and NOTHING owned -- so the calibration fixture itself
    violated two of them and the gate exited 0. Writing a rule down is not enforcing it."""

    def test_found_by_precedence_fires_on_a_later_catalog(self, val):
        d = _search()
        c = next(x for x in d["candidates"] if len(x["present_on"]) > 1)
        g = c["found_by"].split("/")[0]
        later = [s for s in _registry()["angles"][0]["sources"] if s in c["present_on"]][-1]
        c["found_by"] = f"{g}/{later}"
        assert "found-by-precedence" in _s_rules(val, d)

    def test_found_by_precedence_silent_on_the_first_carrier(self, val):
        assert "found-by-precedence" not in _s_rules(val, _search())

    def test_group_term_unqueried_fires_on_a_SEED_service_never_asked(self, val):
        """The case the guide names: `stripe` is in the map's third_party_list AND an expansion of
        the service group, and was recoverable only because another axis happened to catch it."""
        d = _search()
        for c in d["coverage"]:
            if c["group_id"] == "g-svc-named":
                # CASE-INSENSITIVE: the n8n query spells the term CamelCase (`Stripe`), and the
                # rule lowercases before matching -- correctly, since that IS the term being asked.
                c["queries"] = [q for q in c["queries"] if "stripe" not in q.lower()]
        assert "group-term-unqueried" in _s_rules(val, d)

    def test_group_term_unqueried_silent_when_every_term_is_asked(self, val):
        assert "group-term-unqueried" not in _s_rules(val, _search())

    def test_group_term_unqueried_silent_for_a_term_owned_by_ANOTHER_group(self, val):
        """`booking` belongs to g-cat-scheduling by the map's shared_terms, so g-noun-meeting not
        asking it is correct rather than a gap."""
        m = _map()
        owned = {st["term"]: st["owner"] for st in m["scope_guard"]["shared_terms"]}
        assert owned, "fixture assumption: a shared term exists"
        assert "group-term-unqueried" not in _s_rules(val, _search())

    def test_cell_source_skipped_fires_on_a_cell_against_a_SKIPPED_source(self, val):
        """The absent-input policy says "do not write a cell for it" and nothing enforced it: a
        survey could silently claim to have walked the dead channel."""
        d = _search()
        c = dict(d["coverage"][0])
        c["source_id"] = "make-integrations-sitemap"
        c["kept"] = 0
        d["coverage"].append(c)
        assert "cell-source-skipped" in _s_rules(val, d)

    def test_cell_source_skipped_silent_on_an_ACTIVE_source(self, val):
        assert "cell-source-skipped" not in _s_rules(val, _search())


# ---------------------------------------------------------------------------------------------
# C10d — the two defects that survived a cold run, a blind review AND three prose cycles
# ---------------------------------------------------------------------------------------------
class TestStatedCountsAreDerivedFromWhatTheyCount:
    """The reviewer's SKILL said "EIGHT sources, and FIVE of them are PRODUCER-package paths" and
    then named THREE. Both numbers were right and the sentence was still wrong, which is the shape
    playbook #90 is about: a guard that LISTS something must DERIVE it."""

    @staticmethod
    def _evidence_rows():
        t = (REVIEWER / "SKILL.md").read_text()
        body = t.split("## Your evidence", 1)[1].split("**EIGHT", 1)[0]
        return [ln for ln in body.splitlines()
                if ln.startswith("| ") and not ln.startswith("| ---") and "| source |" not in ln]

    def test_the_stated_source_count_matches_the_table(self):
        assert len(self._evidence_rows()) == 8, self._evidence_rows()

    def test_the_stated_producer_path_count_matches_the_table(self):
        producer = [r for r in self._evidence_rows() if "integrations-prior-art-survey/" in r]
        assert len(producer) == 5, producer

    def test_every_producer_path_the_table_names_is_NAMED_in_the_sentence(self):
        """Counting five and naming three leaves a reader looking for two files nobody listed."""
        t = (REVIEWER / "SKILL.md").read_text()
        claim = t.split("**EIGHT", 1)[1].split("## Conditions", 1)[0]
        for word in ("schemas", "registry", "angle references", "absent-input policy",
                     "category vocabulary"):
            assert word in claim, word

    def test_every_producer_path_the_table_names_EXISTS(self):
        for row in self._evidence_rows():
            for tok in row.split("`"):
                if tok.startswith("integrations-prior-art-survey/") and "<" not in tok:
                    hits = list(PKG.parent.glob(tok))
                    assert hits, tok


class TestTheCleanFixturesCellsAreDerivedFromTheMap:
    """The fixture recorded re-runnable commands beside COMPOSED counts. A reviewer who re-ran them
    found 19 of 20 cells contradicted. The counts themselves need the network, but the QUERIES do
    not: every cell must ask exactly the terms the map says that group owns, so a cell cannot drift
    from the vocabulary it claims to be searching."""

    @staticmethod
    def _terms_in(cell):
        joined = " ".join(cell["queries"])
        if cell["source_id"] == "zapier-apps-sitemap":
            return set(re.findall(r"apps/([a-z0-9.-]+)/integrations", joined))
        return set(re.findall(r'test\("([a-z0-9.]+)"\)', joined))

    def test_each_cell_asks_exactly_its_groups_OWNED_terms(self):
        d, m = _search(), _map()
        owner = {s["term"]: s["owner"] for s in m["scope_guard"]["shared_terms"]}
        groups = {g["id"]: g for g in m["groups"]}
        for c in d["coverage"]:
            g = groups[c["group_id"]]
            owned = [t for t in [g["canonical"], *g["expansions"]]
                     if owner.get(t, c["group_id"]) == c["group_id"]]
            want = {t.replace(" ", "-") if c["source_id"] == "zapier-apps-sitemap"
                    else t.lower().replace("-", "").replace("_", "") for t in owned}
            assert self._terms_in(c) == want, (c["group_id"], c["source_id"])

    def test_a_shared_term_is_asked_by_its_OWNER_and_by_nobody_else(self):
        d, m = _search(), _map()
        shared = m["scope_guard"]["shared_terms"]
        assert shared, "fixture assumption: the map declares a shared term"
        for st in shared:
            norm = st["term"].lower().replace("-", "").replace("_", "")
            asks = {c["group_id"] for c in d["coverage"]
                    if norm in self._terms_in(c) or st["term"] in self._terms_in(c)}
            assert asks == {st["owner"]}, (st["term"], asks)

    def test_every_candidate_quotes_a_locator_it_actually_names(self):
        """`evidence_quote` is verbatim FROM THE LOCATOR. A quote with no locator to check it
        against is unfalsifiable, and every composed quote this pair shipped had one."""
        for c in _search()["candidates"]:
            assert c["locator"] and c["locator"].startswith("https://"), c["item_id"]
            assert c["evidence_quote"].strip(), c["item_id"]

    def test_no_candidate_claims_an_api_style_a1_cannot_observe(self):
        for c in _search()["candidates"]:
            assert c["api_style"] == "unknown", c["item_id"]
            assert c["descriptor"] == "unknown", c["item_id"]


class TestEC11aTheMeasuredCapsCannotDriftFromTheirMeasurement:
    """EC11a says "a check re-derives each from §B3 so a cap cannot drift from the measurement that
    set it". The criterion shipped with no such check — a rule stated and not enforced, which is
    this pair's other recurring defect. The spec lives in a different repo, so what is checkable
    HERE is that each measured cap still carries its own measurement, in the registry and in the
    angle reference, and that the two agree.

    The four are the caps the coordinator marks owed-at-build. The numbers are B3's, 2026-09-03.
    """

    MEASURED = {
        "a2": (100, ["94", "180", "235", "282"]),
        "a3": (60, ["18", "7,805", "SIX OF THE TEN"]),
        "b1": (40, ["59.2%", "680"]),
        "b3": (25, ["53.5%", "20.9%"]),
    }

    def test_each_measured_cap_still_holds_its_registry_value(self):
        angles = {a["id"]: a for a in _registry()["angles"]}
        for aid, (cap, _) in self.MEASURED.items():
            assert angles[aid]["cap"] == cap, aid

    def test_each_cap_rationale_carries_the_numbers_that_SET_the_cap(self):
        """A cap whose rationale has lost its measurement is a number nobody can re-derive."""
        angles = {a["id"]: a for a in _registry()["angles"]}
        for aid, (_, tokens) in self.MEASURED.items():
            why = angles[aid]["cap_rationale"]
            assert "B3" in why, aid
            for tok in tokens:
                assert tok in why, (aid, tok)

    def test_the_angle_reference_states_the_SAME_cap_as_the_registry(self):
        """Two homes for one number is how the a1 ordering carried two live readings at once."""
        angles = {a["id"]: a for a in _registry()["angles"]}
        for aid in self.MEASURED:
            t = (PKG / "references" / "angles" / f"{aid}.md").read_text()
            assert str(angles[aid]["cap"]) in t, aid


class TestTheProseCyclesRetractedClaimsStayRetracted:
    """D2b, extended per cycle. Each string below was SHIPPED and is now false. A fold that removes a claim from the one
    file a reviewer happened to quote, while a second copy survives elsewhere, is #89's half-resync
    — and this pair produced it twice, including on the a1 ordering, where the spec kept the
    original text while the registry carried the re-derivation.

    Globs `.py` as well as prose and fixtures: the composed values lived in YAML, and the
    un-appliable ordering lived in a `.md` and a `.yaml` at once.

    **A retracted claim is forbidden as an ASSERTION and permitted as a RECORD.** The corrected
    files legitimately NAME what they replaced — that is how a later reader learns the ordering was
    wrong three times — so a sweep that cannot tell the two apart forces every fix to delete its own
    reasoning. A match is an offender unless a retraction marker appears in its immediate
    neighbourhood.
    """

    #: retracted claim -> why it is false now
    RETRACTED = {
        "Nango category rank":
            "a1's first ordering named a field the corpus does not have",
        "category size descending as the tie-break":
            "a1's third ordering: only nango-providers can compute categories, so four of five "
            "sources could not apply the tie-break",
        "Authentication to the Stripe API is performed via HTTP Bearer Auth":
            "a composed evidence_quote; the page its locator names says API keys",
        "NODOMAIN-bookr":
            "an invented service in a fixture whose premise is that every value is measured",
        "the schemas, the registry and the angle references":
            "the sentence counted FIVE producer paths and named three",
        "item_id: zoom.us":
            "zoom.us redirects to zoom.com, so it is not the vendor's own host",
        # --- C10e ---
        "each with an auth mode, a docs link":
            "61 of the 990 nango rows carry no auth_mode at all, google-calendar among them",
        "a named ten-product sample":
            "six of the ten were never recorded, so the sample's membership is not re-derivable",
        "the six regulated-adjacent categories":
            "which six was never recorded, and no subset reproduces the row count",
        "pipedream-components returned zero on every group":
            "three of its own five cells returned rows",
        "CamelCase directory names, no separator (`AcuityScheduling`, `QuickBooks`)":
            "n8n vendor families nest one level, so a top-level walk fabricates a zero",
        "three checks (two fetches and one resolution inside the first)":
            "the probe makes three separate requests, as the guide and the fixture both say",
        "Six sources, and the last two are the ones a reviewer most often skips":
            "the shipped reviewer names EIGHT, and neither item is in its last two",
        # --- C10f ---
        "308 base nodes, one directory each":
            "308 counts DIRECTORIES; 558 node files live in them and 103 dirs hold more than one",
        "5,500 enumerable entries":
            "the n8n term was a directory count, not a node count; the sum is ~5,800",
        "directory size descending, then seed-product name":
            "only vendor-integration-pages is a directory, and six of ten sampled yielded no count",
        "dependent-repo count descending, then package name":
            "only ecosystems-packages yields dependent counts",
        "event-surface richness (published event-type count), then service name":
            "three of b2's four sources yield an adopter list, not an event-type count",
        "descriptor completeness, then provider name":
            "public-apis carries no descriptor at all",
    }

    #: A claim inside one of these is being RECORDED as retracted, not asserted.
    MARKERS = ("earlier revision", "earlier version", "the original", "originally",
               "re-derived", "previously", "retracted", "no longer", "used to read")

    EXCLUDED = ("test_validate_integrations_prior_art.py",)
    WINDOW = 240

    #: The two COMPANION DESIGN DOCS. C10f found a retracted claim alive in one of them: the sweep
    #: globbed only the two package directories, so the files most likely to RESTATE a measurement
    #: were the two it never read.
    DESIGN_DOCS = [ROOT / "docs" / "skills" / f"{n}-prior-art-survey.md"
                   for n in ("integrations", "reviewing-integrations")]

    def _corpus(self) -> list[pathlib.Path]:
        return sorted(
            p for p in list(PKG.rglob("*.md")) + list(PKG.rglob("*.yaml"))
            + list(PKG.rglob("*.json")) + list(PKG.rglob("*.py"))
            + list(REVIEWER.rglob("*.md")) + list(REVIEWER.rglob("*.yaml"))
            + list(REVIEWER.rglob("*.json"))
            + [d for d in self.DESIGN_DOCS if d.exists()]
            if p.name not in self.EXCLUDED
        )

    @classmethod
    def _assertions_of(cls, text: str) -> list[str]:
        """Every occurrence of a retracted claim that is NOT inside a retraction record."""
        out = []
        for claim in cls.RETRACTED:
            i = text.find(claim)
            while i != -1:
                near = text[max(0, i - cls.WINDOW): i + len(claim) + cls.WINDOW].lower()
                if not any(m in near for m in cls.MARKERS):
                    out.append(claim)
                i = text.find(claim, i + 1)
        return out

    def test_the_globbed_population_meets_its_FLOOR(self):
        """A sweep whose population shrinks to nothing reports green."""
        assert len(self._corpus()) >= 24, len(self._corpus())

    def test_BOTH_design_docs_are_in_the_population(self):
        """Named explicitly, because their absence is exactly what let a retracted claim survive
        a fold: the sweep read both packages and neither companion doc."""
        got = set(self._corpus())
        for d in self.DESIGN_DOCS:
            assert d.exists(), d
            assert d in got, d

    def test_no_retracted_claim_is_ASSERTED_anywhere_an_agent_READS(self):
        offenders: list[str] = []
        for p in self._corpus():
            text = p.read_text(encoding="utf-8", errors="replace")
            for claim in self._assertions_of(text):
                where = p.relative_to(ROOT) if ROOT in p.parents else p.name
                offenders.append(f"{where}: {claim!r} — {self.RETRACTED[claim]}")
        assert not offenders, offenders

    def test_a_bare_RE_ASSERTION_is_caught(self):
        """Proven, not asserted: three of this pair's tests could not fail, each found by mutation.
        The same string with and without its retraction marker must give opposite answers."""
        for claim in self.RETRACTED:
            assert self._assertions_of(f"Ordering: {claim}.") == [claim], claim
            assert self._assertions_of(f"An earlier revision said {claim}.") == [], claim

    def test_the_two_ORDERING_retractions_are_still_recorded(self):
        """Only these two. A fabricated quote, an invented service and a wrong host are DELETED —
        a package that preserves a fabricated quote verbatim is worse, not more honest. But the
        ordering was wrong three times, and a reader who cannot see that will propose the second
        wrong answer again."""
        blob = "".join(p.read_text(encoding="utf-8", errors="replace") for p in self._corpus())
        for claim in ("Nango category rank", "category size descending as the tie-break"):
            assert claim in blob, claim

    def test_the_sweep_really_READS_the_files_it_globs(self):
        """A live claim from the corrected contract. If this is absent, the corpus is not being
        read and every green above is vacuous."""
        blob = "".join(p.read_text(encoding="utf-8", errors="replace") for p in self._corpus())
        assert "the catalog's own entry order" in blob


class TestTheAlwaysOnSetIsREADFromTheRegistry:
    """C10e. `ALWAYS_ON = ("a1", "a2", "a3")` shipped under a comment saying it was "DERIVED from
    the registry at call time". It was a module-level literal — right on the day, and silently
    desynchronised the moment a registry `trigger` changed. A comment asserting a property the code
    beneath it does not have is worse than no comment."""

    def test_it_matches_the_registrys_own_triggers(self, val):
        reg = _registry()
        assert val._always_on(reg) == tuple(
            a["id"] for a in reg["angles"] if a.get("trigger") == "always")

    def test_it_FOLLOWS_a_changed_trigger(self, val):
        """The mutation the literal could not survive. If this passes with a hardcoded tuple, the
        derivation is not happening."""
        reg = copy.deepcopy(_registry())
        next(a for a in reg["angles"] if a["id"] == "a3")["trigger"] = "conditional"
        assert val._always_on(reg) == ("a1", "a2"), val._always_on(reg)
        reg = copy.deepcopy(_registry())
        next(a for a in reg["angles"] if a["id"] == "b5")["trigger"] = "always"
        assert "b5" in val._always_on(reg)

    def test_no_module_level_CONSTANT_restates_the_angle_set(self):
        """Checked on the AST, not by substring: the docstring above deliberately QUOTES the literal
        it replaced, and a substring check would forbid the record of the defect along with the
        defect. Walking module-level assignments asks the question that actually matters."""
        import ast
        src = (PKG / "scripts" / "validate_integrations_prior_art.py").read_text()
        angle_ids = {a["id"] for a in _registry()["angles"]}
        offenders = []
        for node in ast.parse(src).body:
            if not isinstance(node, ast.Assign):
                continue
            v = node.value
            if not isinstance(v, (ast.Tuple, ast.List, ast.Set)):
                continue
            vals = {e.value for e in v.elts
                    if isinstance(e, ast.Constant) and isinstance(e.value, str)}
            if vals and vals <= angle_ids:
                offenders += [t.id for t in node.targets if isinstance(t, ast.Name)]
        assert not offenders, offenders


class TestTheWorkedExamplesTheDocsPromiseActuallyEXIST:
    """C10e. `category-vocabulary.md` told a reviewer that `scheduling` is the worked example and
    that "the calibration fixture records it WITH its provenance note". No fixture recorded any
    out-of-seed category at all, so C13's worked example did not exist. A doc that sends a reviewer
    to check a thing must be checkable."""

    @staticmethod
    def _seeded() -> set[str]:
        """DERIVED from the vocabulary file's own two source sections, not hand-listed."""
        import re
        t = (PKG / "references" / "category-vocabulary.md").read_text()
        return set(re.findall(r"`([a-z][a-z0-9_-]*)`", t.split("## Where the two disagree")[0]))

    def test_a_candidate_records_an_OUT_OF_SEED_category(self):
        cats = {c["category"] for c in _search()["candidates"]}
        assert cats - self._seeded(), f"no candidate exercises C13; categories are {sorted(cats)}"

    def test_that_candidate_carries_its_PROVENANCE(self):
        seeded = self._seeded()
        checked = 0
        for c in _search()["candidates"]:
            if c["category"] in seeded:
                continue
            checked += 1
            joined = " ".join(c.get("notes") or [])
            assert "PROVENANCE" in joined, c["item_id"]
            assert c["locator"] in joined or "locator" in joined or "self-description" in joined, \
                c["item_id"]
        assert checked, "no out-of-seed candidate was examined; this test proved nothing"

    def test_the_vocabulary_doc_names_the_example_the_fixture_actually_records(self):
        t = (PKG / "references" / "category-vocabulary.md").read_text()
        example = [c["category"] for c in _search()["candidates"]
                   if c["category"] not in self._seeded()]
        for cat in example:
            assert f"`{cat}`" in t, cat


class TestTheBlindPacketStagesEveryContractFileAConditionNeeds:
    """C10f. The staging list named three of the five producer paths the reviewer's own evidence
    table lists, omitting the absent-input policy (C9) and the category vocabulary (C13) — the two
    its `sources.md` says those conditions cannot be discharged without. Withholding is for WORKED
    ANSWERS, never for the contract a condition is judged against."""

    @staticmethod
    def _producer_paths_in_the_evidence_table() -> set[str]:
        t = (REVIEWER / "SKILL.md").read_text()
        body = t.split("## Your evidence", 1)[1].split("**EIGHT", 1)[0]
        out = set()
        for row in body.splitlines():
            for tok in row.split("`"):
                if tok.startswith("integrations-prior-art-survey/"):
                    out.add(tok)
        return out

    def test_the_table_really_names_five(self):
        assert len(self._producer_paths_in_the_evidence_table()) == 5, \
            sorted(self._producer_paths_in_the_evidence_table())

    @staticmethod
    def _stem(path: str) -> str:
        """The table writes `schemas/*.json` and `angles/<angle>.md`; the staging list names the
        DIRECTORY. Compare on what both spell the same way."""
        for marker in ("*", "<"):
            if marker in path:
                return path[: path.index(marker)]
        return path

    def test_the_staging_list_names_every_one_of_them(self):
        staging = (REVIEWER / "references" / "fixtures" / "README.md").read_text()
        missing = [q for q in self._producer_paths_in_the_evidence_table()
                   if self._stem(q) not in staging]
        assert not missing, missing

    def test_the_comparison_can_FAIL(self):
        """Guards the normalisation itself: a path the list does not name must be reported."""
        staging = (REVIEWER / "references" / "fixtures" / "README.md").read_text()
        assert self._stem("integrations-prior-art-survey/references/nonexistent.md") not in staging


class TestEveryOrderingIsAppliableAcrossTheSourcesItsAngleWalks:
    """C10f. The registry states the test in its own words — "appliable across every source THIS
    ANGLE walks" is the test, not "appliable somewhere" — and nothing enforced it. It had been
    applied to `a1` alone. Three other angles declared primary keys only ONE of their own sources
    could supply: a3 on directory size (only `vendor-integration-pages` is a directory), b1 on
    dependent-repo count (only `ecosystems-packages` yields it), b2 on event-type count (only
    `vendor-webhook-docs` yields it).

    An ordering the run cannot apply makes `ordering_deviation` the normal path, which is a cap
    with no honesty behind it.
    """

    #: Properties of the LIST YOU WALK, or of any entry whatsoever. Appliable by construction,
    #: because they do not ask the source for a ranking it may not expose.
    UNIVERSAL = ("declaration order", "entry order", "listing order", "name ascending",
                 "name descending", "map's own category order")

    STOP = {"the", "a", "an", "of", "this", "then", "by", "its", "own", "and", "or", "count",
            "descending", "ascending", "order", "walks", "angle", "properties", "input", "list"}

    @staticmethod
    def _primary(sig: str) -> str:
        return re.split(r",| then | -- ", sig)[0].strip().lower()

    def test_the_registry_still_STATES_the_test(self):
        """If the stated test is ever deleted, this guard is enforcing nothing anybody asked for."""
        t = (PKG / "references" / "source-registry.yaml").read_text()
        assert "appliable across every source" in t

    def test_every_angles_ordering_is_appliable_across_all_its_sources(self):
        reg = _registry()
        yields = {s["id"]: (s.get("yields") or "").lower() for s in reg["sources"]}
        skipped = {"make-integrations-sitemap"}
        offenders = []
        for a in reg["angles"]:
            sig = a.get("ordering_signal") or ""
            if any(u in sig.lower() for u in self.UNIVERSAL):
                continue
            srcs = [s for s in a["sources"] if s not in skipped]
            toks = {w.strip("`'\"()") for w in self._primary(sig).split()} - self.STOP
            toks = {w for w in toks if len(w) > 3}
            if not any(all(tok in yields.get(s, "") for s in srcs) for tok in toks):
                offenders.append((a["id"], self._primary(sig)))
        assert not offenders, offenders

    def test_the_guard_REJECTS_the_orderings_that_were_wrong(self, val):
        """Mutation, not assertion. Each of these shipped, and each must now be refused."""
        reg = copy.deepcopy(_registry())
        yields = {s["id"]: (s.get("yields") or "").lower() for s in reg["sources"]}
        for aid, bad in (("a3", "directory size descending, then seed-product name"),
                         ("b1", "dependent-repo count descending, then package name"),
                         ("b2", "event-surface richness (published event-type count), then service name")):
            a = next(x for x in reg["angles"] if x["id"] == aid)
            srcs = [s for s in a["sources"] if s != "make-integrations-sitemap"]
            toks = {w.strip("`'\"()") for w in self._primary(bad).split()} - self.STOP
            toks = {w for w in toks if len(w) > 3}
            assert not any(u in bad.lower() for u in self.UNIVERSAL), aid
            assert not any(all(tok in yields.get(s, "") for s in srcs) for tok in toks), \
                f"{aid}: the guard would have PASSED the ordering that shipped wrong"
