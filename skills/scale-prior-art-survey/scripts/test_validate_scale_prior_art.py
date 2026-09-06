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
        # The shared engine keys off exactly this literal (in `tests/trigger_rules.py`; the line
        # number is deliberately not written — it moved once and the citation went stale). A registry
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


def _emitted_ids(
    tree, shapes=("positional", "keyword", "default", "positional-helper")
) -> set:
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
                # ANY keyword whose name ENDS in `rule`, not the literal `rule` alone. Adding
                # `empty_rule=` created a FOURTH id shape both this walk and the shared
                # cross-package count guard were blind to: a brand-new id could be emitted, be
                # absent from the owner map, and leave every count claim standing.
                if (
                    kw.arg
                    and kw.arg.endswith("rule")
                    and isinstance(kw.value, _ast.Constant)
                    and isinstance(kw.value.value, str)
                ):
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
                    # `endswith`, to match the keyword branch — and `isinstance(value, str)`,
                    # because `empty_rule: str | None = None` has a Constant default that is
                    # NOT a rule id. Widening one half without the other would have put `None`
                    # into the emitted set.
                    if (
                        name.endswith("rule")
                        and isinstance(default, _ast.Constant)
                        and isinstance(default.value, str)
                    ):
                        out.add(default.value)
    # FIFTH shape: a rule id threaded as a POSITIONAL argument into a helper that emits it. The
    # four shapes above all key on the name `rule` — a keyword, or a parameter default — and
    # `is_the_document(doc, name, rule, where, f)` takes it by position, so an id introduced
    # only that way would be emitted by the gate, absent from the owner map, absent from the
    # exit-class sweep, and would leave the rule count standing. Derived from the SIGNATURE:
    # any function whose parameters include one ending in `rule` contributes its callers'
    # constant argument at that index, so a sixth helper of the same shape is covered without
    # editing this.
    if "positional-helper" in shapes:
        # EVERY rule-bearing position, not one. `load_yaml(path, f, rule, empty_rule, …)` has
        # TWO, and assigning to a dict kept the LAST — so an id passed positionally as `rule`
        # was dropped while the walk's own comment claimed complete coverage. A helper with two
        # of them is the ordinary case here, not a corner.
        indices: dict = {}
        for node in _ast.walk(tree):
            if isinstance(node, _ast.FunctionDef) and node.name != "_fail":
                for i, arg in enumerate(node.args.args):
                    if arg.arg.endswith("rule"):
                        indices.setdefault(node.name, []).append(i)
        for node in _ast.walk(tree):
            if isinstance(node, _ast.Call) and getattr(node.func, "id", "") in indices:
                for i in indices[node.func.id]:
                    if len(node.args) > i:
                        arg = node.args[i]
                        if isinstance(arg, _ast.Constant) and isinstance(
                            arg.value, str
                        ):
                            out.add(arg.value)
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
            [
                "synthesis",
                "scale-envelope-index.valid.yaml",
                "--extracts",
                "extracts",
                "--queue",
                "extract-queue.valid.yaml",
            ],
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


class TestCurrencyRulesFire:
    """currency (1)-(3). Lens 8's landing site, and the two ways it can be opted out of.

    `currency-1` cannot go in `MUTATIONS`: a missing key co-fires `schema`, and that table
    asserts exactly one finding. Its only guard before this was a prose number in a deep-dive —
    deleting the rule and its owner-map line left the package suite green.
    """

    @staticmethod
    def _rules(mutate) -> set:
        doc = yaml.safe_load((FIXTURES / "scale-envelope-index.valid.yaml").read_text())
        mutate(doc)
        extracts = [
            yaml.safe_load(p.read_text())
            for p in sorted((FIXTURES / "extracts").glob("*.yaml"))
        ]
        f = V.Findings()
        V.check_synthesis(doc, extracts, f)
        return {r for r, _ in f.items}

    def test_a_TRAVERSAL_CRASH_is_the_authors_fault(self) -> None:
        """Exit 1, not 2. The file read and parsed; only its content was wrong.

        It filed under `input` — a PACKAGE-fault prefix — so a shape-illegal artifact exited 2,
        "a fault an artifact author CANNOT repair", while the handler's own comment said the
        opposite and an accompanying `schema` finding (exit 1 by design) already named it. The
        per-rule exit sweep asserts rule-to-class and structurally cannot see a fault filed under
        the wrong rule.
        """
        import contextlib
        import io
        import tempfile

        doc = yaml.safe_load((FIXTURES / "scale-envelope-index.valid.yaml").read_text())
        doc["areas"][0]["hard_limits"] = ["a string where a mapping belongs"]
        with tempfile.TemporaryDirectory() as td:
            target = pathlib.Path(td) / "i.yaml"
            target.write_text(yaml.safe_dump(doc))
            with contextlib.redirect_stdout(io.StringIO()) as out:
                code = V.main(
                    ["synthesis", str(target), "--extracts", str(FIXTURES / "extracts")]
                )
        found = [ln for ln in out.getvalue().splitlines() if ln.startswith("FAIL ")]
        assert code == 1, (code, found)
        assert any(ln.startswith("FAIL artifact-untraversable:") for ln in found), found
        assert not any(ln.startswith("FAIL input:") for ln in found), found
        assert not V.is_package_fault("artifact-untraversable")

    def test_a_PACKAGE_crash_is_NOT_the_authors_fault(self) -> None:
        """Exit 2, and the mirror of the test above.

        The blanket handler wrapped the WHOLE run, so renaming its rule to the artifact class
        sent a malformed registry — a package file the author cannot reach — back to the
        producing agent at exit 1. The artifact walk is its own function now, and everything
        outside it stays a package fault.
        """
        import shutil
        import subprocess
        import sys
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            pkg = pathlib.Path(td) / "pkg"
            shutil.copytree(PKG, pkg)
            registry = pkg / "references" / "source-registry.yaml"
            doc = yaml.safe_load(registry.read_text())
            doc["sources"][0]["fallback"] = ["a list where a scalar belongs"]
            registry.write_text(yaml.safe_dump(doc))
            result = subprocess.run(
                [
                    sys.executable,
                    str(pkg / "scripts" / "validate_scale_prior_art.py"),
                    "keyword-map",
                    str(FIXTURES / "scale-vocabulary-map.valid.yaml"),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
        assert result.returncode == 2, (result.returncode, result.stdout)
        assert "FAIL package-crash:" in result.stdout, result.stdout
        assert "artifact-untraversable" not in result.stdout, result.stdout
        assert V.is_package_fault("package-crash")

    def test_a_MISSING_currency_fires(self) -> None:
        assert "currency-1" in self._rules(lambda d: d["areas"][0].pop("currency"))

    def test_a_NULL_currency_on_a_dated_corpus_fires(self) -> None:
        """Four shipped documents say null is correct only where every backing source is undated,
        and nothing ran it: a producer that did not compute lens 8 wrote null and reached exit 0."""
        assert "currency-3" in self._rules(
            lambda d: d["areas"][0].__setitem__("currency", None)
        )

    def test_the_CLEAN_index_fires_none_of_them(self) -> None:
        assert not {r for r in self._rules(lambda d: None) if r.startswith("currency")}


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
        """Some of these ids are HYPOTHETICAL, and deliberately so.

        `registry-integrity-5a` and `input-2` are not emitted by this validator. The subject is
        the PREFIX rule — a clause added later must inherit the class of its family rather than
        fall through to exit 1 — and an id that already exists cannot test that. A fresh reviewer
        read them as phantoms, which is fair: they were not labelled.
        """
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
            "artifact-untraversable",
            "queue-row-without-record",
            "ordering-appliable",
            "delta-lineage",
            "extracts-crosscheck-skipped",
        ],
    )
    def test_every_artifact_rule_exits_1(self, rule: str) -> None:
        """`ordering-appliable` and `delta-lineage` are HYPOTHETICAL, like the package-fault
        list's two. The subject is the DEFAULT — a rule matching no package prefix falls to exit
        1 — and an id that already exists cannot test a default. The sibling list was labelled
        one commit ago and this one was left, which is the same omission twice."""
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
            "currency",
            "artifact-untraversable",
            "queue-crosscheck-skipped",
            "queue-row-without-record",
            "record-without-queue-row",
        )
        package_families = (
            "registry-",
            "angle-block-",
            "fallback-",
            "schema-unavailable",
            "dependency-missing",
            "input",
            "thresholds-unreadable",
            "package-crash",
            "extracts-empty",
            "extracts-partial",
            "keyword-map-crosscheck-skipped",
            "queue-unreadable",
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

    def test_EVERY_optional_synthesis_flag_answers_the_SKIP_CONTRACT(self) -> None:
        """The CLASS, derived from the parser rather than named in a list.

        Both optional flags on `synthesis` say whether a cross-check ran, so a run that skipped
        one must name a rule, print a SKIP line, and refuse to exit 0. `--extracts` was built
        that way in C3v; `--queue` shipped answering the opposite way — a bare `return` on a
        `None` path — so the two flags on one subcommand disagreed about what a skipped
        cross-check means. Deriving the flag list here is what stops a THIRD flag inheriting the
        old answer: adding one without extending `supply` fails this test rather than passing
        unnoticed.
        """
        import argparse
        import contextlib
        import io

        (sub,) = [
            a
            for a in V.build_parser()._actions
            if isinstance(a, argparse._SubParsersAction)
        ]
        flags = sorted(
            opt.lstrip("-")
            for action in sub.choices["synthesis"]._actions
            if not isinstance(action, argparse._HelpAction)
            for opt in action.option_strings
            if opt.startswith("--")
        )
        supply = {
            "extracts": str(FIXTURES / "extracts"),
            "queue": str(FIXTURES / "extract-queue.valid.yaml"),
        }
        assert set(supply) == set(flags), (
            "a new optional flag on `synthesis` must say here how to supply it, and answer the "
            "three questions below"
        )
        for flag in flags:
            argv = ["synthesis", str(FIXTURES / "scale-envelope-index.valid.yaml")]
            argv += [
                token
                for other in flags
                if other != flag
                for token in (f"--{other}", supply[other])
            ]
            with contextlib.redirect_stdout(io.StringIO()) as out:
                code = V.main(argv)
            text = out.getvalue()
            assert code == 1, (flag, code, text)
            assert text.count(f"FAIL {flag}-crosscheck-skipped:") == 1, (flag, text)
            assert f"SKIP {flag}-crosscheck" in text, (flag, text)

    #: The MATRIX: every input the CLI reads that a SIBLING WAVE wrote, crossed with every
    #: unusable shape it can arrive in. Enumerated as a product rather than a list, because
    #: enumerating one axis and assuming the other is exactly how this class kept reopening —
    #: the flag axis was derived from the parser and the STATE axis was written from memory with
    #: two members, then three. The artifact itself is deliberately absent: its author CAN
    #: repair it, and that is the whole distinction being tested.
    #: The SEVENTH shape, `wrong-document`, is a file that reads, parses and IS a mapping — and
    #: is a different artifact. `require_mapping` guarded the root and nothing below it, so
    #: pointing `--keyword-map` at a valid envelope index produced TEN findings against cells the
    #: search artifact had queried correctly, at exit 1. It is the commonest real dispatcher
    #: error and it was not on the axis. `is-a-dir` was missing for two of the three file inputs
    #: for no stated reason, which is the same half-enumeration one level down.
    SHAPES = [
        "missing",
        "is-a-dir",
        "unparseable",
        "non-mapping",
        "empty-file",
        "wrong-document",
    ]

    SIBLING_INPUT_SHAPES = [
        (i, s)
        for i, shapes in {
            # Every omission below states its reason. "Each omitted cell needs its reason, or
            # it is not an omission, it is a gap" — the previous revision left two blank and a
            # reviewer had to run them to find out whether they were N/A or missing.
            "--keyword-map": SHAPES,
            # A DIRECTORY has no content shapes: `unparseable`, `non-mapping`, `empty-file` and
            # `wrong-document` are properties of a FILE. `is-a-file` is the wrong-kind-of-path
            # cell for it, and `empty-dir` its own emptiness.
            "--extracts": ["missing", "is-a-file", "empty-dir"],
            # `missing` is not a shape of a record INSIDE the directory: a record that does not
            # exist is the directory being empty or partial, which `--extracts` covers.
            "extracts-record": [s for s in SHAPES if s != "missing"],
            "--queue": SHAPES,
        }.items()
        for s in shapes
    ]

    @staticmethod
    def _unusable(kind: str, shape: str, tmp_path):
        """Build one cell of the matrix and return the argv that exercises it."""
        import shutil

        # The wrong document is the index for every input that takes one — `--extracts` has no
        # `wrong-document` cell, so a second branch here was dead code pretending to be a case.
        other = INDEX
        bad = {
            "unparseable": "this: [is\n  not: valid yaml\n",
            "non-mapping": "- a\n- b\n",
            "empty-file": "",
            "wrong-document": (FIXTURES / other).read_text(),
        }
        if kind == "--keyword-map":
            target = tmp_path / "map.yaml"
            if shape == "is-a-dir":
                target.mkdir()
            elif shape != "missing":
                target.write_text(bad[shape])
            return [
                "search",
                str(FIXTURES / "search-output-b5.valid.yaml"),
                "--keyword-map",
                str(target),
            ]
        argv = ["synthesis", str(FIXTURES / "scale-envelope-index.valid.yaml")]
        extracts = tmp_path / "extracts"
        queue = FIXTURES / "extract-queue.valid.yaml"
        if kind == "--extracts":
            target = {
                "missing": tmp_path / "nope",
                "is-a-file": FIXTURES / "scale-envelope-index.valid.yaml",
                "empty-dir": extracts,
            }[shape]
            if shape == "empty-dir":
                target.mkdir()
            return argv + ["--extracts", str(target), "--queue", str(queue)]
        if kind == "extracts-record":
            shutil.copytree(FIXTURES / "extracts", extracts)
            # A SECOND, GOOD record, so the corpus is PARTIAL rather than empty. With the
            # single-record fixture, breaking the one record empties the directory and the
            # empty-directory guard catches it — the cell would pass over the population that
            # already satisfies the claim, which is the shape this whole matrix exists to stop.
            second = yaml.safe_load(
                (FIXTURES / "extract-output.valid.yaml").read_text()
            )
            second["meta"]["source_id"] = "WEB-second-source"
            for n, ep in enumerate(second["episodes"], 1):
                ep["id"] = f"WEB-second-source#e{n}"
            (extracts / "extract-WEB-second-source.yaml").write_text(
                yaml.safe_dump(second)
            )
            broken = extracts / "extract-WEB-techempower-run-3.yaml"
            if shape == "is-a-dir":
                broken.unlink()
                broken.mkdir()
            else:
                broken.write_text(bad[shape])
            queue = tmp_path / "queue.yaml"
            queue.write_text(
                yaml.safe_dump(
                    {
                        "queue": [
                            {"item_id": "WEB-techempower-run-3"},
                            {"item_id": "WEB-second-source"},
                        ]
                    }
                )
            )
            return argv + ["--extracts", str(extracts), "--queue", str(queue)]
        shutil.copytree(FIXTURES / "extracts", extracts)
        target = tmp_path / "queue.yaml"
        if shape == "is-a-dir":
            target.mkdir()
        elif shape != "missing":
            target.write_text(bad[shape])
        return argv + ["--extracts", str(extracts), "--queue", str(target)]

    @pytest.mark.parametrize(
        ("kind", "shape"),
        SIBLING_INPUT_SHAPES,
        ids=[f"{k}:{s}" for k, s in SIBLING_INPUT_SHAPES],
    )
    def test_an_unusable_SIBLING_INPUT_produces_ONLY_package_faults(
        self, kind: str, shape: str, tmp_path
    ) -> None:
        """One invariant over the whole matrix, and it is the exit contract restated.

        An input a sibling wave wrote is not something the artifact's author can repair. So when
        one arrives unusable in ANY shape, every finding the run emits must be a package fault
        and the run must exit 2. An artifact-family finding here is a FALSE finding by
        construction: it says the author's document is wrong on the strength of a corpus the run
        could not read, and its cheapest remedy is deleting citations that are correct.
        """
        import contextlib
        import io

        argv = self._unusable(kind, shape, tmp_path)
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = V.main(argv)
        text = out.getvalue()
        emitted = [
            ln.split(":", 1)[0][len("FAIL ") :]
            for ln in text.splitlines()
            if ln.startswith("FAIL ")
        ]
        assert emitted, text
        # A `*-crosscheck-skipped` rule is a statement ABOUT THE RUN, not an accusation against
        # the artifact — it says a check did not run. Exempt by SUFFIX rather than by a list, so
        # a fourth cross-check added later is exempt without editing this, and so that naming a
        # rule that way is the deliberate act it should be.
        blamed = [
            r
            for r in emitted
            if not V.is_package_fault(r) and not r.endswith("-crosscheck-skipped")
        ]
        assert not blamed, {
            "artifact blamed for a sibling wave's file": blamed,
            "out": text,
        }
        assert code == 2, (code, text)

    @pytest.mark.parametrize(
        "shape",
        ["a-path-that-is-a-file", "a-path-that-does-not-exist", "an-empty-directory"],
    )
    def test_an_UNUSABLE_extracts_never_cascades(self, shape: str, tmp_path) -> None:
        """PRESENT is not USABLE, and the first build conflated them.

        Every check that reads the records depends on the directory being readable AND holding
        some. When it is not, exactly one thing is true — the cross-check did not run — and
        saying it once is the whole report. Saying it per row blames the artifact's author for
        the dispatcher's typo, and the empty-directory form did it at exit 1, which routes the
        packet back to the author. The cheapest route to exit 0 from that wall is deleting the
        citations, which is why the sibling that ships this guards it with an early return.
        """
        import contextlib
        import io

        target = {
            "a-path-that-is-a-file": FIXTURES / "scale-envelope-index.valid.yaml",
            "a-path-that-does-not-exist": tmp_path / "nope",
            "an-empty-directory": tmp_path / "empty",
        }[shape]
        if shape == "an-empty-directory":
            target.mkdir()
        with contextlib.redirect_stdout(io.StringIO()) as out:
            V.main(
                [
                    "synthesis",
                    str(FIXTURES / "scale-envelope-index.valid.yaml"),
                    "--extracts",
                    str(target),
                    "--queue",
                    str(FIXTURES / "extract-queue.valid.yaml"),
                ]
            )
        text = out.getvalue()
        cascaded = [
            ln
            for ln in text.splitlines()
            if ln.startswith(
                (
                    "FAIL queue-row-without-record",
                    "FAIL synthesis-1b",
                    "FAIL synthesis-3c",
                )
            )
        ]
        assert not cascaded, text
        assert text.count("FAIL extracts-crosscheck-skipped:") == 1, text
        assert "SKIP extracts-crosscheck" in text, text
        assert text.count("FAIL queue-crosscheck-skipped:") == 1, text

    def test_a_PARTIAL_corpus_names_its_own_cause(self, tmp_path) -> None:
        """The narrow mirror the matrix invariant cannot supply.

        The kill sweep found this rule SURVIVING: suppress it and the matrix cells still pass,
        because `_read_extracts` returns None either way, so the run still exits 2 with only
        package faults. An invariant satisfied by the OTHER findings pins nothing about the
        finding that names the cause — the same shape as a rule covered only by a family prefix.
        A reader whose corpus is half-readable needs to be told THAT, not just that some file did
        not parse.
        """
        import contextlib
        import io
        import shutil

        rule = "extracts-partial"
        extracts = tmp_path / "extracts"
        shutil.copytree(FIXTURES / "extracts", extracts)
        good = yaml.safe_load((FIXTURES / "extract-output.valid.yaml").read_text())
        good["meta"]["source_id"] = "WEB-second-source"
        for n, ep in enumerate(good["episodes"], 1):
            ep["id"] = f"WEB-second-source#e{n}"
        (extracts / "extract-WEB-second-source.yaml").write_text(yaml.safe_dump(good))
        (extracts / "extract-WEB-techempower-run-3.yaml").write_text("this: [is\n")
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = V.main(
                [
                    "synthesis",
                    str(FIXTURES / "scale-envelope-index.valid.yaml"),
                    "--extracts",
                    str(extracts),
                    "--queue",
                    str(FIXTURES / "extract-queue.valid.yaml"),
                ]
            )
        text = out.getvalue()
        assert text.count(f"FAIL {rule}:") == 1, text
        assert "1 record(s) could not be read" in text, text
        assert code == 2, (code, text)
        # The narrow mirror: a corpus where every record reads produces no such finding, and the
        # EMPTY case has its own id rather than this one.
        with contextlib.redirect_stdout(io.StringIO()) as clean:
            V.main(
                [
                    "synthesis",
                    str(FIXTURES / "scale-envelope-index.valid.yaml"),
                    "--extracts",
                    str(FIXTURES / "extracts"),
                    "--queue",
                    str(FIXTURES / "extract-queue.valid.yaml"),
                ]
            )
        assert rule not in clean.getvalue()

    def test_an_empty_extracts_directory_names_its_OWN_cause(self, tmp_path) -> None:
        """A directory that resolves and holds nothing is unusable in the way an unreadable one
        is, and the index's author did not write the records — a sibling wave did. So it is
        exit 2 with its own id, not a silent absence."""
        import contextlib
        import io

        empty = tmp_path / "empty"
        empty.mkdir()
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = V.main(
                [
                    "synthesis",
                    str(FIXTURES / "scale-envelope-index.valid.yaml"),
                    "--extracts",
                    str(empty),
                    "--queue",
                    str(FIXTURES / "extract-queue.valid.yaml"),
                ]
            )
        text = out.getvalue()
        assert "FAIL extracts-empty:" in text, text
        assert code == 2, (code, text)
        assert V.is_package_fault("extracts-empty")

    def test_a_queue_with_no_extracts_reports_ONCE_not_once_per_row(self) -> None:
        """One dispatcher omission must not produce one finding per queue row.

        The first implementation let the present-set default to EMPTY when `--extracts` was
        absent, so every row of a correct queue failed `queue-row-without-record` and the
        artifact's author was blamed N times for a flag the dispatcher did not pass. A check
        that cannot run reports that it did not run, once.
        """
        import contextlib
        import io
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            queue = pathlib.Path(td) / "extract-queue.yaml"
            queue.write_text(
                yaml.safe_dump(
                    {"queue": [{"item_id": f"WEB-row-{n}"} for n in range(3)]}
                )
            )
            with contextlib.redirect_stdout(io.StringIO()) as out:
                code = V.main(
                    [
                        "synthesis",
                        str(FIXTURES / "scale-envelope-index.valid.yaml"),
                        "--queue",
                        str(queue),
                    ]
                )
        rule = "queue-crosscheck-skipped"
        text = out.getvalue()
        assert code == 1, (code, text)
        assert text.count(f"FAIL {rule}:") == 1, text
        assert "queue-row-without-record" not in text, text

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

        This pair lands above it; the distance is DERIVED below, not written here. Merging two conditions to fit inside a measured number
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

        **The population is the walk's own default**, not a list. A fifth shape was added and
        this guard kept enumerating three, so the shape written to close a hole sat outside the
        only check that would have shown it closed nothing — which is this guard's own lesson
        applied to itself.

        Two shapes yield ids that OTHER shapes also yield, so removing them changes nothing.
        That is not the same as having no instances, and conflating the two is how a dead branch
        hides, so each is asserted on what it yields ALONE.
        """
        import ast
        import inspect

        tree = ast.parse((HERE / "validate_scale_prior_art.py").read_text())
        shapes = tuple(inspect.signature(_emitted_ids).parameters["shapes"].default)
        assert len(shapes) == 4, shapes
        full = _emitted_ids(tree)
        exercised = {
            s
            for s in shapes
            if _emitted_ids(tree, tuple(x for x in shapes if x != s)) != full
        }
        assert exercised == {"positional", "keyword"}, {
            "exercised": sorted(exercised),
            "redundant-or-unused": sorted(set(shapes) - exercised),
        }
        alone = {s: _emitted_ids(tree, (s,)) for s in set(shapes) - exercised}
        assert alone == {
            "default": set(),
            "positional-helper": {"input", "queue-unreadable"},
        }, {k: sorted(v) for k, v in alone.items()}

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


def _m_currency_names_a_date_no_episode_carries(d):
    d["areas"][0]["currency"] = {
        "dates": ["2019-01-01"],
        "note": "Four hardware generations back.",
    }


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
        _m_currency_names_a_date_no_episode_carries,
        "currency-2",
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
        argv += ["--queue", str(FIXTURES / "extract-queue.valid.yaml")]
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

    #: The families `MUTATIONS` covers, DECLARED. The count in the docstring went stale twice and
    #: was deleted, which was right; deleting it and putting nothing in its place was half the job,
    #: and a commit message claimed the other half had landed when it had not.
    #:
    #: WHAT THIS DOES AND DOES NOT SAY (contract §9e): `MUTATIONS` is the CLI-level table — a
    #: constructed artifact edit producing EXACTLY ONE finding through `main()`. Most families
    #: cannot be reached that way: a package fault is not an artifact edit, and several artifact
    #: families co-fire with `schema`, which breaks the exactly-one bar. That every emitted rule is
    #: reachable by SOME test is a different assertion and C3m owns it. This one says only that the
    #: CLI table's reach is what it is declared to be, in both directions.
    MUTATION_FAMILIES = frozenset(
        {
            "admission",
            "bound",
            "coverage-grid",
            "currency",
            "derived-confidence",
            "map-completeness",
            "measured-coherence",
            "synthesis",
            "vocabularies",
        }
    )

    def test_the_MUTATION_table_reaches_exactly_the_declared_families(self) -> None:
        derived = {re.sub(r"-\d+[a-z]?$", "", rule) for _, _, _, rule in MUTATIONS}
        assert derived == self.MUTATION_FAMILIES, {
            "in the table, undeclared": sorted(derived - self.MUTATION_FAMILIES),
            "declared, absent from the table": sorted(self.MUTATION_FAMILIES - derived),
        }

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
        # An ABSOLUTE floor, not `len(caught) == len(SAMPLE)`. The population WAS the sample, so
        # truncating the sample left the suite green — the identical shape as the access_status
        # anchor hole this module asserts a count for.
        assert len(self.SHIPPED_BROKEN_LEADS) == 16, (
            f"{len(self.SHIPPED_BROKEN_LEADS)} leads embedded; sixteen of the seventeen the "
            "repair rewrote are visible to this shape, and the sample is not the population"
        )
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


#: A fenced block, INDENTED OR NOT. Anchored at column 0, this matched zero blocks in the producer
#: package — every fence there is four-space indented inside a numbered list — so all four example
#: guards were blind to it. Proved by planting, in the producer's SKILL.md at its neighbours'
#: indentation, an example citing a plant's condition and quoting a plant's exact defect string:
#: 387 tests passed. De-indented to column 0, all four failed.
#: `[^\n]*`, not `[a-z]*`: an info string the class cannot match — ```yaml title="x",
#: ```Bash, ```js{1,3} — makes the CLOSER the opener, so the capture becomes the prose
#: BETWEEN two blocks and the real block goes unscanned. Same silent-wrong-target class as
#: the column-0 anchor this replaced.
FENCE = r"^[ \t]*```[^\n]*\n(.*?)^[ \t]*```"


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
        blocks = re.findall(FENCE, text, re.M | re.S)
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

    #: Where a worked FINDING example lives today. The producer's fenced blocks are shell
    #: invocations, not findings, so the discriminator is a cited condition id rather than the
    #: presence of a quoted span.
    #:
    #: An earlier comment here explained the producer's exclusion as a CLI argument having once
    #: flipped it into "has an example". That could not have happened — the extractor was anchored
    #: at column 0 and the producer's fences are all list-indented, so it had returned an empty set
    #: in every version. A false explanation for a real vacuum reads as though the hole were
    #: closed, which is worse than the vacuum.
    PACKAGES_WITH_AN_EXAMPLE = {"reviewing-scale-prior-art-survey"}

    def test_the_declared_example_packages_are_the_ones_that_HAVE_examples(
        self,
    ) -> None:
        """Non-vacuity, both directions. An example that disappears must not pass as clean, and
        one that appears must not be checked by nothing."""
        actual = {
            pkg.name
            for pkg in (PKG, TWIN)
            if any(
                re.search(r"(?<![A-Za-z`])C\d+\b", block)
                for block in re.findall(
                    FENCE,
                    (pkg / "SKILL.md").read_text(),
                    re.M | re.S,
                )
            )
        }
        assert actual == self.PACKAGES_WITH_AN_EXAMPLE, {
            "has an example": sorted(actual),
            "declared": sorted(self.PACKAGES_WITH_AN_EXAMPLE),
        }

    @staticmethod
    def _words(text: str) -> list:
        return re.sub(r"[^a-z ]", " ", text.lower()).split()

    def test_the_example_JUSTIFIES_in_the_conditions_own_words(self) -> None:
        """The third leak, and the one no token or id check can see.

        Three successive examples invented a TEST the condition does not state: "the corpus this
        angle walks" (a wave-1 event cited by a wave-0 condition, and a map is not walked by an
        angle), then "the corpus arrays this map declares" — a real field that legitimately holds
        no expansions, so applying it files findings against six of the seven legitimate
        expansions in the calibration map, in the artifact whose whole job is to teach not-a-gap.

        The rule is that the justification comes from the condition. Asserted as a shared run of
        four or more words between the example and the lead of the condition it cites, which an
        invented test does not have and a restatement does.
        """
        for pkg in (PKG, TWIN):
            text = (pkg / "SKILL.md").read_text()
            leads = {
                m.group(1): " ".join(m.group(2).split())
                for m in re.finditer(
                    r"\*\*C(\d+) — (.*?)\*\*",
                    (TWIN / "references" / "conditions.md").read_text(),
                    re.S,
                )
            }
            for block in re.findall(FENCE, text, re.M | re.S):
                for cid in re.findall(r"(?<![A-Za-z`])C(\d+)\b", block):
                    lead = leads.get(cid)
                    assert lead, (
                        f"{pkg.name}'s example cites C{cid}, which does not exist"
                    )
                    ex, cond = self._words(block), self._words(lead)
                    runs = {
                        " ".join(cond[i : i + 4]) for i in range(max(0, len(cond) - 3))
                    }
                    shared = any(
                        " ".join(ex[i : i + 4]) in runs
                        for i in range(max(0, len(ex) - 3))
                    )
                    assert shared, (
                        f"{pkg.name}'s example for C{cid} shares no four-word run with the "
                        "condition it cites — it is stating a test of its own"
                    )

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
            for block in re.findall(FENCE, text, re.M | re.S):
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


def _clause_rules(kind: str, doc, f) -> set:
    """Run the checks a KIND's artifact goes through, and return the ids they emit.

    Exact ids, never a family prefix. The family idiom — `assert "coverage-grid" in _rules(...)`
    — passes for any clause, which is how 66 of 110 per-clause rules came to be deletable with
    the whole suite green.
    """
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
        V.check_ids(doc, f)
        if doc.get("outcome") != "skipped":
            V.check_score(doc, f)
    elif kind == "synthesis":
        extracts = [
            yaml.safe_load(x.read_text())
            for x in sorted((FIXTURES / "extracts").glob("*.yaml"))
        ]
        V.check_synthesis(doc, extracts, f)
    elif kind == "registry":
        V.check_registry(doc, f)
    elif kind == "body":
        V.check_body_sections(doc, f)
    return {r for r, _ in f.items}


#: One entry per rule that had NO individual coverage — 66 of 110, every one of them reachable
#: only through a family-prefix assertion and so deletable with the suite green. Each is
#: `(kind, base fixture, mutate, rule id)`, and each yields BOTH halves EC5 asks for: the
#: positive pin, and the narrow mirror, which is the same mutation NOT applied.
def _m(kind, base, rule):
    """Register one clause mirror by decorating its mutation."""

    def register(fn):
        CLAUSE_MIRRORS.append((kind, base, fn, rule))
        return fn

    return register


CLAUSE_MIRRORS: list = []

MAP = "scale-vocabulary-map.valid.yaml"
SEARCH = "search-output-b5.valid.yaml"
EXTRACT = "extract-output.valid.yaml"
INDEX = "scale-envelope-index.valid.yaml"


@_m("keyword-map", MAP, "map-completeness-1b")
def _c_registry_row_in_neither_array(d):
    d["sources"]["skipped"].pop()


@_m("keyword-map", MAP, "map-completeness-1c")
def _c_a_row_that_is_not_a_registry_row(d):
    row = dict(d["sources"]["skipped"][0])
    row["id"] = "a-source-the-registry-does-not-carry"
    d["sources"]["skipped"].append(row)


@_m("extract", EXTRACT, "quality-filter-1a")
def _c_a_source_record_with_no_score(d):
    d["source"].pop("score")


@_m("extract", EXTRACT, "bail-3")
def _c_a_bail_on_no_stated_load(d):
    d["outcome"] = "skipped"
    d["skipped"] = {"cause": "no-stated-load", "detail": "the source states no load"}


@_m("search", SEARCH, "bound-2a")
def _c_hit_true_owing_a_dropped_note(d):
    d["bound"]["hit"] = True
    d["bound"]["dropped_note"] = None


@_m("search", SEARCH, "bound-2b")
def _c_a_dropped_note_naming_no_position(d):
    d["bound"]["hit"] = True
    d["bound"]["dropped_note"] = "the rest were dropped"


@_m("search", SEARCH, "bound-3")
def _c_a_deviating_ordering_with_no_deviation_note(d):
    d["bound"]["ordering"] = "by whatever looked good"
    d["bound"]["ordering_deviation"] = None


@_m("synthesis", INDEX, "lineage-liveness-1")
def _c_delta_mode_with_a_null_extends(d):
    d["mode"] = "delta"
    d["lineage"] = {"extends": None}


@_m("body", "extract-output.valid.md", "body-sections-1")
def _c_a_body_missing_one_of_the_four_sections(text: str) -> str:
    return text.replace("## Transferability", "## Notes on transferability")


@_m("body", "extract-output.valid.md", "body-sections-2")
def _c_a_body_section_too_thin_to_be_one(text: str) -> str:
    head, _, _ = text.partition("## Transferability")
    return head + "## Transferability\nIt carries.\n"


@_m("keyword-map", MAP, "map-completeness-1d")
def _c_active_row_missing_a_key(d):
    d["sources"]["active"][0].pop("as_of")


@_m("keyword-map", MAP, "map-completeness-1e")
def _c_skip_cause_class_outside_the_enum(d):
    d["sources"]["skipped"][0]["cause_class"] = "because-i-said-so"


@_m("keyword-map", MAP, "map-completeness-1f")
def _c_skipped_row_with_no_cause(d):
    d["sources"]["skipped"][0]["cause"] = ""


@_m("keyword-map", MAP, "map-completeness-1g")
def _c_skipped_row_carrying_a_posture(d):
    d["sources"]["skipped"][0]["sanitization"] = {"status": "clean", "cause": None}


@_m("keyword-map", MAP, "map-completeness-2a")
def _c_axis_with_no_group_undeclared(d):
    d["groups"] = [g for g in d["groups"] if g["type"] != "failure-class"]


@_m("keyword-map", MAP, "map-completeness-2b")
def _c_absent_axis_with_no_reason(d):
    d["groups"] = [g for g in d["groups"] if g["type"] != "failure-class"]
    d["scope_guard"]["absent_types"] = ["failure-class"]


@_m("keyword-map", MAP, "map-completeness-3")
def _c_shared_term_with_no_owner(d):
    d["scope_guard"]["shared_terms"] = [
        {"term": "saturation", "groups": [], "owner": ""}
    ]


@_m("keyword-map", MAP, "map-completeness-4a")
def _c_angle_with_no_verdict(d):
    d["angle_applicability"] = d["angle_applicability"][:-1]


@_m("keyword-map", MAP, "map-completeness-4b")
def _c_verdict_with_no_reason(d):
    d["angle_applicability"][0]["reason"] = ""


@_m("keyword-map", MAP, "map-completeness-6")
def _c_holds_false_naming_no_deciding_value(d):
    v = next(x for x in d["angle_applicability"] if x["holds"] is False)
    v["reason"] = "It does not apply to this project."


@_m("keyword-map", MAP, "sanitization-1a")
def _c_posture_with_no_status(d):
    d["sources"]["active"][0]["sanitization"] = {"cause": "x"}


@_m("keyword-map", MAP, "declared-band-1")
def _c_band_missing_a_leaf(d):
    d["meta"]["classification"]["scale"].pop("geo_distribution")


@_m("keyword-map", MAP, "declared-band-2")
def _c_band_absent_entirely(d):
    d["meta"]["classification"]["scale"] = None


@_m("search", SEARCH, "coverage-grid-1b")
def _c_not_run_output_carrying_a_body(d):
    d["outcome"] = "not_run"
    d["not_run"] = {"map_verdict": "b5 does not hold"}


@_m("search", SEARCH, "coverage-grid-2a")
def _c_an_owed_cell_absent(d):
    d["coverage"].pop()


@_m("search", SEARCH, "coverage-grid-2b")
def _c_a_cell_the_three_terms_do_not_owe(d):
    extra = dict(d["coverage"][0])
    extra["group_id"] = "g-sys-batch"
    d["coverage"].append(extra)


@_m("search", SEARCH, "coverage-grid-2c")
def _c_a_duplicated_cell(d):
    d["coverage"].append(dict(d["coverage"][0]))


@_m("search", SEARCH, "coverage-grid-4a")
def _c_reached_cell_with_no_kept(d):
    next(c for c in d["coverage"] if c["status"] == "reached").pop("kept")


@_m("search", SEARCH, "coverage-grid-4b")
def _c_nonzero_returned_with_no_count_frame(d):
    next(c for c in d["coverage"] if c.get("returned")).pop("count_frame")


@_m("search", SEARCH, "coverage-grid-4c")
def _c_unreached_cell_with_no_cause(d):
    next(c for c in d["coverage"] if c["status"] != "reached").pop("cause")


@_m("search", SEARCH, "sanitization-1b")
def _c_reached_cell_with_no_posture(d):
    next(c for c in d["coverage"] if c["status"] == "reached").pop("sanitization")


@_m("search", SEARCH, "sanitization-3")
def _c_modified_posture_with_no_cause(d):
    cell = next(c for c in d["coverage"] if c["status"] == "reached")
    cell["sanitization"] = {"status": "modified", "cause": None}


@_m("search", SEARCH, "sanitization-4")
def _c_reached_cell_posted_not_fetched(d):
    cell = next(c for c in d["coverage"] if c["status"] == "reached")
    cell["sanitization"] = {"status": "not-fetched", "cause": "x"}


@_m("search", SEARCH, "admission-1a")
def _c_candidate_with_no_url(d):
    d["candidates"][0]["url"] = ""


@_m("search", SEARCH, "admission-1b")
def _c_candidate_with_no_stated_date(d):
    d["candidates"][0]["stated_date"] = ""


@_m("search", SEARCH, "admission-2a")
def _c_candidate_with_no_found_by(d):
    d["candidates"][0]["found_by"] = ""


@_m("search", SEARCH, "admission-2b")
def _c_unadmitted_row_with_no_found_by(d):
    d["unadmitted"] = [
        {"item_id": "x", "reason_class": "no-stated-date", "reason": "y"}
    ]


@_m("search", SEARCH, "admission-2c")
def _c_unadmitted_row_with_no_reason(d):
    d["unadmitted"] = [
        {
            "item_id": "x",
            "found_by": d["candidates"][0]["found_by"],
            "reason_class": "no-stated-date",
            "reason": "",
        }
    ]


@_m("search", SEARCH, "retrieval-summary-1")
def _c_summary_not_derived_from_the_finished_list(d):
    d["retrieval_summary"]["candidates"] += 1


@_m("extract", EXTRACT, "vocabularies-1")
def _c_signal_outside_the_golden_set(d):
    d["episodes"][0]["signal"] = "vibes"


@_m("extract", EXTRACT, "vocabularies-2")
def _c_load_class_key_that_is_not_a_band_leaf(d):
    d["episodes"][0]["load_class"]["mood"] = "high"


@_m("extract", EXTRACT, "vocabularies-3")
def _c_consistency_model_outside_jepsens(d):
    d["episodes"][0]["consistency_model"] = "pretty-consistent"


@_m("extract", EXTRACT, "vocabularies-5")
def _c_evidence_class_outside_the_enum(d):
    d["episodes"][0]["evidence_class"] = "someone-said-so"


@_m("extract", EXTRACT, "vocabularies-5a")
def _c_episode_cause_class_outside_its_own_vocabulary(d):
    d["episodes"][0]["cause_class"] = "no-holding-angle"


@_m("extract", EXTRACT, "vocabularies-5b")
def _c_episode_with_no_pattern(d):
    d["episodes"][0]["pattern"] = ""


@_m("extract", EXTRACT, "vocabularies-6")
def _c_license_that_is_not_an_spdx_id(d):
    d["source"]["license"] = "free for everyone"


@_m("extract", EXTRACT, "vocabularies-7")
def _c_source_access_status_outside_the_enum(d):
    d["source"]["access_status"] = "probably-fine"


@_m("extract", EXTRACT, "primary-dimension-1")
def _c_primary_dimension_that_is_not_a_band_leaf(d):
    d["episodes"][0]["primary_dimension"] = "throughput"


@_m("extract", EXTRACT, "transferability-1a")
def _c_episode_with_no_transferability(d):
    d["episodes"][0].pop("transferability")


@_m("extract", EXTRACT, "transferability-1b")
def _c_transferability_level_outside_the_enum(d):
    d["episodes"][0]["transferability"]["level"] = "quite-good"


@_m("extract", EXTRACT, "transferability-1c")
def _c_transferability_reason_too_thin_to_weigh(d):
    d["episodes"][0]["transferability"]["reason"] = "it fits"


@_m("extract", EXTRACT, "measured-coherence-1a")
def _c_magnitude_with_no_value(d):
    d["episodes"][0]["measured_value"] = None


@_m("extract", EXTRACT, "derived-load-class-1")
def _c_availability_band_measured_in_the_wrong_unit(d):
    ep = d["episodes"][0]
    ep["primary_dimension"] = "availability_target"
    ep["load_class"]["availability_target"] = "99"
    ep["measured_unit"] = "rows/s"


@_m("extract", EXTRACT, "derived-load-class-2")
def _c_a_band_asserted_with_no_number_behind_it(d):
    ep = d["episodes"][1]
    ep["load_class"]["data_volume"] = "large"


@_m("extract", EXTRACT, "quality-filter-1b")
def _c_score_outside_the_integer_range(d):
    d["source"]["score"] = 44


@_m("extract", EXTRACT, "id-grammar-2")
def _c_id_class_outside_the_three(d):
    d["meta"]["id_class"] = "FTP"


@_m("extract", EXTRACT, "id-grammar-3a")
def _c_episode_id_that_could_be_read_as_a_path(d):
    d["episodes"][0]["id"] = "../../etc/passwd"


@_m("extract", EXTRACT, "id-grammar-1")
def _c_episode_id_outside_the_grammar(d):
    d["episodes"][0]["id"] = "episode one"


@_m("extract", EXTRACT, "id-grammar-3b")
def _c_episode_id_not_rooted_on_its_source(d):
    d["episodes"][0]["id"] = "WEB-somewhere-else#e1"


@_m("extract", EXTRACT, "bail-1")
def _c_bail_carrying_more_than_cause_and_detail(d):
    d["outcome"] = "skipped"
    d["skipped"] = {"cause": "paywalled", "detail": "402", "extra": 1}


@_m("extract", EXTRACT, "bail-2")
def _c_bail_cause_outside_the_enum(d):
    d["outcome"] = "skipped"
    d["skipped"] = {"cause": "did-not-feel-like-it", "detail": "x"}


@_m("synthesis", INDEX, "synthesis-1a")
def _c_area_with_empty_evidence(d):
    d["areas"][0]["evidence"] = []


@_m("synthesis", INDEX, "synthesis-1b")
def _c_evidence_id_resolving_to_no_episode(d):
    d["areas"][0]["evidence"] = ["WEB-nowhere#e9"]


@_m("synthesis", INDEX, "synthesis-3a")
def _c_migration_trigger_with_no_evidence(d):
    d["areas"][0]["migration_trigger"]["evidence"] = []


@_m("synthesis", INDEX, "synthesis-3b")
def _c_failure_mode_with_no_evidence(d):
    d["areas"][0]["failure_modes"][0]["evidence"] = []


@_m("synthesis", INDEX, "synthesis-3c")
def _c_a_hard_limit_source_resolving_to_no_episode(d):
    d["areas"][0]["hard_limits"][0]["source"] = "WEB-nowhere#e9"


@_m("registry", "registry", "angle-block-1a")
def _c_conditional_angle_with_no_predicate(d):
    next(a for a in d["angles"] if a.get("trigger") == "conditional").pop("predicate")


@_m("registry", "registry", "angle-block-1b")
def _c_always_on_angle_carrying_a_predicate(d):
    always = next(a for a in d["angles"] if a.get("trigger") != "conditional")
    always["predicate"] = [
        [{"field": "scale.data_volume", "op": "in", "values": ["large"]}]
    ]


@_m("registry", "registry", "angle-block-4a")
def _c_angle_whose_seed_input_is_not_a_list(d):
    d["angles"][0]["seed_input"] = "the scope"


@_m("registry", "registry", "angle-block-4b")
def _c_seed_input_token_that_is_neither_a_group_type_nor_a_path(d):
    d["angles"][0]["seed_input"] = ["whatever-is-lying-around"]


@_m("search", SEARCH, "admission-3")
def _c_kept_disagreeing_with_the_rows_citing_the_cell(d):
    next(c for c in d["coverage"] if c.get("kept")).__setitem__("kept", 9)


class TestC3mTheClauseMirrors:
    """EC5's partition, built. Every rule that had NO individual coverage now has both halves.

    Sixty-six of a hundred and ten per-clause rules were reachable only through a family-prefix
    assertion — `assert "coverage-grid" in _rules(...)` passes for any clause — so each could be
    deleted with the whole suite green. The task that owns this was marked DONE, discharging EC5,
    with nothing behind it.

    Each entry gives BOTH halves in one construction: the POSITIVE pin (the mutation fires that
    exact id) and the NARROW MIRROR (the same base, unmutated, does not).
    """

    @staticmethod
    def _base(kind: str, base: str):
        import copy

        if kind == "registry":
            return copy.deepcopy(yaml.safe_load(REGISTRY.read_text()))
        if kind == "body":
            return (FIXTURES / base).read_text()
        return copy.deepcopy(yaml.safe_load((FIXTURES / base).read_text()))

    @pytest.mark.parametrize(
        ("kind", "base", "mutate", "rule"),
        CLAUSE_MIRRORS,
        ids=[m[3] for m in CLAUSE_MIRRORS],
    )
    def test_the_clause_FIRES_on_its_own_mutation(
        self, kind: str, base: str, mutate, rule: str
    ) -> None:
        doc = self._base(kind, base)
        # A body is TEXT, so its mutation returns the new value rather than editing in place.
        doc = mutate(doc) if kind == "body" else (mutate(doc) or doc)
        assert rule in _clause_rules(kind, doc, V.Findings())

    @pytest.mark.parametrize(
        ("kind", "base", "mutate", "rule"),
        CLAUSE_MIRRORS,
        ids=[m[3] for m in CLAUSE_MIRRORS],
    )
    def test_the_NARROW_MIRROR_is_silent_on_the_unmutated_base(
        self, kind: str, base: str, mutate, rule: str
    ) -> None:
        """The half EC5 names. A rule that fires on a CORRECT artifact is worse than one that
        never fires, and nothing was checking it per clause."""
        doc = self._base(kind, base)
        assert rule not in _clause_rules(kind, doc, V.Findings())

    #: The ONE rule no artifact mutation can reach: a defensive assertion about
    #: `record_filename` itself, firing only if the identity branch stops refusing an
    #: already-hashed stem — which no input can cause while the implementation is correct. Its
    #: coverage is the cross-branch collision test, which constructs the property directly.
    #: Declared rather than mirrored, because a mirror for it would be a test of nothing.
    NOT_MIRRORABLE = frozenset({"record-filename-2"})

    def test_an_unreadable_keyword_map_fires_and_does_not_crash_the_walk(self) -> None:
        """The skip had NO test and its only occurrences were inside a declaration set.

        It deliberately does not return, and the walk three blocks down dereferenced the map
        anyway — so a typo'd `--keyword-map` aborted the admission, bound and summary families
        and filed the crash as the artifact's fault. It also shared `coverage-grid-1a` with a
        real artifact defect until the two subjects were separated: an accusation and a
        did-not-run notice cannot carry one id, because the exit class differs.
        """
        f = V.Findings()
        reg = yaml.safe_load(REGISTRY.read_text())
        doc = yaml.safe_load((FIXTURES / "search-output-b5.valid.yaml").read_text())
        V.check_search(doc, reg, None, f)
        rules = {r for r, _ in f.items}
        assert "keyword-map-crosscheck-skipped" in rules
        assert "coverage-grid-1a" not in rules
        # The families downstream of the map still ran rather than being lost to the crash.
        assert "admission-1a" not in rules, (
            "the clean artifact should fire none of them"
        )

    def test_a_non_mapping_angle_block_fires(self) -> None:
        """`angle-block-1` had NO coverage. What looked like its test named `angle-block-1`
        while the `_RuleSet` prefix match let an `angle-block-1a` finding satisfy it — a rule
        with only family coverage, sitting in the module built to catch exactly that."""
        reg = yaml.safe_load(REGISTRY.read_text())
        reg["angles"] = ["an angle block that is not a mapping"]
        f = V.Findings()
        V.check_registry(reg, f)
        assert "angle-block-1" in {r for r, _ in f.items}

    def test_a_non_directory_extracts_flag_fires(self) -> None:
        """`input-1`. Passing a FILE where a directory belongs is an input-class fault."""
        import contextlib
        import io

        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = V.main(
                [
                    "synthesis",
                    str(FIXTURES / "scale-envelope-index.valid.yaml"),
                    "--extracts",
                    str(FIXTURES / "scale-envelope-index.valid.yaml"),
                ]
            )
        assert code == 2, out.getvalue()
        assert "FAIL input-1:" in out.getvalue(), out.getvalue()

    def test_an_absent_dependency_fires(self) -> None:
        """`dependency-missing`. Neither of its three sites had a test, and a package that cannot
        import its own dependency must exit 2 rather than pretend the artifact is clean."""
        import builtins

        real = builtins.__import__

        def refuse(name, *args, **kwargs):
            if name == "jsonschema":
                raise ModuleNotFoundError(name)
            return real(name, *args, **kwargs)

        f = V.Findings()
        builtins.__import__ = refuse
        try:
            V.check_schema({}, "extract-output", f)
        finally:
            builtins.__import__ = real
        assert "dependency-missing" in {r for r, _ in f.items}

    @pytest.mark.parametrize(
        ("package_file", "corrupt", "rule"),
        [
            (
                "references/source-registry.yaml",
                "sources: [unclosed\n",
                "registry-unreadable",
            ),
            (
                "references/load-band-thresholds.md",
                "```yaml\nunsourced_dimensions:\n  - just-a-string\n```\n",
                "thresholds-unreadable",
            ),
        ],
    )
    def test_an_unreadable_PACKAGE_file_fires_its_own_rule_at_exit_2(
        self, package_file: str, corrupt: str, rule: str
    ) -> None:
        """Both had no test. The thresholds one is the sharper case: its read and its parse were
        guarded and the walk that dereferences each entry was not, so a scalar there crashed
        INSIDE the artifact walk and was filed as the author's fault at exit 1."""
        import shutil
        import subprocess
        import sys
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            pkg = pathlib.Path(td) / "pkg"
            shutil.copytree(PKG, pkg)
            (pkg / package_file).write_text(corrupt)
            result = subprocess.run(
                [
                    sys.executable,
                    str(pkg / "scripts" / "validate_scale_prior_art.py"),
                    "extract",
                    str(FIXTURES / "extract-output.valid.yaml"),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
        assert result.returncode == 2, (result.returncode, result.stdout)
        assert f"FAIL {rule}:" in result.stdout, result.stdout
        assert "artifact-untraversable" not in result.stdout, result.stdout

    @pytest.mark.parametrize(
        ("mutate", "rule"),
        [
            (
                lambda r: r.clear() or r.update({"not": "a registry"}),
                "registry-integrity-1",
            ),
            (lambda r: r.__setitem__("sources", "not a list"), "registry-integrity-1"),
            (lambda r: r.__setitem__("angles", "not a list"), "registry-integrity-1"),
            (
                lambda r: r["sources"].__setitem__(0, "not a row"),
                "registry-integrity-1",
            ),
            (lambda r: r["sources"][0].__setitem__("id", 7), "registry-integrity-1"),
        ],
        ids=[
            "not-a-mapping",
            "sources-not-a-list",
            "angles-not-a-list",
            "row-not-a-mapping",
            "id-not-a-string",
        ],
    )
    def test_each_registry_integrity_BRANCH_fires(self, mutate, rule: str) -> None:
        """One rule, five branches, and the rule-level sweep could not tell them apart.

        A rule is pinned when SOME test names it; four of these five could be deleted with the
        whole suite green, which is the coverage hole a call-site sweep sees and a rule sweep
        does not.
        """
        reg = yaml.safe_load(REGISTRY.read_text())
        mutate(reg)
        f = V.Findings()
        V.check_registry(reg, f)
        assert rule in {r for r, _ in f.items}

    def test_a_DUPLICATED_id_inside_one_array_fires(self) -> None:
        """`map-completeness-1a`'s OTHER site, and the one a call-site sweep found alive.

        The rule has two branches: a row in BOTH arrays, which was pinned, and a row listed
        TWICE inside one — where the second entry SHADOWS the first, so a defective row hides
        behind a correct one while the set arithmetic still balances. Deleting this branch left
        the whole suite green at exit 0.
        """
        reg = yaml.safe_load(REGISTRY.read_text())
        doc = yaml.safe_load((FIXTURES / "scale-vocabulary-map.valid.yaml").read_text())
        doc["sources"]["active"].append(dict(doc["sources"]["active"][0]))
        f = V.Findings()
        V.check_map(doc, reg, f)
        found = [message for rule, message in f.items if rule == "map-completeness-1a"]
        assert found and "duplicate ids" in found[0], sorted(r for r, _ in f.items)

    def test_an_EMPTY_artifact_does_not_reach_exit_0(self) -> None:
        """The branch whose own comment records that it already shipped once: a comments-only
        file PARSES, to None, and returning it unremarked let a producer that wrote nothing
        pass. Deleted, the suite stayed green and a zero-byte artifact exited 0."""
        import contextlib
        import io
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            empty = pathlib.Path(td) / "empty.yaml"
            empty.write_text("# nothing but a comment\n")
            with contextlib.redirect_stdout(io.StringIO()) as out:
                code = V.main(["keyword-map", str(empty)])
        # EXIT 1, not 2. The file was READ and did PARSE — to None — so it is content its
        # author can repair, which is the same reasoning that moved a top-level non-mapping off
        # exit 2 and is where all four shipped siblings put it. A producing agent that writes a
        # zero-byte artifact must get its own packet back, not have the run called unusable.
        assert code == 1, (code, out.getvalue())
        assert "FAIL artifact-untraversable:" in out.getvalue(), out.getvalue()
        assert "is empty" in out.getvalue(), out.getvalue()

    @pytest.mark.parametrize("kind", ["keyword-map", "search"])
    def test_a_non_mapping_ANGLE_BLOCK_does_not_crash_the_walk(self, kind: str) -> None:
        """The headline fix of the commit before this had NO test in either half.

        `_check_angles` reports a non-mapping angle block and CONTINUES, so two walks inside the
        artifact pass dereferenced it and raised. The exit code stays 2 either way — the rule is
        a package fault — which is exactly why the per-rule exit sweeps could not see it, and why
        the test written for that rule (which calls `check_registry` directly) never reached the
        walk. Reverting either filter leaves the whole suite green without this.
        """
        reg = yaml.safe_load(REGISTRY.read_text())
        reg["angles"].insert(0, "an angle block that is not a mapping")
        f = V.Findings()
        if kind == "keyword-map":
            doc = yaml.safe_load(
                (FIXTURES / "scale-vocabulary-map.valid.yaml").read_text()
            )
            V.check_map(doc, reg, f)
        else:
            doc = yaml.safe_load((FIXTURES / "search-output-b5.valid.yaml").read_text())
            kmap = yaml.safe_load(
                (FIXTURES / "scale-vocabulary-map.valid.yaml").read_text()
            )
            V.check_search(doc, reg, kmap, f)
        # No exception is the assertion. The finding set must also be the clean one: a walk that
        # silently skipped every angle would raise nothing and check nothing.
        rules = {r for r, _ in f.items}
        assert not rules, rules

    @pytest.mark.parametrize(
        ("which", "expected"),
        [("artifact", 1), ("keyword-map", 2), ("extract-record", 2)],
    )
    def test_an_EMPTY_file_is_classed_by_WHO_WROTE_IT(
        self, which: str, expected: int
    ) -> None:
        """The asymmetry is the rule, and it is pinned so nobody "fixes" it into consistency.

        A reviewer read empty-artifact-at-1 beside empty-keyword-map-at-2 as an inconsistency.
        It is not: the class turns on who can REPAIR the fault. The running agent wrote the
        artifact and can rewrite it; the keyword map and the extract records were written by
        sibling agents in earlier waves, so an empty one means the dispatcher must re-run that
        wave — which is what exit 2, "unusable", says.
        """
        import contextlib
        import io
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            empty = pathlib.Path(td) / "empty.yaml"
            empty.write_text("# nothing but a comment\n")
            if which == "artifact":
                argv = ["keyword-map", str(empty)]
            elif which == "keyword-map":
                argv = [
                    "search",
                    str(FIXTURES / "search-output-b5.valid.yaml"),
                    "--keyword-map",
                    str(empty),
                ]
            else:
                extracts = pathlib.Path(td) / "extracts"
                extracts.mkdir()
                (extracts / "e.yaml").write_text("# nothing but a comment\n")
                argv = [
                    "synthesis",
                    str(FIXTURES / "scale-envelope-index.valid.yaml"),
                    "--extracts",
                    str(extracts),
                ]
            with contextlib.redirect_stdout(io.StringIO()) as out:
                code = V.main(argv)
        assert code == expected, (which, code, out.getvalue())

    def test_a_non_mapping_artifact_is_the_AUTHORS_fault(self) -> None:
        """A list where a mapping belongs read and parsed; only its content is wrong. It filed
        under `input` at exit 2, routing a repairable artifact to the package owner."""
        import contextlib
        import io
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            target = pathlib.Path(td) / "alist.yaml"
            target.write_text("- a\n- b\n")
            with contextlib.redirect_stdout(io.StringIO()) as out:
                code = V.main(["keyword-map", str(target)])
        assert code == 1, (code, out.getvalue())
        assert "FAIL artifact-untraversable:" in out.getvalue(), out.getvalue()

    def test_an_INVALID_schema_file_fires_schema_unavailable(self) -> None:
        """A schema that JSON-LOADS and is not a schema. Reverting its guard left 724 green."""
        import json

        f = V.Findings()
        broken = {"type": "object", "properties": {"x": {"type": "strng"}}}
        real = V.load_schema
        try:
            V.load_schema = lambda name, f: broken  # noqa: ARG005
            V.check_schema({"x": 1}, "extract-output", f)
        finally:
            V.load_schema = real
        assert "schema-unavailable" in {r for r, _ in f.items}
        assert json  # the import is the shape this test is about

    def test_an_angle_id_that_is_not_a_registry_angle_fires(self) -> None:
        """`coverage-grid-1a`'s OTHER branch. Its first was tested; this one degraded into a
        crash instead."""
        reg = yaml.safe_load(REGISTRY.read_text())
        doc = yaml.safe_load((FIXTURES / "search-output-b5.valid.yaml").read_text())
        doc["meta"]["angle_id"] = "b99"
        f = V.Findings()
        V.check_search(doc, reg, {}, f)
        assert "coverage-grid-1a" in {r for r, _ in f.items}

    def test_found_by_naming_an_UNREACHED_cell_fires(self) -> None:
        """`admission-2d`. The cell exists, so the id resolves; it was never reached, so the row
        cites evidence this run did not gather. Deleted, the suite stayed green at exit 0."""
        reg = yaml.safe_load(REGISTRY.read_text())
        kmap = yaml.safe_load(
            (FIXTURES / "scale-vocabulary-map.valid.yaml").read_text()
        )
        doc = yaml.safe_load((FIXTURES / "search-output-b5.valid.yaml").read_text())
        unreached = next(c for c in doc["coverage"] if c["status"] != "reached")
        doc["candidates"][0]["found_by"] = (
            f"{unreached['group_id']}/{unreached['source_id']}"
        )
        f = V.Findings()
        V.check_search(doc, reg, kmap, f)
        assert "admission-2d" in {r for r, _ in f.items}

    @pytest.mark.parametrize(
        ("source_id", "id_class"),
        [("DOI-10.1000/x", "WEB"), ("example.invalid-nostat", "WEB")],
        ids=["prefix-of-the-wrong-class", "no-prefix-at-all"],
    )
    def test_each_id_prefix_BRANCH_fires(self, source_id: str, id_class: str) -> None:
        """`id-grammar-2` has TWO prefix branches and one mirror reaching neither. The comment
        beside them records that the clause was once defined and read by nothing; both halves
        were then implemented and neither was pinned."""
        doc = yaml.safe_load((FIXTURES / "extract-output.valid.yaml").read_text())
        doc["meta"]["source_id"] = source_id
        doc["meta"]["id_class"] = id_class
        for n, ep in enumerate(doc["episodes"], 1):
            ep["id"] = f"{source_id}#e{n}"
        f = V.Findings()
        V.check_ids(doc, f)
        assert "id-grammar-2" in {r for r, _ in f.items}

    def test_an_extracted_record_with_NO_body_fires(self) -> None:
        """`body-sections-1`'s missing-file branch. Running the family only where the file is
        present is a check over the population that already satisfies it — and deleting the
        branch left the suite green at exit 0."""
        import contextlib
        import io
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            target = pathlib.Path(td) / "nobody.yaml"
            target.write_text((FIXTURES / "extract-output.valid.yaml").read_text())
            with contextlib.redirect_stdout(io.StringIO()) as out:
                code = V.main(["extract", str(target)])
        assert code == 1, (code, out.getvalue())
        assert "FAIL body-sections-1:" in out.getvalue(), out.getvalue()

    @pytest.mark.parametrize("missing", ["yaml", "jsonschema"])
    def test_an_absent_dependency_fires_from_every_site(self, missing: str) -> None:
        """`dependency-missing` has three sites and none was pinned."""
        import builtins

        real = builtins.__import__

        def refuse(name, *args, **kwargs):
            if name == missing:
                raise ModuleNotFoundError(name)
            return real(name, *args, **kwargs)

        # ONE Findings PER SITE. Calling two sites into a shared one meant either alone
        # satisfied the assertion, so neither was pinned — the "a rule is pinned when SOME test
        # names it" hole, reproduced inside the test written to close it.
        def under_refusal(call) -> set:
            f = V.Findings()
            builtins.__import__ = refuse
            try:
                call(f)
            finally:
                builtins.__import__ = real
            return {r for r, _ in f.items}

        if missing == "yaml":
            sites = [
                lambda f: V.load_yaml(
                    FIXTURES / "extract-output.valid.yaml", f, rule="input"
                ),
                V.unsourced_dimensions,
            ]
        else:
            sites = [lambda f: V.check_schema({}, "extract-output", f)]
        for call in sites:
            assert "dependency-missing" in under_refusal(call)

    @pytest.mark.parametrize(
        ("queue_body", "rule", "code"),
        [
            (None, "queue-unreadable", 2),
            (
                "queue: [{item_id: WEB-nobody-extracted-me}]\n",
                "queue-row-without-record",
                1,
            ),
        ],
        ids=["path-is-not-a-file", "row-produced-no-record"],
    )
    def test_the_frozen_QUEUE_is_reconciled(
        self, queue_body: str | None, rule: str, code: int
    ) -> None:
        """`--queue` was declared, promised by the signature, and read by NOTHING.

        The queue and the files are reconciled in BOTH directions, and nothing else can see
        either gap: the index and the records show only what EXISTS. An earlier revision of this
        docstring said `episode -> index` was checked; it never was, and the rule built to make
        that sentence true was wrong and was removed. A bail that wrote nothing deflates
        the survey and the gate reported neither. Four siblings implement it.
        """
        import contextlib
        import io
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            queue = pathlib.Path(td) / "extract-queue.yaml"
            if queue_body is not None:
                queue.write_text(queue_body)
            with contextlib.redirect_stdout(io.StringIO()) as out:
                result = V.main(
                    [
                        "synthesis",
                        str(FIXTURES / "scale-envelope-index.valid.yaml"),
                        "--extracts",
                        str(FIXTURES / "extracts"),
                        "--queue",
                        str(queue),
                    ]
                )
        assert result == code, (result, out.getvalue())
        assert f"FAIL {rule}:" in out.getvalue(), out.getvalue()

    def test_a_queue_whose_every_row_HAS_a_record_is_clean(self) -> None:
        """The narrow mirror. The record the calibration extract writes is the one the queue
        names, so a correct queue must produce nothing."""
        import contextlib
        import io
        import tempfile

        item = yaml.safe_load((FIXTURES / "extract-output.valid.yaml").read_text())[
            "meta"
        ]["source_id"]
        with tempfile.TemporaryDirectory() as td:
            queue = pathlib.Path(td) / "extract-queue.yaml"
            queue.write_text(yaml.safe_dump({"queue": [{"item_id": item}]}))
            with contextlib.redirect_stdout(io.StringIO()) as out:
                result = V.main(
                    [
                        "synthesis",
                        str(FIXTURES / "scale-envelope-index.valid.yaml"),
                        "--extracts",
                        str(FIXTURES / "extracts"),
                        "--queue",
                        str(queue),
                    ]
                )
        assert (result, out.getvalue()) == (0, ""), out.getvalue()

    @staticmethod
    def _extracts_with_an_extra_record(tmp_path, **overrides):
        """The clean extracts directory plus ONE more record, whose episodes nothing cites."""
        import shutil

        out = tmp_path / "extracts"
        shutil.copytree(FIXTURES / "extracts", out)
        extra = yaml.safe_load((FIXTURES / "extract-output.valid.yaml").read_text())
        extra["meta"]["source_id"] = "WEB-a-record-the-index-never-touched"
        for n, ep in enumerate(extra["episodes"], 1):
            ep["id"] = f"{extra['meta']['source_id']}#e{n}"
        extra.update(overrides)
        (out / f"extract-{extra['meta']['source_id']}.yaml").write_text(
            yaml.safe_dump(extra)
        )
        return out

    def _synthesis_over(self, extracts):
        import contextlib
        import io

        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = V.main(
                [
                    "synthesis",
                    str(FIXTURES / "scale-envelope-index.valid.yaml"),
                    "--extracts",
                    str(extracts),
                    "--queue",
                    str(FIXTURES / "extract-queue.valid.yaml"),
                ]
            )
        return code, out.getvalue()

    def test_a_record_NO_queue_ROW_asked_for_is_REFUSED(self, tmp_path) -> None:
        """The MIRROR of `queue-row-without-record`, and the reason the first mirror was wrong.

        A rule refusing an extract record no AREA cites was built here and removed the same day:
        the quality filter ranks and never cuts, so a source satisfying none of the ten signals
        is still extracted and may honestly back no area; the synthesis agent is a separate
        dispatch and does not own the wave-2 records; and the escape it offered — re-record it as
        `outcome: skipped` — is schema-forbidden to keep its content. Its cheapest route to
        exit 0 was padding an area, which is the failure the quality filter exists against.

        The manifest is the QUEUE. A file no row asked for is a rename leftover or a source
        never admitted, and it is invisible to the row direction. Named by FILENAME, because a
        leftover's internal metadata is exactly what cannot be trusted.
        """
        rule = "record-without-queue-row"
        extracts = self._extracts_plus_one_stray(tmp_path)
        code, text = self._synthesis_over(extracts)
        assert code == 1, (code, text)
        assert text.count(f"FAIL {rule}:") == 1, text
        assert "extract-WEB-nobody-queued-me.yaml" in text, text

    def test_every_DOCUMENTED_record_filename_matches_the_FUNCTION(self) -> None:
        """The producer-facing tables, checked against the code they describe.

        The first attempt at documenting this TRANSCRIBED the algorithm and got three clauses
        wrong — the prefix cap (40 for 80), per-character replacement where the code collapses
        each RUN, and no mention of the trailing strip. Both worked examples passed anyway,
        because both dodged all three: one took the identity branch and the other sanitized to
        27 characters with a single separator. **Worked examples that avoid every divergence
        verify nothing**, which is the subset-that-already-satisfies-the-claim shape one level
        up from where it usually appears.

        So the examples are PARSED OUT of the shipped documents and re-derived. Any id whose
        derivation the documents get wrong fails here, and the documents now NAME the function
        rather than restating it — which is what the sibling that ships this does.
        """
        import inspect
        import re

        pattern = re.compile(r"^ *\| `([^`]+)` \| `extract-([^`]+)\.yaml` \|", re.M)
        checked = 0
        for doc in (
            PKG / "SKILL.md",
            PKG / "references" / "extraction-template-guide.md",
        ):
            rows = pattern.findall(doc.read_text())
            assert rows, f"{doc.name} carries no filename example table"
            for item_id, stem in rows:
                assert stem == V.record_filename(item_id), (doc.name, item_id, stem)
                checked += 1
        # The population must WITNESS EVERY BRANCH. Naming the branches in a comment and
        # asserting two of them is what shipped the last two wrong descriptions: the first
        # missed the cap, the collapse and the strip; the second still missed the strip and the
        # hashed-stem refusal, in the fix for the first. Each witness below is tied to the token
        # in the function that creates the branch, so a branch cannot be dropped from the
        # function while its witness still passes.
        #
        # What this does NOT cover: a branch ADDED to the function later has no witness here and
        # nothing will ask for one. That is why the documents no longer describe the function at
        # all — they name it, and tell the reader to run it.
        source = inspect.getsource(V.record_filename)
        ids = [i for i, _ in pattern.findall((PKG / "SKILL.md").read_text())]
        san = re.compile(r"[^A-Za-z0-9._-]+")
        witnesses = {
            "identity": ("return item_id", lambda i: V.record_filename(i) == i),
            "hashed-stem refused": (
                "HASHED_STEM",
                lambda i: bool(V.HASHED_STEM.search(i)) and V.record_filename(i) != i,
            ),
            "prefix cap": ("PREFIX_CAP", lambda i: len(san.sub("-", i)) > V.PREFIX_CAP),
            # The RUN collapse — the `+` in the character class. It is the clause the first
            # prose description got wrong, it was the only branch with no witness, and its
            # coverage was accidental: a four-row table satisfying every other witness with no
            # collapsing id exists, and against it the `+` is undetectable.
            "run collapse": (
                'r"[^A-Za-z0-9._-]+"',
                lambda i: re.search(r"[^A-Za-z0-9._-]{2,}", i) is not None,
            ),
            # A legal source id carries only `[A-Za-z0-9._/-]`, so the ONLY collapsible run is a
            # doubled slash. The first table witnessed this with `://` — and `:` is outside the
            # id grammar, so those two rows were not source ids at all (see the legality
            # assertion below).
            "trailing strip": (
                '.strip("-")',
                lambda i: san.sub("-", i)[: V.PREFIX_CAP]
                != san.sub("-", i)[: V.PREFIX_CAP].strip("-"),
            ),
        }
        for branch, (token, holds) in witnesses.items():
            assert token in source, f"{branch}: `{token}` is gone from record_filename"
            assert any(holds(i) for i in ids), (
                f"no documented example witnesses {branch}"
            )
        # EVERY documented id must be an id this type can actually USE. The cap and strip
        # witnesses were URLs carrying schemes; `:` is outside the id grammar, so `id-grammar-1`
        # refuses every episode of any record for them, and a producer copying the guide's shape
        # writes a record the gate cannot accept. The COLD RUN found this and worked around it
        # by choosing a scheme-less id — a workaround the guide never told it to make.
        illegal = [
            i
            for i in ids
            if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]*", i)
            or not V.EPISODE_ID.match(f"{i}#e1")
        ]
        assert not illegal, {"documented ids that cannot carry an episode": illegal}
        assert checked >= 14, checked

    def test_a_declared_term_QUERIED_NOWHERE_is_refused(self) -> None:
        """The converse of clause (5), and the gate now owns it.

        Clause (5) checks that every query names a declared term. Nothing checked the other
        direction, so a group could declare a term and no cell query it — and the
        proportionality run found exactly that: three terms dropped with no `notes[]` at all,
        two of them lifted from the scope's own first sentence. It had to read every cell's
        queries against every group by hand. `expansion_cap` is a maximum so a run MAY query
        fewer terms; what it may not do is drop one silently, and that is arithmetic.
        """
        reg = yaml.safe_load(REGISTRY.read_text())
        kmap = yaml.safe_load((FIXTURES / MAP).read_text())
        doc = yaml.safe_load((FIXTURES / SEARCH).read_text())
        f = V.Findings()
        V.check_search(doc, reg, kmap, f)
        assert "coverage-grid-6" not in {r for r, _ in f.items}, [
            m for r, m in f.items if r == "coverage-grid-6"
        ]
        # Declare a term nothing queries, with no note accounting for it.
        applicable = {c["group_id"] for c in doc["coverage"]}
        target = next(g for g in kmap["groups"] if g["id"] in applicable)
        target["expansions"] = [*target["expansions"], "a-term-no-cell-queries"]
        f = V.Findings()
        V.check_search(doc, reg, kmap, f)
        assert "coverage-grid-6" in {r for r, _ in f.items}
        # The narrow mirror: naming it in `notes[]` with a reason is the documented way out.
        doc["notes"] = [
            "`a-term-no-cell-queries` was dropped: the corpus spells it two ways."
        ]
        f = V.Findings()
        V.check_search(doc, reg, kmap, f)
        assert "coverage-grid-6" not in {r for r, _ in f.items}

    def test_the_DECIDING_value_must_be_a_path_the_PREDICATES_turn_on(self) -> None:
        """`map-completeness-6` accepted any lowercase dotted token in the reason.

        "kafka.apache.org was down" satisfied a rule whose entire point is that a refusal names
        the classification value it turned on — found by the cold run. The vocabulary is derived
        from the registry's own predicates, not from the map's `meta.classification`: a map
        carries the blocks it needs, and four of the six refusals in this package's own
        calibration fixture name a block that map does not carry.
        """
        reg = yaml.safe_load(REGISTRY.read_text())
        paths = V.predicate_paths(reg)
        assert "scale.geo_distribution" in paths and len(paths) >= 15, sorted(paths)
        doc = yaml.safe_load((FIXTURES / MAP).read_text())
        for verdict in doc["angle_applicability"]:
            if verdict["holds"] is False:
                verdict["reason"] = "kafka.apache.org was down when we looked."
        f = V.Findings()
        V.check_map(doc, reg, f)
        assert "map-completeness-6" in {r for r, _ in f.items}

    def test_sources_md_ENUMERATIONS_are_derived_from_the_registry(self) -> None:
        """Nine sentences in `sources.md` name registry rows, and one of them was wrong.

        It said two rows carry `complete_listing: n/a` where the registry has THREE — leaving
        `jepsen-consistency`, a row the cold run queried twice and got zero from both times, with
        no stated reading for its zero, in the file whose whole job is to say what a zero from
        each row means. The two claims that are mechanically checkable are checked; the others
        are prose about what a row IS, which is not derivable.
        """
        reg = yaml.safe_load(REGISTRY.read_text())
        ids = {s["id"] for s in reg["sources"]}
        text = (PKG / "references" / "sources.md").read_text()
        na = sorted(
            s["id"] for s in reg["sources"] if s.get("complete_listing") == "n/a"
        )
        line = next(
            row for row in text.splitlines() if "carry `complete_listing: n/a`" in row
        )
        assert sorted(i for i in ids if f"`{i}`" in line) == na, (line, na)
        # The channel-family table PARTITIONS the registry: every row in exactly one family.
        rows = [
            row
            for row in text.splitlines()
            if row.startswith("| ") and any(f"`{i}`" in row for i in ids)
        ]
        placed = {i: sum(f"`{i}`" in row for row in rows) for i in ids}
        assert all(n == 1 for n in placed.values()), {
            "in no family": sorted(i for i, n in placed.items() if n == 0),
            "in more than one": sorted(i for i, n in placed.items() if n > 1),
        }

    def test_no_producer_document_DESCRIBES_the_filename_function(self) -> None:
        """ "Describe it NOWHERE" is a claim about the shipped files, so it is checked over them.

        The fold that wrote that claim deleted the description from three places and left it
        standing in a FOURTH — nineteen lines below the paragraph that removed it, in the same
        file — because nothing asked. The tokens below are the vocabulary of the algorithm: a
        document that needs them is describing the function instead of naming it.
        """
        # `sanitiz` alone is too broad — `sanitization{status, cause}` is an unrelated FIELD
        # this type records on every row, and a guard that fires on it would be turned off
        # rather than obeyed. The tokens are the algorithm's own vocabulary, not the word stem.
        forbidden = (
            "digest",
            "the sanitizer",
            "collaps",
            "truncat",
            "sha-256",
            "prefix cap",
            "hashed stem",
        )
        offenders = [
            f"{doc.name}:{n}: {line.strip()[:70]}"
            for doc in (
                PKG / "SKILL.md",
                PKG / "references" / "extraction-template-guide.md",
            )
            for n, line in enumerate(doc.read_text().splitlines(), 1)
            for token in forbidden
            if token in line.lower()
        ]
        assert not offenders, offenders

    @pytest.mark.parametrize(
        "path", ["not-run", "unknown-angle", "grid-derivation"], ids=lambda p: p
    )
    def test_the_keyword_map_SKIP_is_reported_on_EVERY_path(self, path: str) -> None:
        """Three paths end without an owed grid, and only one of them said so.

        Swapping the artifact and the map on the command line — the commonest two-argument
        error — took the unknown-angle path and reported no skip at all. The fold moved the
        emission into one helper, which fixed the behaviour and left two of its three call sites
        with no test: the kill sweep suppresses by LINE, so one shared `_fail` reads as covered
        while two of its reachable paths are unexercised. A shared emitter is a way to hide call
        sites from the tool whose whole purpose is finding them.
        """
        reg = yaml.safe_load(REGISTRY.read_text())
        doc = yaml.safe_load((FIXTURES / SEARCH).read_text())
        if path == "not-run":
            doc = {
                "schema_version": 1,
                "meta": doc["meta"],
                "outcome": "not_run",
                "not_run": {"map_verdict": "b5 does not hold"},
            }
        elif path == "unknown-angle":
            doc["meta"] = dict(doc["meta"], angle_id="not-an-angle")
        f = V.Findings()
        V.check_search(doc, reg, None, f)
        assert "keyword-map-crosscheck-skipped" in {r for r, _ in f.items}

    def test_the_queue_reconciles_a_DERIVED_filename(self, tmp_path) -> None:
        """Every queue test used an id `record_filename` returns UNCHANGED.

        `WEB-techempower-run-3`, `WEB-nobody-extracted-me`, `WEB-nobody-queued-me` all take the
        identity branch, where `f(x) == x` — so the whole population was the subset that already
        satisfies the claim, and neither direction of the reconciliation had ever been exercised
        against the derivation it actually performs. A DOI always contains `/`, which makes the
        derived form this type's ORDINARY case.
        """
        import contextlib
        import io
        import shutil

        item = "DOI-10.1145/3477132.3483577"
        stem = V.record_filename(item)
        assert stem != item, "pick an id the sanitizer actually touches"
        extracts = tmp_path / "extracts"
        shutil.copytree(FIXTURES / "extracts", extracts)
        record = yaml.safe_load((FIXTURES / "extract-output.valid.yaml").read_text())
        record["meta"]["source_id"] = item
        record["meta"]["id_class"] = "DOI"
        for n, ep in enumerate(record["episodes"], 1):
            ep["id"] = f"{item}#e{n}"
        (extracts / f"extract-{stem}.yaml").write_text(yaml.safe_dump(record))
        queue = tmp_path / "queue.yaml"
        queue.write_text(
            yaml.safe_dump(
                {"queue": [{"item_id": "WEB-techempower-run-3"}, {"item_id": item}]}
            )
        )
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = V.main(
                [
                    "synthesis",
                    str(FIXTURES / "scale-envelope-index.valid.yaml"),
                    "--extracts",
                    str(extracts),
                    "--queue",
                    str(queue),
                ]
            )
        assert (code, out.getvalue()) == (0, ""), out.getvalue()

    def test_a_record_written_under_the_RAW_id_is_reported_BOTH_ways(
        self, tmp_path
    ) -> None:
        """The failure a producer following the SKILL literally would have produced.

        Until this fold the derivation appeared in no producer-facing file — the validator's own
        comment cited the SKILL as its authority for a rule the SKILL did not state. A record
        written under the raw id is valid, sits where nothing looks, and draws BOTH halves of the
        reconciliation at once. Both messages must now say so.
        """
        import contextlib
        import io
        import shutil

        item = "DOI-10.1145/3477132.3483577"
        extracts = tmp_path / "extracts"
        shutil.copytree(FIXTURES / "extracts", extracts)
        record = yaml.safe_load((FIXTURES / "extract-output.valid.yaml").read_text())
        record["meta"]["source_id"] = item
        raw = extracts / f"extract-{item.replace('/', '_')}.yaml"
        raw.write_text(yaml.safe_dump(record))
        queue = tmp_path / "queue.yaml"
        queue.write_text(
            yaml.safe_dump(
                {"queue": [{"item_id": "WEB-techempower-run-3"}, {"item_id": item}]}
            )
        )
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = V.main(
                [
                    "synthesis",
                    str(FIXTURES / "scale-envelope-index.valid.yaml"),
                    "--extracts",
                    str(extracts),
                    "--queue",
                    str(queue),
                ]
            )
        text = out.getvalue()
        assert code == 1, (code, text)
        assert "FAIL queue-row-without-record:" in text, text
        assert "FAIL record-without-queue-row:" in text, text
        assert "DERIVED from the id" in text, text
        assert "written under the RAW id" in text, text
        # And it must NOT push the author toward the escape that deletes the extraction.
        assert "A bail still writes a skip record" not in text, text

    def test_the_clean_set_reconciles_in_BOTH_directions(self) -> None:
        """The narrow mirror. Every record has its row and every row has its record, so the
        calibration pair must produce nothing at all."""
        assert self._synthesis_over(FIXTURES / "extracts") == (0, "")

    @staticmethod
    def _extracts_plus_one_stray(tmp_path):
        import shutil

        out = tmp_path / "extracts"
        shutil.copytree(FIXTURES / "extracts", out)
        stray = yaml.safe_load((FIXTURES / "extract-output.valid.yaml").read_text())
        stray["meta"]["source_id"] = "WEB-nobody-queued-me"
        (out / "extract-WEB-nobody-queued-me.yaml").write_text(yaml.safe_dump(stray))
        return out

    def _synthesis_over(self, extracts):
        import contextlib
        import io

        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = V.main(
                [
                    "synthesis",
                    str(FIXTURES / "scale-envelope-index.valid.yaml"),
                    "--extracts",
                    str(extracts),
                    "--queue",
                    str(FIXTURES / "extract-queue.valid.yaml"),
                ]
            )
        return code, out.getvalue()

    #: Each kind's top-level check functions, and the schema its artifact is validated against.
    #: The pairing is what makes the sweep below decidable: a key read by one kind's checks must
    #: be declared by that kind's schema.
    KIND_CHECKS = {
        "scale-vocabulary-map": ["check_map"],
        "search-output": ["check_search", "check_cell_sanitization"],
        "extract-output": [
            "check_extract",
            "check_confidence",
            "check_load_band",
            "check_ids",
            "check_score",
        ],
        "scale-envelope-index": ["check_synthesis"],
    }

    #: What this sweep does NOT cover, stated rather than implied. `check_queue`'s document is
    #: the frozen QUEUE, not the artifact, and it has no schema in this package — pairing it
    #: with the index schema reported `queue` as undeclared, which is the guard misreading its
    #: own subject. And a key read inside a HELPER the check calls (`check_band` reads
    #: `project_band`) is not in the walk, so the sweep is a subset check: it catches a key the
    #: schema forbids, never a key the schema declares and nothing reads.

    #: Rules that fire on a condition the artifact's JSON Schema ALSO refuses, so the run
    #: prints two findings for one fault. DECLARED, with the schema constraint each one doubles
    #: and the reason it stays: in every case the rule NAMES THE AREA and the schema names a
    #: JSON path, and the specific message is the one a producer acts on.
    #:
    #: Deleting them was considered and rejected — it costs the better message on the commonest
    #: structural defects. Making the schema RETURN EARLY was considered and rejected — it
    #: suppresses every content finding on any schema-invalid document and turns one round trip
    #: into several. What was NOT acceptable is the state this replaced: the overlap existed,
    #: §13 asserted it could not, and nothing anywhere could see it.
    #: The path is walked KEY BY KEY through the schema document, `properties` and `items`
    #: included, so there is no cleverness to get wrong.
    SCHEMA_OVERLAP = {
        "synthesis-1a": ("properties.areas.items.properties.evidence", "minItems"),
        "currency-1": ("properties.areas.items", "required"),
        "synthesis-3b": (
            "properties.areas.items.properties.failure_modes.items.properties.evidence",
            "minItems",
        ),
    }

    def test_every_DECLARED_schema_overlap_is_REAL(self) -> None:
        """A declaration set that is never checked becomes a list of things that used to be true.

        Each member names the schema constraint it doubles, and this resolves that constraint in
        the shipped schema. A rule removed, or a schema relaxed, leaves a stale entry — which is
        how the overlap became invisible in the first place.

        **What it does not cover:** it will not FIND a new overlap. The measurement that would —
        applying every mutation and checking whether the mutated document is schema-invalid —
        was built and rejected as unsound: mutations are coarser than the rules they trigger, so
        it reported twenty-odd members, including `synthesis-3a`, whose constraint the schema
        does not carry at all (`migration_trigger` declares no `required` and an empty schema for
        its `evidence`). A guard that reports members it cannot justify is worse than the gap.
        """
        import json

        schema = json.loads(
            (PKG / "schemas" / "scale-envelope-index.schema.json").read_text()
        )
        for rule, (path, constraint) in self.SCHEMA_OVERLAP.items():
            node = schema
            for part in path.split("."):
                assert part in node, (rule, path, part, sorted(node))
                node = node[part]
            assert constraint in node, (rule, path, constraint, sorted(node))
        # And `currency-1`'s constraint is `required` at the AREA level, so name the field too.
        area = schema["properties"]["areas"]["items"]
        assert "currency" in area["required"], sorted(area["required"])

    def test_NOTHING_in_either_package_is_UNTRACKED(self) -> None:
        """The general form of the schema guard, because the defect was never about schemas.

        A file written, wired in and never staged is present on disk for every run of this suite
        and absent from the package everyone else gets. The first guard for it asked about one
        directory; the validator opens `references/source-registry.yaml` and
        `references/load-band-thresholds.md` on EVERY run of all four kinds, and each has its own
        exit-2 package-fault rule — an untracked registry is the same defect and strictly worse.

        So the question is asked once, over both packages: nothing untracked, and git decides.
        """
        import subprocess

        try:
            proc = subprocess.run(
                [
                    "git",
                    "-C",
                    str(ROOT),
                    "ls-files",
                    "--others",
                    "--exclude-standard",
                    "--",
                    str(PKG.relative_to(ROOT)),
                    str(TWIN.relative_to(ROOT)),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError:  # git not on PATH — the package ships without one
            pytest.skip("git is not installed")
        if "not a git repository" in proc.stderr:
            pytest.skip("not a git checkout — the package ships without one")
        assert proc.returncode == 0, proc.stderr.strip()
        untracked = [ln for ln in proc.stdout.splitlines() if ln.strip()]
        assert not untracked, untracked

    def test_every_SCHEMA_the_validator_NAMES_ships_with_the_package(self) -> None:
        """A schema the code loads and the package does not carry breaks every run that needs it.

        The queue's schema was written and left UNTRACKED. `load_schema` files
        `schema-unavailable` — a package fault — so a commit that missed the file would have
        turned every `--queue` run into an exit-2 refusal for every consumer, with nothing in the
        suite to notice: the tests run against a working tree that has the file. The names are
        walked out of the source rather than listed, so a schema added later is covered without
        editing this.
        """
        import ast

        named = {
            node.args[i].value
            for node in ast.walk(
                ast.parse((HERE / "validate_scale_prior_art.py").read_text())
            )
            if isinstance(node, ast.Call)
            and getattr(node.func, "id", "")
            in {"load_schema", "check_schema", "is_the_document"}
            for i in ([0] if getattr(node.func, "id", "") == "load_schema" else [1])
            if len(node.args) > i and isinstance(node.args[i], ast.Constant)
        }
        assert len(named) >= 5, sorted(named)
        missing = sorted(
            n for n in named if not (SCHEMAS / f"{n}.schema.json").is_file()
        )
        assert not missing, missing
        # …and TRACKED, which is the ACTUAL defect. `is_file()` is a working-tree question, and
        # the failure was a schema written, wired into the validator, and never staged — present
        # on disk for every run of this suite and absent from the package everyone else gets.
        # A guard that cannot see the defect it was written for is worse than none, because it
        # is quoted as covering it. Ask git.
        import subprocess

        rel = [
            str((SCHEMAS / f"{n}.schema.json").relative_to(ROOT)) for n in sorted(named)
        ]
        try:
            proc = subprocess.run(
                ["git", "-C", str(ROOT), "ls-files", "--error-unmatch", "--", *rel],
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError:  # git not on PATH — the package ships without one
            pytest.skip("git is not installed")
        if "not a git repository" in proc.stderr:
            pytest.skip("not a git checkout — the package ships without one")
        assert proc.returncode == 0, proc.stderr.strip()

    def test_every_TOP_LEVEL_key_a_check_reads_is_DECLARED_by_its_schema(self) -> None:
        """A rule keyed on a field the schema forbids can never fire on a valid artifact.

        `lineage-liveness-1` keys on `mode`, and the index schema — root closed to additional
        properties — did not declare it. Every `mode: delta` document was therefore refused by
        `schema` before the rule was consulted, so the rule was dead in the mirror direction of
        the dead-FIELD defect the `lineage` family exists to prevent. Nothing caught it because
        every mutation proving the rule fires calls the check function DIRECTLY and never runs
        the schema.

        This is the mechanical form: for each kind, the literal keys its checks read off the
        document must all be declared properties of that kind's schema.
        """
        import ast
        import json

        functions = {
            node.name: node
            for node in ast.walk(
                ast.parse((HERE / "validate_scale_prior_art.py").read_text())
            )
            if isinstance(node, ast.FunctionDef)
        }
        offenders = {}
        for schema_name, names in self.KIND_CHECKS.items():
            declared = set(
                json.loads(
                    (PKG / "schemas" / f"{schema_name}.schema.json").read_text()
                )["properties"]
            )
            read: set = set()
            for name in names:
                for node in ast.walk(functions[name]):
                    if (
                        isinstance(node, ast.Call)
                        and isinstance(node.func, ast.Attribute)
                        and node.func.attr == "get"
                        and isinstance(node.func.value, ast.Name)
                        and node.func.value.id == "doc"
                        and node.args
                        and isinstance(node.args[0], ast.Constant)
                    ):
                        read.add(node.args[0].value)
            if read - declared:
                offenders[schema_name] = sorted(read - declared)
        assert not offenders, offenders

    def test_the_delta_rule_fires_on_a_SCHEMA_VALID_document(self, tmp_path) -> None:
        """A rule that can only fire on an artifact the gate already refused is DEAD.

        `lineage-liveness-1` keys on `mode`, and `mode` was not declared in a schema whose root
        forbids additional properties — so every `mode: delta` document was refused by `schema`
        first, and the only tests proving the rule fires called the synthesis check directly and
        never ran the schema at all. This runs the CLI and requires the rule to fire with NO
        accompanying `schema` finding: the document must be legal.
        """
        import contextlib
        import io

        doc = yaml.safe_load((FIXTURES / "scale-envelope-index.valid.yaml").read_text())
        doc["mode"] = "delta"
        doc["lineage"] = {"extends": None}
        target = tmp_path / "delta-index.yaml"
        target.write_text(yaml.safe_dump(doc))
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = V.main(
                [
                    "synthesis",
                    str(target),
                    "--extracts",
                    str(FIXTURES / "extracts"),
                    "--queue",
                    str(FIXTURES / "extract-queue.valid.yaml"),
                ]
            )
        text = out.getvalue()
        assert "FAIL schema:" not in text, text
        assert "FAIL lineage-liveness-1:" in text, text
        assert code == 1, (code, text)

    def test_a_delta_index_that_NAMES_its_baseline_is_clean(self, tmp_path) -> None:
        """The narrow mirror, and the boundary of what this rule claims. It checks that a delta
        index NAMES a baseline; it does not resolve the name to a file, because where a baseline
        lives is not settled and a resolution rule would invent the layout it checks."""
        import contextlib
        import io

        doc = yaml.safe_load((FIXTURES / "scale-envelope-index.valid.yaml").read_text())
        doc["mode"] = "delta"
        doc["lineage"] = {"extends": "a-baseline-index-that-is-not-on-disk.yaml"}
        target = tmp_path / "delta-index.yaml"
        target.write_text(yaml.safe_dump(doc))
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = V.main(
                [
                    "synthesis",
                    str(target),
                    "--extracts",
                    str(FIXTURES / "extracts"),
                    "--queue",
                    str(FIXTURES / "extract-queue.valid.yaml"),
                ]
            )
        assert (code, out.getvalue()) == (0, ""), out.getvalue()

    def test_record_filename_2_is_unreachable_by_construction(self) -> None:
        """The one NOT MIRRORABLE rule, named here so nothing has to search a declaration set.

        For any id already ending in a hashed stem the identity branch is refused, so
        `record_filename(f(x)) != f(x)` and the rule cannot fire on any input while the
        implementation is correct.
        """
        rule = "record-filename-2"
        hashed = V.record_filename("WEB-example.invalid/a b")
        assert V.HASHED_STEM.search(hashed)
        assert V.record_filename(hashed) != hashed, f"{rule} would be reachable"

    def test_the_NOT_MIRRORABLE_rule_is_covered_another_way(self) -> None:
        """It has no artifact mutation, so something else must name it. The cross-branch
        collision test constructs the property directly."""
        module = pathlib.Path(__file__).read_text()
        for rule in self.NOT_MIRRORABLE:
            # NOT `"f(f(x))" in module`: the only occurrence of that literal was this line, so
            # the guard proved its own text. The real coverage is a named test, and its absence
            # is what this asserts.
            assert rule in module, rule
            assert "def test_the_cross_branch_collision" in module, rule

    def test_the_table_covers_every_rule_that_had_no_individual_coverage(self) -> None:
        covered = {rule for _, _, _, rule in CLAUSE_MIRRORS} | self.NOT_MIRRORABLE
        still = TestC3mTheMirrorSweepAndUnreachableCode.FAMILY_COVERED_ONLY - covered
        assert not still, {
            "declared family-covered-only and still unmirrored": sorted(still),
            "mirrored": len(covered),
        }


class TestC3mTheMirrorSweepAndUnreachableCode:
    """C3m, the four MECHANICAL halves. EC5's partition is the fifth and is built beside them.

    This whole task was marked DONE, discharging EC5, with nothing behind it: a fresh reviewer
    grepped for `NOT_NEEDED`, `narrow mirror` and a class by this name and found none of them,
    while the sibling package this shape comes from implements all five parts. A status line is
    not a check.
    """

    @staticmethod
    def _tree():
        import ast

        return ast.parse((HERE / "validate_scale_prior_art.py").read_text())

    #: Rules whose SUBJECT is the document, not a row in it. `registry-integrity-1` is about the
    #: registry as a whole; `coverage-grid-1a` is NOT here any more — separating the map-unreadable notice out of it left
    #: only its real artifact defect, which names the angle;
    #: `bound-*` and `bail-*` are about the single `bound`/`skipped` block; `dependency-missing`
    #: and `extracts-crosscheck-skipped` are about the run. A locator on any of them would be the
    #: filename, which the reader already has. DECLARED, in both directions, so a row-level rule
    #: cannot join them by accident.
    WHOLE_ARTIFACT = frozenset(
        {
            "registry-integrity-1",
            "lineage-liveness-1",
            "quality-filter-1a",
            "dependency-missing",
            "bound-2a",
            "bound-2b",
            "bound-3",
            "bail-3",
            "extracts-crosscheck-skipped",
            "queue-crosscheck-skipped",
            "keyword-map-crosscheck-skipped",
        }
    )

    @staticmethod
    def _local_bindings(tree) -> dict:
        """Every `_fail` call in the tree, mapped to its enclosing function's assignments.

        Built from the SAME tree the caller walks. An earlier version re-parsed the file to
        find the enclosing function and compared nodes by identity, which never matched — so
        every f-string was read as carrying a locator and the guard proved nothing new.
        """
        import ast

        # Deliberately LOCAL-ONLY. Following a parameter to its call sites was tried and
        # reverted: it read a call-site variable that happens to share the parameter's name as
        # the parameter itself and looped, and it turned a genuine locator into a false bare.
        # The rule this guard enforces is better served by a validator that builds each message
        # where it emits it — which is now what the validator does.
        out: dict = {}
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            bindings: dict = {}
            for node in ast.walk(fn):
                if isinstance(node, ast.Assign):
                    for tgt in node.targets:
                        if isinstance(tgt, ast.Name):
                            bindings.setdefault(tgt.id, []).append(node.value)
            for node in ast.walk(fn):
                if (
                    isinstance(node, ast.Call)
                    and getattr(node.func, "id", "") == "_fail"
                ):
                    out[id(node)] = bindings
        return out

    def _interpolates_data(self, message, bindings) -> bool:
        """True when an f-string interpolates anything but locally-bound string constants.

        A `FormattedValue` over a bare `Name` is resolved against the assignments in the
        enclosing function: if every binding of that name is a constant — or a conditional
        expression over constants — the interpolation contributes no locator. Anything else
        (an attribute, a call, a subscript, a parameter) is treated as artifact-derived.
        """
        import ast

        def constant_only(node, depth: int = 0) -> bool:
            if depth > 4:
                # A cycle or a chain this long is not something to resolve; call it data.
                return False
            if isinstance(node, ast.Constant):
                return True
            if isinstance(node, ast.IfExp):
                return constant_only(node.body, depth + 1) and constant_only(
                    node.orelse, depth + 1
                )
            if isinstance(node, ast.JoinedStr):
                return all(
                    constant_only(p.value, depth + 1)
                    for p in node.values
                    if isinstance(p, ast.FormattedValue)
                )
            return False

        for part in message.values:
            if not isinstance(part, ast.FormattedValue):
                continue
            value = part.value
            if isinstance(value, ast.Name) and value.id in bindings:
                if all(constant_only(b) for b in bindings[value.id]):
                    continue
            return True
        return False

    #: Rules covered ONLY by a FAMILY-prefix assertion — `assert "coverage-grid" in
    #: _rules(...)` passes for any clause, so each of these can be deleted with the suite
    #: green. That is the gap EC5's partition exists to close and it is NOT closed: this set
    #: makes it VISIBLE and its size measured rather than claimed away. Sixty-six of a
    #: EMPTY, and it was sixty-six. Every per-clause rule is now named by a test of its own —
    #: `CLAUSE_MIRRORS` carries the positive pin and the narrow mirror for each — so the set that
    #: made the gap visible has nothing left in it. Kept rather than deleted because it is the
    #: assertion: a rule added later with only family coverage lands here and fails.
    FAMILY_COVERED_ONLY: frozenset = frozenset()

    def test_the_validator_reads_NO_environment_variable(self) -> None:
        """A sweep left its own patch in the shipped `_fail` and it was committed.

        The sweep rewrites the validator in place and restores it in a `finally`; a run killed by
        a timeout never reached the restore, so an env-var-triggered early return sat in the one
        function every finding passes through — and 562 tests did not notice. A validator's
        behaviour must not depend on the environment at all, which is checkable.
        """
        import ast

        for node in ast.walk(self._tree()):
            if isinstance(node, ast.Attribute) and node.attr in {
                "environ",
                "getenv",
            }:
                raise AssertionError(
                    f"the validator reads the environment at line {node.lineno}"
                )

    def test_no_docstring_has_been_DISPLACED_by_inserted_code(self) -> None:
        """The same accident silently deleted `_fail.__doc__`.

        Code inserted at the top of a function pushes its docstring down, and a string literal
        that is not the FIRST statement is an expression evaluated and thrown away — the
        function loses its documentation and nothing looks. This is narrower than "every
        function has a docstring": several helpers legitimately have none. The defect is a bare
        string sitting BELOW real code.
        """
        import ast

        displaced = [
            f"{node.name}:{stmt.lineno}"
            for node in ast.walk(self._tree())
            if isinstance(node, ast.FunctionDef)
            for stmt in node.body[1:]
            if isinstance(stmt, ast.Expr)
            and isinstance(stmt.value, ast.Constant)
            and isinstance(stmt.value.value, str)
        ]
        assert not displaced, displaced

    def test_every_fail_call_passes_a_LOCATOR(self) -> None:
        """A finding that says WHAT failed without WHERE cannot be acted on.

        The locator is the message's second argument; every call must build one from the
        artifact — an f-string or a name — rather than pass a bare literal sentence.
        """
        import ast

        bare = []
        tree = self._tree()
        bindings_of = self._local_bindings(tree)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if getattr(node.func, "id", "") != "_fail" or len(node.args) < 2:
                continue
            message = node.args[1]
            if isinstance(message, ast.JoinedStr) and not self._interpolates_data(
                message, bindings_of.get(id(node), {})
            ):
                # An f-string whose only interpolations are LOCAL CONSTANTS carries no locator
                # and used to pass as though it did. That is how `queue-crosscheck-skipped`
                # escaped the whole-artifact declaration: `f"{cause}. ..."` where `cause` is a
                # conditional over two literals. The dodge was available to every future rule.
                bare.append(node.args[0].value if node.args else "?")
            elif isinstance(message, ast.Constant):
                bare.append(node.args[0].value if node.args else "?")
            elif isinstance(message, ast.BinOp):
                # an implicit-concatenation chain of constants is still a bare sentence
                parts = [message]
                while parts:
                    part = parts.pop()
                    if isinstance(part, ast.BinOp):
                        parts += [part.left, part.right]
                    elif isinstance(part, ast.JoinedStr):
                        break
                else:
                    bare.append(node.args[0].value if node.args else "?")
        assert set(bare) == self.WHOLE_ARTIFACT, {
            "no locator and not declared whole-artifact": sorted(
                set(bare) - self.WHOLE_ARTIFACT
            ),
            "declared whole-artifact but carries a locator": sorted(
                self.WHOLE_ARTIFACT - set(bare)
            ),
        }

    def test_no_rule_sits_below_an_unconditional_RETURN(self) -> None:
        """A `_fail` after a top-level `return` in the same block never fires."""
        import ast

        offenders = []
        for fn in [n for n in ast.walk(self._tree()) if isinstance(n, ast.FunctionDef)]:
            seen_return = False
            for stmt in fn.body:
                if seen_return:
                    for sub in ast.walk(stmt):
                        if (
                            isinstance(sub, ast.Call)
                            and getattr(sub.func, "id", "") == "_fail"
                            and sub.args
                            and isinstance(sub.args[0], ast.Constant)
                        ):
                            offenders.append(f"{fn.name}: {sub.args[0].value}")
                if isinstance(stmt, ast.Return):
                    seen_return = True
        assert not offenders, offenders

    def test_every_emitted_rule_is_REACHABLE_by_some_test(self) -> None:
        """The assertion this module's other guards point at while it did not exist.

        Every id the validator can emit must be named by at least one test in this module —
        a positive assertion, a mutation-table row, or an exit-class case. A rule nothing names
        can be deleted with the suite green, which is how `currency-1` shipped.
        """

        import ast

        emitted = _emitted_ids(self._tree())
        # NAMED BY A TEST, not mentioned in the file. The first version searched the whole module
        # text, so a rule id sitting in a DECLARATION SET counted as covered by the set that
        # existed to say it was not — the self-match hazard, and it hid `bound-2a` and
        # `coverage-grid-1a`, whose only occurrences in 4,600 lines were inside `WHOLE_ARTIFACT`.
        #
        # A rule is named when it appears inside a test FUNCTION's body, or in a decorator call,
        # which is where the clause-mirror table registers. Class- and module-level assignments
        # are declarations and do not count.
        module_ast = ast.parse(pathlib.Path(__file__).read_text())

        def strings(node) -> set:
            return {
                s.value
                for s in ast.walk(node)
                if isinstance(s, ast.Constant) and isinstance(s.value, str)
            }

        # A module-level TABLE counts when a `parametrize` consumes it — that is a registration,
        # not a declaration. The names are derived from the decorators rather than listed, so a
        # table renamed or a new one added is picked up without editing this.
        parametrized: set = set()
        named: set = set()
        for node in ast.walk(module_ast):
            if isinstance(node, ast.FunctionDef):
                named |= strings(node)
                for dec in node.decorator_list:
                    named |= strings(dec)
                    for sub in ast.walk(dec):
                        if isinstance(sub, ast.Name):
                            parametrized.add(sub.id)
        for node in module_ast.body:
            if isinstance(node, ast.Assign) and any(
                isinstance(tgt, ast.Name) and tgt.id in parametrized
                for tgt in node.targets
            ):
                named |= strings(node.value)
        unnamed = sorted(r for r in emitted if r not in named)
        assert set(unnamed) == self.FAMILY_COVERED_ONLY, {
            "named by nothing and not declared": sorted(
                set(unnamed) - self.FAMILY_COVERED_ONLY
            ),
            "declared but now named individually": sorted(
                self.FAMILY_COVERED_ONLY - set(unnamed)
            ),
        }


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
            "open_gap",
            "outcome_kind",
            "probe",
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
            [
                "synthesis",
                "scale-envelope-index.valid.yaml",
                "--extracts",
                "extracts",
                "--queue",
                "extract-queue.valid.yaml",
            ],
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
