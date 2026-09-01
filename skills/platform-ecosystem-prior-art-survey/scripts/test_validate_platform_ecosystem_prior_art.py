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


class TestPlatformSlugDiscipline:
    """The record id is <platform_slug>__<angle_id>, so a slug minted by an angle rather than by
    the wave-0 map produces two rows for one platform and the dedupe never fires."""

    def test_a_slug_absent_from_the_map_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["platform_slug"] = "notion"
        assert "slug-not-in-map" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_slug_present_in_the_map_passes(self, valid_search, valid_map, registry):
        """MIRROR: every shipped slug must pass, or the rule is unusable."""
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["platform_slug"] = "shopify"
        assert V.validate_search(doc, valid_map, registry) == []

    def test_a_malformed_slug_fails_at_the_schema(
        self, valid_search, valid_map, registry
    ):
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["platform_slug"] = "VS_Code"
        assert "schema" in _rules(V.validate_search(doc, valid_map, registry))[0]


class TestSourceIdResolves:
    def test_a_candidate_citing_an_unknown_source_fails(
        self, valid_search, valid_map, registry
    ):
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["source_id"] = "no-such-source"
        assert "source-not-in-registry" in _rules(
            V.validate_search(doc, valid_map, registry)
        )

    def test_a_cell_citing_an_unknown_source_fails(
        self, valid_search, valid_map, registry
    ):
        """MIRROR: cells and candidates both cite sources, and a rule covering only one of them
        leaves the other free to invent a source."""
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0]["source_id"] = "no-such-source"
        assert "source-not-in-registry" in _rules(
            V.validate_search(doc, valid_map, registry)
        )


class TestEnumerationFrame:
    """A count is meaningless without its frame: one enumerable set yielded six defensible counts
    in a day, differing only by which question they answered."""

    def test_an_a3_candidate_without_a_locator_fails(
        self, valid_search, valid_map, registry
    ):
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["locator"] = None
        assert "enumeration-needs-locator" in _rules(
            V.validate_search(doc, valid_map, registry)
        )

    def test_a_non_a3_candidate_without_a_locator_passes(
        self, valid_search, valid_map, registry
    ):
        """MIRROR: the rule is a3's, not every angle's — a commercial-term candidate has no
        enumerable set to locate."""
        doc = copy.deepcopy(valid_search)
        doc["meta"]["angle_id"] = "a2"
        for c in doc["candidates"]:
            c["locator"] = None
            c["enumeration"] = None
        assert V.validate_search(doc, valid_map, registry) == []

    def test_an_enumeration_without_a_second_derivation_fails_at_the_schema(
        self, valid_search, valid_map, registry
    ):
        doc = copy.deepcopy(valid_search)
        del doc["candidates"][0]["enumeration"]["reconciled_by"]
        assert "schema" in _rules(V.validate_search(doc, valid_map, registry))[0]


class TestRecordFilename:
    """#42, BOTH parts. Mirroring 5c and never 5e, which ships a known collision."""

    def test_a_filename_safe_id_is_identity(self):
        assert V.record_filename("vscode__a3") == "vscode__a3"

    def test_an_id_with_a_slash_is_hashed(self):
        out = V.record_filename("https://example.com/docs/a")
        assert "/" not in out
        assert V._HASHED_STEM.search(out), out

    def test_two_ids_differing_only_in_collapsed_characters_differ(self):
        """The digest covers the WHOLE id, so ids the sanitizer would flatten together stay
        distinct. A non-injective mapping merges two records into one filename, and because the
        extract cursor is disk-authoritative the orphaned row is re-spawned on every wake while
        looking perfectly valid."""
        assert V.record_filename("a/b") != V.record_filename("a:b")

    def test_the_identity_branch_REFUSES_an_already_hashed_stem(self):
        """PART (b), the half a sibling omitted and which genuinely collides there."""
        looks_hashed = "something--0123456789ab"
        assert V.record_filename(looks_hashed) != looks_hashed

    def test_cross_branch_collision_is_impossible(self):
        """The test that matters. A within-branch round-trip passes while f(f(x)) == f(x) != x is
        still constructible — so the cross-branch case is the one that proves injectivity."""
        raw = "https://example.com/docs/a"
        once = V.record_filename(raw)
        twice = V.record_filename(once)
        assert once != twice, (
            "f(f(x)) == f(x): the two branches share an output namespace"
        )
        assert twice != raw

    def test_a_long_id_is_capped_but_still_distinct(self):
        a = V.record_filename("https://example.com/" + "x" * 200 + "/one")
        b = V.record_filename("https://example.com/" + "x" * 200 + "/two")
        assert a != b, (
            "the cap truncated the prefix but the digest must still separate them"
        )


class TestEverySubcommandIsReachable:
    """#51 — the rule that exists because a sibling shipped two subparsers `main()` never routed.

    Both survived a 117-test suite because every test called the `validate_*` functions directly,
    so the dispatch itself had NEVER run. These tests go through `main()` only, and the command
    list is DERIVED from the parser so a third subcommand added later cannot escape them.
    """

    def test_the_registered_set_is_what_wave_1_declares(self):
        assert V.registered_subcommands() == {"keyword-map", "search"}

    def test_every_registered_subcommand_routes_without_raising(
        self, tmp_path, valid_map, valid_search
    ):
        """Each one reached through main(), with an artifact valid FOR THAT COMMAND."""
        m = tmp_path / "map.yaml"
        m.write_text(yaml.safe_dump(valid_map))
        s = tmp_path / "search.yaml"
        s.write_text(yaml.safe_dump(valid_search))
        argv = {
            "keyword-map": ["keyword-map", str(m)],
            "search": ["search", str(s), "--keyword-map", str(m)],
        }
        for cmd in sorted(V.registered_subcommands()):
            assert cmd in argv, (
                f"{cmd!r} is registered but this test has no invocation for it"
            )
            assert V.main(argv[cmd]) == 0, (
                f"{cmd!r} did not route cleanly through main()"
            )

    def test_search_does_not_FALL_THROUGH_to_the_map_branch(
        self, tmp_path, valid_map, valid_search
    ):
        """The sibling's actual defect. A search output is not a valid vocabulary map, so if
        `search` were routed to the map validator it would emit map-schema findings instead of
        passing — which is exactly how the fall-through hid."""
        m = tmp_path / "map.yaml"
        m.write_text(yaml.safe_dump(valid_map))
        s = tmp_path / "search.yaml"
        s.write_text(yaml.safe_dump(valid_search))
        assert V.main(["search", str(s), "--keyword-map", str(m)]) == 0
        # and the converse: the search artifact IS rejected by the map command, proving the two
        # branches are genuinely different code paths rather than one aliased to the other.
        assert V.main(["keyword-map", str(s)]) == 1

    def test_the_map_command_does_not_require_the_search_flag(
        self, tmp_path, valid_map
    ):
        """A shared-parser mistake would make --keyword-map required everywhere."""
        m = tmp_path / "map.yaml"
        m.write_text(yaml.safe_dump(valid_map))
        assert V.main(["keyword-map", str(m)]) == 0

    def test_an_unregistered_subcommand_is_refused(self, tmp_path):
        with pytest.raises(SystemExit):
            V.main(["synthesis", str(tmp_path / "x.yaml")])


class TestTheRootGuardActuallyRuns:
    """EC7 — the producer MUST export REQUIRED_CAPABILITY_FIELDS, because without it the root
    guard SKIPS this package and a silent skip is a green test checking nothing."""

    def test_the_constant_is_exported_at_module_level(self):
        assert isinstance(V.REQUIRED_CAPABILITY_FIELDS, tuple)
        assert len(V.REQUIRED_CAPABILITY_FIELDS) >= 14

    def test_the_constant_is_defined_exactly_once(self):
        """A sibling shipped TWO definitions, the stale one shadowing the correct one, and no
        ruff rule flags a module-level redefinition — F811 included."""
        src = SCRIPT.read_text()
        assert src.count("\nREQUIRED_CAPABILITY_FIELDS = (") == 1
