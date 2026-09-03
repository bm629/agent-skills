"""Tests for the integrations prior-art validator and its registry.

Run:  uv run --group dev pytest skills/integrations-prior-art-survey/scripts -q
"""

from __future__ import annotations

import copy
import os
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

    def test_the_EXIT_2_RULE_SET_is_asserted_by_EQUALITY(self, val):
        """So a rule added later must pick a side rather than inherit one."""
        assert val.EXIT2_REGISTRY_RULES == frozenset(
            {
                "complete-listing-declared",
                "yields-declared",
                "authority-band-known",
                "probe-method-shape",
                "terminal-needs-rationale",
                "fallback-cycle",
                "fallback-unresolvable",
                "seed-input-not-widening",
            }
        )

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
        assert len(val._owed_cells(a1, m, reg)) == 25

    def test_dropping_the_angles_OWN_source_list_INFLATES_the_grid(self, val):
        """5 groups x 5 of a1's active sources = 25. Without the second term every angle would owe
        every ACTIVE row -- 5 x 19 = 95, nearly four times the real obligation."""
        reg, m = _registry(), _map()
        a1 = next(a for a in reg["angles"] if a["id"] == "a1")
        types = set(a1["applicable_group_types"])
        groups = [g["id"] for g in m["groups"] if g["type"] in types]
        active = {a["id"] for a in m["sources"]["active"]}
        assert len(groups) * len(active) == 95
        assert len(val._owed_cells(a1, m, reg)) == 25

    def test_dropping_the_maps_ACTIVE_set_owes_a_row_this_run_never_had(self, val):
        """a1 carries six sources; the map SKIPPED make-integrations-sitemap, so the sixth is not
        owed. Without the third term the angle would owe a cell against a dead channel."""
        reg, m = _registry(), _map()
        a1 = next(a for a in reg["angles"] if a["id"] == "a1")
        owed = val._owed_cells(a1, m, reg)
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

    def test_cap_respected(self, val):
        d = _search()
        d["bound"]["cap"] = 2
        r = _s_rules(val, d)
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

    def test_bound_cap_null_is_LEGAL(self, val):
        """a3 may resolve to "no cap binds", so the no-cap form must validate clean."""
        d = _search()
        d["bound"]["cap"] = None
        d["bound"]["hit"] = False
        reg = _registry()
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
        assert "present-on-source-known" in {
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
        d = _search()
        c = d["candidates"][-1]
        c["id_class"] = "host"
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

    def test_http_scheme_vocabulary_is_CASE_INSENSITIVE(self, val):
        """Real descriptors overwhelmingly write `scheme: bearer`. A JSON Schema enum is exact-match
        and would refuse it before this rule ran, leaving a correctly transcribed descriptor with no
        legal writing -- which is why the field carries a description and no enum."""
        d = _search()
        c = next(x for x in d["candidates"] if x["auth_scheme"] == "http")
        c["http_scheme"] = "bearer"
        assert "http-scheme-vocabulary" not in _s_rules(val, d)

    def test_http_scheme_vocabulary_refuses_an_outsider(self, val):
        d = _search()
        c = next(x for x in d["candidates"] if x["auth_scheme"] == "http")
        c["http_scheme"] = "SuperAuth"
        assert "http-scheme-vocabulary" in _s_rules(val, d)

    def test_the_auth_mode_map_covers_all_NINE_values_including_the_three_that_map_to_null(self, val):
        m = val.AUTH_MODE_TO_OAS
        assert len(m) == 9
        assert sorted(k for k, v in m.items() if v is None) == ["APP", "APP_STORE", "CUSTOM", "OAUTH1", "TBA"]
        assert set(v for v in m.values() if v) <= set(val.OAS_AUTH_SCHEMES)

    def test_an_UNMAPPED_catalog_value_takes_the_same_treatment_as_the_three(self, val):
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
        c = d["candidates"][0]
        assert c["found_by"].split("/")[1] == "nango-providers"
        assert c["source_authority"] == "first-party"
        assert val.validate_search(d, _registry(), _map()) == []
