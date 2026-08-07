"""Tests for the visual prior-art deterministic gate (wave 1).

Every test mutates a deep copy of the valid fixture IN-PROCESS. Never revert a planted
defect with a VCS checkout — that discards any uncommitted work alongside it.

The gate checks SHAPE only. A test asserting the validator caught a SEMANTIC
error would be testing the wrong layer; those belong to the reviewing skill's conditions.
"""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
import validate_visual_prior_art as V
import yaml

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"
ANGLES = HERE.parent / "references" / "angles"


@pytest.fixture
def valid_map() -> dict:
    return yaml.safe_load((FIXTURES / "ui-pattern-vocabulary-map.valid.yaml").read_text())


@pytest.fixture
def registry() -> dict:
    return V.load_registry()


def _rules(failures: list[str]) -> set[str]:
    """The rule names from a list of ``FAIL <rule>: ...`` lines."""
    return {line.split()[1].rstrip(":") for line in failures}


class TestFixtureIsValid:
    def test_valid_fixture_passes_clean(self, valid_map, registry):
        assert V.validate_keyword_map(valid_map, registry) == []

    def test_fixture_covers_every_group_type(self, valid_map):
        """A fixture that exercises only some types would hide a whole class of defect."""
        present = {g["type"] for g in valid_map["groups"]}
        declared_absent = {a["type"] for a in valid_map["scope_guard"]["absent_types"]}
        assert present | declared_absent == set(V.GROUP_TYPES)


class TestSchemaShape:
    def test_missing_required_top_level_key_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        del doc["angle_applicability"]
        assert "schema" in _rules(V.validate_keyword_map(doc, registry))

    def test_unknown_group_type_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["groups"][0]["type"] = "weakness"  # a group type from a different survey
        assert "schema" in _rules(V.validate_keyword_map(doc, registry))

    def test_bad_timestamp_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["meta"]["as_of"] = "2026-08-04"  # date only, not RFC3339
        assert "schema" in _rules(V.validate_keyword_map(doc, registry))

    def test_schema_failure_short_circuits(self, valid_map, registry):
        """Semantic rules must not run on a doc that failed shape — they would crash."""
        doc = copy.deepcopy(valid_map)
        del doc["groups"]
        assert _rules(V.validate_keyword_map(doc, registry)) == {"schema"}


class TestGroupRules:
    def test_duplicate_group_id_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["groups"][1]["id"] = doc["groups"][0]["id"]
        assert "group-id-unique" in _rules(V.validate_keyword_map(doc, registry))

    def test_expansions_above_declared_cap_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        g = doc["groups"][0]
        g["expansion_cap"] = 3
        g["expansions"] = [
            {"term": f"t{i}", "provenance": "model-knowledge", "relation": "related"}
            for i in range(4)
        ]
        assert "expansion-cap" in _rules(V.validate_keyword_map(doc, registry))

    def test_thin_group_without_short_reason_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["groups"][0]["expansions"] = doc["groups"][0]["expansions"][:2]
        doc["groups"][0].pop("short_reason", None)
        assert "expansion-floor" in _rules(V.validate_keyword_map(doc, registry))

    def test_thin_group_with_short_reason_passes(self, valid_map, registry):
        """The escape hatch must actually work — never pad to clear a floor."""
        doc = copy.deepcopy(valid_map)
        doc["groups"][0]["expansions"] = doc["groups"][0]["expansions"][:2]
        doc["groups"][0]["short_reason"] = "the category has no sister terms any directory indexes"
        assert "expansion-floor" not in _rules(V.validate_keyword_map(doc, registry))

    def test_unaccounted_group_type_fails(self, valid_map, registry):
        """A type neither present nor declared absent silently empties its angle."""
        doc = copy.deepcopy(valid_map)
        doc["groups"] = [g for g in doc["groups"] if g["type"] != "design-system"]
        doc["scope_guard"]["absent_types"] = [
            a for a in doc["scope_guard"]["absent_types"] if a["type"] != "design-system"
        ]
        assert "group-type-accounted" in _rules(V.validate_keyword_map(doc, registry))

    def test_declared_absent_type_passes(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["groups"] = [g for g in doc["groups"] if g["type"] != "design-system"]
        others = [a for a in doc["scope_guard"]["absent_types"] if a["type"] != "design-system"]
        doc["scope_guard"]["absent_types"] = [
            *others,
            {"type": "design-system", "reason": "no published system matches this archetype"},
        ]
        assert "group-type-accounted" not in _rules(V.validate_keyword_map(doc, registry))

    def test_all_alt_label_expansions_fails(self, valid_map, registry):
        """A map of nothing but alt-labels is a spelling list, not an expansion."""
        doc = copy.deepcopy(valid_map)
        for g in doc["groups"]:
            for e in g["expansions"]:
                e["relation"] = "alt-label"
        assert "relation-variety" in _rules(V.validate_keyword_map(doc, registry))

    def test_uniform_groups_with_varied_kinds_across_the_map_pass(self, valid_map, registry):
        """Regression: a group may legitimately be uniform, so requiring a MIXED group
        false-failed a map whose groups were each uniform but collectively varied."""
        doc = copy.deepcopy(valid_map)
        kinds = ["broader", "narrower", "related"]
        for i, g in enumerate(doc["groups"]):
            for e in g["expansions"]:
                e["relation"] = kinds[i % len(kinds)]
        assert all(len({e["relation"] for e in g["expansions"]}) == 1 for g in doc["groups"])
        assert "relation-variety" not in _rules(V.validate_keyword_map(doc, registry))


class TestProbeRecord:
    def test_probe_discovered_provenance_without_probe_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["groups"][0]["expansions"][0]["provenance"] = "probe-discovered"
        doc.pop("probe", None)
        assert "probe-record" in _rules(V.validate_keyword_map(doc, registry))

    def test_unperformed_probe_without_reason_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["probe"] = {"performed": False}
        assert "probe-record" in _rules(V.validate_keyword_map(doc, registry))


class TestSourceAccounting:
    def test_degraded_sanitization_without_cause_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["sources"]["active"][0]["sanitization"] = {"status": "content-withheld"}
        assert "sanitization-cause" in _rules(V.validate_keyword_map(doc, registry))

    def test_forbidden_by_terms_source_in_active_fails(self, valid_map, registry):
        """A source excluded on its terms was never read; recording it active is a false receipt."""
        doc = copy.deepcopy(valid_map)
        doc["sources"]["active"][0]["access"] = "forbidden-by-terms"
        assert "forbidden-source-not-active" in _rules(V.validate_keyword_map(doc, registry))


class TestAngleVerdicts:
    def test_missing_angle_verdict_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["angle_applicability"] = doc["angle_applicability"][:-1]
        assert "angle-verdict-complete" in _rules(V.validate_keyword_map(doc, registry))

    def test_always_on_angle_judged_inapplicable_fails(self, valid_map, registry):
        """The mirror. Corroborating only ONE direction of a two-directional property

        reads as covered and is not. An always-on angle switched off is how a survey
        silently does nothing, so the positive direction needs a check as much as the negative.
        """
        doc = copy.deepcopy(valid_map)
        for a in doc["angle_applicability"]:
            if a["angle_id"] == "a1":
                a["holds"] = False
                a["reason"] = "judged not worth running"
        assert "always-on-angle-holds" in _rules(V.validate_keyword_map(doc, registry))

    def test_unknown_angle_id_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["angle_applicability"].append(
            {
                "angle_id": "z9",
                "precondition": "invented",
                "holds": True,
                "reason": "not in the registry",
            }
        )
        assert "angle-unknown" in _rules(V.validate_keyword_map(doc, registry))


class TestRegistryContract:
    def test_registry_declares_every_angle_the_spec_names(self, registry):
        ids = {a["id"] for a in registry["angles"]}
        assert ids == {"a1", "a2", "b1", "b2", "b3", "b4", "b5"}

    def test_always_on_angles_are_exactly_a1_a2(self, registry):
        always = {a["id"] for a in registry["angles"] if a["trigger"] == "always"}
        assert always == {"a1", "a2"}

    def test_every_angle_names_a_fallback(self, registry):
        """An angle whose only source can die has no business being in the taxonomy."""
        for a in registry["angles"]:
            assert a.get("fallback"), a["id"]

    def test_every_angle_declares_applicable_group_types(self, registry):
        valid = set(V.GROUP_TYPES)
        for a in registry["angles"]:
            declared = set(a["applicable_group_types"])
            assert declared, a["id"]
            assert declared <= valid, (a["id"], declared - valid)

    def test_every_angle_source_resolves_in_the_registry(self, registry):
        """An angle naming a source the registry does not define cannot be executed."""
        known = set(registry["sources"])
        for a in registry["angles"]:
            unknown = set(a["sources"]) - known
            assert not unknown, (a["id"], unknown)

    def test_no_angle_sources_an_excluded_site(self, registry):
        """The screenshot galleries are excluded; an angle must not reach for one."""
        excluded = set(registry["excluded"])
        for a in registry["angles"]:
            assert not (set(a["sources"]) & excluded), a["id"]

    def test_every_angle_fallback_resolves_in_the_registry(self, registry):
        """The mirror of the sources check — and it caught a real one.

        a fallback naming no source block is the same as having none: a fallback that cannot
        be resolved is the same as having none, and it would only surface at the moment the
        primary source failed, which is exactly when the angle can least afford it. The
        sources check existed; its mirror did not.
        """
        known = set(registry["sources"])
        for a in registry["angles"]:
            assert a["fallback"] in known, (a["id"], a["fallback"])

    def test_no_angle_falls_back_to_an_excluded_site(self, registry):
        excluded = set(registry["excluded"])
        for a in registry["angles"]:
            assert a["fallback"] not in excluded, (a["id"], a["fallback"])

    def test_every_angle_has_a_reference_file(self, registry):
        """A brief may cite `references/angles/{angle_id}.md`; a missing one is a dead link."""
        for a in registry["angles"]:
            assert (ANGLES / f"{a['id']}.md").is_file(), a["id"]

    def test_no_orphan_angle_reference_files(self, registry):
        """The mirror: a reference for a dropped angle is a document nothing routes to."""
        known = {a["id"] for a in registry["angles"]}
        on_disk = {p.stem for p in ANGLES.glob("*.md")}
        assert on_disk == known, on_disk ^ known

    def test_angle_reference_declares_its_sources_and_fallback(self, registry):
        """The reference and the registry must not drift on the two facts that route work."""
        for a in registry["angles"]:
            text = (ANGLES / f"{a['id']}.md").read_text()
            for src in a["sources"]:
                assert src in text, (a["id"], src)
            assert a["fallback"] in text, (a["id"], a["fallback"])

    def test_no_angle_reference_names_an_excluded_source_as_usable(self, registry):
        """An angle reference may name an excluded site deliberately, to say DO NOT reach for it.

        The check is that any mention sits next to an exclusion word — a reference that named
        one neutrally would read as an instruction to use it.
        """
        for a in registry["angles"]:
            text = (ANGLES / f"{a['id']}.md").read_text().lower()
            for site in registry["excluded"]:
                if site in text:
                    assert any(
                        w in text for w in ("exclud", "do not", "never", "prohibit", "blocks")
                    ), (a["id"], site)

    def test_cross_class_fallback_is_explained(self, registry):
        """A fallback outside the angle's own sources is legitimate but must say why.

        an angle may degrade to a fallback outside its own source list, which is a deliberate
        change of evidence class — defensible, but only because the rationale
        states it. An unexplained one is indistinguishable from a copy-paste error.
        """
        for a in registry["angles"]:
            if a["fallback"] not in a["sources"]:
                assert len(a.get("fallback_rationale", "")) > 80, a["id"]


@pytest.fixture
def valid_search() -> dict:
    return yaml.safe_load((FIXTURES / "search-output.valid.yaml").read_text())


class TestSearchShape:
    def test_valid_fixture_passes_clean(self, valid_search, valid_map, registry):
        assert V.validate_search(valid_search, valid_map, registry) == []

    def test_missing_outcome_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        del doc["outcome"]
        assert "schema" in _rules(V.validate_search(doc, valid_map, registry))

    def test_schema_failure_short_circuits(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["outcome"] = "invented"
        assert _rules(V.validate_search(doc, valid_map, registry)) == {"schema"}


class TestOutcomeBranches:
    def test_ran_without_coverage_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        del doc["coverage"]
        assert "ran-requires-coverage" in _rules(V.validate_search(doc, valid_map, registry))

    def test_not_run_without_block_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["outcome"] = "not_run"
        assert "outcome-block-required" in _rules(V.validate_search(doc, valid_map, registry))

    def test_not_run_carrying_coverage_fails(self, valid_search, valid_map, registry):
        """An unrun angle owes no cells; writing them manufactures zeros that look like searches."""
        doc = copy.deepcopy(valid_search)
        doc["outcome"] = "not_run"
        doc["not_run"] = {"reason": "precondition did not hold"}
        assert "unrun-angle-has-cells" in _rules(V.validate_search(doc, valid_map, registry))

    def test_clean_not_run_passes(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["outcome"] = "not_run"
        doc["not_run"] = {"reason": "archetype.primary is web-app, so no platform HIG applies"}
        for k in ("coverage", "retrieval_summary", "bound", "candidates"):
            doc.pop(k, None)
        assert V.validate_search(doc, valid_map, registry) == []


class TestCoverageReconciliation:
    def test_reached_cell_without_counts_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0].pop("returned", None)
        assert "reached-needs-counts" in _rules(V.validate_search(doc, valid_map, registry))

    def test_non_reached_cell_without_cause_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        c = doc["coverage"][0]
        c["status"] = "unreachable"
        c.pop("cause", None)
        c.pop("returned", None)
        c.pop("kept", None)
        assert "status-needs-cause" in _rules(V.validate_search(doc, valid_map, registry))

    def test_kept_above_returned_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        c = next(x for x in doc["coverage"] if x["status"] == "reached")
        c["kept"] = c["returned"] + 1
        assert "kept-exceeds-returned" in _rules(V.validate_search(doc, valid_map, registry))

    def test_status_counts_disagreeing_with_cells_fails(self, valid_search, valid_map, registry):
        """The duplication IS the check — a discrepancy is a failure laundered into a zero."""
        doc = copy.deepcopy(valid_search)
        doc["retrieval_summary"]["status_counts"]["reached"] += 3
        assert "summary-reconciles" in _rules(V.validate_search(doc, valid_map, registry))

    def test_degraded_source_missing_from_summary_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["retrieval_summary"]["degraded_sources"] = []
        assert "degraded-source-recorded" in _rules(V.validate_search(doc, valid_map, registry))

    def test_cell_group_not_in_map_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0]["group_id"] = "not-a-group-in-the-map"
        assert "cell-group-known" in _rules(V.validate_search(doc, valid_map, registry))

    def test_cell_source_not_in_registry_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0]["source_id"] = "not-a-source"
        assert "cell-source-known" in _rules(V.validate_search(doc, valid_map, registry))

    def test_cell_sourcing_an_excluded_site_fails(self, valid_search, valid_map, registry):
        """Reaching a ToS-excluded source is a policy breach, not a coverage detail."""
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0]["source_id"] = "mobbin"
        assert "cell-source-excluded" in _rules(V.validate_search(doc, valid_map, registry))


class TestBound:
    def test_bound_hit_without_dropped_note_fails(self, valid_search, valid_map, registry):
        """A cap that bound and is not described reads downstream as exhaustive coverage."""
        doc = copy.deepcopy(valid_search)
        doc["bound"]["hit"] = True
        doc["bound"].pop("dropped_note", None)
        assert "bound-hit-needs-note" in _rules(V.validate_search(doc, valid_map, registry))

    def test_candidates_above_cap_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["bound"]["cap"] = 1
        assert "cap-respected" in _rules(V.validate_search(doc, valid_map, registry))


class TestRecordFilename:
    """Injectivity, not merely round-tripping."""

    def test_filename_safe_id_is_identity(self):
        assert V.record_filename("ARIA-combobox") == "ARIA-combobox"
        assert V.record_filename("WCAG-2.4.11") == "WCAG-2.4.11"

    def test_id_slashes_do_not_become_directories(self):
        out = V.record_filename("HIG-apple/navigation bars")
        assert "/" not in out and ":" not in out

    def test_ids_differing_only_in_collapsed_chars_get_different_names(self):
        """A non-injective mapping merges two records into one file."""
        a = V.record_filename("DS-carbon design/tokens")
        b = V.record_filename("DS-carbon design-tokens")
        assert a != b

    def test_a_hashed_stem_fed_back_in_does_not_collide_with_its_own_source(self):
        """The two branches must not share an output namespace.

        The identity branch returns filename-safe input unchanged — and a hashed stem IS
        filename-safe, so without a guard it round-trips to itself and collides with the id it
        was derived from. Testing collisions only WITHIN the hashing branch gave false
        assurance: this is the collision that was actually constructible.
        """
        original = "DS-carbon/tokens"
        stem = V.record_filename(original)
        assert V.record_filename(stem) != stem
        assert V.record_filename(stem) != V.record_filename(original)

    def test_an_all_unsafe_id_still_gets_a_distinct_name(self):
        """A bare digest would collide with any id that happens to look like one."""
        a = V.record_filename("///")
        b = V.record_filename(a)
        assert a != b

    def test_long_id_is_bounded(self):
        out = V.record_filename("DS-" + "x" * 500 + "/y")
        assert len(out) <= V._PREFIX_CAP + 14  # prefix + '--' + 12-hex digest


class TestCoverageCompleteness:
    """The mirror the salvaged validator lost entirely.

    `_applicable_set()` was defined and never called, so a search output could omit an
    applicable (group x source) pair and pass clean — and the pair with no cell is the
    "unexplained gap, not a zero" the schema's own text claims is caught. It is the mechanism
    the provable-absence rule rests on, and it needs BOTH directions: a missing cell, and a
    cell for a pair the angle never owed.
    """

    def test_missing_applicable_cell_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        dropped = doc["coverage"].pop(0)
        doc["retrieval_summary"]["status_counts"][dropped["status"]] -= 1
        assert "coverage-complete" in _rules(V.validate_search(doc, valid_map, registry))

    def test_cell_outside_the_applicable_set_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["coverage"].append(
            {
                "group_id": "admin-console",  # a screen-archetype group; a2 does not query it
                "source_id": "openalternative",
                "queries": ["not owed by this angle"],
                "timestamp": "2026-08-04T10:20:00Z",
                "status": "reached",
                "returned": 1,
                "kept": 1,
            }
        )
        doc["retrieval_summary"]["status_counts"]["reached"] += 1
        assert "cell-in-applicable-set" in _rules(V.validate_search(doc, valid_map, registry))

    def test_valid_fixture_has_a_complete_grid(self, valid_search, valid_map, registry):
        """Guards the fixture itself — a fixture with an incomplete grid would mask the rule."""
        assert V.validate_search(valid_search, valid_map, registry) == []


class TestMalformedInputs:
    """The map is a second untrusted input, and the CLI reads files a caller named.

    Before these existed, a search run against an empty or wrong --keyword-map raised a raw
    traceback instead of reporting, and a missing path or a YAML syntax error exited 1 —
    indistinguishable from "the artifact failed the gate", which sends a caller off to edit an
    artifact that may be perfectly fine.
    """

    @pytest.mark.parametrize("bad", [None, "a string", [], {}, {"groups": None}])
    def test_malformed_keyword_map_reports_rather_than_raises(self, valid_search, registry, bad):
        rules = _rules(V.validate_search(valid_search, bad, registry))
        assert "keyword-map-invalid" in rules

    def test_search_output_passed_as_the_map_is_reported(self, valid_search, registry):
        """--keyword-map aimed at the wrong file is a first-order caller mistake."""
        assert "keyword-map-invalid" in _rules(
            V.validate_search(valid_search, copy.deepcopy(valid_search), registry)
        )

    def test_cli_missing_file_exits_2(self, capsys):
        assert V.main(["keyword-map", str(FIXTURES / "does-not-exist.yaml")]) == 2
        assert "FAIL input" in capsys.readouterr().out

    def test_cli_unparseable_yaml_exits_2(self, tmp_path, capsys):
        bad = tmp_path / "bad.yaml"
        bad.write_text("groups: [\n  unclosed")
        assert V.main(["keyword-map", str(bad)]) == 2
        assert "not valid YAML" in capsys.readouterr().out

    def test_cli_clean_artifact_exits_0(self):
        assert V.main(["keyword-map", str(FIXTURES / "ui-pattern-vocabulary-map.valid.yaml")]) == 0

    def test_cli_failing_artifact_exits_1(self, tmp_path, valid_map):
        doc = copy.deepcopy(valid_map)
        doc["groups"][1]["id"] = doc["groups"][0]["id"]
        f = tmp_path / "dup.yaml"
        f.write_text(yaml.safe_dump(doc))
        assert V.main(["keyword-map", str(f)]) == 1

    def test_cli_search_subcommand_routes(self):
        assert (
            V.main(
                [
                    "search",
                    str(FIXTURES / "search-output.valid.yaml"),
                    "--keyword-map",
                    str(FIXTURES / "ui-pattern-vocabulary-map.valid.yaml"),
                ]
            )
            == 0
        )


class TestUniquenessAndSubstitution:
    def test_duplicate_coverage_cell_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        dup = copy.deepcopy(doc["coverage"][0])
        dup["status"] = "unreachable"
        dup["cause"] = "a contradictory second record for the same pair"
        dup.pop("returned", None)
        dup.pop("kept", None)
        doc["coverage"].append(dup)
        doc["retrieval_summary"]["status_counts"]["unreachable"] = 1
        doc["retrieval_summary"]["degraded_sources"].append(
            {"source_id": dup["source_id"], "status": "unreachable", "cause": "contradiction"}
        )
        assert "cell-pair-unique" in _rules(V.validate_search(doc, valid_map, registry))

    def test_duplicate_angle_verdict_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["angle_applicability"].append(copy.deepcopy(doc["angle_applicability"][0]))
        assert "angle-verdict-unique" in _rules(V.validate_keyword_map(doc, registry))

    def test_fallback_to_an_excluded_source_fails(self, valid_search, valid_map, registry):
        """Substituting an excluded source is the same breach as querying it directly."""
        doc = copy.deepcopy(valid_search)
        doc["retrieval_summary"]["degraded_sources"][0]["fallback_used"] = "mobbin"
        assert "cell-source-excluded" in _rules(V.validate_search(doc, valid_map, registry))

    def test_fallback_to_an_unknown_source_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["retrieval_summary"]["degraded_sources"][0]["fallback_used"] = "not-a-source"
        assert "cell-source-known" in _rules(V.validate_search(doc, valid_map, registry))

    def test_fallback_other_than_the_declared_one_fails(self, valid_search, valid_map, registry):
        """One fallback per angle is the registry's; substituting another is not the run's call."""
        doc = copy.deepcopy(valid_search)
        doc["retrieval_summary"]["degraded_sources"][0]["fallback_used"] = "govuk"
        assert "fallback-declared" in _rules(V.validate_search(doc, valid_map, registry))

    def test_vacated_while_work_was_owed_fails(self, valid_search, valid_map, registry):
        """An angle may not vacate itself when the applicable set is demonstrably non-empty."""
        doc = copy.deepcopy(valid_search)
        doc["outcome"] = "vacated"
        doc["vacated"] = {"reason": "claims nothing was applicable"}
        for k in ("coverage", "retrieval_summary", "bound", "candidates", "unadmitted"):
            doc.pop(k, None)
        assert "vacated-not-empty" in _rules(V.validate_search(doc, valid_map, registry))


class TestVisualCandidateRules:
    """The type-specific rules. All 16 were emitted and untested until a planted defect showed it.

    Stripping the sibling's market-specific test classes left the visual rules with no coverage
    at all — the suite was green and three planted defects survived it. A rule sweep, not a
    passing suite, is what proves the gate.
    """

    def test_missing_corpus_version_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0].pop("corpus_version", None)
        # schema-REQUIRED, so the shape layer owns it — asserting the semantic rule here would
        # be asserting a rule that can never fire
        assert "schema" in _rules(V.validate_search(doc, valid_map, registry))

    def test_missing_prescriptivity_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0].pop("prescriptivity", None)
        assert "schema" in _rules(V.validate_search(doc, valid_map, registry))

    def test_non_dtcg_token_claim_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["token_format"] = "Style Dictionary 3"
        assert "token-format-dtcg" in _rules(V.validate_search(doc, valid_map, registry))

    def test_unversioned_token_claim_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["token_format"] = "DTCG"
        assert "token-format-versioned" in _rules(V.validate_search(doc, valid_map, registry))

    def test_versioned_dtcg_claim_passes(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["token_format"] = "DTCG 2025.10"
        rules = _rules(V.validate_search(doc, valid_map, registry))
        assert "token-format-dtcg" not in rules and "token-format-versioned" not in rules

    def test_id_not_matching_its_class_shape_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["id"] = "WCAG-2.4.11"  # declared aria-pattern
        assert "id-class-shape" in _rules(V.validate_search(doc, valid_map, registry))

    def test_admission_without_corpus_url_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["admission"].pop("corpus_url", None)
        assert "schema" in _rules(V.validate_search(doc, valid_map, registry))

    def test_admission_without_corpus_release_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["admission"].pop("corpus_release", None)
        assert "schema" in _rules(V.validate_search(doc, valid_map, registry))

    def test_duplicate_candidate_id_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["candidates"].append(copy.deepcopy(doc["candidates"][0]))
        assert "candidate-id-unique" in _rules(V.validate_search(doc, valid_map, registry))

    def test_candidate_from_an_unknown_cell_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["found_by"] = "nogroup/nosource"
        assert "candidate-provenance" in _rules(V.validate_search(doc, valid_map, registry))

    def test_kept_not_matching_carried_rows_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        cell = next(c for c in doc["coverage"] if c["status"] == "reached")
        cell["kept"] += 1
        assert "kept-matches-rows" in _rules(V.validate_search(doc, valid_map, registry))

    def test_bound_cap_disagreeing_with_registry_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["bound"]["cap"] = 999
        assert "cap-matches-registry" in _rules(V.validate_search(doc, valid_map, registry))

    def test_declared_hit_under_the_cap_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["bound"]["hit"] = True
        doc["bound"]["dropped_note"] = "claims a tail was dropped"
        assert "bound-hit-consistent" in _rules(V.validate_search(doc, valid_map, registry))

    def test_design_system_group_without_negative_terms_fails(self, valid_map, registry):
        """Scoped to design-system groups only — system NAMES collide, identifiers do not."""
        doc = copy.deepcopy(valid_map)
        for g in doc["groups"]:
            if g["type"] == "design-system":
                g.pop("negative_terms", None)
        assert "negative-terms-required" in _rules(V.validate_keyword_map(doc, registry))

    def test_component_group_without_negative_terms_passes(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        for g in doc["groups"]:
            if g["type"] == "component":
                g.pop("negative_terms", None)
        assert "negative-terms-required" not in _rules(V.validate_keyword_map(doc, registry))


class TestTriggerAnchors:
    """A conditional trigger needs at least one required-rooted leg; optional legs widen."""

    def test_shipped_registry_is_clean(self, registry):
        assert V.anchor_failures(registry) == []

    def test_anchor_on_an_optional_field_fails(self, registry):
        reg = copy.deepcopy(registry)
        next(a for a in reg["angles"] if a["id"] == "b1")["trigger_anchor"] = [
            "archetype.secondary"
        ]
        assert "anchor-must-be-required" in _rules(V.anchor_failures(reg))

    def test_conditional_angle_with_no_anchor_fails(self, registry):
        reg = copy.deepcopy(registry)
        next(a for a in reg["angles"] if a["id"] == "b1")["trigger_anchor"] = []
        assert "anchor-required" in _rules(V.anchor_failures(reg))

    def test_always_on_angle_declaring_an_anchor_fails(self, registry):
        reg = copy.deepcopy(registry)
        next(a for a in reg["angles"] if a["id"] == "a1")["trigger_anchor"] = ["ui.has_ui"]
        assert "anchor-only-on-conditional" in _rules(V.anchor_failures(reg))

    def test_optional_legs_are_legitimate_as_wideners(self, registry):
        """b1/b2/b3 all carry optional disjuncts beside required anchors — that fails OPEN."""
        for aid in ("b1", "b2", "b3"):
            a = next(x for x in registry["angles"] if x["id"] == aid)
            assert a["widening_legs"], aid
            assert all(x in V.REQUIRED_CAPABILITY_FIELDS for x in a["trigger_anchor"]), aid


class TestReviewFindings:
    """Cases a code review found untested. Each would have shipped green without these."""

    def test_a_dtcg_compatible_claim_is_not_a_dtcg_claim(self, valid_search, valid_map, registry):
        """A substring test passed 'Style Dictionary 3 (DTCG-compatible)'. It is not DTCG."""
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["token_format"] = "Style Dictionary 3 (DTCG-compatible)"
        assert "token-format-dtcg" in _rules(V.validate_search(doc, valid_map, registry))

    def test_unadmitted_row_with_a_bogus_cell_fails(self, valid_search, valid_map, registry):
        """An unadmitted row feeds the kept arithmetic exactly as a candidate does.

        Unverified, it vanishes from the cell it should have named — and if that cell is
        reached, the caller gets a misdirecting kept-matches-rows on a cell that is fine.
        """
        doc = copy.deepcopy(valid_search)
        doc["unadmitted"][0]["found_by"] = "typo/aria-apg"
        assert "candidate-provenance" in _rules(V.validate_search(doc, valid_map, registry))

    def test_id_shapes_cover_exactly_the_schema_enum(self):
        """Adding an id_class to the schema must not silently disable its shape check."""
        import json

        schema = json.loads((V.SCHEMAS / "search-output.schema.json").read_text())
        enum = set(schema["$defs"]["candidate"]["properties"]["id_class"]["enum"])
        assert set(V._ID_SHAPES) == enum

    @pytest.mark.parametrize(
        "id_class,good,bad",
        [
            ("aria-pattern", "ARIA-combobox", "ARIA_combobox"),
            ("wcag-criterion", "WCAG-2.4.11", "WCAG-2.4"),
            ("design-system", "DS-carbon", "DS-carbon-datatable-extra!"),
            ("deceptive-pattern", "DP-confirmshaming", "confirmshaming"),
            ("platform-guideline", "HIG-apple-navigation", "HIG-apple"),
        ],
    )
    def test_every_id_class_shape_is_exercised(self, id_class, good, bad):
        """Four of five regexes were never exercised; a typo in any would have shipped."""
        shape = V._ID_SHAPES[id_class]
        assert shape.match(good), (id_class, good)
        assert not shape.match(bad), (id_class, bad)

    def _broken_registry(self):
        reg = copy.deepcopy(V.load_registry())
        next(a for a in reg["angles"] if a["id"] == "b1")["trigger_anchor"] = [
            "archetype.secondary"
        ]
        return reg

    def test_a_registry_fault_exits_2_from_the_keyword_map_subcommand(self, monkeypatch, capsys):
        """Two defects in sequence: anchor_failures was once defined and never called, and then
        it reported a PACKAGE fault as an artifact failure at exit 1 — sending a caller off to
        edit a map that was perfectly fine. The registry ships inside the package; a defect in
        it belongs with the could-not-be-used class."""
        reg = self._broken_registry()
        monkeypatch.setattr(V, "load_registry", lambda *a, **k: reg)
        assert V.main(["keyword-map", str(FIXTURES / "ui-pattern-vocabulary-map.valid.yaml")]) == 2
        assert "anchor-must-be-required" in capsys.readouterr().out

    def test_a_registry_fault_also_exits_2_from_the_search_subcommand(self, monkeypatch):
        """The check used to run on only one of the two paths."""
        reg = self._broken_registry()
        monkeypatch.setattr(V, "load_registry", lambda *a, **k: reg)
        assert (
            V.main(
                [
                    "search",
                    str(FIXTURES / "search-output.valid.yaml"),
                    "--keyword-map",
                    str(FIXTURES / "ui-pattern-vocabulary-map.valid.yaml"),
                ]
            )
            == 2
        )

    def test_vacated_without_its_block_fails(self, valid_search, valid_map, registry):
        """Only the not_run side of outcome-block-required was tested."""
        doc = copy.deepcopy(valid_search)
        doc["outcome"] = "vacated"
        for k in ("coverage", "retrieval_summary", "bound", "candidates", "unadmitted"):
            doc.pop(k, None)
        assert "outcome-block-required" in _rules(V.validate_search(doc, valid_map, registry))

    def test_unknown_angle_on_the_search_side_fails(self, valid_search, valid_map, registry):
        """Only the map-side angle-unknown was tested."""
        doc = copy.deepcopy(valid_search)
        doc["meta"]["angle_id"] = "z9"
        assert "angle-unknown" in _rules(V.validate_search(doc, valid_map, registry))

    def test_absent_trigger_anchor_fails_like_an_empty_one(self):
        reg = copy.deepcopy(V.load_registry())
        next(a for a in reg["angles"] if a["id"] == "b1").pop("trigger_anchor", None)
        assert "anchor-required" in _rules(V.anchor_failures(reg))

    def test_cli_non_utf8_input_exits_2(self, tmp_path, capsys):
        """read_text raises UnicodeDecodeError, which is a ValueError and was uncaught."""
        bad = tmp_path / "binary.yaml"
        bad.write_bytes(b"\x80\x81\x82")
        assert V.main(["keyword-map", str(bad)]) == 2
        assert "FAIL input" in capsys.readouterr().out

class TestExtractsBoundary:
    """`--extracts` supplied but unusable must not read as "the rows are wrong".

    A missing directory, an empty one and a genuine citation mismatch all collapsed to the
    same per-row failure, which blames the author. The synthesis brief tells the agent to
    self-heal to exit 0; from a per-row failure the easiest route there is deleting the
    register's citations — turning a bad path into destruction of the evidence chain.
    Spec `prior-art-type-config` Part D §D2.
    """

    def test_unreadable_directory_names_the_path_not_the_rows(self, tmp_path, capsys):
        code = V.main(
            ["synthesis", str(FIXTURES / "convention-register.valid.yaml"), "--extracts", str(tmp_path / "no-such-dir")]
        )
        out = capsys.readouterr().out
        assert code == 1
        assert "extracts-unreadable" in out
        assert "row-without-record" not in out

    def test_empty_directory_is_its_own_cause(self, tmp_path, capsys):
        (tmp_path / "empty").mkdir()
        code = V.main(
            ["synthesis", str(FIXTURES / "convention-register.valid.yaml"), "--extracts", str(tmp_path / "empty")]
        )
        out = capsys.readouterr().out
        assert code == 1
        assert "extracts-empty" in out
        assert "row-without-record" not in out

    def test_empty_directory_with_nothing_cited_stays_green(self, tmp_path, capsys):
        """A survey that legitimately extracted nothing has an empty directory AND a register
        citing nothing. Those agree; failing there is the S22 false positive again.
        """
        doc = yaml.safe_load((FIXTURES / "convention-register.valid.yaml").read_text())
        doc["conventions"] = []
        f = tmp_path / "empty-register.yaml"
        f.write_text(yaml.safe_dump(doc))
        (tmp_path / "empty").mkdir()
        V.main(["synthesis", str(f), "--extracts", str(tmp_path / "empty")])
        assert "extracts-empty" not in capsys.readouterr().out


class TestQueueCoverage:
    """The third direction: FROZEN QUEUE -> record.

    `row-without-record` checks register->file and `record-without-row` checks file->register,
    so a queue row that produced nothing is invisible to both. A live run shipped a register at
    exit 0 with 5 of 49 rows uncovered. Spec `prior-art-queue-coverage`.
    """

    def _queue(self, tmp_path, ids):
        q = tmp_path / "extract-queue.yaml"
        q.write_text(yaml.safe_dump({"queue": [{"item_id": i} for i in ids]}))
        return q

    def test_uncovered_queue_row_fails(self, tmp_path):
        ex = tmp_path / "extract"
        ex.mkdir()
        (ex / "ARIA-button.md").write_text("x")
        out = V._queue_coverage(self._queue(tmp_path, ["ARIA-button", "ARIA-switch"]), ex, None)
        assert any("queue-row-without-record" in f and "ARIA-switch" in f for f in out)
        assert not any("ARIA-button" in f for f in out)

    def test_full_coverage_passes(self, tmp_path):
        ex = tmp_path / "extract"
        ex.mkdir()
        for i in ("ARIA-button", "ARIA-switch"):
            (ex / f"{i}.md").write_text("x")
        assert V._queue_coverage(self._queue(tmp_path, ["ARIA-button", "ARIA-switch"]), ex, 2) == []

    def test_unreadable_queue_names_its_own_cause(self, tmp_path):
        ex = tmp_path / "extract"
        ex.mkdir()
        out = V._queue_coverage(tmp_path / "nope.yaml", ex, None)
        assert len(out) == 1 and "queue-unreadable" in out[0]

    def test_extract_count_is_judged_against_the_queue_not_the_directory(self, tmp_path):
        """A stray file inflates meta.extract_count, which is taken from a listing."""
        ex = tmp_path / "extract"
        ex.mkdir()
        (ex / "ARIA-button.md").write_text("x")
        (ex / "stray.md").write_text("x")
        out = V._queue_coverage(self._queue(tmp_path, ["ARIA-button"]), ex, 2)
        assert any("extract-count-vs-queue" in f for f in out)
