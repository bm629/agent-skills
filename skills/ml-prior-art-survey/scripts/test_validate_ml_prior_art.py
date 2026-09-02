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

    def test_two_groups_differing_only_in_id_pass(self, valid_map, registry):
        """MIRROR, mutated TOWARD the boundary: two groups with the same type and canonical but
        distinct ids are legitimate. Asserting the unmutated fixture instead would have passed
        with the rule deleted."""
        doc = copy.deepcopy(valid_map)
        twin = copy.deepcopy(doc["groups"][0])
        twin["id"] = twin["id"] + "-alt"
        doc["groups"].append(twin)
        assert V.validate_keyword_map(doc, registry) == []

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
        """MIRROR, at the boundary: an EMPTY expansion list on a modality group is legal, where
        the same emptiness on an ml-task group fails. The rule is per-axis, and a test that only
        read the fixture would pass with the axis check deleted."""
        doc = copy.deepcopy(valid_map)
        g = next(x for x in doc["groups"] if x["type"] == "modality")
        g["expansions"] = []
        assert V.validate_keyword_map(doc, registry) == []
        g["type"] = "ml-task"
        g["borrowed_from"] = "huggingface-pipeline-tag"
        assert "expansion-floor" in _rules(V.validate_keyword_map(doc, registry))

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
        """MIRROR, at the boundary: `ran: true` with a terse note is legal — the rule is about a
        SKIPPED probe, and firing on a short note would demand prose for its own sake."""
        doc = copy.deepcopy(valid_map)
        doc["probe"] = {"ran": True, "note": "Probed the task terms; the corpus answered."}
        assert V.validate_keyword_map(doc, registry) == []


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
        """MIRROR, at the boundary: `clean` with an explicit null cause must pass — the rule is
        about a non-clean status, and firing here would make the honest record illegal."""
        doc = copy.deepcopy(valid_map)
        doc["sources"]["active"][0]["sanitization"] = {"status": "clean", "cause": None}
        assert V.validate_keyword_map(doc, registry) == []

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
        # DERIVED: a source the registry knows and this map did NOT record active. Hard-coding one
        # broke the moment the fixture's active list grew, and the test then passed on a different
        # rule entirely.
        active = {r["id"] for r in valid_map["sources"]["active"]}
        known = {s["id"] for s in registry["sources"]}
        inactive = sorted(known - active)
        assert inactive, "every registry source is active; this test has no input"
        doc["coverage"][0]["source_id"] = inactive[0]
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
        """MIRROR, at the boundary: a reached cell that returned NOTHING still owes no cause —
        the zero is the evidence, and demanding a cause would push producers to omit the cell."""
        doc = copy.deepcopy(valid_search)
        cell = next(c for c in doc["coverage"] if c["status"] == "reached" and c["returned"] == 0)
        assert cell["cause"] is None
        assert V.validate_search(doc, valid_map, registry) == []

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
        counts = collections.Counter(c["status"] for c in doc["coverage"])
        doc["retrieval_summary"]["status_counts"] = {**counts, "gated": 0}
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
        """MIRROR, at the boundary: an explicit `evaluation: null` passes where a block with a
        blank split fails. a1 finds what EXISTS; a3 is where evaluated numbers come from, and
        demanding one here would push a producer to invent it."""
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["evaluation"] = None
        assert V.validate_search(doc, valid_map, registry) == []


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
        """MIRROR, at the boundary: `hit: false` with an explicit null note passes. The rule is
        about a truncation that happened."""
        doc = copy.deepcopy(valid_search)
        doc["bound"].update(hit=False, dropped_note=None)
        assert V.validate_search(doc, valid_map, registry) == []

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
            # `orelse` and `finalbody` too: the first version walked `body` only, so an
            # `if x: return` / `else: <unreachable>` sat outside the guard whose docstring says it
            # caught a real shipped defect.
            for attr in ("body", "orelse", "finalbody"):
                block = getattr(node, attr, None)
                if not isinstance(block, list):
                    continue
                for i, stmt in enumerate(block[:-1]):
                    if isinstance(stmt, (ast.Return, ast.Raise)):
                        dead.append(f"{type(node).__name__}.{attr} line {block[i + 1].lineno}")
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
        # `<=`, not `==`: record_filename strips a trailing hyphen after truncating, so an id whose
        # 80th character is `-` yields a shorter prefix with no behaviour change. The property is
        # that the cap BOUNDS it.
        assert len(a.rsplit("--", 1)[0]) <= V._PREFIX_CAP
        assert len(a.rsplit("--", 1)[0]) >= V._PREFIX_CAP - 1

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

    def test_candidates_exactly_AT_the_cap_pass(self, valid_search, valid_map, registry):
        """MIRROR, at the boundary: the cap is a ceiling, not a target, so equality is legal.
        Asserting the unmutated fixture tested nothing — it sits far below the cap."""
        doc = copy.deepcopy(valid_search)
        cap = doc["bound"]["cap"]
        base = doc["candidates"][0]
        doc["candidates"] = [
            {**copy.deepcopy(base), "item_id": f"WEB-example-{i}", "id_class": "WEB"}
            for i in range(cap)
        ]
        doc["unadmitted"] = []
        _resync(doc)
        assert len(doc["candidates"]) == cap
        assert "cap-respected" not in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_cell_naming_a_source_in_no_registry_row_fails(
        self, valid_search, valid_map, registry
    ):
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0]["source_id"] = "not-a-source-at-all"
        _resync(doc)
        assert "cell-source-known" in _rules(V.validate_search(doc, valid_map, registry))


class TestAngleReferenceContract:
    """C3. Nine references, one per registry angle, checked in BOTH directions (#34).

    One direction alone lets an orphan sit shipped and unused: a source named in a reference that
    no registry row carries is an unreachable instruction, and a registry source no reference
    mentions is a channel nobody was told to walk.
    """

    REFS = HERE.parent / "references" / "angles"

    def _body(self, aid: str) -> str:
        return (self.REFS / f"{aid}.md").read_text()

    def test_every_registry_angle_has_a_reference(self, registry):
        for a in registry["angles"]:
            assert (self.REFS / f"{a['id']}.md").exists(), a["id"]

    def test_every_reference_names_a_registry_angle(self, registry):
        ids = {a["id"] for a in registry["angles"]}
        for f in self.REFS.glob("*.md"):
            assert f.stem in ids, f.stem

    def test_every_source_a_reference_names_resolves(self, registry):
        """The reference's own Sources line, parsed and resolved.

        The first version skipped every token it did not already recognise and then asserted
        against a literal — it could only have failed if a reference contained the exact string
        `not-a-source`. It tested nothing, and would have passed with the behaviour deleted.
        """
        known = {s["id"] for s in registry["sources"]}
        for a in registry["angles"]:
            line = next(
                ln for ln in self._body(a["id"]).splitlines() if ln.startswith("- **Sources:**")
            )
            named = set(re.findall(r"`([a-z0-9-]+)`", line))
            assert named, a["id"]
            assert named <= known, (a["id"], sorted(named - known))

    def test_every_declared_source_appears_in_its_own_reference(self, registry):
        """The direction that catches an orphan: a source the registry gives an angle and the
        reference never mentions is a channel the child is never told to walk."""
        for a in registry["angles"]:
            body = self._body(a["id"])
            for sid in a["sources"] + [a["fallback"]]:
                assert f"`{sid}`" in body, (a["id"], sid)

    def test_every_reference_states_its_cap_and_ordering(self, registry):
        for a in registry["angles"]:
            body = self._body(a["id"])
            assert f"**Cap:** {a['cap']}" in body, a["id"]
            assert a["ordering_signal"].split(",")[0] in body, a["id"]

    def test_every_reference_states_the_axes_it_searches(self, registry):
        for a in registry["angles"]:
            body = self._body(a["id"])
            for t in a["applicable_group_types"]:
                assert f"`{t}`" in body, (a["id"], t)

    def test_every_conditional_reference_argues_it_is_not_a_tautology(self, registry):
        """#53. An angle whose predicate restates the type trigger fires on every survey, and the
        conditional marking is then decorative."""
        for a in registry["angles"]:
            if a["trigger"] != "conditional":
                continue
            assert "not a tautology" in self._body(a["id"]), a["id"]

    def test_no_always_on_reference_claims_a_trigger(self, registry):
        """MIRROR: an always-on angle that describes a precondition is a conditional angle
        someone forgot to mark, and the reference is where that shows first."""
        for a in registry["angles"]:
            if a["trigger"] != "always":
                continue
            assert "always-on angle" in self._body(a["id"]), a["id"]
            assert "not a tautology" not in self._body(a["id"]), a["id"]


class TestGuideExamplesValidate:
    """C4. A worked example that does not validate teaches a shape the gate rejects.

    5j's guide shipped one coverage cell for an angle declaring eleven sources — plausible prose,
    wrong lesson, and the file a producer learns the format from.
    """

    REFS = HERE.parent / "references"

    @staticmethod
    def _restore_sources(doc: dict, registry: dict) -> None:
        holds = {v["angle_id"] for v in doc["angle_applicability"] if v["holds"]}
        have = {r["id"] for r in doc["sources"]["active"]}
        have |= {r["id"] for r in doc["sources"]["skipped"]}
        for angle in registry["angles"]:
            if angle["id"] not in holds:
                continue
            for sid in angle["sources"]:
                if sid not in have:
                    doc["sources"]["active"].append({
                        "id": sid, "release": None, "as_of": None,
                        "access_status": "open", "sanitization": {"status": "clean"},
                    })
                    have.add(sid)

    def _blocks(self, name: str) -> list[dict]:
        """Every fenced YAML block, in order."""
        text = (self.REFS / name).read_text()
        return [yaml.safe_load(b) for b in re.findall(r"```yaml\n(.*?)```", text, re.S)]

    def _example(self, name: str) -> dict:
        """The WORKED EXAMPLE — the block carrying a `schema_version`.

        Selected by content, not by position: a guide may legitimately show a one-field snippet
        before its full example, and `blocks[0]` then validates the snippet and reports the
        example as clean. That happened the moment a `queries:` snippet was added.
        """
        full = [b for b in self._blocks(name) if isinstance(b, dict) and "schema_version" in b]
        assert full, f"no worked example with a schema_version in {name}"
        return full[0]

    def test_the_map_guide_example_validates(self, registry):
        doc = self._example("ml-task-vocabulary-map-guide.md")
        # The example elides verdicts and sources behind comments for readability; restore them
        # from the registry so the check is about the SHAPE the example teaches, not the length it
        # was trimmed to. What it DOES show must be right; what it omits is the guide's choice.
        have = {v["angle_id"] for v in doc["angle_applicability"]}
        for a in registry["angles"]:
            if a["id"] not in have:
                doc["angle_applicability"].append(
                    {
                        "angle_id": a["id"],
                        "precondition": a["precondition"],
                        "holds": a["trigger"] == "always",
                        "reason": "elided in the guide for length; restored by the test",
                    }
                )
        self._restore_sources(doc, registry)
        assert V.validate_keyword_map(doc, registry) == []

    def test_the_search_guide_example_validates(self, registry):
        blocks = [self._example("search-output-guide.md")]
        kmap = self._example("ml-task-vocabulary-map-guide.md")
        have = {v["angle_id"] for v in kmap["angle_applicability"]}
        for a in registry["angles"]:
            if a["id"] not in have:
                kmap["angle_applicability"].append(
                    {
                        "angle_id": a["id"],
                        "precondition": a["precondition"],
                        "holds": a["trigger"] == "always",
                        "reason": "elided in the guide for length; restored by the test",
                    }
                )
        assert V.validate_search(blocks[0], kmap, registry) == []

    def test_the_two_worked_examples_use_DIFFERENT_scopes(self):
        """5j shipped a SKILL example and a guide example reading the identical scope string in
        opposite directions, which flips two conditional angles. An agent taking the guide as its
        template ships the opposite map and never sees the choice."""
        guide = self._example("ml-task-vocabulary-map-guide.md")["meta"]["scope_ref"]
        fixture = yaml.safe_load(
            (FIXTURES / "ml-task-vocabulary-map.valid.yaml").read_text()
        )["meta"]["scope_ref"]
        assert guide != fixture


# Response keys of the HuggingFace Hub API. a1 requires cards be resolved with `?full=true`, whose
# response carries fields and no prose at all, so an `evidence_quote` from this angle IS one of
# these — which means the prose has to name them. They are THEIR grammar, not ours: enumerated
# rather than pattern-matched, so prose naming a real Hub field passes and prose naming an invented
# one still fails. Before this set the guards knew only "our field" and "our source id", and one
# external name sat inlined in two `known` sets where it could drift apart.
HUB_API_FIELDS = frozenset({
    "pipeline_tag", "library_name", "model-index", "cardData", "lastModified",
    "createdAt", "downloads", "likes", "tags", "license", "datasets", "language",
})


class TestGuidesAndSchemasAgree:
    """#60, both directions. Every map schema is `additionalProperties: false`, so a field named
    in prose and absent from the schema is an artifact that cannot validate — and the producer's
    'fix and re-run until exit 0' loop then has no legal fix."""

    REFS = HERE.parent / "references"

    @staticmethod
    def _schema_fields(name: str) -> set[str]:
        import json as _json

        schema = _json.loads((HERE.parent / "schemas" / f"{name}.schema.json").read_text())
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

        walk(schema)
        return found

    @pytest.mark.parametrize(
        "field",
        [
            "count_frame", "found_by", "evidence_quote", "claim", "finding", "evaluation",
            "negative_terms", "expansion_cap", "borrowed_from", "absent_types", "sanitization",
            "ordering_deviation", "dropped_note", "unadmitted", "probe", "lineage",
        ],
    )
    def test_a_field_the_prose_instructs_exists_in_a_schema(self, field):
        fields = self._schema_fields("ml-task-vocabulary-map") | self._schema_fields("search-output")
        assert field in fields, field

    def test_the_hub_field_set_is_not_a_blanket_license(self):
        """Both directions, like the portability allowlist next door. An exemption is only worth
        having if the thing it exempts still fails when it is not on the list — a set that admits
        anything Hub-shaped would let prose invent a field and call it theirs."""
        field_re = re.compile(r"`([a-z][a-z0-9]*(?:_[a-z0-9]+)+)`")
        fields = self._schema_fields("ml-task-vocabulary-map") | self._schema_fields("search-output")

        real = set(field_re.findall("resolve the card and read `library_name`"))
        assert real == {"library_name"}, real
        assert not (real - (fields | HUB_API_FIELDS)), "a real Hub field must pass"

        invented = set(field_re.findall("resolve the card and read `library_flavour`"))
        assert invented == {"library_flavour"}, invented
        assert invented - (fields | HUB_API_FIELDS), "an invented Hub field must still fail"

    def test_no_guide_names_a_field_no_schema_has(self):
        fields = self._schema_fields("ml-task-vocabulary-map") | self._schema_fields("search-output")
        # Backticked snake_case tokens in the guides that look like field names.
        named = set()
        for p in self.REFS.glob("*.md"):
            named |= set(re.findall(r"`([a-z][a-z0-9]*(?:_[a-z0-9]+)+)`", p.read_text()))
        known = fields | HUB_API_FIELDS | {
            "type_trigger", "applicable_group_types", "trigger_anchor",
            "coherence_axioms", "widening_legs", "predicate_omits", "cap_rationale",
            "ordering_signal", "fallback_rationale", "access_status", "unreached_in_wave_1",
            "registry_version", "group_type", "scope_ref", "status_counts", "degraded_sources",
            "source_claimed_modified_at", "source_claim_provenance", "retrieved_at",
            "schema_version", "item_id", "id_class", "group_id", "source_id", "angle_id",
            "measured_on", "retrieval_summary", "not_run", "as_of", "arxiv_id", "code_url",
            "expansion_floor", "background_removal",
        }
        assert not (named - known), sorted(named - known)


SKILL = HERE.parent / "SKILL.md"


class TestProducerSkillContract:
    """C5. The properties of SKILL.md that nothing else checks, because it is prose."""

    @staticmethod
    def _frontmatter() -> dict:
        """PARSED, not pattern-matched. A hand-rolled regex from `description: >` to the closing
        `---` is the whole block only while nothing follows the description; adding `version`
        folds it in and the character cap fires on a field it was not measuring."""
        return yaml.safe_load(SKILL.read_text().split("---", 2)[1])

    def test_the_description_is_within_the_cap(self):
        desc = " ".join(self._frontmatter()["description"].split())
        assert len(desc) <= 1024, len(desc)

    def test_the_description_says_wave_1_only(self):
        """The frontmatter is what a router reads. A skill that does not say what it does NOT do
        gets dispatched for the extract wave it cannot perform."""
        assert "WAVE 1 ONLY" in self._frontmatter()["description"]

    def test_both_procedures_are_numbered_without_a_gap(self):
        body = SKILL.read_text()
        for proc in re.findall(r"### Procedure \d+ —.*?(?=\n### |\n## )", body, re.S):
            nums = [int(m) for m in re.findall(r"^(\d+)\. ", proc, re.M)]
            assert nums == list(range(1, len(nums) + 1)), nums

    def test_the_documented_invocation_states_its_dependencies(self):
        """The documented command must RUN. A bare `python` lacking pyyaml dies with a traceback
        at exit 1 — the artifact-has-findings code — so a cold agent has an exit gate it cannot
        satisfy and no way to know the fault is not its own."""
        body = SKILL.read_text()
        assert "--with pyyaml" in body and "--with jsonschema" in body
        assert "scripts/validate_ml_prior_art.py" in body

    def test_the_external_content_posture_is_present(self):
        assert "External content is DATA" in SKILL.read_text()

    def test_the_quality_bar_does_not_route_through_an_uninstalled_package(self):
        """A sibling's cold run could not read the twin at all — it is not installed beside the
        producer in the projects these ship to."""
        body = SKILL.read_text()
        assert "single source of the quality bar" not in body
        assert "if it is installed" in body

    def test_every_reference_it_promises_exists(self):
        for path in re.findall(r"`(references/[a-z0-9/<>._-]+)`", SKILL.read_text()):
            if "<" in path:
                continue  # a placeholder like references/angles/<id>.md
            if path.endswith("conditions.md"):
                continue  # cross-package: it lives in the REVIEWING half, which C7 owns
            assert (HERE.parent / path).exists(), path

    def test_it_RESTATES_no_numbered_condition(self):
        """A restated bar is a bar that drifts."""
        body = SKILL.read_text()
        assert "VERDICT:" not in body
        assert not re.search(r"^\s*\*\*C[0-9]+", body, re.MULTILINE)


class TestProseAndSchemasAgree:
    """C6, the half whose inputs exist before the twin does.

    Both schemas are `additionalProperties: false`, so a field the prose instructs a producer to
    write and the schema does not declare is an artifact that CANNOT validate — and the SKILL's
    own "fix and re-run until exit 0" loop then has no legal fix. That was a four-blocker class in
    a sibling.
    """

    @staticmethod
    def _authored() -> list[Path]:
        """DERIVED by glob, never enumerated. A guard that names the files it was written from
        certifies those and licenses the rest — which has happened, twice, in this family."""
        out = [SKILL] + sorted((HERE.parent / "references").rglob("*.md"))
        assert len(out) >= 12, len(out)
        return out

    def test_no_prose_names_a_field_the_schemas_lack(self):
        fields = TestGuidesAndSchemasAgree._schema_fields("ml-task-vocabulary-map")
        fields |= TestGuidesAndSchemasAgree._schema_fields("search-output")
        known = fields | HUB_API_FIELDS | {
            "type_trigger", "applicable_group_types", "trigger_anchor",
            "coherence_axioms", "widening_legs", "predicate_omits", "cap_rationale",
            "ordering_signal", "fallback_rationale", "access_status", "unreached_in_wave_1",
            "registry_version", "group_type", "scope_ref", "status_counts", "degraded_sources",
            "source_claimed_modified_at", "source_claim_provenance", "retrieved_at",
            "schema_version", "item_id", "id_class", "group_id", "source_id", "angle_id",
            "measured_on", "retrieval_summary", "not_run", "as_of", "arxiv_id", "code_url",
            "expansion_floor", "background_removal", "full_true",
            # capability-map classification leaves, named in triggers and predicates.
            "data_ml", "risk_level", "eu_ai_act", "ml_involvement", "real_time",
            "availability_target", "geo_distribution", "data_volume", "has_ui",
        }
        named: set[str] = set()
        for p in self._authored():
            named |= set(re.findall(r"`([a-z][a-z0-9]*(?:_[a-z0-9]+)+)`", p.read_text()))
        assert not (named - known), sorted(named - known)

    def test_no_host_program_term_ships(self):
        """EC6. These packages ship to projects that cannot see the program that authored them.
        Case-insensitive and whole-package: a sibling's case-sensitive check reported zero while a
        playbook reference sat in a shippable file."""
        leak = re.compile(
            r"playbook ?#|spec L-|classification-schema|\b5[a-j]\b|disk-authoritative|"
            r"this ticket|agents-hq|coordinator|project_prior_art",
            re.I,
        )
        allowed = re.compile(r"agents-hq\.local/schemas/", re.I)
        offenders = []
        for p in self._authored() + sorted((HERE.parent / "schemas").glob("*.json")) + [
            HERE.parent / "references" / "source-registry.yaml"
        ]:
            for n, line in enumerate(p.read_text().splitlines(), 1):
                if leak.search(line) and not allowed.search(line):
                    offenders.append(f"{p.name}:{n}: {line.strip()[:80]}")
        assert not offenders, offenders

    def test_the_allowlist_actually_fires(self):
        """Proven in both directions: the pattern still matches the string it exempts, and the
        exemption still matches the real `$id`. An earlier version of this check used a pattern
        requiring a trailing space and matched neither."""
        real = '  "$id": "https://agents-hq.local/schemas/search-output.schema.json",'
        # The patterns under test, not re-declared copies: a change to the real allowlist would
        # not have been caught by the test named for it.
        leak = re.compile(
            r"playbook ?#|spec L-|classification-schema|\b5[a-j]\b|disk-authoritative|"
            r"this ticket|agents-hq|coordinator|project_prior_art",
            re.I,
        )
        allowed = re.compile(r"agents-hq\.local/schemas/", re.I)
        assert leak.search(real), "the pattern no longer matches the string it exempts"
        assert allowed.search(real), "the exemption no longer matches the real $id"

    def test_the_id_host_is_what_the_allowlist_expects(self):
        import json as _json

        for name in ("search-output", "ml-task-vocabulary-map"):
            schema = _json.loads((HERE.parent / "schemas" / f"{name}.schema.json").read_text())
            assert re.search(r"agents-hq\.local/schemas/", schema["$id"], re.I), schema["$id"]

    def test_no_authoring_reference_ships(self):
        """A dispatched agent cannot resolve "(playbook #53)" — the playbook lives in a program
        this package is explicitly told it cannot see."""
        pattern = re.compile(r"\(?playbook #\d+\)?|\(#\d{1,3}\)")
        for p in self._authored():
            m = pattern.search(p.read_text())
            assert not m, (p.name, m.group(0))


CONDITIONS = REVIEWER / "references" / "conditions.md"


class TestReviewerPackage:
    """C7. The reviewing half is prose, so its contract is checked here or nowhere."""

    def test_all_artifacts_exist(self):
        for rel in (
            "SKILL.md",
            "references/conditions.md",
            "references/sources.md",
            "references/fixtures/README.md",
            "references/fixtures/map.clean.yaml",
            "references/fixtures/search.clean.yaml",
        ):
            assert (REVIEWER / rel).exists(), rel

    def test_the_conditions_are_numbered_contiguously_from_one(self):
        """Contiguous as a SET, not in file order.

        Each condition lives under the artifact it judges, and C2 judges a search output while
        taking the map as its second input — so it sits in the search section, out of numeric
        order. The numbers are stable identities: a finding cites a number, and renumbering to
        restore file order would invalidate every report already written against them. What must
        hold is that no number is missing and none is reused.
        """
        found = [int(n) for n in re.findall(r"^\*\*C([0-9]+) ", CONDITIONS.read_text(), re.M)]
        assert len(found) == len(set(found)), f"a number is reused: {found}"
        assert sorted(found) == list(range(1, len(found) + 1)), sorted(found)
        assert len(found) >= 20, found

    def test_every_condition_carries_an_evidence_rule(self):
        """The rule is per condition, not stated once at the top: the one place a reviewer reads
        under time pressure is the condition it is about to cite."""
        blocks = re.split(r"^\*\*C([0-9]+) ", CONDITIONS.read_text(), flags=re.M)[1:]
        pairs = list(zip(blocks[::2], blocks[1::2]))
        assert pairs
        for num, body in pairs:
            assert re.search(r"^\*Evidence:\*", body, re.M), f"C{num} states no evidence"

    def test_the_preamble_states_the_ungrounded_rule_and_its_cost(self):
        text = CONDITIONS.read_text()
        assert "OBSERVATION" in text and "revise round" in text and "park" in text

    def test_the_reviewer_emits_one_verdict_vocabulary(self):
        skill = (REVIEWER / "SKILL.md").read_text()
        assert set(re.findall(r"^VERDICT: (\w+)$", skill, re.M)) == {"approve", "revise"}

    def test_the_reviewer_does_not_duplicate_the_deterministic_gate(self):
        assert "never report what the validator already checks" in (
            REVIEWER / "SKILL.md"
        ).read_text().lower()

    def test_the_reviewer_names_the_map_as_an_input(self):
        """C2's whole test is a candidate's evidence against the group its `found_by` names, and
        the map is neither the artifact nor any of the other three evidence sources."""
        assert "vocabulary map" in (REVIEWER / "SKILL.md").read_text()

    def test_the_reviewer_locates_the_producer_files_BY_PATH(self):
        """Three of five evidence sources live in the producer package, which is often not
        installed beside this one. A path claim is exactly what needs a mechanical check."""
        skill = (REVIEWER / "SKILL.md").read_text()
        for rel in ("schemas/", "references/source-registry.yaml", "references/angles/"):
            assert f"ml-prior-art-survey/{rel}" in skill, rel

    def test_the_reviewer_knows_about_outcome(self, registry):
        """A correctly `not_run` angle — whose emptiness the gate REQUIRES — would otherwise be
        revised for having no cells."""
        text = CONDITIONS.read_text() + (REVIEWER / "SKILL.md").read_text()
        for value in ("not_run", "vacated", "ran"):
            assert value in text, value

    @pytest.mark.parametrize(
        "produced,calibration",
        [
            ("ml-task-vocabulary-map.valid.yaml", "map.clean.yaml"),
            ("search-output.valid.yaml", "search.clean.yaml"),
        ],
    )
    def test_the_calibration_fixture_is_byte_identical(self, produced, calibration):
        """Two copies of one artifact in two packages is a drift path with nothing watching it."""
        assert (FIXTURES / produced).read_text() == (
            REVIEWER / "references/fixtures" / calibration
        ).read_text()

    def test_the_clean_fixtures_still_pass_the_producers_validator(self, registry):
        rev_map = yaml.safe_load((REVIEWER / "references/fixtures/map.clean.yaml").read_text())
        rev_search = yaml.safe_load(
            (REVIEWER / "references/fixtures/search.clean.yaml").read_text()
        )
        assert V.validate_keyword_map(rev_map, registry) == []
        assert V.validate_search(rev_search, rev_map, registry) == []


class TestConditionValidatorBoundary:
    """#56, pinned in BOTH directions.

    An artifact reaching the reviewer has passed at exit 0, so a condition whose stated gap the
    gate already catches can never be cited: it occupies a number, reads as covered, and covers
    nothing. Every condition disclaiming a rule must name it, and the rule must exist.
    """

    def test_every_disclaimed_rule_is_a_REAL_validator_rule(self):
        """A carve-out naming a rule that does not exist is worse than none: it reads as a
        boundary and marks nothing."""
        shipped = set(re.findall(r'_fail\(\s*"([a-z0-9-]+)"', SCRIPT.read_text()))
        text = CONDITIONS.read_text()
        # Only the rule-naming clause, not every backtick in the disclaimer: a field name in the
        # explanatory prose is not a claim about a rule, and treating it as one makes the check
        # fail on correct text — which is how a guard gets loosened instead of fixed.
        disclaimed: set[str] = set()
        for blk in text.split("*Not yours to report:*")[1:]:
            body = blk.split("**C")[0]
            for clause in re.findall(r"fails th(?:at|ose) at([^.]*)", body):
                disclaimed |= set(re.findall(r"`([a-z0-9-]+)`", clause))
        assert disclaimed, "no condition disclaims anything — the boundary is unmarked"
        assert disclaimed <= shipped, sorted(disclaimed - shipped)

    @pytest.mark.parametrize(
        "rule",
        [
            "borrowed-vocabulary-unmarked", "cell-group-known", "angle-verdict-complete",
            "always-on-angle-holds", "coverage-complete", "kept-matches-rows",
            "evaluation-needs-split", "sanitization-cause",
        ],
    )
    def test_the_shape_half_still_FAILS_the_gate(self, rule):
        """Direction one: the disclaimed rule genuinely fires, so the condition is right to
        exclude it.

        Asserted against the emitted rule-id set rather than a substring of the file — a substring
        search passes for a rule that appears only in a comment, or one whose branch is
        unreachable.
        """
        emitted = set(re.findall(r'_fail\(\s*"([a-z0-9-]+)"', SCRIPT.read_text()))
        assert rule in emitted, rule

    def test_the_judgement_half_still_PASSES_the_gate(self, valid_search, valid_map, registry):
        """Direction two, and the one that matters: an artifact carrying only a JUDGEMENT defect
        reaches the reviewer at exit 0. Here — a claim asserting more than its quote warrants,
        which is C19's, and which the gate cannot see."""
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["claim"] = (
            "This model is the best available choice for support-ticket triage."
        )
        assert V.validate_search(doc, valid_map, registry) == []

    def test_no_condition_restates_a_rule_it_does_not_disclaim(self):
        """The #56 failure in its pure form: a condition whose IS-a-gap is a validator rule under
        another name. Checked by requiring that any condition mentioning a shipped rule-id does so
        under a `Not yours to report` heading."""
        shipped = set(re.findall(r'_fail\(\s*"([a-z0-9-]+)"', SCRIPT.read_text()))
        for blk in re.split(r"^\*\*C", CONDITIONS.read_text(), flags=re.M)[1:]:
            head, _, tail = blk.partition("*Not yours to report:*")
            # A rule-id mentioned in the IS-a-gap half is #56's failure: the condition is
            # restating something the gate already catches. Field names that happen to match a
            # rule-id token are excluded by requiring the hyphenated multi-word form.
            named = {
                r for r in re.findall(r"`([a-z0-9]+(?:-[a-z0-9]+){2,})`", head) if r in shipped
            }
            assert not named, (blk.split("\n")[0][:40], sorted(named))


# The answer key for the blind runs. It lives HERE, not beside the fixtures, because a reviewer
# that has read the key demonstrates nothing.
PLANTED_DEFECTS = {
    "map-01.yaml": ("keyword-map", "C5", "b1 holds TRUE while its own reason concedes the scope "
                    "value is outside the precondition's set — the inflating direction"),
    "search-01.yaml": ("search", "C9", "two cells record a description of a strategy instead of "
                       "the request as issued, so their numbers cannot be reproduced"),
    "search-02.yaml": ("search", "C19", "a claim asserting what the model DOES on top of a quote "
                       "about what the document SAYS"),
    "search-03.yaml": ("search", "C17", "a vendor's own card recorded as an independent "
                       "benchmark, and an option dropped for low authority rather than ranked"),
}


class TestPlantedFixtures:
    """C8. Each is wrong AND passes at exit 0 — that combination is the whole test.

    A planted defect the validator catches proves the validator works, which was never in
    question. The reviewer is what is under test, and it only ever sees artifacts that passed.
    """

    def _cli(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args], capture_output=True, text=True,
            cwd=HERE, check=False,
        )

    @pytest.mark.parametrize("name", sorted(PLANTED_DEFECTS))
    def test_it_passes_the_deterministic_gate(self, name, registry, valid_map):
        kind, _, _ = PLANTED_DEFECTS[name]
        doc = yaml.safe_load((PLANTED / name).read_text())
        if kind == "keyword-map":
            assert V.validate_keyword_map(doc, registry) == []
        else:
            assert V.validate_search(doc, valid_map, registry) == []

    def test_it_passes_through_main_too(self):
        """The brief runs `main()`, not the functions. A fixture clean in-process and non-zero at
        the CLI would send the reviewer an artifact the producer never could."""
        km = FIXTURES / "ml-task-vocabulary-map.valid.yaml"
        assert self._cli("keyword-map", str(PLANTED / "map-01.yaml")).returncode == 0
        for name in ("search-01.yaml", "search-02.yaml", "search-03.yaml"):
            r = self._cli("search", str(PLANTED / name), "--keyword-map", str(km))
            assert r.returncode == 0, (name, r.stdout)

    def test_no_fixture_names_its_own_defect(self):
        """An answer written on the exam is not an exam."""
        leak = re.compile(r"\bC[0-9]{1,2}\b|planted|defect|deliberate|contradict", re.I)
        for path in PLANTED.glob("*.yaml"):
            assert not leak.search(path.read_text()), path.name

    def test_the_key_names_distinct_conditions(self):
        conds = [c for _, c, _ in PLANTED_DEFECTS.values()]
        assert len(set(conds)) == len(conds), conds
        assert len(conds) >= 4

    def test_every_planted_file_is_in_the_key(self):
        assert {p.name for p in PLANTED.glob("*.yaml")} == set(PLANTED_DEFECTS)

    @pytest.mark.parametrize("cond", sorted({c for _, c, _ in PLANTED_DEFECTS.values()}))
    def test_every_keyed_condition_exists(self, cond):
        """DERIVED from the key: hand-listing it lets a re-keyed fixture check the old one."""
        assert re.search(rf"^\*\*{cond} ", CONDITIONS.read_text(), re.M), cond


class TestNoIncidentalGapInAnyFixture:
    """Every fixture carries exactly the defect its key names, and no other.

    A sibling's blind runs each returned the keyed condition PLUS an incidental gap that a loop
    over the registry would have found for free — so the method was paying ~70k tokens per run to
    discover a missing dict key. Run this BEFORE dispatching any reviewer.
    """

    SEARCHES = [
        (FIXTURES / "search-output.valid.yaml", FIXTURES / "ml-task-vocabulary-map.valid.yaml"),
        (PLANTED / "search-01.yaml", FIXTURES / "ml-task-vocabulary-map.valid.yaml"),
        (PLANTED / "search-02.yaml", FIXTURES / "ml-task-vocabulary-map.valid.yaml"),
        (PLANTED / "search-03.yaml", FIXTURES / "ml-task-vocabulary-map.valid.yaml"),
    ]

    @pytest.mark.parametrize("search,kmap", SEARCHES, ids=lambda p: getattr(p, "name", ""))
    def test_the_owed_set_is_fully_covered(self, search, kmap, registry):
        doc = yaml.safe_load(search.read_text())
        m = yaml.safe_load(kmap.read_text())
        angle = next(a for a in registry["angles"] if a["id"] == doc["meta"]["angle_id"])
        seen = {(c["group_id"], c["source_id"]) for c in doc["coverage"]}
        assert V._owed_cells(angle, m) - seen == set(), search.name

    @pytest.mark.parametrize("search,kmap", SEARCHES, ids=lambda p: getattr(p, "name", ""))
    def test_kept_reconciles_in_every_fixture(self, search, kmap, registry):
        doc = yaml.safe_load(search.read_text())
        rows = collections.Counter(
            r["found_by"] for r in doc["candidates"] + (doc.get("unadmitted") or [])
        )
        for cell in doc["coverage"]:
            if cell["status"] == "reached":
                key = f"{cell['group_id']}/{cell['source_id']}"
                assert cell["kept"] == rows.get(key, 0), (search.name, key)

    @pytest.mark.parametrize("search,kmap", SEARCHES, ids=lambda p: getattr(p, "name", ""))
    def test_every_row_names_a_real_cell(self, search, kmap, registry):
        doc = yaml.safe_load(search.read_text())
        cells = {f"{c['group_id']}/{c['source_id']}" for c in doc["coverage"]}
        for row in doc["candidates"] + (doc.get("unadmitted") or []):
            assert row["found_by"] in cells, (search.name, row["found_by"])


class TestSourceAccounting:
    """The rule a blind reviewer's observation earned.

    A source in neither `active` nor `skipped` is not a neutral omission: `_owed_cells`
    intersects the angle's sources with the ACTIVE list, so an angle whose sources are all
    unaccounted owes ZERO cells and passes with an empty grid. The schema said "a source missing
    from BOTH lists is unaccounted for" and nothing enforced it.
    """

    def test_an_unaccounted_source_on_an_applicable_angle_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["sources"]["active"] = [
            r for r in doc["sources"]["active"] if r["id"] != "huggingface-hub-api"
        ]
        assert "source-unaccounted" in _rules(V.validate_keyword_map(doc, registry))

    def test_recording_it_SKIPPED_satisfies_the_rule(self, valid_map, registry):
        """MIRROR: the rule asks for an ACCOUNT, not for the source to be reachable. A skipped
        source with a cause is a complete answer."""
        doc = copy.deepcopy(valid_map)
        doc["sources"]["active"] = [
            r for r in doc["sources"]["active"] if r["id"] != "huggingface-hub-api"
        ]
        doc["sources"]["skipped"].append(
            {"id": "huggingface-hub-api", "cause": "429 throughout the wave-0 window"}
        )
        assert V.validate_keyword_map(doc, registry) == []

    def test_an_angle_that_does_NOT_hold_owes_no_accounting(self, valid_map, registry):
        """MIRROR, and the one that keeps the rule proportionate: b2/b3/b4 are false for this
        scope, so their sources are never searched and demanding a wave-0 probe of them would be
        work with no consumer."""
        doc = copy.deepcopy(valid_map)
        falsy = {v["angle_id"] for v in doc["angle_applicability"] if not v["holds"]}
        accounted = {r["id"] for r in doc["sources"]["active"]}
        accounted |= {r["id"] for r in doc["sources"]["skipped"]}
        # DERIVED: whichever non-holding angle actually has an unaccounted source. Naming b4
        # assumed a source list that overlaps a1's entirely, so the test asserted nothing.
        unaccounted = {
            a["id"]: set(a["sources"]) - accounted
            for a in registry["angles"]
            if a["id"] in falsy and set(a["sources"]) - accounted
        }
        assert unaccounted, "every non-holding angle's sources are accounted; test has no input"
        assert V.validate_keyword_map(doc, registry) == []


class TestCodeReviewFindings:
    """Every rule the C9 code review earned, each with its mirror.

    Two of these were BLOCKERS: an artifact could name an angle that does not exist and every
    coverage and cap rule would simply not run, and a row attributed to a cell that never reached
    its source escaped the `kept` reconciliation entirely rather than failing it.
    """

    def test_an_unknown_angle_id_fails_LOUDLY(self, valid_search, valid_map, registry):
        """The schema pattern admits a6-a9 and b5-b9. With no matching registry angle there is no
        owed set, no cap and no fallback to check — so the artifact passed clean with one cell and
        any cap it liked. A one-character escape from the grid the type exists for."""
        doc = copy.deepcopy(valid_search)
        doc["meta"]["angle_id"] = "a9"
        assert "angle-unknown" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_known_angle_id_still_passes(self, valid_search, valid_map, registry):
        """MIRROR: the early return must not swallow a legitimate artifact."""
        assert V.validate_search(valid_search, valid_map, registry) == []

    def test_rows_citing_an_unreached_cell_fail(self, valid_search, valid_map, registry):
        """A producer only had to mark the cell gated and the arithmetic was SKIPPED, not failed —
        which is the "dropped without a record" case `kept` exists to catch, from the other side."""
        doc = copy.deepcopy(valid_search)
        cell = next(
            c for c in doc["coverage"]
            if c["status"] == "reached" and c["kept"] and c["group_id"] == "text-classification"
        )
        cell.update(status="gated", cause="HTTP 401", returned=None, kept=None, count_frame=None)
        doc["retrieval_summary"]["status_counts"] = dict(
            collections.Counter(c["status"] for c in doc["coverage"])
        )
        doc["retrieval_summary"]["degraded_sources"] = [cell["source_id"]]
        assert "rows-cite-an-unreached-cell" in _rules(
            V.validate_search(doc, valid_map, registry)
        )

    def test_an_unreached_cell_with_NO_rows_is_fine(self, valid_search, valid_map, registry):
        """MIRROR: a cell that reached nothing and produced nothing is the honest record."""
        doc = copy.deepcopy(valid_search)
        cell = next(c for c in doc["coverage"] if c["status"] == "reached" and not c["kept"])
        cell.update(status="gated", cause="HTTP 401", returned=None, kept=None, count_frame=None)
        doc["retrieval_summary"]["status_counts"] = dict(
            collections.Counter(c["status"] for c in doc["coverage"])
        )
        doc["retrieval_summary"]["degraded_sources"] = [cell["source_id"]]
        assert V.validate_search(doc, valid_map, registry) == []

    def test_omitting_bound_entirely_fails(self, valid_search, valid_map, registry):
        """Every cap rule reads `bound`, so omitting it removed the ceiling from the gate rather
        than recording an unbounded run."""
        doc = copy.deepcopy(valid_search)
        doc.pop("bound")
        assert "bound-required" in _rules(V.validate_search(doc, valid_map, registry))

    def test_an_unrun_angle_owes_no_bound(self, valid_search, valid_map, registry):
        """MIRROR: nothing was searched, so there was no cap to apply."""
        doc = copy.deepcopy(valid_search)
        doc.update(outcome="not_run", coverage=[], candidates=[], unadmitted=[])
        doc.pop("bound")
        doc.pop("retrieval_summary")
        assert V.validate_search(doc, valid_map, registry) == []

    def test_over_the_cap_fails_even_when_hit_is_TRUE(self, valid_search, valid_map, registry):
        """Gating this on `hit is False` let `hit: true` plus a note carry any number past the
        ceiling — a cap that announces it truncated and then exceeds itself."""
        doc = copy.deepcopy(valid_search)
        doc["bound"].update(hit=True, dropped_note="the tail below rank 40")
        base = doc["candidates"][0]
        doc["candidates"] = [
            {**copy.deepcopy(base), "item_id": f"WEB-x-{i}", "id_class": "WEB"}
            for i in range(doc["bound"]["cap"] + 6)
        ]
        doc["unadmitted"] = []
        _resync(doc)
        assert "cap-respected" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_fallback_that_is_not_the_DECLARED_one_fails(
        self, valid_search, valid_map, registry
    ):
        """Checking only that the target was some registry row let a cell claim it fell back to an
        unrelated source — which reads as a documented recovery and is a walk nothing authorised."""
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0]["fallback_used"] = "angle:eurlex-ai-act"
        assert "fallback-declared" in _rules(V.validate_search(doc, valid_map, registry))

    def test_the_declared_fallback_passes(self, valid_search, valid_map, registry):
        """MIRROR."""
        doc = copy.deepcopy(valid_search)
        angle = next(a for a in registry["angles"] if a["id"] == doc["meta"]["angle_id"])
        doc["coverage"][0]["fallback_used"] = f"angle:{angle['fallback']}"
        assert V.validate_search(doc, valid_map, registry) == []

    def test_a_vacated_angle_still_owes_its_cells(self, valid_search, valid_map, registry):
        """`vacated` owes cells and causes — that is what distinguishes it from `not_run`. Gating
        the owed-set check on `ran` let a vacated angle with twelve owed pairs and zero cells pass,
        which is `not_run` wearing a different label and no verdict behind it."""
        doc = copy.deepcopy(valid_search)
        doc.update(outcome="vacated", coverage=[], candidates=[], unadmitted=[])
        doc.pop("retrieval_summary")
        assert "coverage-complete" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_run_that_attempted_nothing_is_not_a_run(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        for c in doc["coverage"]:
            c.update(
                status="not-attempted", returned=None, kept=None, count_frame=None,
                cause="budget spent on the API channel",
            )
        doc.update(candidates=[], unadmitted=[])
        doc["retrieval_summary"]["status_counts"] = {"not-attempted": len(doc["coverage"])}
        assert "ran-attempted-nothing" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_run_that_attempted_SOME_of_them_is(self, valid_search, valid_map, registry):
        """MIRROR, and the shipped shape: four cells are deliberately `not-attempted` for a stated
        budget reason while the rest reached. That is a run."""
        statuses = {c["status"] for c in valid_search["coverage"]}
        assert "not-attempted" in statuses and "reached" in statuses
        assert V.validate_search(valid_search, valid_map, registry) == []

    def test_an_unrun_angle_may_not_record_unadmitted_rows(
        self, valid_search, valid_map, registry
    ):
        """It searched nothing, so there was nothing to admit or reject."""
        doc = copy.deepcopy(valid_search)
        doc.update(outcome="not_run", coverage=[], candidates=[])
        doc.pop("retrieval_summary")
        assert "unrun-angle-has-candidates" in _rules(
            V.validate_search(doc, valid_map, registry)
        )


class TestTheTwoRulesTheMirrorSweepFound:
    """#34. A sweep over every rule found two with a negative test and no mirror beside it.

    Both are membership checks, and membership checks are exactly where a missing mirror hides: a
    rule that fires on EVERYTHING passes its negative test and fails nothing else, and the suite
    reads as covered.
    """

    def test_a_candidate_naming_a_minted_group_passes(self, valid_search, valid_map, registry):
        """MIRROR for `candidate-group-known`: every shipped candidate names a real group, so the
        rule must not fire on the corpus it was written for."""
        minted = {g["id"] for g in valid_map["groups"]}
        assert all(
            c["found_by"].split("/", 1)[0] in minted for c in valid_search["candidates"]
        )
        assert "candidate-group-known" not in _rules(
            V.validate_search(valid_search, valid_map, registry)
        )

    def test_a_cell_naming_a_registry_source_passes(self, valid_search, valid_map, registry):
        """MIRROR for `cell-source-known`: the rule is about a source in NO registry row, and a
        legitimate cell names one that is both in the registry and active in the map."""
        known = {s["id"] for s in registry["sources"]}
        active = {r["id"] for r in valid_map["sources"]["active"]}
        for cell in valid_search["coverage"]:
            assert cell["source_id"] in known and cell["source_id"] in active, cell["source_id"]
        assert "cell-source-known" not in _rules(
            V.validate_search(valid_search, valid_map, registry)
        )

    def test_the_sweep_itself_stays_green(self):
        """The sweep that found these two, shipped so the next rule added cannot skip its mirror.

        A rule with a negative test and no pass-assertion in the same class is a rule nobody has
        checked for over-firing — and an over-firing rule is indistinguishable from a correct one
        until it revises honest work.
        """
        src = SCRIPT.read_text()
        tst = Path(__file__).read_text()
        negatives = set(re.findall(r'"([a-z0-9-]+)" in _rules', tst))
        mirrored: set[str] = set()
        for block in re.split(r"^class ", tst, flags=re.M):
            named = set(re.findall(r'"([a-z0-9-]+)" in _rules', block))
            if named and ("== []" in block or "not in _rules" in block):
                mirrored |= named
        assert negatives, "no negative tests found; the sweep is looking at the wrong thing"
        assert not (negatives - mirrored), sorted(negatives - mirrored)
        assert set(re.findall(r'_fail\(\s*"([a-z0-9-]+)"', src)) >= negatives


class TestProseDoesNotContradictTheRegistry:
    """#57. Prose about a source cites that source's registry row, in its words.

    A sibling type shipped five of these in one build — a channel death narrated from a redirect
    that never happened, an access posture invented to sound better than the recorded one — and
    every instance was written while FIXING something else, from recall rather than from the row.
    """

    @staticmethod
    def _prose() -> dict[str, str]:
        base = HERE.parent
        files = [base / "SKILL.md"] + sorted((base / "references").rglob("*.md"))
        assert len(files) >= 12, len(files)
        return {p.name: p.read_text() for p in files}

    def test_no_prose_file_names_an_EXCLUDED_source_as_searchable(self, registry):
        """An excluded row is excluded for a reason the prose does not get to overrule."""
        excluded = {e["id"] for e in registry["excluded"]}
        offenders = [
            f"{name}: `{sid}`"
            for name, text in self._prose().items()
            for sid in excluded
            if f"`{sid}`" in text and "excluded" not in text.lower()
        ]
        assert not offenders, offenders

    def test_no_prose_claims_an_access_status_the_row_denies(self, registry):
        rows = {s["id"]: s for s in registry["sources"]}
        offenders = []
        for name, text in self._prose().items():
            for sid, row in rows.items():
                if f"`{sid}`" not in text:
                    continue
                for claim in ("open", "gated", "blocked"):
                    near = re.search(rf"`{re.escape(sid)}`[^.\n]{{0,60}}\b{claim}\b", text)
                    if near and row["access_status"] != claim:
                        offenders.append(f"{name}: `{sid}` called {claim}, row says {row['access_status']}")
        assert not offenders, offenders

    def test_every_source_id_in_prose_resolves_to_a_row(self, registry):
        """A backticked id that resolves to nothing is an instruction pointing at no channel."""
        known = {s["id"] for s in registry["sources"]} | {e["id"] for e in registry["excluded"]}
        looks_like_a_source = re.compile(r"`([a-z]+(?:-[a-z]+){1,3})`")
        vocab = known | HUB_API_FIELDS | {
            "ml-task", "domain-term", "runtime-format", "harm-category", "group-type",
            "not-attempted", "forbidden-by-terms", "rate-limited", "vendor-published",
            "independent-benchmark", "peer-reviewed", "community-reported", "self-reported",
            "time-series", "text-classification", "text-generation", "image-segmentation",
            "object-detection", "support-ticket", "encoder-finetune", "intent-benchmarks",
            "support-corpora", "modality-text", "modality-image", "on-device-photo",
            "mobile-runtimes", "trains-from-scratch", "uses-pre-trained", "multi-model",
            "single-region", "mobile-app", "embedded-iot", "desktop-app", "browser-extension",
            "web-app", "background-removal", "zero-shot", "text-to-image",
            # CLI subcommands, not sources — `keyword-map` is the validator's name for the map.
            "keyword-map",
        }
        offenders = [
            f"{name}: `{tok}`"
            for name, text in self._prose().items()
            for tok in set(looks_like_a_source.findall(text))
            if tok not in vocab and "-" in tok and tok.count("-") <= 2 and tok.islower()
        ]
        assert not offenders, offenders


class TestRetractedClaimsHaveNoSurvivors:
    """Every claim a review retracted, checked across BOTH packages including the fixtures.

    Cycle 2 found three retracted claims still standing — one in five files, one in three, one in
    a schema the same fold had just added to the producer's reading list. Each fix had been applied
    where the review pointed and nowhere else. This is the guard that makes a retraction mean
    something, and it names the claims rather than the files, because the file list is what got it
    wrong last time.
    """

    RETRACTED = {
        "all three or the result is not recorded": "a rank needs benchmark + split; the date may be null",
        "record all three or do not record": "same claim, registry wording",
        "requires all three": "same claim, angle-reference wording",
        "lost two channels that way": "one was lost to gating, one to a redirect",
        "lost two channels this way": "same",
        "tightest published limit in this registry": "it is the tightest on that HOST only",
        "tightest limit in the registry — 100 requests": "same, fixture cause wording",
        "TIGHTEST published bound in this registry": "same, registry-row wording",
    }

    @staticmethod
    def _everything() -> list[Path]:
        """Both packages, every authored file AND every fixture — derived by glob.

        The fixtures are in scope on purpose: a retracted claim written into a calibration cause
        string teaches it to every reviewer that reads the exemplar, which is how one of these
        survived a fold that corrected the prose.
        """
        out: list[Path] = []
        for root in (HERE.parent, REVIEWER):
            for pattern in ("**/*.md", "**/*.json", "**/*.yaml"):
                out += list(root.glob(pattern))
        assert len(out) >= 25, len(out)
        return out

    @pytest.mark.parametrize("claim", sorted(RETRACTED))
    def test_no_file_still_asserts_it(self, claim):
        offenders = [p.name for p in self._everything() if claim in p.read_text()]
        assert not offenders, f"{offenders} still assert: {self.RETRACTED[claim]}"


class TestClassificationValuesAreRecordable:
    """A verdict citing a classification value must be checkable against what the producer was
    handed. `scope_ref` is prose, so without this a fabricated value and a real one read
    identically — and the rule forbidding invention had nothing enforcing it."""

    def test_the_map_can_record_what_it_was_handed(self):
        import json as _json

        schema = _json.loads(
            (HERE.parent / "schemas" / "ml-task-vocabulary-map.schema.json").read_text()
        )
        assert "classification" in schema["properties"]["meta"]["properties"]

    def test_the_producer_is_told_to_write_it(self):
        assert "meta.classification" in (HERE.parent / "SKILL.md").read_text()

    def test_a_condition_judges_a_verdict_against_it(self):
        assert "meta.classification" in CONDITIONS.read_text()

    def test_the_exemplar_carries_every_value_its_verdicts_cite(self, valid_map):
        """The exemplar must MODEL the field, not merely be permitted by it — a calibration
        artifact that leaves it empty teaches that leaving it empty is fine."""
        recorded = set(valid_map["meta"]["classification"])
        cited = set()
        for v in valid_map["angle_applicability"]:
            cited |= set(re.findall(r"\b([a-z_]+(?:\.[a-z_]+)+)\b", v["reason"]))
        assert cited, "no verdict cites a classification field"
        assert not (cited - recorded), sorted(cited - recorded)
