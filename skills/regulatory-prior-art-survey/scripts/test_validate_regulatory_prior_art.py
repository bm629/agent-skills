"""Tests for the regulatory prior-art gate.

Every rule gets a negative test that FIRES it and a mirror that passes at the boundary. A negative
test alone proves a rule can fire; it does not prove the rule is not firing on everything, and a
membership check that fires on everything passes its negative test and fails nothing else.
"""

from __future__ import annotations

import copy
import importlib.util
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
        assert "fallback-cycle" not in _rules(V.registry_failures(doc))


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
        assert "probe-method-shape" not in _rules(V.registry_failures(doc))


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
        assert "expansion-floor" not in _rules(V.validate_keyword_map(doc, registry))
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
        assert "negative-terms-required" not in _rules(V.validate_keyword_map(doc, registry))

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
        assert "always-on-angle-holds" not in _rules(V.validate_keyword_map(doc, registry))

    # ── sector receipt ───────────────────────────────────────────────────────
    def test_a_missing_sector_verdict_fails(self, valid_map, registry):
        """L-10: a family silently absent from the receipt is a validator failure, not a
        judgement call."""
        doc = copy.deepcopy(valid_map)
        doc["sector_scoping"] = [s for s in doc["sector_scoping"] if s["family"] != "insurance"]
        assert "sector-verdict-complete" in _rules(V.validate_keyword_map(doc, registry))

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
        assert "sector-verdict-complete" not in _rules(V.validate_keyword_map(doc, registry))

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
        assert "probe-record" not in _rules(V.validate_keyword_map(doc, registry))

    def test_a_non_clean_sanitization_with_no_cause_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["sources"]["active"][0]["sanitization"] = {"status": "modified", "cause": None}
        assert "sanitization-cause" in _rules(V.validate_keyword_map(doc, registry))

    def test_a_clean_sanitization_owes_no_cause(self, valid_map, registry):
        """MIRROR at the boundary: `clean` is the one status that explains itself."""
        doc = copy.deepcopy(valid_map)
        doc["sources"]["active"][0]["sanitization"] = {"status": "clean", "cause": None}
        assert "sanitization-cause" not in _rules(V.validate_keyword_map(doc, registry))

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
        assert "source-unaccounted" not in _rules(V.validate_keyword_map(doc, registry))
