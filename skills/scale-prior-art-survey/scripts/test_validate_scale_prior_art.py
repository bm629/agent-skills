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


def _emitted_ids(tree, shapes=("positional", "keyword", "default")) -> set:
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
        if (
            "positional" in shapes
            and getattr(node.func, "id", "") == "_fail"
            and node.args
        ):
            if isinstance(node.args[0], _ast.Constant):
                out.add(node.args[0].value)
        if "keyword" in shapes:
            for kw in node.keywords:
                if kw.arg == "rule" and isinstance(kw.value, _ast.Constant):
                    out.add(kw.value.value)
    # THIRD shape: a `rule` PARAMETER DEFAULT. `load_yaml(path, f)` called without the keyword
    # emits the default, and a walk reading only calls reported the map complete while it was
    # short by exactly that id — the same blindness this function's own comment describes, one
    # level further in.
    if "default" in shapes:
        for node in _ast.walk(tree):
            if isinstance(node, _ast.FunctionDef):
                args = node.args
                names = [a.arg for a in args.args]
                for name, default in zip(
                    names[len(names) - len(args.defaults) :], args.defaults
                ):
                    if name == "rule" and isinstance(default, _ast.Constant):
                        out.add(default.value)
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


def _findings(fn, *args) -> list:
    """The raw (rule, message) pairs, for assertions that must be EXACT rather than by family."""
    f = V.Findings()
    fn(*args, f)
    return f.items


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
            lambda m: m["scope_guard"].__setitem__(
                "shared_terms",
                [
                    {
                        "term": "throughput",
                        "groups": ["g-load-volume", "g-sys-batch"],
                        "owner": "",
                    }
                ],
            ),
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
        f = V.Findings()
        V.load_yaml(tmp_path / "absent.yaml", f, rule="input")
        assert "input" in {r for r, _ in f.items}


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
        # EVERY id's class, checked against the contract rather than counted. Appending a
        # prefix that misclassifies one rule used to leave the failure set byte-identical.
        artifact_families = (
            "map-completeness",
            "declared-band",
            "sanitization",
            "coverage-grid",
            "admission",
            "bound",
            "vocabularies",
            "bail",
            "body-sections",
            "primary-dimension",
            "transferability",
            "measured-coherence",
            "derived-confidence",
            "derived-load-class",
            "synthesis",
            "lineage-liveness",
            "id-grammar",
            "record-filename",
            "quality-filter",
            "schema",
            "retrieval-summary",
            "extracts-crosscheck-skipped",
        )
        package_families = (
            "registry-",
            "angle-block-",
            "fallback-",
            "schema-unavailable",
            "dependency-missing",
            "input",
            "thresholds-unreadable",
        )
        for rule in sorted(emitted):
            is_artifact = (
                rule.startswith(artifact_families) and rule != "schema-unavailable"
            )
            is_package = rule.startswith(package_families)
            assert is_artifact != is_package, f"{rule} is in neither class or both"
            assert V.is_package_fault(rule) is is_package, rule


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
        return [int(m) for m in re.findall(r"^\*\*C(\d+) — ", text, re.M)]

    def test_conditions_are_numbered_contiguously(self) -> None:
        got = self._conditions()
        assert got == list(range(1, len(got) + 1))

    def test_the_count_is_near_the_shipped_range_and_the_deviation_is_DECLARED(
        self,
    ) -> None:
        """The range is a MEASUREMENT of the siblings, not a budget.

        This pair lands one above it. Merging two conditions to fit inside a measured number
        would be picking the number over a duty, so the deviation is DECLARED instead — in a
        file that ships, because the first version of this assertion read the authoring
        repository by absolute path and failed from a clean checkout.
        """
        count = len(self._conditions())
        assert 20 <= count <= 45
        if count > 40:
            doc = ROOT / "docs/skills/reviewing-scale-prior-art-survey.md"
            # Whitespace collapsed: the doc wraps the sentence, and a raw substring test fails
            # on a correct declaration.
            flat = " ".join(doc.read_text().split())
            # DERIVED, not a literal: the declaration named a distance of ONE and stayed green
            # when the count moved to 43, because nothing tied the word to the measurement.
            words = {1: "ONE", 2: "TWO", 3: "THREE", 4: "FOUR", 5: "FIVE"}
            assert f"{words[count - 40]} above the sibling range" in flat, (
                f"the declaration does not state the measured distance of {count - 40}"
            )

    def test_the_count_is_NEVER_stated_in_prose(self) -> None:
        # A count restated beside the list it summarises goes stale; the file is the record.
        #
        # HYPHENATED compounds and a bare "of the forty-one" both slipped past the first
        # version: it required whitespace after the numeral and a following "conditions", so
        # `forty-one` was invisible and so was a count with the noun elided. The numeral alone
        # is the needle now, flattened so a line break cannot hide it either.
        words = r"twenty|thirty|forty|fifty"
        for path in (TWIN / "SKILL.md", TWIN / "references" / "conditions.md"):
            flat = " ".join(path.read_text().split())
            hits = re.findall(
                rf"\b(?:{words})(?:[- ](?:one|two|three|four|five|six|seven|eight|nine))?\b",
                flat,
                re.I,
            )
            hits += re.findall(r"\b\d\d\s+(?:numbered\s+)?conditions\b", flat, re.I)
            assert not hits, f"{path.name} states a count in prose: {hits}"

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
        span = text.split("## Evidence, per kind", 1)[1].split("\n---\n", 1)[0]
        table = "\n".join(row for row in span.splitlines() if row.startswith("| `"))
        for kind in ("keyword-map", "search", "extract", "synthesis"):
            assert f"| `{kind}` |" in table

    def test_every_declared_evidence_source_is_USED_by_a_condition(self) -> None:
        # 5i shipped an evidence table promising a judgement no condition asked, so a fabricated
        # value was unfilable.
        text = (TWIN / "references" / "conditions.md").read_text()
        span, body = text.split("## Evidence, per kind", 1)[1].split("\n---\n", 1)
        # The TABLE ROWS only. Prose above the table explains which paths are the producer's,
        # and naming them there made the guard treat its own explanation as a declaration.
        table = "\n".join(row for row in span.splitlines() if row.startswith("| `"))
        # `producer: ` prefixes the paths that live in the OTHER package, so the pattern has
        # to see past it — without that it matched four of seven and the guard went quiet.
        declared = set(
            re.findall(r"`(?:producer: )?(references/[A-Za-z0-9./*<>_-]+)`", table)
        )
        assert len(declared) >= 7, f"the pattern matched only {len(declared)} sources"
        for source in declared:
            # A glob or a placeholder names a FAMILY: `references/angles/<angle>.md`,
            # `references/fixtures/source-*.md`. Match on the stable part, because the earlier
            # character class excluded `<` and `*` and silently skipped both — including the
            # SOURCE-itself row that five conditions depend on.
            stem = (
                re.split(r"[<*]", pathlib.Path(source).name)[0].rstrip("-.")
                or pathlib.Path(source).parent.name
            )
            assert stem and (stem in body or source in body), (
                f"declared and unused: {source}"
            )

    def test_the_blind_packet_stages_every_file_a_condition_needs(self) -> None:
        # 5i's packet named a scope document that did not exist, so that condition could only
        # ever record "unjudgeable".
        text = (TWIN / "references" / "conditions.md").read_text()
        # `(?:producer: )?` — WITHOUT it this matched two paths of nine. Prefixing the producer's
        # paths took the population from seven to two and the guard stayed green, while its
        # neighbour above was updated for the identical cause in the same commit.
        refs = set(
            re.findall(
                r"`(?:producer: )?(references/[a-z0-9./-]+\.(?:md|yaml|json))`", text
            )
        )
        for ref in refs:
            assert (PKG / ref).exists() or (TWIN / ref).exists(), (
                f"staged nowhere: {ref}"
            )
        # DERIVED, so the population cannot quietly empty: the evidence table declares these
        # paths, and every one of them must be in the set this test just walked.
        table = text[text.index("| kind | what you are handed |") :]
        declared = set(
            re.findall(
                r"`(?:producer: )?(references/[a-z0-9./-]+\.(?:md|yaml|json))`",
                table[: table.index("\n\n", table.index("|"))],
            )
        )
        assert declared and declared <= refs, {
            "declared by the evidence table": sorted(declared),
            "reached by this guard": sorted(refs),
        }

    def test_the_demoted_duty_landed(self) -> None:
        # `primary_dimension` is judged HERE because no signal-to-dimension mapping exists to
        # decide it deterministically. If this condition does not carry it, nothing does.
        text = (TWIN / "references" / "conditions.md").read_text()
        assert "DEMOTED from the validator" in text
        assert "actually MEASURED" in text

    def test_the_search_kind_has_its_type_specific_condition(self) -> None:
        text = (TWIN / "references" / "conditions.md").read_text()
        # Whitespace collapsed: the condition wraps, so a raw two-phrase substring test fails
        # on a correct file.
        flat = " ".join(text.split())
        assert "AT FETCH TIME" in flat and "a host the run never visited" in flat

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
            for para in re.findall(r"^\*\*C\d+ — (?:[^\n]*\n)+?(?=\n)", text, re.M):
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
        # OUT: this module declares the forbidden tokens as DATA and would fail on its own
        # definition. IN: every other file of a swept type is in the population, so the
        # exclusion cannot quietly widen.
        corpus = {p.resolve() for p in self._corpus()}
        assert pathlib.Path(__file__).resolve() not in corpus
        for pkg in (PKG, TWIN):
            for suffix in ("*.md", "*.yaml", "*.json", "*.py"):
                for path in pkg.rglob(suffix):
                    if path.resolve() == pathlib.Path(__file__).resolve():
                        continue
                    assert path.resolve() in corpus, path

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

    def test_every_shape_the_walk_READS_is_one_the_validator_USES(self) -> None:
        """A branch nothing exercises is a branch nothing protects.

        A fix moved the last keyword call site to positional and left the branch, its test, and a
        docstring all asserting an id "reaches `_fail` only the second way". Measured after that
        commit, positional-only and both-branches-disabled yielded the identical set, so two
        branches and the test guarding them were dead in the same change that reasserted them.

        A shape may legitimately have no instances; what may not happen is a shape with no
        instances that some other assertion claims to depend on. So: every shape with instances
        must CHANGE the derived set when removed, and the shapes with none are named here.
        """
        import ast

        tree = ast.parse((HERE / "validate_scale_prior_art.py").read_text())
        full = _emitted_ids(tree)
        shapes = ("positional", "keyword", "default")
        exercised = {
            s
            for s in shapes
            if _emitted_ids(tree, tuple(x for x in shapes if x != s)) != full
        }
        assert exercised == {"positional", "keyword"}, {
            "exercised": sorted(exercised),
            "unused": sorted(set(shapes) - exercised),
        }

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


#: The per-CLAUSE mutations that used to be nine files in `planted/`. They belong here: a
#: test must CONSTRUCT the shape it asserts on rather than select it out of a fixture, and a file
#: that fires a validator rule is not a planted fixture at all — it tests the validator, which was
#: never what `planted/` is for. Each entry is (kind, base fixture, mutate, the exact clause id).
def _m_always_on_angle_refused(d):
    v = next(x for x in d["angle_applicability"] if x["angle_id"] == "a3")
    v["holds"] = False
    v["reason"] = "The DECIDING value is archetype.primary = cli-tool."


def _m_source_row_in_both_arrays(d):
    d["sources"]["active"].append({**d["sources"]["active"][0]})
    d["sources"]["active"][-1]["id"] = d["sources"]["skipped"][0]["id"]


def _m_unreached_cell_records_a_count(d):
    next(c for c in d["coverage"] if c["status"] != "reached")["returned"] = 0


def _m_query_names_no_group_term(d):
    # The rule shipped named in the validator and the owner map and NOWHERE else: disabling its
    # condition left every test green. This is the constructed case that makes it testable.
    d["coverage"][0]["queries"] = ['"volume" in tpc.org/tpcc results listing']


def _m_cap_wider_than_the_registry(d):
    d["bound"]["cap"] = 999


def _m_found_by_names_no_cell(d):
    d["candidates"][0]["found_by"] = "g-nonexistent/no-such-source"
    next(c for c in d["coverage"] if c["status"] == "reached")["kept"] = 0


def _m_confidence_disagrees_with_the_derivation(d):
    d["episodes"][0]["confidence"] = "very-low"


def _m_measured_unit_dropped(d):
    d["episodes"][0]["measured_unit"] = None


def _m_technology_outside_the_purl_grammar(d):
    d["episodes"][0]["technology"] = "duckdb 1.1"


def _m_area_confidence_above_its_weakest(d):
    d["areas"][0]["confidence"] = "high"


MUTATIONS = [
    (
        "keyword-map",
        "scale-vocabulary-map.valid.yaml",
        _m_always_on_angle_refused,
        "map-completeness-5",
    ),
    (
        "keyword-map",
        "scale-vocabulary-map.valid.yaml",
        _m_source_row_in_both_arrays,
        "map-completeness-1a",
    ),
    (
        "search",
        "search-output-b5.valid.yaml",
        _m_unreached_cell_records_a_count,
        "coverage-grid-4d",
    ),
    (
        "search",
        "search-output-b5.valid.yaml",
        _m_query_names_no_group_term,
        "coverage-grid-5",
    ),
    (
        "search",
        "search-output-b5.valid.yaml",
        _m_cap_wider_than_the_registry,
        "bound-1",
    ),
    (
        "search",
        "search-output-b5.valid.yaml",
        _m_found_by_names_no_cell,
        "admission-2d",
    ),
    (
        "extract",
        "extract-output.valid.yaml",
        _m_confidence_disagrees_with_the_derivation,
        "derived-confidence-1",
    ),
    (
        "extract",
        "extract-output.valid.yaml",
        _m_measured_unit_dropped,
        "measured-coherence-1b",
    ),
    (
        "extract",
        "extract-output.valid.yaml",
        _m_technology_outside_the_purl_grammar,
        "vocabularies-4",
    ),
    (
        "synthesis",
        "scale-envelope-index.valid.yaml",
        _m_area_confidence_above_its_weakest,
        "synthesis-2",
    ),
]

#: The ANSWER KEY for the true plants, one per kind. It lives HERE, in the module the reviewer
#: under test never reads: recorded beside the fixtures it would turn every blind run into an
#: open-book one. Each plant is keyed to a numbered CONDITION, never to a validator rule — a
#: defect the gate catches proves the gate works, which was never in question.
PLANTED_DEFECTS = {
    "map-01.yaml": (
        "keyword-map",
        "scale-vocabulary-map.valid.yaml",
        "C7",
        "the probe note claims all three checks returned, and names a fourth channel it never "
        "opened; the `sources.active[]` posture for that row still says `not-fetched`, so the "
        "note and the record contradict each other and only a reader comparing them can say so",
    ),
    "search-01.yaml": (
        "search",
        "search-output-b5.valid.yaml",
        "C14",
        "a candidate's `stated_date` is the retrieval date rather than the source's own — the "
        "admission conjunct applied dishonestly, which is shape-legal and makes an undated claim "
        "look placeable",
    ),
    "extract-01.yaml": (
        "extract",
        "extract-output.valid.yaml",
        "C22",
        "`measured_value` is a rounded, unit-converted restatement of the source's figure rather "
        "than the number the source words; the arithmetic is right and the record is still wrong",
    ),
    "index-01.yaml": (
        "synthesis",
        "scale-envelope-index.valid.yaml",
        "C42",
        "`open_gap` asserts an absence with no receipt — it says nothing was found and never says "
        "what was looked for or where, which is the phrasing this type exists to refuse",
    ),
}


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


def _edit_sites(a, b, path="") -> list:
    """The SITES two documents differ at, so one logical edit counts as one."""
    if type(a) is not type(b):
        return [path or "(root)"]
    if isinstance(a, dict):
        out = []
        for key in set(a) | set(b):
            if key not in a or key not in b:
                out.append(f"{path}.{key}")
            else:
                out += _edit_sites(a[key], b[key], f"{path}.{key}")
        return out
    if isinstance(a, list):
        if len(a) != len(b):
            return [f"{path}[]"]
        out = []
        for i, (x, y) in enumerate(zip(a, b)):
            out += _edit_sites(x, y, f"{path}[{i}]")
        return out
    return [] if a == b else [path]


def _cli_argv(kind: str, path) -> list:
    argv = [kind, str(path)]
    if kind == "search":
        argv += ["--keyword-map", str(FIXTURES / "scale-vocabulary-map.valid.yaml")]
    if kind == "synthesis":
        argv += ["--extracts", str(FIXTURES / "extracts")]
    return argv


def _run_cli(argv: list) -> tuple:
    """Exit code and the FAIL lines, through the SAME path a user runs."""
    import contextlib
    import io

    with contextlib.redirect_stdout(io.StringIO()) as out:
        code = V.main(argv)
    return code, [ln for ln in out.getvalue().splitlines() if ln.startswith("FAIL ")]


class TestEveryClauseFiresOnAConstructedMutation:
    """The per-clause cases, CONSTRUCTED rather than selected out of a fixture directory."""

    @pytest.mark.parametrize(("kind", "base", "mutate", "rule"), MUTATIONS)
    def test_the_mutation_fires_EXACTLY_its_clause(
        self, kind: str, base: str, mutate, rule: str, tmp_path
    ) -> None:
        doc = yaml.safe_load((FIXTURES / base).read_text())
        mutate(doc)
        target = tmp_path / base
        target.write_text(yaml.safe_dump(doc, sort_keys=False))
        companion = (FIXTURES / base).with_suffix(".md")
        if companion.exists():
            target.with_suffix(".md").write_text(companion.read_text())
        code, found = _run_cli(_cli_argv(kind, target))
        assert found and found[0].startswith(f"FAIL {rule}:"), found
        assert len(found) == 1, found
        assert code == 1, code

    def test_a_VALID_purl_passes(self, tmp_path) -> None:
        """The positive path, CONSTRUCTED.

        Correcting the calibration extract removed the last `technology` value in any fixture —
        the source names no engine, so `null` is the honest record — and the only remaining
        coverage of the purl grammar was the mutation that violates it. An absent instance is
        worse than a wrong one, because the wrong one gets caught.
        """
        doc = yaml.safe_load((FIXTURES / "extract-output.valid.yaml").read_text())
        doc["episodes"][0]["technology"] = "pkg:generic/duckdb@1.1"
        target = tmp_path / "extract-output.valid.yaml"
        target.write_text(yaml.safe_dump(doc, sort_keys=False))
        target.with_suffix(".md").write_text(
            (FIXTURES / "extract-output.valid.md").read_text()
        )
        assert _run_cli(_cli_argv("extract", target)) == (0, [])

    @pytest.mark.parametrize(("kind", "base", "mutate", "rule"), MUTATIONS)
    def test_the_UNMUTATED_base_is_clean(
        self, kind: str, base: str, mutate, rule: str, tmp_path
    ) -> None:
        """Run the guard over the unmutated corpus before believing what it says about a mutant."""
        target = tmp_path / base
        target.write_text((FIXTURES / base).read_text())
        companion = (FIXTURES / base).with_suffix(".md")
        if companion.exists():
            target.with_suffix(".md").write_text(companion.read_text())
        code, found = _run_cli(_cli_argv(kind, target))
        assert (code, found) == (0, []), (code, found)


class TestC8aThePlantedFixtures:
    """C8a — shape-legal, gate-passing, keyed to a CONDITION, answer key not beside them. EC1a."""

    @pytest.mark.parametrize("name", sorted(PLANTED_DEFECTS))
    def test_it_PASSES_the_gate_at_exit_0(self, name: str) -> None:
        """The whole point. A plant the validator refuses never reaches the reviewer under test."""
        kind, _, _, _ = PLANTED_DEFECTS[name]
        code, found = _run_cli(_cli_argv(kind, PLANTED / name))
        assert (code, found) == (0, []), (code, found)

    @pytest.mark.parametrize("name", sorted(PLANTED_DEFECTS))
    def test_it_differs_from_its_base_in_EXACTLY_ONE_edit(self, name: str) -> None:
        _, base, _, _ = PLANTED_DEFECTS[name]
        changed = _edit_sites(
            yaml.safe_load((FIXTURES / base).read_text()),
            yaml.safe_load((PLANTED / name).read_text()),
        )
        # EXACTLY one. The guard shipped `1 <= n <= 2` with no comment and no plant using the
        # slack, while EC24, this test's own name and the fixtures README all said one.
        assert len(changed) == 1, sorted(changed)

    @pytest.mark.parametrize("name", sorted(PLANTED_DEFECTS))
    def test_it_is_keyed_to_a_CONDITION_that_exists(self, name: str) -> None:
        declared = set(
            re.findall(
                r"^\*\*(C\d+) — ",
                (TWIN / "references" / "conditions.md").read_text(),
                re.M,
            )
        )
        _, _, cond, _ = PLANTED_DEFECTS[name]
        assert cond in declared, (
            f"{name} is keyed to {cond}, which no condition declares"
        )

    @pytest.mark.parametrize("name", sorted(PLANTED_DEFECTS))
    def test_it_NAMES_no_rule_and_no_condition_of_its_own(self, name: str) -> None:
        """A fixture that hints at what is wrong with it turns a blind run into an open-book one.

        The first build shipped `# RULE:` and `# WHY:` headers stating the defect outright, and a
        blind run was spent on them.
        """
        text = (PLANTED / name).read_text()
        for needle in ("RULE:", "WHY:", "PLANT", "defect", "wrong is"):
            assert needle not in text, f"{name} names its own answer: {needle}"
        header = "".join(ln + "\n" for ln in text.splitlines() if ln.startswith("#"))
        assert header == self._header(), f"{name}'s header is not the shared one"

    @staticmethod
    def _header() -> str:
        """The header every plant carries, byte for byte.

        Identical across all four so it cannot carry a per-file hint; asserted rather than
        assumed, because the previous set's headers carried the answer outright.
        """
        first = sorted(PLANTED_DEFECTS)[0]
        return "".join(
            ln + "\n"
            for ln in (PLANTED / first).read_text().splitlines()
            if ln.startswith("#")
        )

    def test_the_answer_key_covers_every_file_and_no_others(self) -> None:
        on_disk = {p.name for p in PLANTED.glob("*.yaml")}
        assert on_disk == set(PLANTED_DEFECTS), (
            f"unkeyed: {sorted(on_disk - set(PLANTED_DEFECTS))}, "
            f"keyed but absent: {sorted(set(PLANTED_DEFECTS) - on_disk)}"
        )

    def test_there_is_one_plant_per_KIND(self) -> None:
        assert {v[0] for v in PLANTED_DEFECTS.values()} == {
            "keyword-map",
            "search",
            "extract",
            "synthesis",
        }

    def test_the_README_states_the_exit_code_the_gate_MEASURES(self) -> None:
        """It said the plants gate at exit 0 while all nine exited 1, and nothing compared them."""
        measured = {
            _run_cli(_cli_argv(PLANTED_DEFECTS[n][0], PLANTED / n))[0]
            for n in PLANTED_DEFECTS
        }
        assert measured == {0}, measured
        # Flattened: the README wraps, and the first version of this check failed on a CORRECT
        # file because "exit 0" fell across a line break. Same hazard as every other substring
        # guard in this module.
        flat = " ".join((PLANTED / "README.md").read_text().split())
        (code,) = measured
        assert f"exit {code}" in flat, flat[:300]
        for other in {0, 1, 2} - measured:
            assert f"exit {other}" not in flat, f"the README also states exit {other}"


class TestC7jTheConditionFilesAuthoredShape:
    """C7j — the shape has broken twice in consecutive commits, in opposite directions.

    One reformat left 40 of 41 bold leads closing mid-phrase on a function word. The repair pass
    rebuilt 40 of those 41, skipped the one its own commit message was written about, and ran two
    sentences together in 17 more. Both passed the whole suite: nothing was checking.
    """

    @staticmethod
    def _text() -> str:
        return (TWIN / "references" / "conditions.md").read_text()

    @staticmethod
    def _leads() -> list:
        return [
            (int(m.group(1)), " ".join(m.group(2).split()))
            for m in re.finditer(
                r"\*\*C(\d+) — (.*?)\*\*",
                TestC7jTheConditionFilesAuthoredShape._text(),
                re.S,
            )
        ]

    def test_every_lead_is_a_COMPLETE_SENTENCE(self) -> None:
        bad = [(n, lead[-48:]) for n, lead in self._leads() if not lead.endswith(".")]
        assert not bad, bad

    def test_no_lead_closes_on_a_FUNCTION_WORD(self) -> None:
        """The defect the first reformat shipped 40 times: `…it names a signal every**`.

        A period alone does not catch it — a lead can end in a period and still be a fragment —
        so the last word before it is checked against the closed class that cannot end a clause.
        """
        stop = {
            "a",
            "an",
            "the",
            "and",
            "or",
            "but",
            "of",
            "every",
            "each",
            "its",
            "their",
            "which",
            "who",
            "that",
            "than",
            "into",
            "per",
        }
        bad = [
            (n, lead[-48:])
            for n, lead in self._leads()
            if re.sub(r"[^a-z]", "", lead.rstrip(".").split()[-1].lower()) in stop
        ]
        assert not bad, bad

    def test_no_lead_SWALLOWS_a_second_sentence(self) -> None:
        """The defect the repair pass shipped 17 times.

        A lowercase word followed by a capitalised one INSIDE the bold, with no sentence break
        between them, is two sentences the emphasis has run together. Backticked spans are
        stripped first: `producer: references/…` and `holds: false` are not sentence boundaries.
        """
        assert not self._swallowed(self._text()), self._swallowed(self._text())

    @staticmethod
    def _swallowed(source: str) -> list:
        """Two sentences the emphasis has run together, in any of the file's three idioms.

        The first version required a lowercase letter before the break and two lowercase letters
        after it. Measured against the 17 leads it was written for, it caught 10: an ALL-CAPS word
        before the break is this file's dominant emphasis (30+ leads), and `A note…` / `A map…` /
        `A band…` is its most common second-sentence opener — a single capital letter followed by
        a space, which `[A-Z][a-z]` cannot match. Both blind spots were the house style.
        """
        out = []
        for m in re.finditer(r"\*\*C(\d+) — (.*?)\*\*", source, re.S):
            lead = " ".join(m.group(2).split())
            # Backticked spans become a single token: `holds: false` is not a sentence break, and
            # a backtick run reduced to `X X` used to hide a break between two of them.
            # The placeholder is a LOWERCASE word. Substituting `X` made every backticked span a
            # one-letter capital, so the `[A-Z]\s` branch matched 22 correct leads on the
            # placeholder itself — a guard widened into uselessness by its own scaffolding.
            plain = re.sub(r"`[^`]*`", "codespan", lead)
            # `A\s(?=[a-z`])`, not `[A-Z]\s`: the broad form flagged a CORRECT sibling lead,
            # `Every admitted source STATES A METHOD.`, because `A ` before a capital looked like
            # a sentence opener. The idiom this catches is the article — `A note`, `A map`,
            # `A band`, `A `stated_date`` — which is always followed by a lowercase word or a
            # codespan.
            if re.search(r"(?:[a-z,]|[A-Z]{2})\s+(?:[A-Z][a-z]|A\s(?=[a-z`]))", plain):
                out.append((m.group(1), lead[:70]))
        return out

    def test_the_swallowed_check_FIRES_on_the_leads_that_actually_SHIPPED(self) -> None:
        """Calibrated against the FILE, not against samples written from memory.

        The first calibration used seven hand-written approximations, which is a
        re-implementation of the defect and tests the re-implementation. Measured against the
        real pre-repair text, the check catches sixteen of the seventeen broken leads, and the sixteen are embedded below.

        WHAT IT DOES NOT COVER (contract §9e): the seventeenth is a break whose second sentence
        OPENS with a codespan — "…never a `sanitization` posture `clean` asserts a read…" — where
        substitution leaves no capital at the boundary and nothing distinguishes it from one long
        noun phrase. A length bound does not separate it either: it is 147 characters and five
        correct leads in the shipped file are longer. That lead is gone for a different reason
        (its condition was unfilable and was repointed), and the shape is recorded here as open
        rather than described as closed — the earlier docstring named two blind spots and implied
        it had closed the class.
        """
        caught = {n for n, _ in self._swallowed("\n\n".join(self.SHIPPED_BROKEN_LEADS))}
        assert len(caught) == len(self.SHIPPED_BROKEN_LEADS), sorted(caught)

    #: The leads the repair commit rewrote THAT THIS SHAPE CAN SEE, VERBATIM from the file it rewrote them
    #: in. Reconstructed samples are a re-implementation of the defect, which tests the
    #: reconstruction; these are the strings that actually shipped.
    SHIPPED_BROKEN_LEADS = (
        "**C6 — "
        "Each angle verdict FOLLOWS from the classification Read the angle's `predicate` in `prod"
        "ucer: references/source-registry.yaml` and evaluate it against the transcribed band your"
        "self: a `holds: false` names a deciding value that really decides it, and a `holds: true"
        "` on a conditional angle means the predicate really fires."
        "**",
        "**C7 — "
        "The probe note describes what the three checks actually returned A note that says a chan"
        "nel is open where the record says otherwise is a finding."
        "**",
        "**C10 — "
        "`scope_guard` is internally consistent with the groups Every `shared_terms[]` entry name"
        "s a term BOTH its groups actually carry and an `owner` that is one of them — a term decl"
        "ared shared with a group that does not have it de-duplicates a query that was never goin"
        "g to run twice."
        "**",
        "**C11 — "
        "`assumptions[]` records what the author had to assume A map that assumed something and r"
        "ecorded nothing is a finding even when the assumption was reasonable."
        "**",
        "**C13 — "
        "Each candidate's `url` RESOLVES to what the row claims it is The gate checks the field i"
        "s present (`admission`); whether it resolves is yours."
        "**",
        "**C14 — "
        "The admission conjuncts were applied HONESTLY A `stated_date` copied from the retrieval "
        "date rather than the source is the failure this condition exists for — an undated claim "
        "cannot be placed, because what ages is the hardware and managed-service generation under"
        "neath it."
        "**",
        "**C15 — "
        "Admission is RECORDED in both directions Every unadmitted row's `reason_class` is the on"
        "e that actually applies and its `reason` says what was looked for — and, the other way, "
        "nothing that belongs in `unadmitted[]` is sitting in `candidates[]`."
        "**",
        "**C16 — "
        "A zero is read against the ROW, not against the cell Look the row up in `producer: refer"
        "ences/source-registry.yaml`: a zero from a `complete_listing: false` row says only that "
        "the query did not match, and recording it as evidence of absence is a finding."
        "**",
        "**C18 — "
        "`bound.cap` is the registry's value TRANSCRIBED VERBATIM Look the angle up in `producer:"
        " references/source-registry.yaml` and compare."
        "**",
        "**C22 — "
        "The episode's `claim` does not reach past the evidence behind it The quote lives on the "
        "upstream SEARCH candidate, not on the episode — `producer: references/extraction-templat"
        "e-guide.md`'s episode field list carries no `evidence_quote` — so read the candidate tha"
        "t admitted this source, or the body's `## Method and configuration`, and ask whether the"
        " claim asserts more than either supports."
        "**",
        "**C23 — "
        "`evidence_class` fits what the source IS A vendor's own blog post describing its own sys"
        "tem is not `independent-verification` however measured it is."
        "**",
        "**C29 — "
        "The episode's `cause_class` is a FAILURE MODE, not the map's field of the same name Two "
        "levels, two vocabularies, disjoint members — and the gate checks membership, not meaning"
        "."
        "**",
        "**C30 — "
        "`load_class` sub-keys record what the SOURCE states A band filled in from the project's "
        "own classification rather than from the source is a finding, and the gate cannot see it "
        "— it re-derives only the `primary_dimension`'s sub-key, and only where a boundary is pub"
        "lished."
        "**",
        "**C32 — "
        "The four body sections `producer: references/extraction-template-guide.md` names say som"
        "ething The gate checks presence and non-triviality; whether `## Method and configuration"
        "` actually explains how each number was obtained — and whether `## Transferability` comp"
        "ares the band it was measured at against this project's — is yours."
        "**",
        "**C34 — "
        "Every `evidence[]` id resolves to an episode that says what the area claims it says The "
        "gate checks resolution (`synthesis`); whether the episode supports the pattern is yours."
        "**",
        "**C37 — "
        "A `blocks_requirement: true` hard limit really blocks a requirement this project has It "
        "is the only blocker-producing lens, and a false one costs more than a missed one."
        "**",
    )

    def test_every_cross_reference_is_an_EXPLICIT_id_that_RESOLVES(self) -> None:
        text = self._text()
        declared = {int(x) for x in re.findall(r"\*\*C(\d+) — ", text)}
        assert not re.findall(r"the condition (?:above|below)", text), (
            "a relative pointer is correct only until something is inserted, and two were "
            "found stale in this file"
        )
        cited = {int(x) for x in re.findall(r"(?<![A-Za-z`])C(\d+)\b", text)}
        assert cited <= declared, sorted(cited - declared)

    def test_the_conditions_are_CONTIGUOUS_from_one(self) -> None:
        nums = [n for n, _ in self._leads()]
        assert nums == list(range(1, len(nums) + 1)), nums


class TestC7kNoConditionIsUnfilable:
    """C7k — a condition the schema already decides is satisfied by every artifact that reaches a
    reviewer, so it can never be filed.

    Two shipped. One asked for a threshold its own design forbade; one asked that a `skipped`
    source row carry `cause_class` and a `cause` and no `sanitization` posture — which is that
    object's `required` list, plus `additionalProperties: false`, plus `map-completeness-1g`.
    Both were found by fresh review rather than by any check.

    The rule is schema-DERIVED, not a word list: a DUTY that names two or more `required` keys of
    one closed object AND a field that object forbids is restating `required` plus
    `additionalProperties: false`. It reads the LEAD only — the bold duty — because the
    elaboration after it is rationale, and four correct conditions mention a forbidden-elsewhere
    field there while asking something the schema cannot decide.

    WHAT IT DOES NOT COVER (contract §9e): the CONTENT half. A duty whose verb asks whether a
    value is consistent, faithful, honest or measured is judgement and is skipped by design, so a
    condition that names the right fields and then asks a gated question anyway is invisible to
    it. It also says nothing about the FIRST defect's shape — a threshold the design forbids is
    not a schema fact — which is why that one is recorded in the plan rather than guarded here.
    """

    #: Verbs that ask about a VALUE rather than a key's presence. Their presence means the duty
    #: is judgement, whatever fields it names.
    CONTENT = (
        "consistent",
        "say",
        "says",
        "establish",
        "restate",
        "weighable",
        "actually",
        "really",
        "faithful",
        "follows",
        "fits",
        "supports",
        "defensible",
        "resolve",
        "verbatim",
        "observable",
        "honest",
        "measured",
        "converged",
        "proportionate",
        "equals",
        "independent",
        "re-appliable",
        "transcribed",
        "populated",
        "describes",
        "reach",
        "phrased",
        "applied",
        "blocks",
        "exclude",
    )

    @staticmethod
    def _closed_shapes() -> list:
        """Every `additionalProperties: false` object's (properties, required), all four schemas."""
        import json

        out: list = []

        def walk(node):
            if isinstance(node, dict):
                if node.get("additionalProperties") is False and node.get("properties"):
                    out.append(
                        (set(node["properties"]), set(node.get("required") or ()))
                    )
                for v in node.values():
                    walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)

        for path in sorted((PKG / "schemas").glob("*.json")):
            walk(json.loads(path.read_text()))
        return out

    @classmethod
    def _unfilable(cls, source: str) -> list:
        shapes = cls._closed_shapes()
        assert shapes, (
            "the schemas declare no closed object — the check would pass vacuously"
        )
        out = []
        for m in re.finditer(r"\*\*C(\d+) — (.*?)\*\*", source, re.S):
            lead = " ".join(m.group(2).split())
            if any(w in lead.lower() for w in cls.CONTENT):
                continue
            judged = {
                f.strip("`").split(".")[0].split("[")[0]
                for f in re.findall(r"`([a-z_]+(?:\.[a-z_]+)*(?:\[\])?)`", lead)
            }
            for props, required in shapes:
                if len(judged & required) >= 2 and (judged - props):
                    out.append(
                        (m.group(1), sorted(judged & required), sorted(judged - props))
                    )
                    break
        return out

    def test_no_shipped_condition_is_unfilable(self) -> None:
        assert not self._unfilable((TWIN / "references" / "conditions.md").read_text())

    def test_the_check_FIRES_on_the_condition_that_shipped(self) -> None:
        """A guard silent over a clean corpus proves nothing until it is shown the real defect."""
        shipped = (
            "**C9 — A SKIPPED row carries `cause_class` and a `cause` and never a "
            "`sanitization` posture `clean` asserts a read, and you do not read a row you "
            "skipped.**"
        )
        assert self._unfilable(shipped), (
            "the guard cannot see the defect it was written for"
        )


class TestC8iEveryReferencesTableNamesEveryReference:
    """C8i — the twin's table described `references/fixtures/` without its `extracts/`, which the
    fixtures README names and without which the synthesis fixture cannot reach exit 0."""

    #: The ONE file deliberately absent from a References table: it maps rule ids to authoring
    #: task ids, which is a maintainer's record and not something a dispatched agent reads. Its
    #: absence is already asserted from the other side by the rule-owner tests.
    TABLE_EXEMPT = {"references/rule-owners.yaml"}

    @staticmethod
    def _rows(pkg) -> set:
        table = (pkg / "SKILL.md").read_text()
        table = table[table.index("## References") :]
        return set(re.findall(r"^\| `([^`]+)`", table, re.M))

    @pytest.mark.parametrize("pkg_name", ["producer", "twin"])
    def test_every_row_names_a_path_that_EXISTS(self, pkg_name: str) -> None:
        pkg = PKG if pkg_name == "producer" else TWIN
        for row in self._rows(pkg):
            if "{" in row:  # a brace expansion, e.g. `references/angles/{a1,a2}.md`
                stem, _, rest = row.partition("{")
                members, _, suffix = rest.partition("}")
                targets = [pkg / f"{stem}{m}{suffix}" for m in members.split(",")]
            else:
                targets = [pkg / row]
            for target in targets:
                assert target.exists(), f"{pkg.name}'s References table names {target}"

    @pytest.mark.parametrize("pkg_name", ["producer", "twin"])
    def test_every_file_under_references_is_NAMED_by_a_row(self, pkg_name: str) -> None:
        pkg = PKG if pkg_name == "producer" else TWIN
        rows = self._rows(pkg)
        covered = set()
        for row in rows:
            if "{" in row:
                stem, _, rest = row.partition("{")
                members, _, suffix = rest.partition("}")
                covered |= {f"{stem}{m}{suffix}" for m in members.split(",")}
            else:
                covered.add(row)
        for path in sorted((pkg / "references").rglob("*")):
            if not path.is_file():
                continue
            rel = str(path.relative_to(pkg))
            if rel in self.TABLE_EXEMPT:
                continue
            named = rel in covered or any(
                c.endswith("/") and rel.startswith(c) for c in covered
            )
            assert named, f"{pkg.name}'s References table does not name {rel}"


class TestC7lTheWorkedExampleQuotesNothingThatShips:
    """C7l — the twin's only worked example was built out of a shipped fixture, inverted.

    It said "the source's own table says '1,200,000 rows/second'" against a source that says
    `1.2M rows/s` twice and has no table, so a reviewer calibrating on it files the condition
    against the value that IS verbatim. And `1,200,000 rows/second` is a planted fixture's exact
    defect string, printed with its condition id in the file every reviewer reads first — the
    answer key to one plant in four, three files from the commit that stripped `# RULE:` headers
    off nine fixtures to close a smaller version of the same leak.
    """

    @staticmethod
    def _example_tokens(pkg) -> set:
        """Every backticked or double-quoted span inside a fenced example block in a SKILL.md."""
        text = (pkg / "SKILL.md").read_text()
        # `[a-z]*` after the opening fence: a future example inside ```yaml would otherwise be
        # silently unchecked, which is a guard that stops looking rather than one that passes.
        blocks = re.findall(r"^```[a-z]*\n(.*?)^```", text, re.M | re.S)
        out: set = set()
        for block in blocks:
            out |= set(re.findall(r"`([^`\n]+)`", block))
            out |= set(re.findall(r'"([^"\n]+)"', block))
        return {tok for tok in out if len(tok) > 3}

    @staticmethod
    def _shipped_corpus() -> str:
        parts = []
        for root in (PKG / "scripts" / "fixtures", TWIN / "references" / "fixtures"):
            for path in sorted(root.rglob("*")):
                if path.is_file():
                    parts.append(path.read_text(errors="ignore"))
        return "\n".join(parts)

    #: Where a worked example lives today. The PRODUCER ships none, so its half of the token
    #: check iterates an empty set and passes unconditionally — a vacuum, not a pass. Declared
    #: here so adding one to the producer turns its check on rather than leaving it asleep.
    PACKAGES_WITH_AN_EXAMPLE = {"reviewing-scale-prior-art-survey"}

    def test_the_declared_example_packages_are_the_ones_that_HAVE_examples(
        self,
    ) -> None:
        """Non-vacuity, both directions. An example that disappears must not pass as clean, and
        one that appears must not be checked by nothing."""
        actual = {pkg.name for pkg in (PKG, TWIN) if self._example_tokens(pkg)}
        assert actual == self.PACKAGES_WITH_AN_EXAMPLE, {
            "has an example": sorted(actual),
            "declared": sorted(self.PACKAGES_WITH_AN_EXAMPLE),
        }

    def test_the_example_cites_a_condition_NO_PLANT_is_keyed_to(self) -> None:
        """The METHOD half, which the token check cannot see.

        Removing the leaked defect string, the replacement example demonstrated the exact
        comparison the MAP plant is built on — a probe note read against a row's own posture. The
        tokens were clean and the technique was handed over, so the next blind run on that plant
        would have measured nothing either. The keyed set is DERIVED from the answer key.
        """
        keyed = {cond for _, _, cond, _ in PLANTED_DEFECTS.values()}
        assert keyed, "the answer key is empty — the CHECK is broken, not the example"
        for pkg in (PKG, TWIN):
            text = (pkg / "SKILL.md").read_text()
            for block in re.findall(r"^```[a-z]*\n(.*?)^```", text, re.M | re.S):
                cited = set(re.findall(r"(?<![A-Za-z`])(C\d+)\b", block))
                assert not (cited & keyed), (
                    f"{pkg.name}'s worked example walks through {sorted(cited & keyed)}, "
                    "which a calibration fixture is keyed to"
                )

    @staticmethod
    def _vocabulary() -> set:
        """Schema property names and enum members — SHARED by design, and not data.

        An example must be able to say `sanitization.status` and `clean`; what it may not do is
        reuse a fixture's ids, quotes or numbers. The line is vocabulary against data, and the
        vocabulary is DERIVED from the schemas rather than listed here.
        """
        import json

        out: set = set()

        def walk(node):
            if isinstance(node, dict):
                for key, value in node.items():
                    if key == "properties" and isinstance(value, dict):
                        out.update(value)
                    if key == "enum" and isinstance(value, list):
                        out.update(str(v) for v in value)
                    walk(value)
            elif isinstance(node, list):
                for v in node:
                    walk(v)

        for path in sorted((PKG / "schemas").glob("*.json")):
            walk(json.loads(path.read_text()))
        return out

    @classmethod
    def _is_vocabulary(cls, token: str) -> bool:
        vocab = cls._vocabulary()
        parts = [p for p in re.split(r"[.\[\]:\s]+", token) if p]
        return bool(parts) and all(p in vocab for p in parts)

    @pytest.mark.parametrize("pkg_name", ["producer", "twin"])
    def test_no_example_token_occurs_in_any_shipped_fixture(
        self, pkg_name: str
    ) -> None:
        pkg = PKG if pkg_name == "producer" else TWIN
        corpus = self._shipped_corpus()
        leaks = sorted(
            tok
            for tok in self._example_tokens(pkg)
            if tok in corpus and not self._is_vocabulary(tok)
        )
        assert not leaks, f"{pkg.name}'s worked example quotes shipped content: {leaks}"

    def test_the_leak_that_shipped_would_be_CAUGHT(self) -> None:
        """The example that shipped, replayed: a defect string is not vocabulary."""
        shipped = "1,200,000 rows/second"
        assert shipped in self._shipped_corpus(), (
            "the plant no longer carries the string this test replays"
        )
        assert not self._is_vocabulary(shipped), (
            "the vocabulary exemption would have let the shipped leak through"
        )


class TestTheAccessStatusVocabularyIsONE:
    """A field name shared across two levels with two vocabularies is the `cause_class` trap.

    The registry's `access_status` carried `polite-pool`; the map schema, the extract schema and
    the validator's source-record check all listed five members without it. So a `polite-pool`
    row's posture could not be recorded downstream at all, and the calibration map flattened five
    of them to `open` under an assumption that said the value was INHERITED from the registry.
    Nothing compared the vocabularies.
    """

    @staticmethod
    def _registry_values() -> set:
        reg = yaml.safe_load(REGISTRY.read_text())
        return {
            r.get("access_status") for r in reg["sources"] if r.get("access_status")
        }

    @staticmethod
    def _schema_enum(path, *keys) -> set:
        import json

        node = json.loads((PKG / "schemas" / path).read_text())
        for key in keys:
            node = node[key]
        return set(node["enum"])

    def test_the_map_schema_accepts_every_registry_value(self) -> None:
        declared = self._schema_enum(
            "scale-vocabulary-map.schema.json",
            "properties",
            "sources",
            "properties",
            "active",
            "items",
            "properties",
            "access_status",
        )
        assert self._registry_values() <= declared, sorted(
            self._registry_values() - declared
        )

    def test_the_extract_schema_accepts_every_registry_value(self) -> None:
        declared = self._schema_enum(
            "extract-output.schema.json",
            "properties",
            "source",
            "properties",
            "access_status",
        )
        assert self._registry_values() <= declared, sorted(
            self._registry_values() - declared
        )

    @staticmethod
    def _validator_tuples() -> list:
        """Every `access_status` membership tuple in the validator, read from its AST."""
        import ast

        tree = ast.parse((HERE / "validate_scale_prior_art.py").read_text())
        out = [
            {
                e.value
                for e in n.elts
                if isinstance(e, ast.Constant) and isinstance(e.value, str)
            }
            for n in ast.walk(tree)
            if isinstance(n, ast.Tuple)
            and {"open", "blocked"}
            <= {e.value for e in n.elts if isinstance(e, ast.Constant)}
        ]
        # The COUNT, not merely "at least one". The predicate selects tuples by two ANCHOR
        # members, so deleting an anchor removes that tuple from the population instead of
        # failing: dropping `"blocked"` from the `vocabularies-7` tuple left all 384 tests green
        # while the validator would refuse a legal `access_status`. Two sites carry this
        # vocabulary and the number is asserted, which is the same move the example-package and
        # producer-doc declarations make — "unreached" and "nothing to check" are otherwise
        # indistinguishable from outside.
        assert len(out) == 2, (
            f"{len(out)} access_status membership tuples found, expected 2 — either a site was "
            "added, or an ANCHOR member was deleted and its tuple silently left the population"
        )
        return out

    def test_the_validators_source_record_check_accepts_every_registry_value(
        self,
    ) -> None:
        """Read from the SOURCE, not restated: the schema and the check drifted independently."""
        for members in self._validator_tuples():
            assert self._registry_values() <= members, sorted(
                self._registry_values() - members
            )

    def test_the_three_DECLARED_vocabularies_are_the_SAME_SET(self) -> None:
        """The class this guard exists for, closed.

        The first version asserted each site against the values the registry rows happen to USE —
        two of six — so the map schema, the extract schema and the validator tuple could each hold
        a different member set and stay green. Deleting `crawl-delayed` from one schema passed the
        whole suite. Equality between the DECLARED vocabularies is the check; the registry's used
        values are then a subset of that one set.
        """
        map_enum = self._schema_enum(
            "scale-vocabulary-map.schema.json",
            "properties",
            "sources",
            "properties",
            "active",
            "items",
            "properties",
            "access_status",
        )
        extract_enum = self._schema_enum(
            "extract-output.schema.json",
            "properties",
            "source",
            "properties",
            "access_status",
        )
        assert map_enum == extract_enum, {
            "map only": sorted(map_enum - extract_enum),
            "extract only": sorted(extract_enum - map_enum),
        }
        for members in self._validator_tuples():
            assert members == map_enum, {
                "validator only": sorted(members - map_enum),
                "schema only": sorted(map_enum - members),
            }
        assert self._registry_values() <= map_enum


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
            "claim",
            "classification",
            "corpus_version",
            "default_pattern",
            "evidence_quote",
            "expansion_cap",
            "failure_classes",
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
            "ran",
            "reason_class",
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


class TestEC27TheScopeDocumentExists:
    """EC27 — every file a condition names is staged, in both packages.

    5i's packet named a scope document that did not exist, so the transcription condition could
    only ever record "unjudgeable". The map fixture's `meta.scope_ref` is the path a reviewer is
    told to judge the declared band against.
    """

    def test_the_map_fixtures_scope_ref_resolves(self, clean_map: dict) -> None:
        assert (PKG / clean_map["meta"]["scope_ref"]).exists()

    def test_the_twin_stages_it_too(self) -> None:
        assert (TWIN / "references" / "fixtures" / "scope-logscan-cli.md").exists()

    def test_the_scope_states_the_band_the_map_transcribes(
        self, clean_map: dict
    ) -> None:
        text = (PKG / clean_map["meta"]["scope_ref"]).read_text()
        for leaf, value in clean_map["meta"]["classification"]["scale"].items():
            assert leaf in text, leaf
            assert str(value) in text, f"{leaf}: {value}"


class TestI9TheTwoPackagesStayInSync:
    """The files duplicated across both packages, asserted EQUAL.

    They were hand-mirrored across three consecutive commits, and the drift had already happened
    once: the twin's calibration extract shipped with no companion `.md`, so running the gate on
    the reviewing package's own copy returned exit 1 — on the artifact whose SKILL.md tells the
    reviewer it has already passed.
    """

    DUPLICATED = (
        "sources.md",
        "fixtures/scale-vocabulary-map.valid.yaml",
        "fixtures/search-output-b5.valid.yaml",
        "fixtures/extract-output.valid.yaml",
        "fixtures/extract-output.valid.md",
        "fixtures/scale-envelope-index.valid.yaml",
        "fixtures/scope-logscan-cli.md",
        "fixtures/source-techempower-run-3.md",
        "fixtures/extracts/extract-WEB-techempower-run-3.yaml",
        "fixtures/extracts/extract-WEB-techempower-run-3.md",
    )

    @pytest.mark.parametrize("name", DUPLICATED)
    def test_each_copy_is_byte_identical(self, name: str) -> None:
        twin = TWIN / "references" / name
        producer = PKG / (
            "references/sources.md" if name == "sources.md" else f"scripts/{name}"
        )
        assert twin.exists(), twin
        assert producer.exists(), producer
        assert twin.read_bytes() == producer.read_bytes(), name

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
    def test_ALL_FOUR_twin_fixtures_gate_at_zero(self, argv: list[str]) -> None:
        """Its README says all four do, and only the extract one was ever checked.

        The guard was added last cycle for the copy whose companion `.md` had gone missing, and
        stopped one file short of the synthesis copy — which could not reach 0 at all, because
        the twin shipped no `extracts/` directory beside it.
        """
        import contextlib
        import io

        base = TWIN / "references" / "fixtures"
        resolved = [
            a
            if a.startswith("-")
            else str(base / a)
            if "." in a or a == "extracts"
            else a
            for a in argv
        ]
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = V.main(resolved)
        assert code == 0, out.getvalue()

    def test_the_twins_calibration_extract_PASSES_its_own_gate(self) -> None:
        # Its SKILL.md tells the reviewer "It has already passed the deterministic gate." That
        # sentence has to be true of the copy the reviewer is handed.
        import contextlib
        import io

        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = V.main(
                ["extract", str(TWIN / "references/fixtures/extract-output.valid.yaml")]
            )
        assert code == 0, out.getvalue()

    def test_every_extract_ARTIFACT_has_its_companion_body(self) -> None:
        # A missing `.md` is now a finding, so an extract fixture without one is wrong in TWO
        # ways — and a fixture wrong in two ways proves nothing about either.
        for path in sorted(FIXTURES.rglob("*.yaml")):
            doc = yaml.safe_load(path.read_text())
            if (
                isinstance(doc, dict)
                and doc.get("outcome") == "extracted"
                and "episodes" in doc
            ):
                assert path.with_suffix(".md").exists(), path


class TestI3TheTenQualitySignals:
    """C4c's exit: the ten signals ship, and the condition that judges `score` can reach them."""

    def test_ten_numbered_signals_ship(self) -> None:
        text = (PKG / "references" / "quality-filter.md").read_text()
        rows = re.findall(r"^\| (\d+) \| \*\*", text, re.M)
        assert [int(r) for r in rows] == list(range(1, 11))

    def test_they_are_the_SPECS_ten_and_not_another_ten(self) -> None:
        """Any ten rows numbered 1..10 satisfied the shape test; these must be THE ten.

        The first shipped set silently swapped three of the spec's signals for two of its own
        invention, and the reviewer would then have been counting a different ten from the one
        the design records. Under the single-source rule the defining section wins.
        """

        # PINNED here rather than read from the authoring repo's spec by absolute path: that
        # read passed only where both repos sat side by side, and the installed skill shipped a
        # suite that could not run. This list is the spec's ten, transcribed once, and a change
        # to either side now shows up as a diff on this literal.
        def flat(text: str) -> str:
            return " ".join(text.lower().split())

        shipped = flat((PKG / "references" / "quality-filter.md").read_text())
        for phrase in (
            "configuration and its date",
            "load class",
            "measurement method",
            "independent verification",
            "regression or limit",
            "system named",
            "before/after",
            "hardware and managed-service generation",
            "percentiles rather than",
            "cost stated",
        ):
            assert phrase in shipped, f"pinned as the spec's and not shipped: {phrase}"

    def test_the_condition_judging_score_names_the_file(self) -> None:
        conditions = (TWIN / "references" / "conditions.md").read_text()
        assert "quality-filter.md" in conditions

    def test_the_filing_threshold_is_not_one_the_design_forbids(self) -> None:
        # `score` is written after the queue is fixed and nothing truncates the extracts
        # directory, so "would this have changed what synthesis sees" can never be satisfied.
        conditions = (TWIN / "references" / "conditions.md").read_text()
        assert (
            "would have changed which records synthesis sees is worth a finding"
            not in conditions
        )
        assert "name the signals the source satisfies" in conditions


class TestEC6NoHostProgramReferencesShip:
    """These packages ship to projects that cannot see the program that authored them.

    Three sibling packages carry this guard and this pair did not, so a fresh review found six
    leaking lines in shippable files — a coordinator, two earlier surveys by codename, a playbook
    number and a scheduler-internal term. Case-insensitive and whole-package, because a sibling's
    case-sensitive version reported zero while a reference sat in a shippable file.
    """

    LEAK = re.compile(
        r"playbook ?#|spec L-|classification-schema|(?<![a-z-])5[a-j]\b|disk-authoritative|"
        r"this ticket|agents-hq|coordinator|project_prior_art",
        re.I,
    )

    #: The AUTHORING-PROGRAM half. `§` is forbidden OUTRIGHT rather than in the six phrasings the
    #: first version enumerated: it closed none of the class, and a fresh review found `§6`
    #: printing from a `FAIL` message plus 24 more section and task references in shippable
    #: files. The task-id needle requires a LETTER SUFFIX, because the twin's own conditions are
    #: numbered `C1` upward and a suffix-free pattern calls every one of them a leak.
    PROGRAM = re.compile(r"§|(?<![A-Za-z])[A-E]\d+[a-z]\d?(?![A-Za-z])")

    #: The ONE file whose VALUES are plan task ids — the map from rule id to owning task is what
    #: it is. Declared, not assumed: a second file acquiring task ids fails the sweep.
    PROGRAM_EXEMPT = {"rule-owners.yaml"}

    @staticmethod
    def _shippable() -> list[pathlib.Path]:
        """Everything a dispatched agent reads, the VALIDATOR included.

        Its `FAIL` messages print straight to an agent's console, so a host-program reference in
        one ships exactly as a reference in a guide would. The TEST MODULE is excluded and the
        next test asserts that rather than leaving it to be rediscovered.
        """
        out: list[pathlib.Path] = []
        for pkg in (PKG, TWIN):
            for suffix in ("*.md", "*.yaml", "*.json", "*.py"):
                out += [
                    p
                    for p in pkg.rglob(suffix)
                    if p.name != pathlib.Path(__file__).name
                ]
        return sorted(out)

    def test_no_shippable_file_names_the_authoring_program(self) -> None:
        offenders = [
            f"{p.relative_to(ROOT)}:{n}: {line.strip()[:80]}"
            for p in self._shippable()
            for n, line in enumerate(p.read_text(errors="ignore").splitlines(), 1)
            if self.LEAK.search(line)
        ]
        assert not offenders, offenders

    def test_no_shippable_file_names_the_AUTHORING_PROGRAM(self) -> None:
        """Scoped to what a DISPATCHED AGENT reads — the two packages, the validator included.

        The two companion design docs are deliberately outside this half and inside the
        absolute-path half: they are the authoring program's own record of the type, so naming a
        section or a task in them is what they are for.
        """
        offenders = [
            f"{p.relative_to(ROOT)}:{n}: {line.strip()[:80]}"
            for p in self._shippable()
            if p.name not in self.PROGRAM_EXEMPT
            for n, line in enumerate(p.read_text(errors="ignore").splitlines(), 1)
            if self.PROGRAM.search(line)
        ]
        assert not offenders, offenders

    def test_the_ONE_exemption_is_real_and_alone(self) -> None:
        """Asserted in both directions, so the exemption cannot quietly cover a second file."""
        leaking = {
            p.name
            for p in self._shippable()
            if any(
                self.PROGRAM.search(ln)
                for ln in p.read_text(errors="ignore").splitlines()
            )
        }
        assert leaking == self.PROGRAM_EXEMPT, {
            "leaking": sorted(leaking),
            "exempted": sorted(self.PROGRAM_EXEMPT),
        }

    def test_every_shippable_file_ends_with_a_NEWLINE(self) -> None:
        # A fold left one file in the pair without one, and it was the only such file in either
        # package — found by a reviewer diffing, not by anything here.
        bad = [
            str(p.relative_to(ROOT))
            for p in self._shippable()
            if p.read_bytes() and not p.read_bytes().endswith(b"\n")
        ]
        assert not bad, bad

    def test_the_test_module_is_deliberately_out_of_scope(self) -> None:
        # Its comments name the sibling packages each rule came from, and that provenance is how
        # a maintainer tells a considered divergence from a typo. An exemption nobody states is
        # indistinguishable from an oversight.
        assert pathlib.Path(__file__).resolve() not in {
            p.resolve() for p in self._shippable()
        }

    def test_no_shippable_file_reads_a_path_OUTSIDE_this_repository(self) -> None:
        """The blocker this class was written for.

        Two tests read the authoring repository by absolute path, so the suite was green only
        where both repos sat side by side: CI failed from a clean checkout, and `npx skills add`
        installed a suite no consumer could run. Three siblings already forbade the string.

        The needles are BUILT, so this file is not itself an occurrence of what it forbids — the
        self-match hazard this pair has hit four times, twice inside a guard written to close it.
        """
        outside = "ROOT" + ".parent"
        authoring = "agents" + "-hq"
        for path in self._shippable():
            text = path.read_text(errors="ignore").lower()
            assert outside.lower() not in text, (
                f"{path}: reads a path outside this repository"
            )
            assert authoring not in text, f"{path}: names the authoring repository"

    def test_this_module_reads_no_path_outside_the_repository_either(self) -> None:
        # It is excluded from `_shippable()`, so it needs its own assertion — an exemption that
        # exempts the file from every check is how the first version of this passed.
        mine = pathlib.Path(__file__).read_text()
        assert ("ROOT" + ".parent") not in mine, (
            "the test module reads outside the repository"
        )
