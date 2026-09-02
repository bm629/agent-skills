"""Tests for the regulatory prior-art gate.

Every rule gets a negative test that FIRES it and a mirror that passes at the boundary. A negative
test alone proves a rule can fire; it does not prove the rule is not firing on everything, and a
membership check that fires on everything passes its negative test and fails nothing else.
"""

from __future__ import annotations

import copy
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "validate_regulatory_prior_art.py"
FIXTURES = HERE / "fixtures"
PACKAGE = HERE.parent
REVIEWER = PACKAGE.parent / "reviewing-regulatory-prior-art-survey"


def _load():
    spec = importlib.util.spec_from_file_location("validate_regulatory_prior_art", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


V = _load()


_HASHED = re.compile(r"--[0-9a-f]{12}$")


def _undeclared_pair(doc: dict) -> tuple[dict, dict]:
    """Two groups whose canonicals are NOT already in `shared_terms`.

    The clean fixture declares one real collision on purpose, so a mutation that happens to land on
    it tests the DECLARED path while claiming to test the undeclared one.
    """
    declared = {" ".join(str(d["term"]).split()).casefold()
                for d in doc["scope_guard"].get("shared_terms") or []}
    free = [g for g in doc["groups"]
            if " ".join(str(g["canonical"]).split()).casefold() not in declared]
    assert len(free) >= 2, "the fixture declares every group's canonical as shared"
    return free[0], free[1]


def _rules(findings: list[str]) -> list[str]:
    """The rule ids out of `FAIL <rule>: <message>` lines."""
    return [f.split(":", 1)[0].removeprefix("FAIL ").strip() for f in findings]


def _clean(findings: list[str]) -> list[str]:
    """The rule ids, for a MIRROR assertion, refusing a vacuous pass.

    The schema pass returns EARLY: one shape error and no rule below it runs. So
    `assert "x" not in _clean(...)` on a schema-invalid mutation passes while proving nothing
    about `x` -- the rule never got the chance to fire. Every mirror in this module goes through
    here, so that failure mode is a test error at the call site rather than a silent green.
    """
    rules = _rules(findings)
    assert "schema" not in rules, (
        "MIRROR ran on a schema-INVALID document, so the rule it names never ran: "
        + "; ".join(f for f in findings if f.startswith("FAIL schema")))
    return rules


@pytest.fixture
def registry() -> dict:
    return yaml.safe_load((PACKAGE / "references" / "source-registry.yaml").read_text())


@pytest.fixture
def valid_map() -> dict:
    return yaml.safe_load((FIXTURES / "regulatory-scope-map.valid.yaml").read_text())


@pytest.fixture
def valid_search() -> dict:
    return yaml.safe_load((FIXTURES / "search-output.valid.yaml").read_text())


class TestRegistryIntegrity:
    """Exit 2, before any artifact is read. These are faults in the PACKAGE, and reporting one as
    exit 1 sends an author off to edit an artifact that is fine."""

    def test_the_shipped_registry_is_clean(self, registry):
        assert V.registry_failures(registry) == []

    @pytest.mark.parametrize("shape", [[], "a string", None, 3])
    def test_a_registry_that_is_not_a_mapping_is_caught(self, shape):
        assert "not-a-mapping" in _rules(V.registry_failures(shape))

    def test_an_angle_with_no_id_is_caught(self, registry):
        doc = copy.deepcopy(registry)
        doc["angles"][0].pop("id")
        assert "angle-id-required" in _rules(V.registry_failures(doc))

    def test_an_unknown_trigger_is_caught(self, registry):
        doc = copy.deepcopy(registry)
        doc["angles"][0]["trigger"] = "sometimes"
        assert "trigger-must-be-known" in _rules(V.registry_failures(doc))

    def test_a_conditional_angle_with_no_anchor_is_caught(self, registry):
        doc = copy.deepcopy(registry)
        a = next(x for x in doc["angles"] if x["trigger"] == "conditional")
        a.pop("trigger_anchor")
        assert "anchor-required" in _rules(V.registry_failures(doc))

    def test_an_always_on_angle_carrying_an_anchor_is_caught(self, registry):
        doc = copy.deepcopy(registry)
        a = next(x for x in doc["angles"] if x["trigger"] == "always")
        a["trigger_anchor"] = ["regulatory.applies"]
        assert "anchor-only-on-conditional" in _rules(V.registry_failures(doc))

    def test_an_anchor_on_an_optional_field_is_caught(self, registry):
        """An anchor rooted on an OPTIONAL classification field fails closed for every map that
        omits it — silently, and for exactly the products that needed the angle."""
        doc = copy.deepcopy(registry)
        a = next(x for x in doc["angles"] if x["trigger"] == "conditional")
        a["trigger_anchor"] = ["data_ml.eu_ai_act.risk_level"]
        assert "anchor-must-be-required" in _rules(V.registry_failures(doc))

    def test_an_anchor_that_is_not_a_list_is_caught(self, registry):
        doc = copy.deepcopy(registry)
        a = next(x for x in doc["angles"] if x["trigger"] == "conditional")
        a["trigger_anchor"] = "business.platform.type"
        assert "anchor-must-be-a-list" in _rules(V.registry_failures(doc))

    def test_an_angle_naming_an_unknown_source_is_caught(self, registry):
        doc = copy.deepcopy(registry)
        doc["angles"][0]["sources"] = ["not-a-real-row"]
        assert "angle-source-unknown" in _rules(V.registry_failures(doc))

    def test_an_angle_whose_fallback_is_outside_its_own_sources_is_caught(self, registry):
        """A fallback the angle cannot reach is a route on paper only."""
        doc = copy.deepcopy(registry)
        a = doc["angles"][0]
        a["fallback"] = next(s["id"] for s in doc["sources"] if s["id"] not in a["sources"])
        assert "angle-fallback-unreachable" in _rules(V.registry_failures(doc))

    def test_a_null_terminal_with_no_rationale_is_caught(self, registry):
        doc = copy.deepcopy(registry)
        row = next(s for s in doc["sources"] if s.get("fallback") is None)
        row.pop("fallback_rationale")
        assert "terminal-needs-rationale" in _rules(V.registry_failures(doc))

    def test_a_fallback_cycle_is_caught(self, registry):
        doc = copy.deepcopy(registry)
        term = next(s for s in doc["sources"] if s.get("fallback") is None)
        term["fallback"] = next(
            s["id"] for s in doc["sources"] if s.get("fallback") == term["id"]
        )
        assert "fallback-cycle" in _rules(V.registry_failures(doc))

    def test_a_self_fallback_is_a_terminal_not_a_cycle(self, registry):
        """MIRROR at the boundary. A sibling registry uses a self-fallback to mean 'there is no
        second channel', documented in its own preamble. Reading it as a cycle would report ten
        false defects there; this package uses `null` and both must read as terminal."""
        doc = copy.deepcopy(registry)
        row = next(s for s in doc["sources"] if s.get("fallback") is None)
        row["fallback"] = row["id"]
        assert "fallback-cycle" not in _clean(V.registry_failures(doc))

    def test_a_fallback_to_a_row_that_DOES_NOT_EXIST_is_caught(self, registry):
        """`fallback-unresolvable` and `fallback-cycle` are different defects and this one had no
        negative at all: a cycle promises a second channel and returns to the first, this promises
        a channel that was never a row. Asserting the cycle rule stays quiet keeps the pair from
        collapsing into one check that fires on both and distinguishes neither.
        """
        doc = copy.deepcopy(registry)
        row = next(s for s in doc["sources"] if s.get("fallback") is None)
        row["fallback"] = "a-source-that-was-never-a-row"
        found = _rules(V.registry_failures(doc))
        assert "fallback-unresolvable" in found
        assert "fallback-cycle" not in found


class TestProbeMethodShape:
    """`probe_method` is a REGISTRY field, so a wrong-shaped one is exit 2 — not exit 1 beside the
    artifact rules. Grouping it with those would have left its exit code undecided."""

    def test_the_registry_wide_default_is_required(self, registry):
        doc = copy.deepcopy(registry)
        doc.pop("probe_default")
        assert "probe-method-shape" in _rules(V.registry_failures(doc))

    @pytest.mark.parametrize("bad", ["yes", 3, [], {"headers": {}}])
    def test_a_default_missing_its_method_is_caught(self, bad, registry):
        doc = copy.deepcopy(registry)
        doc["probe_default"] = bad
        assert "probe-method-shape" in _rules(V.registry_failures(doc))

    def test_a_row_override_missing_its_method_is_caught(self, registry):
        doc = copy.deepcopy(registry)
        row = next(s for s in doc["sources"] if "probe_method" in s)
        row["probe_method"] = {"headers": {"Accept": "text/html"}}
        assert "probe-method-shape" in _rules(V.registry_failures(doc))

    def test_a_row_override_with_non_string_headers_is_caught(self, registry):
        doc = copy.deepcopy(registry)
        row = next(s for s in doc["sources"] if "probe_method" in s)
        row["probe_method"] = {"method": "GET", "headers": {"Accept": 5}}
        assert "probe-method-shape" in _rules(V.registry_failures(doc))

    def test_a_row_with_no_override_is_legal(self, registry):
        """MIRROR: the field is an OVERRIDE. Requiring it on every row would put the same three
        lines on nineteen of them, which a reader learns to skip."""
        doc = copy.deepcopy(registry)
        for s in doc["sources"]:
            s.pop("probe_method", None)
        assert "probe-method-shape" not in _clean(V.registry_failures(doc))


class TestTheExitContract:
    """Run through `main()`, because a subcommand reachable only in tests is a subcommand that
    does not ship."""

    def _cli(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            capture_output=True, text=True, cwd=HERE, check=False,
        )

    def test_a_clean_map_exits_0(self):
        r = self._cli("keyword-map", str(FIXTURES / "regulatory-scope-map.valid.yaml"))
        assert r.returncode == 0, r.stdout + r.stderr

    def test_a_missing_file_exits_2(self, tmp_path):
        r = self._cli("keyword-map", str(tmp_path / "nope.yaml"))
        assert r.returncode == 2
        assert "FAIL input:" in r.stdout + r.stderr

    def test_unparseable_yaml_exits_2(self, tmp_path):
        bad = tmp_path / "bad.yaml"
        bad.write_text("a: [1, 2\n  b: {\n")
        r = self._cli("keyword-map", str(bad))
        assert r.returncode == 2

    def test_an_unreadable_registry_exits_2(self, tmp_path, monkeypatch):
        r = subprocess.run(
            [sys.executable, str(SCRIPT), "keyword-map",
             str(FIXTURES / "regulatory-scope-map.valid.yaml")],
            capture_output=True, text=True, cwd=HERE, check=False,
            env={**__import__("os").environ, "REGULATORY_REGISTRY_OVERRIDE": str(tmp_path / "gone.yaml")},
        )
        assert r.returncode == 2
        assert "registry-unreadable" in r.stdout + r.stderr

    def test_a_missing_dependency_exits_2_with_the_invocation_and_no_traceback(self, tmp_path):
        """The guard must be NON-RAISING at import: the shared root guard `exec_module`s this
        file, and a raising import turns that test into an ERROR rather than a run."""
        stub = tmp_path / "yaml.py"
        stub.write_text("raise ModuleNotFoundError('No module named yaml', name='yaml')\n")
        r = subprocess.run(
            [sys.executable, str(SCRIPT), "keyword-map",
             str(FIXTURES / "regulatory-scope-map.valid.yaml")],
            capture_output=True, text=True, cwd=HERE, check=False,
            env={**__import__("os").environ, "PYTHONPATH": str(tmp_path)},
        )
        out = r.stdout + r.stderr
        assert r.returncode == 2, out
        assert "FAIL dependency-missing:" in out
        assert "Traceback" not in out
        assert "--with pyyaml" in out, "the message must carry the working invocation"

    def test_both_subcommands_are_reachable_through_main(self):
        for args in (["keyword-map", str(FIXTURES / "regulatory-scope-map.valid.yaml")],
                     ["search", str(FIXTURES / "search-output.valid.yaml"),
                      "--keyword-map", str(FIXTURES / "regulatory-scope-map.valid.yaml")]):
            r = self._cli(*args)
            assert r.returncode in (0, 1), f"{args} -> {r.returncode}: {r.stdout}{r.stderr}"
            assert "no such subcommand" not in (r.stdout + r.stderr).lower()

    def test_the_exported_constant_exists(self):
        """The shared root guard SKIPS its constant check without this, and a silent skip is a
        green test checking nothing."""
        assert isinstance(V.REQUIRED_CAPABILITY_FIELDS, tuple)
        assert "regulatory.applies" in V.REQUIRED_CAPABILITY_FIELDS


class TestMapRules:
    """The fifteen inherited map rule-ids, plus `sector-verdict-complete`. Each has a negative test
    that FIRES it and a mirror mutated toward the boundary."""

    def test_the_clean_map_is_clean(self, valid_map, registry):
        assert V.validate_keyword_map(valid_map, registry) == []

    @pytest.mark.parametrize("mutate", [
        lambda m: m["meta"].pop("classification"),
        lambda m: m["meta"].update(classification={}),
    ], ids=["absent", "empty"])
    def test_a_map_recording_NO_classification_is_refused(self, mutate, valid_map, registry):
        """The SCHEMA owns it — `required` plus `minProperties: 1` — because that is exactly what a
        shape check can say and a rule restating it would be the unreachable duplicate this module
        deleted four of. Both mutations were legal until the derived sweep found the field loose
        and read by nothing: every sector verdict and every angle verdict is justified against the
        classification, so a map recording none leaves all of them unfalsifiable.
        """
        doc = copy.deepcopy(valid_map)
        mutate(doc)
        assert "schema" in _rules(V.validate_keyword_map(doc, registry))

    def test_ONE_recorded_value_is_enough(self, valid_map, registry):
        """MIRROR at the boundary: `minProperties: 1` is a floor, not a demand for a full
        capability map. A scope handed one value records one."""
        doc = copy.deepcopy(valid_map)
        k = next(iter(doc["meta"]["classification"]))
        doc["meta"]["classification"] = {k: doc["meta"]["classification"][k]}
        assert V.validate_keyword_map(doc, registry) == []

    # ── ids and axes ─────────────────────────────────────────────────────────
    def test_a_group_id_minted_twice_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["groups"].append(copy.deepcopy(doc["groups"][0]))
        assert "group-id-unique" in _rules(V.validate_keyword_map(doc, registry))

    def test_two_groups_of_one_type_with_distinct_ids_and_terms_pass(self, valid_map, registry):
        """MIRROR: the rule keys on the ID. A second group of the same type is legitimate — its
        vocabulary has to differ too, which `term-sited-once` owns."""
        doc = copy.deepcopy(valid_map)
        twin = copy.deepcopy(doc["groups"][0])
        twin["id"] += "-alt"
        twin["canonical"] += " (alt)"
        twin["expansions"] = [e + " alt" for e in twin["expansions"]]
        doc["groups"].append(twin)
        assert V.validate_keyword_map(doc, registry) == []

    def test_an_axis_a_searching_angle_needs_must_be_populated_or_declared_absent(
        self, valid_map, registry
    ):
        doc = copy.deepcopy(valid_map)
        doc["groups"] = [g for g in doc["groups"] if g["type"] != "control-catalog"]
        assert "group-type-accounted" in _rules(V.validate_keyword_map(doc, registry))

    def test_declaring_it_absent_satisfies_the_rule(self, valid_map, registry):
        """MIRROR: an empty axis is legitimate — it has to be a DECLARED emptiness."""
        doc = copy.deepcopy(valid_map)
        doc["groups"] = [g for g in doc["groups"] if g["type"] != "control-catalog"]
        doc["scope_guard"]["absent_types"].append("control-catalog")
        assert V.validate_keyword_map(doc, registry) == []

    def test_an_axis_cannot_be_both_absent_and_populated(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["scope_guard"]["absent_types"].append("instrument")
        assert "group-type-accounted" in _rules(V.validate_keyword_map(doc, registry))

    def test_an_axis_no_HOLDING_angle_searches_may_be_absent_and_unpopulated(
        self, valid_map, registry
    ):
        """MIRROR at the boundary: `platform-role` is searched only by b3, which does not hold for
        this scope. The rule is about axes a SEARCHING angle needs, not every axis in the enum."""
        doc = copy.deepcopy(valid_map)
        assert not any(g["type"] == "platform-role" for g in doc["groups"])
        assert "platform-role" in doc["scope_guard"]["absent_types"]
        assert V.validate_keyword_map(doc, registry) == []

    # ── vocabulary ───────────────────────────────────────────────────────────
    def test_expansions_above_the_cap_fail(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        g = doc["groups"][0]
        g["expansions"] = ["a", "b", "c", "d", "e"]
        g["expansion_cap"] = 2
        assert "expansion-cap" in _rules(V.validate_keyword_map(doc, registry))

    def test_expansions_exactly_at_the_cap_pass(self, valid_map, registry):
        """MIRROR at the boundary: the cap is a ceiling, and equality is legal."""
        doc = copy.deepcopy(valid_map)
        g = doc["groups"][0]
        g["expansions"] = ["alpha term", "beta term"]
        g["expansion_cap"] = 2
        assert V.validate_keyword_map(doc, registry) == []

    @pytest.mark.parametrize("gtype", ["instrument", "sector", "obligation-dimension"])
    def test_a_vocabulary_axis_with_no_expansions_fails(self, gtype, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        next(g for g in doc["groups"] if g["type"] == gtype)["expansions"] = []
        assert "expansion-floor" in _rules(V.validate_keyword_map(doc, registry))

    def test_a_jurisdiction_group_owes_no_expansions(self, valid_map, registry):
        """MIRROR, per-axis: an empty expansion list is legal on an axis whose terms have one
        spelling, and the same emptiness fails on an instrument group. A test that only read the
        fixture would pass with the axis check deleted."""
        doc = copy.deepcopy(valid_map)
        g = next(x for x in doc["groups"] if x["type"] == "jurisdiction")
        g["expansions"] = []
        assert "expansion-floor" not in _clean(V.validate_keyword_map(doc, registry))
        g["type"] = "instrument"
        assert "expansion-floor" in _rules(V.validate_keyword_map(doc, registry))

    @pytest.mark.parametrize("gtype", ["sector", "obligation-dimension"])
    def test_an_ordinary_english_axis_owes_negative_terms(self, gtype, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        next(g for g in doc["groups"] if g["type"] == gtype)["negative_terms"] = []
        assert "negative-terms-required" in _rules(V.validate_keyword_map(doc, registry))

    def test_an_instrument_group_owes_none(self, valid_map, registry):
        """MIRROR at the boundary: an instrument short name is not ordinary English and reaches no
        homonym corpus, so the same emptiness is legal there."""
        doc = copy.deepcopy(valid_map)
        g = next(x for x in doc["groups"] if x["type"] == "instrument")
        g["negative_terms"] = []
        assert "negative-terms-required" not in _clean(V.validate_keyword_map(doc, registry))

    def test_a_term_reaching_two_groups_undeclared_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        first, second = _undeclared_pair(doc)
        second["expansions"] = list(second["expansions"]) + [first["canonical"]]
        second["expansion_cap"] = len(second["expansions"])
        assert "term-sited-once" in _rules(V.validate_keyword_map(doc, registry))

    def test_declaring_the_shared_term_satisfies_the_rule(self, valid_map, registry):
        """MIRROR: the collision is DECLARED, not forbidden — an instrument name can legitimately
        be its own group and another's expansion."""
        doc = copy.deepcopy(valid_map)
        first, second = _undeclared_pair(doc)
        second["expansions"] = list(second["expansions"]) + [first["canonical"]]
        second["expansion_cap"] = len(second["expansions"])
        doc["scope_guard"]["shared_terms"].append(
            {"term": first["canonical"], "groups": [first["id"], second["id"]],
             "owner": first["id"]})
        assert V.validate_keyword_map(doc, registry) == []

    def test_a_declaration_whose_owner_is_outside_the_collision_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        first, second = _undeclared_pair(doc)
        second["expansions"] = list(second["expansions"]) + [first["canonical"]]
        second["expansion_cap"] = len(second["expansions"])
        other = next(g for g in doc["groups"] if g["id"] not in (first["id"], second["id"]))
        doc["scope_guard"]["shared_terms"].append(
            {"term": first["canonical"], "groups": [first["id"], second["id"]],
             "owner": other["id"]})
        assert "term-sited-once" in _rules(V.validate_keyword_map(doc, registry))

    def test_the_collision_folds_case_and_whitespace(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        first, second = _undeclared_pair(doc)
        second["expansions"] = list(second["expansions"]) + [f"  {first['canonical'].upper()} "]
        second["expansion_cap"] = len(second["expansions"])
        assert "term-sited-once" in _rules(V.validate_keyword_map(doc, registry))

    # ── angle verdicts ───────────────────────────────────────────────────────
    @pytest.mark.parametrize("angle_id", ["a1", "b3"])
    def test_deleting_an_angle_verdict_fails_for_BOTH_kinds(self, angle_id, valid_map, registry):
        """EC9, and it names both kinds on purpose: a rule tested only on an always-on angle
        proves nothing about the conditional half of the table."""
        doc = copy.deepcopy(valid_map)
        doc["angle_applicability"] = [
            v for v in doc["angle_applicability"] if v["angle_id"] != angle_id]
        assert "angle-verdict-complete" in _rules(V.validate_keyword_map(doc, registry))

    def test_two_verdicts_for_one_angle_fail(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["angle_applicability"].append(copy.deepcopy(doc["angle_applicability"][0]))
        assert "angle-verdict-unique" in _rules(V.validate_keyword_map(doc, registry))

    def test_a_verdict_on_an_angle_the_registry_does_not_declare_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        v = copy.deepcopy(doc["angle_applicability"][0])
        v["angle_id"] = "b9"
        doc["angle_applicability"].append(v)
        assert "angle-unknown" in _rules(V.validate_keyword_map(doc, registry))

    def test_an_always_on_angle_may_never_be_false(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        next(v for v in doc["angle_applicability"] if v["angle_id"] == "a1")["holds"] = False
        assert "always-on-angle-holds" in _rules(V.validate_keyword_map(doc, registry))

    def test_a_conditional_angle_may_be_false(self, valid_map, registry):
        """MIRROR at the boundary: the same `holds: false` that is a producer error on an
        always-on angle is the ordinary case on a conditional one."""
        doc = copy.deepcopy(valid_map)
        next(v for v in doc["angle_applicability"] if v["angle_id"] == "b4")["holds"] = False
        assert "always-on-angle-holds" not in _clean(V.validate_keyword_map(doc, registry))

    # ── sector receipt ───────────────────────────────────────────────────────
    def test_a_missing_sector_verdict_fails(self, valid_map, registry):
        """L-10: a family silently absent from the receipt is a validator failure, not a
        judgement call."""
        doc = copy.deepcopy(valid_map)
        # Schema-VALID on purpose: still nine rows, still all in the enum. `minItems: 9` and the
        # family enum are the schema's; that nine rows name nine DISTINCT families is this rule's,
        # and nine rows naming eight with one repeated satisfies both schema constraints.
        doc["sector_scoping"][3]["family"] = doc["sector_scoping"][0]["family"]
        found = _rules(V.validate_keyword_map(doc, registry))
        assert "schema" not in found, "the mutation must reach the rule, not stop at the schema"
        assert "sector-verdict-complete" in found

    def test_a_duplicate_sector_verdict_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["sector_scoping"].append(copy.deepcopy(doc["sector_scoping"][0]))
        assert "sector-verdict-complete" in _rules(V.validate_keyword_map(doc, registry))

    def test_all_nine_present_passes_whatever_the_verdicts_say(self, valid_map, registry):
        """MIRROR: the rule is about COVERAGE, not about the answers. A receipt of nine
        `undetermined` is complete — and honest, where nine `does-not-apply` guesses would not be."""
        doc = copy.deepcopy(valid_map)
        for s in doc["sector_scoping"]:
            s["applies"] = "undetermined"
            s["instruments"] = []
        assert "sector-verdict-complete" not in _clean(V.validate_keyword_map(doc, registry))

    # ── probe and sources ────────────────────────────────────────────────────
    def test_a_probe_that_did_not_run_and_says_nothing_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["probe"] = {"ran": False, "note": "   "}
        assert "probe-record" in _rules(V.validate_keyword_map(doc, registry))

    def test_a_probe_that_did_not_run_but_says_why_passes(self, valid_map, registry):
        """MIRROR: `ran: false` is legal. What is not legal is `ran: false` with nothing said."""
        doc = copy.deepcopy(valid_map)
        doc["probe"] = {"ran": False, "note": "Every a1 source was rate-limited at wave 0; the "
                                              "probe is owed and recorded as not run."}
        assert "probe-record" not in _clean(V.validate_keyword_map(doc, registry))

    def test_a_non_clean_sanitization_with_no_cause_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["sources"]["active"][0]["sanitization"] = {"status": "modified", "cause": None}
        assert "sanitization-cause" in _rules(V.validate_keyword_map(doc, registry))

    def test_a_clean_sanitization_owes_no_cause(self, valid_map, registry):
        """MIRROR at the boundary: `clean` is the one status that explains itself."""
        doc = copy.deepcopy(valid_map)
        doc["sources"]["active"][0]["sanitization"] = {"status": "clean", "cause": None}
        assert "sanitization-cause" not in _clean(V.validate_keyword_map(doc, registry))

    def test_an_active_source_the_registry_excludes_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["sources"]["active"].append(
            {"id": "iso", "as_of": "2026-09-02", "access_status": "open",
             "sanitization": {"status": "clean", "cause": None}})
        assert "forbidden-source-not-active" in _rules(V.validate_keyword_map(doc, registry))

    def test_an_active_source_that_is_not_a_registry_row_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["sources"]["active"].append(
            {"id": "some-blog", "as_of": "2026-09-02", "access_status": "open",
             "sanitization": {"status": "clean", "cause": None}})
        assert "source-not-in-registry" in _rules(V.validate_keyword_map(doc, registry))

    def test_a_registry_row_in_neither_list_fails(self, valid_map, registry):
        """Every row is ACCOUNTED FOR: reached, or refused with a cause. A row in neither list is
        a source nobody decided about, and it reads exactly like one that was fine."""
        doc = copy.deepcopy(valid_map)
        doc["sources"]["active"] = doc["sources"]["active"][:-1]
        assert "source-unaccounted" in _rules(V.validate_keyword_map(doc, registry))

    def test_a_row_in_skipped_is_accounted_for(self, valid_map, registry):
        """MIRROR at the boundary: moving a row from active to skipped keeps it accounted."""
        doc = copy.deepcopy(valid_map)
        row = doc["sources"]["active"].pop()
        doc["sources"]["skipped"].append({"id": row["id"], "cause": "HTTP 503 on three attempts."})
        assert "source-unaccounted" not in _clean(V.validate_keyword_map(doc, registry))


def _resync(doc: dict) -> None:
    """Recompute `retrieval_summary` and every cell's `kept` after a mutation.

    Without this a test that moves one thing trips three unrelated rules, and the assertion passes
    for the wrong reason.
    """
    import collections
    rows = collections.Counter()
    for c in doc.get("candidates") or []:
        rows[tuple(c["found_by"].split("/", 1))] += 1
    for u in doc.get("unadmitted") or []:
        rows[tuple(u["found_by"].split("/", 1))] += 1
    for cell in doc.get("coverage") or []:
        if cell["status"] == "reached":
            cell["kept"] = rows.get((cell["group_id"], cell["source_id"]), 0)
    doc["retrieval_summary"]["status_counts"] = dict(
        collections.Counter(c["status"] for c in doc["coverage"]))
    doc["retrieval_summary"]["degraded_sources"] = sorted(
        {c["source_id"] for c in doc["coverage"]
         if c["status"] not in ("reached", "not-attempted")})


class TestTheTwoDimensionalGrid:
    """The owed set is DERIVED from THREE terms, and dropping any one of them is a different bug."""

    def test_the_clean_search_output_is_clean(self, valid_search, valid_map, registry):
        assert V.validate_search(valid_search, valid_map, registry) == []

    def test_an_omitted_owed_pair_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["coverage"] = doc["coverage"][:-1]
        _resync(doc)
        assert "coverage-complete" in _rules(V.validate_search(doc, valid_map, registry))

    def test_the_owed_set_uses_the_ANGLES_OWN_SOURCES(self, valid_search, valid_map, registry):
        """The third term, and the one a paraphrase drops. `a1` searches 5 of the map's 20 active
        sources; against every active source the grid would be 4x20 = 80 instead of 4x5 = 20, and
        a reviewer applying the wrong reading finds 60 missing cells in a correct artifact."""
        angle = next(a for a in registry["angles"] if a["id"] == "a1")
        active = {a["id"] for a in valid_map["sources"]["active"]}
        types = set(angle["applicable_group_types"])
        groups = [g["id"] for g in valid_map["groups"] if g["type"] in types]
        own = [s for s in angle["sources"] if s in active]
        assert len(groups) * len(own) == len(valid_search["coverage"])
        assert len(groups) * len(active) > len(valid_search["coverage"]), (
            "the fixture cannot tell the two readings apart")
        assert V.validate_search(valid_search, valid_map, registry) == []

    def test_the_owed_set_uses_the_ANGLES_APPLICABLE_TYPES(self, valid_search, valid_map, registry):
        """The first term. `a1` searches three axes, not all nine."""
        angle = next(a for a in registry["angles"] if a["id"] == "a1")
        assert set(angle["applicable_group_types"]) < {g["type"] for g in valid_map["groups"]}
        seen = {c["group_id"] for c in valid_search["coverage"]}
        off_axis = {g["id"] for g in valid_map["groups"]
                    if g["type"] not in angle["applicable_group_types"]}
        assert not (seen & off_axis), "a cell keys on a group this angle does not search"

    def test_a_cell_outside_the_owed_set_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        off = next(g["id"] for g in valid_map["groups"] if g["type"] == "control-catalog")
        cell = copy.deepcopy(doc["coverage"][0])
        cell["group_id"] = off
        doc["coverage"].append(cell)
        _resync(doc)
        assert "cell-in-applicable-set" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_duplicate_cell_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["coverage"].append(copy.deepcopy(doc["coverage"][0]))
        _resync(doc)
        assert "cell-pair-unique" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_cell_naming_an_unminted_group_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0]["group_id"] = "not-a-group"
        _resync(doc)
        assert "cell-group-known" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_cell_naming_a_source_the_map_never_activated_fails(
        self, valid_search, valid_map, registry
    ):
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0]["source_id"] = "eba"
        _resync(doc)
        assert "cell-source-known" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_cell_naming_an_EXCLUDED_source_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0]["source_id"] = "iso"
        _resync(doc)
        assert "cell-source-excluded" in _rules(V.validate_search(doc, valid_map, registry))


class TestCountsAndCauses:
    def test_a_reached_cell_owes_its_counts(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0].update(returned=None, kept=None)
        assert "reached-needs-counts" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_non_zero_count_owes_a_frame(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        cell = next(c for c in doc["coverage"] if c["status"] == "reached" and c["returned"])
        cell["count_frame"] = None
        assert "count-frame-required" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_recorded_ZERO_owes_no_frame(self, valid_search, valid_map, registry):
        """MIRROR at the boundary: a reached cell that returned nothing owes no frame, and
        demanding one would push producers toward omitting the cell — the failure the rule exists
        to prevent."""
        doc = copy.deepcopy(valid_search)
        cell = next(c for c in doc["coverage"] if c["status"] == "reached" and c["returned"] == 0)
        assert cell["count_frame"] is None
        assert "count-frame-required" not in _clean(V.validate_search(doc, valid_map, registry))

    def test_an_unreached_cell_owes_a_cause(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        cell = next(c for c in doc["coverage"] if c["status"] == "not-attempted")
        cell["cause"] = "  "
        assert "status-needs-cause" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_reached_cell_owes_none(self, valid_search, valid_map, registry):
        """MIRROR: the zero IS the evidence on a reached cell."""
        doc = copy.deepcopy(valid_search)
        cell = next(c for c in doc["coverage"] if c["status"] == "reached" and c["returned"] == 0)
        assert cell["cause"] is None
        assert "status-needs-cause" not in _clean(V.validate_search(doc, valid_map, registry))

    def test_an_unreached_cell_may_not_carry_a_count(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        cell = next(c for c in doc["coverage"] if c["status"] == "not-attempted")
        cell.update(returned=0, kept=0)
        assert "coverage-unreached-has-count" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_cell_sanitization_with_no_cause_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0]["sanitization"] = {"status": "modified", "cause": None}
        assert "cell-sanitization-cause" in _rules(V.validate_search(doc, valid_map, registry))

    def test_an_absent_cell_sanitization_is_legal(self, valid_search, valid_map, registry):
        """MIRROR: the field is an OVERRIDE, written only where this cell's fetch departed from the
        map's posture. Requiring it on every cell would restate the map on every row."""
        doc = copy.deepcopy(valid_search)
        for c in doc["coverage"]:
            c.pop("sanitization", None)
        assert "cell-sanitization-cause" not in _clean(V.validate_search(doc, valid_map, registry))

    def test_kept_above_returned_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        cell = next(c for c in doc["coverage"] if c["status"] == "reached" and c["returned"])
        cell["kept"] = cell["returned"] + 1
        assert "kept-exceeds-returned" in _rules(V.validate_search(doc, valid_map, registry))

    def test_kept_equal_to_returned_passes(self, valid_search, valid_map, registry):
        """MIRROR at the boundary: carrying everything a cell returned is legal."""
        doc = copy.deepcopy(valid_search)
        # `returned > kept` is a PRECONDITION, not decoration. Selecting on `kept == 1` alone
        # picked a cell the fixture already had at `returned == 1`, so the mutation was a no-op
        # and the assertion was made against the unmutated fixture -- a mirror that never
        # approached the boundary it claims to sit on.
        cell = next(c for c in doc["coverage"]
                    if c["status"] == "reached" and (c["returned"] or 0) > (c["kept"] or 0) > 0)
        before = cell["returned"]
        cell["returned"] = cell["kept"]
        cell["count_frame"] = "One instrument, resolved by identifier."
        assert cell["returned"] != before, "the mutation must change the cell"
        _resync(doc)
        assert "kept-exceeds-returned" not in _clean(V.validate_search(doc, valid_map, registry))

    def test_a_row_citing_an_unreached_cell_fails(self, valid_search, valid_map, registry):
        """Without this a row can name a cell that never ran, and `kept` reconciliation never sees
        it because an unreached cell's kept is null."""
        doc = copy.deepcopy(valid_search)
        dead = next(c for c in doc["coverage"] if c["status"] == "not-attempted")
        doc["candidates"][0]["found_by"] = f"{dead['group_id']}/{dead['source_id']}"
        _resync(doc)
        assert "rows-cite-an-unreached-cell" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_row_citing_a_cell_that_does_not_exist_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["found_by"] = "health/nist-csrc"
        _resync(doc)
        assert "row-cell-unknown" in _rules(V.validate_search(doc, valid_map, registry))


class TestCountsBoundAndCandidates:
    """The remaining twenty search rule-ids."""

    # ── kept reconciles against candidates PLUS unadmitted ───────────────────
    def test_kept_counts_candidates_PLUS_unadmitted(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["unadmitted"] = []
        assert "kept-matches-rows" in _rules(V.validate_search(doc, valid_map, registry))

    def test_dropping_a_candidate_breaks_it_too(self, valid_search, valid_map, registry):
        """MIRROR on the other side of the sum: the rule counts BOTH lists, so removing from
        either must fire it. A rule that only watched `candidates` would pass the first test."""
        doc = copy.deepcopy(valid_search)
        doc["candidates"] = doc["candidates"][:-1]
        assert "kept-matches-rows" in _rules(V.validate_search(doc, valid_map, registry))

    def test_moving_a_row_between_the_lists_keeps_it_balanced(
        self, valid_search, valid_map, registry
    ):
        """MIRROR at the boundary: `kept` counts ROWS, so a row that moves from admitted to
        unadmitted changes neither the cell's kept nor the sum. Under a result-count reading this
        would break, which is exactly why the row reading is the one that holds."""
        doc = copy.deepcopy(valid_search)
        cand = doc["candidates"].pop()
        doc["unadmitted"].append({
            "item_id": cand["item_id"], "found_by": cand["found_by"], "name": cand["name"],
            "locator": cand["locator"], "reason_class": "out-of-scope-for-this-angle",
            "reason": "Reclassified during review; it belongs to another angle's corpus.",
        })
        assert "kept-matches-rows" not in _clean(V.validate_search(doc, valid_map, registry))

    # ── outcome ──────────────────────────────────────────────────────────────
    def test_a_ran_angle_with_no_cells_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["coverage"] = []
        _resync(doc)
        assert "ran-requires-coverage" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_ran_angle_whose_every_cell_was_skipped_fails(self, valid_search, valid_map, registry):
        """`ran` means it searched. An output whose every cell is `not-attempted` did not."""
        doc = copy.deepcopy(valid_search)
        doc["candidates"], doc["unadmitted"] = [], []
        for c in doc["coverage"]:
            c.update(status="not-attempted", returned=None, kept=None, count_frame=None,
                     cause="(not attempted) the whole wave was deferred")
        _resync(doc)
        assert "ran-attempted-nothing" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_not_run_angle_with_cells_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["outcome"] = "not_run"
        doc["not_run"] = {"map_verdict": "b3 does not hold: business.platform.type is none"}
        assert "unrun-angle-has-cells" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_not_run_angle_with_candidates_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["outcome"] = "not_run"
        doc["not_run"] = {"map_verdict": "b3 does not hold"}
        doc["coverage"] = []
        assert "unrun-angle-has-candidates" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_not_run_angle_that_is_EMPTY_passes(self, valid_search, valid_map, registry):
        """MIRROR: NOTHING is owed. Reading a coverage rule against a `not_run` artifact would
        revise work the other half of the gate certified."""
        doc = copy.deepcopy(valid_search)
        doc.update(outcome="not_run", coverage=[], candidates=[], unadmitted=[], bound=None,
                   retrieval_summary=None,
                   not_run={"map_verdict": "a1 holds for every scope; this is the shape test"})
        assert V.validate_search(doc, valid_map, registry) == []

    def test_a_not_run_angle_that_says_WHY_is_required(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc.update(outcome="not_run", coverage=[], candidates=[], unadmitted=[], bound=None,
                   retrieval_summary=None)
        assert "outcome-block-required" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_vacated_angle_with_candidates_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["outcome"] = "vacated"
        doc["vacated"] = {"cause": "Every source in this angle's set was rate-limited."}
        assert "vacated-not-empty" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_vacated_angle_owes_cells_and_a_cause(self, valid_search, valid_map, registry):
        """MIRROR at the boundary: `vacated` owes CELLS -- that is what distinguishes it from
        `not_run`. An empty candidate list is not a gap there."""
        doc = copy.deepcopy(valid_search)
        doc.update(outcome="vacated", candidates=[], unadmitted=[],
                   vacated={"cause": "Every source in this angle's set was rate-limited."})
        for c in doc["coverage"]:
            c.update(status="rate-limited", returned=None, kept=None, count_frame=None,
                     cause="HTTP 429 with a Retry-After of 3600 on every attempt.")
        _resync(doc)
        assert V.validate_search(doc, valid_map, registry) == []

    def test_a_vacated_angle_with_ONLY_unadmitted_rows_fails(
        self, valid_search, valid_map, registry
    ):
        """The other arm of the same `or`, and the one the test above cannot reach. Guarding
        `candidates` alone leaves `unadmitted` unguarded -- and an angle that recorded rejects
        recorded a search, which is exactly what `vacated` denies happened."""
        doc = copy.deepcopy(valid_search)
        doc.update(outcome="vacated", candidates=[],
                   vacated={"cause": "Every source in this angle\'s set was rate-limited."})
        assert doc["unadmitted"], "the fixture must carry rejects for this to mutate anything"
        assert "vacated-not-empty" in _rules(V.validate_search(doc, valid_map, registry))

    @pytest.mark.parametrize("block", [None, {"cause": "   "}], ids=["absent", "whitespace"])
    def test_a_vacated_angle_with_no_STATED_cause_fails(
        self, block, valid_search, valid_map, registry
    ):
        """Two ways to have no cause and one rule. `minLength: 1` is the schema\'s, so a blank
        string never reaches here; whitespace passes the schema and is still not a reason, and
        that gap is the whole of what this rule adds over the shape check.
        """
        doc = copy.deepcopy(valid_search)
        doc.update(outcome="vacated", candidates=[], unadmitted=[], vacated=block)
        found = _rules(V.validate_search(doc, valid_map, registry))
        assert "schema" not in found, "the mutation must reach the rule, not stop at the schema"
        assert "outcome-block-required" in found

    # ── the summary ──────────────────────────────────────────────────────────
    def test_dropping_the_summary_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc.pop("retrieval_summary")
        assert "summary-required" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_disagreeing_summary_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["retrieval_summary"]["status_counts"] = {"reached": 99}
        assert "summary-reconciles" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_degraded_source_must_be_listed(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        cell = next(c for c in doc["coverage"] if c["status"] == "reached")
        cell.update(status="rate-limited", returned=None, kept=None, count_frame=None,
                    cause="HTTP 429, Retry-After 3600.")
        doc["candidates"] = [c for c in doc["candidates"]
                             if c["found_by"] != f"{cell['group_id']}/{cell['source_id']}"]
        doc["unadmitted"] = [u for u in doc["unadmitted"]
                             if u["found_by"] != f"{cell['group_id']}/{cell['source_id']}"]
        _resync(doc)
        doc["retrieval_summary"]["degraded_sources"] = []   # the omission under test
        assert "degraded-source-recorded" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_not_attempted_cell_is_NOT_degraded(self, valid_search, valid_map, registry):
        """MIRROR at the boundary: a recorded CHOICE is not a degradation. Listing it would make
        the degraded list mean 'cells that are not reached', which is a different fact."""
        doc = copy.deepcopy(valid_search)
        assert any(c["status"] == "not-attempted" for c in doc["coverage"])
        assert doc["retrieval_summary"]["degraded_sources"] == []
        assert "degraded-source-recorded" not in _clean(V.validate_search(doc, valid_map, registry))

    # ── bound ────────────────────────────────────────────────────────────────
    def test_a_ran_angle_owes_a_bound(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["bound"] = None
        assert "bound-required" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_cap_that_is_not_the_registrys_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["bound"]["cap"] = 999
        assert "cap-matches-registry" in _rules(V.validate_search(doc, valid_map, registry))

    def test_more_candidates_than_the_cap_fails(self, valid_search, valid_map, registry):
        """Checked UNCONDITIONALLY. Gating it on `hit is False` would let `hit: true` plus a
        dropped_note carry any number past the ceiling."""
        doc = copy.deepcopy(valid_search)
        base = doc["candidates"][0]
        doc["candidates"] = [{**copy.deepcopy(base), "item_id": f"WEB-example-{i}",
                              "id_class": "WEB"} for i in range(doc["bound"]["cap"] + 1)]
        doc["unadmitted"] = []
        _resync(doc)
        assert "cap-respected" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_DECLARED_truncation_does_not_licence_exceeding_the_cap(
        self, valid_search, valid_map, registry
    ):
        """The mutation the unconditional check exists to refuse, and until now only a COMMENT
        said so. Gating `cap-respected` on `hit is False` leaves the test above green -- it never
        sets `hit` -- while `hit: true` plus a dropped_note carries any number past the ceiling.
        Declaring that you stopped at 25 is not permission to return 26.
        """
        doc = copy.deepcopy(valid_search)
        base = doc["candidates"][0]
        doc["candidates"] = [{**copy.deepcopy(base), "item_id": f"WEB-example-{i}",
                              "id_class": "WEB"} for i in range(doc["bound"]["cap"] + 1)]
        doc["unadmitted"] = []
        doc["bound"].update(hit=True, dropped_note="Six instruments below the ordering threshold.")
        _resync(doc)
        found = _rules(V.validate_search(doc, valid_map, registry))
        assert "cap-respected" in found
        # and the two rules that WOULD have absorbed the complaint stay silent, so the finding
        # cannot be mistaken for a bookkeeping quarrel about the note.
        assert "bound-hit-needs-note" not in found and "bound-hit-consistent" not in found

    def test_candidates_exactly_AT_the_cap_pass(self, valid_search, valid_map, registry):
        """MIRROR at the boundary: the cap is a ceiling, so equality is legal. Asserting the
        unmutated fixture would test nothing -- it sits far below."""
        doc = copy.deepcopy(valid_search)
        base = doc["candidates"][0]
        doc["candidates"] = [{**copy.deepcopy(base), "item_id": f"WEB-example-{i}",
                              "id_class": "WEB"} for i in range(doc["bound"]["cap"])]
        doc["unadmitted"] = []
        _resync(doc)
        assert "cap-respected" not in _clean(V.validate_search(doc, valid_map, registry))

    def test_a_hit_cap_owes_a_dropped_note(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["bound"].update(hit=True, dropped_note=None)
        assert "bound-hit-needs-note" in _rules(V.validate_search(doc, valid_map, registry))

    def test_hit_false_with_a_dropped_note_fails(self, valid_search, valid_map, registry):
        """Nothing was dropped, and something is recorded as dropped. The two cannot both hold."""
        doc = copy.deepcopy(valid_search)
        doc["bound"]["dropped_note"] = "Six instruments below the ordering threshold."
        assert "bound-hit-consistent" in _rules(V.validate_search(doc, valid_map, registry))

    # ── candidates ───────────────────────────────────────────────────────────
    def test_a_duplicate_item_id_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["candidates"].append(copy.deepcopy(doc["candidates"][0]))
        _resync(doc)
        assert "candidate-id-unique" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_candidate_naming_an_unminted_group_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["found_by"] = "not-a-group/eu-cellar"
        _resync(doc)
        assert "candidate-group-known" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_candidate_naming_a_minted_group_passes(self, valid_search, valid_map, registry):
        """MIRROR for a membership check: every shipped candidate names a real group, so the rule
        must not fire on the corpus it was written for. A membership check that fires on
        EVERYTHING passes its negative test and fails nothing else."""
        minted = {g["id"] for g in valid_map["groups"]}
        assert all(c["found_by"].split("/")[0] in minted for c in valid_search["candidates"])
        assert "candidate-group-known" not in _clean(
            V.validate_search(valid_search, valid_map, registry))

    def test_an_id_class_disagreeing_with_the_prefix_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["id_class"] = "WEB"
        assert "id-class-shape" in _rules(V.validate_search(doc, valid_map, registry))

    @pytest.mark.parametrize("mutate", [
        lambda c: c.pop("provenance"),
        lambda c: c.update(provenance="45 CFR 164"),
    ], ids=["omitted", "a scalar"])
    def test_a_candidate_carrying_no_provenance_BLOCK_is_refused(
        self, mutate, valid_search, valid_map, registry
    ):
        """The SCHEMA owns it: `required` plus `type: object` is exactly what the deleted
        `candidate-provenance` rule said, and behind the schema's early return the rule could not
        fire anyway. The external identifiers are what make a citation checkable, so their ABSENCE
        is recorded as null rather than omitted -- an omitted block and one saying `celex: null`
        are different claims, and only the second is a record.
        """
        doc = copy.deepcopy(valid_search)
        mutate(doc["candidates"][0])
        assert "schema" in _rules(V.validate_search(doc, valid_map, registry))


class TestIdGrammars:
    """Six externally-owned prefixes, six grammars. `WEB-` has none -- it is the honest fallback
    for an instrument with no registry identity, and C2d's `id-class-shape` checks it against the
    minted id.

    INVENTING A CELEX NUMBER IS THE WORST THING THIS TYPE CAN DO, which is why each grammar is
    tested with a PLAUSIBLE wrong id rather than obvious garbage: `32016R679` is one digit short
    and reads exactly like a real one.
    """

    def _with(self, doc: dict, item_id: str, id_class: str) -> dict:
        d = copy.deepcopy(doc)
        d["candidates"][0]["item_id"] = item_id
        d["candidates"][0]["id_class"] = id_class
        return d

    @pytest.mark.parametrize("bad", ["CELEX-32016R679", "CELEX-2016R0679", "CELEX-32016-0679",
                                     "CELEX-32016r0679"])
    def test_a_plausible_but_wrong_celex_fails(self, bad, valid_search, valid_map, registry):
        doc = self._with(valid_search, bad, "CELEX")
        assert "celex-grammar" in _rules(V.validate_search(doc, valid_map, registry))

    @pytest.mark.parametrize("good", ["CELEX-32016R0679", "CELEX-32024R1689", "CELEX-32011L0024",
                                      "CELEX-62018CJ0311"])
    def test_real_celex_numbers_pass(self, good, valid_search, valid_map, registry):
        """MIRROR, and it carries a CJEU judgment on purpose: case law resolves by CELEX through
        the same channel as legislation, which is why ECLI is not used."""
        doc = self._with(valid_search, good, "CELEX")
        assert "celex-grammar" not in _clean(V.validate_search(doc, valid_map, registry))

    @pytest.mark.parametrize("bad", ["CFR-45", "CFR-451-164", "CFR-45-164-C", "CFR-45.164"])
    def test_a_malformed_cfr_citation_fails(self, bad, valid_search, valid_map, registry):
        doc = self._with(valid_search, bad, "CFR")
        assert "cfr-citation-grammar" in _rules(V.validate_search(doc, valid_map, registry))

    @pytest.mark.parametrize("good", ["CFR-45-164", "CFR-45-160", "CFR-21-11"])
    def test_real_cfr_citations_pass(self, good, valid_search, valid_map, registry):
        doc = self._with(valid_search, good, "CFR")
        assert "cfr-citation-grammar" not in _clean(V.validate_search(doc, valid_map, registry))

    @pytest.mark.parametrize("bad", ["USC-15", "USC-155-6501", "USC-15-6501-a"])
    def test_a_malformed_usc_citation_fails(self, bad, valid_search, valid_map, registry):
        doc = self._with(valid_search, bad, "USC")
        assert "usc-citation-grammar" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_real_usc_citation_passes(self, valid_search, valid_map, registry):
        doc = self._with(valid_search, "USC-15-6501", "USC")
        assert "usc-citation-grammar" not in _clean(V.validate_search(doc, valid_map, registry))

    @pytest.mark.parametrize("bad", ["NIST-800-53r5", "NIST-SP-80053r5", "NIST-SP-800-53-r5"])
    def test_a_malformed_nist_pub_fails(self, bad, valid_search, valid_map, registry):
        doc = self._with(valid_search, bad, "NIST")
        assert "nist-pub-grammar" in _rules(V.validate_search(doc, valid_map, registry))

    @pytest.mark.parametrize("good", ["NIST-SP-800-53r5", "NIST-SP-800-171r3"])
    def test_real_nist_pubs_pass(self, good, valid_search, valid_map, registry):
        doc = self._with(valid_search, good, "NIST")
        assert "nist-pub-grammar" not in _clean(V.validate_search(doc, valid_map, registry))

    @pytest.mark.parametrize("bad", ["ISO-27001", "ISO-IEC-27001", "ISO-IEC-27001-22"])
    def test_a_malformed_iso_number_fails(self, bad, valid_search, valid_map, registry):
        """An ISO number is as inventable as a CELEX one, and its TEXT is unretrievable here -- so
        nothing downstream can catch a wrong one by reading the standard."""
        doc = self._with(valid_search, bad, "ISO")
        assert "iso-number-grammar" in _rules(V.validate_search(doc, valid_map, registry))

    @pytest.mark.parametrize("good", ["ISO-IEC-27001-2022", "ISO-9001-2015", "ISO-IEC-27701-2019"])
    def test_real_iso_numbers_pass(self, good, valid_search, valid_map, registry):
        doc = self._with(valid_search, good, "ISO")
        assert "iso-number-grammar" not in _clean(V.validate_search(doc, valid_map, registry))

    @pytest.mark.parametrize("bad", ["STD-WCAG-2.2", "STD-W3C-WCAG", "STD-w3c-WCAG-2.2"])
    def test_a_malformed_std_slug_fails(self, bad, valid_search, valid_map, registry):
        doc = self._with(valid_search, bad, "STD")
        assert "std-slug-grammar" in _rules(V.validate_search(doc, valid_map, registry))

    @pytest.mark.parametrize("good", ["STD-W3C-WCAG-2.2", "STD-PCI-DSS-4.0"])
    def test_real_std_slugs_pass(self, good, valid_search, valid_map, registry):
        doc = self._with(valid_search, good, "STD")
        assert "std-slug-grammar" not in _clean(V.validate_search(doc, valid_map, registry))

    def test_a_WEB_id_is_governed_by_no_grammar(self, valid_search, valid_map, registry):
        """MIRROR at the boundary: `WEB-` is the honest fallback for an instrument with no registry
        identity. Giving it a grammar would force a shape onto the one class that has none."""
        doc = self._with(valid_search, "WEB-ico-org-uk-uk-idta", "WEB")
        found = _clean(V.validate_search(doc, valid_map, registry))
        assert not [r for r in found if r.endswith("-grammar")]


class TestRecordFilename:
    """MANDATORY, both parts. This type's ids are citations: `ISO/IEC 27001` has a slash,
    `45 CFR 164.312` has spaces and dots. The moment anyone reaches for the citation instead of the
    minted id, the sanitizing branch fires.
    """

    def test_a_filename_safe_id_is_returned_unchanged(self):
        assert V.record_filename("CELEX-32016R0679") == "CELEX-32016R0679"
        assert V.record_filename("CFR-45-164") == "CFR-45-164"

    @pytest.mark.parametrize("raw", ["ISO/IEC 27001", "45 CFR 164.312", "AT-2(2)",
                                     "Directive 2011/24/EU"])
    def test_a_citation_shaped_id_is_sanitized_and_keeps_a_digest(self, raw):
        got = V.record_filename(raw)
        assert "/" not in got and " " not in got, got
        assert re.search(r"--[0-9a-f]{12}$", got), got

    def test_the_digest_covers_the_WHOLE_id(self):
        """Two ids differing only where the sanitizer collapses must not collide. A non-injective
        mapping merges two records into one filename, and the orphan is then re-spawned on every
        wake while looking perfectly valid."""
        assert V.record_filename("ISO/IEC 27001") != V.record_filename("ISO IEC-27001")
        assert V.record_filename("45 CFR 164.312") != V.record_filename("45/CFR/164.312")

    @pytest.mark.parametrize("raw", ["ISO/IEC 27001", "45 CFR 164.312", "AT-2(2)",
                                     "Directive 2011/24/EU", "45/CFR/164.312"])
    def test_the_CROSS_BRANCH_collision_test(self, raw):
        """`f(f(x)) != f(x)` for an id whose SANITIZED form is itself filename-safe.

        That is the whole point and it is easy to get wrong in both directions. It does NOT apply
        to an already-safe id: identity is idempotent by definition, and asserting otherwise tests
        nothing (my first version did, and failed on four correct inputs). It DOES apply here,
        because f(x) ends in `--<digest>` and the identity branch must REFUSE that shape -- without
        that guard the two branches share an output namespace and injectivity is lost. A
        within-branch round-trip is what gave false assurance elsewhere.
        """
        once = V.record_filename(raw)
        assert _HASHED.search(once), f"{raw!r} should take the sanitizing branch, got {once!r}"
        assert V.record_filename(once) != once, f"{raw!r} -> {once!r} is a fixed point"

    @pytest.mark.parametrize("raw", ["CELEX-32016R0679", "CFR-45-164", "USC-15-6501",
                                     "NIST-SP-800-53r5", "STD-W3C-WCAG-2.2",
                                     "WEB-ico-org-uk-uk-idta"])
    def test_an_already_safe_id_IS_idempotent(self, raw):
        """MIRROR, and the boundary the cross-branch test must not be confused with: an id that
        needs no sanitizing is returned unchanged, so applying the function twice is the same as
        once. Requiring `f(f(x)) != f(x)` here would demand the function corrupt a clean id."""
        assert V.record_filename(raw) == raw
        assert V.record_filename(V.record_filename(raw)) == raw

    def test_every_prefix_produces_a_distinct_stem(self):
        ids = ["CELEX-32016R0679", "CFR-45-164", "USC-15-6501", "NIST-SP-800-53r5",
               "ISO-IEC-27001-2022", "STD-W3C-WCAG-2.2", "WEB-ico-org-uk-uk-idta",
               "ISO/IEC 27001", "45 CFR 164.312"]
        stems = [V.record_filename(i) for i in ids]
        assert len(set(stems)) == len(ids), sorted(stems)


class TestAuthorityAndBindingForce:
    """Two fields, and collapsing them is a defect. `authority` is how close to the ISSUING BODY
    the text is; `binding_force` is whether and how it binds. PCI DSS is authority tier 3 and
    binding force `contractual` -- not law, and it binds anyway.

    NEITHER EVER CUTS. The deterministic half of that is the SCHEMA's closed enum on
    `unadmitted[].reason_class`, whose every member is a verifiability class; the semantic half --
    whether a candidate was dropped because its source ranked low -- is a reviewer condition,
    because a validator cannot see a candidate that was never written.
    """

    @pytest.mark.parametrize("mutate", [
        lambda c: c.pop("authority"),
        lambda c: c.update(authority="issuing-body-text"),
        lambda c: c.pop("binding_force"),
        lambda c: c.update(binding_force="advisory"),
        lambda c: c.pop("text_retrievable"),
        lambda c: c.update(text_retrievable="readable"),
    ])
    def test_the_SCHEMA_owns_these_enums(self, mutate, valid_search, valid_map, registry):
        """Deliberately asserted against the SCHEMA, not a rule.

        Rules duplicating these enums existed and became unreachable the moment the schema pass
        returned early — nothing behind that return can fire. They are gone, and their reasoning
        lives in the schema `description`s, which is where a producer reads it. Two statements of
        one enum drift; this is the one that runs.
        """
        doc = copy.deepcopy(valid_search)
        mutate(doc["candidates"][0])
        assert "schema" in _rules(V.validate_search(doc, valid_map, registry))

    def test_the_two_fields_are_INDEPENDENT(self, valid_search, valid_map, registry):
        """MIRROR, and the point of the pair: a tier-3 standard with binding force `contractual`
        is the PCI case and must pass. A rule that derived one from the other would refuse it."""
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0].update(authority="incorporated-standard", binding_force="contractual")
        assert V.validate_search(doc, valid_map, registry) == []

    @pytest.mark.parametrize("klass", ["low-authority", "not-authoritative", "tier-4", ""])
    def test_a_reason_class_outside_the_enum_is_refused(
        self, klass, valid_search, valid_map, registry
    ):
        """The enum's members are ALL verifiability classes, on purpose. A free-prose reason could
        phrase a verifiability failure as 'low authority' and no keyword scan could tell; an enum
        can. The SCHEMA enforces it — note the values here are exactly the dishonest phrasings the
        closed set exists to make unsayable."""
        doc = copy.deepcopy(valid_search)
        doc["unadmitted"][0]["reason_class"] = klass
        assert "schema" in _rules(V.validate_search(doc, valid_map, registry))

    @pytest.mark.parametrize("klass", ["unresolvable-at-issuing-body", "no-stated-version-or-date",
                                       "superseded", "out-of-scope-for-this-angle", "duplicate-of"])
    def test_every_enum_member_passes(self, klass, valid_search, valid_map, registry):
        """MIRROR over the WHOLE enum, not one member: a rule written against one value would let
        the other four through, which is how a partial guard licenses the rest."""
        doc = copy.deepcopy(valid_search)
        doc["unadmitted"][0]["reason_class"] = klass
        assert "schema" not in _clean(V.validate_search(doc, valid_map, registry))


class TestTextRetrievable:
    """Three source classes in this registry cannot be read: ISO texts are paywalled behind a
    challenge, PCI documents 403 from a separate host, and UK primary law refuses non-JS clients.
    `paywalled` and `blocked` are legitimate terminal states -- and a record in one of them may
    NEVER carry a quoted requirement, because a paraphrase of a clause nobody read is exactly the
    fabrication this type must not have.
    """

    @pytest.mark.parametrize("state", ["paywalled", "blocked"])
    def test_an_unretrievable_text_may_not_carry_a_quote(
        self, state, valid_search, valid_map, registry
    ):
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["text_retrievable"] = state
        assert "quote-forbidden-when-unretrievable" in _rules(
            V.validate_search(doc, valid_map, registry))

    def test_summary_only_MAY_carry_a_quote(self, valid_search, valid_map, registry):
        """MIRROR at the boundary: `summary-only` means the CATALOGUE entry was readable even
        though the instrument was not, so quoting the catalogue is honest. Folding it in with
        paywalled/blocked would forbid the one quote that IS available."""
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["text_retrievable"] = "summary-only"
        found = _clean(V.validate_search(doc, valid_map, registry))
        assert "quote-forbidden-when-unretrievable" not in found
        # The mirror is only worth having if the mutation it makes is one a producer could ship.
        # `_clean` proves the SHAPE is legal; this proves nothing else objected either, so the
        # rule really did run on a document it was entitled to fire on and declined.
        assert found == [], found

    def test_full_text_with_a_quote_passes(self, valid_search, valid_map, registry):
        """MIRROR: the ordinary case, and the rule must not fire on the corpus it was written for."""
        assert all(c["text_retrievable"] == "full-text" for c in valid_search["candidates"])
        assert "quote-forbidden-when-unretrievable" not in _clean(
            V.validate_search(valid_search, valid_map, registry))


class TestAnUnretrievableTextIsWRITABLE:
    """B1, and the defect this class exists for: for the whole first draft it was not.

    `evidence_quote` sat in the candidate `required` array unconditionally, while six prose sites
    across the two packages and `quote-forbidden-when-unretrievable` all said a `paywalled` or
    `blocked` record carries its NUMBER and no quote. All three writings failed -- with a quote the
    rule fired, without it the schema did, with an empty string `minLength` did -- so the three
    unretrievable source classes this registry is built around (ISO behind a challenge, PCI behind
    a 403, UK primary law refusing non-JS clients) had no admissible shape at all.

    It survived every review because BOTH clean fixtures are `full-text` throughout, and the only
    test that touched `text_retrievable` mutated it on a candidate that kept its quote. That is the
    shape of the miss, not just its content: a state no fixture reaches is a state no test reaches.
    """

    @pytest.mark.parametrize("state", ["paywalled", "blocked"])
    def test_a_NUMBER_and_no_quote_is_the_admissible_shape(
        self, state, valid_search, valid_map, registry
    ):
        """The record the prose prescribes, written three ways: the field absent, and explicitly
        null. Both must pass, because a producer reading `carries its NUMBER and no quote` writes
        one or the other."""
        for quote in ("absent", None):
            doc = copy.deepcopy(valid_search)
            cand = doc["candidates"][0]
            cand["text_retrievable"] = state
            cand.pop("evidence_quote") if quote == "absent" else cand.update(evidence_quote=None)
            assert V.validate_search(doc, valid_map, registry) == [], (state, quote)

    @pytest.mark.parametrize("state", ["full-text", "summary-only"])
    def test_a_READABLE_text_still_OWES_its_quote(self, state, valid_search, valid_map, registry):
        """The other direction, and the reason the requirement is conditional rather than dropped.
        A record whose text WAS read and quotes nothing is an unwarranted claim, and making the
        field optional for everyone would have traded one hole for a wider one."""
        for mutate in (lambda c: c.pop("evidence_quote"), lambda c: c.update(evidence_quote=None)):
            doc = copy.deepcopy(valid_search)
            doc["candidates"][0]["text_retrievable"] = state
            mutate(doc["candidates"][0])
            assert "schema" in _rules(V.validate_search(doc, valid_map, registry)), state

    @pytest.mark.parametrize("state", ["paywalled", "blocked"])
    def test_an_unretrievable_text_may_still_not_QUOTE(
        self, state, valid_search, valid_map, registry
    ):
        """The rule and the conditional are two halves of one contract, not a duplicate: the schema
        says the field is owed when the text was read, the rule says it is forbidden when it was
        not, and only together do they leave exactly one legal shape per state."""
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["text_retrievable"] = state
        assert doc["candidates"][0]["evidence_quote"]
        assert "quote-forbidden-when-unretrievable" in _rules(
            V.validate_search(doc, valid_map, registry))

    @pytest.mark.parametrize("kind", ["decision", "judgment"])
    def test_the_instrument_type_enum_carries_the_corpus_b4_and_a1_ACTUALLY_survey(
        self, kind, valid_search, valid_map, registry
    ):
        """B3. b4's whole corpus is Commission decisions -- adequacy decisions, standard-
        contractual-clause implementing decisions -- and a1's includes CJEU judgments. With neither
        in the enum a producer had to mistype them, and the one worked example typed two decisions
        `regulation` against its own verbatim quote in the same block."""
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["instrument_type"] = kind
        assert V.validate_search(doc, valid_map, registry) == []

    def test_the_enum_is_still_CLOSED(self, valid_search, valid_map, registry):
        """MIRROR on the widening: adding two members must not turn the field into free text."""
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["instrument_type"] = "adequacy-decision"
        assert "schema" in _rules(V.validate_search(doc, valid_map, registry))


class TestOrderingMatchesTheRegistry:
    """I14. `bound.cap` was checked against the registry verbatim and `bound.ordering` -- the field
    a truncation is justified by, and the one `dropped_note` reconciles against -- was free text no
    rule and no reviewer condition ever compared to anything.
    """

    def test_an_ordering_the_angle_never_declared_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["bound"]["ordering"] = "alphabetical by instrument name"
        assert "ordering-matches-registry" in _rules(
            V.validate_search(doc, valid_map, registry))

    def test_the_registrys_own_signal_passes(self, valid_search, valid_map, registry):
        """MIRROR: the shipped exemplar states the signal the registry declares, hyphens and all."""
        angle = next(a for a in registry["angles"] if a["id"] == valid_search["meta"]["angle_id"])
        doc = copy.deepcopy(valid_search)
        doc["bound"]["ordering"] = angle["ordering_signal"]
        assert "ordering-matches-registry" not in _clean(
            V.validate_search(doc, valid_map, registry))

    def test_a_run_MAY_say_more_than_the_signal(self, valid_search, valid_map, registry):
        """MIRROR, and the reason this is containment rather than equality. The registry states a
        signal; a run may record how it applied it. Demanding the exact string would force every
        producer to transcribe a phrase and forbid it from explaining a tie-break."""
        angle = next(a for a in registry["angles"] if a["id"] == valid_search["meta"]["angle_id"])
        doc = copy.deepcopy(valid_search)
        doc["bound"]["ordering"] = (
            f"{angle['ordering_signal']}, with ties broken by CELEX sector")
        assert "ordering-matches-registry" not in _clean(
            V.validate_search(doc, valid_map, registry))

    def test_a_PARTIAL_ordering_fails(self, valid_search, valid_map, registry):
        """The half that makes containment worth having: dropping one leg of a two-leg signal is
        how a run silently reorders. `issuing-body authority` alone is not
        `issuing-body authority, then instrument recency`."""
        doc = copy.deepcopy(valid_search)
        doc["bound"]["ordering"] = "issuing body authority"
        assert "ordering-matches-registry" in _rules(
            V.validate_search(doc, valid_map, registry))


class TestFieldsTheSchemaShapesButCannotCheck:
    """Three fields whose schema `description` states a claim `minLength: 1` cannot enforce, and
    that nothing read until the derived sweep below went looking. `see the register` is a locator
    of length 15; `ecfr-api` is a fallback_used of length 8; a candidate with no issuing body is
    one L-7 refuses and the schema admits.
    """

    @pytest.mark.parametrize("loc", ["see the register", "www.ecfr.gov/title-45", "/title-45",
                                     "ftp://example.org/x"])
    def test_a_locator_that_is_not_an_absolute_http_url_fails(
        self, loc, valid_search, valid_map, registry
    ):
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["locator"] = loc
        assert "locator-resolvable" in _rules(V.validate_search(doc, valid_map, registry))

    @pytest.mark.parametrize("loc", ["http://publications.europa.eu/resource/celex/32016R0679",
                                     "https://www.ecfr.gov/api/versioner/v1/full/2026-01-01/x.xml"])
    def test_both_http_schemes_pass(self, loc, valid_search, valid_map, registry):
        """MIRROR over BOTH schemes: this registry resolves Cellar over plain http and eCFR over
        https, and a rule written for one would refuse half the corpus."""
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["locator"] = loc
        assert "locator-resolvable" not in _clean(V.validate_search(doc, valid_map, registry))

    @pytest.mark.parametrize("eli", ["eli/reg/2016/679/oj", "data.europa.eu/eli/reg/2016/679/oj"])
    def test_an_ELI_that_does_not_RESOLVE_fails(self, eli, valid_search, valid_map, registry):
        """Being resolvable is the whole of what distinguishes an ELI from the CELEX number beside
        it. A path fragment is an ELI-shaped string and not an ELI."""
        doc = copy.deepcopy(valid_search)
        cand = next(c for c in doc["candidates"] if c["provenance"]["eli"])
        cand["provenance"]["eli"] = eli
        assert "locator-resolvable" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_NULL_eli_is_legal(self, valid_search, valid_map, registry):
        """MIRROR: three of the six id classes have no ELI at all, and demanding one would invent
        a European identifier for a CFR part."""
        doc = copy.deepcopy(valid_search)
        assert any(c["provenance"]["eli"] is None for c in doc["candidates"])
        assert "locator-resolvable" not in _clean(
            V.validate_search(doc, valid_map, registry))

    @pytest.mark.parametrize("body", [None, "", "   "])
    def test_an_admitted_candidate_with_no_issuing_body_fails(
        self, body, valid_search, valid_map, registry
    ):
        """L-7 refuses admission on whether the instrument resolves at a NAMED issuing body. The
        schema types the field nullable, so without this rule a row that fails the ladder's own
        test sits among the candidates."""
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["issuing_body"] = body
        assert "issuing-body-required" in _rules(V.validate_search(doc, valid_map, registry))

    def test_an_UNADMITTED_row_owes_no_issuing_body(self, valid_search, valid_map, registry):
        """MIRROR, and the point of the rule: not naming one is the REASON a row is unadmitted.
        Applying L-7 to the rejects would refuse the record of the rejection."""
        doc = copy.deepcopy(valid_search)
        assert not any(u.get("issuing_body") for u in doc["unadmitted"])
        assert "issuing-body-required" not in _clean(
            V.validate_search(doc, valid_map, registry))

    @pytest.mark.parametrize("used", ["ecfr-api", "angle:", "row:", "fallback", "angle-a1"])
    def test_a_fallback_used_with_no_ROUTE_prefix_fails(
        self, used, valid_search, valid_map, registry
    ):
        """`angle:<id>` and `row:<id>` are different channels -- the registry declares a fallback
        on each angle AND on each source row -- so a bare id cannot say which was walked."""
        doc = copy.deepcopy(valid_search)
        cell = next(c for c in doc["coverage"] if c["status"] == "reached")
        cell["fallback_used"] = used
        assert "fallback-used-shape" in _rules(V.validate_search(doc, valid_map, registry))

    @pytest.mark.parametrize("used", ["angle:a99", "row:a-source-that-was-never-a-row"])
    def test_a_well_shaped_fallback_naming_NOTHING_fails(
        self, used, valid_search, valid_map, registry
    ):
        """The shape is the cheap half. A route recorded against a row the registry does not have
        is a channel nobody can check was taken."""
        doc = copy.deepcopy(valid_search)
        cell = next(c for c in doc["coverage"] if c["status"] == "reached")
        cell["fallback_used"] = used
        found = _rules(V.validate_search(doc, valid_map, registry))
        assert "fallback-used-unknown" in found
        assert "fallback-used-shape" not in found

    def test_a_REAL_route_on_each_side_passes(self, valid_search, valid_map, registry):
        """MIRROR on both arms of the branch. Resolving an angle id against the SOURCE table (or
        the reverse) would refuse every honest record, and one arm alone cannot show that."""
        doc = copy.deepcopy(valid_search)
        reached = [c for c in doc["coverage"] if c["status"] == "reached"]
        reached[0]["fallback_used"] = f"angle:{doc['meta']['angle_id']}"
        reached[1]["fallback_used"] = f"row:{registry['sources'][0]['id']}"
        found = _clean(V.validate_search(doc, valid_map, registry))
        assert "fallback-used-shape" not in found and "fallback-used-unknown" not in found

    def test_no_fallback_used_at_all_is_legal(self, valid_search, valid_map, registry):
        """MIRROR: the ordinary case. Most cells reach their first channel, and a rule that
        demanded the field would force a fabricated route onto every one of them."""
        assert not any(c.get("fallback_used") for c in valid_search["coverage"])
        assert "fallback-used-shape" not in _clean(
            V.validate_search(valid_search, valid_map, registry))


class TestProvenanceAgreesWithTheId:
    """The id and the external identifier are two spellings of ONE instrument, transcribed from
    the same document at different moments. This build shipped a fixture where they disagreed --
    a part-160 row carrying part-164 text -- and every grammar rule passed it, because each one
    checked a spelling against itself.
    """

    def test_a_CELEX_that_is_not_the_ids_CELEX_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        cand = next(c for c in doc["candidates"] if c["id_class"] == "CELEX")
        cand["provenance"]["celex"] = "32011L0024"
        assert cand["item_id"] != "CELEX-32011L0024"
        assert "provenance-matches-id" in _rules(V.validate_search(doc, valid_map, registry))

    @pytest.mark.parametrize("cite", ["45 CFR 160", "42 CFR 164", "45 CFR 1640", "part 164"])
    def test_a_CFR_citation_naming_another_title_or_part_fails(
        self, cite, valid_search, valid_map, registry
    ):
        """All four disagree with `CFR-45-164` in a different way: the part, the title, a part it
        is a prefix of, and a citation with no title at all."""
        doc = copy.deepcopy(valid_search)
        cand = next(c for c in doc["candidates"] if c["item_id"] == "CFR-45-164")
        cand["provenance"]["cfr_citation"] = cite
        assert "provenance-matches-id" in _rules(V.validate_search(doc, valid_map, registry))

    @pytest.mark.parametrize("cite", ["45 CFR 164", "45 CFR 164 subpart C",
                                      "45 CFR 164.308(a)(1)(i)"])
    def test_a_citation_carrying_a_SUBPART_or_SECTION_passes(
        self, cite, valid_search, valid_map, registry
    ):
        """MIRROR, and the reason only the title and part are compared: the field is the citation
        AS WRITTEN, so it carries a depth the id never does. A rule tight enough to demand an
        exact match would refuse the most precise citation in the corpus."""
        doc = copy.deepcopy(valid_search)
        cand = next(c for c in doc["candidates"] if c["item_id"] == "CFR-45-164")
        cand["provenance"]["cfr_citation"] = cite
        assert "provenance-matches-id" not in _clean(
            V.validate_search(doc, valid_map, registry))

    def test_an_ABSENT_identifier_is_not_a_disagreement(self, valid_search, valid_map, registry):
        """MIRROR at the boundary: `null` means the instrument has no such identifier, which is
        the ordinary case for three of the six classes. Reading absence as disagreement would
        refuse every instrument that carries only one."""
        doc = copy.deepcopy(valid_search)
        for c in doc["candidates"]:
            c["provenance"] = dict.fromkeys(c["provenance"], None)
        assert "provenance-matches-id" not in _clean(
            V.validate_search(doc, valid_map, registry))


class TestControlIdGrammar:
    """Branches PER CATALOG. A blanket OSCAL lowercase-dotted rule would refuse every WCAG success
    criterion and every PCI requirement number -- two of the eight angles' own vocabularies.
    """

    def test_a_nist_control_id_in_prose_casing_fails(self, valid_search, valid_map, registry):
        """`AT-2(2)` and `at-2.2` are the same control under two spellings, and mixing them
        silently splits a merge group in two."""
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["control_ids"] = ["AT-2(2)"]
        assert "control-id-grammar" in _rules(V.validate_search(doc, valid_map, registry))

    @pytest.mark.parametrize("cid", ["ac-1", "at-2.2", "sc-13"])
    def test_oscal_lowercase_dotted_passes(self, cid, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["control_ids"] = [cid]
        assert "control-id-grammar" not in _clean(V.validate_search(doc, valid_map, registry))

    @pytest.mark.parametrize("cid", ["1.4.3", "2.4.7", "4.1.2"])
    def test_a_WCAG_success_criterion_passes(self, cid, valid_search, valid_map, registry):
        """MIRROR, and the reason the rule branches: a success-criterion number is its own grammar
        and would be refused by the OSCAL pattern."""
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0].update(control_ids=[cid], control_vocabulary="wcag")
        assert "control-id-grammar" not in _clean(V.validate_search(doc, valid_map, registry))

    @pytest.mark.parametrize("cid", ["3.2.1", "12.10.1"])
    def test_a_PCI_requirement_number_passes(self, cid, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0].update(control_ids=[cid], control_vocabulary="pci")
        assert "control-id-grammar" not in _clean(V.validate_search(doc, valid_map, registry))

    @pytest.mark.parametrize("cid", ["1", "1.2.3.4"])
    def test_a_PCI_shaped_id_under_WCAG_fails(self, cid, valid_search, valid_map, registry):
        """The pair that separates the two NUMERIC grammars, and the reason the mirrors above are
        not enough on their own: `1.4.3` satisfies the PCI pattern as well as the WCAG one, so
        swapping one branch for the other survives every mirror. A success criterion is
        `<principle>.<guideline>.<criterion>` -- never bare, never four deep.
        """
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0].update(control_ids=[cid], control_vocabulary="wcag")
        assert "control-id-grammar" in _rules(V.validate_search(doc, valid_map, registry))

    @pytest.mark.parametrize("cid", ["1", "1.2.3.4"])
    def test_the_same_ids_are_LEGAL_under_PCI(self, cid, valid_search, valid_map, registry):
        """The other half of that pair. PCI numbers a whole requirement (`1`) and sub-divides four
        deep; borrowing WCAG's pattern for it would refuse both."""
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0].update(control_ids=[cid], control_vocabulary="pci")
        assert "control-id-grammar" not in _clean(V.validate_search(doc, valid_map, registry))

    @pytest.mark.parametrize("cid", ["1.2.3.4.5", "AT-2(2)"])
    def test_a_PCI_id_outside_its_own_grammar_fails(self, cid, valid_search, valid_map, registry):
        """PCI is the LOOSEST of the three, and a branch that accepted everything would be
        indistinguishable from no branch at all."""
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0].update(control_ids=[cid], control_vocabulary="pci")
        assert "control-id-grammar" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_candidate_with_no_control_ids_is_legal(self, valid_search, valid_map, registry):
        """MIRROR: most instruments carry none. The field is for the ones law incorporates by
        reference, and requiring it everywhere would invent a control for a directive."""
        assert not any("control_ids" in c for c in valid_search["candidates"])
        assert "control-id-grammar" not in _clean(
            V.validate_search(valid_search, valid_map, registry))


class TestTheSuiteGuardsItself:
    """EC2 and the AST guard. Two sweeps that check the TESTS and the CODE rather than an artifact,
    because a rule with a negative test and no mirror reads as covered and is not.
    """

    _SRC = property(lambda self: SCRIPT.read_text())

    @property
    def _TESTS(self) -> str:
        """This module with its DOCSTRINGS REMOVED.

        A sweep that scans its own prose finds its own examples. This one matched the sentence
        describing its pattern and reported `rule` as a phantom -- the third time in this build a
        guard has matched its own text, after the retracted-claims mask and the plan's dependency
        extractor. Stripping docstrings is the structural fix: a guard reads CODE, and prose about
        a guard is not an instance of what it guards.
        """
        import ast

        src = Path(__file__).read_text()
        tree = ast.parse(src)
        spans: list[tuple[int, int]] = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                body = getattr(node, "body", [])
                if (body and isinstance(body[0], ast.Expr)
                        and isinstance(body[0].value, ast.Constant)
                        and isinstance(body[0].value.value, str)):
                    spans.append((body[0].lineno, body[0].end_lineno))
        drop = {n for lo, hi in spans for n in range(lo, hi + 1)}
        return "\n".join(line for i, line in enumerate(src.splitlines(), 1) if i not in drop)

    def test_the_docstring_stripper_actually_strips(self):
        """Both directions: the prose is gone and the code is not. A stripper that removed
        everything would make every sweep above vacuously green.

        Both probes are DERIVED. Writing the prose probe as a literal put it in this assertion's
        own source, where the stripper correctly leaves it -- so the test asserted something that
        could never hold. That is the same self-reference the stripper exists to fix, one level up.
        """
        code = self._TESTS
        doc = (type(self)._mirrored.__doc__ or "").strip().splitlines()[0]
        assert doc and doc not in code, f"docstrings survived the strip: {doc!r}"
        probe = next(ln.strip() for ln in Path(__file__).read_text().splitlines()
                     if ln.strip().startswith('assert "cap-respected" not in _clean'))
        assert probe in code, "code was stripped along with prose"

    def _shipped_rules(self) -> set[str]:
        """Literal `_fail("id", ...)` sites UNION the ids emitted through a lookup table.

        Six grammar rules are raised as `_fail(rule, ...)` where `rule` comes from `ID_GRAMMARS`,
        and a source regex cannot see them. A sweep that missed them would call six real rules
        phantoms and, worse, would never notice if their mirrors disappeared.
        """
        literal = set(re.findall(r'_fail\(\s*"([a-z0-9-]+)"', self._SRC))
        via_table = {rule for rule, _ in V.ID_GRAMMARS.values()}
        assert via_table - literal, "ID_GRAMMARS no longer emits any rule the regex misses -- if "\
                                    "the tables were inlined, simplify this method"
        return literal | via_table

    def _negatives(self) -> set[str]:
        """Rules some test asserts FIRE."""
        return set(re.findall(r'assert\s+"([a-z0-9-]+)"\s+in\s+_rules', self._TESTS))

    def _mirrored(self) -> set[str]:
        """Rules an explicit `assert "rule" not in _clean(...)` proves do not fire on correct input.

        NARROW ONLY, and that is a correction. An earlier version also credited every `== []`
        assertion on a clean artifact — by unioning in the whole shipped rule set — which made
        `negatives - mirrored` empty by construction. The test built on it could not fail, and its
        failure message named something the computation could not produce. A guard that cannot fail
        is worse than no guard: it occupies the place where a real one would go.

        The clean-artifact assertions still matter and still run; they are simply not a substitute
        for a boundary mirror, because a fixture sitting far from a threshold cannot exercise it.
        """
        return set(re.findall(r'assert\s+"([a-z0-9-]+)"\s+not\s+in\s+_clean', self._TESTS))

    def test_every_negative_names_a_rule_that_EXISTS(self):
        """A test asserting a rule id the validator never emits passes forever and guards nothing:
        the id simply never appears in the findings."""
        phantom = self._negatives() - self._shipped_rules()
        assert not phantom, f"tests assert rule ids the validator does not emit: {sorted(phantom)}"

    def test_every_mirror_names_a_rule_that_EXISTS(self):
        phantom = self._mirrored() - self._shipped_rules()
        assert not phantom, f"mirrors name rule ids the validator does not emit: {sorted(phantom)}"

    def test_the_MEMBERSHIP_and_THRESHOLD_rules_carry_the_NARROW_mirror(self):
        """The broad `== []` form is credited above, and for most rules it is enough. It is NOT
        enough where the live risk is a rule that fires on everything -- a membership check or a
        threshold -- because those are exactly the rules a clean fixture sitting far from the
        boundary cannot exercise. Each of these carries an explicit `not in _clean`.
        """
        narrow = set(re.findall(r'assert\s+"([a-z0-9-]+)"\s+not\s+in\s+_clean', self._TESTS))
        need = {
            "cap-respected", "kept-exceeds-returned", "expansion-floor",
            "negative-terms-required", "count-frame-required", "status-needs-cause",
            "candidate-group-known", "always-on-angle-holds", "cell-sanitization-cause",
            "sanitization-cause", "probe-record", "source-unaccounted", "probe-method-shape",
            "fallback-cycle", "control-id-grammar",
            "quote-forbidden-when-unretrievable", "sector-verdict-complete", "kept-matches-rows",
        }
        assert need <= narrow, f"boundary-sensitive rules with no explicit mirror: {sorted(need - narrow)}"

    def test_the_sweep_is_actually_looking_at_something(self):
        """A derived guard that matches nothing is green and worthless."""
        assert len(self._shipped_rules()) >= 60
        assert len(self._negatives()) >= 40
        assert len(self._mirrored()) >= 15, "the narrow-mirror count collapsed"

    def test_no_unreachable_code_in_the_validator(self):
        """A rule appended after a `return` never runs, and the clean fixture passes either way.

        This shipped in a sibling: the whole candidate/kept/bound half of a validator sat below an
        early return and the suite was green, because every test that would have caught it asserted
        a clean artifact stays clean.
        """
        import ast

        dead: list[str] = []

        def scan(body: list[ast.stmt], where: str) -> None:
            for i, node in enumerate(body):
                if isinstance(node, (ast.Return, ast.Raise, ast.Continue, ast.Break)):
                    if i + 1 < len(body):
                        dead.append(f"{where}: line {body[i + 1].lineno}")
                for attr in ("body", "orelse", "finalbody"):
                    inner = getattr(node, attr, None)
                    if isinstance(inner, list) and inner and isinstance(inner[0], ast.stmt):
                        scan(inner, where)
                for handler in getattr(node, "handlers", []) or []:
                    scan(handler.body, where)

        tree = ast.parse(self._SRC)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                scan(node.body, node.name)
        assert not dead, f"statements after an unconditional exit: {dead}"


class TestAngleReferences:
    """One file per registry angle, and the check runs in BOTH directions.

    A one-directional check on a two-directional property reads as covered and is not: every
    angle's sources resolving says nothing about a registry row that no angle reaches, and a row
    nobody searches is a source shipped and unused.
    """

    ANGLES = PACKAGE / "references" / "angles"

    def _files(self) -> dict[str, str]:
        return {p.stem: p.read_text() for p in self.ANGLES.glob("*.md")}

    def test_every_registry_angle_has_a_reference(self, registry):
        """All eight ship in wave 1, because a map must give a verdict on every one -- including
        the ones that will not hold for a given scope."""
        declared = {a["id"] for a in registry["angles"]}
        assert set(self._files()) == declared, (
            f"missing: {sorted(declared - set(self._files()))}, "
            f"orphaned: {sorted(set(self._files()) - declared)}")

    def test_every_reference_states_its_cap_and_ordering(self, registry):
        """A cap with no ordering cannot show what a truncation dropped."""
        for a in registry["angles"]:
            text = self._files()[a["id"]]
            assert f"**Cap:** {a['cap']}" in text, f"{a['id']}: cap not stated or disagrees"
            assert "**ordering:**" in text, f"{a['id']}: no ordering"

    def test_every_reference_lists_the_registrys_sources(self, registry):
        """Direction one: the file agrees with the registry."""
        for a in registry["angles"]:
            text = self._files()[a["id"]]
            for sid in a["sources"]:
                assert f"`{sid}`" in text, f"{a['id']}: reference omits source {sid!r}"

    def test_every_angle_source_resolves_to_a_registry_row(self, registry):
        rows = {s["id"] for s in registry["sources"]}
        for a in registry["angles"]:
            unknown = [s for s in a["sources"] if s not in rows]
            assert not unknown, f"{a['id']} names sources that are not rows: {unknown}"

    def test_every_registry_SOURCE_is_reached_by_some_angle(self, registry):
        """Direction two -- the MIRROR, and the half a one-directional check misses. A row no angle
        searches and no chain falls back to is a source shipped and unused, which reads exactly
        like one that is covered."""
        rows = {s["id"]: s for s in registry["sources"]}
        searched = {s for a in registry["angles"] for s in a["sources"]}
        reached = set(searched)
        changed = True
        while changed:
            changed = False
            for rid in list(reached):
                nxt = rows.get(rid, {}).get("fallback")
                if isinstance(nxt, str) and nxt != rid and nxt not in reached:
                    reached.add(nxt)
                    changed = True
        assert set(rows) == reached, f"registry rows no angle can reach: {sorted(set(rows) - reached)}"

    def test_no_reference_names_an_EXCLUDED_source_as_one_of_its_own(self, registry):
        """An excluded row may be NAMED -- several references explain why a channel is gone, and
        that is worth saying. What it may not be is one of the angle's sources."""
        excluded = {e["id"] for e in registry["excluded"]}
        for a in registry["angles"]:
            bad = [s for s in a["sources"] if s in excluded]
            assert not bad, f"{a['id']} lists excluded sources: {bad}"

    def test_every_conditional_reference_argues_it_is_not_tautological(self, registry):
        """#53: a conditional angle whose predicate the type trigger already entails is an
        always-on angle with extra machinery, and the argument has to be written down where the
        next author will meet it."""
        for a in registry["angles"]:
            if a["trigger"] == "conditional":
                assert "tautolog" in self._files()[a["id"]].lower(), (
                    f"{a['id']} is conditional and its reference does not argue non-tautology")


class TestTheGuidesWorkedExample:
    """C4's exit. A guide's example is the thing a producer copies, so it has to be a COMPLETE
    artifact that passes the gate -- not an illustrative fragment. An example that would fail the
    validator teaches the shape that fails it.
    """

    GUIDE = PACKAGE / "references" / "search-output-guide.md"

    def _example(self) -> dict:
        blocks = re.findall(r"```yaml\n(.*?)```", self.GUIDE.read_text(), re.S)
        # Selected by CONTENT, not by position: an added snippet earlier in the file would silently
        # move blocks[0] and this test would then validate the wrong thing.
        full = [b for b in blocks if "schema_version" in b and "coverage:" in b]
        assert len(full) == 1, f"expected one complete example, found {len(full)}"
        return yaml.safe_load(full[0])

    def test_the_example_validates_against_the_SCHEMA(self):
        import json
        import jsonschema
        schema = json.loads((PACKAGE / "schemas" / "search-output.schema.json").read_text())
        jsonschema.Draft202012Validator(schema).validate(self._example())

    def test_the_example_passes_the_GATE_against_the_shipped_clean_map(
        self, valid_map, registry
    ):
        assert V.validate_search(self._example(), valid_map, registry) == []

    def test_the_example_quotes_only_what_its_MECHANISM_returns(self):
        """b4 resolves by identifier. A quote attributed to a rendered page the angle never fetches
        would teach a producer to spend five times the budget for weaker evidence -- and it is
        exactly the contradiction a sibling shipped, where the mandated endpoint returned no prose
        and the worked example quoted prose anyway."""
        ex = self._example()
        for cand in ex["candidates"]:
            assert cand["locator"].startswith("http://publications.europa.eu/resource/celex/"), (
                f"{cand['item_id']}: locator is not the resolver this angle uses")
        queried = {q for c in ex["coverage"] for q in c["queries"]}
        for cand in ex["candidates"]:
            assert any(cand["provenance"]["celex"] in q for q in queried), (
                f"{cand['item_id']}: quoted from a document no recorded query fetched")

    def test_the_example_exercises_BOTH_quote_forms(self):
        """One prose quote and one field-value quote, on purpose. A guide showing only prose
        teaches that a field value is second-class, which on an identifier resolver is backwards."""
        quotes = [c["evidence_quote"] for c in self._example()["candidates"]]
        assert any(q.strip().startswith('"') for q in quotes), "no verbatim prose quote"
        assert any(":" in q and not q.strip().startswith('"') for q in quotes), (
            "no field-value quote")


class TestTheReferencesShip:
    """C4's other half. The exit check named every part rather than one, because a task whose
    check covers a third of its deliverables reports done for the other two."""

    @pytest.mark.parametrize("name", ["sources.md", "absent-input-policy.md",
                                      "regulatory-scope-map-guide.md", "search-output-guide.md"])
    def test_the_reference_exists_and_is_substantive(self, name):
        p = PACKAGE / "references" / name
        assert p.exists(), f"{name} does not ship"
        assert len(p.read_text().split()) > 200, f"{name} is a stub"

    @pytest.mark.parametrize("name", ["validate_regulatory_prior_art.py.validation.md",
                                      "test_validate_regulatory_prior_art.py.validation.md"])
    def test_the_validation_sidecar_exists(self, name):
        p = HERE / name
        assert p.exists(), f"{name} does not ship"
        assert len(p.read_text().split()) > 80, f"{name} is a stub"


SKILL = PACKAGE / "SKILL.md"


class TestProducerSkill:
    """C5. The producer states every duty ITSELF -- and that is a decision with two shipped
    precedents pointing opposite ways, so it is proven by grep rather than asserted in prose.
    """

    def _frontmatter(self) -> dict:
        return yaml.safe_load(SKILL.read_text().split("---", 2)[1])

    def test_the_description_fits_the_platform_cap(self):
        assert len(self._frontmatter()["description"]) <= 1024

    def test_the_skill_is_SELF_SUFFICIENT(self):
        """BOTH sibling phrasings are checked, not one.

        Four shipped producers say some form of "the conditions win"; one says the conditions are
        "the single source of the quality bar"; the most recent reversed both after a cold agent
        could not read the conditions file at all. A guard written against one phrasing licenses
        the other -- so neither may appear here.
        """
        text = SKILL.read_text()
        assert "single source of the quality bar" not in text
        assert "the conditions win" not in text
        assert "states every duty itself" in text.lower() or "states every duty" in text.lower()

    @pytest.mark.parametrize("field", [
        "sector_scoping", "scope_guard.shared_terms", "angle_applicability", "meta.classification",
        "sources.active", "sources.skipped", "expansion_cap", "negative_terms",
        "found_by", "authority", "binding_force", "text_retrievable", "reason_class",
        "count_frame", "kept", "bound", "retrieval_summary", "degraded_sources",
        "coverage[].sanitization", "not_run.map_verdict", "outcome", "instrument_type",
    ])
    def test_every_field_the_producer_writes_has_a_procedure_step(self, field):
        """#60's inverse in the prose direction: a field the producer must write and no step
        mentions is a field the producer will not write."""
        leaf = field.split(".")[-1].replace("[]", "")
        assert leaf in SKILL.read_text(), f"no procedure step mentions {field!r}"

    def test_both_subcommand_invocations_are_spelled_out(self):
        text = SKILL.read_text()
        assert "keyword-map <your file>" in text
        assert "search <your file> --keyword-map <the map>" in text
        assert text.count("--with pyyaml --with jsonschema") >= 2

    def test_the_skill_carries_the_fabrication_warning(self):
        """The type's whole shape follows from it, so it is stated once at the top rather than
        implied by the rules that come from it."""
        text = SKILL.read_text().lower()
        assert "fabricat" in text
        assert "never quote a text you could not read" in text


class TestProseAndSchemasAgree:
    """C6. Three guards, and they run in opposite directions on purpose.

    Both schemas are `additionalProperties: false`, so a field the prose instructs a producer to
    write and the schema does not declare is an artifact that CANNOT validate -- and the SKILL's own
    "fix and re-run until exit 0" loop then has no legal fix. The inverse is the one a sibling
    shipped: a field the schema OFFERS that no step writes and no rule reads is dead, and
    documenting it as a known gap is not the same as closing it.
    """

    @staticmethod
    def _authored() -> list[Path]:
        """DERIVED by glob, never enumerated. A guard that names the files it was written from
        certifies those and licenses the rest."""
        out = [SKILL] + sorted((PACKAGE / "references").rglob("*.md"))
        assert len(out) >= 12, f"only {len(out)} authored files -- the glob is wrong"
        return out

    @staticmethod
    def _schema_fields() -> set[str]:
        import json
        found: set[str] = set()

        def walk(node):
            if isinstance(node, dict):
                for k, v in node.items():
                    if k == "properties" and isinstance(v, dict):
                        found.update(v)
                    walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)

        for p in (PACKAGE / "schemas").glob("*.schema.json"):
            walk(json.loads(p.read_text()))
        return found

    #: Field names that belong to someone ELSE's vocabulary. The prose has to name them -- a
    #: producer resolving a Cellar URI needs to know the header, and one describing the
    #: capability-map trigger needs the leaf -- but a schema field they are not. Enumerated rather
    #: than pattern-matched, so prose naming a REAL external field passes and prose naming an
    #: invented one still fails.
    EXTERNAL_FIELDS = frozenset({
        "ml_involvement", "has_ui", "platform_type", "geo_distribution", "data_residency",
        "required_level", "risk_level", "data_sensitivity", "open_to_public", "multi_region",
        "cloud_providers", "model_governance", "responsible_ai", "eu_ai_act",
        "registry_version", "probe_default", "url_kind", "probe_method", "user_agent",
        "access_status", "applicable_group_types", "trigger_anchor", "widening_legs",
        "predicate_omits", "cap_rationale", "ordering_signal", "fallback_rationale",
        "type_trigger", "coherence_axioms", "group_type", "sector_family", "control_vocabulary",
        "count_frame", "text_retrievable", "reason_class", "map_verdict", "status_counts",
        "degraded_sources", "shared_terms", "absent_types", "sector_scoping", "not_run",
        "item_id", "id_class", "group_id", "source_id", "angle_id", "found_by", "schema_version",
        "retrieved_at", "as_of", "in_force_date", "issuing_body", "instrument_type",
        "binding_force", "evidence_quote", "expansion_cap", "negative_terms", "control_ids",
        "source_claimed_modified_at", "source_claim_provenance", "dropped_note",
        "ordering_deviation", "fallback_used", "scope_ref", "expansions", "borrowed_from",
    })

    def test_no_prose_names_a_field_the_SCHEMAS_lack(self):
        known = self._schema_fields() | self.EXTERNAL_FIELDS
        named: set[str] = set()
        for p in self._authored():
            named |= set(re.findall(r"`([a-z][a-z0-9]*(?:_[a-z0-9]+)+)`", p.read_text()))
        assert not (named - known), sorted(named - known)

    def test_the_external_set_is_not_a_blanket_licence(self):
        """Both directions. An exemption is only worth having if the thing it exempts still fails
        when it is not on the list."""
        known = self._schema_fields() | self.EXTERNAL_FIELDS
        assert "ml_involvement" in known
        assert "ml_invulvement" not in known

    #: Schema blocks that constrain something beyond the bare type. A field with one of these has
    #: a machine-checkable claim on it already; a field with NONE is shaped only as "a string",
    #: and if no rule reads it too then its `description` is the whole of its enforcement.
    _CONSTRAINTS = frozenset({"enum", "const", "pattern", "$ref", "minimum", "maximum",
                              "minItems", "minProperties", "format"})

    #: Reads a field, as opposed to naming it in a message. `.get("x")` and `["x"]`, derived --
    #: the substring form this replaced counted `instruments` as read the moment an unrelated rule
    #: message used the ordinary English word, which is a guard reporting green off a coincidence.
    _READS = re.compile(r"""(?:\.get\(|\[)["']([a-z_][a-z0-9_]*)["']""")

    #: EXACTLY the fields the schema leaves loose and no rule reads. Asserted by EQUALITY, in both
    #: directions, because this is a change-detector and not a completeness proof: it cannot tell
    #: which `description`s state a checkable claim, so it holds the line where the argument was
    #: last made. A new loose field, or a field that loses its rule, fails here and has to be
    #: argued onto the list; a field that gains one has to leave it.
    #:
    #: - free prose whose CONTENT no rule can judge; `minLength: 1` refuses the empty one and that
    #:   is the whole checkable claim:  assumptions, claim, evidence, finding, item, jurisdiction,
    #:   name, notes, ordering, ordering_deviation, precondition, reason, scope_ref
    #: - names an EXTERNAL vocabulary, whose set is unbounded; any check would be against a list
    #:   this package would have to invent:  borrowed_from
    #: - an identifier with nothing in the id to disagree with. `celex`, `cfr_citation` and
    #:   `standard_number` are checked against `item_id` because the id is BUILT from them; a DOI
    #:   is not:  doi
    #: - deliberately NOT `$defs/timestamp`. One is what the instrument itself states, which can be
    #:   a period rather than a date; the other is the page's claim ABOUT ITSELF, recorded so it
    #:   can never be promoted into `as_of`. Constraining either refuses the honest record:
    #:   in_force_date, source_claimed_modified_at
    #: - the shortlist a sector verdict hands a1. Checking it against the corpus needs a fetch,
    #:   which wave 1 does not do:  instruments
    #: - `probe-record` demands the note UNCONDITIONALLY, which is strictly stronger than the
    #:   pairing this field describes; reading it could only weaken the rule:  ran
    UNREADABLE = frozenset({
        "assumptions", "claim", "evidence", "finding", "item", "jurisdiction", "name", "notes",
        "ordering_deviation", "precondition", "reason", "scope_ref",
        "borrowed_from", "doi", "in_force_date", "source_claimed_modified_at", "instruments",
        "ran",
    })

    @classmethod
    def _schema_blocks(cls) -> dict[str, list[dict]]:
        import json
        out: dict[str, list[dict]] = {}

        def walk(node):
            if isinstance(node, dict):
                for k, v in node.items():
                    if k == "properties" and isinstance(v, dict):
                        for name, block in v.items():
                            out.setdefault(name, []).append(block)
                    walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)

        for p in (PACKAGE / "schemas").glob("*.schema.json"):
            walk(json.loads(p.read_text()))
        return out

    def test_every_field_a_SCHEMA_offers_is_INSTRUCTED(self):
        """#63, DERIVED over every field in both schemas rather than a hand-picked few.

        The parametrized form named five and certified those, which is exactly the shape #61
        warns about: a guard that names its subjects licenses everything it did not name. Run over
        all of them, it found `lineage` -- a block copied schema-only into six sibling packages,
        instructed nowhere, read by nothing, and already dropped by the newest sibling -- plus two
        REQUIRED fields, `meta.scope_ref` and `borrowed_from`, that no procedure step wrote. A
        producer following the prose alone would have been refused by the schema for one and would
        have silently omitted the other.
        """
        prose = " ".join(p.read_text() for p in self._authored())
        missing = sorted(f for f in self._schema_fields() if f not in prose)
        assert not missing, f"in a schema and instructed by no procedure step: {missing}"

    def test_every_field_the_SCHEMA_leaves_LOOSE_is_read_by_a_rule(self):
        """The other half, and the one with teeth. A field the schema constrains is checked by the
        schema; a field it shapes only as `string` is checked by NOTHING unless a rule reads it,
        however precise its `description` is about what it must contain.

        Run derived, this found three: `locator` ("a resolvable URL" -- `see the register` passed),
        `fallback_used` ("prefixed `angle:` or `row:`" -- a bare id passed), and `issuing_body`
        ("L-7 admits an instrument only when this resolves to a named body" -- null passed). All
        three now have rules. The remainder is enumerated above WITH its reason.
        """
        read = set(self._READS.findall(SCRIPT.read_text()))
        loose = {name for name, blocks in self._schema_blocks().items()
                 if not any(self._constrained(b) for b in blocks)}
        assert loose - read == self.UNREADABLE, {
            "loose in the schema and read by no rule": sorted(loose - read - self.UNREADABLE),
            "exempted as unreadable and now read": sorted(self.UNREADABLE - (loose - read)),
        }

    @classmethod
    def _constrained(cls, block: dict) -> bool:
        if cls._CONSTRAINTS & set(block):
            return True
        item = block.get("items")
        if isinstance(item, dict) and (cls._CONSTRAINTS & set(item)
                                       or "properties" in item or "required" in item):
            return True
        return "properties" in block or "required" in block

    def test_the_LOOSE_sweep_is_actually_looking_at_something(self):
        """A derived guard that classifies everything as constrained is green and worthless."""
        blocks = self._schema_blocks()
        loose = {n for n, bs in blocks.items() if not any(self._constrained(b) for b in bs)}
        assert len(blocks) >= 90, f"only {len(blocks)} schema fields -- the walk is wrong"
        assert 20 <= len(loose) < len(blocks), f"{len(loose)} of {len(blocks)} read as loose"

    def test_probe_method_is_a_REGISTRY_field_and_is_read(self, registry):
        """It is deliberately NOT in either artifact schema -- it describes how a SOURCE was
        probed, not what a producer writes. The same three-way check still applies, one layer
        over: the registry declares it, the prose instructs it, and a rule reads it."""
        assert "probe_default" in registry
        assert any("probe_method" in s for s in registry["sources"])
        prose = " ".join(p.read_text() for p in self._authored())
        assert "probe_method" in prose
        assert "probe-method-shape" in SCRIPT.read_text()


class TestProseDoesNotContradictTheRegistry:
    """#57: prose invents its own support. Three checks over every authored file, because this
    type's prose is unusually dense in source-posture claims -- the B1 re-verification produced
    around thirty status, redirect and user-agent assertions that were then transcribed into the
    registry, the guides and eight angle references.
    """

    @staticmethod
    def _prose() -> dict[str, str]:
        return {p.name: p.read_text() for p in TestProseAndSchemasAgree._authored()}

    def test_every_source_id_in_prose_resolves_to_a_registry_row(self, registry):
        known = {s["id"] for s in registry["sources"]} | {e["id"] for e in registry["excluded"]}
        vocab = known | {
            "regulatory-scope-map", "search-output", "source-registry", "scope-guard",
            "not-attempted", "rate-limited", "forbidden-by-terms", "not-fetched",
            "full-text", "summary-only", "primary-law", "regulator-guidance",
            "incorporated-standard", "secondary-compilation", "voluntary-standard",
            "does-not-apply", "children-minors", "financial-payments", "employment-hr",
            "public-sector", "export-controlled", "telecom-critical-infrastructure",
            "obligation-dimension", "control-catalog", "platform-role", "transfer-mechanism",
            "model-term", "ui-term", "group-source", "keyword-map", "online-platform",
            "hosting-service", "intermediary-service", "cross-border", "in-force",
            "post-market", "risk-management", "lowercase-dotted", "single-region",
            "multi-region", "api-service", "payments-network", "web-app", "b2c", "ePHI",
            "uses-pre-trained", "no-stated-version-or-date", "unresolvable-at-issuing-body",
            "out-of-scope-for-this-angle", "duplicate-of", "incorporated-by-reference",
            # Group ids minted by the clean map and the guide's example, and control ids from the
            # catalogs a3 walks. Both are lowercase-hyphenated and neither is a source.
            "adequacy-decision", "hipaa-security-rule", "breach-notification", "conformance-level",
            "us-federal",
            "risk-management-system", "contract-corpora", "sp800-53",
            "ac-1", "at-2.2", "sc-13", "ac-14",
        }
        # RULE IDS are lowercase-hyphenated too, and prose that tells a producer WHICH rule refuses
        # a thing is doing its job. Derived from the validator rather than added to `vocab` by hand:
        # enumerating them here would go stale the next time a rule is added or renamed, which is
        # the failure this whole class exists to catch one layer down.
        rule_ids = set(re.findall(r'_fail\(\s*"([a-z0-9-]+)"', SCRIPT.read_text()))
        assert len(rule_ids) >= 50, f"only {len(rule_ids)} rule ids -- the sweep is wrong"

        looks_like_a_source = re.compile(r"`([a-z]+(?:-[a-z0-9]+){1,3})`")
        offenders = [
            f"{name}: `{tok}`"
            for name, text in self._prose().items()
            for tok in sorted(set(looks_like_a_source.findall(text)))
            if tok not in vocab and tok not in rule_ids and tok.islower()
        ]
        assert not offenders, offenders

    def test_every_angle_id_in_prose_is_a_real_angle(self, registry):
        declared = {a["id"] for a in registry["angles"]}
        used = set()
        for text in self._prose().values():
            used |= set(re.findall(r"`([ab][0-9]+)`", text))
        assert not (used - declared), sorted(used - declared)

    def test_a_cap_stated_in_prose_matches_the_registry(self, registry):
        """A cap is a number, and a number in prose goes stale the moment the registry moves."""
        caps = {a["id"]: a["cap"] for a in registry["angles"]}
        for name, text in self._prose().items():
            for aid, cap in re.findall(r"\*\*Cap:\*\* (\d+)", text) and [] or []:
                pass
            for stated in re.findall(r"\*\*Cap:\*\* (\d+)", text):
                angle = name.removesuffix(".md")
                if angle in caps:
                    assert int(stated) == caps[angle], (
                        f"{name} states cap {stated}, registry says {caps[angle]}")


CONDITIONS = REVIEWER / "references" / "conditions.md"


class TestReviewerPackage:
    """C7. The reviewing twin, and the paths it depends on.

    Three of the reviewer's five evidence sources live in the PRODUCER package. A path claim is
    exactly the kind of thing that needs a mechanical check -- a sibling's cold agent could not
    read the conditions file at all, and nothing in that package would have noticed.
    """

    def test_the_reviewer_ships_its_parts(self):
        for rel in ("SKILL.md", "references/conditions.md", "references/sources.md",
                    "references/fixtures/map.clean.yaml",
                    "references/fixtures/search.clean.yaml",
                    "references/fixtures/README.md"):
            assert (REVIEWER / rel).exists(), f"reviewer is missing {rel}"

    def test_the_reviewers_clean_fixtures_are_the_producers(self):
        """Byte-identical, because two copies that drift are two different bars."""
        for reviewer_name, producer_name in (
            ("map.clean.yaml", "regulatory-scope-map.valid.yaml"),
            ("search.clean.yaml", "search-output.valid.yaml"),
        ):
            a = (REVIEWER / "references" / "fixtures" / reviewer_name).read_bytes()
            b = (FIXTURES / producer_name).read_bytes()
            assert a == b, f"{reviewer_name} has drifted from {producer_name}"

    def test_the_PLANTED_fixtures_are_NOT_in_the_reviewer(self):
        """A blind reviewer handed this skill must not be able to read the answer key."""
        stray = list((REVIEWER / "references" / "fixtures").glob("*planted*"))
        assert not stray, f"planted fixtures leaked into the reviewer package: {stray}"

    def test_every_producer_path_the_reviewer_names_RESOLVES(self):
        """The claim under test is 'you can read this'. It is checked, not asserted."""
        text = (REVIEWER / "SKILL.md").read_text() + (REVIEWER / "references" / "sources.md").read_text()
        named = set(re.findall(r"`(regulatory-prior-art-survey/[A-Za-z0-9_./<>-]+)`", text))
        assert named, "the reviewer names no producer path at all"
        for rel in sorted(named):
            concrete = rel.replace("<angle_id>", "a1")
            target = PACKAGE.parent / concrete
            assert target.exists(), f"reviewer names {rel!r}, which does not resolve"

    def test_the_reviewer_description_fits_the_cap(self):
        fm = yaml.safe_load((REVIEWER / "SKILL.md").read_text().split("---", 2)[1])
        assert len(fm["description"]) <= 1024

    def test_the_reviewer_emits_exactly_one_verdict_grammar(self):
        text = (REVIEWER / "SKILL.md").read_text()
        assert "VERDICT: approve" in text and "VERDICT: revise" in text
        assert "there is no third verdict" in text.lower()


class TestConditionsShape:
    """C7a. Every condition carries its evidence and both directions, and every carve-out names a
    rule that exists -- in BOTH directions.
    """

    def _blocks(self) -> dict[str, str]:
        text = CONDITIONS.read_text()
        out, cur, buf = {}, None, []
        for line in text.splitlines():
            m = re.match(r"^\*\*(C\d+[a-z]?) — ", line)
            if m:
                if cur:
                    out[cur] = "\n".join(buf)
                cur, buf = m.group(1), [line]
            elif cur:
                buf.append(line)
        if cur:
            out[cur] = "\n".join(buf)
        return out

    def test_there_are_conditions_at_all(self):
        assert len(self._blocks()) >= 20

    @pytest.mark.parametrize("marker", ["*Evidence:*", "*IS a gap:*"])
    def test_every_condition_carries(self, marker):
        missing = [cid for cid, body in self._blocks().items() if marker not in body]
        assert not missing, f"conditions with no {marker}: {missing}"

    def test_most_conditions_say_what_is_NOT_a_gap(self):
        """A condition with only the failing side invites a reviewer to read every near-miss as a
        finding, and the revise round costs more than the gap. Not every condition can have one --
        some have no legitimate near-miss -- so this asserts the majority do rather than all."""
        blocks = self._blocks()
        with_mirror = [cid for cid, body in blocks.items() if "*NOT a gap:*" in body]
        assert len(with_mirror) >= len(blocks) * 0.6, (
            f"only {len(with_mirror)} of {len(blocks)} conditions say what is NOT a gap")

    def test_every_DISCLAIMED_rule_is_a_real_validator_rule(self):
        """#56, and it is the direction that matters: a carve-out naming a rule that does not exist
        reads as a boundary and marks nothing."""
        shipped = set(re.findall(r'_fail\(\s*"([a-z0-9-]+)"', SCRIPT.read_text()))
        shipped |= {rule for rule, _ in V.ID_GRAMMARS.values()}
        disclaimed: set[str] = set()
        for blk in CONDITIONS.read_text().split("*Not yours to report:*")[1:]:
            body = blk.split("**C")[0]
            disclaimed |= set(re.findall(r"`([a-z0-9]+(?:-[a-z0-9]+)+)`", body))
        assert disclaimed, "no condition disclaims any rule -- the boundary is unstated"
        phantom = disclaimed - shipped
        assert not phantom, f"conditions disclaim rules that do not exist: {sorted(phantom)}"

    def test_the_conditions_do_not_RESTATE_a_rule_they_disclaim(self):
        """The other direction of #56. A condition whose stated gap the gate already catches
        occupies a number, reads as covered, and covers nothing -- an artifact reaching the
        reviewer has already passed at exit 0, so that finding can never be made."""
        for cid, body in self._blocks().items():
            if "*Not yours to report:*" not in body:
                continue
            disclaimed = set(re.findall(r"`([a-z0-9]+(?:-[a-z0-9]+)+)`",
                                        body.split("*Not yours to report:*")[1]))
            gap_text = " ".join(body.split("*Not yours to report:*")[0].split("*IS a gap:*")[1:])
            overlap = {r for r in disclaimed if f"`{r}`" in gap_text}
            assert not overlap, f"{cid} names {overlap} as its own gap AND disclaims it"


class TestJudgedFieldsAreDescribed:
    """C7b. §9c's first guard, and the highest-yield one here: this pair adds five judged fields,
    and a reviewer judging a field with no schema description is judging a name.
    """

    def _schema_descriptions(self) -> dict[str, str]:
        import json
        out: dict[str, str] = {}

        def walk(node):
            if isinstance(node, dict):
                for k, v in (node.get("properties") or {}).items():
                    if isinstance(v, dict) and "description" in v:
                        out[k] = v["description"]
                for v in node.values():
                    walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)

        for p in (PACKAGE / "schemas").glob("*.schema.json"):
            walk(json.loads(p.read_text()))
        return out

    @pytest.mark.parametrize("field", [
        "authority", "binding_force", "text_retrievable", "applies", "reason_class",
        "evidence_quote", "claim", "finding", "count_frame", "cause", "status", "kept",
        "instrument_type", "as_of", "source_claimed_modified_at", "holds", "canonical",
    ])
    def test_every_field_a_reviewer_JUDGES_carries_a_description(self, field):
        desc = self._schema_descriptions()
        assert field in desc, f"{field} has no schema description, and a condition judges it"
        assert len(desc[field].split()) >= 8, f"{field}'s description is a label, not a description"

    def test_every_field_a_CONDITION_names_as_evidence_exists(self):
        """EC9b(b). A condition grounded on a field the schema does not declare is unexecutable,
        and every finding under it silently collapses to an Observation."""
        known = set(self._schema_descriptions())
        import json

        def walk(node):
            """Field names AND enum values. A condition naming `undetermined` or `sector` is
            naming something the schema declares -- an enum member and a group type -- and
            counting only property names reports both as phantoms."""
            if isinstance(node, dict):
                known.update((node.get("properties") or {}).keys())
                for v in (node.get("enum") or []):
                    if isinstance(v, str):
                        known.add(v)
                for v in node.values():
                    walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)

        for p in (PACKAGE / "schemas").glob("*.schema.json"):
            walk(json.loads(p.read_text()))
        external = {"probe_default", "probe_method", "sources", "coverage", "candidates",
                    "unadmitted", "groups", "notes", "queries", "meta"}
        named: set[str] = set()
        for blk in CONDITIONS.read_text().split("*Evidence:*")[1:]:
            body = blk.split("*IS a gap:*")[0]
            named |= set(re.findall(r"`(?:[a-z_]+\[\])?\.?([a-z][a-z0-9_]*)`", body))
            named |= set(re.findall(r"`[a-z_]+\[\]\.([a-z][a-z0-9_]*)`", body))
        unknown = {f for f in named if f not in known and f not in external}
        assert not unknown, f"conditions name evidence fields no schema declares: {sorted(unknown)}"

    def test_that_guard_still_catches_a_real_phantom(self):
        """Both directions. Widening the known set to include enum values fixed two false
        positives; it must not have made the check unfalsifiable."""
        import json
        known: set[str] = set()

        def walk(node):
            if isinstance(node, dict):
                known.update((node.get("properties") or {}).keys())
                known.update(v for v in (node.get("enum") or []) if isinstance(v, str))
                for v in node.values():
                    walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)

        for p in (PACKAGE / "schemas").glob("*.schema.json"):
            walk(json.loads(p.read_text()))
        assert "authority" in known and "undetermined" in known
        assert "authoritee" not in known


class TestPortability:
    """C7c / EC6. These packages ship to projects that cannot see the program that authored them.

    It runs HERE and not beside the validator, because at that point the guides, the eight angle
    references and the whole reviewer package did not exist -- a guard authored against a third of
    its population certifies that third and licenses the rest.
    """

    LEAK = re.compile(
        r"playbook ?#|spec L-|classification-schema|\b5[a-j]\b|disk-authoritative|"
        r"this ticket|agents-hq|coordinator|project_prior_art|docs/superpowers",
        re.I,
    )
    ALLOWED = re.compile(r"agents-hq\.local/schemas/", re.I)

    @staticmethod
    def _shippable() -> list[Path]:
        """Everything a dispatched AGENT reads, INCLUDING the validator.

        The validator is in scope because its `FAIL` messages print straight to an agent's console,
        so a program reference in one ships exactly as a reference in a guide would. A sibling
        learned that the expensive way: its portability check scanned the prose and the schemas and
        never the validator, and closing the gap cost a dedicated re-run.

        WHAT IS DELIBERATELY OUT: this test module. Its docstrings name the sibling packages each
        rule came from, and that provenance is how a maintainer tells a considered divergence from
        a typo. The exclusion is asserted below rather than left implicit -- an exemption nobody
        states is indistinguishable from an oversight, which is the whole failure this check exists
        to catch.
        """
        out = [SKILL, SCRIPT]
        out += sorted((PACKAGE / "references").rglob("*.md"))
        out += sorted((PACKAGE / "schemas").glob("*.json"))
        out += [PACKAGE / "references" / "source-registry.yaml"]
        out += sorted((PACKAGE / "scripts").glob("*.validation.md"))
        out += sorted(REVIEWER.rglob("*.md"))
        out += sorted((REVIEWER / "references" / "fixtures").glob("*.yaml"))
        out += sorted((PACKAGE / "scripts" / "fixtures").rglob("*.yaml"))
        assert len(out) >= 25, f"only {len(out)} shippable files -- the glob is wrong, not the repo"
        return out

    def test_no_host_program_term_ships(self):
        offenders = []
        for p in self._shippable():
            for n, line in enumerate(p.read_text().splitlines(), 1):
                if self.LEAK.search(line) and not self.ALLOWED.search(line):
                    offenders.append(f"{p.name}:{n}: {line.strip()[:90]}")
        assert not offenders, offenders

    def test_the_allowlist_fires_in_BOTH_directions(self):
        """The exempted string must still MATCH the leak pattern, and still be exempted. An
        allowlist that no longer matches what it exempts is dead code that reads as protection."""
        import json
        ids = [json.loads(p.read_text())["$id"]
               for p in (PACKAGE / "schemas").glob("*.schema.json")]
        assert len(ids) == 2
        for sid in ids:
            assert self.LEAK.search(sid), f"{sid} no longer matches the leak pattern"
            assert self.ALLOWED.search(sid), f"{sid} is no longer exempted"

    def test_the_test_module_is_deliberately_OUT_of_scope(self):
        """Both directions: the exclusion is real, and it is narrow. The validator beside it is
        IN, which is the half a sibling missed."""
        shippable = {p.resolve() for p in self._shippable()}
        assert Path(__file__).resolve() not in shippable
        assert SCRIPT.resolve() in shippable

    def test_the_validator_is_actually_clean(self):
        """Named separately from the sweep, because this is the file the sweep was widened to
        cover and a regression here would be invisible inside a list of thirty."""
        text = SCRIPT.read_text()
        hits = [ln for ln in text.splitlines()
                if self.LEAK.search(ln) and not self.ALLOWED.search(ln)]
        assert not hits, hits


PLANTED = FIXTURES / "planted"

#: The answer key. It lives HERE, in the module the reviewer under test never reads -- recording it
#: beside the fixtures would turn every future blind run into an open-book one.
PLANTED_DEFECTS = {
    "map-01.yaml": ("keyword-map", "C5",
                    "b4 holds TRUE and its reason cites `infrastructure.data_residency` as though "
                    "it carried a value -- the field is declared with zero properties, so the "
                    "verdict rests on something the classification cannot have said. The inflating "
                    "direction, and the harder one to see"),
    "search-01.yaml": ("search", "C9",
                       "the eu-cellar cells record a described strategy instead of the request as "
                       "issued, and drop the Accept headers -- on this corpus the same URI returns "
                       "200 under one and 404 under another, so the count cannot be reproduced"),
    "search-02.yaml": ("search", "C19",
                       "a claim about what the SYSTEM MUST DO resting on a quote about what the "
                       "act SAYS -- the recurring failure, and the one this type is shaped around"),
    "search-03.yaml": ("search", "C16",
                       "a tier-4 tracker recorded as `primary-law` with the tracker as locator, "
                       "AND an instrument dropped because its source ranked low -- authority "
                       "orders the list, it does not filter it"),
}


class TestPlantedFixtures:
    """C8. Each is wrong AND passes at exit 0 -- that combination is the whole test.

    A planted defect the validator catches proves the validator works, which was never in question.
    The REVIEWER is what is under test, and it only ever sees artifacts that passed.
    """

    def _cli(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(SCRIPT), *args],
                              capture_output=True, text=True, cwd=HERE, check=False)

    @pytest.mark.parametrize("name", sorted(PLANTED_DEFECTS))
    def test_it_passes_the_deterministic_gate(self, name, registry, valid_map):
        kind, _, _ = PLANTED_DEFECTS[name]
        doc = yaml.safe_load((PLANTED / name).read_text())
        found = (V.validate_keyword_map(doc, registry) if kind == "keyword-map"
                 else V.validate_search(doc, valid_map, registry))
        assert found == [], f"{name} does not reach the reviewer: {found}"

    @pytest.mark.parametrize("name", sorted(PLANTED_DEFECTS))
    def test_it_passes_through_main_too(self, name):
        """Through the CLI, not just the function -- a fixture that passes in-process and fails at
        the command line is one no blind run can use."""
        kind, _, _ = PLANTED_DEFECTS[name]
        args = ([kind, str(PLANTED / name)] if kind == "keyword-map" else
                [kind, str(PLANTED / name), "--keyword-map",
                 str(FIXTURES / "regulatory-scope-map.valid.yaml")])
        r = self._cli(*args)
        assert r.returncode == 0, r.stdout + r.stderr

    def test_the_answer_key_covers_every_file_and_no_others(self):
        on_disk = {p.name for p in PLANTED.glob("*.yaml")}
        assert on_disk == set(PLANTED_DEFECTS), (
            f"unkeyed: {sorted(on_disk - set(PLANTED_DEFECTS))}, "
            f"keyed but absent: {sorted(set(PLANTED_DEFECTS) - on_disk)}")

    def test_each_names_a_condition_that_EXISTS(self):
        declared = set(re.findall(r"^\*\*(C\d+[a-z]?) — ", CONDITIONS.read_text(), re.M))
        for name, (_, cond, _) in PLANTED_DEFECTS.items():
            assert cond in declared, f"{name} is keyed to {cond}, which no condition declares"

    def test_no_fixture_NAMES_its_own_defect(self):
        """A fixture that hints at what is wrong with it turns a blind run into an open-book one."""
        for p in PLANTED.glob("*.yaml"):
            text = p.read_text().lower()
            for word in ("planted", "deliberate", "defect", "wrong on purpose", "answer key"):
                assert word not in text, f"{p.name} names its own defect: {word!r}"

    @pytest.mark.parametrize("name", sorted(PLANTED_DEFECTS))
    def test_it_differs_from_the_CLEAN_fixture_only_in_its_plant(self, name):
        """EC9b(d). A fixture that differs in ten places tests which difference a reviewer notices
        first, not whether it can find the one that matters. Asserted BEFORE a blind run is spent,
        because the run is the expensive half."""
        kind, _, _ = PLANTED_DEFECTS[name]
        clean_name = ("regulatory-scope-map.valid.yaml" if kind == "keyword-map"
                      else "search-output.valid.yaml")
        clean = yaml.safe_load((FIXTURES / clean_name).read_text())
        planted = yaml.safe_load((PLANTED / name).read_text())

        def paths(node, prefix=""):
            if isinstance(node, dict):
                for k, v in node.items():
                    yield from paths(v, f"{prefix}.{k}")
            elif isinstance(node, list):
                for i, v in enumerate(node):
                    yield from paths(v, f"{prefix}[{i}]")
            else:
                yield prefix, node

        a, b = dict(paths(clean)), dict(paths(planted))
        changed = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
        assert len(changed) <= 8, f"{name} differs from clean in {len(changed)} places: {changed}"


class TestNoIncidentalGapInAnyFixture:
    """Build-contract §9c's fixture sweep, over PLANTED and CLEAN alike.

    Its whole point is to not spend a blind run on a broken fixture. A reviewer handed an artifact
    with an accidental second defect reports that one, the run proves nothing about the planted
    condition, and the cost is paid before anyone notices.
    """

    def _all_search(self) -> list[tuple[str, dict]]:
        out = [("clean", yaml.safe_load((FIXTURES / "search-output.valid.yaml").read_text()))]
        out += [(p.name, yaml.safe_load(p.read_text())) for p in sorted(PLANTED.glob("search-*.yaml"))]
        return out

    @pytest.mark.parametrize("label", ["clean", "search-01.yaml", "search-02.yaml", "search-03.yaml"])
    def test_no_active_source_is_missing_from_the_grid(self, label, valid_map, registry):
        doc = dict(self._all_search())[label]
        angle = next(a for a in registry["angles"] if a["id"] == doc["meta"]["angle_id"])
        active = {s["id"] for s in valid_map["sources"]["active"]}
        expected = {s for s in angle["sources"] if s in active}
        seen = {c["source_id"] for c in doc["coverage"]}
        assert expected == seen, f"{label}: sources owed {sorted(expected - seen)}, extra {sorted(seen - expected)}"

    @pytest.mark.parametrize("label", ["clean", "search-01.yaml", "search-02.yaml", "search-03.yaml"])
    def test_no_fallback_is_claimed_without_a_trace(self, label):
        doc = dict(self._all_search())[label]
        for cell in doc["coverage"]:
            used = cell.get("fallback_used")
            if used:
                assert cell["status"] != "reached" or "fallback" in (cell.get("cause") or "").lower(), (
                    f"{label}: {cell['group_id']}/{cell['source_id']} claims a fallback with no "
                    "trace of why one was needed")

    @pytest.mark.parametrize("label", ["clean", "search-01.yaml", "search-02.yaml", "search-03.yaml"])
    def test_no_kept_zero_hides_a_dropped_row(self, label):
        """A cell that returned something and kept nothing is legitimate -- and it is also where a
        silent drop hides. The frame has to say what happened to the remainder."""
        doc = dict(self._all_search())[label]
        for cell in doc["coverage"]:
            if cell["status"] == "reached" and cell.get("returned") and cell.get("kept") == 0:
                frame = (cell.get("count_frame") or "").lower()
                assert frame, f"{label}: {cell['group_id']}/{cell['source_id']} kept 0 of {cell['returned']} with no frame"
                assert len(frame.split()) >= 12, (
                    f"{label}: {cell['group_id']}/{cell['source_id']} kept 0 of {cell['returned']} "
                    "and its frame does not say what happened to the remainder")


class TestTheShippedInventory:
    """Every file the pair promises, asserted as a SET.

    The per-file tests above each check one thing exists. None of them would notice a file that
    was promised and never written, or one that shipped and should not have -- and the planted
    fixtures leaking into the reviewer package is exactly the second kind.
    """

    PRODUCER_FILES = {
        "SKILL.md",
        "references/absent-input-policy.md",
        "references/regulatory-scope-map-guide.md",
        "references/search-output-guide.md",
        "references/source-registry.yaml",
        "references/sources.md",
        "schemas/regulatory-scope-map.schema.json",
        "schemas/search-output.schema.json",
        "scripts/validate_regulatory_prior_art.py",
        "scripts/validate_regulatory_prior_art.py.validation.md",
        "scripts/test_validate_regulatory_prior_art.py",
        "scripts/test_validate_regulatory_prior_art.py.validation.md",
        "scripts/fixtures/regulatory-scope-map.valid.yaml",
        "scripts/fixtures/search-output.valid.yaml",
        "scripts/fixtures/planted/README.md",
        "scripts/fixtures/planted/map-01.yaml",
        "scripts/fixtures/planted/search-01.yaml",
        "scripts/fixtures/planted/search-02.yaml",
        "scripts/fixtures/planted/search-03.yaml",
    } | {f"references/angles/{a}.md" for a in ("a1", "a2", "a3", "b1", "b2", "b3", "b4", "b5")}

    REVIEWER_FILES = {
        "SKILL.md",
        "references/conditions.md",
        "references/sources.md",
        "references/fixtures/README.md",
        "references/fixtures/map.clean.yaml",
        "references/fixtures/search.clean.yaml",
    }

    @staticmethod
    def _actual(root: Path) -> set[str]:
        return {str(p.relative_to(root)) for p in root.rglob("*")
                if p.is_file() and "__pycache__" not in p.parts}

    def test_the_producer_ships_exactly_what_it_promises(self):
        actual = self._actual(PACKAGE)
        assert actual == self.PRODUCER_FILES, (
            f"missing: {sorted(self.PRODUCER_FILES - actual)}, "
            f"unexpected: {sorted(actual - self.PRODUCER_FILES)}")

    def test_the_reviewer_ships_exactly_what_it_promises(self):
        actual = self._actual(REVIEWER)
        assert actual == self.REVIEWER_FILES, (
            f"missing: {sorted(self.REVIEWER_FILES - actual)}, "
            f"unexpected: {sorted(actual - self.REVIEWER_FILES)}")

    def test_the_angle_files_match_the_registry_one_for_one(self, registry):
        """Derived rather than restated, so a ninth angle cannot ship without its reference."""
        declared = {a["id"] for a in registry["angles"]}
        listed = {f.split("/")[-1].removesuffix(".md")
                  for f in self.PRODUCER_FILES if f.startswith("references/angles/")}
        assert declared == listed, f"registry {sorted(declared)} vs inventory {sorted(listed)}"
