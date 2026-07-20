# ruff: noqa: D101, D102
"""Tests for validate_prior_art.py — written test-first (test names are the docs).

Run from the package's scripts/ dir or repo root:
    pytest skills/code-prior-art-survey/scripts/test_validate_prior_art.py -q
"""

import copy
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

SCRIPTS = Path(__file__).parent
FIXTURES = SCRIPTS / "fixtures"
KW_FIXTURE = FIXTURES / "keyword-map.valid.yaml"
SEARCH_FIXTURE = FIXTURES / "search-output.valid.yaml"
SEARCH_DEGRADED = FIXTURES / "search-output.degraded.yaml"
EXTRACT_VALID = FIXTURES / "extract-output.valid.md"
EXTRACT_SKIP_IRRELEVANT = FIXTURES / "extract-output.skip-irrelevant.md"
EXTRACT_SKIP_VANISHED = FIXTURES / "extract-output.skip-vanished.md"
EXTRACT_SKIP_UNAVAILABLE = FIXTURES / "extract-output.skip-unavailable.md"
VALIDATOR = SCRIPTS / "validate_prior_art.py"

sys.path.insert(0, str(SCRIPTS))


def _write(tmp_path: Path, doc: dict, name: str = "doc.yaml") -> Path:
    p = tmp_path / name
    p.write_text(yaml.safe_dump(doc, sort_keys=False))
    return p


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text())


# ── keyword-map subcommand (C4) ──────────────────────────────────────────────


class TestKeywordMap:
    def _fails(self, tmp_path, doc):
        from validate_prior_art import validate_keyword_map

        return validate_keyword_map(_write(tmp_path, doc))

    def test_valid_fixture_passes(self, tmp_path):
        from validate_prior_art import validate_keyword_map

        assert validate_keyword_map(KW_FIXTURE) == []

    def test_unquoted_datetime_is_normalized(self, tmp_path):
        doc = _load(KW_FIXTURE)
        raw = yaml.safe_dump(doc, sort_keys=False).replace(
            "'2026-07-17T09:15:00Z'", "2026-07-17T09:15:00Z"
        )
        p = tmp_path / "kw.yaml"
        p.write_text(raw)
        from validate_prior_art import validate_keyword_map

        assert validate_keyword_map(p) == []

    def test_schema_violation_fails(self, tmp_path):
        doc = _load(KW_FIXTURE)
        doc["filters"]["popularity_floor"] = "stars>500"
        fails = self._fails(tmp_path, doc)
        assert any("schema" in f for f in fails)

    def test_expansion_floor_enforced(self, tmp_path):
        doc = _load(KW_FIXTURE)
        doc["groups"][0]["expansions"] = doc["groups"][0]["expansions"][:2]
        assert self._fails(tmp_path, doc)

    def test_expansion_cap_enforced(self, tmp_path):
        doc = _load(KW_FIXTURE)
        base = doc["groups"][0]["expansions"][0]
        doc["groups"][0]["expansions"] = [
            {**base, "term": f"variant {i}"} for i in range(9)
        ]
        assert self._fails(tmp_path, doc)

    def test_duplicate_group_ids_fail(self, tmp_path):
        doc = _load(KW_FIXTURE)
        doc["groups"].append(copy.deepcopy(doc["groups"][0]))
        fails = self._fails(tmp_path, doc)
        assert any("group_id_unique" in f for f in fails)

    def test_duplicate_expansion_terms_fail(self, tmp_path):
        doc = _load(KW_FIXTURE)
        doc["groups"][0]["expansions"][1]["term"] = doc["groups"][0]["expansions"][0][
            "term"
        ]
        fails = self._fails(tmp_path, doc)
        assert any("expansion_term_unique" in f for f in fails)

    def test_delta_requires_extends(self, tmp_path):
        doc = _load(KW_FIXTURE)
        doc["mode"] = "delta"
        doc["lineage"]["extends"] = None
        fails = self._fails(tmp_path, doc)
        assert any("delta_lineage" in f for f in fails)

    def test_probe_skipped_without_reason_fails(self, tmp_path):
        doc = _load(KW_FIXTURE)
        doc["probe"]["performed"] = False
        doc["probe"]["reason"] = None
        assert self._fails(tmp_path, doc)

    def test_excluded_without_reason_fails(self, tmp_path):
        doc = _load(KW_FIXTURE)
        del doc["excluded"][0]["reason"]
        assert self._fails(tmp_path, doc)

    def test_empty_file_fails(self, tmp_path):
        from validate_prior_art import validate_keyword_map

        p = tmp_path / "empty.yaml"
        p.write_text("")
        fails = validate_keyword_map(p)
        assert fails and any("empty" in f for f in fails)

    def test_unknown_active_source_fails(self, tmp_path):
        doc = _load(KW_FIXTURE)
        doc["sources"]["active"].append("libraries.io")
        fails = self._fails(tmp_path, doc)
        assert any("unknown_source" in f and "libraries.io" in f for f in fails)

    def test_missing_file_fails_cleanly(self, tmp_path):
        from validate_prior_art import validate_keyword_map

        fails = validate_keyword_map(tmp_path / "absent.yaml")
        assert fails and any("unreadable" in f for f in fails)

    def test_cli_exit_codes(self, tmp_path):
        ok = subprocess.run(
            [sys.executable, str(VALIDATOR), "keyword-map", str(KW_FIXTURE)],
            capture_output=True,
            text=True,
        )
        assert ok.returncode == 0, ok.stdout + ok.stderr
        doc = _load(KW_FIXTURE)
        doc["version"] = 99
        bad = _write(tmp_path, doc)
        res = subprocess.run(
            [sys.executable, str(VALIDATOR), "keyword-map", str(bad)],
            capture_output=True,
            text=True,
        )
        assert res.returncode == 1
        assert "FAIL " in res.stdout


# ── search subcommand (C6) ───────────────────────────────────────────────────


class TestSearch:
    def _fails(self, tmp_path, doc, kw_doc=None):
        from validate_prior_art import validate_search

        kw = KW_FIXTURE if kw_doc is None else _write(tmp_path, kw_doc, "kw.yaml")
        return validate_search(_write(tmp_path, doc, "search.yaml"), kw)

    def test_valid_fixture_passes(self):
        from validate_prior_art import validate_search

        assert validate_search(SEARCH_FIXTURE, KW_FIXTURE) == []

    def test_degraded_fixture_passes_with_complete_matrix(self):
        """Spec exit criterion 8: unreachable cells keep the matrix COMPLETE."""
        from validate_prior_art import validate_search

        fails = validate_search(SEARCH_DEGRADED, KW_FIXTURE)
        assert fails == []
        assert not any("coverage_missing" in f for f in fails)

    def test_unreachable_cell_passes(self, tmp_path):
        doc = _load(SEARCH_FIXTURE)
        cell = doc["coverage"][0]
        cell["status"] = "unreachable"
        cell["cause"] = "503 Service Unavailable, 3 attempts"
        cell["result_count"] = 0
        assert self._fails(tmp_path, doc) == []

    def test_partial_cell_passes(self, tmp_path):
        doc = _load(SEARCH_FIXTURE)
        cell = doc["coverage"][0]
        cell["status"] = "partial"
        cell["cause"] = "429 after 12 results, 3 attempts"
        assert self._fails(tmp_path, doc) == []

    def test_unreachable_without_cause_fails(self, tmp_path):
        doc = _load(SEARCH_FIXTURE)
        doc["coverage"][0]["status"] = "unreachable"
        doc["coverage"][0]["result_count"] = 0
        assert any("cause" in f for f in self._fails(tmp_path, doc))

    def test_partial_without_cause_fails(self, tmp_path):
        doc = _load(SEARCH_FIXTURE)
        doc["coverage"][0]["status"] = "partial"
        assert any("cause" in f for f in self._fails(tmp_path, doc))

    def test_partial_trivial_cause_fails(self, tmp_path):
        """The SAME threshold as extract — this pins the one-vocabulary constraint."""
        doc = _load(SEARCH_FIXTURE)
        doc["coverage"][0]["status"] = "partial"
        doc["coverage"][0]["cause"] = "nope"
        assert any("cause" in f for f in self._fails(tmp_path, doc))

    def test_unreachable_blank_cause_fails(self, tmp_path):
        doc = _load(SEARCH_FIXTURE)
        doc["coverage"][0]["status"] = "unreachable"
        doc["coverage"][0]["result_count"] = 0
        doc["coverage"][0]["cause"] = "   "
        assert any("cause" in f for f in self._fails(tmp_path, doc))

    def test_unreachable_with_nonzero_count_fails(self, tmp_path):
        doc = _load(SEARCH_FIXTURE)
        cell = doc["coverage"][0]
        cell["status"] = "unreachable"
        cell["cause"] = "503 Service Unavailable, 3 attempts"
        cell["result_count"] = 7
        assert any("unreachable_count" in f for f in self._fails(tmp_path, doc))

    def test_cause_without_failure_status_fails(self, tmp_path):
        doc = _load(SEARCH_FIXTURE)
        doc["coverage"][0]["cause"] = "429 Too Many Requests"
        assert any("cause_without_status" in f for f in self._fails(tmp_path, doc))

    @staticmethod
    def _make_source_unreachable(doc, source):
        """Retype every cell of `source` unreachable and list it in the notes."""
        for cell in doc["coverage"]:
            if cell["source"] == source:
                cell["status"] = "unreachable"
                cell["cause"] = "503 Service Unavailable, 3 attempts"
                cell["result_count"] = 0
        doc["notes"]["unreachable_sources"] = [source]

    def test_fully_unreachable_source_listed_in_notes_passes(self, tmp_path):
        doc = _load(SEARCH_FIXTURE)
        self._make_source_unreachable(doc, "npm")
        assert self._fails(tmp_path, doc) == []

    def test_fully_unreachable_source_absent_from_notes_fails(self, tmp_path):
        doc = _load(SEARCH_FIXTURE)
        self._make_source_unreachable(doc, "npm")
        doc["notes"]["unreachable_sources"] = []
        assert any("unreachable_not_noted" in f for f in self._fails(tmp_path, doc))

    def test_noted_source_still_reachable_fails(self, tmp_path):
        doc = _load(SEARCH_FIXTURE)
        doc["notes"]["unreachable_sources"] = ["npm"]
        assert any("noted_not_unreachable" in f for f in self._fails(tmp_path, doc))

    def test_note_entry_not_a_registry_id_fails(self, tmp_path):
        doc = _load(SEARCH_FIXTURE)
        doc["notes"]["unreachable_sources"] = ["NPM registry (the website)"]
        assert any("unknown_noted_source" in f for f in self._fails(tmp_path, doc))

    def test_partial_source_needs_no_note(self, tmp_path):
        """`partial` means the source WAS reached — listing it would be false."""
        doc = _load(SEARCH_FIXTURE)
        for cell in doc["coverage"]:
            if cell["source"] == "npm":
                cell["status"] = "partial"
                cell["cause"] = "429 after 12 results, 3 attempts"
        assert self._fails(tmp_path, doc) == []

    def test_found_by_names_fully_unreachable_source_fails(self, tmp_path):
        doc = _load(SEARCH_FIXTURE)
        self._make_source_unreachable(doc, "pypi")
        assert any("found_by_unreachable" in f for f in self._fails(tmp_path, doc))

    def test_schema_violation_fails(self, tmp_path):
        doc = _load(SEARCH_FIXTURE)
        doc["coverage"][0]["queries"] = []
        fails = self._fails(tmp_path, doc)
        assert any("schema" in f for f in fails)

    def test_missing_applicable_pair_fails(self, tmp_path):
        doc = _load(SEARCH_FIXTURE)
        doc["coverage"] = [
            c
            for c in doc["coverage"]
            if not (c["group_id"] == "kw-anchor-ccxt" and c["source"] == "deps-dev")
        ]
        fails = self._fails(tmp_path, doc)
        assert any(
            "coverage_missing" in f and "kw-anchor-ccxt" in f and "deps-dev" in f
            for f in fails
        )

    def test_unknown_group_id_in_coverage_fails(self, tmp_path):
        doc = _load(SEARCH_FIXTURE)
        doc["coverage"][0]["group_id"] = "kw-nonexistent"
        fails = self._fails(tmp_path, doc)
        assert any("unknown_group" in f for f in fails)

    def test_unknown_source_in_coverage_fails(self, tmp_path):
        doc = _load(SEARCH_FIXTURE)
        doc["coverage"][0]["source"] = "made-up-source"
        fails = self._fails(tmp_path, doc)
        assert any("unknown_source" in f for f in fails)

    def test_found_by_group_must_exist_in_map(self, tmp_path):
        doc = _load(SEARCH_FIXTURE)
        doc["candidates"][0]["found_by"]["group_ids"] = ["kw-nonexistent"]
        fails = self._fails(tmp_path, doc)
        assert any("unknown_group" in f for f in fails)

    def test_duplicate_candidate_ids_fail(self, tmp_path):
        doc = _load(SEARCH_FIXTURE)
        doc["candidates"].append(copy.deepcopy(doc["candidates"][0]))
        fails = self._fails(tmp_path, doc)
        assert any("candidate_id_unique" in f for f in fails)

    def test_zero_hit_cells_are_valid(self):
        doc = _load(SEARCH_FIXTURE)
        assert any(c["result_count"] == 0 for c in doc["coverage"]), (
            "fixture must carry a zero-hit cell as the worked example"
        )

    def test_project_mismatch_fails(self, tmp_path):
        doc = _load(SEARCH_FIXTURE)
        doc["meta"]["project"] = "some-other-project"
        fails = self._fails(tmp_path, doc)
        assert any("project_mismatch" in f for f in fails)

    def test_found_by_source_must_exist_in_registry(self, tmp_path):
        doc = _load(SEARCH_FIXTURE)
        doc["candidates"][0]["found_by"]["sources"] = ["made-up-source"]
        fails = self._fails(tmp_path, doc)
        assert any("unknown_source" in f for f in fails)

    def test_map_revision_mismatch_fails(self, tmp_path):
        doc = _load(SEARCH_FIXTURE)
        doc["meta"]["keyword_map_revision"] = 7
        fails = self._fails(tmp_path, doc)
        assert any("revision_mismatch" in f for f in fails)

    def test_malformed_map_fails_not_crashes(self, tmp_path):
        from validate_prior_art import validate_search

        bad_map = tmp_path / "badmap.yaml"
        bad_map.write_text("project: x\n")
        fails = validate_search(SEARCH_FIXTURE, bad_map)
        assert fails and any("keyword_map_invalid" in f for f in fails)

    def test_cli_exit_codes(self, tmp_path):
        ok = subprocess.run(
            [
                sys.executable,
                str(VALIDATOR),
                "search",
                str(SEARCH_FIXTURE),
                "--keyword-map",
                str(KW_FIXTURE),
            ],
            capture_output=True,
            text=True,
        )
        assert ok.returncode == 0, ok.stdout + ok.stderr
        res = subprocess.run(
            [sys.executable, str(VALIDATOR), "search", str(SEARCH_FIXTURE)],
            capture_output=True,
            text=True,
        )
        assert res.returncode == 2, "search without --keyword-map is a usage error"


# ── extract subcommand (B4) ──────────────────────────────────────────────────


def _split_md(path: Path):
    _, fm, body = path.read_text().split("---", 2)
    return yaml.safe_load(fm), body


def _write_md(tmp_path: Path, fm: dict, body: str, name: str = "extract.md") -> Path:
    p = tmp_path / name
    p.write_text("---\n" + yaml.safe_dump(fm, sort_keys=False) + "---" + body)
    return p


class TestExtract:
    def _fails(self, tmp_path, fm, body):
        from validate_prior_art import validate_extract

        return validate_extract(_write_md(tmp_path, fm, body))

    def test_valid_full_passes(self):
        from validate_prior_art import validate_extract

        assert validate_extract(EXTRACT_VALID) == []

    def test_skip_irrelevant_with_rationale_passes(self):
        from validate_prior_art import validate_extract

        assert validate_extract(EXTRACT_SKIP_IRRELEVANT) == []

    def test_skip_vanished_passes(self):
        from validate_prior_art import validate_extract

        assert validate_extract(EXTRACT_SKIP_VANISHED) == []

    def test_bad_verdict_enum_fails(self, tmp_path):
        fm, body = _split_md(EXTRACT_VALID)
        fm["verdict"] = "totally-borrow"
        assert any("schema" in f for f in self._fails(tmp_path, fm, body))

    def test_score_out_of_range_fails(self, tmp_path):
        fm, body = _split_md(EXTRACT_VALID)
        fm["score"] = 11
        assert any("schema" in f for f in self._fails(tmp_path, fm, body))

    def test_non_spdx_license_fails(self, tmp_path):
        fm, body = _split_md(EXTRACT_VALID)
        fm["license"] = "some free text license"
        assert any("schema" in f for f in self._fails(tmp_path, fm, body))

    def test_non_purl_dep_fails(self, tmp_path):
        fm, body = _split_md(EXTRACT_VALID)
        fm["key_deps"] = ["pandas"]
        assert any("schema" in f for f in self._fails(tmp_path, fm, body))

    def test_missing_heading_fails(self, tmp_path):
        fm, body = _split_md(EXTRACT_VALID)
        body = body.replace("## Anti-patterns", "## Antipatterns")
        fails = self._fails(tmp_path, fm, body)
        assert any("missing_heading" in f for f in fails)

    def test_irrelevant_skip_missing_rationale_fails(self, tmp_path):
        fm, _ = _split_md(EXTRACT_SKIP_IRRELEVANT)
        del fm["bail_rationale"]
        fails = self._fails(tmp_path, fm, "")
        assert any("bail_rationale" in f for f in fails)

    def test_irrelevant_skip_trivial_rationale_fails(self, tmp_path):
        fm, _ = _split_md(EXTRACT_SKIP_IRRELEVANT)
        fm["bail_rationale"] = "no"
        fails = self._fails(tmp_path, fm, "")
        assert any("bail_rationale" in f for f in fails)

    def test_skip_unavailable_passes(self):
        from validate_prior_art import validate_extract

        assert validate_extract(EXTRACT_SKIP_UNAVAILABLE) == []

    def test_unavailable_skip_missing_cause_fails(self, tmp_path):
        fm, _ = _split_md(EXTRACT_SKIP_UNAVAILABLE)
        fm.pop("cause", None)
        assert any("cause" in f for f in self._fails(tmp_path, fm, ""))

    def test_vanished_skip_missing_cause_fails(self, tmp_path):
        fm, _ = _split_md(EXTRACT_SKIP_VANISHED)
        fm.pop("cause", None)
        assert any("cause" in f for f in self._fails(tmp_path, fm, ""))

    def test_blank_cause_fails(self, tmp_path):
        fm, _ = _split_md(EXTRACT_SKIP_VANISHED)
        fm["reason"] = "unavailable"
        fm["cause"] = "   "
        assert any("cause" in f for f in self._fails(tmp_path, fm, ""))

    def test_bare_status_code_cause_passes(self, tmp_path):
        """A bare "404" is the canonical correct value — the threshold must not reject it."""
        fm, _ = _split_md(EXTRACT_SKIP_VANISHED)
        fm["cause"] = "404"
        assert self._fails(tmp_path, fm, "") == []

    def test_short_wordy_cause_fails(self, tmp_path):
        fm, _ = _split_md(EXTRACT_SKIP_VANISHED)
        fm["cause"] = "nope"
        assert any("cause" in f for f in self._fails(tmp_path, fm, ""))

    def test_irrelevant_skip_needs_no_cause(self, tmp_path):
        fm, _ = _split_md(EXTRACT_SKIP_IRRELEVANT)
        fm.pop("cause", None)
        assert self._fails(tmp_path, fm, "") == []

    def test_bad_reason_enum_fails(self, tmp_path):
        fm, _ = _split_md(EXTRACT_SKIP_VANISHED)
        fm["reason"] = "whatever"
        assert any("schema" in f for f in self._fails(tmp_path, fm, ""))

    def test_no_frontmatter_fails(self, tmp_path):
        from validate_prior_art import validate_extract

        p = tmp_path / "bare.md"
        p.write_text("# just a heading\n")
        fails = validate_extract(p)
        assert fails and any("no_frontmatter" in f for f in fails)

    def test_missing_file_fails_cleanly(self, tmp_path):
        from validate_prior_art import validate_extract

        fails = validate_extract(tmp_path / "absent.md")
        assert fails and any("unreadable" in f for f in fails)

    def test_cli_extract_exit_codes(self, tmp_path):
        ok = subprocess.run(
            [sys.executable, str(VALIDATOR), "extract", str(EXTRACT_VALID)],
            capture_output=True,
            text=True,
        )
        assert ok.returncode == 0, ok.stdout + ok.stderr
        fm, body = _split_md(EXTRACT_VALID)
        fm["score"] = 99
        bad = _write_md(tmp_path, fm, body)
        res = subprocess.run(
            [sys.executable, str(VALIDATOR), "extract", str(bad)],
            capture_output=True,
            text=True,
        )
        assert res.returncode == 1
        assert "FAIL " in res.stdout


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
