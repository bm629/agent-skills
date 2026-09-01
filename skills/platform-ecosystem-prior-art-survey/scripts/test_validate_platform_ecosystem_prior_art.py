"""Tests for the platform-ecosystem prior-art deterministic gate (wave 1).

Every test mutates a deep copy of a valid fixture IN-PROCESS. Never revert a planted defect with
a VCS checkout — that discards uncommitted work alongside it.

The gate checks SHAPE only. A test asserting the validator caught a SEMANTIC error would be
testing the wrong layer; those belong to the reviewing skill's numbered conditions.

Each comparison here ships its MIRROR (#34). The shipped `candidates > kept` check in a sibling
had only the direction that essentially never fires, while the direction that parked three
tickets was absent — a one-directional check on a two-directional property reads as covered and
is not.
"""

from __future__ import annotations

import copy
import subprocess
import sys
from pathlib import Path

import pytest
import validate_platform_ecosystem_prior_art as V
import yaml

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"
SCRIPT = HERE / "validate_platform_ecosystem_prior_art.py"


@pytest.fixture
def valid_map() -> dict:
    return yaml.safe_load((FIXTURES / "platform-vocabulary-map.valid.yaml").read_text())


@pytest.fixture
def valid_search() -> dict:
    return yaml.safe_load((FIXTURES / "search-output.valid.yaml").read_text())


@pytest.fixture
def registry() -> dict:
    return V.load_registry()


def _rules(findings: list[str]) -> list[str]:
    return [f.split(":", 1)[0].replace("FAIL ", "") for f in findings]


class TestFailureFormat:
    """The only thing that makes a failure observable (§19). A caller greps this line."""

    def test_a_finding_is_literally_FAIL_rule_colon_message(self):
        out = V._fail("some-rule", "the message")
        assert out.startswith("FAIL some-rule: "), out
        assert out.endswith("the message")

    def test_the_rule_id_contains_no_spaces(self):
        """A rule id with a space cannot be grepped as a token, which is the whole point."""
        assert " " not in V._fail("x-y", "m").split(":")[0].replace("FAIL ", "")


class TestShippedFixturesAreClean:
    def test_the_shipped_map_passes(self, valid_map, registry):
        assert V.validate_keyword_map(valid_map, registry) == []

    def test_the_shipped_search_passes(self, valid_search, valid_map, registry):
        assert V.validate_search(valid_search, valid_map, registry) == []


class TestSchemaConformance:
    def test_a_missing_required_top_level_key_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        del doc["platforms"]
        assert "schema" in _rules(V.validate_keyword_map(doc, registry))[0]

    def test_an_unknown_top_level_key_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["extra_thing"] = 1
        assert "schema" in _rules(V.validate_keyword_map(doc, registry))[0]

    def test_a_bad_enum_value_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["platforms"][0]["platform_type"] = "none"
        assert "schema" in _rules(V.validate_keyword_map(doc, registry))[0]


class TestRevisionMonotonic:
    def test_revision_below_one_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["meta"]["revision"] = 0
        assert V.validate_keyword_map(doc, registry)

    def test_revision_one_passes(self, valid_map, registry):
        """MIRROR: the floor is legal, so the rule cannot be 'any revision is suspicious'."""
        doc = copy.deepcopy(valid_map)
        doc["meta"]["revision"] = 1
        assert V.validate_keyword_map(doc, registry) == []


class TestTimestampFormat:
    def test_a_non_iso_retrieved_at_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["meta"]["retrieved_at"] = "yesterday"
        assert V.validate_keyword_map(doc, registry)

    def test_a_bare_date_passes(self, valid_map, registry):
        """MIRROR: many sources state a date and no time; rejecting that would be wrong."""
        doc = copy.deepcopy(valid_map)
        doc["meta"]["retrieved_at"] = "2026-09-01"
        assert V.validate_keyword_map(doc, registry) == []


class TestApplicabilityVerdicts:
    def test_a_verdict_for_an_unknown_angle_fails(self, valid_map, registry):
        """`a9` is WELL-FORMED but unregistered. An earlier version of this test used `z9`, which
        the schema pattern rejects first — so it exercised the schema layer and never reached the
        rule it claimed to test. A test that passes for the wrong reason is worse than no test."""
        doc = copy.deepcopy(valid_map)
        doc["angle_applicability"][0]["angle_id"] = "a9"
        assert "applicability-angle-unknown" in _rules(
            V.validate_keyword_map(doc, registry)
        )

    def test_a_missing_verdict_fails(self, valid_map, registry):
        """MIRROR of the above: a wrong verdict and an ABSENT one are both defects, and the
        absent one is the direction that hides an unexamined angle."""
        doc = copy.deepcopy(valid_map)
        doc["angle_applicability"] = [
            a for a in doc["angle_applicability"] if a["angle_id"] != "b2"
        ]
        assert "applicability-incomplete" in _rules(
            V.validate_keyword_map(doc, registry)
        )

    def test_a_verdict_with_an_empty_reason_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["angle_applicability"][0]["reason"] = "   "
        assert V.validate_keyword_map(doc, registry)


class TestZeroHitCell:
    """#20 — a recorded zero proves the search RAN. Absence of a cell proves nothing."""

    def test_a_reached_cell_without_returned_fails(
        self, valid_search, valid_map, registry
    ):
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0]["returned"] = None
        assert "coverage-reached-needs-count" in _rules(
            V.validate_search(doc, valid_map, registry)
        )

    def test_a_reached_cell_with_zero_returned_PASSES(
        self, valid_search, valid_map, registry
    ):
        """MIRROR, and the load-bearing one: a recorded ZERO is the evidence, not a defect.
        A validator that rejected it would push producers toward omitting the cell instead."""
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0]["returned"] = 0
        doc["coverage"][0]["kept"] = 0
        doc["retrieval_summary"]["status_counts"] = {"reached": 3, "superseded": 1}
        assert V.validate_search(doc, valid_map, registry) == []

    def test_a_non_reached_cell_with_a_count_fails(
        self, valid_search, valid_map, registry
    ):
        """A count on an unreached cell is a zero laundered out of a failure."""
        doc = copy.deepcopy(valid_search)
        cell = next(c for c in doc["coverage"] if c["status"] == "superseded")
        cell["returned"] = 0
        assert "coverage-unreached-has-count" in _rules(
            V.validate_search(doc, valid_map, registry)
        )

    def test_a_non_reached_cell_without_a_cause_fails(
        self, valid_search, valid_map, registry
    ):
        doc = copy.deepcopy(valid_search)
        next(c for c in doc["coverage"] if c["status"] == "superseded")["cause"] = None
        assert "coverage-cause-required" in _rules(
            V.validate_search(doc, valid_map, registry)
        )

    def test_a_cell_with_no_queries_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0]["queries"] = []
        assert V.validate_search(doc, valid_map, registry)


class TestKeptVersusReturned:
    def test_kept_above_returned_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0]["kept"] = 999
        assert "kept-exceeds-returned" in _rules(
            V.validate_search(doc, valid_map, registry)
        )

    def test_kept_equal_to_returned_passes(self, valid_search, valid_map, registry):
        """MIRROR: equality is the common case and must not be flagged."""
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0]["kept"] = doc["coverage"][0]["returned"]
        assert V.validate_search(doc, valid_map, registry) == []


class TestRetrievalSummaryReconciles:
    """The summary duplicates the cells DELIBERATELY: a discrepancy is the signal that a failure
    was laundered into a zero."""

    def test_a_summary_disagreeing_with_the_cells_fails(
        self, valid_search, valid_map, registry
    ):
        doc = copy.deepcopy(valid_search)
        doc["retrieval_summary"]["status_counts"]["reached"] = 99
        assert "summary-mismatch" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_summary_agreeing_passes(self, valid_search, valid_map, registry):
        assert V.validate_search(valid_search, valid_map, registry) == []


class TestBoundOrdering:
    """#40 — a cap that BOUND must record the ordering it truncated by."""

    def test_bound_true_without_ordering_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["bound"] = {"cap": 14, "bound": True}
        assert "bound-needs-ordering" in _rules(
            V.validate_search(doc, valid_map, registry)
        )

    def test_bound_false_without_ordering_passes(
        self, valid_search, valid_map, registry
    ):
        """MIRROR: an unbound cap owes no ordering, so the rule must not fire on every angle."""
        doc = copy.deepcopy(valid_search)
        doc["bound"] = {"cap": 14, "bound": False}
        assert V.validate_search(doc, valid_map, registry) == []


class TestUnrunAngleOwesNoCells:
    def test_not_run_with_coverage_cells_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["outcome"] = "not_run"
        assert "not-run-owes-no-cells" in _rules(
            V.validate_search(doc, valid_map, registry)
        )

    def test_ran_with_no_cells_fails(self, valid_search, valid_map, registry):
        """MIRROR: the opposite direction — a ran angle with no cells is an unexplained gap."""
        doc = copy.deepcopy(valid_search)
        doc["coverage"] = []
        assert "ran-needs-cells" in _rules(V.validate_search(doc, valid_map, registry))


class TestRegistrySelfCheck:
    """The registry ships INSIDE this package, so a defect in it is a package fault rather than a
    fault in the artifact under test — exit 2, and before any subcommand reads its input."""

    def test_the_shipped_registry_is_clean(self, registry):
        assert V.anchor_failures(registry) == []

    def test_an_anchor_on_an_optional_field_fails(self, registry):
        reg = copy.deepcopy(registry)
        next(a for a in reg["angles"] if a["id"] == "b1")["trigger_anchor"] = [
            "business.model"
        ]
        assert "anchor-must-be-required" in _rules(V.anchor_failures(reg))

    def test_an_anchor_on_a_required_field_outside_the_stale_list_passes(
        self, registry
    ):
        """MIRROR, and the direction that actually broke in a sibling: every one of that type's
        anchors happened to sit in a stale 5-entry list, so its clean run proved nothing."""
        reg = copy.deepcopy(registry)
        next(a for a in reg["angles"] if a["id"] == "b1")["trigger_anchor"] = [
            "scale.concurrency"
        ]
        assert V.anchor_failures(reg) == []

    def test_a_conditional_angle_without_an_anchor_fails(self, registry):
        reg = copy.deepcopy(registry)
        del next(a for a in reg["angles"] if a["id"] == "b1")["trigger_anchor"]
        assert "anchor-required" in _rules(V.anchor_failures(reg))

    def test_an_always_on_angle_declaring_an_anchor_fails(self, registry):
        reg = copy.deepcopy(registry)
        next(a for a in reg["angles"] if a["id"] == "a1")["trigger_anchor"] = [
            "ui.has_ui"
        ]
        assert "anchor-only-on-conditional" in _rules(V.anchor_failures(reg))

    def test_the_constant_covers_every_required_classification_leaf(self):
        """A sibling shipped TWO definitions of this tuple, the stale one shadowing the correct
        one, and no ruff rule flags a module-level redefinition."""
        for leaf in (
            "regulatory.applies",
            "scale.concurrency",
            "integrations.expected",
            "data_ml.ml_involvement",
            "business.platform.type",
        ):
            assert leaf in V.REQUIRED_CAPABILITY_FIELDS, leaf


class TestExitContract:
    """0 clean, 1 the artifact has findings, 2 it could not be used at all. The 2 class exists so
    a package fault never sends an author off to edit a map that is fine."""

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            capture_output=True,
            text=True,
            cwd=HERE,
            check=False,  # a non-zero exit is the thing under test
        )

    def test_a_clean_map_exits_0(self):
        r = self._run(
            "keyword-map", str(FIXTURES / "platform-vocabulary-map.valid.yaml")
        )
        assert r.returncode == 0, r.stdout + r.stderr

    def test_a_defective_artifact_exits_1(self, valid_map, tmp_path):
        doc = copy.deepcopy(valid_map)
        doc["angle_applicability"][0]["angle_id"] = "z9"
        p = tmp_path / "bad.yaml"
        p.write_text(yaml.safe_dump(doc))
        r = self._run("keyword-map", str(p))
        assert r.returncode == 1, r.stdout + r.stderr
        assert "FAIL " in r.stdout

    def test_a_missing_file_exits_2(self, tmp_path):
        r = self._run("keyword-map", str(tmp_path / "nope.yaml"))
        assert r.returncode == 2, r.stdout + r.stderr

    def test_a_malformed_registry_exits_2_from_every_subcommand(
        self, monkeypatch, valid_map, tmp_path
    ):
        """The third exit-2 case, and the one the class exists for: a PACKAGE fault must never be
        reported as a fault in the artifact, or a caller goes off to edit a map that is fine.
        Asserted on BOTH subcommands, because a check that runs on one path only is the defect
        `main()` orders the registry check first to avoid."""
        broken = copy.deepcopy(V.load_registry())
        next(a for a in broken["angles"] if a["id"] == "b1")["trigger_anchor"] = [
            "business.model"
        ]
        monkeypatch.setattr(V, "load_registry", lambda *a, **k: broken)
        good = tmp_path / "map.yaml"
        good.write_text(yaml.safe_dump(valid_map))
        assert V.main(["keyword-map", str(good)]) == 2
        assert V.main(["search", str(good), "--keyword-map", str(good)]) == 2

    def test_unparseable_yaml_exits_2(self, tmp_path):
        p = tmp_path / "bad.yaml"
        p.write_text("key: [unclosed\n")
        r = self._run("keyword-map", str(p))
        assert r.returncode == 2, r.stdout + r.stderr
