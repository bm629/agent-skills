"""Rule-by-rule tests for the user-research prior-art gate.

Every rule the validator can emit gets at least one test that DRIVES it — the fixture is mutated
in-process so the shipped file on disk always stays the clean reference. A rule with no test that
makes it fire is a rule nobody has shown can fire at all, which is how a function defined and
never called ships green.
"""

from __future__ import annotations

import copy
import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"

_spec = importlib.util.spec_from_file_location(
    "validate_user_research_prior_art", HERE / "validate_user_research_prior_art.py"
)
V = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = V
_spec.loader.exec_module(V)


@pytest.fixture
def valid_map() -> dict:
    return yaml.safe_load((FIXTURES / "research-vocabulary-map.valid.yaml").read_text())


@pytest.fixture
def valid_search() -> dict:
    return yaml.safe_load((FIXTURES / "search-output.valid.yaml").read_text())


@pytest.fixture
def registry() -> dict:
    return V.load_registry()


def _rules(failures: list[str]) -> set[str]:
    return {f.split(" ", 2)[1].rstrip(":") for f in failures}


# ── the shipped fixtures are the reference, and must stay clean ────────────────


class TestFixturesAreValid:
    def test_valid_map_passes_clean(self, valid_map, registry):
        assert V.validate_keyword_map(valid_map, registry) == []

    def test_valid_search_passes_clean(self, valid_search, valid_map, registry):
        assert V.validate_search(valid_search, valid_map, registry) == []

    def test_shipped_registry_has_no_anchor_failures(self, registry):
        assert V.anchor_failures(registry) == []


# ── schema shape ──────────────────────────────────────────────────────────────


class TestSchemaShape:
    def test_missing_required_top_level_key_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        del doc["angle_applicability"]
        assert "schema" in _rules(V.validate_keyword_map(doc, registry))

    def test_group_type_from_another_survey_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["groups"][0]["type"] = "design-system"
        assert "schema" in _rules(V.validate_keyword_map(doc, registry))

    def test_date_only_timestamp_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["meta"]["as_of"] = "2026-08-04"
        assert "schema" in _rules(V.validate_keyword_map(doc, registry))

    def test_access_status_from_a_sibling_survey_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["sources"]["active"][0]["access_status"] = "forbidden-by-terms"
        assert "schema" in _rules(V.validate_keyword_map(doc, registry))

    def test_unknown_property_on_a_candidate_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["certainty"] = "high"
        assert "schema" in _rules(V.validate_search(doc, valid_map, registry))

    def test_broken_map_reports_as_keyword_map_invalid(self, valid_search, valid_map, registry):
        mapping = copy.deepcopy(valid_map)
        del mapping["sources"]
        rules = _rules(V.validate_search(valid_search, mapping, registry))
        assert rules == {"keyword-map-invalid"}


# ── map: groups ───────────────────────────────────────────────────────────────


class TestGroupRules:
    def test_duplicate_group_id_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["groups"][1]["id"] = doc["groups"][0]["id"]
        assert "group-id-unique" in _rules(V.validate_keyword_map(doc, registry))

    def test_expansions_above_declared_cap_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        g = doc["groups"][0]
        g["expansion_cap"] = 2
        assert "expansion-cap" in _rules(V.validate_keyword_map(doc, registry))

    def test_thin_group_without_short_reason_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["groups"][0]["expansions"] = doc["groups"][0]["expansions"][:2]
        assert "expansion-floor" in _rules(V.validate_keyword_map(doc, registry))

    def test_thin_group_with_short_reason_passes(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["groups"][0]["expansions"] = doc["groups"][0]["expansions"][:2]
        doc["groups"][0]["short_reason"] = "Only two terms retrieve this population."
        assert "expansion-floor" not in _rules(V.validate_keyword_map(doc, registry))

    def test_method_group_without_negative_terms_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        for g in doc["groups"]:
            if g["type"] == "method":
                g.pop("negative_terms", None)
        assert "negative-terms-required" in _rules(V.validate_keyword_map(doc, registry))

    def test_non_method_group_needs_no_negative_terms(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        for g in doc["groups"]:
            if g["type"] != "method":
                g.pop("negative_terms", None)
        assert "negative-terms-required" not in _rules(V.validate_keyword_map(doc, registry))

    def test_missing_axis_neither_present_nor_declared_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["groups"] = [g for g in doc["groups"] if g["type"] != "component"]
        assert "group-type-accounted" in _rules(V.validate_keyword_map(doc, registry))

    def test_missing_axis_declared_absent_passes(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["groups"] = [g for g in doc["groups"] if g["type"] != "component"]
        doc["scope_guard"]["absent_types"].append(
            {"type": "component", "reason": "The terminal exposes no named widget in scope."}
        )
        assert "group-type-accounted" not in _rules(V.validate_keyword_map(doc, registry))

    def test_all_alt_label_expansions_fail_relation_variety(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        for g in doc["groups"]:
            for e in g["expansions"]:
                e["relation"] = "alt-label"
        assert "relation-variety" in _rules(V.validate_keyword_map(doc, registry))


# ── map: probe, sanitization, sources ─────────────────────────────────────────


class TestProbeAndSources:
    def test_probe_discovered_without_a_performed_probe_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["groups"][0]["expansions"][0]["provenance"] = "probe-discovered"
        assert "probe-record" in _rules(V.validate_keyword_map(doc, registry))

    def test_probe_not_performed_without_reason_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["probe"] = {"performed": False}
        assert "probe-record" in _rules(V.validate_keyword_map(doc, registry))

    def test_probe_discovered_with_a_performed_probe_passes(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["groups"][0]["expansions"][0]["provenance"] = "probe-discovered"
        doc["probe"] = {"performed": True, "sources": ["crossref"], "discoveries": ["kiosk"]}
        assert "probe-record" not in _rules(V.validate_keyword_map(doc, registry))

    def test_degraded_sanitization_without_cause_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["sources"]["active"][0]["sanitization"] = {"status": "content-withheld"}
        assert "sanitization-cause" in _rules(V.validate_keyword_map(doc, registry))

    def test_blocked_source_listed_active_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["sources"]["active"][0]["access_status"] = "blocked"
        assert "forbidden-source-not-active" in _rules(V.validate_keyword_map(doc, registry))

    def test_blocked_source_listed_skipped_passes(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["sources"]["skipped"][0]["access_status"] = "blocked"
        assert "forbidden-source-not-active" not in _rules(V.validate_keyword_map(doc, registry))

    def test_source_of_a_holding_angle_recorded_nowhere_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["sources"]["active"] = [s for s in doc["sources"]["active"] if s["id"] != "crossref"]
        assert "access-status-required" in _rules(V.validate_keyword_map(doc, registry))

    def test_source_recorded_skipped_satisfies_access_status_required(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["sources"]["active"] = [s for s in doc["sources"]["active"] if s["id"] != "crossref"]
        doc["sources"]["skipped"].append(
            {
                "id": "crossref",
                "cause": "The index returned 503 through the whole wave-0 window.",
                "access_status": "blocked",
            }
        )
        assert "access-status-required" not in _rules(V.validate_keyword_map(doc, registry))

    def test_source_of_a_non_holding_angle_need_not_be_recorded(self, valid_map, registry):
        """b5's only source is absent from the map, and b5's verdict is holds=false."""
        doc = copy.deepcopy(valid_map)
        recorded = {s["id"] for s in doc["sources"]["active"]} | {
            s["id"] for s in doc["sources"]["skipped"]
        }
        assert "stackoverflow-survey" not in recorded
        assert "access-status-required" not in _rules(V.validate_keyword_map(doc, registry))


# ── map: angle verdicts ───────────────────────────────────────────────────────


class TestAngleVerdicts:
    def test_missing_verdict_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["angle_applicability"] = [
            a for a in doc["angle_applicability"] if a["angle_id"] != "b4"
        ]
        assert "angle-verdict-complete" in _rules(V.validate_keyword_map(doc, registry))

    def test_duplicate_verdict_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["angle_applicability"].append(copy.deepcopy(doc["angle_applicability"][0]))
        assert "angle-verdict-unique" in _rules(V.validate_keyword_map(doc, registry))

    def test_verdict_on_an_unknown_angle_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["angle_applicability"].append(
            {"angle_id": "b9", "precondition": "invented", "holds": True, "reason": "invented"}
        )
        assert "angle-unknown" in _rules(V.validate_keyword_map(doc, registry))

    def test_always_on_angle_switched_off_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        for a in doc["angle_applicability"]:
            if a["angle_id"] == "a1":
                a["holds"] = False
        assert "always-on-angle-holds" in _rules(V.validate_keyword_map(doc, registry))


# ── registry: trigger anchors ─────────────────────────────────────────────────


class TestTriggerAnchors:
    def test_conditional_angle_without_an_anchor_fails(self, registry):
        reg = copy.deepcopy(registry)
        for a in reg["angles"]:
            if a["id"] == "b1":
                a.pop("trigger_anchor")
        assert "anchor-required" in _rules(V.anchor_failures(reg))

    def test_anchor_on_an_optional_field_fails(self, registry):
        reg = copy.deepcopy(registry)
        for a in reg["angles"]:
            if a["id"] == "b2":
                a["trigger_anchor"] = ["ui.accessibility.required_level"]
        assert "anchor-must-be-required" in _rules(V.anchor_failures(reg))

    def test_optional_leg_declared_as_widening_is_fine(self, registry):
        """b3 pairs a required primary with an optional secondary; that only ADDS firings."""
        b3 = next(a for a in registry["angles"] if a["id"] == "b3")
        assert b3["widening_legs"] == ["archetype.secondary"]
        assert b3["trigger_anchor"] == ["archetype.primary"]
        assert V.anchor_failures(registry) == []

    def test_always_on_angle_declaring_an_anchor_fails(self, registry):
        reg = copy.deepcopy(registry)
        for a in reg["angles"]:
            if a["id"] == "a1":
                a["trigger_anchor"] = ["ui.has_ui"]
        assert "anchor-only-on-conditional" in _rules(V.anchor_failures(reg))

    def test_anchor_failures_are_wired_into_the_map_subcommand(self, valid_map):
        """Defined-and-never-called is the defect class this asserts against."""
        reg = copy.deepcopy(V.load_registry())
        for a in reg["angles"]:
            if a["id"] == "b1":
                a["trigger_anchor"] = ["archetype.lifecycle_stage"]
        assert "anchor-must-be-required" in _rules(V.validate_keyword_map(valid_map, reg))

    def test_every_shipped_conditional_anchor_is_a_required_field(self, registry):
        for a in registry["angles"]:
            if a["trigger"] != "conditional":
                continue
            assert a["trigger_anchor"], a["id"]
            for anchor in a["trigger_anchor"]:
                assert anchor in V.REQUIRED_CAPABILITY_FIELDS, (a["id"], anchor)


# ── search: outcome discrimination ────────────────────────────────────────────


class TestOutcome:
    def test_not_run_without_its_block_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["outcome"] = "not_run"
        doc.pop("coverage")
        doc.pop("retrieval_summary")
        doc.pop("bound")
        doc.pop("candidates")
        doc.pop("unadmitted")
        assert "outcome-block-required" in _rules(V.validate_search(doc, valid_map, registry))

    def test_not_run_with_coverage_cells_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["outcome"] = "not_run"
        doc["not_run"] = {"reason": "precondition failed", "precondition": "always applicable"}
        assert "unrun-angle-has-cells" in _rules(V.validate_search(doc, valid_map, registry))

    def test_vacated_while_work_was_owed_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["outcome"] = "vacated"
        doc["vacated"] = {"reason": "nothing applicable"}
        for key in ("coverage", "retrieval_summary", "bound", "candidates", "unadmitted"):
            doc.pop(key, None)
        assert "vacated-not-empty" in _rules(V.validate_search(doc, valid_map, registry))

    def test_ran_without_coverage_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc.pop("coverage")
        assert "ran-requires-coverage" in _rules(V.validate_search(doc, valid_map, registry))

    def test_ran_without_bound_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc.pop("bound")
        assert "ran-requires-coverage" in _rules(V.validate_search(doc, valid_map, registry))


# ── search: coverage completeness, both directions ────────────────────────────


class TestCoverageCompleteness:
    def test_deleting_an_applicable_cell_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        dropped = doc["coverage"].pop()
        doc["candidates"] = [
            c
            for c in doc["candidates"]
            if c["found_by"] != f"{dropped['group_id']}/{dropped['source_id']}"
        ]
        doc["retrieval_summary"]["status_counts"][dropped["status"]] -= 1
        assert "coverage-complete" in _rules(V.validate_search(doc, valid_map, registry))

    def test_adding_a_cell_outside_the_applicable_set_fails(
        self, valid_search, valid_map, registry
    ):
        doc = copy.deepcopy(valid_search)
        extra = copy.deepcopy(doc["coverage"][1])
        extra["source_id"] = "crossref"
        extra["kept"] = 0
        doc["coverage"].append(extra)
        doc["retrieval_summary"]["status_counts"]["reached"] += 1
        assert "cell-in-applicable-set" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_map_skipped_source_is_outside_the_applicable_set(self, valid_map, registry):
        """baymard is one of a2's registry sources but is skipped in the map."""
        angle = next(a for a in registry["angles"] if a["id"] == "a2")
        owed = V._applicable_set(valid_map, angle)
        assert not any(src == "baymard" for _, src in owed)
        assert any(src == "nngroup" for _, src in owed)

    def test_search_for_an_unknown_angle_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["meta"]["angle_id"] = "b9"
        assert "angle-unknown" in _rules(V.validate_search(doc, valid_map, registry))


# ── search: per-cell rules ────────────────────────────────────────────────────


class TestCellRules:
    def test_duplicate_cell_pair_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["coverage"].append(copy.deepcopy(doc["coverage"][3]))
        doc["retrieval_summary"]["status_counts"]["reached"] += 1
        assert "cell-pair-unique" in _rules(V.validate_search(doc, valid_map, registry))

    def test_reached_cell_without_counts_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["coverage"][3].pop("returned")
        doc["coverage"][3].pop("kept")
        assert "reached-needs-counts" in _rules(V.validate_search(doc, valid_map, registry))

    def test_kept_above_returned_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0]["returned"] = 1
        assert "kept-exceeds-returned" in _rules(V.validate_search(doc, valid_map, registry))

    def test_kept_not_matching_the_rows_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0]["kept"] = 5
        assert "kept-matches-rows" in _rules(V.validate_search(doc, valid_map, registry))

    def test_non_reached_cell_without_cause_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["coverage"][8].pop("cause")
        assert "status-needs-cause" in _rules(V.validate_search(doc, valid_map, registry))

    def test_cell_naming_an_unknown_group_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0]["group_id"] = "no-such-group"
        assert "cell-group-known" in _rules(V.validate_search(doc, valid_map, registry))

    def test_cell_naming_an_unknown_source_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0]["source_id"] = "no-such-source"
        assert "cell-source-known" in _rules(V.validate_search(doc, valid_map, registry))

    def test_cell_naming_an_excluded_source_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0]["source_id"] = "acm-digital-library"
        assert "cell-source-excluded" in _rules(V.validate_search(doc, valid_map, registry))


# ── search: crawl delay ───────────────────────────────────────────────────────


class TestCrawlDelay:
    def test_delayed_source_reached_without_a_selection_fails(
        self, valid_search, valid_map, registry
    ):
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0].pop("selection")
        assert "crawl-delay-honoured" in _rules(V.validate_search(doc, valid_map, registry))

    def test_undelayed_source_needs_no_selection(self, valid_search, valid_map, registry):
        """The govuk cells carry no selection and must not be faulted for it."""
        govuk = [c for c in valid_search["coverage"] if c["source_id"] == "govuk-service-manual"]
        assert govuk and all("selection" not in c for c in govuk)
        assert "crawl-delay-honoured" not in _rules(
            V.validate_search(valid_search, valid_map, registry)
        )

    def test_delayed_source_that_never_responded_needs_no_selection(
        self, valid_search, valid_map, registry
    ):
        """A rate-limited cell made no selection; demanding one would invite inventing it."""
        cell = next(c for c in valid_search["coverage"] if c["status"] == "rate-limited")
        assert cell["source_id"] == "nngroup"
        assert "selection" not in cell
        assert "crawl-delay-honoured" not in _rules(
            V.validate_search(valid_search, valid_map, registry)
        )


# ── search: counts belong only to a cell that retrieved something ─────────────


class TestCountsOnlyWhenRetrieved:
    def test_returned_on_a_rate_limited_cell_fails(self, valid_search, valid_map, registry):
        """One field-rename from the laundered zero, so the schema must not tolerate it."""
        doc = copy.deepcopy(valid_search)
        cell = next(c for c in doc["coverage"] if c["status"] == "rate-limited")
        cell["returned"] = 0
        cell["kept"] = 0
        assert "counts-only-when-retrieved" in _rules(V.validate_search(doc, valid_map, registry))

    def test_kept_alone_on_an_unreachable_cell_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        cell = next(c for c in doc["coverage"] if c["status"] == "rate-limited")
        cell["status"] = "unreachable"
        cell["kept"] = 0
        assert "counts-only-when-retrieved" in _rules(V.validate_search(doc, valid_map, registry))

    def test_counts_on_a_partial_cell_pass(self, valid_search, valid_map, registry):
        """A partial cell DID retrieve something, so its arithmetic is meaningful."""
        doc = copy.deepcopy(valid_search)
        cell = next(c for c in doc["coverage"] if c["status"] == "rate-limited")
        cell["status"] = "partial"
        cell["returned"] = 4
        cell["kept"] = 0
        cell["selection"] = "Two of four index pages retrieved before the run's budget ran out."
        doc["retrieval_summary"]["status_counts"] = {"reached": 9, "partial": 1}
        doc["retrieval_summary"]["degraded_sources"][0]["status"] = "partial"
        assert "counts-only-when-retrieved" not in _rules(
            V.validate_search(doc, valid_map, registry)
        )

    def test_counts_on_a_reached_cell_pass(self, valid_search, valid_map, registry):
        assert "counts-only-when-retrieved" not in _rules(
            V.validate_search(valid_search, valid_map, registry)
        )


# ── search: the precondition is the registry's, verbatim ──────────────────────


class TestPreconditionVerbatim:
    def test_reworded_precondition_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        for a in doc["angle_applicability"]:
            if a["angle_id"] == "b4":
                a["precondition"] = "the product involves some machine learning"
        assert "precondition-verbatim" in _rules(V.validate_keyword_map(doc, registry))

    def test_whitespace_differences_are_tolerated(self, valid_map, registry):
        """YAML folding reflows a long precondition; that is not a rewording."""
        doc = copy.deepcopy(valid_map)
        for a in doc["angle_applicability"]:
            if a["angle_id"] == "b5":
                a["precondition"] = " ".join(a["precondition"].split()) + "   \n"
        assert "precondition-verbatim" not in _rules(V.validate_keyword_map(doc, registry))

    def test_the_shipped_fixture_quotes_every_precondition_verbatim(self, valid_map, registry):
        assert "precondition-verbatim" not in _rules(V.validate_keyword_map(valid_map, registry))


# ── search: retrieval summary ─────────────────────────────────────────────────


class TestRetrievalSummary:
    def test_status_counts_not_matching_the_cells_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["retrieval_summary"]["status_counts"]["reached"] = 99
        assert "summary-reconciles" in _rules(V.validate_search(doc, valid_map, registry))

    def test_degraded_source_missing_from_the_summary_fails(
        self, valid_search, valid_map, registry
    ):
        doc = copy.deepcopy(valid_search)
        doc["retrieval_summary"]["degraded_sources"] = []
        assert "degraded-source-recorded" in _rules(V.validate_search(doc, valid_map, registry))

    def test_fallback_to_an_undeclared_source_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["retrieval_summary"]["degraded_sources"][0]["fallback_used"] = "crossref"
        assert "fallback-declared" in _rules(V.validate_search(doc, valid_map, registry))

    def test_fallback_to_an_unknown_source_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["retrieval_summary"]["degraded_sources"][0]["fallback_used"] = "not-a-source"
        assert "cell-source-known" in _rules(V.validate_search(doc, valid_map, registry))

    def test_fallback_to_an_excluded_source_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["retrieval_summary"]["degraded_sources"][0]["fallback_used"] = "openalex"
        assert "cell-source-excluded" in _rules(V.validate_search(doc, valid_map, registry))


# ── search: the per-angle limit ───────────────────────────────────────────────


class TestBound:
    def test_cap_not_matching_the_registry_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["bound"]["cap"] = 99
        assert "cap-matches-registry" in _rules(V.validate_search(doc, valid_map, registry))

    def test_lowering_the_cap_also_fails(self, valid_search, valid_map, registry):
        """Both directions: a quietly lowered cap truncates coverage while looking compliant."""
        doc = copy.deepcopy(valid_search)
        doc["bound"]["cap"] = 3
        assert "cap-matches-registry" in _rules(V.validate_search(doc, valid_map, registry))

    def test_hit_without_a_dropped_note_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["bound"]["hit"] = True
        rules = _rules(V.validate_search(doc, valid_map, registry))
        assert "bound-hit-needs-note" in rules

    def test_hit_declared_below_the_cap_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["bound"]["hit"] = True
        doc["bound"]["dropped_note"] = "Four practitioner articles on adjacent tasks."
        assert "bound-hit-consistent" in _rules(V.validate_search(doc, valid_map, registry))

    def test_more_candidates_than_the_cap_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["bound"]["cap"] = 12
        base = doc["candidates"][0]
        for i in range(12):
            extra = copy.deepcopy(base)
            extra["id"] = f"WEB-nngroup-filler-{i}"
            doc["candidates"].append(extra)
        assert "cap-respected" in _rules(V.validate_search(doc, valid_map, registry))

    def test_the_shipped_caps_are_not_uniform(self, registry):
        caps = [a["cap"] for a in registry["angles"]]
        assert len(set(caps)) > 1
        assert min(caps) < max(caps)


# ── search: candidates ────────────────────────────────────────────────────────


class TestCandidates:
    def test_duplicate_candidate_id_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["candidates"].append(copy.deepcopy(doc["candidates"][0]))
        doc["coverage"][0]["kept"] = 3
        assert "candidate-id-unique" in _rules(V.validate_search(doc, valid_map, registry))

    def test_doi_id_not_matching_its_class_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["id_class"] = "doi"
        assert "id-class-shape" in _rules(V.validate_search(doc, valid_map, registry))

    def test_wellformed_doi_id_passes(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["id_class"] = "doi"
        doc["candidates"][0]["id"] = "DOI-10.1145/3313831.3376728"
        assert "id-class-shape" not in _rules(V.validate_search(doc, valid_map, registry))

    def test_wellformed_arxiv_id_passes(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["id_class"] = "arxiv"
        doc["candidates"][0]["id"] = "ARXIV-2401.01234v2"
        assert "id-class-shape" not in _rules(V.validate_search(doc, valid_map, registry))

    def test_web_candidate_without_a_url_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0].pop("url")
        assert "web-id-needs-url" in _rules(V.validate_search(doc, valid_map, registry))

    def test_doi_candidate_without_a_url_passes(self, valid_search, valid_map, registry):
        """A DOI has a resolver behind it; a web id has nothing."""
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["id_class"] = "doi"
        doc["candidates"][0]["id"] = "DOI-10.1145/3313831.3376728"
        doc["candidates"][0].pop("url")
        assert "web-id-needs-url" not in _rules(V.validate_search(doc, valid_map, registry))

    def test_candidate_from_a_cell_that_does_not_exist_fails(
        self, valid_search, valid_map, registry
    ):
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["found_by"] = "pop-library-staff/crossref"
        assert "candidate-provenance" in _rules(V.validate_search(doc, valid_map, registry))

    def test_unadmitted_row_from_a_cell_that_does_not_exist_fails(
        self, valid_search, valid_map, registry
    ):
        doc = copy.deepcopy(valid_search)
        doc["unadmitted"][0]["found_by"] = "pop-library-staff/crossref"
        assert "candidate-provenance" in _rules(V.validate_search(doc, valid_map, registry))


# ── search: this type's own admission rule ────────────────────────────────────


class TestAdmission:
    def test_full_text_admission_from_an_abstract_only_source_fails(
        self, valid_search, valid_map, registry
    ):
        mapping = copy.deepcopy(valid_map)
        for s in mapping["sources"]["active"]:
            if s["id"] == "nngroup":
                s["access_status"] = "paywalled-abstract-only"
        assert "admission-vs-access-status" in _rules(
            V.validate_search(valid_search, mapping, registry)
        )

    def test_admission_from_an_open_access_source_passes(self, valid_search, valid_map, registry):
        assert "admission-vs-access-status" not in _rules(
            V.validate_search(valid_search, valid_map, registry)
        )

    def test_an_abstract_only_source_may_still_carry_unadmitted_rows(
        self, valid_search, valid_map, registry
    ):
        """The rule bites on ADMISSION, not on recording that a source was reached and unusable."""
        doc = copy.deepcopy(valid_search)
        mapping = copy.deepcopy(valid_map)
        for s in mapping["sources"]["active"]:
            if s["id"] == "govuk-service-manual":
                s["access_status"] = "paywalled-abstract-only"
        doc["candidates"] = [
            c for c in doc["candidates"] if not c["found_by"].endswith("/govuk-service-manual")
        ]
        for c in doc["coverage"]:
            if c["source_id"] == "govuk-service-manual" and c["status"] == "reached":
                c["kept"] = 0
        doc["unadmitted"].append(
            {
                "name": "A gated transaction-research report",
                "found_by": "task-self-checkout/govuk-service-manual",
                "reason": "Abstract only; the method section is not retrievable.",
            }
        )
        for c in doc["coverage"]:
            if c["group_id"] == "task-self-checkout" and c["source_id"] == "govuk-service-manual":
                c["kept"] = 1
        assert "admission-vs-access-status" not in _rules(V.validate_search(doc, mapping, registry))


# ── record_filename: injectivity across BOTH branches ─────────────────────────


class TestRecordFilename:
    def test_filename_safe_id_is_returned_unchanged(self):
        assert V.record_filename("ARXIV-2401.01234v2") == "ARXIV-2401.01234v2"

    def test_a_doi_slash_never_reaches_the_filename(self):
        stem = V.record_filename("DOI-10.1145/3313831.3376728")
        assert "/" not in stem

    def test_two_ids_differing_only_in_collapsed_characters_get_different_names(self):
        a = V.record_filename("DOI-10.1145/abc")
        b = V.record_filename("DOI-10.1145:abc")
        assert a != b

    def test_a_hashed_stem_fed_back_in_does_not_return_itself(self):
        """The cross-branch collision: the identity branch must refuse a hashed-looking stem."""
        original = "DOI-10.1145/3313831.3376728"
        stem = V.record_filename(original)
        assert V._HASHED_STEM.search(stem)
        assert V.record_filename(stem) != stem

    def test_injective_over_a_mixed_sample(self):
        ids = [
            "DOI-10.1145/3313831.3376728",
            "DOI-10.1145:3313831.3376728",
            "DOI-10.1016/j.ijhcs.2020.102437",
            "ARXIV-2401.01234",
            "ARXIV-2401.01234v2",
            "WEB-nngroup-error-recovery-rate",
            "WEB-gov.uk-assisted-digital-research",
        ]
        stems = [V.record_filename(i) for i in ids]
        assert len(set(stems)) == len(ids)

    def test_an_id_with_no_safe_characters_still_gets_a_name(self):
        stem = V.record_filename("///")
        assert stem and "/" not in stem


# ── CLI ───────────────────────────────────────────────────────────────────────


class TestCLI:
    def test_clean_map_exits_0(self):
        assert V.main(["keyword-map", str(FIXTURES / "research-vocabulary-map.valid.yaml")]) == 0

    def test_clean_search_exits_0(self):
        assert (
            V.main(
                [
                    "search",
                    str(FIXTURES / "search-output.valid.yaml"),
                    "--keyword-map",
                    str(FIXTURES / "research-vocabulary-map.valid.yaml"),
                ]
            )
            == 0
        )

    def test_failing_artifact_exits_1(self, tmp_path, valid_map):
        doc = copy.deepcopy(valid_map)
        doc["groups"][1]["id"] = doc["groups"][0]["id"]
        f = tmp_path / "map.yaml"
        f.write_text(yaml.safe_dump(doc))
        assert V.main(["keyword-map", str(f)]) == 1

    def test_missing_file_exits_2(self, tmp_path, capsys):
        assert V.main(["keyword-map", str(tmp_path / "absent.yaml")]) == 2
        assert "FAIL input" in capsys.readouterr().out

    def test_unparseable_yaml_exits_2(self, tmp_path, capsys):
        f = tmp_path / "broken.yaml"
        f.write_text("groups: [\n  - id: x\n bad indent\n")
        assert V.main(["keyword-map", str(f)]) == 2
        assert "not valid YAML" in capsys.readouterr().out

    def test_non_utf8_input_exits_2(self, tmp_path, capsys):
        """An unreadable input is a CALLER fault; exiting 1 would send them to edit a fine file."""
        f = tmp_path / "binary.yaml"
        f.write_bytes(b"\xff\xfe\x00\x01 not text")
        assert V.main(["keyword-map", str(f)]) == 2
        assert "not valid UTF-8" in capsys.readouterr().out

    def test_missing_keyword_map_on_search_exits_2(self, tmp_path, capsys):
        assert (
            V.main(
                [
                    "search",
                    str(FIXTURES / "search-output.valid.yaml"),
                    "--keyword-map",
                    str(tmp_path / "absent.yaml"),
                ]
            )
            == 2
        )
        assert "FAIL input" in capsys.readouterr().out


# ── the package's own consistency ─────────────────────────────────────────────


class TestPackageConsistency:
    def test_every_angle_source_exists_and_is_not_excluded(self, registry):
        for a in registry["angles"]:
            for s in a["sources"] + [a["fallback"]]:
                assert s in registry["sources"], (a["id"], s)
                assert s not in registry["excluded"], (a["id"], s)

    def test_every_registry_source_carries_a_verified_date(self, registry):
        for name, s in registry["sources"].items():
            assert s.get("verified"), name
        for name, s in registry["excluded"].items():
            assert s.get("verified"), name

    def test_an_angle_reference_exists_for_every_angle(self, registry):
        refs = HERE.parent / "references" / "angles"
        for a in registry["angles"]:
            assert (refs / f"{a['id']}.md").exists(), a["id"]

    def test_the_four_axes_match_the_schema(self, valid_map):
        import json

        schema = json.loads(
            (HERE.parent / "schemas" / "research-vocabulary-map.schema.json").read_text()
        )
        assert tuple(schema["$defs"]["group_type"]["enum"]) == V.GROUP_TYPES

    def test_no_wave_two_field_is_reachable_in_a_wave_one_candidate(self):
        import json

        schema = json.loads((HERE.parent / "schemas" / "search-output.schema.json").read_text())
        props = set(schema["$defs"]["candidate"]["properties"])
        forbidden = {
            "certainty",
            "transferability",
            "study_date",
            "population",
            "platform_context",
            "effect_size",
            "sample_size",
        }
        assert not (props & forbidden)
