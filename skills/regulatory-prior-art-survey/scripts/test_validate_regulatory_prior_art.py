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
        assert "count-frame-required" not in _rules(V.validate_search(doc, valid_map, registry))

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
        assert "status-needs-cause" not in _rules(V.validate_search(doc, valid_map, registry))

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
        assert "cell-sanitization-cause" not in _rules(V.validate_search(doc, valid_map, registry))

    def test_kept_above_returned_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        cell = next(c for c in doc["coverage"] if c["status"] == "reached" and c["returned"])
        cell["kept"] = cell["returned"] + 1
        assert "kept-exceeds-returned" in _rules(V.validate_search(doc, valid_map, registry))

    def test_kept_equal_to_returned_passes(self, valid_search, valid_map, registry):
        """MIRROR at the boundary: carrying everything a cell returned is legal."""
        doc = copy.deepcopy(valid_search)
        cell = next(c for c in doc["coverage"] if c["status"] == "reached" and c["kept"] == 1)
        cell["returned"] = 1
        cell["count_frame"] = "One instrument, resolved by identifier."
        assert "kept-exceeds-returned" not in _rules(V.validate_search(doc, valid_map, registry))

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
        assert "kept-matches-rows" not in _rules(V.validate_search(doc, valid_map, registry))

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
        assert "degraded-source-recorded" not in _rules(V.validate_search(doc, valid_map, registry))

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

    def test_candidates_exactly_AT_the_cap_pass(self, valid_search, valid_map, registry):
        """MIRROR at the boundary: the cap is a ceiling, so equality is legal. Asserting the
        unmutated fixture would test nothing -- it sits far below."""
        doc = copy.deepcopy(valid_search)
        base = doc["candidates"][0]
        doc["candidates"] = [{**copy.deepcopy(base), "item_id": f"WEB-example-{i}",
                              "id_class": "WEB"} for i in range(doc["bound"]["cap"])]
        doc["unadmitted"] = []
        _resync(doc)
        assert "cap-respected" not in _rules(V.validate_search(doc, valid_map, registry))

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
        assert "candidate-group-known" not in _rules(
            V.validate_search(valid_search, valid_map, registry))

    def test_an_id_class_disagreeing_with_the_prefix_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["id_class"] = "WEB"
        assert "id-class-shape" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_candidate_carrying_no_provenance_block_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0].pop("provenance")
        assert "candidate-provenance" in _rules(V.validate_search(doc, valid_map, registry))


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
        assert "celex-grammar" not in _rules(V.validate_search(doc, valid_map, registry))

    @pytest.mark.parametrize("bad", ["CFR-45", "CFR-451-164", "CFR-45-164-C", "CFR-45.164"])
    def test_a_malformed_cfr_citation_fails(self, bad, valid_search, valid_map, registry):
        doc = self._with(valid_search, bad, "CFR")
        assert "cfr-citation-grammar" in _rules(V.validate_search(doc, valid_map, registry))

    @pytest.mark.parametrize("good", ["CFR-45-164", "CFR-45-160", "CFR-21-11"])
    def test_real_cfr_citations_pass(self, good, valid_search, valid_map, registry):
        doc = self._with(valid_search, good, "CFR")
        assert "cfr-citation-grammar" not in _rules(V.validate_search(doc, valid_map, registry))

    @pytest.mark.parametrize("bad", ["USC-15", "USC-155-6501", "USC-15-6501-a"])
    def test_a_malformed_usc_citation_fails(self, bad, valid_search, valid_map, registry):
        doc = self._with(valid_search, bad, "USC")
        assert "usc-citation-grammar" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_real_usc_citation_passes(self, valid_search, valid_map, registry):
        doc = self._with(valid_search, "USC-15-6501", "USC")
        assert "usc-citation-grammar" not in _rules(V.validate_search(doc, valid_map, registry))

    @pytest.mark.parametrize("bad", ["NIST-800-53r5", "NIST-SP-80053r5", "NIST-SP-800-53-r5"])
    def test_a_malformed_nist_pub_fails(self, bad, valid_search, valid_map, registry):
        doc = self._with(valid_search, bad, "NIST")
        assert "nist-pub-grammar" in _rules(V.validate_search(doc, valid_map, registry))

    @pytest.mark.parametrize("good", ["NIST-SP-800-53r5", "NIST-SP-800-171r3"])
    def test_real_nist_pubs_pass(self, good, valid_search, valid_map, registry):
        doc = self._with(valid_search, good, "NIST")
        assert "nist-pub-grammar" not in _rules(V.validate_search(doc, valid_map, registry))

    @pytest.mark.parametrize("bad", ["ISO-27001", "ISO-IEC-27001", "ISO-IEC-27001-22"])
    def test_a_malformed_iso_number_fails(self, bad, valid_search, valid_map, registry):
        """An ISO number is as inventable as a CELEX one, and its TEXT is unretrievable here -- so
        nothing downstream can catch a wrong one by reading the standard."""
        doc = self._with(valid_search, bad, "ISO")
        assert "iso-number-grammar" in _rules(V.validate_search(doc, valid_map, registry))

    @pytest.mark.parametrize("good", ["ISO-IEC-27001-2022", "ISO-9001-2015", "ISO-IEC-27701-2019"])
    def test_real_iso_numbers_pass(self, good, valid_search, valid_map, registry):
        doc = self._with(valid_search, good, "ISO")
        assert "iso-number-grammar" not in _rules(V.validate_search(doc, valid_map, registry))

    @pytest.mark.parametrize("bad", ["STD-WCAG-2.2", "STD-W3C-WCAG", "STD-w3c-WCAG-2.2"])
    def test_a_malformed_std_slug_fails(self, bad, valid_search, valid_map, registry):
        doc = self._with(valid_search, bad, "STD")
        assert "std-slug-grammar" in _rules(V.validate_search(doc, valid_map, registry))

    @pytest.mark.parametrize("good", ["STD-W3C-WCAG-2.2", "STD-PCI-DSS-4.0"])
    def test_real_std_slugs_pass(self, good, valid_search, valid_map, registry):
        doc = self._with(valid_search, good, "STD")
        assert "std-slug-grammar" not in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_WEB_id_is_governed_by_no_grammar(self, valid_search, valid_map, registry):
        """MIRROR at the boundary: `WEB-` is the honest fallback for an instrument with no registry
        identity. Giving it a grammar would force a shape onto the one class that has none."""
        doc = self._with(valid_search, "WEB-ico-org-uk-uk-idta", "WEB")
        found = _rules(V.validate_search(doc, valid_map, registry))
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
