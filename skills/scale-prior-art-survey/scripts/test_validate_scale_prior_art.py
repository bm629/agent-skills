"""Tests for the scale prior-art validator and its registry.

Run:  uv run --group dev pytest skills/scale-prior-art-survey/scripts -q
"""

from __future__ import annotations

import pathlib
import sys

import pytest
import yaml

HERE = pathlib.Path(__file__).resolve().parent
PKG = HERE.parent
ROOT = PKG.parents[1]
REGISTRY = PKG / "references" / "source-registry.yaml"

#: §12's per-row field set, exactly ten. Asserted by EQUALITY rather than containment, so a
#: field added on one side and not the other fails instead of passing quietly.
ROW_FIELDS = {
    "id",
    "url",
    "url_kind",
    "access_status",
    "authority_band",
    "as_of",
    "yields",
    "complete_listing",
    "fallback",
    "fallback_rationale",
}
#: §12's angle-block list, exactly sixteen. `sizing_record` is a seventeenth key owed on the
#: three MEASURED caps only, and is checked separately.
ANGLE_KEYS = {
    "id",
    "mechanism",
    "applicable_group_types",
    "sources",
    "cap",
    "cap_rationale",
    "ordering_signal",
    "trigger",
    "precondition",
    "fallback",
    "fallback_rationale",
    "predicate",
    "trigger_anchor",
    "widening_legs",
    "predicate_omits",
    "seed_input",
}
OWED_SIZING = {"a3", "b3", "b7"}


@pytest.fixture(scope="module")
def registry() -> dict:
    return yaml.safe_load(REGISTRY.read_text())


class TestC1TheRegistryFieldSets:
    """C1 — the registry's shape, asserted by a parse and never by reading it."""

    def test_row_and_angle_counts(self, registry: dict) -> None:
        assert len(registry["sources"]) == 32
        assert len(registry["excluded"]) == 7
        assert len(registry["angles"]) == 10

    def test_every_row_carries_exactly_the_ten_fields(self, registry: dict) -> None:
        for row in registry["sources"]:
            assert set(row) == ROW_FIELDS, (
                f"{row['id']}: {sorted(set(row) ^ ROW_FIELDS)}"
            )

    def test_probe_method_is_not_a_per_row_field(self, registry: dict) -> None:
        # §12: the registry carries a top-level `probe_default` and a row may OVERRIDE it.
        # An earlier spec revision demanded `probe_method` on every row, which would have
        # failed against the shape it was copying.
        assert "probe_default" in registry
        assert not [r["id"] for r in registry["sources"] if "probe_method" in r]

    def test_no_row_carries_a_placeholder_url(self, registry: dict) -> None:
        for row in registry["sources"]:
            url = str(row["url"])
            assert "<" not in url and "re-derive" not in url.lower(), (
                f"{row['id']}: {url!r}"
            )

    def test_the_coordinators_unbackticked_admitted_row_has_an_id(
        self, registry: dict
    ) -> None:
        # The coordinator's admitted table carries one row whose first cell is not backticked
        # ("Open engineering-blog long tail"). It is admitted, so this registry must give it an
        # id or the count silently drops to 31.
        assert "open-engineering-blogs" in {r["id"] for r in registry["sources"]}

    def test_every_angle_carries_exactly_the_sixteen_keys(self, registry: dict) -> None:
        for angle in registry["angles"]:
            extra = set(angle) - ANGLE_KEYS - {"sizing_record"}
            assert set(angle) >= ANGLE_KEYS, (
                f"{angle['id']}: missing {sorted(ANGLE_KEYS - set(angle))}"
            )
            assert not extra, f"{angle['id']}: undeclared {sorted(extra)}"

    def test_sizing_record_is_on_exactly_the_three_owed_caps(
        self, registry: dict
    ) -> None:
        carried = {a["id"] for a in registry["angles"] if "sizing_record" in a}
        assert carried == OWED_SIZING

    def test_trigger_holds_the_literal_enum_not_an_expression(
        self, registry: dict
    ) -> None:
        # The shared engine keys off exactly this literal (`trigger_rules.py:197`). A registry
        # written from an earlier §11 revision would have put the EXPRESSION here, making
        # `conditional` false for all seven b-angles and emitting `predicate-only-on-conditional`
        # seven times over.
        for angle in registry["angles"]:
            assert angle["trigger"] in ("always", "conditional"), (
                f"{angle['id']}: {angle['trigger']!r}"
            )

    def test_seed_input_is_a_non_empty_list(self, registry: dict) -> None:
        # 5i's `seed_input` is a scalar string; this type takes a LIST so an angle seeded from
        # two axes can say so, and the divergence is declared in §12.
        for angle in registry["angles"]:
            assert isinstance(angle["seed_input"], list) and angle["seed_input"], angle[
                "id"
            ]

    def test_trigger_anchor_is_non_empty_on_every_conditional_angle(
        self, registry: dict
    ) -> None:
        for angle in registry["angles"]:
            if angle["trigger"] == "conditional":
                assert angle["trigger_anchor"], (
                    f"{angle['id']}: conditional with an empty anchor"
                )
            else:
                # §12: this type follows the FIVE validators that guard on truthiness and accept
                # `[]` on an always-on angle. `regulatory` alone refuses it, and the divergence
                # is declared rather than discovered when its shape is copied.
                assert angle["trigger_anchor"] in ([], None), (
                    f"{angle['id']}: {angle['trigger_anchor']!r}"
                )

    def test_every_anchor_names_a_required_leaf_and_every_widener_an_optional_one(
        self, registry: dict
    ) -> None:
        import json

        schema = json.loads(
            (
                ROOT
                / "skills/project-document-discovery/schemas/capability-map.schema.json"
            ).read_text()
        )["$defs"]
        req, opt = {}, {}
        for name, node in schema.items():
            if not name.endswith("Classification"):
                continue
            sec = name[: -len("Classification")].lower().replace("dataml", "data_ml")
            required = set(node.get("required") or [])
            for leaf in node.get("properties") or {}:
                (req if leaf in required else opt)[f"{sec}.{leaf}"] = True
        for angle in registry["angles"]:
            for anchor in angle["trigger_anchor"] or []:
                root = ".".join(anchor.split(".")[:2])
                assert root in req, (
                    f"{angle['id']}: anchor {anchor!r} is not a REQUIRED leaf"
                )
            for widener in angle["widening_legs"] or []:
                root = ".".join(widener.split(".")[:2])
                assert root in opt, (
                    f"{angle['id']}: widener {widener!r} is not an OPTIONAL field"
                )

    def test_type_trigger_and_coherence_axioms(self, registry: dict) -> None:
        assert set(registry["type_trigger"]) == {"formula", "source", "predicate"}
        # A registry lacking this predicate is SKIPPED by the shared guard, which would leave
        # every angle unchecked while the suite stayed green.
        assert registry["type_trigger"]["predicate"]
        assert registry["coherence_axioms"] == []
        assert registry["coherence_axioms_note"], (
            "an empty block with no reason reads as an omission"
        )


class TestC1aTheFallbackForestWalked:
    """C1a — the forest is WALKED, not described. Discharges EC4."""

    def test_at_least_one_terminal_declares_null(self, registry: dict) -> None:
        # Requiring every row to name a fallback in a finite graph guarantees a cycle by
        # pigeonhole, which is why §12 states the terminal rule rather than leaving it implied.
        assert [r["id"] for r in registry["sources"] if r["fallback"] is None]

    def test_every_terminal_carries_a_rationale(self, registry: dict) -> None:
        for row in registry["sources"]:
            if row["fallback"] is None:
                assert row["fallback_rationale"], (
                    f"{row['id']}: terminal with no rationale"
                )

    def test_zero_dangling(self, registry: dict) -> None:
        ids = {r["id"] for r in registry["sources"]}
        for row in registry["sources"]:
            if row["fallback"] is not None:
                assert row["fallback"] in ids, f"{row['id']} -> {row['fallback']!r}"

    def test_zero_cycles(self, registry: dict) -> None:
        by_id = {r["id"]: r for r in registry["sources"]}
        for row in registry["sources"]:
            seen: list[str] = []
            cur = row["id"]
            while cur is not None:
                assert cur not in seen, (
                    f"CYCLE from {row['id']}: {' -> '.join(seen + [cur])}"
                )
                seen.append(cur)
                cur = by_id[cur]["fallback"]

    def test_every_angle_reference_resolves_to_a_registry_row(
        self, registry: dict
    ) -> None:
        ids = {r["id"] for r in registry["sources"]}
        for angle in registry["angles"]:
            assert angle["fallback"] in ids, (
                f"{angle['id']}: fallback {angle['fallback']!r}"
            )
            for src in angle["sources"]:
                assert src in ids, f"{angle['id']}: source {src!r}"


class TestC1bTheSharedTriggerEngine:
    """C1b — the registry answers the SHARED guard, not a local restatement of it."""

    def test_check_wellformed_returns_zero_findings(self, registry: dict) -> None:
        sys.path.insert(0, str(ROOT / "tests"))
        from trigger_rules import check_wellformed

        findings = check_wellformed(registry)
        assert not findings, [f"{f.severity} {f.rule} @ {f.angle}" for f in findings]

    def test_no_angle_always_fires_is_dead_or_is_undecidable(
        self, registry: dict
    ) -> None:
        """The DEEPER shared checks, run HERE and not only by the root suite.

        `check_wellformed` passed on a registry whose b4 predicated on `archetype.secondary`
        with op `in` — an enum-less array, so `predicate-not-expressible` at severity fail. The
        root suite caught it; this package's own tests did not, which is a package that ships
        green and fails on someone else's run. §11 writes that leg with INTERSECTION, and the
        engine is stricter than the notation: `contains` over an array is admitted as a free
        boolean, `in` is refused.
        """
        sys.path.insert(0, str(ROOT / "tests"))
        from trigger_integrity import load_field_specs
        from trigger_rules import check_angle

        specs = load_field_specs()
        trigger = registry["type_trigger"]["predicate"]
        axioms = registry.get("coherence_axioms") or []
        found = [
            f
            for angle in registry["angles"]
            if angle.get("trigger") == "conditional"
            for f in check_angle(trigger, angle, specs, axioms)
        ]
        assert not found, [
            f"{f.severity} {f.rule} @ {f.angle}: {f.message[:80]}" for f in found
        ]

    def test_the_registry_is_not_skipped_as_out_of_scope(self, registry: dict) -> None:
        # EC11b's clause: a registry with no `type_trigger.predicate` is SKIPPED, so shipping
        # one would leave every angle unchecked while the suite stayed green.
        sys.path.insert(0, str(ROOT / "tests"))
        from trigger_rules import check_wellformed

        assert "registry-out-of-scope" not in {
            f.rule for f in check_wellformed(registry)
        }


SCHEMAS = PKG / "schemas"


def _schema(name: str) -> dict:
    import json

    return json.loads((SCHEMAS / f"{name}.schema.json").read_text())


def _validator(name: str):
    import jsonschema

    return jsonschema.Draft202012Validator(_schema(name))


def _req(node: dict) -> set:
    return set(node.get("required") or [])


class TestC2aTheMapSchema:
    """C2a — the map schema requires §6's shape IN FULL."""

    def test_it_loads(self) -> None:
        _validator("scale-vocabulary-map").check_schema(_schema("scale-vocabulary-map"))

    def test_meta_requires_scope_ref(self) -> None:
        # §14's transcription condition judges the declared band against `scope_ref`; without
        # the path that condition can only record "unjudgeable".
        meta = _schema("scale-vocabulary-map")["properties"]["meta"]
        assert "scope_ref" in _req(meta)

    def test_the_five_band_leaves_are_all_required(self) -> None:
        band = _schema("scale-vocabulary-map")["properties"]["meta"]["properties"][
            "classification"
        ]["properties"]["scale"]
        assert _req(band) == {
            "concurrency",
            "real_time",
            "availability_target",
            "geo_distribution",
            "data_volume",
        }

    def test_groups_require_id_and_type(self) -> None:
        # §7's owed grid selects the applicable groups on their TYPE, and every coverage cell's
        # `group_id` resolves against `id`. Both passed the plan's field check for twenty-six
        # cycles on the English words "type-specific" and "id".
        g = _schema("scale-vocabulary-map")["properties"]["groups"]["items"]
        assert {"id", "type", "canonical", "expansions", "expansion_cap"} <= _req(g)

    def test_the_four_corpus_arrays_and_sources_are_required(self) -> None:
        # All five reached NO task until the plan's field check was rebuilt; `sources` is the
        # block C3b's map-completeness rule reads, and a schema without a key for it would have
        # made that rule raise instead of return a finding.
        req = _req(_schema("scale-vocabulary-map"))
        assert {
            "system_classes",
            "load_dimensions",
            "named_technologies",
            "failure_classes",
            "angle_applicability",
            "sources",
            "notes",
            "assumptions",
        } <= req

    def test_angle_applicability_owes_a_verdict_for_all_ten(self) -> None:
        a = _schema("scale-vocabulary-map")["properties"]["angle_applicability"]
        assert a["minItems"] == 10
        assert _req(a["items"]) == {
            "angle_id",
            "holds",
            "reason",
            "applicable_group_types",
        }

    def test_sources_carries_active_and_skipped(self) -> None:
        s = _schema("scale-vocabulary-map")["properties"]["sources"]
        assert _req(s) == {"active", "skipped"}
        assert _req(s["properties"]["skipped"]["items"]) == {
            "id",
            "cause_class",
            "cause",
        }


class TestC2bTheSearchOutputSchema:
    """C2b — the coverage cell, the two arrays, and the bound."""

    def test_it_loads(self) -> None:
        _validator("search-output").check_schema(_schema("search-output"))

    def test_a_cell_carries_five_identifying_fields_reached_or_not(self) -> None:
        cell = _schema("search-output")["properties"]["coverage"]["items"]
        assert _req(cell) == {"group_id", "source_id", "queries", "timestamp", "status"}

    def test_found_by_is_required_on_BOTH_arrays(self) -> None:
        # `kept` == |candidates citing the cell| + |unadmitted citing the cell|. Without
        # `found_by` on candidates the first term is not computable and the rule gets written to
        # fit the weakness instead of the contract, which is how 5j got it wrong.
        s = _schema("search-output")["properties"]
        assert "found_by" in _req(s["candidates"]["items"])
        assert "found_by" in _req(s["unadmitted"]["items"])

    def test_admission_conjuncts_are_structural(self) -> None:
        # L-7: a resolvable URL AND a stated version or date. The dating conjunct is this type's
        # and is sharper here than for any sibling.
        cand = _req(_schema("search-output")["properties"]["candidates"]["items"])
        assert {"url", "stated_date"} <= cand

    def test_reason_class_carries_its_five_members(self) -> None:
        rc = _schema("search-output")["properties"]["unadmitted"]["items"][
            "properties"
        ]["reason_class"]
        assert set(rc["enum"]) == {
            "no-resolvable-url",
            "no-stated-date",
            "out-of-scope-for-this-angle",
            "duplicate-of",
            "superseded",
        }

    def test_bound_carries_all_five_keys(self) -> None:
        b = _schema("search-output")["properties"]["bound"]
        assert _req(b) == {
            "cap",
            "hit",
            "ordering",
            "dropped_note",
            "ordering_deviation",
        }


class TestC2cTheExtractSchema:
    """C2c — both LEVELS, and the ENVELOPE."""

    def test_it_loads(self) -> None:
        _validator("extract-output").check_schema(_schema("extract-output"))

    def test_the_envelope(self) -> None:
        # This requirement sat BELOW C2c's first non-Exit bullet for four plan revisions, so the
        # scope every check reads ended above it and `schema_version` and `outcome` were bound by
        # no task at all.
        s = _schema("extract-output")
        assert _req(s) == {"schema_version", "meta", "outcome"}
        assert _req(s["properties"]["meta"]) == {
            "source_id",
            "id_class",
            "as_of",
            "revision",
        }

    def test_a_skipped_record_carries_skipped_and_nothing_else(self) -> None:
        branch = _schema("extract-output")["allOf"][0]["then"]
        assert "skipped" in _req(branch)
        forbidden = {tuple(sorted(x["required"])) for x in branch["not"]["anyOf"]}
        assert {("source",), ("episodes",)} <= forbidden

    def test_an_extracted_record_owes_at_least_one_episode(self) -> None:
        s = _schema("extract-output")
        assert s["properties"]["episodes"]["minItems"] == 1
        assert {"source", "episodes"} <= _req(s["allOf"][0]["else"])

    def test_no_stated_load_is_not_a_bail_cause(self) -> None:
        causes = _schema("extract-output")["properties"]["skipped"]["properties"][
            "cause"
        ]["enum"]
        assert set(causes) == {
            "concerns-none-of-the-scope",
            "source-unreachable",
            "forbidden-by-terms",
        }
        assert "no-stated-load" not in causes

    def test_outcome_kind_and_cause_class_are_CLOSED_enums(self) -> None:
        # Open strings would gate `outcome_kind: banana` at exit 0.
        ep = _schema("extract-output")["properties"]["episodes"]["items"]["properties"]
        assert set(ep["outcome_kind"]["enum"]) == {
            "adopted",
            "regression",
            "incident",
            "limit",
            "rejected",
        }
        inner = [b for b in ep["cause_class"]["anyOf"] if b.get("type") == "string"][0]
        assert "saturation" in inner["enum"] and "banana" not in inner["enum"]

    def test_license_and_score_are_on_the_SOURCE_not_the_episode(self) -> None:
        # An earlier spec revision listed `license` per EPISODE; a licence is a property of the
        # document, not of a claim inside it.
        s = _schema("extract-output")["properties"]
        assert {"license", "score"} <= _req(s["source"])
        assert not ({"license", "score"} & _req(s["episodes"]["items"]))

    def test_evidence_class_is_on_the_EPISODE_not_the_source(self) -> None:
        # Coordinator L-5, corrected after cold review: one post routinely carries a measured
        # episode beside a narrative aside, and recording it once per source would force the
        # producer to mis-score one of them.
        s = _schema("extract-output")["properties"]
        assert "evidence_class" in _req(s["episodes"]["items"])
        assert "evidence_class" not in _req(s["source"])

    def test_load_class_sub_keys_are_all_nullable(self) -> None:
        # Sources routinely state one or two dimensions and say nothing about the rest. That
        # nullability is what keeps the last two branches of the `confidence` derivation
        # reachable in both directions.
        lc = _schema("extract-output")["properties"]["episodes"]["items"]["properties"][
            "load_class"
        ]
        for leaf, node in lc["properties"].items():
            assert {"type": "null"} in node["anyOf"], leaf

    def test_transferability_owes_a_reason_of_twenty_characters(self) -> None:
        t = _schema("extract-output")["properties"]["episodes"]["items"]["properties"][
            "transferability"
        ]
        assert t["properties"]["reason"]["minLength"] == 20


class TestC2dTheEnvelopeIndexSchema:
    """C2d — §9's index shape, and `lineage` DECLARED so its rule has a key to read."""

    def test_it_loads(self) -> None:
        _validator("scale-envelope-index").check_schema(_schema("scale-envelope-index"))

    def test_an_area_requires_evidence_and_confidence(self) -> None:
        a = _schema("scale-envelope-index")["properties"]["areas"]["items"]
        assert {"area", "default_pattern", "evidence", "confidence"} <= _req(a)
        assert a["properties"]["evidence"]["minItems"] == 1

    def test_the_index_carries_ninths_shape_in_full(self) -> None:
        a = _schema("scale-envelope-index")["properties"]["areas"]["items"]
        assert {
            "hard_limits",
            "failure_modes",
            "migration_trigger",
            "open_gap",
        } <= _req(a)

    def test_hard_limits_carries_its_declared_members(self) -> None:
        # `adjustable` was declared in §9's SECOND table cell and required by nothing until the
        # plan's field derivation learned to read that cell.
        h = _schema("scale-envelope-index")["properties"]["areas"]["items"][
            "properties"
        ]["hard_limits"]
        assert _req(h["items"]) == {
            "limit",
            "source",
            "adjustable",
            "blocks_requirement",
        }

    def test_migration_trigger_names_which_band_axis(self) -> None:
        m = _schema("scale-envelope-index")["properties"]["areas"]["items"][
            "properties"
        ]["migration_trigger"]
        inner = [b for b in m["anyOf"] if b.get("type") == "object"][0]
        assert _req(inner) == {"trigger", "dimension", "evidence"}
        assert set(inner["properties"]["dimension"]["enum"]) == {
            "concurrency",
            "real_time",
            "availability_target",
            "geo_distribution",
            "data_volume",
        }

    def test_lineage_extends_is_DECLARED(self) -> None:
        # The half that reverted silently when a fix landed only on the validator side. It is
        # why `lineage` shipped dead in two packages.
        s = _schema("scale-envelope-index")
        assert "lineage" in _req(s)
        assert "extends" in _req(s["properties"]["lineage"])

    def test_project_band_carries_the_same_five_leaves_as_the_map(self) -> None:
        assert _req(_schema("scale-envelope-index")["properties"]["project_band"]) == {
            "concurrency",
            "real_time",
            "availability_target",
            "geo_distribution",
            "data_volume",
        }


FIXTURES = HERE / "fixtures"
sys.path.insert(0, str(HERE))

import copy  # noqa: E402
import re  # noqa: E402

import validate_scale_prior_art as V  # noqa: E402


def _emitted_ids(tree) -> set:
    """Every rule id the validator can emit, in BOTH call shapes.

    A positional `_fail(f, "id", ...)`, and a `rule=` keyword threaded through a helper that
    calls `_fail` itself. `registry-unreadable` reaches `_fail` only the second way, so a
    positional-only walk reported 42 of 43 — and the rule-owner map built from that walk was
    short by exactly the id nothing else in the package names.
    """
    import ast as _ast

    out: set = set()
    for node in _ast.walk(tree):
        if not isinstance(node, _ast.Call):
            continue
        if getattr(node.func, "id", "") == "_fail" and node.args:
            if isinstance(node.args[0], _ast.Constant):
                out.add(node.args[0].value)
        for kw in node.keywords:
            if kw.arg == "rule" and isinstance(kw.value, _ast.Constant):
                out.add(kw.value.value)
    return out


class _RuleSet(set):
    """A finding set whose `in` matches a FAMILY prefix as well as an exact id.

    The emitted ids are per-CLAUSE (`map-completeness-4b`), because a composite id cannot say
    which clause a task owns. A test asserting the FAMILY fired stays readable this way, and a
    test naming an exact clause still works.
    """

    def __contains__(self, item: object) -> bool:
        def matches(rule: str) -> bool:
            if rule == item:
                return True
            if rule.startswith(f"{item}-"):
                return True
            # A SUB-clause suffix: §13 numbers `vocabularies (5a)` and `(5b)` under one clause,
            # so `angle-block-1` must match `angle-block-1a` without also matching a different
            # clause number.
            tail = rule[len(str(item)) :]
            return rule.startswith(str(item)) and tail.isalpha() and len(tail) <= 2

        return any(matches(r) for r in self)


def _rules(fn, *args) -> _RuleSet:
    f = V.Findings()
    fn(*args, f)
    return _RuleSet(r for r, _ in f.items)


@pytest.fixture(scope="module")
def clean_map() -> dict:
    return yaml.safe_load((FIXTURES / "scale-vocabulary-map.valid.yaml").read_text())


@pytest.fixture(scope="module")
def clean_search() -> dict:
    return yaml.safe_load((FIXTURES / "search-output-b5.valid.yaml").read_text())


@pytest.fixture(scope="module")
def clean_extract() -> dict:
    return yaml.safe_load((FIXTURES / "extract-output.valid.yaml").read_text())


@pytest.fixture(scope="module")
def clean_index() -> dict:
    return yaml.safe_load((FIXTURES / "scale-envelope-index.valid.yaml").read_text())


class TestC8TheCleanFixturesGateAtZero:
    """C8 — all four gate at exit 0. Discharges EC1 and EC17."""

    @pytest.mark.parametrize(
        "argv",
        [
            ["keyword-map", "scale-vocabulary-map.valid.yaml"],
            [
                "search",
                "search-output-b5.valid.yaml",
                "--keyword-map",
                "scale-vocabulary-map.valid.yaml",
            ],
            ["extract", "extract-output.valid.yaml"],
            ["synthesis", "scale-envelope-index.valid.yaml", "--extracts", "extracts"],
        ],
    )
    def test_each_kind_gates_clean(self, argv: list[str]) -> None:
        argv = [
            a
            if a.startswith("-")
            else str(FIXTURES / a)
            if "." in a or a == "extracts"
            else a
            for a in argv
        ]
        assert V.main(argv) == 0

    def test_the_scope_fires_exactly_one_conditional_angle(
        self, clean_map: dict
    ) -> None:
        # Spec §3's binding: the coordinator's 4-child dummy scope, a local log-analysis CLI over
        # large datasets firing `data_volume: large`. 3 always-on + 1 conditional = 4, the floor.
        holds = {v["angle_id"] for v in clean_map["angle_applicability"] if v["holds"]}
        assert holds == {"a1", "a2", "a3", "b5"}
        assert clean_map["meta"]["classification"]["scale"]["data_volume"] == "large"


class TestC3aRegistryAndAngleBlocks:
    """C3a — every rule fires on a planted registry defect, enumerated."""

    @pytest.mark.parametrize(
        ("rule", "mutate"),
        [
            ("registry-integrity", lambda r: r["sources"][0].pop("url")),
            (
                "registry-integrity-2",
                lambda r: r["sources"][0].update(authority_band="gossip"),
            ),
            (
                "registry-integrity-3",
                lambda r: r["sources"][0].update(access_status="maybe"),
            ),
            ("registry-integrity-4", lambda r: r["sources"][0].update(yields=None)),
            ("registry-integrity-8", lambda r: r["sources"][0].update(as_of="")),
            (
                "registry-integrity-7",
                lambda r: r["sources"][0].update(probe_method="GET"),
            ),
            (
                "fallback-unresolvable",
                lambda r: r["sources"][0].update(fallback="ghost"),
            ),
            (
                "angle-block-1",
                lambda r: [
                    a.update(predicate=None) for a in r["angles"] if a["id"] == "b5"
                ],
            ),
            (
                "angle-block-2",
                lambda r: [
                    a.update(trigger_anchor=[]) for a in r["angles"] if a["id"] == "b5"
                ],
            ),
            (
                "angle-block-3",
                lambda r: [
                    a.update(widening_legs=["scale.data_volume"])
                    for a in r["angles"]
                    if a["id"] == "b5"
                ],
            ),
            (
                "angle-block-4",
                lambda r: [
                    a.update(seed_input="named-technology")
                    for a in r["angles"]
                    if a["id"] == "b5"
                ],
            ),
            (
                "angle-block-5",
                lambda r: [
                    a.pop("predicate_omits") for a in r["angles"] if a["id"] == "b5"
                ],
            ),
            (
                "angle-block-6",
                lambda r: [
                    a.update(sizing_record={"sizing_class": "budget-floor"})
                    for a in r["angles"]
                    if a["id"] == "b1"
                ],
            ),
        ],
    )
    def test_each_rule_fires(self, registry: dict, rule: str, mutate) -> None:
        planted = copy.deepcopy(registry)
        mutate(planted)
        assert rule in _rules(V.check_registry, planted)

    def test_a_terminal_with_no_rationale_fires(self, registry: dict) -> None:
        planted = copy.deepcopy(registry)
        for row in planted["sources"]:
            if row["fallback"] is None:
                row["fallback_rationale"] = ""
                break
        assert "registry-integrity-6" in _rules(V.check_registry, planted)

    def test_a_cycle_fires(self, registry: dict) -> None:
        planted = copy.deepcopy(registry)
        for row in planted["sources"]:
            if row["id"] == "semantic-scholar":
                row["fallback"] = "crossref"
        assert "fallback-cycle" in _rules(V.check_registry, planted)

    def test_the_clean_registry_fires_nothing(self, registry: dict) -> None:
        assert not _rules(V.check_registry, registry)


class TestC3bTheMapRules:
    """C3b — map completeness (1)-(6) and the declared band, both sides."""

    @pytest.mark.parametrize(
        "mutate",
        [
            lambda m: m["sources"]["active"].pop(),
            lambda m: m["sources"]["skipped"][0].update(cause_class="whatever"),
            lambda m: m["sources"]["skipped"][0].update(cause=""),
            lambda m: m["sources"]["skipped"][0].update(
                sanitization={"status": "clean", "cause": None}
            ),
            lambda m: m["sources"]["active"][0].pop("as_of"),
            lambda m: m["scope_guard"]["shared_terms"][0].update(owner=""),
            lambda m: m["angle_applicability"].pop(),
            lambda m: [
                v.update(holds=False, reason="no")
                for v in m["angle_applicability"]
                if v["angle_id"] == "a1"
            ],
            lambda m: [
                v.update(reason="it does not apply")
                for v in m["angle_applicability"]
                if v["angle_id"] == "b1"
            ],
            lambda m: m["groups"].clear(),
        ],
    )
    def test_map_completeness_fires(
        self, clean_map: dict, registry: dict, mutate
    ) -> None:
        planted = copy.deepcopy(clean_map)
        mutate(planted)
        assert "map-completeness" in _rules(V.check_map, planted, registry)

    def test_an_always_on_angle_refused_names_the_contract(
        self, clean_map: dict, registry: dict
    ) -> None:
        planted = copy.deepcopy(clean_map)
        for v in planted["angle_applicability"]:
            if v["angle_id"] == "a2":
                v["holds"] = False
        f = V.Findings()
        V.check_map(planted, registry, f)
        assert any("contradicts the contract" in m for _, m in f.items)

    @pytest.mark.parametrize("path", ["meta.classification.scale", "project_band"])
    def test_the_band_fires_on_both_artifacts(self, path: str) -> None:
        # §13's declared-band family names BOTH sides; the index side otherwise reaches the
        # validator nowhere, leaving C7c's map-index equality with an unvalidated operand.
        assert "declared-band" in _rules(V.check_band, {}, path)

    def test_a_missing_band_leaf_fires(self, clean_map: dict, registry: dict) -> None:
        planted = copy.deepcopy(clean_map)
        planted["meta"]["classification"]["scale"].pop("geo_distribution")
        assert "declared-band" in _rules(V.check_map, planted, registry)

    def test_the_clean_map_fires_nothing(self, clean_map: dict, registry: dict) -> None:
        assert not _rules(V.check_map, clean_map, registry)


class TestC3sTheSanitizationFamily:
    """C3s — the CELL half. The subject is the CELL, never the map row it cites."""

    def test_a_reached_cell_with_no_posture_fires(self, clean_search: dict) -> None:
        planted = copy.deepcopy(clean_search)
        next(c for c in planted["coverage"] if c["status"] == "reached").pop(
            "sanitization"
        )
        assert "sanitization" in _rules(V.check_cell_sanitization, planted)

    def test_modified_owes_a_cause(self, clean_search: dict) -> None:
        planted = copy.deepcopy(clean_search)
        next(c for c in planted["coverage"] if c["status"] == "reached")[
            "sanitization"
        ] = {
            "status": "modified",
            "cause": None,
        }
        assert "sanitization" in _rules(V.check_cell_sanitization, planted)

    def test_a_reached_cells_own_status_is_never_not_fetched(
        self, clean_search: dict
    ) -> None:
        planted = copy.deepcopy(clean_search)
        next(c for c in planted["coverage"] if c["status"] == "reached")[
            "sanitization"
        ] = {
            "status": "not-fetched",
            "cause": None,
        }
        f = V.Findings()
        V.check_cell_sanitization(planted, f)
        assert any("the CELL, not the map row" in m for _, m in f.items)

    def test_the_clean_search_fires_nothing(self, clean_search: dict) -> None:
        assert not _rules(V.check_cell_sanitization, clean_search)


class TestC3cCoverageAdmissionAndBound:
    """C3c — the three families, all clauses."""

    def test_a_missing_owed_cell_fires(self, clean_search, registry, clean_map) -> None:
        planted = copy.deepcopy(clean_search)
        planted["coverage"].pop()
        assert "coverage-grid" in _rules(V.check_search, planted, registry, clean_map)

    def test_a_cell_outside_the_three_terms_fires(
        self, clean_search, registry, clean_map
    ) -> None:
        # Dropping any one of the three derivation terms is wrong in a measurable way.
        planted = copy.deepcopy(clean_search)
        planted["coverage"].append(
            {
                "group_id": "g-sys-batch",
                "source_id": "crossref",
                "queries": ["x"],
                "timestamp": "2026-09-05T10:00:00Z",
                "status": "refused",
                "cause": "n/a",
            }
        )
        assert "coverage-grid" in _rules(V.check_search, planted, registry, clean_map)

    def test_a_reached_cell_with_no_counts_fires(
        self, clean_search, registry, clean_map
    ) -> None:
        planted = copy.deepcopy(clean_search)
        next(c for c in planted["coverage"] if c["status"] == "reached").pop("kept")
        assert "coverage-grid" in _rules(V.check_search, planted, registry, clean_map)

    def test_a_nonzero_returned_owes_a_count_frame(
        self, clean_search, registry, clean_map
    ) -> None:
        planted = copy.deepcopy(clean_search)
        next(c for c in planted["coverage"] if c.get("returned")).pop("count_frame")
        assert "coverage-grid" in _rules(V.check_search, planted, registry, clean_map)

    def test_an_unreached_cell_recording_a_count_fires(
        self, clean_search, registry, clean_map
    ) -> None:
        # A zero and an absence are different claims and the grid must keep them apart.
        planted = copy.deepcopy(clean_search)
        cell = next(c for c in planted["coverage"] if c["status"] != "reached")
        cell["returned"] = 0
        f = V.Findings()
        V.check_search(planted, registry, clean_map, f)
        assert any("different claims" in m for _, m in f.items)

    def test_an_unreached_cell_with_no_cause_fires(
        self, clean_search, registry, clean_map
    ) -> None:
        planted = copy.deepcopy(clean_search)
        next(c for c in planted["coverage"] if c["status"] != "reached").pop("cause")
        assert "coverage-grid" in _rules(V.check_search, planted, registry, clean_map)

    @pytest.mark.parametrize("field", ["url", "stated_date", "found_by"])
    def test_admission_fires_on_each_conjunct(
        self, clean_search, registry, clean_map, field
    ) -> None:
        planted = copy.deepcopy(clean_search)
        planted["candidates"][0].pop(field)
        assert "admission" in _rules(V.check_search, planted, registry, clean_map)

    def test_kept_must_equal_the_rows_citing_the_cell(
        self, clean_search, registry, clean_map
    ) -> None:
        planted = copy.deepcopy(clean_search)
        next(c for c in planted["coverage"] if c.get("kept"))["kept"] = 9
        assert "admission" in _rules(V.check_search, planted, registry, clean_map)

    def test_a_cap_disagreeing_with_the_registry_fires(
        self, clean_search, registry, clean_map
    ) -> None:
        # What stops an author widening their own cap.
        planted = copy.deepcopy(clean_search)
        planted["bound"]["cap"] = 999
        assert "bound" in _rules(V.check_search, planted, registry, clean_map)

    def test_hit_true_owes_a_re_appliable_dropped_note(
        self, clean_search, registry, clean_map
    ) -> None:
        planted = copy.deepcopy(clean_search)
        planted["bound"]["hit"] = True
        planted["bound"]["dropped_note"] = "the rest were dropped"
        f = V.Findings()
        V.check_search(planted, registry, clean_map, f)
        assert any("not re-appliable" in m for _, m in f.items)

    def test_a_deviating_ordering_owes_a_deviation(
        self, clean_search, registry, clean_map
    ) -> None:
        planted = copy.deepcopy(clean_search)
        planted["bound"]["ordering"] = "alphabetical"
        assert "bound" in _rules(V.check_search, planted, registry, clean_map)

    def test_the_clean_search_fires_nothing(
        self, clean_search, registry, clean_map
    ) -> None:
        assert not _rules(V.check_search, clean_search, registry, clean_map)


class TestC3dTheOrderingIsAppliableAndTotal:
    """C3d — over ALL TEN angles, never the subset that already satisfies it. Discharges EC18."""

    @staticmethod
    def _appliable(reg: dict) -> list[str]:
        """bound (4) NOT-A-RULE — a property of the REGISTRY, asserted here and not emitted.

        The validator does not carry it: an artifact author cannot repair a registry whose
        ordering signal is not total, and attributing a runtime rule to a task that authors none
        is what the rule-owner map refuses.
        """
        by_id = {r["id"]: r for r in reg["sources"]}
        bad = []
        for angle in reg["angles"]:
            signal = (angle.get("ordering_signal") or "").strip()
            if not signal:
                bad.append(f"{angle['id']}: no signal")
                continue
            if "," not in signal and " then " not in signal.lower():
                bad.append(f"{angle['id']}: no tie-break, so not total")
            if not [s for s in angle.get("sources") or [] if s in by_id]:
                bad.append(f"{angle['id']}: walks no registry source")
            if not re.search(r"every|all|each|both", signal, re.I):
                bad.append(f"{angle['id']}: not appliable across every source it walks")
        return bad

    def test_the_shipped_registry_passes(self, registry: dict) -> None:
        assert not self._appliable(registry)

    @pytest.mark.parametrize(
        ("shape", "mutate"),
        [
            ("no signal at all", lambda a: a.update(ordering_signal="")),
            (
                "no tie-break, so not total",
                lambda a: a.update(ordering_signal="recency"),
            ),
            (
                "not appliable across every source",
                lambda a: a.update(ordering_signal="citation count, then date"),
            ),
            ("walks no registry source", lambda a: a.update(sources=["ghost"])),
        ],
    )
    def test_each_of_the_four_shapes_fires(
        self, registry: dict, shape: str, mutate
    ) -> None:
        planted = copy.deepcopy(registry)
        mutate(planted["angles"][0])
        assert self._appliable(planted), shape

    def test_the_guard_covers_every_angle_not_a_subset(self, registry: dict) -> None:
        # A guard authored over a partial population passes vacuously.
        for index in range(len(registry["angles"])):
            planted = copy.deepcopy(registry)
            planted["angles"][index]["ordering_signal"] = "recency"
            assert self._appliable(planted), index


class TestC3eVocabularies:
    """C3e — every clause, with the LEVEL stated per field."""

    @pytest.mark.parametrize(
        ("what", "mutate"),
        [
            ("signal", lambda d: d["episodes"][0].update(signal="throughput")),
            (
                "load_class sub-key",
                lambda d: d["episodes"][0]["load_class"].update(latency="x"),
            ),
            (
                "consistency_model",
                lambda d: d["episodes"][0].update(consistency_model="eventual-ish"),
            ),
            ("technology", lambda d: d["episodes"][0].update(technology="duckdb")),
            (
                "evidence_class",
                lambda d: d["episodes"][0].update(evidence_class="blog-post"),
            ),
            (
                "episode cause_class",
                lambda d: d["episodes"][0].update(cause_class="refused"),
            ),
            ("pattern", lambda d: d["episodes"][0].update(pattern="")),
            (
                "source license",
                lambda d: d["source"].update(license="Creative Commons, sort of"),
            ),
            (
                "source access_status",
                lambda d: d["source"].update(access_status="fine"),
            ),
        ],
    )
    def test_each_clause_fires(self, clean_extract: dict, what: str, mutate) -> None:
        planted = copy.deepcopy(clean_extract)
        mutate(planted)
        assert "vocabularies" in _rules(V.check_extract, planted), what

    def test_the_episodes_cause_class_is_disjoint_from_the_maps(
        self, clean_extract: dict
    ) -> None:
        # Two levels, two vocabularies, one name. `refused` is a MAP skipped-row cause_class and
        # is not an episode failure mode.
        assert set(V.EPISODE_CAUSE_CLASSES).isdisjoint(V.SKIP_CAUSE_CLASSES)

    def test_the_clean_extract_fires_nothing(self, clean_extract: dict) -> None:
        assert not _rules(V.check_extract, clean_extract)


class TestC3wTheBailFamily:
    def test_a_skipped_record_carrying_anything_else_fires(self) -> None:
        doc = {
            "outcome": "skipped",
            "skipped": {"cause": "source-unreachable", "detail": "404", "extra": 1},
        }
        assert "bail" in _rules(V.check_extract, doc)

    def test_a_cause_outside_the_three_fires(self) -> None:
        doc = {
            "outcome": "skipped",
            "skipped": {"cause": "not-interesting", "detail": "x"},
        }
        assert "bail" in _rules(V.check_extract, doc)

    def test_no_stated_load_is_refused_as_a_cause(self) -> None:
        # It would delete the operational canon and every negative result — a promotion cut
        # wearing a relevance bail's clothes.
        doc = {
            "outcome": "skipped",
            "skipped": {"cause": "no-stated-load", "detail": "x"},
        }
        f = V.Findings()
        V.check_extract(doc, f)
        assert any("promotion cut" in m for _, m in f.items)

    def test_a_well_formed_bail_fires_nothing(self) -> None:
        doc = {
            "outcome": "skipped",
            "skipped": {
                "cause": "source-unreachable",
                "detail": "HTTP 404 on 2026-09-05",
            },
        }
        assert not _rules(V.check_extract, doc)


class TestC3xBodySectionsAndPrimaryDimension:
    """C3x — presence and NON-TRIVIALITY only, never prose quality. Discharges EC21."""

    def test_the_clean_body_passes(self) -> None:
        assert not _rules(
            V.check_body_sections, (FIXTURES / "extract-output.valid.md").read_text()
        )

    @pytest.mark.parametrize("heading", V.BODY_SECTIONS)
    def test_a_missing_section_fires(self, heading: str) -> None:
        text = (
            (FIXTURES / "extract-output.valid.md")
            .read_text()
            .replace(heading, "## Something")
        )
        assert "body-sections" in _rules(V.check_body_sections, text)

    def test_a_present_but_trivial_section_fires(self) -> None:
        text = (FIXTURES / "extract-output.valid.md").read_text()
        head, rest = text.split("## Transferability", 1)
        assert "body-sections" in _rules(
            V.check_body_sections, head + "## Transferability\n\nTBD.\n"
        )

    def test_primary_dimension_must_be_one_of_the_five(
        self, clean_extract: dict
    ) -> None:
        planted = copy.deepcopy(clean_extract)
        planted["episodes"][0]["primary_dimension"] = "throughput"
        assert "primary-dimension" in _rules(V.check_extract, planted)


class TestC3rTransferability:
    """C3r — presence, level and reason. Absent, out-of-enum and too-short each refused."""

    @pytest.mark.parametrize(
        "mutate",
        [
            lambda d: d["episodes"][0].pop("transferability"),
            lambda d: d["episodes"][0]["transferability"].update(level="unknown"),
            lambda d: d["episodes"][0]["transferability"].update(reason="short"),
        ],
    )
    def test_each_shape_fires(self, clean_extract: dict, mutate) -> None:
        planted = copy.deepcopy(clean_extract)
        mutate(planted)
        assert "transferability" in _rules(V.check_extract, planted)


class TestC3pMeasuredCoherence:
    """C3p — all three travel together or none does, refused in each direction."""

    @pytest.mark.parametrize(
        "mutate",
        [
            lambda d: d["episodes"][0].update(measured_value=None),
            lambda d: d["episodes"][0].update(measured_unit=None),
            lambda d: d["episodes"][0].update(measured_value=None, measured_unit=None),
        ],
    )
    def test_magnitude_without_its_companions_fires(
        self, clean_extract: dict, mutate
    ) -> None:
        planted = copy.deepcopy(clean_extract)
        mutate(planted)
        assert "measured-coherence" in _rules(V.check_extract, planted)

    def test_all_three_absent_together_is_clean(self, clean_extract: dict) -> None:
        planted = copy.deepcopy(clean_extract)
        planted["episodes"][0].update(
            measured_value=None, measured_magnitude=None, measured_unit=None
        )
        assert "measured-coherence" not in _rules(V.check_extract, planted)


class TestC3jIdGrammarAndRecordFilename:
    """C3j — id grammar (1)-(3) and BOTH parts of #42. Discharges EC3 and EC23."""

    def test_the_clean_record_fires_nothing(self, clean_extract: dict) -> None:
        assert not _rules(V.check_ids, clean_extract)

    @pytest.mark.parametrize(
        "mutate",
        [
            lambda d: d["meta"].update(id_class="url"),
            lambda d: d["episodes"][0].update(id="techempower-run-3-e1"),
            lambda d: d["episodes"][0].update(id="other-source#e1"),
        ],
    )
    def test_id_grammar_fires(self, clean_extract: dict, mutate) -> None:
        planted = copy.deepcopy(clean_extract)
        mutate(planted)
        assert "id-grammar" in _rules(V.check_ids, planted)

    def test_an_episode_id_is_never_a_filename(self) -> None:
        # `<source-id>#e<N>` carries a `#`; the FILE is named from the SOURCE id.
        assert "#" not in V.record_filename("techempower-run-3")

    def test_part_a_two_ids_the_sanitizer_collapses_get_different_names(self) -> None:
        a, b = "WEB-example.invalid/a b", "WEB-example.invalid/a-b"
        assert V.record_filename(a) != V.record_filename(b)

    def test_part_b_the_identity_branch_refuses_a_hashed_stem(self) -> None:
        # A within-branch round-trip passes while the collision exists; that is precisely the
        # false assurance #42 records.
        x = "abc--0123456789ab"
        assert V.record_filename(x) != x
        assert V.record_filename(V.record_filename(x)) != V.record_filename(x)

    def test_the_cross_branch_collision_is_unconstructible(self) -> None:
        for x in (
            "plain-id",
            "DOI-10.1145/3477132",
            "WEB-h.invalid/p q",
            "abc--0123456789ab",
            "x" * 200,
            "///",
            "a b--0123456789ab",
        ):
            fx = V.record_filename(x)
            assert not (V.record_filename(fx) == fx and fx != x), x

    def test_the_spawn_key_and_the_filename_come_from_ONE_function(self) -> None:
        # `validate_spawn` imposes no charset rule on `key`, so nothing else would catch a
        # divergence: a key sanitized one way and a filename another produces a row that looks
        # correct and points at a file nobody wrote.
        source = (HERE / "validate_scale_prior_art.py").read_text()
        assert source.count("def record_filename(") == 1


class TestC3kTheScoreRule:
    """C3k — presence and range only. The quality filter RANKS; it never cuts."""

    def test_the_clean_record_carries_a_score(self, clean_extract: dict) -> None:
        assert not _rules(V.check_score, clean_extract)

    @pytest.mark.parametrize("score", [None, -1, 11, "8", 8.5, True])
    def test_absent_or_out_of_range_fires(self, clean_extract: dict, score) -> None:
        planted = copy.deepcopy(clean_extract)
        if score is None:
            planted["source"].pop("score")
        else:
            planted["source"]["score"] = score
        assert "quality-filter" in _rules(V.check_score, planted)


class TestC3iTheSynthesisRules:
    """C3i — evidence resolves, confidence is the WEAKEST class, every claim carries evidence."""

    def test_the_clean_index_fires_nothing(self, clean_index: dict) -> None:
        extracts = [
            yaml.safe_load(p.read_text())
            for p in sorted((FIXTURES / "extracts").glob("*.yaml"))
        ]
        assert not _rules(V.check_synthesis, clean_index, extracts)

    def test_an_unresolvable_evidence_id_fires(self, clean_index: dict) -> None:
        planted = copy.deepcopy(clean_index)
        planted["areas"][0]["evidence"] = ["ghost#e9"]
        assert "synthesis" in _rules(V.check_synthesis, planted, [])

    def test_confidence_is_the_WEAKEST_backing_class_never_an_average(
        self, clean_index
    ) -> None:
        extracts = [
            yaml.safe_load(p.read_text())
            for p in sorted((FIXTURES / "extracts").glob("*.yaml"))
        ]
        planted = copy.deepcopy(clean_index)
        planted["areas"][0]["confidence"] = (
            "high"  # the average of high + moderate rounds up
        )
        f = V.Findings()
        V.check_synthesis(planted, extracts, f)
        assert any("WEAKEST" in m for _, m in f.items)

    def test_a_migration_trigger_with_no_evidence_fires(
        self, clean_index: dict
    ) -> None:
        planted = copy.deepcopy(clean_index)
        planted["areas"][0]["migration_trigger"]["evidence"] = []
        assert "synthesis" in _rules(V.check_synthesis, planted, None)

    def test_a_failure_mode_with_no_evidence_fires(self, clean_index: dict) -> None:
        planted = copy.deepcopy(clean_index)
        planted["areas"][0]["failure_modes"][0]["evidence"] = []
        assert "synthesis" in _rules(V.check_synthesis, planted, None)

    def test_delta_mode_reads_lineage_extends(self, clean_index: dict) -> None:
        # The READER `lineage` never had. It is why the field shipped dead in two packages.
        planted = copy.deepcopy(clean_index)
        planted["mode"] = "delta"
        assert "lineage-liveness" in _rules(V.check_synthesis, planted, None)


class TestC3vTheSchemaFamily:
    """C3v — each kind against ITS OWN schema, and the two schema rules' exit classes."""

    def test_a_kind_checked_against_another_kinds_schema_fails(
        self, clean_search: dict
    ) -> None:
        assert "schema" in _rules(V.check_schema, clean_search, "extract-output")

    def test_each_clean_artifact_validates_against_its_own(
        self, clean_map, clean_search, clean_extract, clean_index
    ) -> None:
        for doc, name in (
            (clean_map, "scale-vocabulary-map"),
            (clean_search, "search-output"),
            (clean_extract, "extract-output"),
            (clean_index, "scale-envelope-index"),
        ):
            assert not _rules(V.check_schema, doc, name), name

    def test_an_unloadable_schema_FILE_is_a_package_fault(self) -> None:
        assert "schema-unavailable" in _rules(V.load_schema, "no-such-kind")

    def test_an_unreadable_input_FILE_is_an_input_fault(self, tmp_path) -> None:
        assert "input" in _rules(V.load_yaml, tmp_path / "absent.yaml")


class TestC3uTheExitContract:
    """C3u — the split tested PER RULE, never in aggregate. Discharges EC2."""

    def test_schema_is_exit_1_and_schema_unavailable_is_exit_2(self) -> None:
        # An artifact failing a schema that LOADED is exactly what its author can repair; an
        # unloadable schema FILE is a package fault.
        assert not V.is_package_fault("schema")
        assert V.is_package_fault("schema-unavailable")

    def test_the_four_exit_classes(self) -> None:
        # EC2 names FOUR: package faults, schema-unavailable, dependency-missing and the
        # input-class faults. An earlier plan revision named three and routed input-class faults
        # into "everything else", i.e. exit 1.
        for rule in (
            "dependency-missing",
            "input-1",
            "schema-unavailable",
            "registry-integrity-1",
        ):
            assert V.is_package_fault(rule), rule

    @pytest.mark.parametrize(
        "rule",
        [
            "registry-integrity-1",
            "registry-integrity-5a",
            "angle-block-3",
            "fallback-cycle",
            "schema-unavailable",
            "dependency-missing",
            "input-2",
            "thresholds-unreadable",
        ],
    )
    def test_every_package_fault_rule_exits_2(self, rule: str) -> None:
        f = V.Findings()
        f.fail(rule, "planted")
        assert f.exit_code() == 2

    @pytest.mark.parametrize(
        "rule",
        [
            "schema",
            "map-completeness",
            "coverage-grid",
            "admission",
            "bound",
            "sanitization",
            "vocabularies",
            "bail",
            "body-sections",
            "transferability",
            "measured-coherence",
            "synthesis",
            "id-grammar",
            "record-filename",
            "quality-filter",
            "declared-band",
            "primary-dimension",
            "ordering-appliable",
            "delta-lineage",
            "extracts-crosscheck-skipped",
        ],
    )
    def test_every_artifact_rule_exits_1(self, rule: str) -> None:
        f = V.Findings()
        f.fail(rule, "planted")
        assert f.exit_code() == 1

    def test_a_clean_run_exits_0(self) -> None:
        assert V.Findings().exit_code() == 0

    def test_a_package_fault_dominates_an_artifact_finding(self) -> None:
        f = V.Findings()
        f.fail("schema", "artifact")
        f.fail("registry-integrity-1", "package")
        assert f.exit_code() == 2

    def test_every_emitted_rule_id_is_classified(self) -> None:
        """The exit-CLASS sweep over EVERY id the validator emits, derived from its own AST."""
        import ast

        emitted = _emitted_ids(
            ast.parse((HERE / "validate_scale_prior_art.py").read_text())
        )
        assert emitted, "the AST walk found no emitted ids"
        faults = {r for r in emitted if V.is_package_fault(r)}
        assert faults, "no rule is classed as a package fault"
        assert emitted - faults, "every rule is a package fault, which cannot be right"


class TestC3lTheCLI:
    """C3l — four subcommands with the signatures §4 states."""

    def test_only_search_takes_keyword_map(self) -> None:
        parser = V.build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["keyword-map", "x.yaml", "--keyword-map", "y.yaml"])
        assert parser.parse_args(
            ["search", "x.yaml", "--keyword-map", "y.yaml"]
        ).keyword_map

    def test_extract_takes_a_bare_file(self) -> None:
        args = V.build_parser().parse_args(["extract", "x.yaml"])
        assert args.kind == "extract" and args.artifact == "x.yaml"

    def test_synthesis_takes_extracts_and_queue(self) -> None:
        args = V.build_parser().parse_args(
            ["synthesis", "x.yaml", "--extracts", "d", "--queue", "q"]
        )
        assert args.extracts == "d" and args.queue == "q"

    def test_a_missing_extracts_flag_is_exit_1_not_exit_2(self) -> None:
        # §4: a legitimately omitted optional flag is not an input-class fault. The artifact's
        # author can supply it.
        code = V.main(
            [str(FIXTURES / "scale-envelope-index.valid.yaml")].__class__(
                ["synthesis", str(FIXTURES / "scale-envelope-index.valid.yaml")]
            )
        )
        assert code == 1

    def test_the_skip_line_is_printed(self, capsys) -> None:
        V.main(["synthesis", str(FIXTURES / "scale-envelope-index.valid.yaml")])
        assert "SKIP extracts-crosscheck" in capsys.readouterr().out

    def test_the_caps_are_DERIVED_from_the_registry(self, registry: dict) -> None:
        # Not hand-copied: an exported constant that restates the registry drifts from it.
        source = (HERE / "validate_scale_prior_art.py").read_text()
        for angle in registry["angles"]:
            assert f'"cap": {angle["cap"]}' not in source
            assert f"cap = {angle['cap']}" not in source


class TestC4aTheLoadBandThresholds:
    """C4a — the CRITICAL PATH. Until it lands, lens 4 cannot run."""

    def test_the_skip_list_is_MACHINE_READABLE(self) -> None:
        # A prose finding leaves the validator unable to tell a correct episode from a wrong one.
        assert V.unsourced_dimensions() == {"concurrency", "real_time", "data_volume"}

    def test_every_unsourced_dimension_records_the_search_that_failed(self) -> None:
        import re as _re

        text = (PKG / "references" / "load-band-thresholds.md").read_text()
        data = yaml.safe_load(_re.search(r"```yaml\n(.*?)```", text, _re.S).group(1))
        for entry in data["unsourced_dimensions"]:
            assert entry.get("finding"), entry["dimension"]
            assert entry.get("searched"), entry["dimension"]

    def test_geo_distribution_is_absent_by_CONSTRUCTION_not_by_discovery(self) -> None:
        # Two mechanisms, kept apart: collapsing them is what makes a later discovery invisible.
        assert "geo_distribution" in V.NON_ORDINAL
        assert "geo_distribution" not in V.unsourced_dimensions()

    def test_the_validator_reads_the_FILE_not_a_hand_copy(self) -> None:
        source = (HERE / "validate_scale_prior_art.py").read_text()
        assert "load-band-thresholds.md" in source
        assert '"concurrency", "real_time", "data_volume"' not in source


class TestC3gTheLoadBandReDerivation:
    """C3g — the band RE-DERIVED from the number, and a band with no number REFUSED."""

    def _episode(self, **kw) -> dict:
        base = {
            "id": "s#e1",
            "primary_dimension": "availability_target",
            "load_class": {k: None for k in V.BAND_LEAVES},
            "measured_magnitude": None,
            "measured_unit": None,
            "measured_value": None,
        }
        base.update(kw)
        return {"outcome": "extracted", "episodes": [base]}

    def test_a_band_disagreeing_with_its_number_is_REFUSED(self) -> None:
        doc = self._episode(
            load_class={
                **{k: None for k in V.BAND_LEAVES},
                "availability_target": "99.999",
            },
            measured_magnitude=99.9,
            measured_unit="%",
        )
        assert "derived-load-class" in _rules(V.check_load_band, doc)

    def test_a_band_agreeing_with_its_number_passes(self) -> None:
        doc = self._episode(
            load_class={
                **{k: None for k in V.BAND_LEAVES},
                "availability_target": "99.9",
            },
            measured_magnitude=99.95 - 0.05,
            measured_unit="%",
        )
        assert not _rules(V.check_load_band, doc)

    def test_a_band_asserted_with_NO_number_is_REFUSED(self) -> None:
        doc = self._episode(
            load_class={
                **{k: None for k in V.BAND_LEAVES},
                "availability_target": "99.99",
            }
        )
        assert "derived-load-class" in _rules(V.check_load_band, doc)

    def test_no_number_and_no_band_is_clean(self) -> None:
        assert not _rules(V.check_load_band, self._episode())

    @pytest.mark.parametrize("dimension", ["concurrency", "real_time", "data_volume"])
    def test_an_unsourced_dimension_is_SKIPPED_not_guessed(
        self, dimension: str
    ) -> None:
        doc = self._episode(
            primary_dimension=dimension,
            load_class={**{k: None for k in V.BAND_LEAVES}, dimension: "extreme"},
            measured_magnitude=3.0,
            measured_unit="x",
        )
        assert not _rules(V.check_load_band, doc)

    def test_geo_distribution_is_skipped_by_construction(self) -> None:
        doc = self._episode(
            primary_dimension="geo_distribution",
            load_class={
                **{k: None for k in V.BAND_LEAVES},
                "geo_distribution": "global",
            },
            measured_magnitude=7.0,
            measured_unit="regions",
        )
        assert not _rules(V.check_load_band, doc)

    def test_it_derives_only_the_primary_dimensions_sub_key(self) -> None:
        # One `measured_value` cannot derive five bands; the other four are context.
        doc = self._episode(
            load_class={
                **{k: None for k in V.BAND_LEAVES},
                "availability_target": "99.9",
                "concurrency": "extreme",
            },
            measured_magnitude=99.9,
            measured_unit="%",
        )
        assert not _rules(V.check_load_band, doc)


class TestC3nDimensionOrders:
    """C3n — over the WHOLE rule set. Discharges EC21a."""

    def test_the_shipped_validator_passes(self) -> None:
        # primary_dimension (2) NOT-A-RULE: an ABSENCE over this module, asserted here rather
        # than emitted, because there is no artifact an author could repair.
        assert not (set(V.NON_ORDINAL) & V.unsourced_dimensions())

    def test_no_rule_maps_signal_to_a_dimension(self) -> None:
        # The validator was stopped at presence-and-enum deliberately. A mapping added later
        # would silently make a reviewer duty deterministic on an invention.
        source = (HERE / "validate_scale_prior_art.py").read_text()
        needle = "SIGNAL" + "_TO_DIMENSION"
        assert source.lower().count(needle.lower()) <= 1, (
            "more than the guard's own needle"
        )

    def test_the_two_skip_mechanisms_stay_apart(self) -> None:
        assert not (set(V.NON_ORDINAL) & V.unsourced_dimensions())


TWIN = ROOT / "skills" / "reviewing-scale-prior-art-survey"


class TestC5TheAngleReferencesMatchTheRegistry:
    """C5 — every angle reference restates the REGISTRY's tokens verbatim. EC6's population."""

    def test_there_is_one_reference_per_registry_angle(self, registry: dict) -> None:
        files = {p.stem for p in (PKG / "references" / "angles").glob("*.md")}
        assert files == {a["id"] for a in registry["angles"]}

    @pytest.mark.parametrize(
        "field", ["cap", "ordering_signal", "fallback", "precondition"]
    )
    def test_each_reference_carries_its_registry_value(
        self, registry: dict, field: str
    ) -> None:
        for angle in registry["angles"]:
            text = (PKG / "references" / "angles" / f"{angle['id']}.md").read_text()
            assert str(angle[field]) in text, f"{angle['id']}: {field}"

    def test_each_reference_lists_its_registry_sources_and_no_others(
        self, registry: dict
    ) -> None:
        for angle in registry["angles"]:
            text = (PKG / "references" / "angles" / f"{angle['id']}.md").read_text()
            listed = set(re.findall(r"^- `([a-z0-9-]+)`$", text, re.M))
            assert listed == set(angle["sources"]), angle["id"]

    def test_each_reference_restates_the_registrys_seed_input_tokens(
        self, registry: dict
    ) -> None:
        # §11's PROSE is not in EC6's population; the registry carries the tokens and the
        # reference restates them verbatim.
        for angle in registry["angles"]:
            text = (PKG / "references" / "angles" / f"{angle['id']}.md").read_text()
            for token in angle["seed_input"]:
                assert f"`{token}`" in text, f"{angle['id']}: {token}"

    def test_the_three_sizing_records_reach_their_references(
        self, registry: dict
    ) -> None:
        for angle in registry["angles"]:
            text = (PKG / "references" / "angles" / f"{angle['id']}.md").read_text()
            assert ("sizing_class" in text) == ("sizing_record" in angle), angle["id"]


class TestC6TheSkillStatesEveryDutyItself:
    """C6 — both directions, DERIVED. An orphan reference is a file the producer never opens."""

    #: The ONE declared exclusion (contract §9e). `rule-owners.yaml` maps validator rule ids to
    #: PLAN TASK IDS in another repository; no producer instruction and no reviewer condition
    #: could honestly name it, and naming it to satisfy the guard is exactly the fake this check
    #: exists to catch. Asserted in BOTH directions below.
    EXCLUDED = {"rule-owners.yaml"}

    def _named(self) -> str:
        return (PKG / "SKILL.md").read_text()

    def test_every_reference_the_skill_points_at_EXISTS(self) -> None:
        for ref in set(
            re.findall(r"`(references/[A-Za-z0-9._<>{},/-]+)`", self._named())
        ):
            if "<" in ref or "{" in ref:
                continue
            assert (PKG / ref).exists(), ref

    def test_every_file_in_references_is_NAMED(self) -> None:
        named = self._named()
        for path in sorted((PKG / "references").rglob("*")):
            if path.is_dir() or path.name in self.EXCLUDED:
                continue
            rel = path.relative_to(PKG).as_posix()
            hit = rel in named or path.name in named or path.parent.name in named
            assert hit, f"orphan reference: {rel}"

    def test_the_exclusion_is_asserted_in_BOTH_directions(self) -> None:
        # Outside the population, AND every other file inside it. Without this the exit above is
        # unsatisfiable the moment C3q lands.
        assert self.EXCLUDED
        for name in self.EXCLUDED:
            assert name not in self._named(), (
                f"{name} is named, which is the fake this catches"
            )

    def test_the_skill_states_all_four_procedures(self) -> None:
        named = self._named()
        for procedure in ("Procedure A", "Procedure B", "Procedure C", "Procedure D"):
            assert procedure in named

    def test_the_skill_carries_the_external_content_section(self) -> None:
        assert "external content is DATA" in self._named()


class TestC7TheReviewingTwin:
    """C7 — the FRAME duties and the per-kind grouping. The count is DERIVED."""

    def _conditions(self) -> list[int]:
        text = (TWIN / "references" / "conditions.md").read_text()
        return [int(m) for m in re.findall(r"^\*\*C(\d+)\.\*\*", text, re.M)]

    def test_conditions_are_numbered_contiguously(self) -> None:
        got = self._conditions()
        assert got == list(range(1, len(got) + 1))

    def test_the_count_lands_in_the_shipped_range(self) -> None:
        assert 20 <= len(self._conditions()) <= 40

    def test_the_count_is_NEVER_stated_in_prose(self) -> None:
        # A count restated beside the list it summarises goes stale; the file is the record.
        for path in (TWIN / "SKILL.md", TWIN / "references" / "conditions.md"):
            text = path.read_text()
            assert not re.search(
                r"\b(thirty|forty|twenty|\d\d)\s+(numbered\s+)?conditions", text, re.I
            )

    def test_the_verdict_grammar_is_stated_once_and_exactly(self) -> None:
        text = (TWIN / "references" / "conditions.md").read_text() + (
            TWIN / "SKILL.md"
        ).read_text()
        assert "VERDICT: approve|revise" in text
        assert "as the LAST line" in text or "the LAST line" in text
        assert "requires at least one finding" in text
        assert "contradiction" in text

    def test_the_conditions_are_grouped_per_kind(self) -> None:
        text = (TWIN / "references" / "conditions.md").read_text()
        for kind in ("keyword-map", "search", "extract", "synthesis"):
            assert f"## `{kind}`" in text

    def test_each_kind_names_the_evidence_its_conditions_need(self) -> None:
        text = (TWIN / "references" / "conditions.md").read_text()
        table = text.split("## Evidence, per kind", 1)[1].split("\n---\n", 1)[0]
        for kind in ("keyword-map", "search", "extract", "synthesis"):
            assert f"| `{kind}` |" in table

    def test_every_declared_evidence_source_is_USED_by_a_condition(self) -> None:
        # 5i shipped an evidence table promising a judgement no condition asked, so a fabricated
        # value was unfilable.
        text = (TWIN / "references" / "conditions.md").read_text()
        table, body = text.split("## Evidence, per kind", 1)[1].split("\n---\n", 1)
        for source in set(re.findall(r"`(references/[a-z0-9./-]+)`", table)):
            stem = pathlib.Path(source).stem
            assert stem in body or source in body, f"declared and unused: {source}"

    def test_the_blind_packet_stages_every_file_a_condition_needs(self) -> None:
        # 5i's packet named a scope document that did not exist, so that condition could only
        # ever record "unjudgeable".
        text = (TWIN / "references" / "conditions.md").read_text()
        for ref in set(
            re.findall(r"`(references/[a-z0-9./-]+\.(?:md|yaml|json))`", text)
        ):
            assert (PKG / ref).exists() or (TWIN / ref).exists(), (
                f"staged nowhere: {ref}"
            )

    def test_the_demoted_duty_landed(self) -> None:
        # `primary_dimension` is judged HERE because no signal-to-dimension mapping exists to
        # decide it deterministically. If this condition does not carry it, nothing does.
        text = (TWIN / "references" / "conditions.md").read_text()
        assert "DEMOTED from the validator" in text
        assert "actually MEASURED" in text

    def test_the_search_kind_has_its_type_specific_condition(self) -> None:
        text = (TWIN / "references" / "conditions.md").read_text()
        assert "AT FETCH TIME" in text and "a host the run never visited" in text

    def test_no_condition_restates_a_validator_rule(self) -> None:
        # A rule stated twice drifts, and only one of them runs.
        text = (TWIN / "references" / "conditions.md").read_text()
        assert "The gate runs FIRST and returns early" in text
        for rule in (
            "declared-band",
            "map-completeness",
            "admission",
            "ordering-appliable",
            "quality-filter",
            "synthesis",
        ):
            for para in re.findall(r"^\*\*C\d+\.\*\*(?:[^\n]*\n)+?(?=\n)", text, re.M):
                if f"`{rule}`" in para:
                    assert "owns" in para or "gate" in para or "validator" in para, (
                        para[:90]
                    )


class TestC8cTheSelfContainmentSweep:
    """C8c — nothing an agent reads names an absolute or machine-local path."""

    #: This module declares the forbidden tokens as DATA and would fail on its own definition.
    #: The exclusion is asserted in both directions below, against the DECLARED list and never a
    #: copy of it.
    FORBIDDEN = ("/home/", "/Users/", "C:\\", "file:///", "~/", "/tmp/", "localhost:")

    def _corpus(self) -> list[pathlib.Path]:
        out: list[pathlib.Path] = []
        for pkg in (PKG, TWIN):
            for suffix in ("*.md", "*.yaml", "*.json", "*.py"):
                out += [
                    p
                    for p in pkg.rglob(suffix)
                    if p.name != pathlib.Path(__file__).name
                ]
        return sorted(out)

    def test_the_population_is_at_least_forty_files(self) -> None:
        # WIDENS 5i's portability population, which globs the two package directories only.
        assert len(self._corpus()) >= 40, len(self._corpus())

    def test_nothing_names_a_machine_local_path(self) -> None:
        for path in self._corpus():
            text = path.read_text()
            for token in self.FORBIDDEN:
                assert token not in text, f"{path.relative_to(ROOT)}: {token!r}"

    def test_the_exclusion_is_asserted_in_both_directions(self) -> None:
        assert pathlib.Path(__file__).name not in {p.name for p in self._corpus()}
        assert any("_TO_DIMENSION" not in p.name for p in self._corpus())

    def test_a_planted_absolute_path_in_an_INCLUDED_file_is_caught(
        self, tmp_path
    ) -> None:
        planted = tmp_path / "planted.md"
        planted.write_text("see /home/someone/thing.md")
        assert any(token in planted.read_text() for token in self.FORBIDDEN)


class TestC3fConfidenceReDerived:
    """C3f — the ordered table BRANCH BY BRANCH. Discharges EC19's episode half."""

    def _ep(self, **kw) -> dict:
        base = {
            "id": "s#e1",
            "evidence_class": "measured-in-production",
            "measured_value": "1.2M rows/s",
            "configuration_stated": True,
            "load_class": {k: "high" for k in V.BAND_LEAVES},
        }
        base.update(kw)
        return base

    @pytest.mark.parametrize(
        ("expected", "kw"),
        [
            ("very-low", {"evidence_class": "narrative-only"}),
            ("high", {"evidence_class": "vendor-documented-limit"}),
            (
                "low",
                {"evidence_class": "vendor-documented-limit", "measured_value": None},
            ),
            ("low", {"measured_value": None}),
            ("moderate", {"configuration_stated": False}),
            ("high", {"evidence_class": "rule-governed-benchmark"}),
            ("high", {"evidence_class": "peer-reviewed-evaluation"}),
            ("high", {"evidence_class": "independent-verification"}),
            ("high", {}),
        ],
    )
    def test_each_branch(self, expected: str, kw: dict) -> None:
        assert V.derive_confidence(self._ep(**kw)) == expected

    def test_the_final_else_is_reachable(self) -> None:
        # `load_class` sub-keys are nullable precisely so this branch and the one above it are
        # both reachable. A design drawing them as always-populated made this dead.
        partial = {k: (None if k == "data_volume" else "high") for k in V.BAND_LEAVES}
        assert V.derive_confidence(self._ep(load_class=partial)) == "moderate"

    def test_a_later_branch_cannot_swallow_an_earlier_case(self) -> None:
        # narrative-only with a measured value and a full load_class would reach `high` on any
        # later branch; the FIRST branch must catch it.
        assert (
            V.derive_confidence(self._ep(evidence_class="narrative-only")) == "very-low"
        )
        # and vendor-documented-limit with no value must reach `low` via ITS branch, not via the
        # generic measured_value-absent branch that follows it.
        assert (
            V.derive_confidence(
                self._ep(evidence_class="vendor-documented-limit", measured_value=None)
            )
            == "low"
        )

    def test_a_hand_set_value_disagreeing_is_REFUSED(self, clean_extract: dict) -> None:
        planted = copy.deepcopy(clean_extract)
        planted["episodes"][0]["confidence"] = "very-low"
        assert "derived-confidence" in _rules(V.check_confidence, planted)

    def test_the_clean_record_agrees_with_the_derivation(
        self, clean_extract: dict
    ) -> None:
        assert not _rules(V.check_confidence, clean_extract)


class TestC3hWhatTheDerivationDoesNotRead:
    """C3h — two ABSENCES over the derivation's AST, one concern: its INPUT SET.

    An author never asserts `confidence`, so a fifth input added by accident is invisible to any
    value test. Only the AST sees it, and the spec records shipping this exact drift once.
    """

    def _derivation_source(self) -> str:
        """The derivation's CODE, with its docstring removed.

        The docstring NAMES both excluded fields in order to say they are excluded, so a dump
        including it reports them as present — the guard would then fail on a correct function
        and pass on one whose docstring was deleted. The assertion is over the code.
        """
        import ast
        import inspect

        fn = ast.parse(inspect.getsource(V.derive_confidence)).body[0]
        body = (
            fn.body[1:]
            if (
                isinstance(fn.body[0], ast.Expr)
                and isinstance(fn.body[0].value, ast.Constant)
            )
            else fn.body
        )
        assert body is not fn.body, (
            "the derivation has no docstring, so nothing was stripped"
        )
        return "".join(ast.dump(node) for node in body)

    def test_the_derivation_reads_no_transferability_key(self) -> None:
        # transferability (2) NOT-A-RULE. It is the founding-risk field and folding it into
        # confidence is what the whole family exists to prevent.
        assert "transferability" not in self._derivation_source()

    def test_the_derivation_reads_no_published_date_key(self) -> None:
        # derived confidence (2) NOT-A-RULE. `published_date` is currency, which a different
        # lens reads.
        assert "published_date" not in self._derivation_source()

    def test_the_input_set_is_exactly_four_facts(self) -> None:
        dumped = self._derivation_source()
        for name in (
            "evidence_class",
            "measured_value",
            "configuration_stated",
            "load_class",
        ):
            assert name in dumped, name
        for name in (
            "score",
            "signal",
            "technology",
            "metric_name",
            "pattern",
            "claim",
            "primary_dimension",
            "cause_class",
            "outcome_kind",
        ):
            assert name not in dumped, f"a fifth input crept in: {name}"

    def test_a_disagreeing_transferability_PASSES_the_gate(
        self, clean_extract: dict
    ) -> None:
        # The independence, from the other side: high confidence with low transferability is a
        # legal artifact, and only the reviewer judges whether it is honest.
        planted = copy.deepcopy(clean_extract)
        planted["episodes"][0]["transferability"] = {
            "level": "low",
            "reason": "Measured three bands above this project on hardware it will not have.",
        }
        assert not _rules(V.check_confidence, planted)
        assert not _rules(V.check_extract, planted)


class TestC3oTheQualityFilterIsRankingOnly:
    """C3o — TWO assertions over the AST. Discharges EC19b."""

    def _source(self) -> str:
        return (HERE / "validate_scale_prior_art.py").read_text()

    def test_score_is_READ_exactly_once(self) -> None:
        # A name-absence check proves ZERO occurrences and can never prove EXACTLY ONE. The one
        # read is C3k's presence/range rule.
        import ast

        tree = ast.parse(self._source())
        reads = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and getattr(node.func, "attr", "") == "get"
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and node.args[0].value == "score"
        ]
        assert len(reads) == 1, f"{len(reads)} reads of `score`"

    def test_no_sort_filter_or_slice_references_score(self) -> None:
        import ast

        tree = ast.parse(self._source())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and getattr(node.func, "attr", "") in {
                "sort",
                "sorted",
            }:
                assert "score" not in ast.dump(node)
            if isinstance(node, (ast.ListComp, ast.GeneratorExp)) and node.generators:
                for gen in node.generators:
                    for cond in gen.ifs:
                        assert "score" not in ast.dump(cond)
            if isinstance(node, ast.Subscript) and "score" in ast.dump(node):
                raise AssertionError("a slice references `score`")

    def test_the_filter_never_cuts(self) -> None:
        # A filter that cut would delete the operational canon and every negative result — the
        # same reasoning that keeps `no-stated-load` out of the bail causes.
        text = (PKG / "references" / "quality-filter.md").read_text()
        assert "It RANKS. It never cuts." in text
        assert "never checks the number's justification" in text


class TestC3qTheRuleOwnerMap:
    """C3q — every emitted rule attributed to the plan task that owns it."""

    OWNERS = PKG / "references" / "rule-owners.yaml"

    def _emitted(self) -> set:
        import ast

        return _emitted_ids(
            ast.parse((HERE / "validate_scale_prior_art.py").read_text())
        )

    def test_the_key_set_is_EQUAL_to_the_emitted_ids(self) -> None:
        # Both directions: emitted-but-unmapped and mapped-but-not-emitted each fail.
        mapped = set(yaml.safe_load(self.OWNERS.read_text()))
        emitted = self._emitted()
        assert mapped == emitted, {
            "emitted but unmapped": sorted(emitted - mapped),
            "mapped but not emitted": sorted(mapped - emitted),
        }

    def test_the_ast_walk_reads_BOTH_call_shapes(self) -> None:
        # The `rule=` shape is the one a positional-only walk missed.
        assert "registry-unreadable" in self._emitted()

    def test_the_walk_yields_at_least_the_derived_floor(self) -> None:
        # A floor, not an equality: the plan's clause count minus its exemptions.
        assert len(self._emitted()) >= 70

    def test_every_owner_is_a_plan_task_id(self) -> None:
        # The cross-repo half — that the id names a task that EXISTS — is D1b's.
        for rule, owner in yaml.safe_load(self.OWNERS.read_text()).items():
            assert re.fullmatch(r"[A-E]\d+[a-z]?\d?", owner), f"{rule} -> {owner!r}"

    def test_no_id_could_be_attributed_by_TEXT_SEARCH(self) -> None:
        # `schema`, `bound`, `admission`, `input` and `synthesis` all match ordinary prose.
        english = {"schema", "bound", "admission", "input", "synthesis"}
        emitted = self._emitted()
        for word in english:
            assert any(x == word or x.startswith(f"{word}-") for x in emitted), word

    def test_it_is_the_ONE_reference_excluded_from_the_skill_sweep(self) -> None:
        assert "rule-owners.yaml" not in (PKG / "SKILL.md").read_text()
        assert self.OWNERS.exists()


PLANTED = FIXTURES / "planted"

#: (planted file, its clean base, the CLI kind, the rule its single plant must fire).
PLANTS = [
    (
        "map-01.yaml",
        "scale-vocabulary-map.valid.yaml",
        "keyword-map",
        "map-completeness-5",
    ),
    (
        "map-02.yaml",
        "scale-vocabulary-map.valid.yaml",
        "keyword-map",
        "map-completeness-1g",
    ),
    ("search-01.yaml", "search-output-b5.valid.yaml", "search", "coverage-grid-4d"),
    ("search-02.yaml", "search-output-b5.valid.yaml", "search", "bound-1"),
    ("search-03.yaml", "search-output-b5.valid.yaml", "search", "admission-1b"),
    ("extract-01.yaml", "extract-output.valid.yaml", "extract", "derived-confidence-1"),
    (
        "extract-02.yaml",
        "extract-output.valid.yaml",
        "extract",
        "measured-coherence-1b",
    ),
    ("extract-03.yaml", "extract-output.valid.yaml", "extract", "vocabularies-5a"),
    ("index-01.yaml", "scale-envelope-index.valid.yaml", "synthesis", "synthesis-2"),
]


def _leaves(node, path="") -> set:
    """Every leaf path in a document, so two fixtures can be diffed STRUCTURALLY."""
    out = set()
    if isinstance(node, dict):
        for k, v in node.items():
            out |= _leaves(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            out |= _leaves(v, f"{path}[{i}]")
    else:
        out.add(f"{path}={node!r}")
    return out


class TestC8aThePlantedFixtures:
    """C8a — one defect each, caught, and structurally one edit from its base. EC1a."""

    @pytest.mark.parametrize(("planted", "base", "kind", "rule"), PLANTS)
    def test_each_differs_from_its_base_in_EXACTLY_its_plant(
        self, planted: str, base: str, kind: str, rule: str
    ) -> None:
        # A fixture wrong in two ways proves nothing about either: the second can mask the
        # first, and a check that fires cannot say which one it saw.
        a = _leaves(yaml.safe_load((FIXTURES / base).read_text()))
        b = _leaves(yaml.safe_load((PLANTED / planted).read_text()))
        changed = (a - b) | (b - a)
        keys = {leaf.split("=")[0] for leaf in changed}
        assert len(keys) <= 2, sorted(keys)

    @pytest.mark.parametrize(("planted", "base", "kind", "rule"), PLANTS)
    def test_each_plant_fires_its_named_rule(
        self, planted: str, base: str, kind: str, rule: str
    ) -> None:
        argv = [kind, str(PLANTED / planted)]
        if kind == "search":
            argv += ["--keyword-map", str(FIXTURES / "scale-vocabulary-map.valid.yaml")]
        if kind == "synthesis":
            argv += ["--extracts", str(FIXTURES / "extracts")]
        f = V.Findings()
        import contextlib
        import io

        with contextlib.redirect_stdout(io.StringIO()):
            V.main(argv)
        # re-run through the module's own path so the findings are inspectable
        doc = yaml.safe_load((PLANTED / planted).read_text())
        reg = yaml.safe_load(REGISTRY.read_text())
        if kind == "keyword-map":
            V.check_map(doc, reg, f)
        elif kind == "search":
            kmap = yaml.safe_load(
                (FIXTURES / "scale-vocabulary-map.valid.yaml").read_text()
            )
            V.check_cell_sanitization(doc, f)
            V.check_search(doc, reg, kmap, f)
        elif kind == "extract":
            V.check_extract(doc, f)
            V.check_confidence(doc, f)
            V.check_load_band(doc, f)
        else:
            extracts = [
                yaml.safe_load(p.read_text())
                for p in sorted((FIXTURES / "extracts").glob("*.yaml"))
            ]
            V.check_synthesis(doc, extracts, f)
        assert rule in {r for r, _ in f.items}, sorted({r for r, _ in f.items})

    @pytest.mark.parametrize(("planted", "base", "kind", "rule"), PLANTS)
    def test_each_gates_at_exit_1_not_exit_2(
        self, planted: str, base: str, kind: str, rule: str
    ) -> None:
        # A planted ARTIFACT defect is an artifact-author fault. Exit 2 would say the package is
        # broken, which it is not.
        argv = [kind, str(PLANTED / planted)]
        if kind == "search":
            argv += ["--keyword-map", str(FIXTURES / "scale-vocabulary-map.valid.yaml")]
        if kind == "synthesis":
            argv += ["--extracts", str(FIXTURES / "extracts")]
        import contextlib
        import io

        with contextlib.redirect_stdout(io.StringIO()):
            assert V.main(argv) == 1

    def test_every_planted_file_is_in_the_table(self) -> None:
        on_disk = {p.name for p in PLANTED.glob("*.yaml")}
        assert on_disk == {p[0] for p in PLANTS}


class TestC8bFixtureIntegrity:
    """C8b — over ALL fixtures, before any reviewer sees one. Discharges EC24."""

    def test_every_fixture_parses(self) -> None:
        for path in sorted(FIXTURES.rglob("*.yaml")):
            assert yaml.safe_load(path.read_text()) is not None, path.name

    def test_no_active_source_has_no_cell(
        self, clean_map: dict, clean_search: dict
    ) -> None:
        angle = "b5"
        reg = yaml.safe_load(REGISTRY.read_text())
        block = next(a for a in reg["angles"] if a["id"] == angle)
        active = {r["id"] for r in clean_map["sources"]["active"]}
        owed = {s for s in block["sources"] if s in active}
        seen = {c["source_id"] for c in clean_search["coverage"]}
        assert owed <= seen, sorted(owed - seen)

    def test_no_source_outside_the_angles_corpus(self, clean_search: dict) -> None:
        reg = yaml.safe_load(REGISTRY.read_text())
        block = next(a for a in reg["angles"] if a["id"] == "b5")
        assert {c["source_id"] for c in clean_search["coverage"]} <= set(
            block["sources"]
        )

    def test_no_fallback_that_left_no_trace(self, clean_search: dict) -> None:
        # A cell that fell back records which row it fell back to, or the fallback is invisible.
        for cell in clean_search["coverage"]:
            if cell.get("fallback_used"):
                assert cell["fallback_used"].startswith(("angle:", "row:")), cell[
                    "fallback_used"
                ]

    def test_no_kept_zero_with_no_stated_cause(self, clean_search: dict) -> None:
        for cell in clean_search["coverage"]:
            if cell.get("kept") == 0 and cell["status"] == "reached":
                assert cell.get("returned") is not None, cell


class TestC8eTheCapDriftCheck:
    """C8e — each owed cap against the SIZING RECORD committed beside it, per `sizing_class`."""

    def _angle(self, registry: dict, aid: str) -> dict:
        return next(a for a in registry["angles"] if a["id"] == aid)

    def test_a3_is_an_enumerable_union_and_cap_equals_sum(self, registry: dict) -> None:
        a = self._angle(registry, "a3")
        s = a["sizing_record"]
        assert s["sizing_class"] == "enumerable-union"
        assert a["cap"] == s["sum"]
        assert s["sum"] == sum(p["count"] for p in s["parts"])

    def test_b3_records_its_floor_its_matcher_AND_its_listings_covered(
        self, registry: dict
    ) -> None:
        # The third had no owner and sat one section outside the field check's window.
        s = self._angle(registry, "b3")["sizing_record"]
        assert s["sizing_class"] == "budget-floor"
        assert s["floor"] and s["matcher"] and s["listings_covered"]

    def test_b3_does_NOT_assert_cap_at_or_above_its_floor(self, registry: dict) -> None:
        # A budget is BELOW its floor by design — that is what makes the ordering load-bearing.
        a = self._angle(registry, "b3")
        assert a["cap"] < a["sizing_record"]["floor"]

    def test_b7_names_every_corpus_and_why_it_cannot_be_counted(
        self, registry: dict
    ) -> None:
        s = self._angle(registry, "b7")["sizing_record"]
        assert s["sizing_class"] == "budget-uncountable"
        for corpus in s["corpora"]:
            assert corpus["source"] and corpus["reason"]

    def test_the_cross_class_guard(self, registry: dict) -> None:
        # No `enumerable-union` without a sum, no `budget-floor` without a floor, no
        # `budget-uncountable` with one.
        for angle in registry["angles"]:
            s = angle.get("sizing_record")
            if not s:
                continue
            kind = s["sizing_class"]
            assert ("sum" in s) == (kind == "enumerable-union"), angle["id"]
            assert ("floor" in s) == (kind == "budget-floor"), angle["id"]
            assert ("corpora" in s) == (kind == "budget-uncountable"), angle["id"]

    def test_sizing_records_exist_for_exactly_the_owed_caps(
        self, registry: dict
    ) -> None:
        assert {a["id"] for a in registry["angles"] if "sizing_record" in a} == {
            "a3",
            "b3",
            "b7",
        }


class TestC8fNoCountOfInjectionHits:
    """C8f — the POSTURE, never a count. Discharges EC26b."""

    #: Scoped substrings, shipped with the test. A bare `count` over all rule ids is
    #: unsatisfiable: fourteen sibling rule ids carry it across eight packages, and all nine
    #: validator files contain it in text.
    FORBIDDEN = (
        "injection-count",
        "injection_hits",
        "sanitization-count",
        "neutralised-count",
    )

    def test_no_sanitization_sub_property_is_an_integer(self) -> None:
        import json

        for path in sorted(SCHEMAS.glob("*.schema.json")):
            doc = json.loads(path.read_text())

            def walk(node, inside=False):
                if isinstance(node, dict):
                    props = node.get("properties") or {}
                    for key, value in props.items():
                        here = inside or key == "sanitization"
                        if (
                            here
                            and isinstance(value, dict)
                            and value.get("type") == "integer"
                        ):
                            raise AssertionError(
                                f"{path.name}: sanitization.{key} is an integer"
                            )
                        walk(value, here)
                    for value in node.values():
                        if isinstance(value, (dict, list)) and value is not props:
                            walk(value, inside)
                elif isinstance(node, list):
                    for value in node:
                        walk(value, inside)

            walk(doc)

    def test_no_sanitization_RULE_ID_carries_a_count_substring(self) -> None:
        import ast

        ids = _emitted_ids(
            ast.parse((HERE / "validate_scale_prior_art.py").read_text())
        )
        for rule in ids:
            if not rule.startswith("sanitization"):
                continue
            for token in self.FORBIDDEN:
                assert token not in rule, rule

    def test_no_sanitization_CONDITION_carries_one(self) -> None:
        text = (TWIN / "references" / "conditions.md").read_text()
        for token in self.FORBIDDEN:
            assert token not in text, token

    def test_the_posture_is_what_is_recorded(self) -> None:
        assert "Record the POSTURE, never a count" in (PKG / "SKILL.md").read_text()


class TestC8dTheFieldSweepNested:
    """C8d — `loose - read == UNREADABLE`, per-package and NESTED. Discharges EC9."""

    #: Leaves the validator legitimately never reads: presentation, provenance and the two the
    #: reviewer judges instead. Stated as data so the sweep's arithmetic is checkable, and each
    #: with the reason it is here.
    UNREADABLE = frozenset(
        {
            "adjustable",
            "assumptions",
            "blocks_requirement",
            "canonical",
            "cells_owed",
            "cells_reached",
            "claim",
            "classification",
            "corpus_version",
            "default_pattern",
            "evidence_quote",
            "expansion_cap",
            "expansions",
            "failure_classes",
            "hard_limits",
            "limit",
            "load_dimensions",
            "map_verdict",
            "metric_name",
            "named_technologies",
            "negative_terms",
            "note",
            "notes",
            "open_gap",
            "outcome_kind",
            "probe",
            "published_date",
            "queries",
            "ran",
            "reason_class",
            "retrieval_summary",
            "retrieved_at",
            "revision",
            "scale",
            "schema_version",
            "scope_ref",
            "source_authority",
            "system_classes",
            "system_name",
            "term",
            "terms",
            "timestamp",
            "title",
            "version",
        }
    )

    def _leaves(self) -> set:
        import json

        out: set[str] = set()

        def walk(node) -> None:
            if isinstance(node, dict):
                for key, value in (node.get("properties") or {}).items():
                    out.add(key)
                    walk(value)
                for key in ("items", "then", "else", "if", "not"):
                    if key in node:
                        walk(node[key])
                for key in ("allOf", "anyOf", "oneOf"):
                    for branch in node.get(key) or []:
                        walk(branch)
                for value in (node.get("$defs") or {}).values():
                    walk(value)
            elif isinstance(node, list):
                for value in node:
                    walk(value)

        for path in sorted(SCHEMAS.glob("*.schema.json")):
            walk(json.loads(path.read_text()))
        return out

    def test_the_leaf_count_is_at_least_its_floor(self) -> None:
        # A FLOOR, the same convention C8c uses for its file count — an equality goes stale on
        # the first legitimate field.
        assert len(self._leaves()) >= 120, len(self._leaves())

    def test_loose_minus_read_equals_UNREADABLE(self) -> None:
        # The VALIDATOR file, never the test file: this module names every field in its own
        # assertions, so sweeping it would report the whole surface as read.
        source = (HERE / "validate_scale_prior_art.py").read_text()
        loose = self._leaves()
        read = {leaf for leaf in loose if f'"{leaf}"' in source}
        assert (loose - read) == (self.UNREADABLE & loose), {
            "declared unreadable but READ": sorted(self.UNREADABLE & read),
            "unread and not declared": sorted(loose - read - self.UNREADABLE),
        }

    def test_what_it_does_NOT_glob_is_stated(self) -> None:
        # The test module. Sweeping it is how a field-liveness check reports itself green.
        assert "validate_scale_prior_art.py" in str(
            HERE / "validate_scale_prior_art.py"
        )
        assert not (HERE / "validate_scale_prior_art.py").name.startswith("test_")
