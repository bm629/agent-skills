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

import collections
import copy
import re
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
        """MIRROR: the floor is legal, so the rule cannot be 'any revision is suspicious'.

        Asserted by RAISING the fixture and coming back down, because the fixture already carries
        revision 1 — setting it to 1 mutated nothing and made this a second copy of
        `test_the_shipped_map_passes` under a name that promised more.
        """
        doc = copy.deepcopy(valid_map)
        doc["meta"]["revision"] = 7
        assert V.validate_keyword_map(doc, registry) == []
        doc["meta"]["revision"] = 1
        assert V.validate_keyword_map(doc, registry) == []


class TestTimestampFormat:
    """The SCHEMA owns this, and a hand-written rule duplicating it was unreachable.

    `_ISO_PREFIX` was a strict superset of the schema's own `pattern`, so schema-valid implied
    regex-match and the rule could never fire — while its test asserted only truthiness and so
    passed on the schema finding, naming a rule it never exercised. One owner per property (#56);
    the rule is gone and this asserts the owner that remains.
    """

    @pytest.mark.parametrize(
        "bad", ["yesterday", "", "20260901", "2026-9-1", None, 20260901]
    )
    def test_a_non_iso_retrieved_at_is_the_SCHEMAS_job(self, bad, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["meta"]["retrieved_at"] = bad
        assert "schema" in _rules(V.validate_keyword_map(doc, registry)), bad

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
        # kept counts ROWS, so zeroing it means dropping the row it counted.
        doc["candidates"] = [
            c for c in doc["candidates"] if c["source_id"] != doc["coverage"][0]["source_id"]
        ]
        # Derived, not written down: this mutation changes a COUNT, not a STATUS, so the summary
        # is unaffected. A literal here would break on every fixture edit and train the next
        # reader to patch the number rather than ask whether the property still holds.
        doc["retrieval_summary"]["status_counts"] = collections.Counter(
            c["status"] for c in doc["coverage"]
        )
        assert V.validate_search(doc, valid_map, registry) == []

    def test_a_non_reached_cell_with_a_count_fails(
        self, valid_search, valid_map, registry
    ):
        """A count on an unreached cell is a zero laundered out of a failure.

        The non-reached cell is CONSTRUCTED, not selected out of the fixture: the rule is what is
        under test, and a test that needs the fixture to contain a particular status breaks when
        the fixture is corrected for an unrelated reason — which is exactly what happened when the
        one `superseded` cell turned out to describe a redirect that never occurred.
        """
        doc = copy.deepcopy(valid_search)
        cell = doc["coverage"][0]
        cell.update(status="unreachable", cause="HTTP 503 from the origin", returned=0, kept=None)
        assert "coverage-unreached-has-count" in _rules(
            V.validate_search(doc, valid_map, registry)
        )

    def test_a_non_reached_cell_without_a_cause_fails(
        self, valid_search, valid_map, registry
    ):
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0].update(status="unreachable", cause=None, returned=None, kept=None)
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
        """MIRROR: equality is the common case and must not be flagged.

        Both values are MOVED, not copied from each other: the fixture's first cell was already
        38/38, so assigning returned to kept changed nothing and this asserted the unmutated
        fixture.
        """
        doc = copy.deepcopy(valid_search)
        # kept counts candidate ROWS, so equality with `returned` means one item, one row.
        doc["coverage"][0]["returned"] = 1
        doc["coverage"][0]["kept"] = 1
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
        """Rebuilt from the cells rather than asserting the untouched fixture, which is what this
        did before — a duplicate of `test_the_shipped_search_passes` under another name."""
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0]["status"] = "unreachable"
        doc["coverage"][0].update(returned=None, kept=None, cause="HTTP 503 from the origin")
        doc["candidates"] = [
            c for c in doc["candidates"] if c["source_id"] != doc["coverage"][0]["source_id"]
        ]
        doc["retrieval_summary"]["status_counts"] = collections.Counter(
            c["status"] for c in doc["coverage"]
        )
        assert V.validate_search(doc, valid_map, registry) == []

    def test_a_declared_ZERO_in_the_summary_is_not_a_mismatch(
        self, valid_search, valid_map, registry
    ):
        """"We had no unreachable cells" is a reasonable thing to write down, and comparing raw
        dicts rejected it. A zero carries nothing the cells do not already say."""
        doc = copy.deepcopy(valid_search)
        doc["retrieval_summary"]["status_counts"] = {
            **collections.Counter(c["status"] for c in doc["coverage"]),
            "unreachable": 0,
        }
        assert V.validate_search(doc, valid_map, registry) == []


class TestBoundOrdering:
    """#40 — a cap that was HIT must record the ordering it truncated by, and what fell out.

    The flag is `hit`, not `bound`: all three sibling types spell it `hit`, and this type shipped
    its own spelling for the same concept, which is the drift #32 exists to stop.
    """

    def test_an_absent_ordering_is_caught_by_the_SCHEMA(self, valid_search, valid_map, registry):
        """Two layers, two rules, deliberately. `ordering` is schema-required, so its ABSENCE is a
        shape failure — the rule below owns the case the schema cannot see."""
        doc = copy.deepcopy(valid_search)
        doc["bound"] = {"cap": 14, "hit": True, "dropped_note": "two lower-completeness rows"}
        assert "schema" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_BLANK_ordering_is_caught_by_the_RULE(self, valid_search, valid_map, registry):
        """The one the schema lets through: `minLength: 1` is satisfied by a space. Whitespace is
        how a required string gets silenced without anything noticing."""
        doc = copy.deepcopy(valid_search)
        doc["bound"] = {
            "cap": 14,
            "hit": True,
            "ordering": "   ",
            "dropped_note": "two lower-completeness rows",
        }
        assert "bound-needs-ordering" in _rules(
            V.validate_search(doc, valid_map, registry)
        )

    def test_hit_without_a_dropped_note_fails(self, valid_search, valid_map, registry):
        """With no note the ordering is the ONLY evidence a truncation leaves, and a reader
        cannot tell a cap that dropped one near-miss from one that dropped half the corpus."""
        doc = copy.deepcopy(valid_search)
        doc["bound"] = {"cap": 14, "hit": True, "ordering": "vendor-published first"}
        assert "bound-needs-dropped-note" in _rules(
            V.validate_search(doc, valid_map, registry)
        )

    def test_not_hit_owes_neither(self, valid_search, valid_map, registry):
        """MIRROR: an unbound cap owes neither, so neither rule fires on every angle. `hit: false`
        is the STRONGER claim — every admissible candidate is present."""
        doc = copy.deepcopy(valid_search)
        doc["bound"] = {"cap": 14, "hit": False, "ordering": "vendor-published first"}
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
        assert len(V.REQUIRED_CAPABILITY_FIELDS) == len(set(V.REQUIRED_CAPABILITY_FIELDS))
        # Every leaf, not a hand-picked five — a subset check passes on a list missing ten of
        # them, which is exactly the staleness this test names.
        assert set(V.REQUIRED_CAPABILITY_FIELDS) == {
            "archetype.primary",
            "domain.audience",
            "regulatory.applies",
            "scale.concurrency",
            "scale.real_time",
            "scale.availability_target",
            "scale.geo_distribution",
            "scale.data_volume",
            "integrations.expected",
            "integrations.complexity",
            "ui.has_ui",
            "ui.complexity",
            "data_ml.ml_involvement",
            "business.platform",
            "business.platform.type",
        }


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
        a2 = next(a for a in registry["angles"] if a["id"] == "a2")
        doc["meta"]["angle_id"] = "a2"
        # Everything angle-scoped travels with the angle: the cap AND the source list. Derived,
        # not written down — a literal is a second place for a2's facts to live, and moving the
        # angle while leaving a3's coverage behind is the defect the new rules exist to catch.
        doc["bound"]["cap"] = a2["cap"]
        doc["coverage"] = [
            {
                "source_id": sid,
                "queries": [f"site:{sid} program policy"],
                "status": "reached",
                "returned": 1,
                "kept": 1 if sid == a2["sources"][0] else 0,
                "cause": None,
                "fallback_used": None,
            }
            for sid in a2["sources"]
        ]
        doc["retrieval_summary"]["status_counts"] = collections.Counter(
            c["status"] for c in doc["coverage"]
        )
        doc["retrieval_summary"]["degraded_sources"] = []
        doc["candidates"] = [
            {
                **copy.deepcopy(doc["candidates"][0]),
                "source_id": a2["sources"][0],
                "locator": None,
                "enumeration": None,
            }
        ]
        doc["unadmitted"] = [
            {
                "item": "the rest",
                "found_by": a2["sources"][1],
                "reason": "nothing admissible on this pass",
            }
        ]
        # kept counts candidates PLUS unadmitted rows naming the cell, so the row just added
        # moves its source's arithmetic with it.
        for cell in doc["coverage"]:
            cell["kept"] = sum(
                1 for c in doc["candidates"] if c["source_id"] == cell["source_id"]
            ) + sum(1 for u in doc["unadmitted"] if u["found_by"] == cell["source_id"])
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
        """Two assertions, because the name makes two promises. `a != b` alone holds for ANY cap
        value — it exercises the digest and says nothing about truncation, so changing
        `_PREFIX_CAP` from 80 to 4 left it green."""
        a = V.record_filename("https://example.com/" + "x" * 200 + "/one")
        b = V.record_filename("https://example.com/" + "x" * 200 + "/two")
        assert a != b, "the digest must still separate them"
        prefix = a.rsplit("--", 1)[0]
        assert len(prefix) == V._PREFIX_CAP, (len(prefix), V._PREFIX_CAP)

    def test_an_id_with_no_usable_characters_still_yields_a_filename(self):
        """The empty-prefix fallback was reachable and unexercised: deleting it left the suite
        green. A record whose id sanitises to nothing still needs somewhere to be written."""
        name = V.record_filename("///")
        assert name.startswith("--")
        assert name != V.record_filename("...")


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


ANGLES_DIR = HERE.parent / "references" / "angles"


class TestAngleReferenceContract:
    """C3 — the angle-to-registry contract, asserted in BOTH directions (#34).

    A one-directional check reads as covered and is not: checking only that briefs cite real
    sources lets an orphan source sit shipped and unused, and checking only that every source is
    used lets a brief cite one that does not exist.
    """

    def _brief(self, angle_id: str) -> str:
        return (ANGLES_DIR / f"{angle_id}.md").read_text()

    def test_one_brief_per_registered_angle(self, registry):
        on_disk = {p.stem for p in ANGLES_DIR.glob("*.md")}
        assert on_disk == {a["id"] for a in registry["angles"]}

    def _declared_in_brief(self, angle_id: str) -> set[str]:
        """The ids in the brief's HEADER BLOCK — everything before the first `##`.

        Read as a block rather than line by line: a Sources list of eleven ids wraps, and a
        line-based parser silently drops the continuation, which reads as drift that is not there.
        """
        head = self._brief(angle_id).split("\n## ", 1)[0]
        return set(re.findall(r"`([a-z0-9]+(?:-[a-z0-9]+)+)`", head))

    def test_every_source_a_brief_names_exists_in_the_registry(self, registry):
        """An earlier version of this test filtered candidate ids through a set that was EMPTY,
        so it could never fail. It is now derived from the brief's own Sources line and checked
        against the registry — a test that cannot fail is worse than no test, because it reports
        coverage it does not have."""
        known = {s["id"] for s in registry["sources"]}
        for angle in registry["angles"]:
            cited = self._declared_in_brief(angle["id"])
            assert cited, f"{angle['id']}: brief names no sources at all"
            unknown = cited - known
            assert not unknown, (
                f"{angle['id']}: cites unknown source(s) {sorted(unknown)}"
            )

    def test_each_brief_names_exactly_the_sources_the_registry_gives_it(self, registry):
        """The tightest form: brief and registry must agree, not merely overlap. Drift either way
        means an angle is documented to read something it will not, or reads something undocumented."""
        for angle in registry["angles"]:
            # Parenthesised deliberately: `-` binds tighter than `|`, so the unbracketed form
            # was correct by accident and read as a precedence bug — the kind a later editor
            # "fixes" INTO one.
            expected = set(angle.get("sources") or []) | ({angle.get("fallback")} - {None})
            assert self._declared_in_brief(angle["id"]) == expected, angle["id"]

    def test_every_registry_source_is_reachable_from_some_angle(self, registry):
        """The MIRROR. An orphan source is a row nobody can reach — shipped, verified, and dead."""
        known = {s["id"] for s in registry["sources"]}
        reachable = set()
        for angle in registry["angles"]:
            reachable |= set(angle.get("sources") or [])
            if angle.get("fallback"):
                reachable.add(angle["fallback"])
        for src in registry["sources"]:
            if src.get("fallback"):
                reachable.add(src["fallback"])
        assert known - reachable == set(), (
            f"orphan sources: {sorted(known - reachable)}"
        )

    def test_every_brief_states_its_cap_and_its_ordering(self, registry):
        """#40 — a cap with no ordering cannot be reviewed when it binds."""
        for angle in registry["angles"]:
            text = self._brief(angle["id"])
            assert "**Cap:**" in text, angle["id"]
            assert "ordering:" in text, angle["id"]

    def test_every_conditional_brief_names_its_anchor_and_its_witness(self, registry):
        """#53 — a conditional angle must show it is not a restatement of the type trigger, and
        the cheapest proof is a concrete map that satisfies the trigger and leaves it false."""
        for angle in registry["angles"]:
            if angle.get("trigger") != "conditional":
                continue
            text = self._brief(angle["id"])
            assert "required-rooted" in text, f"{angle['id']}: no anchor stated"
            assert "Falsifying witness" in text, (
                f"{angle['id']}: no non-tautology witness"
            )

    def test_no_always_on_brief_claims_a_witness(self, registry):
        """MIRROR: an always-on angle has nothing to falsify, so claiming a witness would be
        cargo-culted structure rather than reasoning."""
        for angle in registry["angles"]:
            if angle.get("trigger") == "always":
                assert "Falsifying witness" not in self._brief(angle["id"]), angle["id"]


REFS = HERE.parent / "references"


def _yaml_blocks(path) -> list[dict]:
    """Every fenced yaml block in a markdown file, parsed."""
    text = path.read_text()
    return [
        yaml.safe_load(b) for b in re.findall(r"```yaml\n(.*?)```", text, re.DOTALL)
    ]


class TestGuideExamplesValidate:
    """C4 — a guide whose worked example does not pass the gate teaches the wrong thing, and the
    reader has no way to know. This is the cheapest check in the package and the one most likely
    to rot, because a guide is prose and nothing else reads it.
    """

    def test_the_map_guide_example_is_clean(self, registry):
        blocks = _yaml_blocks(REFS / "platform-vocabulary-map-guide.md")
        assert blocks, "the guide has no worked example at all"
        for doc in blocks:
            assert V.validate_keyword_map(doc, registry) == []

    def test_the_search_guide_example_is_clean(self, registry):
        maps = _yaml_blocks(REFS / "platform-vocabulary-map-guide.md")
        blocks = _yaml_blocks(REFS / "search-output-guide.md")
        assert blocks, "the guide has no worked example at all"
        for doc in blocks:
            assert V.validate_search(doc, maps[0], registry) == []

    def test_every_guide_and_validation_doc_exists(self):
        for name in (
            "platform-vocabulary-map-guide.md",
            "search-output-guide.md",
            "absent-input-policy.md",
            "sources.md",
        ):
            assert (REFS / name).is_file(), name
        for script in HERE.glob("*.py"):
            assert (HERE / f"{script.name}.validation.md").is_file(), script.name


SKILL = HERE.parent / "SKILL.md"
RSKILL = (
    HERE.parent.parent / "reviewing-platform-ecosystem-prior-art-survey" / "SKILL.md"
)


class TestProducerSkillContract:
    """C5 — the properties of SKILL.md that nothing else checks, because it is prose."""

    @staticmethod
    def _frontmatter() -> dict:
        """PARSED, not pattern-matched.

        The hand-rolled version read from `description: >` to the closing `---`, which was the
        whole block only because nothing followed the description. Adding `version` and `forge`
        below it silently folded both into the "description" and blew the character cap by 117 —
        a test failing on a field it was not measuring.
        """
        body = SKILL.read_text().split("---", 2)[1]
        return yaml.safe_load(body)

    def _description(self) -> str:
        return " ".join(self._frontmatter()["description"].split())

    def test_the_description_is_within_the_cap(self):
        assert len(self._description()) <= 1024, len(self._description())

    def test_the_frontmatter_carries_a_version_and_a_forge_stamp(self):
        fm = self._frontmatter()
        assert fm["version"], "unversioned"
        assert fm["forge"]["status"] == "reviewed", fm["forge"]
        assert fm["forge"]["reviewed"], "no review date"

    def test_the_reviewing_twin_is_versioned_in_step(self):
        """Two halves of one gate at two versions is a pair a consumer can install mismatched."""
        twin = yaml.safe_load((REVIEWER / "SKILL.md").read_text().split("---", 2)[1])
        assert twin["version"] == self._frontmatter()["version"], (
            twin["version"],
            self._frontmatter()["version"],
        )
        assert twin["forge"]["status"] == "reviewed"

    def test_the_description_states_the_wave_1_scope(self):
        """A future reader must not mistake this for the whole survey; #12 ships wave by wave."""
        assert "WAVE 1" in self._description().upper()

    def test_it_points_at_conditions_by_name(self):
        assert "conditions.md" in SKILL.read_text()

    def test_it_RESTATES_no_condition(self):
        """#32's defect in its purest form: a restated bar is a bar that drifts. A sibling shipped
        one term meaning results in the producer and distinct rows in the reviewer; it survived
        five forge cycles and two live runs and parked three tickets."""
        skill = SKILL.read_text()
        assert "VERDICT:" not in skill, (
            "SKILL.md emits a verdict; that is the reviewer's job"
        )
        assert not re.search(r"^\s*\*\*C[0-9]+", skill, re.MULTILINE), (
            "restates a numbered condition"
        )

    def test_every_reference_it_promises_exists(self):
        """A progressive-disclosure table naming a file that does not ship is a dead end at the
        exact moment the reader needed it."""
        for path in re.findall(r"`(references/[a-z0-9/<>._-]+)`", SKILL.read_text()):
            if "<" in path:
                continue  # a placeholder like references/angles/<id>.md
            if path.endswith("conditions.md"):
                continue  # cross-package: it lives in the REVIEWING half, and C6 owns its check
            assert (HERE.parent / path).exists(), path


REVIEWER = HERE.parent.parent / "reviewing-platform-ecosystem-prior-art-survey"
CONDITIONS = REVIEWER / "references" / "conditions.md"


class TestReviewerPackage:
    """C6. The reviewing half is prose, so its contract is checked here or nowhere.

    A reviewer whose bar drifts from the producer's contract fails in the expensive direction:
    it revises correct work, and at the cap it parks a ticket that needed no human.
    """

    def test_all_four_artifacts_exist(self):
        for rel in (
            "SKILL.md",
            "references/conditions.md",
            "references/sources.md",
            "references/fixtures/map.clean.yaml",
            "references/fixtures/search.clean.yaml",
        ):
            assert (REVIEWER / rel).exists(), rel

    def test_the_conditions_are_numbered_contiguously_from_one(self):
        """A gap in the numbering means a finding can name a condition that does not exist, and
        a producer cannot look up what it was asked to fix."""
        found = [int(n) for n in re.findall(r"^\*\*C([0-9]+) ", CONDITIONS.read_text(), re.M)]
        assert found == list(range(1, len(found) + 1)), found
        assert len(found) >= 20, found

    def test_every_condition_carries_an_evidence_rule(self):
        """#33. The rule is per condition, not stated once at the top, because the one place a
        reviewer reads under time pressure is the condition it is about to cite."""
        blocks = re.split(r"^\*\*C([0-9]+) ", CONDITIONS.read_text(), flags=re.M)[1:]
        pairs = list(zip(blocks[::2], blocks[1::2]))
        assert pairs
        for num, body in pairs:
            assert re.search(r"^\*Evidence:\*", body, re.M), f"C{num} states no evidence"

    def test_the_conditions_preamble_states_the_ungrounded_rule_and_its_cost(self):
        """Evidence per condition is half of #33. The other half is what an ungrounded finding
        costs — without it the rule reads as bookkeeping rather than as a price."""
        text = CONDITIONS.read_text()
        assert "OBSERVATION" in text
        assert "revise round" in text
        assert "park" in text

    def test_the_reviewer_skill_states_the_cost_too(self):
        skill = (REVIEWER / "SKILL.md").read_text()
        assert "OBSERVATION" in skill
        assert "revise round" in skill

    def test_the_reviewer_emits_exactly_one_verdict_vocabulary(self):
        """Two spellings of the terminal line is two parsers downstream."""
        skill = (REVIEWER / "SKILL.md").read_text()
        assert set(re.findall(r"^VERDICT: (\w+)$", skill, re.M)) == {"approve", "revise"}

    def test_the_reviewer_does_not_duplicate_the_deterministic_gate(self):
        """A finding the script could have produced costs a revise round on correct work."""
        assert "never report what the validator already checks" in (
            REVIEWER / "SKILL.md"
        ).read_text().lower()

    @pytest.mark.parametrize(
        ("produced", "calibration"),
        [
            ("platform-vocabulary-map.valid.yaml", "map.clean.yaml"),
            ("search-output.valid.yaml", "search.clean.yaml"),
        ],
    )
    def test_the_calibration_fixture_is_byte_identical_to_the_produced_one(
        self, produced, calibration
    ):
        """Two copies of one artifact in two packages is a drift path with nothing watching it.

        It is not hypothetical: correcting one `angle_applicability` verdict during C7 meant
        editing both files, and the second was easy to forget. "Clean" must mean the same bytes
        on both sides of the gate, or the reviewer calibrates on an artifact the producer would
        no longer emit.
        """
        assert (FIXTURES / produced).read_text() == (
            REVIEWER / "references/fixtures" / calibration
        ).read_text()

    def test_the_clean_fixtures_still_pass_the_producers_validator(self, registry):
        """The reviewer's calibration fixtures are what "clean" means. If they drift out of
        validity, every reviewer trained on them learns a bar the gate does not hold."""
        rev_map = yaml.safe_load((REVIEWER / "references/fixtures/map.clean.yaml").read_text())
        rev_search = yaml.safe_load(
            (REVIEWER / "references/fixtures/search.clean.yaml").read_text()
        )
        assert V.validate_keyword_map(rev_map, registry) == []
        assert V.validate_search(rev_search, rev_map, registry) == []


PLANTED = FIXTURES / "planted"

# The answer key for the blind run. It lives here, not beside the fixtures, because a reviewer
# that has read the key demonstrates nothing (#15). Kept as data so the exit-0 requirement is
# asserted over the same list a human reads.
PLANTED_DEFECTS = {
    "map-01.yaml": ("keyword-map", "C4", "b2's verdict is `false` while its own reason states the "
                    "scope value that satisfies the first leg of b2's disjunction"),
    "search-01.yaml": ("search", "C8", "two cells record a zero behind a paraphrase of a strategy "
                       "rather than a query that could be re-run"),
    "search-02.yaml": ("search", "C2", "a candidate is filed under `shopify` while its locator, "
                       "source and enumeration are all VS Code's"),
    "search-03.yaml": ("search", "C17", "the cap BOUND and its ordering restates the outcome "
                       "instead of stating a rule a reader could re-apply"),
}

# Each fixture carries ONE defect, deliberately. The first blind run returned a correct extra
# finding on every artifact it saw — an active source with no coverage cell, a source outside the
# angle's own list — because the first drafts were built forwards from the schema rather than
# backwards from the condition. A fixture with two defects does not test which one the reviewer
# can find; it tests which one it happens to look at first.


class TestPlantedFixtures:
    """C7. Each of these is wrong AND passes at exit 0 — that combination is the whole test.

    A planted defect the validator catches proves the validator works, which was never in
    question. It is the reviewer that is under test, and it only sees artifacts that already
    passed.
    """

    @pytest.mark.parametrize("name", sorted(PLANTED_DEFECTS))
    def test_it_passes_the_deterministic_gate(self, name, valid_map, registry):
        kind, _, _ = PLANTED_DEFECTS[name]
        doc = yaml.safe_load((PLANTED / name).read_text())
        if kind == "keyword-map":
            assert V.validate_keyword_map(doc, registry) == []
        else:
            km = yaml.safe_load((PLANTED / "map-01.yaml").read_text())
            assert V.validate_search(doc, km, registry) == []

    def _cli(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            capture_output=True,
            text=True,
            cwd=HERE,
            check=False,
        )

    def test_it_passes_through_main_too(self):
        """#51: the brief runs `main()`, not the functions. A fixture clean in-process and
        non-zero at the CLI would send the reviewer an artifact the producer never could."""
        km = PLANTED / "map-01.yaml"
        assert self._cli("keyword-map", str(km)).returncode == 0
        for name in ("search-01.yaml", "search-02.yaml", "search-03.yaml"):
            r = self._cli("search", str(PLANTED / name), "--keyword-map", str(km))
            assert r.returncode == 0, (name, r.stdout, r.stderr)

    def test_no_fixture_names_its_own_defect(self):
        """An answer written on the exam is not an exam."""
        leak = re.compile(r"\bC[0-9]{1,2}\b|planted|defect|deliberate|contradict", re.I)
        for path in PLANTED.glob("*.yaml"):
            assert not leak.search(path.read_text()), path.name

    def test_the_key_covers_at_least_four_and_names_distinct_conditions(self):
        assert len(PLANTED_DEFECTS) >= 4
        conds = [c for _, c, _ in PLANTED_DEFECTS.values()]
        assert len(set(conds)) == len(conds), conds

    def test_every_planted_file_is_in_the_key(self):
        """A fixture with no key entry is one nobody can grade, and it will sit here looking
        like coverage."""
        assert {p.name for p in PLANTED.glob("*.yaml")} == set(PLANTED_DEFECTS)

    @pytest.mark.parametrize("cond", sorted({c for _, c, _ in PLANTED_DEFECTS.values()}))
    def test_every_keyed_condition_exists_in_the_reviewing_skill(self, cond):
        """DERIVED from the key, not written down beside it. Hand-listed, re-keying a fixture to
        a different condition left this checking the old one — in the one file whose stated
        principle is that a second copy of a fact is a place for it to drift."""
        assert re.search(rf"^\*\*{cond} ", CONDITIONS.read_text(), re.M), cond


class TestJudgedFieldsAreDescribed:
    """Every field a reviewer judges must carry a schema `description`.

    `holds` and `kept` both shipped without one, and both were then read differently by the
    guide, the fixture and the reviewer. A field with no description has as many meanings as it
    has readers — and the FIXTURE's reading is the one that propagates, because the fixture is
    what the reviewing half copies. Identifiers (`angle_id`, `source_id`) are exempt: a reviewer
    matches them, it does not judge them.
    """

    @staticmethod
    def _schema(name: str) -> dict:
        import json

        return json.loads((HERE.parent / "schemas" / f"{name}.schema.json").read_text())

    def _cell(self) -> dict:
        return self._schema("search-output")["$defs"]["cell"]["properties"]

    def _verdict(self) -> dict:
        return self._schema("platform-vocabulary-map")["properties"]["angle_applicability"][
            "items"
        ]["properties"]

    @pytest.mark.parametrize("field", ["holds", "precondition", "reason"])
    def test_the_applicability_verdict_fields_are_described(self, field):
        assert self._verdict()[field].get("description"), field

    @pytest.mark.parametrize("field", ["queries", "status", "returned", "kept", "cause"])
    def test_the_coverage_cell_fields_are_described(self, field):
        assert self._cell()[field].get("description"), field

    def test_kept_says_it_counts_rows_into_candidates_PLUS_unadmitted(self):
        """#32, corrected twice. It first said ITEMS; then ROWS with the equality
        `kept == candidates`, described as "the same meaning the sibling types give it" — which
        was FALSE. market-competitive, visual and user-research all say candidate rows carried
        into candidates PLUS unadmitted. The unit was right and the SET was wrong, and counting
        only candidates scores a row dropped without a record as correct."""
        desc = self._cell()["kept"]["description"]
        assert "candidate ROWS" in desc
        assert "PLUS `unadmitted`" in desc
        assert "NEVER a result count" in desc

    def test_returned_states_its_unit_and_demands_a_frame(self):
        """It had none. Obvious for an enumeration angle, meaningless for a policy angle — where
        a cold agent had to invent a counting frame and said plainly that two competent agents
        would differ and neither would be wrong."""
        desc = self._cell()["returned"]["description"]
        assert "count_frame" in desc
        assert self._cell()["count_frame"].get("description")

    def test_holds_says_it_is_evaluated_over_the_scope(self):
        assert "THE SCOPE" in self._verdict()["holds"]["description"]

    def test_the_reason_field_names_the_disjunction_trap(self):
        """The defect a blind reviewer found: a reason establishing one leg of an OR and
        reporting the verdict of the other."""
        assert "leg" in self._verdict()["reason"]["description"]


class TestNoIncidentalGapInAnyFixture:
    """Every fixture carries exactly the defect its key names, and no other.

    Three separate blind runs each found an INCIDENTAL gap the key did not name — an active
    source with no cell, a source outside the angle's list, a fallback that left no trace, a
    kept-zero with no cause. Every one was mechanically checkable and none was checked, so the
    method was paying a blind run to discover what a loop over the registry finds for free (#49).

    A fixture with two defects does not test which one the reviewer can find; it tests which one
    it happens to look at first. These assertions apply to the CLEAN fixtures too, which is where
    the same gaps had been sitting longest.
    """

    SEARCHES = [
        (FIXTURES / "search-output.valid.yaml", FIXTURES / "platform-vocabulary-map.valid.yaml"),
        (PLANTED / "search-01.yaml", PLANTED / "map-01.yaml"),
        (PLANTED / "search-02.yaml", PLANTED / "map-01.yaml"),
        (PLANTED / "search-03.yaml", PLANTED / "map-01.yaml"),
    ]

    @staticmethod
    def _angle(doc: dict, registry: dict) -> dict:
        return next(a for a in registry["angles"] if a["id"] == doc["meta"]["angle_id"])

    @pytest.mark.parametrize("search,_map", SEARCHES, ids=lambda p: getattr(p, "name", ""))
    def test_every_source_the_angle_declares_has_a_cell(self, search, _map, registry):
        doc = yaml.safe_load(search.read_text())
        angle = self._angle(doc, registry)
        cells = {c["source_id"] for c in doc["coverage"]}
        assert not (set(angle["sources"]) - cells), search.name

    @pytest.mark.parametrize("search,_map", SEARCHES, ids=lambda p: getattr(p, "name", ""))
    def test_no_cell_comes_from_outside_the_angles_corpus(self, search, _map, registry):
        doc = yaml.safe_load(search.read_text())
        angle = self._angle(doc, registry)
        allowed = set(angle["sources"]) | {angle["fallback"]}
        assert not ({c["source_id"] for c in doc["coverage"]} - allowed), search.name

    @pytest.mark.parametrize("search,_map", SEARCHES, ids=lambda p: getattr(p, "name", ""))
    def test_a_named_fallback_leaves_a_trace(self, search, _map, registry):
        """C9. A walked fallback that returned nothing and a fallback never walked are different
        facts; with no cell they are indistinguishable."""
        doc = yaml.safe_load(search.read_text())
        cells = {c["source_id"] for c in doc["coverage"]}
        for cell in doc["coverage"]:
            used = cell.get("fallback_used")
            if used:
                assert used in cells, (search.name, used)

    @pytest.mark.parametrize("search,_map", SEARCHES, ids=lambda p: getattr(p, "name", ""))
    def test_a_kept_zero_that_had_something_to_drop_is_explained(self, search, _map, registry):
        doc = yaml.safe_load(search.read_text())
        owed = [
            c["source_id"]
            for c in doc["coverage"]
            if c["status"] == "reached" and c.get("kept") == 0 and (c.get("returned") or 0) > 0
        ]
        if owed:
            assert doc.get("unadmitted") or doc.get("notes"), (search.name, owed)

    @pytest.mark.parametrize("search,_map", SEARCHES, ids=lambda p: getattr(p, "name", ""))
    def test_admitted_rows_leave_a_trace(self, search, _map, registry):
        """`kept > 0` with no row naming the source means rows were carried forward and left no
        trace. A trace is a CANDIDATE or an `unadmitted` entry — the second is the whole point of
        that list, and counting only candidates scored a recorded rejection as a missing row."""
        doc = yaml.safe_load(search.read_text())
        traced = {c["source_id"] for c in doc["candidates"]}
        traced |= {u["found_by"] for u in doc.get("unadmitted") or []}
        for cell in doc["coverage"]:
            if (cell.get("kept") or 0) > 0:
                assert cell["source_id"] in traced, (search.name, cell["source_id"])


class TestFixtureProseCarriesNoStaleCardinality:
    """A hardcoded count inside a fixture's prose is a defect waiting for the next edit.

    "all three platforms" survived a fourth platform being added, in three files at once, and was
    found by a blind reviewer rather than by anything cheaper. Incrementing it to four would have
    reset the same trap for the fifth. The fix is to ban the shape: prose describes the list, the
    list carries the cardinality.
    """

    COUNTED = re.compile(r"\ball (?:two|three|four|five|six|seven)\b", re.I)

    def _fixture_files(self):
        yield from FIXTURES.glob("*.yaml")
        yield from PLANTED.glob("*.yaml")
        yield from (REVIEWER / "references" / "fixtures").glob("*.yaml")

    def test_no_fixture_hardcodes_a_count_of_something_it_lists(self):
        offenders = [
            (p.name, m.group(0))
            for p in self._fixture_files()
            for m in [self.COUNTED.search(p.read_text())]
            if m
        ]
        assert not offenders, offenders


class TestSupersededStatus:
    """`superseded` is this type's reason for existing at the status layer, and after the a3
    fixtures were corrected nothing exercised it any more.

    The correction was right — a3's four sources are all at their registry URLs, so the redirect
    the fixture narrated had never happened. But removing the only instance of a value the schema
    calls "the corpus's characteristic failure" silently deleted its coverage, which is a worse
    state than the wrong fixture: a wrong fixture gets caught, an absent one does not.
    """

    def test_a_superseded_cell_validates(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0].update(
            status="superseded",
            returned=None,
            kept=None,
            cause="301 to the live replacement at the vendor's new docs host; the fetch succeeded",
            fallback_used=None,
        )
        doc["retrieval_summary"]["status_counts"] = collections.Counter(
            c["status"] for c in doc["coverage"]
        )
        doc["candidates"] = [
            c for c in doc["candidates"] if c["source_id"] != doc["coverage"][0]["source_id"]
        ]
        assert V.validate_search(doc, valid_map, registry) == []

    def test_a_superseded_cell_still_owes_a_cause(self, valid_search, valid_map, registry):
        """The MIRROR (#34). `superseded` is the status most likely to be used as a shrug, because
        it sounds like a fact about the corpus rather than a claim needing evidence."""
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0].update(status="superseded", returned=None, kept=None, cause="  ")
        assert "coverage-cause-required" in _rules(
            V.validate_search(doc, valid_map, registry)
        )


class TestConditionValidatorBoundary:
    """C7's correction, pinned in BOTH directions (#34).

    C2 and C17 first shipped stating gaps the validator already fails, so neither could ever be
    cited: an artifact reaching the reviewer has passed at exit 0. The condition keeps the
    judgment half only. Each test asserts the shape half still FAILS the gate and the judgment
    half still PASSES it — one direction alone would let the boundary slide back.

    This class was silently deleted once, by a script that rebuilt the file as `text[:index] +
    replacement` and discarded everything after the index. The suite stayed green, because the
    only thing that noticed was gone. Truncating writes need an assertion on what they drop.
    """

    def test_a_slug_the_map_does_not_mint_is_the_VALIDATORS_job(
        self, valid_search, valid_map, registry
    ):
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["platform_slug"] = "notion"
        assert "slug-not-in-map" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_slug_naming_the_wrong_platform_is_the_REVIEWERS_job(self, registry):
        doc = yaml.safe_load((PLANTED / "search-02.yaml").read_text())
        km = yaml.safe_load((PLANTED / "map-01.yaml").read_text())
        assert V.validate_search(doc, km, registry) == []

    def test_a_missing_ordering_is_the_VALIDATORS_job(
        self, valid_search, valid_map, registry
    ):
        doc = copy.deepcopy(valid_search)
        doc["bound"]["hit"] = True
        doc["bound"]["ordering"] = "  "
        doc["bound"]["dropped_note"] = "the two lowest-completeness rows"
        assert "bound-needs-ordering" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_vacuous_ordering_is_the_REVIEWERS_job(self, registry):
        doc = yaml.safe_load((PLANTED / "search-03.yaml").read_text())
        km = yaml.safe_load((PLANTED / "map-01.yaml").read_text())
        assert V.validate_search(doc, km, registry) == []

    @pytest.mark.parametrize("rule", ["slug-not-in-map", "bound-needs-ordering"])
    def test_the_condition_text_disclaims_the_rule_the_validator_owns(self, rule):
        """Naming the owning rule in the condition is what stops it drifting back: a later editor
        reading "the validator fails that at X" cannot restore the shape gap by accident."""
        assert rule in CONDITIONS.read_text()


class TestFixtureProseDoesNotContradictTheRegistry:
    """The defect this task produced five times: prose asserting a fact the cited row denies.

    In order — a 301 the registry records no move for; an `as_of` carried from a different
    source's row; "a b2b marketplace that DOES publish a split" about a row whose note reads
    "publishes no revenue-share percentage"; a partner-agreement gate on a row whose note reads
    HTTP 403 bot-block; and a six-counts cause attributed to the wrong artifact. Every one was
    written while FIXING an earlier finding, and every one was caught by a reviewer rather than
    by anything here.

    This guard is narrow on purpose. It cannot check prose in general, but the recurring shape is
    specific: three rows in this corpus publish no commission figure, that absence IS the finding
    (C19), and asserting the opposite inverts it. Cheap, and it fires on the exact mistake.
    """

    # Platform as a fixture names it -> the registry row a claim about it must agree with.
    NAMED_ROWS = {
        "Atlassian Marketplace": "atlassian-marketplace",
        "GitHub Marketplace": "github-marketplace",
        "Apple App Store": "apple-review",
        # Salesforce is deliberately NOT here: its row records a 403, not an absent figure, so
        # this check has nothing to compare and the case only ever skipped. Its own claim is
        # asserted by `test_the_blocked_row_is_described_as_blocked_not_as_gated` below.
    }
    PUBLISHES_A_FIGURE = re.compile(
        r"\b(does publish|publishes) (?:a |its )?(split|revenue.share|commission|rate)", re.I
    )

    def _maps(self):
        yield FIXTURES / "platform-vocabulary-map.valid.yaml"
        yield PLANTED / "map-01.yaml"
        yield REVIEWER / "references" / "fixtures" / "map.clean.yaml"

    @staticmethod
    def _entry_text(doc: dict, item: str) -> str | None:
        for e in (doc.get("scope_guard") or {}).get("excluded") or []:
            if e.get("item") == item:
                return e.get("reason") or ""
        return None

    @pytest.mark.parametrize("platform,row_id", sorted(NAMED_ROWS.items()))
    def test_no_map_claims_a_figure_a_row_says_is_absent(self, platform, row_id, registry):
        note = next(
            (s.get("note") or "") for s in registry["sources"] if s["id"] == row_id
        )
        denies = re.search(r"publishes no|states no .*(rate|split)|no revenue.share", note, re.I)
        if not denies:
            pytest.skip(f"{row_id} records no absence to contradict")
        for path in self._maps():
            reason = self._entry_text(yaml.safe_load(path.read_text()), platform)
            if reason is None:
                continue
            assert not self.PUBLISHES_A_FIGURE.search(reason), (path.name, platform, reason)

    def test_the_blocked_row_is_described_as_blocked_not_as_gated(self, registry):
        """`blocked` is 403-from-this-client. Restating it as an access-terms gate is the more
        flattering cause — "nobody could fetch this" rather than "this client was blocked" — and
        `references/sources.md` states this corpus has no ToS gate on any row."""
        row = next(s for s in registry["sources"] if s["id"] == "salesforce-appexchange")
        assert row["access_status"] == "blocked"
        for path in self._maps():
            reason = self._entry_text(
                yaml.safe_load(path.read_text()), "Salesforce AppExchange"
            )
            if reason is None:
                continue
            assert not re.search(r"partner agreement|behind a (paywall|gate)", reason, re.I), (
                path.name,
                reason,
            )
            assert "403" in reason, (path.name, "the recorded cause is not stated")


class TestCallerInputIsAPackageFault:
    """Exit 2, not exit 1 — folded from the C8 code review, which found all three.

    Exit 1 means "the artifact under test has findings". Sending that for a bad CALLER input is
    the same harm the exit-2 class was built to prevent, one actor over: it dispatches an author
    to edit a file that is correct. Two of the three also produced no FAIL line at all, so a
    caller grepping for one found nothing while being told the artifact was defective.
    """

    def _cli(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            capture_output=True,
            text=True,
            cwd=HERE,
            check=False,
        )

    @pytest.mark.parametrize(
        "body", ["- a\n- b\n", "", "just a string\n", "platforms: not-a-list\n"]
    )
    def test_an_unusable_keyword_map_exits_2_with_a_grepable_line(self, body, tmp_path):
        bad = tmp_path / "map.yaml"
        bad.write_text(body)
        r = self._cli(
            "search", str(FIXTURES / "search-output.valid.yaml"), "--keyword-map", str(bad)
        )
        assert r.returncode == 2, (r.returncode, r.stdout, r.stderr)
        assert r.stdout.startswith("FAIL keyword-map-unusable"), r.stdout

    def test_a_wrong_but_parseable_map_does_not_blame_the_artifact(self, tmp_path):
        """The sharpest case: handing the SEARCH OUTPUT as the keyword map used to yield three
        `slug-not-in-map` findings at exit 1 against a file that is entirely correct."""
        r = self._cli(
            "search",
            str(FIXTURES / "search-output.valid.yaml"),
            "--keyword-map",
            str(FIXTURES / "search-output.valid.yaml"),
        )
        assert r.returncode == 2, r.stdout
        assert "slug-not-in-map" not in r.stdout

    @pytest.mark.parametrize("kind", ["artifact", "keyword-map"])
    def test_a_non_utf8_file_exits_2(self, kind, tmp_path):
        """`UnicodeDecodeError` is a ValueError, not an OSError, so an `except OSError` that looks
        exhaustive let it escape as a traceback at exit 1."""
        bad = tmp_path / "bad.bin"
        bad.write_bytes(b"\xff\xfe\x00\x01 not utf8")
        if kind == "artifact":
            r = self._cli("keyword-map", str(bad))
        else:
            r = self._cli(
                "search", str(FIXTURES / "search-output.valid.yaml"), "--keyword-map", str(bad)
            )
        assert r.returncode == 2, (r.returncode, r.stdout, r.stderr)
        assert "FAIL input" in r.stdout


class TestRegistryShapeIsAPackageFault:
    @pytest.mark.parametrize("shape", [[], "a string", None, 3])
    def test_a_registry_that_is_not_a_mapping_is_caught_before_use(self, shape, monkeypatch):
        """Unreadable and unparseable were covered; WRONG-SHAPED reached `anchor_failures` and
        raised, giving exit 1 — the artifact-fault code — for a fault in the shipped package."""
        monkeypatch.setattr(V, "load_registry", lambda: shape)
        assert V.main(["keyword-map", str(FIXTURES / "platform-vocabulary-map.valid.yaml")]) == 2

    def test_an_unreadable_registry_exits_2(self, monkeypatch):
        """The `registry-unreadable` branch had no test at all: turning its `return 2` into a
        `return 0` left the whole suite green."""
        def boom():
            raise OSError(2, "No such file or directory")

        monkeypatch.setattr(V, "load_registry", boom)
        assert V.main(["keyword-map", str(FIXTURES / "platform-vocabulary-map.valid.yaml")]) == 2


class TestTriggerValueIsChecked:
    """A one-character typo in `trigger` made a conditional angle look always-on to every check
    below it, so the anchor rules failed OPEN — the direction #53 exists to close."""

    def test_a_mistyped_trigger_is_caught(self):
        bad = {"angles": [{"id": "b1", "trigger": "conditonal"}]}
        assert "trigger-must-be-known" in _rules(V.anchor_failures(bad))

    def test_a_missing_trigger_is_caught(self):
        assert "trigger-must-be-known" in _rules(V.anchor_failures({"angles": [{"id": "b1"}]}))

    def test_the_shipped_registry_declares_only_known_triggers(self, registry):
        assert {a.get("trigger") for a in registry["angles"]} <= {"always", "conditional"}

    def test_a_scalar_anchor_is_rejected(self, registry):
        """`anchor-must-be-a-list` was reachable and unexercised: deleting the branch left the
        suite green. A scalar cannot describe a disjunctive predicate."""
        bad = {
            "angles": [
                {
                    "id": "b1",
                    "trigger": "conditional",
                    "trigger_anchor": "business.platform.type",
                }
            ]
        }
        assert "anchor-must-be-a-list" in _rules(V.anchor_failures(bad))


class TestUnrunAngleOwesNoCandidatesEither:
    """#34. The coverage half of this mirror shipped; the candidates half did not — and candidates
    are the layer synthesis actually reads."""

    def test_not_run_with_candidates_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc.update(outcome="not_run", coverage=[])
        doc["retrieval_summary"]["status_counts"] = {}
        assert "not-run-owes-no-candidates" in _rules(
            V.validate_search(doc, valid_map, registry)
        )

    def test_not_run_with_neither_passes(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc.update(outcome="not_run", coverage=[], candidates=[])
        doc["retrieval_summary"]["status_counts"] = {}
        assert V.validate_search(doc, valid_map, registry) == []


class TestCapAndHitReconcileWithTheRegistry:
    """Both are pure arithmetic over data the validator already holds, and neither the gate nor
    any of the 20 reviewer conditions owned them — so a run that raised its own ceiling reached
    synthesis unremarked."""

    def test_a_cap_the_registry_does_not_set_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["bound"]["cap"] = 9999
        assert "cap-not-the-registrys" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_LOWERED_cap_fails_too(self, valid_search, valid_map, registry):
        """MIRROR (#34): quietly lowering the ceiling shrinks a survey, which is the direction
        that hides work rather than inventing it."""
        doc = copy.deepcopy(valid_search)
        doc["bound"]["cap"] = 2
        assert "cap-not-the-registrys" in _rules(V.validate_search(doc, valid_map, registry))

    def test_the_registrys_own_cap_passes(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        angle = doc["meta"]["angle_id"]
        doc["bound"]["cap"] = next(a["cap"] for a in registry["angles"] if a["id"] == angle)
        assert V.validate_search(doc, valid_map, registry) == []

    def test_not_hit_above_the_cap_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["bound"]["hit"] = False
        doc["candidates"] = doc["candidates"] * 8
        assert "not-hit-contradicts-the-count" in _rules(
            V.validate_search(doc, valid_map, registry)
        )

    def test_not_hit_at_or_under_the_cap_passes(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["bound"]["hit"] = False
        assert V.validate_search(doc, valid_map, registry) == []


class TestDuplicatesInTheMap:
    """Absence was checked in both places; DUPLICATION was checked in neither (#34)."""

    def test_a_slug_minted_twice_fails(self, valid_map, registry):
        doc = copy.deepcopy(valid_map)
        doc["platforms"].append(copy.deepcopy(doc["platforms"][0]))
        assert "slug-minted-twice" in _rules(V.validate_keyword_map(doc, registry))

    def test_distinct_slugs_pass(self, valid_map, registry):
        assert V.validate_keyword_map(valid_map, registry) == []

    def test_two_verdicts_for_one_angle_fail(self, valid_map, registry):
        """The sharp form: the two disagree, and a reader takes whichever it meets first."""
        doc = copy.deepcopy(valid_map)
        clash = copy.deepcopy(doc["angle_applicability"][0])
        clash["holds"] = not clash["holds"]
        doc["angle_applicability"].append(clash)
        assert "verdict-declared-twice" in _rules(V.validate_keyword_map(doc, registry))


class TestReachedCellOwesKept:
    def test_a_reached_cell_without_kept_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0].pop("kept")
        assert "coverage-reached-needs-kept" in _rules(
            V.validate_search(doc, valid_map, registry)
        )

    def test_an_unreached_cell_owes_no_kept(self, valid_search, valid_map, registry):
        """MIRROR: a null kept is REQUIRED there — a count on an unreached cell is a zero
        laundered out of a failure."""
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0].update(
            status="unreachable", returned=None, kept=None, cause="HTTP 503 from the origin"
        )
        doc["candidates"] = [
            c for c in doc["candidates"] if c["source_id"] != doc["coverage"][0]["source_id"]
        ]
        doc["retrieval_summary"]["status_counts"] = collections.Counter(
            c["status"] for c in doc["coverage"]
        )
        assert V.validate_search(doc, valid_map, registry) == []


class TestSummaryIsRequired:
    def test_dropping_the_summary_fails(self, valid_search, valid_map, registry):
        """It silently disabled the reconciliation, which is indistinguishable from a run where
        the reconciliation happened to agree."""
        doc = copy.deepcopy(valid_search)
        doc.pop("retrieval_summary")
        assert "summary-required" in _rules(V.validate_search(doc, valid_map, registry))

    def test_an_unrun_angle_owes_no_summary(self, valid_search, valid_map, registry):
        """MIRROR: with no cells there is nothing to reconcile, so the rule must not fire."""
        doc = copy.deepcopy(valid_search)
        doc.update(outcome="not_run", coverage=[], candidates=[])
        doc.pop("retrieval_summary")
        assert V.validate_search(doc, valid_map, registry) == []


class TestProseAgreesWithTheRegistry:
    """C9a found the registry's own headline claims false on its own rows. Both are cheap to pin.

    A header sentence is read by every agent that opens the file and is checked by nobody, so it
    drifts freely — and a false invariant is worse than none, because it tells an agent not to
    look.
    """

    REG = HERE.parent / "references" / "source-registry.yaml"
    SKILL_MD = HERE.parent / "SKILL.md"

    @staticmethod
    def _every_authored_file() -> list[Path]:
        """EVERY prose and schema file in BOTH packages.

        The first version of this guard checked two files, and a claim it was written to kill
        survived in two others — a guard that inspects part of a population certifies that part
        and licenses the rest. If a claim is wrong, it is wrong everywhere it appears.
        """
        roots = [HERE.parent, HERE.parent.parent / "reviewing-platform-ecosystem-prior-art-survey"]
        out: list[Path] = []
        for root in roots:
            for pattern in ("**/*.md", "**/*.json", "**/*.yaml"):
                out += [f for f in root.glob(pattern) if "scripts" not in f.parts]
        assert len(out) >= 15, len(out)
        return out

    def test_no_prose_claims_terms_are_unaddressed_anywhere(self, registry):
        """"automated access is not addressed on any row" was false on five rows, three of which
        carry an AFFIRMATIVE grant. Addressed-and-permitted is a different state from unaddressed,
        and this corpus's own policy file reserves the term for the other one."""
        addressed = [
            s["id"]
            for s in registry["sources"]
            if re.search(r"Content-Signal|automated means|anti-scraping|robots\.txt",
                         s.get("note") or "", re.I)
        ]
        assert addressed, "the premise of this test is gone; re-check the claim"
        for path in self._every_authored_file():
            assert "not addressed on any" not in path.read_text(), (path.name, addressed)

    def test_no_prose_says_a_cell_is_per_mechanism(self):
        """The same survivor shape, one commit later: SKILL.md and the MAP schema were corrected
        and the SEARCH schema — which the reviewer is told is its evidence — was not."""
        for path in self._every_authored_file():
            body = path.read_text()
            assert "mechanism x" not in body, path.name
            assert "mechanism ×" not in body, path.name

    def test_a_self_fallback_is_documented_as_meaning_no_fallback(self, registry):
        """Ten rows name themselves. The header said every fallback "itself resolves", which for
        `salesforce-appexchange` — a row blocked on a 403 — reads as "retry the 403"."""
        selfies = [s["id"] for s in registry["sources"] if s.get("fallback") == s["id"]]
        assert len(selfies) >= 5, selfies
        header = self.REG.read_text()[:2000]
        assert "name THEMSELVES" in header, "the self-fallback convention is unexplained"

    @staticmethod
    def _reachable(registry: dict) -> set[str]:
        """Transitive closure. Reachability has TWO edges — an angle names sources and a
        fallback, and each ROW names a fallback of its own. Following only the first left four
        legitimate rows (`apple-dev-news`, `shopify-llms-md`, `stripe-connect-md`,
        `wp-plugins-svn`) looking orphaned; they are reached one hop further in.
        """
        by_id = {s["id"]: s for s in registry["sources"]}
        seen: set[str] = set()
        queue = []
        for a in registry["angles"]:
            queue += list(a.get("sources") or [])
            if a.get("fallback"):
                queue.append(a["fallback"])
        while queue:
            sid = queue.pop()
            if sid in seen or sid not in by_id:
                continue
            seen.add(sid)
            if by_id[sid].get("fallback"):
                queue.append(by_id[sid]["fallback"])
        return seen

    @pytest.mark.parametrize("rid", ["semantic-scholar", "crossref", "salesforce-appexchange"])
    def test_a_row_no_angle_reaches_says_so(self, rid, registry):
        """~25 lines an agent reads and can never use, with nothing marking them as such."""
        row = next(s for s in registry["sources"] if s["id"] == rid)
        assert rid not in self._reachable(registry), f"{rid} is reachable now — drop it here"
        assert row.get("unreached_in_wave_1"), rid

    def test_every_other_row_is_reachable(self, registry):
        """The mirror: the label must not become a licence to leave rows unreachable."""
        reachable = self._reachable(registry)
        orphans = {
            s["id"]
            for s in registry["sources"]
            if s["id"] not in reachable and not s.get("unreached_in_wave_1")
        }
        assert not orphans, orphans


class TestTheProducerIsToldWhatTheReviewerDemands:
    """C9a's I2: three reviewer conditions demanded artifact content the producer's prose never
    asked for — `unadmitted` on a dropped hit, `bound.dropped_note`, and `meta.scope_ref` plus
    `assumptions`. The last is the worst, because C4 is the condition the reviewer is told to read
    hardest and both its evidence fields are OPTIONAL in the schema.

    A duty that exists only in the reviewer is a revise round waiting to happen: the producer is
    judged on something it was never told to do.
    """

    PRODUCER_PROSE = "SKILL.md"

    def _producer_text(self) -> str:
        return (HERE.parent / self.PRODUCER_PROSE).read_text()

    @pytest.mark.parametrize(
        "field", ["unadmitted", "dropped_note", "scope_ref", "assumptions"]
    )
    def test_a_field_the_conditions_judge_is_named_in_the_producer_procedure(self, field):
        assert field in CONDITIONS.read_text(), f"{field} is no longer judged; drop it here"
        assert field in self._producer_text(), (
            f"the reviewer judges {field} and the producer is never told to write it"
        )

    def test_the_validator_command_is_actually_spelled_out(self):
        """It was ordered four times as `validate_…` — an ellipsis — while the same file says
        "You do not resolve paths yourself". The agent had to guess the interpreter, the path and
        the working directory before it could satisfy its own exit gate."""
        text = self._producer_text()
        assert "scripts/validate_platform_ecosystem_prior_art.py" in text
        assert "validate_…" not in text

    @pytest.mark.parametrize("value", ["not_run", "vacated", "ran"])
    def test_every_outcome_the_schema_requires_is_explained(self, value):
        """`outcome` is required with three values and the prose named none of them, so an angle
        whose own verdict says it does not apply had no branch to take."""
        assert value in self._producer_text(), value


class TestTheThreeShapeHalvesOfC9:
    """Found by auditing all 20 conditions against all 31 rules, rather than waiting for a fourth
    reviewer to find the fourth instance.

    C9 carried three gaps and every one had a decidable shape half sitting only in the condition.
    Two were named as inputs to the code-review task and then not built when that task landed —
    a survivor of my own plan, which is the shape #55 describes.
    """

    def test_an_angle_source_with_no_cell_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        # DERIVED, not positional: popping the last cell took the FALLBACK and fired the sibling
        # rule instead, so the test passed on the wrong finding until it asserted the rule id.
        angle = next(
            a for a in registry["angles"] if a["id"] == doc["meta"]["angle_id"]
        )
        dropped = next(
            c["source_id"] for c in doc["coverage"] if c["source_id"] in angle["sources"]
        )
        doc["coverage"] = [c for c in doc["coverage"] if c["source_id"] != dropped]
        doc["candidates"] = [c for c in doc["candidates"] if c["source_id"] != dropped]
        doc["retrieval_summary"]["status_counts"] = collections.Counter(
            c["status"] for c in doc["coverage"]
        )
        assert "angle-source-without-a-cell" in _rules(
            V.validate_search(doc, valid_map, registry)
        )

    def test_a_complete_coverage_grid_passes(self, valid_search, valid_map, registry):
        """MIRROR: the rule must not fire on the shipped fixture, which covers every a3 source."""
        assert V.validate_search(valid_search, valid_map, registry) == []

    def test_an_unrun_angle_owes_no_cells_at_all(self, valid_search, valid_map, registry):
        """MIRROR, the one that would break the not_run branch: an angle ruled out by its own
        verdict must not be told it is missing eleven cells."""
        doc = copy.deepcopy(valid_search)
        doc.update(outcome="not_run", coverage=[], candidates=[])
        doc.pop("retrieval_summary")
        assert V.validate_search(doc, valid_map, registry) == []

    def test_a_named_fallback_with_no_cell_of_its_own_fails(
        self, valid_search, valid_map, registry
    ):
        doc = copy.deepcopy(valid_search)
        used = next(c["fallback_used"] for c in doc["coverage"] if c.get("fallback_used"))
        doc["coverage"] = [c for c in doc["coverage"] if c["source_id"] != used]
        doc["candidates"] = [c for c in doc["candidates"] if c["source_id"] != used]
        doc["retrieval_summary"]["status_counts"] = collections.Counter(
            c["status"] for c in doc["coverage"]
        )
        assert "fallback-without-a-cell" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_kept_zero_with_nothing_explaining_it_fails(
        self, valid_search, valid_map, registry
    ):
        """Emptying `unadmitted` now moves the kept arithmetic too, so the cells it accounted for
        are zeroed with it — otherwise this test fires `kept-does-not-match-candidates` and passes
        for the wrong reason."""
        doc = copy.deepcopy(valid_search)
        orphaned = {u["found_by"] for u in doc.get("unadmitted") or []}
        doc["unadmitted"] = []
        doc["notes"] = []
        cited = {c["source_id"] for c in doc["candidates"]}
        for cell in doc["coverage"]:
            if cell["source_id"] in orphaned and cell["source_id"] not in cited:
                cell["kept"] = 0
            elif cell["source_id"] in orphaned:
                cell["kept"] = sum(1 for c in doc["candidates"] if c["source_id"] == cell["source_id"])
        assert "kept-zero-unexplained" in _rules(V.validate_search(doc, valid_map, registry))

    def test_a_kept_zero_against_a_zero_return_owes_nothing(
        self, valid_search, valid_map, registry
    ):
        """MIRROR: nothing was retrieved, so nothing was discarded and no reason is owed. Firing
        here would push producers toward omitting the cell, which is the failure C9 exists to
        prevent."""
        doc = copy.deepcopy(valid_search)
        doc["unadmitted"] = []
        doc["notes"] = []
        for cell in doc["coverage"]:
            if cell["status"] == "reached":
                cell["returned"] = 0
                cell["kept"] = 0
        doc["candidates"] = []
        assert V.validate_search(doc, valid_map, registry) == []


class TestEveryFieldTheProseDemandsExists:
    """C9b's blocker class: the prose ordered five things the schema forbade.

    `candidate` is `additionalProperties: false`, so a bolded Rule saying "quote verbatim" against
    a schema with no quote field is not a style problem — the artifact cannot validate, and the
    SKILL's own "fix and re-run until exit 0" loop has no legal fix. Three reviewer conditions
    grounded on the missing text, so all three were unexecutable too.
    """

    @staticmethod
    def _props(defname: str) -> dict:
        import json

        schema = json.loads((HERE.parent / "schemas" / "search-output.schema.json").read_text())
        return schema["$defs"][defname]["properties"]

    @pytest.mark.parametrize(
        "field", ["evidence_quote", "claim", "finding", "announced_on", "enforced_on"]
    )
    def test_the_candidate_can_hold_it(self, field):
        assert field in self._props("candidate"), field

    def test_the_cell_can_record_which_variant_was_read(self):
        assert "variant_read" in self._props("cell")

    @pytest.mark.parametrize(
        "field", ["evidence_quote", "claim", "finding", "variant_read"]
    )
    def test_the_producer_is_told_where_it_goes(self, field):
        assert field in (HERE.parent / "SKILL.md").read_text(), field

    def test_a4s_two_dates_now_validate(self, valid_search, valid_map, registry):
        """a4 orders them as separate fields with its reason stated, and they were forbidden —
        so a4's headline output had nowhere to go."""
        doc = copy.deepcopy(valid_search)
        doc["candidates"][0]["announced_on"] = "2020-01"
        doc["candidates"][0]["enforced_on"] = "2024-06"
        assert V.validate_search(doc, valid_map, registry) == []

    def test_the_shipped_candidates_carry_their_evidence(self, valid_search):
        """The exemplar must MODEL the rule, not merely be permitted by it."""
        for c in valid_search["candidates"]:
            assert c.get("evidence_quote"), c["platform_slug"]
            assert c.get("claim"), c["platform_slug"]


class TestTheReviewerKnowsAboutOutcome:
    """C9's cell expectations are conditional on `outcome`, and the reviewer package did not carry
    the word at all — so a correctly `not_run` angle, which the gate REQUIRES to be empty, would
    have been revised for having no cells."""

    @pytest.mark.parametrize("value", ["not_run", "vacated", "ran"])
    def test_the_conditions_name_every_outcome(self, value):
        assert value in CONDITIONS.read_text(), value

    def test_the_reviewer_is_told_the_map_is_an_input(self):
        """C2's entire test is the candidate's evidence against the map row its slug points at,
        and the evidence table listed four things, none of them the map."""
        assert "vocabulary map" in (REVIEWER / "SKILL.md").read_text()


class TestNoAuthoringReferenceShips:
    """A dispatched agent cannot resolve "(playbook #53)" — the playbook lives in the host program
    this package is explicitly told it cannot see. An unresolvable citation invites an agent to go
    looking, and burns turns on a dead path."""

    def test_no_shipped_prose_cites_a_playbook_decision(self):
        pattern = re.compile(r"\(?playbook #\d+\)?|\(#\d{1,3}\)")
        for path in TestProseAgreesWithTheRegistry._every_authored_file():
            m = pattern.search(path.read_text())
            assert not m, (path.name, m.group(0))


class TestPortability:
    """EC5. These packages ship to other projects and cannot see the program that authored them.

    The pattern includes `agents-hq` and the allowlist exempts the schemas' `$id` host, which the
    owner settled: the project name stays and the check carries a real exemption. An earlier
    version of this pattern used `\\bhq \\b`, which requires a trailing space and so matched
    neither the string that ships nor the allowlist meant to exempt it — both halves broken, so
    the check had never enforced anything. Hence the second test: the exemption must be shown to
    fire, not assumed.
    """

    LEAK = re.compile(
        r"playbook ?#|spec L-|classification-schema|\b5[a-j]\b|disk-authoritative|"
        r"this ticket|agents-hq|coordinator|project_prior_art",
        re.I,
    )
    ALLOWED = re.compile(r"agents-hq\.local/schemas/", re.I)

    def test_no_host_program_term_ships(self):
        offenders = []
        for path in TestProseAgreesWithTheRegistry._every_authored_file():
            for n, line in enumerate(path.read_text().splitlines(), 1):
                if self.LEAK.search(line) and not self.ALLOWED.search(line):
                    offenders.append(f"{path.name}:{n}: {line.strip()[:90]}")
        assert not offenders, offenders

    def test_the_allowlist_actually_fires(self):
        """A real `$id` line, run through both halves. Without the allowlist it matches; with it,
        it does not — which is what "the exemption works" means and what the old one failed."""
        real = '  "$id": "https://agents-hq.local/schemas/search-output.schema.json",'
        assert self.LEAK.search(real), "the pattern no longer matches the string it exempts"
        assert self.ALLOWED.search(real), "the exemption does not match the real $id"

    def test_the_id_host_is_what_the_allowlist_expects(self):
        """If the `$id` host is ever changed, the exemption silently stops covering anything and
        this suite would go green on a check enforcing nothing."""
        import json

        for name in ("search-output", "platform-vocabulary-map"):
            schema = json.loads((HERE.parent / "schemas" / f"{name}.schema.json").read_text())
            assert self.ALLOWED.search(schema["$id"]), schema["$id"]


class TestKeptEqualsTheCandidatesItCounted:
    """The check the ROWS semantics makes possible, and the reason to adopt it.

    Under the ITEMS reading only a DIRECTION was checkable (kept > 0 owes a candidate). Under
    ROWS it is an equality — the same number seen from two sides — which is what a blind reviewer
    asked for when it found a `kept: 29` cell no candidate cited.
    """

    def test_more_kept_than_candidates_fails(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        doc["coverage"][0]["kept"] += 1
        assert "kept-does-not-match-candidates" in _rules(
            V.validate_search(doc, valid_map, registry)
        )

    def test_fewer_kept_than_candidates_fails(self, valid_search, valid_map, registry):
        """MIRROR (#34). Under-reporting hides a row from the coverage arithmetic exactly as
        over-reporting invents one."""
        doc = copy.deepcopy(valid_search)
        sid = doc["candidates"][0]["source_id"]
        for cell in doc["coverage"]:
            if cell["source_id"] == sid:
                cell["kept"] = 0
        doc["unadmitted"] = doc.get("unadmitted") or [{"item": "x", "reason": "y"}]
        assert "kept-does-not-match-candidates" in _rules(
            V.validate_search(doc, valid_map, registry)
        )

    def test_the_shipped_fixture_reconciles_exactly(self, valid_search, valid_map, registry):
        assert V.validate_search(valid_search, valid_map, registry) == []

    def test_an_unreached_cell_is_exempt(self, valid_search, valid_map, registry):
        """MIRROR: kept is NULL there by rule, so there is nothing to reconcile and the check
        must not fire — a rule that fires on every non-reached cell would make the status
        unusable."""
        doc = copy.deepcopy(valid_search)
        cell = doc["coverage"][0]
        sid = cell["source_id"]
        cell.update(status="unreachable", returned=None, kept=None, cause="HTTP 503")
        doc["candidates"] = [c for c in doc["candidates"] if c["source_id"] != sid]
        doc["retrieval_summary"]["status_counts"] = collections.Counter(
            c["status"] for c in doc["coverage"]
        )
        assert V.validate_search(doc, valid_map, registry) == []


class TestD1aFindings:
    """Fixes the cold run earned. It passed both artifacts at exit 0 first time; everything here
    came from the half of the gate that asks what was AMBIGUOUS."""

    def test_the_documented_command_states_its_dependencies(self):
        """The documented invocation did not run: a bare `python` lacking pyyaml died with a
        traceback at exit 1 — the artifact-has-findings code — so a cold agent had an exit gate it
        could not satisfy and no way to know the fault was not its own."""
        skill = (HERE.parent / "SKILL.md").read_text()
        assert "--with pyyaml" in skill and "--with jsonschema" in skill

    def test_a_missing_dependency_is_a_package_fault(self):
        """Exit 2 with a greppable line, like every other package fault."""
        assert "dependency-missing" in SCRIPT.read_text()
        assert "_MISSING_DEPENDENCY" in SCRIPT.read_text()

    def test_the_quality_bar_does_not_route_through_an_uninstalled_package(self):
        """SKILL.md called the twin's conditions "the single source of the quality bar" — and the
        twin is not installed alongside the producer in the projects this ships to, so the cold
        agent never read it."""
        skill = (HERE.parent / "SKILL.md").read_text()
        assert "single source of the quality bar" not in skill
        assert "if it is installed" in skill

    def test_the_two_worked_examples_do_not_read_one_scope_two_ways(self):
        """SKILL.md's example assumption and the map guide's worked example used the IDENTICAL
        scope string and reached opposite readings of it — which flips b1 and b2. An agent taking
        the guide as its template would have shipped the opposite map and never seen the choice."""
        guide = (HERE.parent / "references" / "platform-vocabulary-map-guide.md").read_text()
        skill = (HERE.parent / "SKILL.md").read_text()
        assert "connector marketplace" in skill
        assert "connector marketplace, b2b" not in guide

    def test_the_map_can_record_a_corpus_observation(self):
        import json

        schema = json.loads(
            (HERE.parent / "schemas" / "platform-vocabulary-map.schema.json").read_text()
        )
        assert "notes" in schema["properties"]

    @pytest.mark.parametrize("field", ["count_frame", "ordering_deviation"])
    def test_the_fields_the_cold_run_had_nowhere_to_put(self, field):
        assert field in (HERE.parent / "schemas" / "search-output.schema.json").read_text()


class TestRegistryDatesObeyTheirOwnRule:
    """The type's central rule is that `as_of` is when the FACT became true and a page's own
    revision date is a CLAIM. Three registry rows carried a page self-claim in the `as_of`
    column — the exact conflation the package teaches against, in the file it teaches from.

    A cold agent found it by reading the rule and the rows together and could not honour both.
    """

    def test_no_row_files_its_own_self_claim_as_as_of(self, registry):
        offenders = [
            s["id"]
            for s in registry["sources"]
            if s.get("as_of") and s.get("as_of") == s.get("source_claimed_modified_at")
        ]
        assert not offenders, offenders

    @pytest.mark.parametrize("rid", ["apple-review", "mozilla-policies", "hubspot-listing"])
    def test_the_three_corrected_rows_hold_their_date_as_a_claim(self, rid, registry):
        row = next(s for s in registry["sources"] if s["id"] == rid)
        assert row.get("as_of") is None, rid
        assert row.get("source_claimed_modified_at"), rid
        assert row.get("source_claim_provenance"), rid


class TestKeptCountsUnadmittedToo:
    """The correction the ml design review found by reading this package as an input.

    `kept` shipped as `== candidates citing this source`, described as "the same meaning the
    sibling types give it". That sentence was false: `market-competitive`, `visual` and
    `user-research` all say candidate rows carried into candidates PLUS unadmitted, and market
    enforces it. The unit was right, the SET was wrong — and the weaker equality scored a row
    found and dropped WITHOUT a record as correct, which is the one thing `unadmitted` exists to
    make impossible.

    Root cause was one field upstream: `unadmitted` entries carried no source, so a per-source
    reconciliation against them was impossible and the rule was written to fit the weakness.
    """

    def test_an_unadmitted_row_counts_toward_kept(self, valid_search, valid_map, registry):
        doc = copy.deepcopy(valid_search)
        sid = doc["coverage"][0]["source_id"]
        doc["unadmitted"].append(
            {"item": "another candidate", "found_by": sid, "reason": "not vendor-published"}
        )
        doc["coverage"][0]["kept"] += 1
        assert V.validate_search(doc, valid_map, registry) == []

    def test_dropping_a_row_without_recording_it_now_FAILS(
        self, valid_search, valid_map, registry
    ):
        """The case the candidates-only equality called correct: a row was carried forward and
        left no trace anywhere. Under the old rule `kept` simply had to match the candidates, so
        deleting the record was free."""
        doc = copy.deepcopy(valid_search)
        sid = doc["coverage"][0]["source_id"]
        doc["coverage"][0]["kept"] += 1
        assert "kept-does-not-match-candidates" in _rules(
            V.validate_search(doc, valid_map, registry)
        ), sid

    def test_an_unadmitted_entry_must_name_its_source(self, valid_search, valid_map, registry):
        """Without `found_by` the row cannot be counted, and an uncountable row is exactly how a
        dropped candidate hides — so the schema requires it."""
        doc = copy.deepcopy(valid_search)
        doc["unadmitted"][0].pop("found_by")
        assert "schema" in _rules(V.validate_search(doc, valid_map, registry))

    def test_the_source_it_names_must_be_real(self, valid_search, valid_map, registry):
        """MIRROR: a `found_by` naming a source with no cell would let a row be counted against
        nothing, restoring the hole from the other side."""
        doc = copy.deepcopy(valid_search)
        doc["unadmitted"][0]["found_by"] = "not-a-source"
        assert V.validate_search(doc, valid_map, registry) != []
