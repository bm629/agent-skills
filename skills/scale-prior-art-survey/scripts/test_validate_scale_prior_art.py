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
