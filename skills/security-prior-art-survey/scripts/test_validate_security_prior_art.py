# ruff: noqa: D103
"""B3 — the wave-1 validator: shape only, never semantic judgment.

Test names are the documentation — each names the single rule it proves fires.

Each mutation test proves one rule fires. The valid fixtures must stay clean, because a
validator that fails an honest artifact is worse than none: it trains producers to work around
the gate.
"""

import copy
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

HERE = Path(__file__).parent
FIXTURES = HERE / "fixtures"
SCRIPT = HERE / "validate_security_prior_art.py"
REGISTRY = HERE.parent / "references" / "source-registry.yaml"

sys.path.insert(0, str(HERE))
import validate_security_prior_art as v  # noqa: E402


def _map():
    return yaml.safe_load((FIXTURES / "threat-vocabulary-map.valid.yaml").read_text())


def _search():
    return yaml.safe_load((FIXTURES / "search-output.valid.yaml").read_text())


def _check_map(doc):
    return v.validate_keyword_map(doc)


def _check_search(doc, mapping=None):
    return v.validate_search(doc, mapping or _map(), v.load_registry(REGISTRY))


# ── the valid fixtures are clean ────────────────────────────────────────────────


def test_valid_map_passes():
    assert _check_map(_map()) == []


def test_valid_search_passes():
    assert _check_search(_search()) == []


def test_cli_exits_zero_on_both_fixtures():
    for kind, fx, extra in (
        ("keyword-map", "threat-vocabulary-map.valid.yaml", []),
        (
            "search",
            "search-output.valid.yaml",
            ["--keyword-map", str(FIXTURES / "threat-vocabulary-map.valid.yaml")],
        ),
    ):
        r = subprocess.run(
            [sys.executable, str(SCRIPT), kind, str(FIXTURES / fx), *extra],
            capture_output=True,
            text=True,
        )
        assert r.returncode == 0, f"{kind}: {r.stdout}{r.stderr}"


def test_cli_exits_nonzero_and_prints_fail_lines():
    doc = _map()
    doc["groups"][0]["expansions"] = []
    bad = FIXTURES / "_tmp_bad_map.yaml"
    bad.write_text(yaml.safe_dump(doc))
    try:
        r = subprocess.run(
            [sys.executable, str(SCRIPT), "keyword-map", str(bad)],
            capture_output=True,
            text=True,
        )
        assert r.returncode != 0
        assert "FAIL " in r.stdout
    finally:
        bad.unlink()


# ── keyword-map rules ──────────────────────────────────────────────────────────


def test_map_schema_violation_is_reported():
    doc = _map()
    doc["groups"][0]["type"] = "not-a-type"
    assert any("schema" in f for f in _check_map(doc))


def test_map_duplicate_group_id():
    doc = _map()
    doc["groups"][1]["id"] = doc["groups"][0]["id"]
    assert any("group-id-unique" in f for f in _check_map(doc))


def test_map_expansion_over_cap():
    doc = _map()
    g = doc["groups"][0]
    g["expansion_cap"] = 3
    g["expansions"] = g["expansions"] + [
        {"term": f"x{i}", "provenance": "model-knowledge", "relation": "related"} for i in range(3)
    ]
    assert any("expansion-cap" in f for f in _check_map(doc))


def test_map_expansion_under_floor_without_reason():
    doc = _map()
    doc["groups"][0]["expansions"] = doc["groups"][0]["expansions"][:1]
    assert any("expansion-floor" in f for f in _check_map(doc))


def test_map_expansion_under_floor_with_reason_is_allowed():
    doc = _map()
    doc["groups"][0]["expansions"] = doc["groups"][0]["expansions"][:1]
    doc["groups"][0]["short_reason"] = "the concept has no sister terms in any indexed corpus"
    assert not any("expansion-floor" in f for f in _check_map(doc))


def test_map_group_type_neither_present_nor_declared_absent():
    doc = _map()
    doc["scope_guard"]["absent_types"] = []
    assert any("group-type-accounted" in f for f in _check_map(doc))


def test_map_all_relation_kinds_identical():
    doc = _map()
    for g in doc["groups"]:
        for e in g["expansions"]:
            e["relation"] = "alt-label"
    assert any("relation-variety" in f for f in _check_map(doc))


def test_map_probe_discovered_without_probe_record():
    doc = _map()
    del doc["probe"]
    assert any("probe-record" in f for f in _check_map(doc))


def test_map_probe_not_performed_needs_reason():
    doc = _map()
    doc["probe"] = {"performed": False}
    for g in doc["groups"]:
        for e in g["expansions"]:
            if e["provenance"] == "probe-discovered":
                e["provenance"] = "model-knowledge"
    assert any("probe-record" in f for f in _check_map(doc))


def test_map_active_source_missing_release():
    doc = _map()
    del doc["sources"]["active"][0]["release"]
    assert any("schema" in f or "source-stamp" in f for f in _check_map(doc))


def test_map_active_source_missing_sanitization():
    doc = _map()
    del doc["sources"]["active"][1]["sanitization"]
    assert any("schema" in f or "source-sanitization" in f for f in _check_map(doc))


def test_map_sanitization_non_clean_status_needs_cause():
    doc = _map()
    doc["sources"]["active"][0]["sanitization"] = {"status": "unavailable"}
    assert any("sanitization-cause" in f for f in _check_map(doc))


def test_map_skipped_source_without_reason():
    doc = _map()
    doc["sources"]["skipped"][0] = {"id": "hacktivity"}
    assert any("schema" in f or "skip-reason" in f for f in _check_map(doc))


def test_map_assumption_without_inferred_from():
    doc = _map()
    del doc["assumptions"][0]["inferred_from"]
    assert any("schema" in f or "assumption-basis" in f for f in _check_map(doc))


def test_map_bad_timestamp():
    doc = _map()
    doc["sources"]["active"][0]["as_of"] = "2026-08-03 10:00"
    assert any("schema" in f or "timestamp" in f for f in _check_map(doc))


def test_map_angle_applicability_missing_an_angle():
    doc = _map()
    doc["angle_applicability"] = doc["angle_applicability"][:-1]
    assert any("angle-verdict-complete" in f for f in _check_map(doc))


# ── search rules ───────────────────────────────────────────────────────────────


def test_search_missing_cell_for_applicable_pair():
    doc = _search()
    doc["coverage"] = doc["coverage"][:-1]
    doc["retrieval_summary"]["status_counts"] = {"reached": 3}
    doc["retrieval_summary"]["degraded_sources"] = []
    assert any("coverage-complete" in f for f in _check_search(doc))


def test_search_extra_cell_outside_applicable_set():
    doc = _search()
    cell = copy.deepcopy(doc["coverage"][0])
    cell["source_id"] = "osv"
    doc["coverage"].append(cell)
    doc["retrieval_summary"]["status_counts"]["reached"] = 4
    assert any("cell-in-applicable-set" in f for f in _check_search(doc))


def test_search_reached_cell_without_counts():
    doc = _search()
    del doc["coverage"][0]["returned"]
    assert any("schema" in f or "reached-counts" in f for f in _check_search(doc))


def test_search_non_reached_cell_without_cause():
    doc = _search()
    del doc["coverage"][3]["cause"]
    assert any("schema" in f or "status-cause" in f for f in _check_search(doc))


def test_search_unreachable_without_fallbacks_tried():
    doc = _search()
    del doc["coverage"][3]["fallbacks_tried"]
    assert any("schema" in f or "fallbacks-tried" in f for f in _check_search(doc))


def test_search_kept_exceeds_returned():
    doc = _search()
    doc["coverage"][0]["kept"] = 99
    assert any("kept-le-returned" in f for f in _check_search(doc))


def test_search_kept_below_returned_without_a_drop():
    doc = _search()
    doc["coverage"][0]["kept"] = 2
    assert any("silent-relevance-cut" in f for f in _check_search(doc))


def test_search_cell_with_no_broad_pass():
    doc = _search()
    doc["coverage"][0]["queries"] = ["CWE-434 in multipart handler on line 42"]
    assert any("broad-pass" in f for f in _check_search(doc))


def test_search_query_not_from_its_group():
    doc = _search()
    doc["coverage"][0]["queries"] = ["completely unrelated subject matter"]
    assert any("query-provenance" in f for f in _check_search(doc))


def test_search_retrieval_summary_disagrees_with_cells():
    doc = _search()
    doc["retrieval_summary"]["degraded_sources"] = []
    assert any("summary-reconciles" in f for f in _check_search(doc))


def test_search_status_counts_wrong():
    doc = _search()
    doc["retrieval_summary"]["status_counts"] = {"reached": 99, "unreachable": 1}
    assert any("status-counts" in f for f in _check_search(doc))


def test_search_candidate_found_by_names_a_nonexistent_cell():
    doc = _search()
    doc["candidates"][0]["found_by"] = [
        {"group_id": "file-upload-weaknesses", "source_id": "attack", "query": "x"}
    ]
    assert any("found-by-resolves" in f for f in _check_search(doc))


def test_search_candidate_found_by_query_not_in_cell():
    doc = _search()
    doc["candidates"][0]["found_by"][0]["query"] = "a query that cell never ran"
    assert any("found-by-query" in f for f in _check_search(doc))


def test_search_candidate_count_exceeds_kept():
    doc = _search()
    extra = copy.deepcopy(doc["candidates"][0])
    extra["id"] = "CWE-999"
    doc["candidates"].append(extra)
    assert any("candidates-reconcile" in f for f in _check_search(doc))


def test_search_non_registry_candidate_without_url():
    doc = _search()
    c = doc["candidates"][0]
    c["id_class"] = "non-registry"
    assert any("schema" in f or "non-registry-fields" in f for f in _check_search(doc))


def test_search_registry_candidate_with_invented_shape():
    doc = _search()
    doc["candidates"][0]["id"] = "a blog post about uploads"
    assert any("registry-id-shape" in f for f in _check_search(doc))


def test_search_control_requirement_id_not_version_pinned():
    doc = _search()
    c = doc["candidates"][0]
    c["id_class"] = "control-requirement"
    c["id"] = "1.2.5"
    assert any("control-id-version-pinned" in f for f in _check_search(doc))


def test_search_signal_without_as_of():
    doc = _search()
    doc["candidates"][0]["signals"] = [{"name": "epss", "value": 0.4, "as_of": "nope"}]
    assert any("schema" in f or "signal-as-of" in f for f in _check_search(doc))


def test_search_dropped_item_without_cell():
    doc = _search()
    doc["bound"]["dropped"] = [{"id": "CWE-1", "ordering_value": "Low"}]
    assert any("schema" in f or "drop-names-cell" in f for f in _check_search(doc))


def test_search_not_run_must_not_carry_coverage():
    doc = _search()
    doc["outcome"] = "not_run"
    doc["not_run"] = {"precondition": "a named package set exists", "cause": "none named"}
    assert any("schema" in f or "not-run-no-coverage" in f for f in _check_search(doc))


def test_search_not_run_is_valid_alone():
    doc = {
        "schema_version": 1,
        "meta": {"angle_id": "b1", "as_of": "2026-08-03T11:00:00Z"},
        "outcome": "not_run",
        "not_run": {
            "precondition": "a named package set exists",
            "cause": "no dependency set named at this stage",
        },
    }
    assert _check_search(doc) == []


def test_search_vacated_is_valid_alone():
    doc = {
        "schema_version": 1,
        "meta": {"angle_id": "b1", "as_of": "2026-08-03T11:00:00Z"},
        "outcome": "vacated",
        "vacated": {
            "empty_factor": "group_types",
            "map_entry": "component type recorded absent: no dependency set named",
        },
    }
    assert _check_search(doc) == []


def test_search_angle_id_unknown_to_registry():
    doc = _search()
    doc["meta"]["angle_id"] = "zz"
    assert any("angle-known" in f for f in _check_search(doc))


@pytest.mark.parametrize("kind", ["keyword-map", "search"])
def test_validator_reports_one_line_per_violation(kind):
    doc = _map() if kind == "keyword-map" else _search()
    if kind == "keyword-map":
        doc["groups"][1]["id"] = doc["groups"][0]["id"]
        doc["scope_guard"]["absent_types"] = []
        out = _check_map(doc)
    else:
        # NOT an unknown angle: that is fatal by design and correctly returns a single line,
        # since nothing downstream is computable without the angle.
        doc["coverage"][0]["kept"] = 99
        doc["retrieval_summary"]["status_counts"] = {"reached": 99}
        out = _check_search(doc)
    assert len(out) >= 2
    assert all(f.startswith("FAIL ") for f in out)
