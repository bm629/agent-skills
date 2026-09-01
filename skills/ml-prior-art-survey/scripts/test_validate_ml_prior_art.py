"""Tests for the ML prior-art deterministic gate (wave 1).

Every test mutates a deep copy of a valid fixture IN-PROCESS. Never revert a planted defect with
a VCS checkout — that discards uncommitted work alongside it.

The gate checks SHAPE. A test asserting the validator caught a SEMANTIC error would be testing the
wrong layer; those belong to the reviewing skill's numbered conditions.

Each comparison here ships its MIRROR (#34). A one-directional check on a two-directional property
reads as covered and is not — a sibling shipped the `candidates > kept` direction that essentially
never fires while the direction that parked three tickets was absent.
"""

from __future__ import annotations

import collections
import copy
import re
import subprocess
import sys
from pathlib import Path

import pytest
import validate_ml_prior_art as V
import yaml

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"
PLANTED = FIXTURES / "planted"
SCRIPT = HERE / "validate_ml_prior_art.py"
REVIEWER = HERE.parent.parent / "reviewing-ml-prior-art-survey"


@pytest.fixture
def valid_map() -> dict:
    return yaml.safe_load((FIXTURES / "ml-task-vocabulary-map.valid.yaml").read_text())


@pytest.fixture
def valid_search() -> dict:
    return yaml.safe_load((FIXTURES / "search-output.valid.yaml").read_text())


@pytest.fixture
def registry() -> dict:
    return V.load_registry()


def _rules(findings: list[str]) -> list[str]:
    return [f.split(":", 1)[0].replace("FAIL ", "") for f in findings]


def _resync(doc: dict) -> None:
    """Recompute the two derived counts a mutation moves.

    `kept` and `status_counts` are both restatements of the cells and rows. A test that mutates a
    row and leaves them stale fires the reconciliation rule instead of the one it names, and then
    passes for the wrong reason.
    """
    rows = collections.Counter(
        r["found_by"] for r in (doc.get("candidates") or []) + (doc.get("unadmitted") or [])
    )
    for cell in doc.get("coverage") or []:
        if cell.get("status") == "reached":
            cell["kept"] = rows.get(f"{cell['group_id']}/{cell['source_id']}", 0)
    if doc.get("retrieval_summary") is not None:
        doc["retrieval_summary"]["status_counts"] = dict(
            collections.Counter(c["status"] for c in doc.get("coverage") or [])
        )


class TestFailureFormat:
    """The only thing that makes a failure observable (§19). A caller greps this line."""

    def test_a_finding_is_literally_FAIL_rule_colon_message(self):
        out = V._fail("some-rule", "the message")
        assert out.startswith("FAIL some-rule: ")
        assert out.endswith("the message")

    def test_the_rule_id_contains_no_spaces(self):
        """A rule id with a space cannot be grepped as a token, which is the whole point."""
        assert " " not in V._fail("x-y", "m").split(":")[0].replace("FAIL ", "")


class TestShippedFixturesAreClean:
    def test_the_shipped_map_passes(self, valid_map, registry):
        assert V.validate_keyword_map(valid_map, registry) == []

    def test_the_shipped_search_passes(self, valid_search, valid_map, registry):
        assert V.validate_search(valid_search, valid_map, registry) == []


class TestRegistryIntegrity:
    """Exit-2 class: a package fault, checked before any artifact is read."""

    def test_a_conditional_angle_without_an_anchor_fails(self, registry):
        reg = copy.deepcopy(registry)
        next(a for a in reg["angles"] if a["trigger"] == "conditional").pop("trigger_anchor")
        assert "anchor-required" in _rules(V.anchor_failures(reg))

    def test_an_always_on_angle_with_an_anchor_fails(self, registry):
        """MIRROR: the rule is two-directional — an always-on angle declaring an anchor is a
        conditional angle someone forgot to mark."""
        reg = copy.deepcopy(registry)
        next(a for a in reg["angles"] if a["trigger"] == "always")["trigger_anchor"] = ["ui.has_ui"]
        assert "anchor-only-on-conditional" in _rules(V.anchor_failures(reg))

    def test_an_anchor_on_an_optional_field_fails(self, registry):
        reg = copy.deepcopy(registry)
        next(a for a in reg["angles"] if a["trigger"] == "conditional")["trigger_anchor"] = [
            "data_ml.eu_ai_act.risk_level"
        ]
        assert "anchor-must-be-required" in _rules(V.anchor_failures(reg))

    def test_an_anchor_on_a_required_field_passes(self, registry):
        """MIRROR, and the direction that actually broke in a sibling: every one of that type's
        anchors happened to sit in a stale list, so its clean run proved nothing."""
        reg = copy.deepcopy(registry)
        next(a for a in reg["angles"] if a["trigger"] == "conditional")["trigger_anchor"] = [
            "scale.concurrency"
        ]
        assert V.anchor_failures(reg) == []

    def test_a_scalar_anchor_is_rejected(self, registry):
        reg = copy.deepcopy(registry)
        next(a for a in reg["angles"] if a["trigger"] == "conditional")["trigger_anchor"] = (
            "scale.concurrency"
        )
        assert "anchor-must-be-a-list" in _rules(V.anchor_failures(reg))

    @pytest.mark.parametrize("bad", ["conditonal", "ALWAYS", None, ""])
    def test_a_mistyped_trigger_is_caught(self, bad, registry):
        """A one-character typo made a conditional angle read as always-on to every check below,
        so the anchor rules failed OPEN — the direction that is silent and total."""
        reg = copy.deepcopy(registry)
        a = next(x for x in reg["angles"] if x["trigger"] == "conditional")
        a["trigger"] = bad
        assert "trigger-must-be-known" in _rules(V.anchor_failures(reg))

    @pytest.mark.parametrize("shape", [[], "a string", None, 3])
    def test_a_registry_that_is_not_a_mapping_is_caught(self, shape):
        assert "not-a-mapping" in _rules(V.anchor_failures(shape))

    def test_the_shipped_registry_is_clean(self, registry):
        assert V.anchor_failures(registry) == []

    def test_the_shipped_registry_declares_only_known_triggers(self, registry):
        assert {a["trigger"] for a in registry["angles"]} <= {"always", "conditional"}


class TestMapRules:
    def test_a_group_id_minted_twice_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["groups"].append(copy.deepcopy(doc["groups"][0]))
        assert "group-id-unique" in _rules(V.validate_keyword_map(doc, registry))

    def test_distinct_group_ids_pass(self, valid_map, registry):
        """MIRROR: the rule must not fire on a map that mints correctly."""
        assert V.validate_keyword_map(valid_map, registry) == []

    def test_an_axis_an_angle_searches_must_be_populated_or_declared_absent(
        self, valid_map, registry
    ):
        doc = copy.deepcopy(valid_map)
        doc["groups"] = [g for g in doc["groups"] if g["type"] != "benchmark"]
        assert "group-type-accounted" in _rules(V.validate_keyword_map(doc, registry))

    def test_declaring_it_absent_satisfies_the_rule(self, valid_map, registry):
        """MIRROR: an empty axis is legitimate — it just has to be a DECLARED emptiness."""
        doc = copy.deepcopy(valid_map)
        doc["groups"] = [g for g in doc["groups"] if g["type"] != "benchmark"]
        doc["scope_guard"]["absent_types"].append("benchmark")
        assert V.validate_keyword_map(doc, registry) == []

    def test_an_axis_cannot_be_both_absent_and_populated(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["scope_guard"]["absent_types"].append("ml-task")
        assert "group-type-accounted" in _rules(V.validate_keyword_map(doc, registry))

    def test_expansions_above_the_cap_fail(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        g = doc["groups"][0]
        g["expansions"] = ["a", "b", "c", "d", "e", "f"]
        g["expansion_cap"] = 2
        assert "expansion-cap" in _rules(V.validate_keyword_map(doc, registry))

    def test_expansions_at_the_cap_pass(self, valid_map, registry):
        """MIRROR: the cap is a ceiling, not a target, and equality is legal."""
        doc = copy.deepcopy(valid_map)
        g = doc["groups"][0]
        g["expansions"] = ["a", "b"]
        g["expansion_cap"] = 2
        assert V.validate_keyword_map(doc, registry) == []

    @pytest.mark.parametrize("gtype", ["ml-task", "domain-term", "method"])
    def test_a_vocabulary_axis_with_no_expansions_fails(self, gtype, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        next(g for g in doc["groups"] if g["type"] == gtype)["expansions"] = []
        assert "expansion-floor" in _rules(V.validate_keyword_map(doc, registry))

    def test_a_modality_group_owes_no_expansions(self, valid_map, registry):
        """MIRROR: `text` has no synonyms worth querying, and demanding them would produce
        invented ones — which is worse than none."""
        doc = copy.deepcopy(valid_map)
        assert next(g for g in doc["groups"] if g["type"] == "modality")["expansions"] == []
        assert V.validate_keyword_map(doc, registry) == []

    def test_an_unmarked_borrowed_task_name_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        next(g for g in doc["groups"] if g["type"] == "ml-task").pop("borrowed_from")
        assert "borrowed-vocabulary-unmarked" in _rules(V.validate_keyword_map(doc, registry))

    def test_a_domain_term_without_negative_terms_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        next(g for g in doc["groups"] if g["type"] == "domain-term")["negative_terms"] = []
        assert "negative-terms-required" in _rules(V.validate_keyword_map(doc, registry))

    def test_a_skipped_probe_owes_a_note(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["probe"] = {"ran": False, "note": "  "}
        assert "probe-record" in _rules(V.validate_keyword_map(doc, registry))

    def test_a_probe_that_ran_needs_no_excuse(self, valid_map, registry):
        """MIRROR."""
        assert V.validate_keyword_map(valid_map, registry) == []


class TestAngleVerdicts:
    def test_a_missing_verdict_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["angle_applicability"] = [
            v for v in doc["angle_applicability"] if v["angle_id"] != "b3"
        ]
        assert "angle-verdict-complete" in _rules(V.validate_keyword_map(doc, registry))

    def test_two_verdicts_for_one_angle_fail(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        clash = copy.deepcopy(doc["angle_applicability"][0])
        clash["holds"] = not clash["holds"]
        doc["angle_applicability"].append(clash)
        assert "angle-verdict-unique" in _rules(V.validate_keyword_map(doc, registry))

    def test_a_verdict_for_an_unknown_angle_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        v = copy.deepcopy(doc["angle_applicability"][0])
        v["angle_id"] = "a9"
        doc["angle_applicability"].append(v)
        assert "angle-unknown" in _rules(V.validate_keyword_map(doc, registry))

    def test_an_always_on_angle_cannot_be_false(self, valid_map, registry):
        """The rule three siblings ship and 5j does not. An always-on angle has no precondition
        to fail, so `holds: false` is not a judgement about the scope — it is an angle being
        dropped with no predicate behind it."""
        doc = copy.deepcopy(valid_map)
        next(v for v in doc["angle_applicability"] if v["angle_id"] == "a1")["holds"] = False
        assert "always-on-angle-holds" in _rules(V.validate_keyword_map(doc, registry))

    def test_a_conditional_angle_may_be_false(self, valid_map, registry):
        """MIRROR, and the load-bearing one: recording that a conditional angle does not apply is
        the point of the field, not a shortfall."""
        doc = copy.deepcopy(valid_map)
        assert next(v for v in doc["angle_applicability"] if v["angle_id"] == "b2")["holds"] is False
        assert V.validate_keyword_map(doc, registry) == []


class TestMapSources:
    def test_an_excluded_source_cannot_be_active(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["sources"]["active"].append(
            {
                "id": "kaggle",
                "release": None,
                "as_of": None,
                "access_status": "open",
                "sanitization": {"status": "clean"},
            }
        )
        assert "forbidden-source-not-active" in _rules(V.validate_keyword_map(doc, registry))

    def test_an_unknown_source_cannot_be_active(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["sources"]["active"][0]["id"] = "not-a-source"
        assert "source-not-in-registry" in _rules(V.validate_keyword_map(doc, registry))

    def test_a_non_clean_sanitization_owes_a_cause(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["sources"]["active"][0]["sanitization"] = {"status": "modified"}
        assert "sanitization-cause" in _rules(V.validate_keyword_map(doc, registry))

    def test_a_clean_sanitization_owes_nothing(self, valid_map, registry):
        """MIRROR: nothing was stripped, so there is no cause to state."""
        assert V.validate_keyword_map(valid_map, registry) == []

    def test_not_fetched_still_owes_a_cause(self, valid_map, registry):
        """A posture established from response headers retrieved no body, so there was nothing to
        sanitize — but WHY there was nothing is the reviewable part."""
        doc = copy.deepcopy(valid_map)
        doc["sources"]["active"][0]["sanitization"] = {"status": "not-fetched"}
        assert "sanitization-cause" in _rules(V.validate_keyword_map(doc, registry))


class TestTheTwoDimensionalGrid:
    """The rules that fail if the owed set is computed as every group x every source.

    That is 5j's ONE-dimensional completeness rule shipped against a 2-D grid: a missing
    (group, source) pair passes, which is exactly what the grid exists to catch.
    """

    def test_a_missing_owed_pair_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["coverage"] = doc["coverage"][:-1]
        _resync(doc)
        doc["candidates"] = [
            c for c in doc["candidates"] if c["found_by"] != "support-ticket/huggingface-hub-api"
        ]
        doc["unadmitted"] = [
            u for u in doc["unadmitted"] if u["found_by"] != "support-ticket/huggingface-hub-api"
        ]
        _resync(doc)
        assert "coverage-complete" in _rules(V.validate_search(doc, valid_map, registry))

    def test_the_owed_set_is_DERIVED_not_every_group_by_every_source(
        self, valid_search, valid_map, registry
    ):
        """The load-bearing test. a1 declares [ml-task, domain-term], so the map's benchmark,
        dataset, method and modality groups are NOT owed — a 1-D rule would demand all of them.
        """
        angle = next(a for a in registry["angles"] if a["id"] == "a1")
        owed = V._owed_cells(angle, valid_map)
        all_pairs = {
            (g["id"], s["id"])
            for g in valid_map["groups"]
            for s in valid_map["sources"]["active"]
        }
        assert owed < all_pairs, "the derivation is not narrowing anything"
        assert {g for g, _ in owed} == {
            g["id"] for g in valid_map["groups"] if g["type"] in ("ml-task", "domain-term")
        }
        assert V.validate_search(valid_search, valid_map, registry) == []

    def test_a_cell_outside_the_owed_set_fails(self, valid_search, valid_map, registry):
        """MIRROR: searching an axis the angle does not declare puts one group's evidence under
        another angle's mechanism."""
        doc = copy.deepcopy(valid_search)
        doc["coverage"].append(
            {
                "group_id": "intent-benchmarks",
                "source_id": "huggingface-hub-api",
                "queries": ["GET /api/models?search=banking77"],
                "timestamp": "2026-09-02",
                "status": "reached",
                "returned": 1,
                "count_frame": "models matching the benchmark name",
                "kept": 0,
                "cause": None,
                "fallback_used": None,
            }
        )
        _resync(doc)
        assert "cell-in-applicable-set" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_duplicate_pair_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["coverage"].append(copy.deepcopy(doc["coverage"][0]))
        _resync(doc)
        assert "cell-pair-unique" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_cell_naming_an_unminted_group_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0]["group_id"] = "not-a-group"
        _resync(doc)
        assert "cell-group-known" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_cell_naming_a_non_active_source_fails(self, valid_search, valid_map, registry):
        """A source the map could not reach at wave 0 cannot have answered an angle."""
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0]["source_id"] = "zenodo-records"
        _resync(doc)
        assert "cell-source-excluded" in _rules(V.validate_search(doc, valid_map, registry))


class TestCountsAndCauses:
    def test_a_reached_cell_owes_both_counts(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0]["kept"] = None
        assert "reached-needs-counts" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_nonzero_return_owes_a_count_frame(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0]["count_frame"] = "  "
        assert "count-frame-required" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_zero_return_owes_no_frame(self, valid_search, valid_map, registry):
        """MIRROR: nothing was counted, so there is no frame to state."""
        doc = copy.deepcopy(valid_search)
        cell = doc["coverage"][0]
        cell.update(returned=0, count_frame=None)
        doc["candidates"] = [c for c in doc["candidates"] if c["found_by"] != "text-classification/huggingface-hub-api"]
        doc["unadmitted"] = [u for u in doc["unadmitted"] if u["found_by"] != "text-classification/huggingface-hub-api"]
        _resync(doc)
        assert V.validate_search(doc, valid_map, registry) == []

    def test_kept_above_returned_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0]["returned"] = 1
        assert "kept-exceeds-returned" in _rules(V.validate_search(doc, valid_map, registry))

    def test_an_unreached_cell_may_not_carry_a_count(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["coverage"][-1].update(status="gated", cause="HTTP 401", returned=0, kept=0)
        assert "coverage-unreached-has-count" in _rules(
            V.validate_search(doc, valid_map, registry)
        )

    def test_an_unreached_cell_owes_a_cause(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["coverage"][-1].update(status="gated", cause=None, returned=None, kept=None)
        assert "status-needs-cause" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_reached_cell_owes_no_cause(self, valid_search, valid_map, registry):
        """MIRROR."""
        assert V.validate_search(valid_search, valid_map, registry) == []

    def test_dropping_the_summary_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc.pop("retrieval_summary")
        assert "summary-required" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_disagreeing_summary_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["retrieval_summary"]["status_counts"] = {"reached": 99}
        assert "summary-reconciles" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_declared_zero_in_the_summary_is_not_a_mismatch(
        self, valid_search, valid_map, registry
    ):
        """"We had no gated cells" is a reasonable thing to write down, and comparing raw dicts
        rejected it. A zero carries nothing the cells do not already say."""
        doc = copy.deepcopy(valid_search)
        doc["retrieval_summary"]["status_counts"] = {"reached": 4, "gated": 0}
        assert V.validate_search(doc, valid_map, registry) == []


class TestOutcomeBranches:
    def test_not_run_with_cells_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["outcome"] = "not_run"
        assert "unrun-angle-has-cells" in _rules(V.validate_search(doc, valid_map, registry))

    def test_not_run_with_candidates_fails(self, valid_search, valid_map, registry):
        """#34. The cell half of this mirror is the obvious one; candidates are the layer
        synthesis actually reads."""
        doc = copy.deepcopy(valid_search)
        doc.update(outcome="not_run", coverage=[])
        doc["retrieval_summary"]["status_counts"] = {}
        assert "unrun-angle-has-candidates" in _rules(V.validate_search(doc, valid_map, registry))

    def test_not_run_with_neither_passes(self, valid_search, valid_map, registry):
        """MIRROR: an angle its own map verdict ruled out MUST be empty, and the gate requires it."""
        doc = copy.deepcopy(valid_search)
        doc.update(outcome="not_run", coverage=[], candidates=[], unadmitted=[])
        doc.pop("retrieval_summary")
        assert V.validate_search(doc, valid_map, registry) == []

    def test_ran_with_no_cells_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc.update(coverage=[], candidates=[], unadmitted=[])
        doc.pop("retrieval_summary")
        assert "ran-requires-coverage" in _rules(V.validate_search(doc, valid_map, registry))

    def test_vacated_with_candidates_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["outcome"] = "vacated"
        assert "vacated-not-empty" in _rules(V.validate_search(doc, valid_map, registry))


class TestKeptReconciles:
    """`kept` counts rows carried into candidates PLUS unadmitted — the reading three shipped
    siblings use, and the one that makes the check an EQUALITY rather than a direction.

    Counting only candidates scores a row found and dropped WITHOUT a record as correct, which is
    the one thing `unadmitted` exists to make impossible.
    """

    def test_more_kept_than_rows_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0]["kept"] += 1
        assert "kept-matches-rows" in _rules(V.validate_search(doc, valid_map, registry))

    def test_fewer_kept_than_rows_fails(self, valid_search, valid_map, registry):
        """MIRROR: under-reporting hides a row from the arithmetic exactly as over-reporting
        invents one."""
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0]["kept"] -= 1
        assert "kept-matches-rows" in _rules(V.validate_search(doc, valid_map, registry))

    def test_an_unadmitted_row_counts_toward_kept(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["unadmitted"].append(
            {
                "item": "another checkpoint",
                "found_by": "summarization/huggingface-hub-api",
                "reason": "no card, so no evidence to quote",
            }
        )
        _resync(doc)
        assert V.validate_search(doc, valid_map, registry) == []

    def test_dropping_a_row_without_recording_it_FAILS(self, valid_search, valid_map, registry):
        """The case a candidates-only equality called correct: a row carried forward that left no
        trace anywhere. Deleting the record used to be free."""
        doc = copy.deepcopy(valid_search)
        doc["unadmitted"] = [
            u for u in doc["unadmitted"] if u["found_by"] != "support-ticket/huggingface-hub-api"
        ]
        assert "kept-matches-rows" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_row_naming_a_cell_that_does_not_exist_fails(
        self, valid_search, valid_map, registry
    ):
        doc = copy.deepcopy(valid_search)
        doc["unadmitted"][0]["found_by"] = "summarization/openml-api"
        assert "row-cell-unknown" in _rules(V.validate_search(doc, valid_map, registry))


class TestCandidateGrammar:
    def test_a_duplicate_item_id_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["candidates"].append(copy.deepcopy(doc["candidates"][0]))
        _resync(doc)
        assert "candidate-id-unique" in _rules(V.validate_search(doc, valid_map, registry))

    def test_id_class_must_agree_with_the_prefix(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["id_class"] = "WEB"
        assert "id-class-shape" in _rules(V.validate_search(doc, valid_map, registry))

    @pytest.mark.parametrize(
        "bad_body",
        ["a/b/c", "has--double", "has..dots", "repo.git"],
    )
    def test_a_body_the_hub_grammar_forbids_fails(
        self, bad_body, valid_search, valid_map, registry
    ):
        """The grammar is the Hub's, not ours: at most one `/`, no `--`, no `..`, no trailing
        `.git`. An id that violates it resolves to nothing."""
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["item_id"] = f"HF-{bad_body}"
        assert "hub-id-grammar" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_legal_hub_id_passes(self, valid_search, valid_map, registry):
        """MIRROR: the common case is a namespaced repo id, and rejecting it would reject the
        corpus."""
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["item_id"] = "HF-google/flan-t5-base"
        assert V.validate_search(doc, valid_map, registry) == []

    def test_a_bench_slug_may_not_carry_the_hashed_stem_marker(
        self, valid_search, valid_map, registry
    ):
        """`--` is the marker `record_filename`'s hashing branch appends. A minted slug carrying
        it can collide with the sanitized form of a different id."""
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0].update(item_id="BENCH-banking--77", id_class="BENCH")
        assert "bench-slug-marker" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_candidate_from_no_recorded_cell_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["found_by"] = "summarization/openml-api"
        _resync(doc)
        assert "candidate-provenance" in _rules(V.validate_search(doc, valid_map, registry))

    def test_an_evaluation_without_a_split_fails(self, valid_search, valid_map, registry):
        """A rank is a claim under a stated evaluation, on a stated split, at a stated date."""
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["evaluation"] = {
            "benchmark": "banking77",
            "split": "  ",
            "measured_on": "2026-05-01",
        }
        assert "evaluation-needs-split" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_complete_evaluation_passes(self, valid_search, valid_map, registry):
        """MIRROR: a result WITH its frame is exactly what this angle wants recorded."""
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["evaluation"] = {
            "benchmark": "banking77",
            "split": "test",
            "measured_on": "2026-05-01",
            "metric": "accuracy",
            "value": 0.93,
        }
        assert V.validate_search(doc, valid_map, registry) == []

    def test_no_evaluation_at_all_is_legal(self, valid_search, valid_map, registry):
        """MIRROR, and the common case: a1 finds what EXISTS; a3 is where evaluated numbers come
        from. Demanding one here would push a producer to invent it."""
        assert all(c.get("evaluation") is None for c in valid_search["candidates"])
        assert V.validate_search(valid_search, valid_map, registry) == []


class TestBoundAndFallback:
    def test_a_cap_the_registry_does_not_set_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["bound"]["cap"] = 999
        assert "cap-matches-registry" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_LOWERED_cap_fails_too(self, valid_search, valid_map, registry):
        """MIRROR: quietly lowering the ceiling shrinks a survey, which is the direction that
        hides work rather than inventing it."""
        doc = copy.deepcopy(valid_search)
        doc["bound"]["cap"] = 2
        assert "cap-matches-registry" in _rules(V.validate_search(doc, valid_map, registry))

    def test_hit_without_a_dropped_note_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["bound"]["hit"] = True
        assert "bound-hit-needs-note" in _rules(V.validate_search(doc, valid_map, registry))

    def test_not_hit_owes_no_note(self, valid_search, valid_map, registry):
        """MIRROR: nothing was truncated, so there is nothing to describe."""
        assert V.validate_search(valid_search, valid_map, registry) == []

    def test_a_blank_ordering_fails(self, valid_search, valid_map, registry):
        """`minLength: 1` is satisfied by a space — whitespace is how a required string gets
        silenced without anything noticing."""
        doc = copy.deepcopy(valid_search)
        doc["bound"]["ordering"] = "   "
        assert "bound-hit-consistent" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_fallback_without_its_level_fails(self, valid_search, valid_map, registry):
        """Every row names a fallback and every angle names one; they differ, and a bare id
        cannot say which was walked."""
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0]["fallback_used"] = "ngc-catalog"
        assert "fallback-declared" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_levelled_fallback_passes(self, valid_search, valid_map, registry):
        """MIRROR."""
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0]["fallback_used"] = "angle:ngc-catalog"
        assert V.validate_search(doc, valid_map, registry) == []

    def test_a_fallback_resolving_to_nothing_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0]["fallback_used"] = "row:not-a-source"
        assert "fallback-declared" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_degraded_cell_must_appear_in_the_summary(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["coverage"][-1].update(
            status="gated", cause="HTTP 401 on every dataset", returned=None, kept=None
        )
        doc["candidates"] = [
            c for c in doc["candidates"] if c["found_by"] != "support-ticket/huggingface-hub-api"
        ]
        doc["unadmitted"] = [
            u for u in doc["unadmitted"] if u["found_by"] != "support-ticket/huggingface-hub-api"
        ]
        doc["retrieval_summary"]["status_counts"] = {"reached": 3, "gated": 1}
        assert "degraded-source-recorded" in _rules(V.validate_search(doc, valid_map, registry))


class TestNoUnreachableCode:
    """A `return` followed by more statements in the same block is dead code that reads as shipped.

    It happened here: the whole candidate/kept/bound half of `validate_search` was appended after
    a `return out` and never ran. The clean fixture passed either way, so nothing but the negative
    tests noticed — which is precisely the shape of a rule that "exists" and enforces nothing.
    """

    def test_no_statement_follows_a_return_in_any_block(self):
        import ast

        tree = ast.parse(SCRIPT.read_text())
        dead = []
        for node in ast.walk(tree):
            body = getattr(node, "body", None)
            if not isinstance(body, list):
                continue
            for i, stmt in enumerate(body[:-1]):
                if isinstance(stmt, (ast.Return, ast.Raise)):
                    nxt = body[i + 1]
                    dead.append(f"{type(node).__name__} line {nxt.lineno}")
        assert not dead, dead

    def test_every_rule_id_the_module_emits_is_reachable(self):
        """A rule defined in a branch nothing can enter is the same defect one level down."""
        ids = set(re.findall(r'_fail\(\s*"([a-z0-9-]+)"', SCRIPT.read_text()))
        assert len(ids) >= 30, sorted(ids)
        # The idiom is deliberately uniform: `assert "<rule>" in _rules(...)`. A test that binds
        # the result to a local first is invisible here, so the guard would pass while the rule
        # went untested — which is the failure it exists to prevent, one level up.
        tested = set(re.findall(r'"([a-z0-9-]+)" in _rules', Path(__file__).read_text()))
        # Exempt ONLY the rules whose negative test is a subprocess assertion on stdout rather
        # than an `in _rules(...)` call — they are tested, just not through that idiom.
        via_subprocess = {"schema", "registry-unreadable", "keyword-map-invalid", "input",
                          "dependency-missing"}
        untested = ids - tested - via_subprocess
        assert not untested, f"rules with no negative test: {sorted(untested)}"
        for rule in sorted(via_subprocess - {"schema", "registry-unreadable"}):
            assert rule in Path(__file__).read_text(), f"{rule} is exempt but never asserted"


class TestRecordFilename:
    """#42, both parts. This type is the MOST exposed of the ten: `HF-`, `HFD-` and `DOI-` ids
    essentially always carry a `/`, so the sanitizing branch is the COMMON case and there is no
    version of this type in which part (b) looks optional.
    """

    def test_a_filename_safe_id_is_returned_unchanged(self):
        assert V.record_filename("BENCH-banking77") == "BENCH-banking77"

    def test_a_slash_carrying_id_is_sanitized_with_a_digest(self):
        out = V.record_filename("HF-facebook/bart-large-mnli")
        assert "/" not in out
        assert re.search(r"--[0-9a-f]{12}$", out)

    def test_part_b_REFUSES_an_id_that_already_looks_hashed(self):
        """Without this the two branches share an output namespace: a caller could pass the hashed
        stem of one id and get it back unchanged, colliding with the id it came from."""
        stem = V.record_filename("HF-facebook/bart-large-mnli")
        assert V.record_filename(stem) != stem

    def test_the_cross_branch_collision_property_holds(self):
        """The test that gave a sibling FALSE assurance was within-branch: it passes while
        `f(f(x))` collides. This one spans every prefix and asserts injectivity across branches."""
        ids = [
            "HF-facebook/bart-large-mnli",
            "HF-facebook-bart-large-mnli",
            "HFD-squad/plain-text",
            "API-openai-gpt-4o-mini",
            "OPENML-D-1596",
            "DOI-10.1145/3313831.3376283",
            "DOI-10.1145-3313831.3376283",
            "BENCH-banking77",
            "WEB-https://example.com/a/b",
        ]
        stems = [V.record_filename(i) for i in ids]
        assert len(set(stems)) == len(stems), "two distinct ids share a stem"
        for i, stem in zip(ids, stems):
            assert V.record_filename(stem) != stem or stem == i

    def test_a_long_id_is_capped_and_still_distinct(self):
        a = V.record_filename("HF-org/" + "x" * 200 + "/one")
        b = V.record_filename("HF-org/" + "x" * 200 + "/two")
        assert a != b, "the digest must still separate them"
        assert len(a.rsplit("--", 1)[0]) == V._PREFIX_CAP

    def test_an_id_with_no_usable_characters_still_yields_a_filename(self):
        assert V.record_filename("///").startswith("--")


class TestCLI:
    """#51: the brief runs `main()`, not the functions. A sibling shipped two subcommands `main()`
    never routed, and both survived a large suite because every test called the functions."""

    def _cli(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            capture_output=True,
            text=True,
            cwd=HERE,
            check=False,
        )

    def test_every_registered_subcommand_is_reachable(self):
        assert V.registered_subcommands() == {"keyword-map", "search"}
        for cmd in V.registered_subcommands():
            r = self._cli(cmd, "--help")
            assert r.returncode == 0, (cmd, r.stderr)

    def test_a_clean_map_exits_0(self):
        assert self._cli("keyword-map", str(FIXTURES / "ml-task-vocabulary-map.valid.yaml")).returncode == 0

    def test_a_clean_search_exits_0(self):
        r = self._cli(
            "search",
            str(FIXTURES / "search-output.valid.yaml"),
            "--keyword-map",
            str(FIXTURES / "ml-task-vocabulary-map.valid.yaml"),
        )
        assert r.returncode == 0, r.stdout

    def test_an_artifact_with_findings_exits_1_with_a_grepable_line(self, tmp_path, valid_map):
        bad = tmp_path / "map.yaml"
        doc = copy.deepcopy(valid_map)
        doc["angle_applicability"] = doc["angle_applicability"][:-1]
        bad.write_text(yaml.safe_dump(doc))
        r = self._cli("keyword-map", str(bad))
        assert r.returncode == 1
        assert r.stdout.startswith("FAIL ")

    @pytest.mark.parametrize("body", ["- a\n- b\n", "", "just a string\n"])
    def test_an_unusable_keyword_map_exits_2(self, body, tmp_path):
        """Exit 1 means "the artifact under test has findings". Sending that for a bad CALLER
        input dispatches an author to edit a file that is correct."""
        bad = tmp_path / "km.yaml"
        bad.write_text(body)
        r = self._cli(
            "search", str(FIXTURES / "search-output.valid.yaml"), "--keyword-map", str(bad)
        )
        assert r.returncode == 2, (r.returncode, r.stdout)
        assert "keyword-map-invalid" in r.stdout

    def test_a_missing_file_exits_2(self, tmp_path):
        r = self._cli("keyword-map", str(tmp_path / "nope.yaml"))
        assert r.returncode == 2
        assert "FAIL input" in r.stdout

    @pytest.mark.parametrize("kind", ["artifact", "keyword-map"])
    def test_a_non_utf8_file_exits_2(self, kind, tmp_path):
        """`UnicodeDecodeError` is a ValueError, not an OSError, so an `except OSError` that looks
        exhaustive lets it escape as a traceback at exit 1."""
        bad = tmp_path / "bad.bin"
        bad.write_bytes(b"\xff\xfe\x00\x01 not utf8")
        r = (
            self._cli("keyword-map", str(bad))
            if kind == "artifact"
            else self._cli(
                "search", str(FIXTURES / "search-output.valid.yaml"), "--keyword-map", str(bad)
            )
        )
        assert r.returncode == 2, (r.returncode, r.stdout, r.stderr)
        assert "FAIL input" in r.stdout

    def test_a_missing_dependency_exits_2_and_the_guard_does_not_RAISE(self, tmp_path):
        """Two properties in one place, because they fail together. The shared root guard
        `exec_module`s this file: a raising import turns that test into an ERROR rather than a run,
        which is the silent-skip failure one level down."""
        stub = tmp_path / "yaml.py"
        stub.write_text("raise ModuleNotFoundError(name='yaml')\n")
        env = {"PYTHONPATH": str(tmp_path), "PATH": "/usr/bin:/bin"}
        r = subprocess.run(
            [sys.executable, str(SCRIPT), "keyword-map", "x.yaml"],
            capture_output=True, text=True, cwd=HERE, check=False, env=env,
        )
        assert r.returncode == 2, (r.returncode, r.stdout, r.stderr)
        assert "dependency-missing" in r.stdout
        assert "Traceback" not in r.stderr


class TestRulesTheCoverageGuardFound:
    """Three rules shipped with no negative test until the reachability guard named them.

    Worth recording rather than quietly fixing: the guard is doing what a coverage assertion is
    for, on its first run, against its own author.
    """

    def test_a_candidate_naming_an_unminted_group_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["found_by"] = "not-a-group/huggingface-hub-api"
        _resync(doc)
        assert "candidate-group-known" in _rules(V.validate_search(doc, valid_map, registry))

    def test_not_hit_above_the_cap_fails(self, valid_search, valid_map, registry):
        """`hit: false` is the STRONGER claim — every admissible candidate is present — and it
        cannot hold above the ceiling."""
        doc = copy.deepcopy(valid_search)
        doc["bound"].update(cap=40, hit=False)
        doc["candidates"] = doc["candidates"] * 9
        assert "cap-respected" in _rules(V.validate_search(doc, valid_map, registry))

    def test_not_hit_at_or_under_the_cap_passes(self, valid_search, valid_map, registry):
        """MIRROR."""
        assert V.validate_search(valid_search, valid_map, registry) == []

    def test_a_cell_naming_a_source_in_no_registry_row_fails(
        self, valid_search, valid_map, registry
    ):
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0]["source_id"] = "not-a-source-at-all"
        _resync(doc)
        assert "cell-source-known" in _rules(V.validate_search(doc, valid_map, registry))
