#!/usr/bin/env python
"""Deterministic gate for the scale prior-art survey's four artifact kinds.

Exit contract (spec §5), inherited unchanged because a coordinator reads exit codes and cannot
read prose:

    0  clean
    1  the artifact has findings — its author can repair them
    2  unusable — a fault an artifact author CANNOT repair

`schema` is exit 1: an artifact failing a schema that LOADED is exactly what its author can fix.
`schema-unavailable` is exit 2, because an unloadable schema FILE is a package fault. The split is
tested per rule, never in aggregate.

Run:
    uv run --no-project --with pyyaml --with jsonschema python validate_scale_prior_art.py \
        keyword-map scale-vocabulary-map.yaml
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
PKG = HERE.parent
REGISTRY_PATH = PKG / "references" / "source-registry.yaml"
THRESHOLDS_PATH = PKG / "references" / "load-band-thresholds.md"
SCHEMA_DIR = PKG / "schemas"

#: Rules only a PACKAGE author can cause. They exit 2; everything else exits 1. Derived from
#: this module's own AST by the exit-contract sweep, never hand-listed on both sides.
PACKAGE_FAULT = frozenset(
    {
        "registry-unreadable",
        "registry-integrity",
        "registry-band",
        "registry-access-status",
        "registry-yields",
        "fallback-unresolvable",
        "fallback-cycle",
        "registry-terminal-rationale",
        "registry-probe-method",
        "registry-as-of",
        "angle-predicate-placement",
        "angle-trigger-anchor",
        "angle-widening-legs",
        "angle-seed-input",
        "angle-predicate-omits",
        "angle-sizing-record",
        "schema-unavailable",
        "dependency-missing",
        "input",
    }
)

#: The map's five band leaves, NAMED rather than counted — §13's declared-band family.
BAND_LEAVES = (
    "concurrency",
    "real_time",
    "availability_target",
    "geo_distribution",
    "data_volume",
)
#: The five capability-map `scale` fields declared OPTIONAL. A widener that is a REQUIRED leaf
#: would fail closed on every map that omits it, which is why they are named here.
OPTIONAL_SCALE = (
    "throughput",
    "consistency",
    "burst_traffic",
    "latency_sensitive",
    "stateful",
)
#: Every OPTIONAL capability-map field, not only the scale ones. §12's rule is "naming only
#: OPTIONAL fields", and two of this registry's wideners are `archetype.secondary` and
#: `security.authz_complexity` — a scale-only test refuses both, which is a guard that fails
#: closed on a correct registry. TRANSCRIBED from the schema and asserted equal to it by a test,
#: so the constant cannot drift from the file it came from.
OPTIONAL_FIELDS = frozenset(
    {
        "archetype.lifecycle_stage",
        "archetype.secondary",
        "business.commercialization",
        "business.distribution",
        "business.model",
        "business.open_source",
        "data_ml.data_governance",
        "data_ml.data_volume_class",
        "data_ml.eu_ai_act",
        "data_ml.has_data_pipeline",
        "data_ml.model_governance",
        "data_ml.model_serving",
        "data_ml.pipeline_type",
        "data_ml.responsible_ai",
        "domain.consumer_facing",
        "domain.open_to_public",
        "domain.primary",
        "domain.secondary",
        "infrastructure.cloud_providers",
        "infrastructure.compute_paradigm",
        "infrastructure.data_residency",
        "infrastructure.deployment_model",
        "infrastructure.dr",
        "infrastructure.edge_computing",
        "infrastructure.iac_required",
        "infrastructure.managed_services",
        "infrastructure.multi_region",
        "infrastructure.observability",
        "infrastructure.on_premises_option",
        "integrations.categories",
        "integrations.patterns",
        "integrations.third_party_list",
        "regulatory.ai_governance",
        "regulatory.data_privacy",
        "regulatory.export_control",
        "regulatory.financial",
        "regulatory.frameworks",
        "regulatory.government",
        "regulatory.health",
        "regulatory.safety_critical",
        "regulatory.standards",
        "regulatory.supply_chain",
        "scale.burst_traffic",
        "scale.consistency",
        "scale.latency_sensitive",
        "scale.stateful",
        "scale.throughput",
        "security.asvs_level",
        "security.auth_complexity",
        "security.authz_complexity",
        "security.data_sensitivity",
        "security.external_attack_surface",
        "security.pen_test_required",
        "security.supply_chain_risk",
        "ui.accessibility",
        "ui.design_system",
        "ui.i18n",
        "ui.mobile",
        "ui.multi_tenancy_ux",
        "ui.target_users",
    }
)
GROUP_TYPES = ("system-class", "load-dimension", "named-technology", "failure-class")
ALWAYS_ON = ("a1", "a2", "a3")
BAIL_CAUSES = ("concerns-none-of-the-scope", "source-unreachable", "forbidden-by-terms")
GOLDEN_SIGNALS = ("latency", "traffic", "errors", "saturation")
EVIDENCE_CLASSES = (
    "measured-in-production",
    "rule-governed-benchmark",
    "peer-reviewed-evaluation",
    "independent-verification",
    "vendor-documented-limit",
    "narrative-only",
)
#: The EPISODE's `cause_class`. NOT the map's skipped-row field of the same name: two levels,
#: two vocabularies, disjoint members.
EPISODE_CAUSE_CLASSES = (
    "saturation",
    "skew",
    "coordination",
    "partition",
    "quota",
    "cold-start",
    "fan-out",
    "retry-storm",
)
SKIP_CAUSE_CLASSES = (
    "refused",
    "no-holding-angle",
    "excluded-on-robots",
    "excluded-on-terms",
)
BODY_SECTIONS = (
    "## System under load",
    "## Episodes",
    "## Method and configuration",
    "## Transferability",
)
#: Jepsen's taxonomy, names VERBATIM. A stable name is REUSED, never minted.
CONSISTENCY_MODELS = (
    "strict-serializable",
    "strong-serializable",
    "serializable",
    "snapshot-isolation",
    "repeatable-read",
    "read-committed",
    "read-uncommitted",
    "linearizable",
    "sequential",
    "causal",
    "pram",
    "monotonic-atomic-view",
    "read-your-writes",
    "monotonic-reads",
    "monotonic-writes",
)
PURL = re.compile(r"^pkg:[a-z][a-z0-9.+-]*/")
SPDX = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.+-]*$")


class Findings:
    """Collected findings, and the exit code they imply."""

    def __init__(self) -> None:
        self.items: list[tuple[str, str]] = []

    def fail(self, rule: str, message: str) -> None:
        self.items.append((rule, message))

    def exit_code(self) -> int:
        if not self.items:
            return 0
        # A package fault anywhere makes the run unusable, whatever else was found.
        return 2 if any(r in PACKAGE_FAULT for r, _ in self.items) else 1

    def report(self) -> None:
        for rule, message in self.items:
            print(f"FAIL {rule}: {message}")


def _fail(f: Findings, rule: str, message: str) -> None:
    f.fail(rule, message)


# --------------------------------------------------------------------------- loading


def load_yaml(path: pathlib.Path, f: Findings, rule: str = "input"):
    """Read a YAML file, or record `rule` and return None.

    An INPUT-CLASS fault is an input FILE that cannot be read or parsed. A legitimately omitted
    optional flag is not one.
    """
    try:
        import yaml
    except ModuleNotFoundError:
        _fail(f, "dependency-missing", "pyyaml is not installed")
        return None
    try:
        return yaml.safe_load(path.read_text())
    except FileNotFoundError:
        _fail(f, rule, f"{path} does not exist")
    except Exception as exc:  # noqa: BLE001 — any parse failure is the same class of fault
        _fail(f, rule, f"{path} cannot be parsed: {exc}")
    return None


def load_schema(name: str, f: Findings):
    path = SCHEMA_DIR / f"{name}.schema.json"
    try:
        return json.loads(path.read_text())
    except Exception as exc:  # noqa: BLE001
        _fail(f, "schema-unavailable", f"{path.name} will not load: {exc}")
        return None


def check_schema(doc, name: str, f: Findings) -> None:
    """schema (1) and (2): the artifact validates against ITS OWN schema, which LOADED."""
    schema = load_schema(name, f)
    if schema is None:
        return
    try:
        import jsonschema
    except ModuleNotFoundError:
        _fail(f, "dependency-missing", "jsonschema is not installed")
        return
    validator = jsonschema.Draft202012Validator(schema)
    for err in sorted(validator.iter_errors(doc), key=lambda e: list(e.path)):
        where = "/".join(str(p) for p in err.path) or "(root)"
        _fail(f, "schema", f"{where}: {err.message}")


# --------------------------------------------------------------------------- C3a


def check_registry(reg, f: Findings) -> None:
    """registry integrity (1)-(8) and angle block (1)-(6)."""
    if not isinstance(reg, dict) or "sources" not in reg or "angles" not in reg:
        _fail(
            f,
            "registry-integrity",
            "the registry is not a mapping with `sources` and `angles`",
        )
        return
    rows = reg["sources"]
    by_id = {}
    for row in rows:
        if not isinstance(row, dict) or "id" not in row:
            _fail(f, "registry-integrity", f"malformed row: {row!r}")
            continue
        by_id[row["id"]] = row
        for key in (
            "url",
            "url_kind",
            "access_status",
            "authority_band",
            "as_of",
            "yields",
            "complete_listing",
            "fallback",
            "fallback_rationale",
        ):
            if key not in row:
                _fail(f, "registry-integrity", f"{row['id']}: missing `{key}`")
        if row.get("authority_band") not in (
            "first-party",
            "peer-reviewed",
            "aggregator",
            "community",
            None,
        ):
            _fail(
                f,
                "registry-band",
                f"{row['id']}: unknown band {row.get('authority_band')!r}",
            )
        if row.get("access_status") not in (
            "open",
            "crawl-delayed",
            "rate-limited",
            "paywalled-abstract-only",
            "polite-pool",
            "blocked",
            None,
        ):
            _fail(
                f,
                "registry-access-status",
                f"{row['id']}: {row.get('access_status')!r}",
            )
        if row.get("yields") in (None, "") or "complete_listing" not in row:
            _fail(
                f,
                "registry-yields",
                f"{row['id']}: `yields`/`complete_listing` not declared",
            )
        if not row.get("as_of"):
            _fail(f, "registry-as-of", f"{row['id']}: no `as_of`")
        if row.get("fallback") is None and not row.get("fallback_rationale"):
            _fail(
                f,
                "registry-terminal-rationale",
                f"{row['id']}: terminal with no rationale",
            )
        probe = row.get("probe_method")
        if probe is not None and not (isinstance(probe, dict) and probe.get("method")):
            _fail(
                f,
                "registry-probe-method",
                f"{row['id']}: `probe_method` override is malformed",
            )
    # registry integrity (5) — the forest, WALKED
    for row in rows:
        if not isinstance(row, dict):
            continue
        seen: list[str] = []
        cur = row.get("id")
        while cur is not None:
            if cur in seen:
                _fail(
                    f,
                    "fallback-cycle",
                    f"cycle from {row['id']}: {' -> '.join(seen + [cur])}",
                )
                break
            if cur not in by_id:
                _fail(
                    f,
                    "fallback-unresolvable",
                    f"{row['id']}: fallback {cur!r} resolves to nothing",
                )
                break
            seen.append(cur)
            cur = by_id[cur].get("fallback")
    _check_angles(reg, f)


def _check_angles(reg, f: Findings) -> None:
    owed_sizing = {"a3", "b3", "b7"}
    for angle in reg.get("angles") or []:
        aid = angle.get("id", "?")
        conditional = angle.get("trigger") == "conditional"
        if conditional and not angle.get("predicate"):
            _fail(
                f,
                "angle-predicate-placement",
                f"{aid}: conditional with no `predicate`",
            )
        if not conditional and angle.get("predicate"):
            _fail(
                f,
                "angle-predicate-placement",
                f"{aid}: always-on carrying a `predicate`",
            )
        anchors = angle.get("trigger_anchor") or []
        if conditional and not anchors:
            _fail(
                f,
                "angle-trigger-anchor",
                f"{aid}: conditional with an empty `trigger_anchor`",
            )
        for widener in angle.get("widening_legs") or []:
            root = ".".join(str(widener).split(".")[:2])
            if root not in OPTIONAL_FIELDS:
                _fail(
                    f,
                    "angle-widening-legs",
                    f"{aid}: widener {widener!r} is not an OPTIONAL capability-map field; a "
                    "required leaf would fail closed on every map that omits it",
                )
        seed = angle.get("seed_input")
        if not isinstance(seed, list) or not seed:
            _fail(f, "angle-seed-input", f"{aid}: `seed_input` is not a non-empty LIST")
        else:
            for token in seed:
                if token not in GROUP_TYPES and "." not in str(token):
                    _fail(
                        f,
                        "angle-seed-input",
                        f"{aid}: {token!r} is neither a group-type id nor a capability-map path",
                    )
        if "predicate_omits" not in angle:
            _fail(f, "angle-predicate-omits", f"{aid}: `predicate_omits` absent")
        if ("sizing_record" in angle) != (aid in owed_sizing):
            _fail(f, "angle-sizing-record", f"{aid}: `sizing_record` presence is wrong")


# --------------------------------------------------------------------------- C3b, C3s


def check_band(doc, path: str, f: Findings) -> None:
    """the declared band (1) and (2), on whichever artifact carries it."""
    band = doc
    for part in path.split("."):
        band = (band or {}).get(part) if isinstance(band, dict) else None
    if not band:
        _fail(
            f,
            "declared-band",
            f"no band at `{path}`; lens 1 and lens 4 cannot run without it",
        )
        return
    for leaf in BAND_LEAVES:
        if leaf not in band:
            _fail(f, "declared-band", f"`{path}.{leaf}` absent")


def check_map(doc, reg, f: Findings) -> None:
    """map completeness (1)-(6), the MAP half of sanitization (1), and the declared band."""
    check_band(doc, "meta.classification.scale", f)
    sources = doc.get("sources") or {}
    active = {r.get("id"): r for r in sources.get("active") or []}
    skipped = {r.get("id"): r for r in sources.get("skipped") or []}
    registry_ids = {r["id"] for r in (reg.get("sources") or []) if isinstance(r, dict)}
    both = set(active) & set(skipped)
    if both:
        _fail(f, "map-completeness", f"rows in BOTH active and skipped: {sorted(both)}")
    missing = registry_ids - set(active) - set(skipped)
    if missing:
        _fail(
            f, "map-completeness", f"registry rows in neither array: {sorted(missing)}"
        )
    unknown = (set(active) | set(skipped)) - registry_ids
    if unknown:
        _fail(
            f, "map-completeness", f"rows that are not registry rows: {sorted(unknown)}"
        )
    for rid, row in active.items():
        for key in ("as_of", "access_status", "sanitization"):
            if not row.get(key):
                _fail(f, "map-completeness", f"active row {rid}: no `{key}`")
        posture = row.get("sanitization") or {}
        if posture and not posture.get("status"):
            _fail(f, "sanitization", f"active row {rid}: posture with no `status`")
    for rid, row in skipped.items():
        if row.get("cause_class") not in SKIP_CAUSE_CLASSES:
            _fail(
                f,
                "map-completeness",
                f"skipped row {rid}: `cause_class` {row.get('cause_class')!r}",
            )
        if not row.get("cause"):
            _fail(f, "map-completeness", f"skipped row {rid}: no `cause`")
        if "sanitization" in row:
            _fail(
                f,
                "map-completeness",
                f"skipped row {rid}: carries a `sanitization` posture, which §6 places on ACTIVE "
                "rows only",
            )
    declared = {g.get("type") for g in doc.get("groups") or []}
    guard = doc.get("scope_guard") or {}
    absent = set(guard.get("absent_types") or [])
    excluded = {e.get("item") for e in guard.get("excluded") or []}
    for gtype in GROUP_TYPES:
        if gtype not in declared and gtype not in absent:
            _fail(
                f,
                "map-completeness",
                f"axis {gtype!r} has no group and is not in `absent_types`",
            )
        if gtype in absent and gtype not in excluded:
            _fail(
                f,
                "map-completeness",
                f"axis {gtype!r} is absent with no reason in `excluded`",
            )
    for shared in guard.get("shared_terms") or []:
        if not shared.get("owner"):
            _fail(
                f,
                "map-completeness",
                f"shared term {shared.get('term')!r} names no owner",
            )
    verdicts = {v.get("angle_id"): v for v in doc.get("angle_applicability") or []}
    for aid in [a.get("id") for a in reg.get("angles") or []]:
        if aid not in verdicts:
            _fail(f, "map-completeness", f"no verdict for angle {aid}")
            continue
        verdict = verdicts[aid]
        if not verdict.get("reason"):
            _fail(f, "map-completeness", f"{aid}: verdict with no reason")
        if aid in ALWAYS_ON and verdict.get("holds") is False:
            _fail(
                f,
                "map-completeness",
                f"{aid} is declared `trigger: always` in the registry and the map refuses it; "
                "that contradicts the contract rather than describing the project",
            )
        if verdict.get("holds") is False and not re.search(
            r"[a-z_]+\.[a-z_]+", verdict.get("reason", "")
        ):
            _fail(
                f, "map-completeness", f"{aid}: `holds: false` names no DECIDING value"
            )


def check_cell_sanitization(doc, f: Findings) -> None:
    """sanitization (1) cell half, (3) and (4). The subject is the CELL, never the map row."""
    for cell in doc.get("coverage") or []:
        key = f"{cell.get('group_id')}/{cell.get('source_id')}"
        if cell.get("status") != "reached":
            continue
        posture = cell.get("sanitization")
        if not posture:
            _fail(f, "sanitization", f"{key}: reached cell records no `sanitization`")
            continue
        status = posture.get("status")
        if status == "modified" and not posture.get("cause"):
            _fail(f, "sanitization", f"{key}: `modified` with no `cause`")
        if status == "not-fetched":
            _fail(
                f,
                "sanitization",
                f"{key}: a REACHED cell's own status is `not-fetched`. The subject is the CELL, "
                "not the map row it cites",
            )


# --------------------------------------------------------------------------- C3c


def check_search(doc, reg, kmap, f: Findings) -> None:
    """coverage grid (1)(2)(4), admission (1)-(3) and bound (1)-(3)."""
    if doc.get("outcome") == "not_run":
        return
    angle_id = (doc.get("meta") or {}).get("angle_id")
    angle = next((a for a in reg.get("angles") or [] if a.get("id") == angle_id), None)
    if angle is None:
        _fail(f, "coverage-grid", f"angle {angle_id!r} is not a registry angle")
        return
    cells = doc.get("coverage") or []
    seen = {(c.get("group_id"), c.get("source_id")) for c in cells}
    if kmap:
        verdict = next(
            (
                v
                for v in kmap.get("angle_applicability") or []
                if v.get("angle_id") == angle_id
            ),
            {},
        )
        applicable = set(verdict.get("applicable_group_types") or [])
        # THREE terms: the map's groups OF THIS ANGLE'S APPLICABLE TYPES, crossed with THIS
        # ANGLE'S OWN sources INTERSECTED with the map's ACTIVE sources. Dropping any one is
        # wrong in a measurable way.
        groups = [
            g["id"] for g in kmap.get("groups") or [] if g.get("type") in applicable
        ]
        active = {
            r.get("id") for r in ((kmap.get("sources") or {}).get("active") or [])
        }
        sources = [s for s in angle.get("sources") or [] if s in active]
        owed = {(g, s) for g in groups for s in sources}
        for missing in sorted(owed - seen):
            _fail(f, "coverage-grid", f"owed cell {missing[0]}/{missing[1]} is absent")
        for extra in sorted(seen - owed):
            _fail(
                f,
                "coverage-grid",
                f"cell {extra[0]}/{extra[1]} is not owed by the three terms",
            )
    for cell in cells:
        key = f"{cell.get('group_id')}/{cell.get('source_id')}"
        reached = cell.get("status") == "reached"
        if reached:
            for field in ("returned", "kept"):
                if cell.get(field) is None:
                    _fail(
                        f, "coverage-grid", f"{key}: reached and records no `{field}`"
                    )
            if cell.get("returned") and not cell.get("count_frame"):
                _fail(
                    f,
                    "coverage-grid",
                    f"{key}: non-zero `returned` with no `count_frame`; a count is "
                    "unre-derivable without knowing what was counted",
                )
        else:
            if not cell.get("cause"):
                _fail(
                    f,
                    "coverage-grid",
                    f"{key}: not reached and records no observable `cause`",
                )
            if cell.get("returned") is not None or cell.get("kept") is not None:
                _fail(
                    f,
                    "coverage-grid",
                    f"{key}: not reached and records a count. A zero and an absence are "
                    "different claims and the grid must keep them apart",
                )
    _check_admission(doc, cells, f)
    _check_bound(doc, angle, f)


def _check_admission(doc, cells, f: Findings) -> None:
    for cand in doc.get("candidates") or []:
        item = cand.get("item_id", "?")
        if not cand.get("url"):
            _fail(
                f,
                "admission",
                f"{item}: admitted with no resolvable URL (L-7 conjunct 1)",
            )
        if not cand.get("stated_date"):
            _fail(
                f,
                "admission",
                f"{item}: admitted with no stated version or date (L-7 conjunct 2)",
            )
        if not cand.get("found_by"):
            _fail(f, "admission", f"{item}: candidate with no `found_by`")
    for row in doc.get("unadmitted") or []:
        item = row.get("item_id", "?")
        if not row.get("found_by"):
            _fail(f, "admission", f"{item}: unadmitted row with no `found_by`")
        if not row.get("reason"):
            _fail(f, "admission", f"{item}: unadmitted row with no reason")
    # admission (3): `kept` == |candidates CITING THE CELL| + |unadmitted CITING THE CELL|.
    # Both qualifiers: without `found_by` on candidates the first term is not computable.
    for cell in cells:
        if cell.get("status") != "reached":
            continue
        key = f"{cell.get('group_id')}/{cell.get('source_id')}"
        cited = sum(1 for c in doc.get("candidates") or [] if c.get("found_by") == key)
        cited += sum(1 for u in doc.get("unadmitted") or [] if u.get("found_by") == key)
        if cell.get("kept") != cited:
            _fail(
                f,
                "admission",
                f"{key}: `kept` is {cell.get('kept')} and {cited} rows cite the cell",
            )


def _check_bound(doc, angle, f: Findings) -> None:
    bound = doc.get("bound") or {}
    if bound.get("cap") != angle.get("cap"):
        _fail(
            f,
            "bound",
            f"`bound.cap` is {bound.get('cap')!r} and the registry declares {angle.get('cap')!r}. "
            "The cap is transcribed VERBATIM; an author does not widen their own cap",
        )
    if bound.get("hit"):
        note = bound.get("dropped_note") or ""
        if not note:
            _fail(f, "bound", "`hit: true` owes a `dropped_note`")
        elif not re.search(r"\d", note):
            _fail(
                f,
                "bound",
                "`dropped_note` names no ordering position and no first row that fell off; "
                '"the rest were dropped" is not re-appliable',
            )
    if bound.get("ordering") and bound["ordering"] != angle.get("ordering_signal"):
        if not bound.get("ordering_deviation"):
            _fail(
                f,
                "bound",
                "`ordering` deviates from the registry with no `ordering_deviation`",
            )


# --------------------------------------------------------------------------- C3d


def check_ordering_appliable(reg, f: Findings) -> None:
    """bound (4) NOT-A-RULE — over ALL TEN angles, never the subset that already satisfies it."""
    by_id = {r["id"]: r for r in (reg.get("sources") or []) if isinstance(r, dict)}
    for angle in reg.get("angles") or []:
        aid = angle.get("id", "?")
        signal = (angle.get("ordering_signal") or "").strip()
        if not signal:
            _fail(f, "ordering-appliable", f"{aid}: no `ordering_signal`")
            continue
        if "," not in signal and " then " not in signal.lower():
            _fail(
                f,
                "ordering-appliable",
                f"{aid}: the signal states no TIE-BREAK, so it is not total over the axes it walks",
            )
        walked = [s for s in angle.get("sources") or [] if s in by_id]
        if not walked:
            _fail(f, "ordering-appliable", f"{aid}: walks no registry source")
        if not re.search(r"every|all|each|both", signal, re.I):
            _fail(
                f,
                "ordering-appliable",
                f"{aid}: the signal does not say it is appliable across every source the angle "
                "walks; a signal only one source can compute is not an ordering",
            )


# --------------------------------------------------------------------------- C3e, C3w, C3x, C3r, C3p


def check_extract(doc, f: Findings) -> None:
    """vocabularies (1)-(7), bail (1)-(3), body sections, transferability, measured_* coherence."""
    if doc.get("outcome") == "skipped":
        bail = doc.get("skipped") or {}
        if set(bail) - {"cause", "detail"}:
            _fail(
                f,
                "bail",
                f"`skipped` carries {sorted(set(bail) - {'cause', 'detail'})}",
            )
        if bail.get("cause") not in BAIL_CAUSES:
            _fail(f, "bail", f"cause {bail.get('cause')!r} is not one of the three")
        if bail.get("cause") == "no-stated-load":
            _fail(
                f,
                "bail",
                "`no-stated-load` is REFUSED as a cause: it would delete the operational canon "
                "and every negative result, which is a promotion cut wearing a bail's clothes",
            )
        return
    source = doc.get("source") or {}
    lic = source.get("license")
    if lic is not None and lic != "unverified" and not SPDX.match(str(lic)):
        _fail(
            f,
            "vocabularies",
            f"`license` {lic!r} is neither an SPDX id, `unverified` nor null",
        )
    if source.get("access_status") not in (
        "open",
        "crawl-delayed",
        "rate-limited",
        "paywalled-abstract-only",
        "blocked",
    ):
        _fail(
            f, "vocabularies", f"source `access_status` {source.get('access_status')!r}"
        )
    for ep in doc.get("episodes") or []:
        eid = ep.get("id", "?")
        if ep.get("signal") not in GOLDEN_SIGNALS:
            _fail(f, "vocabularies", f"{eid}: `signal` {ep.get('signal')!r}")
        for leaf, value in (ep.get("load_class") or {}).items():
            if leaf not in BAND_LEAVES:
                _fail(
                    f, "vocabularies", f"{eid}: `load_class.{leaf}` is not a band leaf"
                )
        cm = ep.get("consistency_model")
        if cm is not None and cm not in CONSISTENCY_MODELS:
            _fail(
                f,
                "vocabularies",
                f"{eid}: `consistency_model` {cm!r} is not Jepsen's, verbatim",
            )
        tech = ep.get("technology")
        if tech is not None and not PURL.match(str(tech)):
            _fail(f, "vocabularies", f"{eid}: `technology` {tech!r} is not a purl")
        if ep.get("evidence_class") not in EVIDENCE_CLASSES:
            _fail(
                f,
                "vocabularies",
                f"{eid}: `evidence_class` {ep.get('evidence_class')!r}",
            )
        cc = ep.get("cause_class")
        if cc is not None and cc not in EPISODE_CAUSE_CLASSES:
            _fail(
                f,
                "vocabularies",
                f"{eid}: `cause_class` {cc!r} is not in the EPISODE's nine-member vocabulary, "
                "which is disjoint from the map's field of the same name",
            )
        if not ep.get("pattern"):
            _fail(f, "vocabularies", f"{eid}: no `pattern`")
        if ep.get("primary_dimension") not in BAND_LEAVES:
            _fail(
                f,
                "primary-dimension",
                f"{eid}: `primary_dimension` {ep.get('primary_dimension')!r}",
            )
        _check_transferability(ep, eid, f)
        _check_measured(ep, eid, f)


def _check_transferability(ep, eid: str, f: Findings) -> None:
    t = ep.get("transferability")
    if not t:
        _fail(f, "transferability", f"{eid}: no `transferability`")
        return
    if t.get("level") not in ("high", "moderate", "low"):
        _fail(f, "transferability", f"{eid}: level {t.get('level')!r}")
    if len(str(t.get("reason") or "")) < 20:
        _fail(f, "transferability", f"{eid}: reason is under 20 characters")


def _check_measured(ep, eid: str, f: Findings) -> None:
    """measured_* coherence (1): all three travel together or none does."""
    mag, val, unit = (
        ep.get("measured_magnitude"),
        ep.get("measured_value"),
        ep.get("measured_unit"),
    )
    if mag is not None:
        if val is None:
            _fail(
                f,
                "measured-coherence",
                f"{eid}: `measured_magnitude` with no `measured_value`",
            )
        if unit is None:
            _fail(
                f,
                "measured-coherence",
                f"{eid}: `measured_magnitude` with no `measured_unit`",
            )


def check_body_sections(text: str, f: Findings) -> None:
    """body sections (1) presence and (2) non-triviality. Never prose quality."""
    for heading in BODY_SECTIONS:
        if heading not in text:
            _fail(f, "body-sections", f"the record has no `{heading}` section")
            continue
        after = text.split(heading, 1)[1]
        body = after.split("\n## ", 1)[0].strip()
        if len(body) < 40:
            _fail(
                f,
                "body-sections",
                f"`{heading}` is present but trivial ({len(body)} chars)",
            )


# --------------------------------------------------------------------------- C3i


def check_synthesis(doc, extracts, f: Findings) -> None:
    """synthesis (1)-(3), and the delta-mode `lineage` rule that READS the schema's half."""
    check_band(doc, "project_band", f)
    known = set()
    for record in extracts or []:
        for ep in record.get("episodes") or []:
            if ep.get("id"):
                known.add(ep["id"])
    order = {"very-low": 0, "low": 1, "moderate": 2, "high": 3}
    for area in doc.get("areas") or []:
        name = area.get("area", "?")
        evidence = area.get("evidence") or []
        if not evidence:
            _fail(f, "synthesis", f"{name}: `evidence[]` is empty")
        for eid in evidence:
            if extracts is not None and eid not in known:
                _fail(
                    f,
                    "synthesis",
                    f"{name}: evidence {eid!r} resolves to no extracted episode",
                )
        if extracts is not None and evidence and all(e in known for e in evidence):
            backing = [
                ep.get("confidence")
                for record in extracts
                for ep in record.get("episodes") or []
                if ep.get("id") in evidence
            ]
            if backing:
                weakest = min(backing, key=lambda c: order.get(c, 0))
                if area.get("confidence") != weakest:
                    _fail(
                        f,
                        "synthesis",
                        f"{name}: `confidence` is {area.get('confidence')!r} and the WEAKEST "
                        f"backing class is {weakest!r}; it is re-derived, never averaged",
                    )
        trigger = area.get("migration_trigger")
        if trigger and not (trigger.get("evidence") or []):
            _fail(f, "synthesis", f"{name}: `migration_trigger` carries no evidence")
        for mode in area.get("failure_modes") or []:
            if not (mode.get("evidence") or []):
                _fail(
                    f,
                    "synthesis",
                    f"{name}: a `failure_modes` entry carries no evidence",
                )
    lineage = doc.get("lineage") or {}
    if doc.get("mode") == "delta" and not lineage.get("extends"):
        _fail(f, "delta-lineage", "mode is `delta` and `lineage.extends` is null")


# --------------------------------------------------------------------------- C3g


#: NON-ORDINAL, so there is no adjacent pair for a boundary to sit between. Skipped by
#: CONSTRUCTION, which is a different mechanism from the discovered-unsourced list below and is
#: kept apart from it deliberately.
NON_ORDINAL = ("geo_distribution",)
#: The availability enum members ARE the boundaries — numeric literals, ascending.
AVAILABILITY_BANDS = ("99", "99.9", "99.95", "99.99", "99.999")


def unsourced_dimensions(f: Findings | None = None) -> frozenset[str]:
    """The dimensions the re-derivation SKIPS, read from `load-band-thresholds.md`.

    DERIVED from the file C4a wrote, never hand-copied here: a skip set restated beside the file
    it came from drifts from it, and a dimension discovered to be unsourced would then leave the
    validator unable to tell a correct episode from a wrong one.
    """
    try:
        import yaml
    except ModuleNotFoundError:
        if f is not None:
            _fail(f, "dependency-missing", "pyyaml is not installed")
        return frozenset()
    try:
        block = re.search(r"```yaml\n(.*?)```", THRESHOLDS_PATH.read_text(), re.S)
        data = yaml.safe_load(block.group(1)) if block else {}
    except Exception as exc:  # noqa: BLE001
        if f is not None:
            _fail(f, "thresholds-unreadable", f"{THRESHOLDS_PATH.name}: {exc}")
        return frozenset()
    return frozenset(
        entry["dimension"]
        for entry in (data.get("unsourced_dimensions") or [])
        if entry.get("dimension")
    )


def _availability_band(magnitude: float) -> str | None:
    """The band a measured availability percentage meets and does not exceed."""
    met = [b for b in AVAILABILITY_BANDS if magnitude >= float(b)]
    return met[-1] if met else None


def check_load_band(doc, f: Findings) -> None:
    """derived load_class (1) and (2): the band RE-DERIVED, and a band with no number REFUSED."""
    skip = unsourced_dimensions(f)
    for ep in doc.get("episodes") or []:
        eid = ep.get("id", "?")
        dimension = ep.get("primary_dimension")
        if dimension in NON_ORDINAL or dimension in skip:
            continue
        band = (ep.get("load_class") or {}).get(dimension)
        magnitude = ep.get("measured_magnitude")
        if magnitude is None:
            if band is not None:
                _fail(
                    f,
                    "derived-load-class",
                    f"{eid}: `load_class.{dimension}` is {band!r} with no `measured_magnitude` "
                    "behind it. A band asserted with no number is refused",
                )
            continue
        if dimension == "availability_target":
            derived = _availability_band(float(magnitude))
            if derived is not None and band != derived:
                _fail(
                    f,
                    "derived-load-class",
                    f"{eid}: `load_class.availability_target` is {band!r} and {magnitude} "
                    f"derives {derived!r}. A band that disagrees with the number it was computed "
                    "from is a hard failure, not an opinion",
                )


# --------------------------------------------------------------------------- C3n


def check_dimension_orders(f: Findings) -> None:
    """Every ORDERED dimension carries its order and `geo_distribution` carries NONE.

    Over the WHOLE rule set, not the subset that already avoids the field: a guard authored over
    a partial population passes vacuously.
    """
    skip = unsourced_dimensions(f)
    ordered = [d for d in BAND_LEAVES if d not in NON_ORDINAL]
    for dimension in ordered:
        if dimension in skip:
            continue
        if dimension == "availability_target" and not AVAILABILITY_BANDS:
            _fail(f, "dimension-order", f"{dimension} is ordered and carries no order")
    for dimension in NON_ORDINAL:
        if dimension in skip:
            _fail(
                f,
                "dimension-order",
                f"{dimension} is NON-ORDINAL and appears in the DISCOVERED-unsourced list. It is "
                "skipped by CONSTRUCTION, and collapsing the two mechanisms is what makes a "
                "later discovery invisible",
            )
    # primary_dimension (2) NOT-A-RULE: NO rule maps `signal` to a dimension. The validator was
    # stopped at presence-and-enum deliberately, and a mapping added later would silently make a
    # reviewer duty deterministic on an invention.
    #
    # The needle is BUILT, never written whole: spelled out here it is an occurrence of itself,
    # and the first version of this check failed on its own source.
    needle = "SIGNAL" + "_TO_DIMENSION"
    source = pathlib.Path(__file__).read_text()
    if needle.lower() in source.lower().replace(needle.lower(), "", 1):
        _fail(
            f,
            "dimension-order",
            "a rule maps `signal` to a dimension. No such mapping exists upstream, in this spec "
            "or in any owed deliverable, so a rule keying on one would be deterministic on an "
            "invention",
        )


# --------------------------------------------------------------------------- C3j


#: Part (b) of #42: an id already ending in a hashed stem cannot take the identity branch.
HASHED_STEM = re.compile(r"--[0-9a-f]{12}$")
PREFIX_CAP = 80
EPISODE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*#e[1-9][0-9]*$")
ID_PREFIX = re.compile(r"^(DOI-|ARXIV-|WEB-)")


def record_filename(item_id: str) -> str:
    """The filename stem a record for `item_id` must be written under.

    BOTH parts of playbook #42, mirroring 5c's shipped copy and never 5e's, which has part (a)
    only and genuinely collides.

    (a) Sanitize to `[A-Za-z0-9._-]`, cap the prefix, and append a 12-hex digest OF THE WHOLE
        ID — so two ids differing only in characters the sanitizer collapses still get
        different names.
    (b) The identity branch REFUSES an id that already ends in a hashed stem, so `f(f(x))`
        cannot equal `f(x)` for an `x` the sanitizer touched.

    This type is in the MOST-exposed class: a DOI always contains `/` and a `WEB-` id carries
    dots and may carry `/`. An id written verbatim lands the record in a directory nothing
    looks in, stays perfectly valid, and is treated as never written — and because the extract
    cursor is disk-authoritative, the orphaned row is re-spawned on every wake looking correct.

    Args:
        item_id: The record's canonical identity, verbatim.

    Returns:
        The filename stem, without extension.
    """
    if re.fullmatch(r"[A-Za-z0-9._-]+", item_id) and not HASHED_STEM.search(item_id):
        return item_id
    prefix = re.sub(r"[^A-Za-z0-9._-]+", "-", item_id)[:PREFIX_CAP].strip("-")
    digest = hashlib.sha256(item_id.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}--{digest}" if prefix else f"--{digest}"


def check_ids(doc, f: Findings) -> None:
    """id grammar (1)-(3), and `record_filename` parity."""
    meta = doc.get("meta") or {}
    sid = str(meta.get("source_id") or "")
    id_class = meta.get("id_class")
    if id_class not in ("DOI", "ARXIV", "WEB"):
        _fail(
            f, "id-grammar", f"`id_class` {id_class!r} is not one of the three prefixes"
        )
    for ep in doc.get("episodes") or []:
        eid = str(ep.get("id") or "")
        if not EPISODE_ID.match(eid):
            _fail(f, "id-grammar", f"episode id {eid!r} is not `<source-id>#e<N>`")
            continue
        if "/" in eid or "\\" in eid:
            _fail(f, "id-grammar", f"episode id {eid!r} could be read as a path")
        if not eid.startswith(f"{sid}#e"):
            _fail(f, "id-grammar", f"episode id {eid!r} does not root on `{sid}`")
    # The CROSS-BRANCH property, not a round-trip: a within-branch round-trip passes while the
    # collision exists, which is exactly the false assurance #42 records.
    name = record_filename(sid)
    if HASHED_STEM.search(sid) and record_filename(name) == name:
        _fail(
            f,
            "record-filename",
            f"{sid!r} already ends in a hashed stem and took the identity branch, so f(f(x)) "
            "== f(x) for an id the sanitizer touched",
        )


# --------------------------------------------------------------------------- C3k


def check_score(doc, f: Findings) -> None:
    """The quality filter's `score`: PRESENT and in range. Ranking only, never a cut."""
    source = doc.get("source") or {}
    score = source.get("score")
    if score is None:
        _fail(f, "quality-filter", "the source record carries no `score`")
        return
    if not isinstance(score, int) or isinstance(score, bool) or not 0 <= score <= 10:
        _fail(f, "quality-filter", f"`score` {score!r} is not an integer 0-10")


# --------------------------------------------------------------------------- the CLI


def _read_extracts(directory, f: Findings):
    if directory is None:
        return None
    path = pathlib.Path(directory)
    if not path.is_dir():
        _fail(f, "input", f"{path} is not a directory")
        return None
    out = []
    for child in sorted(path.glob("*.yaml")):
        doc = load_yaml(child, f)
        if doc is not None:
            out.append(doc)
    return out


def build_parser() -> argparse.ArgumentParser:
    """Four subcommands, with the signatures spec §4 states.

    Only `search` takes `--keyword-map`; only `synthesis` takes `--extracts` and `--queue`;
    `extract` takes a bare file. A missing `--extracts` is exit 1, not exit 2 — the artifact's
    author can supply it.
    """
    parser = argparse.ArgumentParser(prog="validate_scale_prior_art.py")
    sub = parser.add_subparsers(dest="kind", required=True)

    p = sub.add_parser("keyword-map")
    p.add_argument("artifact")

    p = sub.add_parser("search")
    p.add_argument("artifact")
    p.add_argument("--keyword-map", required=True)

    p = sub.add_parser("extract")
    p.add_argument("artifact")

    p = sub.add_parser("synthesis")
    p.add_argument("artifact")
    p.add_argument("--extracts")
    p.add_argument("--queue")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    f = Findings()
    reg = load_yaml(REGISTRY_PATH, f, rule="registry-unreadable")
    if reg is None:
        f.report()
        return f.exit_code()
    check_registry(reg, f)
    check_ordering_appliable(reg, f)

    path = pathlib.Path(args.artifact)
    doc = load_yaml(path, f)
    if doc is None:
        f.report()
        return f.exit_code()

    if args.kind == "keyword-map":
        check_schema(doc, "scale-vocabulary-map", f)
        check_map(doc, reg, f)
    elif args.kind == "search":
        check_schema(doc, "search-output", f)
        kmap = load_yaml(pathlib.Path(args.keyword_map), f)
        check_cell_sanitization(doc, f)
        check_search(doc, reg, kmap, f)
    elif args.kind == "extract":
        check_schema(doc, "extract-output", f)
        check_extract(doc, f)
        check_load_band(doc, f)
        check_dimension_orders(f)
        check_ids(doc, f)
        if doc.get("outcome") != "skipped":
            check_score(doc, f)
        body = path.with_suffix(".md")
        if body.exists():
            check_body_sections(body.read_text(), f)
    elif args.kind == "synthesis":
        check_schema(doc, "scale-envelope-index", f)
        if args.extracts is None:
            _fail(
                f,
                "extracts-crosscheck-skipped",
                "no `--extracts`, so evidence resolution was NOT checked. This is exit 1: the "
                "artifact's author can supply the flag",
            )
            print("SKIP extracts-crosscheck")
        extracts = _read_extracts(args.extracts, f)
        check_synthesis(doc, extracts, f)

    f.report()
    return f.exit_code()


if __name__ == "__main__":
    sys.exit(main())
