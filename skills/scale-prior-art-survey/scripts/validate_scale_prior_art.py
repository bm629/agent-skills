#!/usr/bin/env python
"""Deterministic gate for the scale prior-art survey's four artifact kinds.

Exit contract, inherited unchanged because the caller reads exit codes and cannot read prose:

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

#: Rules only a PACKAGE author can cause. They exit 2; everything else exits 1. Matched by
#: PREFIX because the ids are per-CLAUSE — a `registry-integrity-2` is the same class of fault as
#: a `registry-integrity-1`, and a set listing them one by one would have to grow with every
#: clause. The exit-contract sweep derives every id from this module's AST and asserts each one
#: against the four-class table, so the two sides cannot drift.
#:
#: An earlier revision carried this stanza TWICE, the first copy saying the set is "derived from
#: this module's own AST, never hand-listed" — which the tuple below plainly is not — and the
#: second naming `registry-integrity-5a`, an id this validator does not emit.
PACKAGE_FAULT_PREFIXES = (
    "registry-",
    "angle-block-",
    "fallback-",
    "schema-unavailable",
    "dependency-missing",
    "input",
    "thresholds-unreadable",
    "package-crash",
    "queue-unreadable",
)


def is_package_fault(rule: str) -> bool:
    """Whether `rule` is a fault an artifact author CANNOT repair.

    `schema` is deliberately NOT one: an artifact failing a schema that LOADED is exactly what
    its author repairs. `schema-unavailable` is, because an unloadable schema FILE is ours.
    """
    return rule.startswith(PACKAGE_FAULT_PREFIXES)


def _report_and_exit(f: Findings) -> int:
    """Report, then exit. Called from BOTH crash handlers as well as the normal path, so a
    crash cannot discard the findings already collected.

    Any exception between the first check and the report used to leave stdout EMPTY and the
    interpreter exiting 1 — the code that means "the artifact has findings, its author can repair
    them" — while a correct `schema` finding had already been recorded and was thrown away.
    """
    f.report()
    return f.exit_code()


#: The map's five band leaves, NAMED rather than counted — the declared-band family reads them.
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
#: Every OPTIONAL capability-map field, not only the scale ones. The rule is "naming only
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
        return 2 if any(is_package_fault(r) for r, _ in self.items) else 1

    def report(self) -> None:
        for rule, message in self.items:
            print(f"FAIL {rule}: {message}")


def _fail(rule: str, message: str, f: Findings) -> None:
    """Record a finding.

    The rule id is the FIRST argument. Eight of the nine shipped validators put it there, and the
    cross-repo rule-owner walk reads `args[0]` — ordering it second made that walk return zero
    ids against a floor of seventy.
    """
    f.fail(rule, message)


# --------------------------------------------------------------------------- loading


def load_yaml(
    path: pathlib.Path, f: Findings, rule: str, empty_rule: str | None = None
):
    """Read a YAML file, or record `rule` and return None.

    An INPUT-CLASS fault is an input FILE that cannot be read or parsed, and its id is `input`. A
    legitimately omitted optional flag is not one. A PACKAGE file passes its own id instead —
    `registry-unreadable` for the registry, `thresholds-unreadable` for the threshold table — so
    the finding that carries the parse error is also the finding filed under the right rule.

    `rule` has no DEFAULT, deliberately. As a default it was a fourth id shape — invisible to a
    positional AST walk and to the shared cross-package rule-count guard, which read 103 where
    the validator emits 104. Every call names its rule.
    """
    try:
        import yaml
    except ModuleNotFoundError:
        _fail("dependency-missing", "pyyaml is not installed", f)
        return None
    try:
        doc = yaml.safe_load(path.read_text())
    except FileNotFoundError:
        _fail(rule, f"{path} does not exist", f)
        return None
    except Exception as exc:  # noqa: BLE001 — any parse failure is the same class of fault
        _fail(rule, f"{path} cannot be parsed: {exc}", f)
        return None
    if doc is None:
        # An empty or comments-only file PARSES, to None. Returning it unremarked made the gate
        # exit 0 on a zero-byte artifact: a producer that wrote nothing passed.
        #
        # `empty_rule` because the CLASS differs from the read failures above it, and because
        # it differs PER FILE. The class turns on who can repair the fault, and this validator
        # reads four kinds of file: the ARTIFACT, which the running agent wrote and can rewrite;
        # the keyword map and the extract records, which SIBLING agents wrote in earlier waves;
        # and the package's own registry, schemas and threshold table. Only the first is exit 1.
        # An empty keyword map is not this agent's to fix — the dispatcher must re-run wave 0 —
        # so it stays exit 2, and the asymmetry is deliberate rather than an oversight. A file that
        # could not be read or parsed is `input`, exit 2. An empty ARTIFACT was read and did
        # parse — it is content the author can repair, which is the same reasoning that moved a
        # top-level non-mapping to exit 1, and it is where all four shipped siblings put it. The
        # default keeps the package files (`registry-unreadable`, `thresholds-unreadable`) where
        # they are. It is `None`, not a string, so it adds no id shape to the AST walk.
        _fail(empty_rule or rule, f"{path} is empty, or carries only comments", f)
        return None
    return doc


def load_schema(name: str, f: Findings):
    path = SCHEMA_DIR / f"{name}.schema.json"
    try:
        return json.loads(path.read_text())
    except Exception as exc:  # noqa: BLE001
        _fail("schema-unavailable", f"{path.name} will not load: {exc}", f)
        return None


def check_schema(doc, name: str, f: Findings) -> None:
    """schema (1) and (2): the artifact validates against ITS OWN schema, which LOADED."""
    schema = load_schema(name, f)
    if schema is None:
        return
    try:
        import jsonschema
    except ModuleNotFoundError:
        _fail("dependency-missing", "jsonschema is not installed", f)
        return
    try:
        validator = jsonschema.Draft202012Validator(schema)
        errors = sorted(validator.iter_errors(doc), key=lambda e: list(e.path))
    except Exception as exc:  # noqa: BLE001
        # A schema that JSON-LOADS and is not a schema — one typo'd `"type": "strng"` — slipped
        # past `schema-unavailable`, which only guards the load, and crashed inside the artifact
        # walk where it was filed as the author's fault.
        _fail(
            "schema-unavailable",
            f"{name}.schema.json loaded but is not a valid schema: "
            f"{type(exc).__name__}: {exc}",
            f,
        )
        return
    for err in errors:
        where = "/".join(str(p) for p in err.path) or "(root)"
        _fail("schema", f"{where}: {err.message}", f)


# ------------------------------------------- registry integrity and the angle blocks


def check_registry(reg, f: Findings) -> None:
    """registry integrity (1)-(8) and angle block (1)-(6)."""
    if not isinstance(reg, dict) or "sources" not in reg or "angles" not in reg:
        _fail(
            "registry-integrity-1",
            "the registry is not a mapping with `sources` and `angles`",
            f,
        )
        return
    rows = reg.get("sources")
    if not isinstance(rows, list):
        _fail(
            "registry-integrity-1", f"`sources` is {type(rows).__name__}, not a list", f
        )
        return
    if not isinstance(reg.get("angles"), list):
        _fail(
            "registry-integrity-1",
            f"`angles` is {type(reg.get('angles')).__name__}, not a list",
            f,
        )
        return
    by_id = {}
    for row in rows:
        if not isinstance(row, dict) or "id" not in row:
            _fail("registry-integrity-1", f"malformed row: {row!r}", f)
            continue
        if not isinstance(row["id"], str):
            _fail(
                "registry-integrity-1",
                f"a row id is {type(row['id']).__name__}, not a string",
                f,
            )
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
                _fail("registry-integrity-1", f"{row['id']}: missing `{key}`", f)
        if row.get("authority_band") not in (
            "first-party",
            "peer-reviewed",
            "aggregator",
            "community",
            None,
        ):
            _fail(
                "registry-integrity-2",
                f"{row['id']}: unknown band {row.get('authority_band')!r}",
                f,
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
                "registry-integrity-3", f"{row['id']}: {row.get('access_status')!r}", f
            )
        if row.get("yields") in (None, "") or "complete_listing" not in row:
            _fail(
                "registry-integrity-4",
                f"{row['id']}: `yields`/`complete_listing` not declared",
                f,
            )
        if not row.get("as_of"):
            _fail("registry-integrity-8", f"{row['id']}: no `as_of`", f)
        if row.get("fallback") is None and not row.get("fallback_rationale"):
            _fail("registry-integrity-6", f"{row['id']}: terminal with no rationale", f)
        probe = row.get("probe_method")
        if probe is not None and not (isinstance(probe, dict) and probe.get("method")):
            _fail(
                "registry-integrity-7",
                f"{row['id']}: `probe_method` override is malformed",
                f,
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
                    "fallback-cycle",
                    f"cycle from {row['id']}: {' -> '.join(seen + [cur])}",
                    f,
                )
                break
            if cur not in by_id:
                _fail(
                    "fallback-unresolvable",
                    f"{row['id']}: fallback {cur!r} resolves to nothing",
                    f,
                )
                break
            seen.append(cur)
            cur = by_id[cur].get("fallback")
    _check_angles(reg, f)


def _check_angles(reg, f: Findings) -> None:
    owed_sizing = {"a3", "b3", "b7"}
    for angle in reg.get("angles") or []:
        if not isinstance(angle, dict):
            _fail(
                "angle-block-1",
                f"an angle block is {type(angle).__name__}, not a mapping",
                f,
            )
            continue
        aid = angle.get("id", "?")
        conditional = angle.get("trigger") == "conditional"
        if conditional and not angle.get("predicate"):
            _fail("angle-block-1a", f"{aid}: conditional with no `predicate`", f)
        if not conditional and angle.get("predicate"):
            _fail("angle-block-1b", f"{aid}: always-on carrying a `predicate`", f)
        anchors = angle.get("trigger_anchor") or []
        if conditional and not anchors:
            _fail(
                "angle-block-2", f"{aid}: conditional with an empty `trigger_anchor`", f
            )
        for widener in angle.get("widening_legs") or []:
            root = ".".join(str(widener).split(".")[:2])
            if root not in OPTIONAL_FIELDS:
                _fail(
                    "angle-block-3",
                    f"{aid}: widener {widener!r} is not an OPTIONAL capability-map field; a "
                    "required leaf would fail closed on every map that omits it",
                    f,
                )
        seed = angle.get("seed_input")
        if not isinstance(seed, list) or not seed:
            _fail("angle-block-4a", f"{aid}: `seed_input` is not a non-empty LIST", f)
        else:
            for token in seed:
                if token not in GROUP_TYPES and "." not in str(token):
                    _fail(
                        "angle-block-4b",
                        f"{aid}: {token!r} is neither a group-type id nor a capability-map path",
                        f,
                    )
        if "predicate_omits" not in angle:
            _fail("angle-block-5", f"{aid}: `predicate_omits` absent", f)
        if ("sizing_record" in angle) != (aid in owed_sizing):
            _fail("angle-block-6", f"{aid}: `sizing_record` presence is wrong", f)


# -------------------------------------------------- the map rules and sanitization


def check_band(doc, path: str, f: Findings) -> None:
    """the declared band (1) and (2), on whichever artifact carries it."""
    band = doc
    for part in path.split("."):
        band = (band or {}).get(part) if isinstance(band, dict) else None
    if not band:
        _fail(
            "declared-band-2",
            f"no band at `{path}`; lens 1 and lens 4 cannot run without it",
            f,
        )
        return
    for leaf in BAND_LEAVES:
        if leaf not in band:
            _fail("declared-band-1", f"`{path}.{leaf}` absent", f)


def check_map(doc, reg, f: Findings) -> None:
    """map completeness (1)-(6), the MAP half of sanitization (1), and the declared band."""
    check_band(doc, "meta.classification.scale", f)
    sources = doc.get("sources") or {}
    active_rows = sources.get("active") or []
    skipped_rows = sources.get("skipped") or []
    for label, rows_ in (("active", active_rows), ("skipped", skipped_rows)):
        seen_ids = [r.get("id") for r in rows_ if isinstance(r, dict)]
        dupes = sorted({i for i in seen_ids if seen_ids.count(i) > 1})
        if dupes:
            # A second entry for one id SHADOWS the first, so a defective row hides behind a
            # correct one while the set arithmetic still balances.
            _fail(
                "map-completeness-1a", f"duplicate ids in `sources.{label}`: {dupes}", f
            )
    active = {r.get("id"): r for r in active_rows if isinstance(r, dict)}
    skipped = {r.get("id"): r for r in skipped_rows if isinstance(r, dict)}
    # `.get`, not `[]`. `check_registry` reports an id-less row and CONTINUES, so this walk met
    # it and raised — a malformed registry, the canonical package fault, filed as the artifact's.
    registry_ids = {
        r.get("id")
        for r in (reg.get("sources") or [])
        if isinstance(r, dict) and r.get("id")
    }
    both = set(active) & set(skipped)
    if both:
        _fail(
            "map-completeness-1a", f"rows in BOTH active and skipped: {sorted(both)}", f
        )
    missing = registry_ids - set(active) - set(skipped)
    if missing:
        _fail(
            "map-completeness-1b",
            f"registry rows in neither array: {sorted(missing)}",
            f,
        )
    unknown = (set(active) | set(skipped)) - registry_ids
    if unknown:
        _fail(
            "map-completeness-1c",
            f"rows that are not registry rows: {sorted(unknown)}",
            f,
        )
    for rid, row in active.items():
        for key in ("as_of", "access_status", "sanitization"):
            if not row.get(key):
                _fail("map-completeness-1d", f"active row {rid}: no `{key}`", f)
        posture = row.get("sanitization") or {}
        if posture and not posture.get("status"):
            _fail("sanitization-1a", f"active row {rid}: posture with no `status`", f)
    for rid, row in skipped.items():
        if row.get("cause_class") not in SKIP_CAUSE_CLASSES:
            _fail(
                "map-completeness-1e",
                f"skipped row {rid}: `cause_class` {row.get('cause_class')!r}",
                f,
            )
        if not row.get("cause"):
            _fail("map-completeness-1f", f"skipped row {rid}: no `cause`", f)
        if "sanitization" in row:
            _fail(
                "map-completeness-1g",
                f"skipped row {rid}: carries a `sanitization` posture, which belongs on ACTIVE "
                "rows only",
                f,
            )
    declared = {g.get("type") for g in doc.get("groups") or []}
    guard = doc.get("scope_guard") or {}
    absent = set(guard.get("absent_types") or [])
    excluded = {e.get("item") for e in guard.get("excluded") or []}
    for gtype in GROUP_TYPES:
        if gtype not in declared and gtype not in absent:
            _fail(
                "map-completeness-2a",
                f"axis {gtype!r} has no group and is not in `absent_types`",
                f,
            )
        if gtype in absent and gtype not in excluded:
            _fail(
                "map-completeness-2b",
                f"axis {gtype!r} is absent with no reason in `excluded`",
                f,
            )
    for shared in guard.get("shared_terms") or []:
        if not shared.get("owner"):
            _fail(
                "map-completeness-3",
                f"shared term {shared.get('term')!r} names no owner",
                f,
            )
    verdicts = {v.get("angle_id"): v for v in doc.get("angle_applicability") or []}
    # `isinstance` filtered, like the sources walk beside it. `_check_angles` reports a
    # non-mapping angle block and CONTINUES, so this walk met a string and raised — a package
    # fault filed as the artifact's, the third instance of the same pattern in this file.
    for aid in [a.get("id") for a in reg.get("angles") or [] if isinstance(a, dict)]:
        if aid not in verdicts:
            _fail("map-completeness-4a", f"no verdict for angle {aid}", f)
            continue
        verdict = verdicts[aid]
        if not verdict.get("reason"):
            _fail("map-completeness-4b", f"{aid}: verdict with no reason", f)
        if aid in ALWAYS_ON and verdict.get("holds") is False:
            _fail(
                "map-completeness-5",
                f"{aid} is declared `trigger: always` in the registry and the map refuses it; "
                "that contradicts the contract rather than describing the project",
                f,
            )
        if verdict.get("holds") is False and not re.search(
            r"[a-z_]+\.[a-z_]+", verdict.get("reason", "")
        ):
            _fail(
                "map-completeness-6",
                f"{aid}: `holds: false` names no DECIDING value",
                f,
            )


def check_cell_sanitization(doc, f: Findings) -> None:
    """sanitization (1) cell half, (3) and (4). The subject is the CELL, never the map row."""
    for cell in doc.get("coverage") or []:
        key = f"{cell.get('group_id')}/{cell.get('source_id')}"
        if cell.get("status") != "reached":
            continue
        posture = cell.get("sanitization")
        if not posture:
            _fail(
                "sanitization-1b", f"{key}: reached cell records no `sanitization`", f
            )
            continue
        status = posture.get("status")
        if status == "modified" and not posture.get("cause"):
            _fail("sanitization-3", f"{key}: `modified` with no `cause`", f)
        if status == "not-fetched":
            _fail(
                "sanitization-4",
                f"{key}: a REACHED cell's own status is `not-fetched`. The subject is the CELL, "
                "not the map row it cites",
                f,
            )


# ------------------------------------- the coverage grid, admission and the bound


def check_search(doc, reg, kmap, f: Findings) -> None:
    """coverage grid (1)(2)(4)(5), admission (1)-(3) and bound (1)-(3)."""
    if doc.get("outcome") == "not_run":
        for key in (
            "coverage",
            "candidates",
            "unadmitted",
            "bound",
            "retrieval_summary",
        ):
            if doc.get(key) is not None:
                _fail(
                    "coverage-grid-1b",
                    f"`outcome: not_run` carrying `{key}`. The guide says a not-run output "
                    "carries the map's verdict and NOTHING else",
                    f,
                )
        return
    angle_id = (doc.get("meta") or {}).get("angle_id")
    owed = None
    angle = next(
        (
            a
            for a in reg.get("angles") or []
            if isinstance(a, dict) and a.get("id") == angle_id
        ),
        None,
    )
    if angle is None:
        _fail("coverage-grid-1a", f"angle {angle_id!r} is not a registry angle", f)
        return
    cells = doc.get("coverage") or []
    keys = [(c.get("group_id"), c.get("source_id")) for c in cells]
    seen = set(keys)
    dupes = sorted({k for k in keys if keys.count(k) > 1})
    if dupes:
        # A cell is the intersection of ONE group and ONE source; two rows for it are two
        # different claims about the same query. Compared as sets they were invisible, and a
        # second row with `status: reached` re-opened the attribution hole a rule had just
        # closed.
        _fail(
            "coverage-grid-2c",
            f"the same cell appears more than once: {['/'.join(map(str, k)) for k in dupes]}",
            f,
        )
    if kmap is None:
        _fail(
            "coverage-grid-1a",
            "the keyword map could not be read, so the owed grid was NOT derived. Dropping any "
            "one of the three terms is wrong in a measurable way; dropping all three is not a "
            "check",
            f,
        )
    else:
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
            _fail(
                "coverage-grid-2a", f"owed cell {missing[0]}/{missing[1]} is absent", f
            )
        for extra in sorted(seen - owed):
            _fail(
                "coverage-grid-2b",
                f"cell {extra[0]}/{extra[1]} is not owed by the three terms",
                f,
            )
    #: The map's declared terms, per group. The owed grid is DERIVED from these groups, so a cell
    #: querying a term the map never declared has broken the link the grid rests on. Nothing read
    #: `queries[]` at all until a blind run found every cell of the calibration fixture querying a
    #: bare word its group does not carry.
    # `(kmap or {})`. The rule three blocks up fires when the map could not be read and
    # DELIBERATELY does not return, so this walk met `None` and crashed — aborting the admission,
    # bound and summary families on nothing worse than a typo'd `--keyword-map`.
    terms = {
        g.get("id"): [g.get("canonical"), *(g.get("expansions") or [])]
        for g in ((kmap or {}).get("groups") or [])
    }
    for cell in cells:
        key = f"{cell.get('group_id')}/{cell.get('source_id')}"
        # SUBSTRING, because a query is recorded VERBATIM including its filter expression, so the
        # term is embedded in a larger string rather than equal to it.
        declared = [x for x in terms.get(cell.get("group_id"), []) if x]
        for query in cell.get("queries") or []:
            if declared and not any(term in str(query) for term in declared):
                _fail(
                    "coverage-grid-5",
                    f"{key}: query {query!r} names none of the group's terms {declared}",
                    f,
                )
        reached = cell.get("status") == "reached"
        if reached:
            for field in ("returned", "kept"):
                if cell.get(field) is None:
                    _fail(
                        "coverage-grid-4a",
                        f"{key}: reached and records no `{field}`",
                        f,
                    )
            if cell.get("returned") and not cell.get("count_frame"):
                _fail(
                    "coverage-grid-4b",
                    f"{key}: non-zero `returned` with no `count_frame`; a count is "
                    "unre-derivable without knowing what was counted",
                    f,
                )
        else:
            if not cell.get("cause"):
                _fail(
                    "coverage-grid-4c",
                    f"{key}: not reached and records no observable `cause`",
                    f,
                )
            if cell.get("returned") is not None or cell.get("kept") is not None:
                _fail(
                    "coverage-grid-4d",
                    f"{key}: not reached and records a count. A zero and an absence are "
                    "different claims and the grid must keep them apart",
                    f,
                )
    _check_admission(doc, cells, f)
    _check_bound(doc, angle, f)
    _check_summary(doc, cells, f, owed)


def _check_summary(doc, cells, f: Findings, owed: set | None = None) -> None:
    """The summary is DERIVED from the finished coverage list, never counted as you go.

    `cells_owed` comes from the OWED GRID, not from `len(cells)`. Taken from the list, a
    duplicated row inflated the number and the gate rewarded the inflation while refusing the
    true count.
    """
    summary = doc.get("retrieval_summary") or {}
    derived = {
        "cells_owed": len(owed)
        if owed is not None
        else len(set((c.get("group_id"), c.get("source_id")) for c in cells)),
        "cells_reached": sum(1 for c in cells if c.get("status") == "reached"),
        "candidates": len(doc.get("candidates") or []),
        "unadmitted": len(doc.get("unadmitted") or []),
    }
    for key, value in derived.items():
        if summary.get(key) != value:
            _fail(
                "retrieval-summary-1",
                f"`retrieval_summary.{key}` is {summary.get(key)!r} and the finished coverage "
                f"list gives {value}",
                f,
            )


def _check_admission(doc, cells, f: Findings) -> None:
    reached = {
        f"{c.get('group_id')}/{c.get('source_id')}"
        for c in cells
        if c.get("status") == "reached"
    }
    every = {f"{c.get('group_id')}/{c.get('source_id')}" for c in cells}
    for row, label in [(r, "candidate") for r in doc.get("candidates") or []] + [
        (r, "unadmitted row") for r in doc.get("unadmitted") or []
    ]:
        key = row.get("found_by")
        if not key:
            continue  # presence is admission-2a's, below
        if key not in every:
            _fail(
                "admission-2d",
                f"{row.get('item_id', '?')}: `found_by` is {key!r} and no such cell exists",
                f,
            )
        elif key not in reached:
            _fail(
                "admission-2d",
                f"{row.get('item_id', '?')}: `found_by` names {key!r}, which this run records as "
                "NOT reached. The artifact cannot say both that a query was refused and that a "
                "row came out of it",
                f,
            )
    for cand in doc.get("candidates") or []:
        item = cand.get("item_id", "?")
        if not cand.get("url"):
            _fail(
                "admission-1a",
                f"{item}: admitted with no resolvable URL (L-7 conjunct 1)",
                f,
            )
        if not cand.get("stated_date"):
            _fail(
                "admission-1b",
                f"{item}: admitted with no stated version or date (L-7 conjunct 2)",
                f,
            )
        if not cand.get("found_by"):
            _fail("admission-2a", f"{item}: candidate with no `found_by`", f)
    for row in doc.get("unadmitted") or []:
        item = row.get("item_id", "?")
        if not row.get("found_by"):
            _fail("admission-2b", f"{item}: unadmitted row with no `found_by`", f)
        if not row.get("reason"):
            _fail("admission-2c", f"{item}: unadmitted row with no reason", f)
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
                "admission-3",
                f"{key}: `kept` is {cell.get('kept')} and {cited} rows cite the cell",
                f,
            )


def _check_bound(doc, angle, f: Findings) -> None:
    bound = doc.get("bound") or {}
    if bound.get("cap") != angle.get("cap"):
        _fail(
            "bound-1",
            f"`bound.cap` is {bound.get('cap')!r} and the registry declares {angle.get('cap')!r}. "
            "The cap is transcribed VERBATIM; an author does not widen their own cap",
            f,
        )
    if bound.get("hit"):
        note = bound.get("dropped_note") or ""
        if not note:
            _fail("bound-2a", "`hit: true` owes a `dropped_note`", f)
        elif not re.search(r"\d", note):
            _fail(
                "bound-2b",
                "`dropped_note` names no ordering position and no first row that fell off; "
                '"the rest were dropped" is not re-appliable',
                f,
            )
    if bound.get("ordering") and bound["ordering"] != angle.get("ordering_signal"):
        if not bound.get("ordering_deviation"):
            _fail(
                "bound-3",
                "`ordering` deviates from the registry with no `ordering_deviation`",
                f,
            )


# ---------------------------------- the ordering is appliable, total, and ordered
#
# `bound (4)` (the ordering is appliable and total) and `primary_dimension (2)` (no rule maps
# `signal` to a dimension) are BOTH declared NOT-A-RULE. They are properties of the REGISTRY and
# of this module asserted at build time by the test suite, not rules this validator emits at
# runtime — an artifact author cannot repair either one, and emitting them here would attribute a
# runtime rule to a task that authors none.


# ------- extract vocabularies, the bail family, body sections, transferability, coherence


def check_extract(doc, f: Findings) -> None:
    """vocabularies (1)-(7), bail (1)-(3), body sections, transferability, measured_* coherence."""
    if doc.get("outcome") == "skipped":
        bail = doc.get("skipped") or {}
        if set(bail) - {"cause", "detail"}:
            _fail(
                "bail-1",
                f"`skipped` carries {sorted(set(bail) - {'cause', 'detail'})}",
                f,
            )
        # `no-stated-load` gets its OWN rule and only that one. Firing the enum rule as well
        # produced two findings for one fault, and the general one carries the weaker message —
        # the spec's "a fault fires ONE rule and that rule carries the cause".
        if (
            bail.get("cause") not in BAIL_CAUSES
            and bail.get("cause") != "no-stated-load"
        ):
            _fail("bail-2", f"cause {bail.get('cause')!r} is not one of the three", f)
        if bail.get("cause") == "no-stated-load":
            _fail(
                "bail-3",
                "`no-stated-load` is REFUSED as a cause: it would delete the operational canon "
                "and every negative result, which is a promotion cut wearing a bail's clothes",
                f,
            )
        return
    source = doc.get("source") or {}
    lic = source.get("license")
    if lic is not None and lic != "unverified" and not SPDX.match(str(lic)):
        _fail(
            "vocabularies-6",
            f"`license` {lic!r} is neither an SPDX id, `unverified` nor null",
            f,
        )
    if source.get("access_status") not in (
        "open",
        "crawl-delayed",
        "rate-limited",
        "paywalled-abstract-only",
        "polite-pool",
        "blocked",
    ):
        _fail(
            "vocabularies-7",
            f"source `access_status` {source.get('access_status')!r}",
            f,
        )
    for ep in doc.get("episodes") or []:
        eid = ep.get("id", "?")
        if ep.get("signal") not in GOLDEN_SIGNALS:
            _fail("vocabularies-1", f"{eid}: `signal` {ep.get('signal')!r}", f)
        for leaf, value in (ep.get("load_class") or {}).items():
            if leaf not in BAND_LEAVES:
                _fail(
                    "vocabularies-2",
                    f"{eid}: `load_class.{leaf}` is not a band leaf",
                    f,
                )
        cm = ep.get("consistency_model")
        if cm is not None and cm not in CONSISTENCY_MODELS:
            _fail(
                "vocabularies-3",
                f"{eid}: `consistency_model` {cm!r} is not Jepsen's, verbatim",
                f,
            )
        tech = ep.get("technology")
        if tech is not None and not PURL.match(str(tech)):
            _fail("vocabularies-4", f"{eid}: `technology` {tech!r} is not a purl", f)
        if ep.get("evidence_class") not in EVIDENCE_CLASSES:
            _fail(
                "vocabularies-5",
                f"{eid}: `evidence_class` {ep.get('evidence_class')!r}",
                f,
            )
        cc = ep.get("cause_class")
        if cc is not None and cc not in EPISODE_CAUSE_CLASSES:
            _fail(
                "vocabularies-5a",
                f"{eid}: `cause_class` {cc!r} is not in the EPISODE's vocabulary, "
                "which is disjoint from the map's field of the same name",
                f,
            )
        if not ep.get("pattern"):
            _fail("vocabularies-5b", f"{eid}: no `pattern`", f)
        if ep.get("primary_dimension") not in BAND_LEAVES:
            _fail(
                "primary-dimension-1",
                f"{eid}: `primary_dimension` {ep.get('primary_dimension')!r}",
                f,
            )
        _check_transferability(ep, eid, f)
        _check_measured(ep, eid, f)


def _check_transferability(ep, eid: str, f: Findings) -> None:
    t = ep.get("transferability")
    if not t:
        _fail("transferability-1a", f"{eid}: no `transferability`", f)
        return
    if t.get("level") not in ("high", "moderate", "low"):
        _fail("transferability-1b", f"{eid}: level {t.get('level')!r}", f)
    if len(str(t.get("reason") or "")) < 20:
        _fail("transferability-1c", f"{eid}: reason is under 20 characters", f)


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
                "measured-coherence-1a",
                f"{eid}: `measured_magnitude` with no `measured_value`",
                f,
            )
        if unit is None:
            _fail(
                "measured-coherence-1b",
                f"{eid}: `measured_magnitude` with no `measured_unit`",
                f,
            )


def check_body_sections(text: str, f: Findings) -> None:
    """body sections (1) presence and (2) non-triviality. Never prose quality."""
    # Anchored, not substring: `## Episodes` was satisfied by `## Episodes and observations`,
    # and a `## ` inside a fenced block truncated a section into a false triviality finding.
    fenced = re.sub(r"```.*?```", "", text, flags=re.S)
    headings = {line.strip() for line in fenced.splitlines() if line.startswith("## ")}
    for heading in BODY_SECTIONS:
        if heading not in headings:
            _fail("body-sections-1", f"the record has no `{heading}` section", f)
            continue
        after = fenced.split(f"\n{heading}\n", 1)[-1]
        body = after.split("\n## ", 1)[0].strip()
        if len(body) < 40:
            _fail(
                "body-sections-2",
                f"`{heading}` is present but trivial ({len(body)} chars)",
                f,
            )


# ------------------------------------------------------------ the synthesis rules


def check_queue(queue_path, extracts_dir, f: Findings) -> None:
    """queue (1)-(3): the FROZEN queue reconciled against the records that were written.

    The THIRD direction. `synthesis-1b` checks index -> episode and `synthesis-4` checks
    episode -> index, so a queue row that produced NO FILE is invisible to both: a bail that
    wrote nothing deflates the survey and the gate reports neither. `synthesis-4` did not exist
    when this was written, and three documents said it did — the claim was made true rather
    than softened. `--queue` was on this
    validator's signature and in the spec's input-file list, and was read by NOTHING — four
    siblings implement it, and a declared flag that is silently ignored is a lie in the CLI.

    Args:
        queue_path: The frozen `extract-queue.yaml`, or None when the flag was not passed.
        extracts_dir: The directory the records were written to, or None. Both are needed:
            reconciliation compares one against the other, so either being absent means the
            check did not run, which is a finding rather than a silent pass.
        f: The findings collector.
    """
    if queue_path is None or extracts_dir is None:
        cause = (
            "no `--queue`, so the FROZEN queue was not reconciled against the records on disk "
            "and the third direction went unchecked"
            if queue_path is None
            else "`--queue` without `--extracts`, so there is no record set to reconcile the "
            "queue against"
        )
        _fail(
            "queue-crosscheck-skipped",
            f"{cause}. Reported ONCE, not once per row: the omitted flag is the dispatcher's "
            "and blaming the artifact's author for each row of a queue it never saw is N false "
            "findings from one fault. Exit 1 — the flag can be supplied and the run repeated",
            f,
        )
        print("SKIP queue-crosscheck")
        return
    path = pathlib.Path(queue_path)
    if not path.is_file():
        # A bad INVOCATION, which belongs at exit 2 with the other input-class faults: the
        # agent under test cannot repair a path the dispatcher got wrong.
        _fail("queue-unreadable", f"--queue {path} is not a file", f)
        return
    doc = load_yaml(path, f, rule="queue-unreadable")
    if doc is None:
        return
    present = (
        {child.stem for child in pathlib.Path(extracts_dir).glob("*.yaml")}
        if extracts_dir
        else set()
    )
    for row in doc.get("queue") or []:
        item = row.get("item_id") if isinstance(row, dict) else None
        if not item:
            continue
        # `extract-` + the sanitized stem: the SKILL says the record is written as
        # `extract-<source>.yaml`, and comparing the bare stem made a correct queue look empty.
        want = f"extract-{record_filename(item)}"
        if want not in present:
            _fail(
                "queue-row-without-record",
                f"queue row {item!r} has no record at {want!r}.yaml in the extracts directory — the extraction produced "
                "nothing for it, and an index synthesised over a queue with holes in it is "
                "built on a corpus its own manifest says is incomplete. A bail still writes a "
                "skip record",
                f,
            )


def check_synthesis(doc, extracts, f: Findings) -> None:
    """synthesis (1)-(3), currency (1)-(2), and the delta-mode `lineage` rule."""
    check_band(doc, "project_band", f)
    known = set()
    #: Every episode id the index cites, across ALL FOUR evidence sites. The mirror direction
    #: reads it, so an id cited only by a `hard_limits[].source` still counts as cited.
    cited: set = set()
    #: Episode id -> its source's `published_date`. Lens 8's caveat has to be re-derivable from
    #: the extracts rather than asserted, which is what the second currency rule reads.
    dated: dict = {}
    for record in extracts or []:
        published = (record.get("source") or {}).get("published_date")
        for ep in record.get("episodes") or []:
            if ep.get("id"):
                known.add(ep["id"])
                if published:
                    dated[ep["id"]] = str(published)
    order = {"very-low": 0, "low": 1, "moderate": 2, "high": 3}
    for area in doc.get("areas") or []:
        name = area.get("area", "?")
        evidence = area.get("evidence") or []
        # currency (1) — lens 8 shipped with no field, no report section, no condition and no
        # rule, so a producer computing it had nowhere to put it. Present is the first half.
        if "currency" not in area:
            _fail(
                "currency-1",
                f"{name}: no `currency`. Lens 8 is a caveat on the whole area and it is owed "
                "even when every backing source is undated, where it is null",
                f,
            )
        # EVERY backing site, not just `evidence[]`. `hard_limits[].source`,
        # `failure_modes[].evidence` and `migration_trigger.evidence` all name episodes the area
        # rests on, and an area whose OLDEST evidence is cited only from one of those three would
        # otherwise be caveated against a newer date.
        backing_ids = set(evidence)
        for limit in area.get("hard_limits") or []:
            if limit.get("source"):
                backing_ids.add(limit["source"])
        for mode in area.get("failure_modes") or []:
            backing_ids.update(mode.get("evidence") or [])
        backing_ids.update((area.get("migration_trigger") or {}).get("evidence") or [])
        backing = {dated[e] for e in backing_ids if e in dated}
        caveat = area.get("currency")
        # currency (2) — EQUALITY over a STRUCTURED field, in both directions.
        #
        # The first version matched dates inside a free-text caveat, and no lookaround survives a
        # field that admits a publication date, a benchmark result date, a documentation version
        # and an incident date: delimiting across `-` and digits alone still let `2019` hide
        # inside `2019/06/01` and `v14` inside `v14.2`, while a correct caveat writing a span as
        # `2019-2024` was refused for BOTH dates it contained. Splitting `currency` into `dates`
        # and `note` removes the parsing — the machine half is compared, the prose half is read.
        if isinstance(caveat, dict) and backing:
            declared = set(caveat.get("dates") or [])
            if declared != backing:
                _fail(
                    "currency-2",
                    f"{name}: `currency.dates` is {sorted(declared)}; its backing episodes' "
                    f"sources carry {sorted(backing)}. Transcribe each one in the form its "
                    "source carries it",
                    f,
                )
        # currency (3) — a NULL caveat on a dated corpus. Four shipped documents say null is
        # correct "only where every backing source is undated" and nothing ran it: a producer that
        # did not compute lens 8 wrote null and reached exit 0, which is the pre-field state with
        # an extra key. The absence had become a value.
        if "currency" in area and caveat is None and backing:
            _fail(
                "currency-3",
                f"{name}: `currency` is null while its backing episodes carry dates "
                f"({sorted(backing)}). Null is for an area whose every backing source is undated",
                f,
            )
        cited.update(e for e in evidence if e)
        if not evidence:
            _fail("synthesis-1a", f"{name}: `evidence[]` is empty", f)
        for eid in evidence:
            if extracts is not None and eid not in known:
                _fail(
                    "synthesis-1b",
                    f"{name}: evidence {eid!r} resolves to no extracted episode",
                    f,
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
                        "synthesis-2",
                        f"{name}: `confidence` is {area.get('confidence')!r} and the WEAKEST "
                        f"backing class is {weakest!r}; it is re-derived, never averaged",
                        f,
                    )
        trigger = area.get("migration_trigger")
        if trigger and not (trigger.get("evidence") or []):
            _fail("synthesis-3a", f"{name}: `migration_trigger` carries no evidence", f)
        for mode in area.get("failure_modes") or []:
            if not (mode.get("evidence") or []):
                _fail(
                    "synthesis-3b",
                    f"{name}: a `failure_modes` entry carries no evidence",
                    f,
                )
        # EVERY evidence site, not just the area's. `evidence[]` is episode ids ALWAYS, and
        # `hard_limits[].source` is one too -- lens 4 is the only blocker-producing lens and its
        # citation was an unconstrained string nothing resolved.
        if extracts is None:
            continue
        sites = [
            (f"{name}: `migration_trigger`", (trigger or {}).get("evidence") or [])
        ]
        sites += [
            (f"{name}: `failure_modes[{i}]`", mode.get("evidence") or [])
            for i, mode in enumerate(area.get("failure_modes") or [])
        ]
        sites += [
            (f"{name}: `hard_limits[{i}].source`", [limit.get("source")])
            for i, limit in enumerate(area.get("hard_limits") or [])
        ]
        cited.update(eid for _, ids in sites for eid in ids if eid)
        for where, ids in sites:
            for eid in ids:
                if eid not in known:
                    _fail(
                        "synthesis-3c",
                        f"{where}: {eid!r} resolves to no extracted episode. A prose citation is "
                        "not evidence",
                        f,
                    )
    # synthesis (4) — the MIRROR of (1), and the direction the queue family's justification
    # assumed. `synthesis-1b` walks index -> episode; nothing walked episode -> index, so a
    # record the index never touched was invisible: a leftover from a rename is
    # indistinguishable from a real one, and it inflates every count taken from the directory.
    # FILE granularity, like the two siblings that ship it — an index citing three of a
    # record's five episodes is synthesis, not an orphan. A recorded SKIP is exempt: a bail has
    # nothing for the index to cite, and flagging it would punish the survey for recording an
    # unread source, which is what the bail family exists to require. DELTA runs are the open
    # edge (OQ-S1): a baseline record this index does not use would be refused here, and the
    # delta slice settles whether a delta run is handed its baseline's records at all.
    for record in extracts or []:
        if record.get("outcome") == "skipped":
            continue
        ids = {ep.get("id") for ep in record.get("episodes") or [] if ep.get("id")}
        if ids & cited:
            continue
        _fail(
            "synthesis-4",
            f"the extract record for {(record.get('meta') or {}).get('source_id')!r} is in the "
            "extracts directory and NO area cites any of its episodes at any of the four "
            "evidence sites. Either the extraction's output was dropped from the index, or the "
            "file is a leftover — a record that backs nothing is not evidence, and it inflates "
            "every count taken from the directory. A record with nothing to cite records its "
            "bail as `outcome: skipped`",
            f,
        )
    lineage = doc.get("lineage") or {}
    if doc.get("mode") == "delta" and not lineage.get("extends"):
        _fail("lineage-liveness-1", "mode is `delta` and `lineage.extends` is null", f)


# ------------------------------------------------- `confidence`, re-derived


def derive_confidence(ep: dict) -> str:
    """The ordered table, branch by branch. The producer never asserts this value.

    Its INPUT SET is FOUR facts: `evidence_class`, `measured_value` (present or absent),
    `configuration_stated`, and whether `load_class` is fully stated. The two fields that are
    NOT inputs are asserted absent from this function by an AST test, because an author never
    asserts the value and a fifth input added by accident is invisible to any value test.

    Args:
        ep: One episode.

    Returns:
        The derived confidence class.
    """
    kind = ep.get("evidence_class")
    has_value = ep.get("measured_value") is not None
    if kind == "narrative-only":
        return "very-low"
    if kind == "vendor-documented-limit":
        return "high" if has_value else "low"
    if not has_value:
        return "low"
    if ep.get("configuration_stated") is False:
        return "moderate"
    if kind in {
        "rule-governed-benchmark",
        "peer-reviewed-evaluation",
        "independent-verification",
    }:
        return "high"
    # "Fully stated" means all FIVE sub-keys non-null. They are nullable because sources report
    # one or two dimensions and say nothing about the rest, and that nullability is what keeps
    # these last two branches reachable in both directions.
    load_class = ep.get("load_class") or {}
    if all(load_class.get(leaf) is not None for leaf in BAND_LEAVES):
        return "high"
    return "moderate"


def check_confidence(doc, f: Findings) -> None:
    """derived confidence (1): a hand-set value disagreeing with the derivation is REFUSED."""
    for ep in doc.get("episodes") or []:
        derived = derive_confidence(ep)
        if ep.get("confidence") != derived:
            _fail(
                "derived-confidence-1",
                f"{ep.get('id', '?')}: `confidence` is {ep.get('confidence')!r} and the table "
                f"derives {derived!r}",
                f,
            )


# ------------------------------- `load_class`, re-derived from the threshold table


#: NON-ORDINAL, so there is no adjacent pair for a boundary to sit between. Skipped by
#: CONSTRUCTION, which is a different mechanism from the discovered-unsourced list below and is
#: kept apart from it deliberately.
NON_ORDINAL = ("geo_distribution",)
#: The availability enum members ARE the boundaries — numeric literals, ascending.
AVAILABILITY_BANDS = ("99", "99.9", "99.95", "99.99", "99.999")


def unsourced_dimensions(f: Findings | None = None) -> frozenset[str]:
    """The dimensions the re-derivation SKIPS, read from `load-band-thresholds.md`.

    DERIVED from the threshold file itself, never hand-copied here: a skip set restated beside it
    it came from drifts from it, and a dimension discovered to be unsourced would then leave the
    validator unable to tell a correct episode from a wrong one.
    """
    try:
        import yaml
    except ModuleNotFoundError:
        if f is not None:
            _fail("dependency-missing", "pyyaml is not installed", f)
        return frozenset()
    try:
        block = re.search(r"```yaml\n(.*?)```", THRESHOLDS_PATH.read_text(), re.S)
        data = yaml.safe_load(block.group(1)) if block else {}
        # INSIDE the try. The read and the parse were guarded and the walk that dereferences
        # each entry was not, so a thresholds file holding a scalar crashed the run and filed
        # under the ARTIFACT's rule at exit 1 — a package file blamed on the author, which is
        # the defect `thresholds-unreadable` exists to prevent.
        return frozenset(
            entry["dimension"]
            for entry in (data.get("unsourced_dimensions") or [])
            if entry.get("dimension")
        )
    except Exception as exc:  # noqa: BLE001
        if f is not None:
            _fail("thresholds-unreadable", f"{THRESHOLDS_PATH.name}: {exc}", f)
        return frozenset()


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
        if dimension in NON_ORDINAL:
            continue
        band = (ep.get("load_class") or {}).get(dimension)
        magnitude = ep.get("measured_magnitude")
        # The NO-NUMBER rule applies to every ordered dimension, sourced or not. The skip list
        # governs the DERIVATION -- comparing a band against a number needs a published boundary
        # -- and says nothing about whether a band may be asserted with no number at all. Skipping
        # both together let `data_volume: large` stand on an episode whose own claim says the
        # authors described the effect "without measuring it", and a blind reviewer found it in
        # the CLEAN fixture where the gate could not.
        if magnitude is None:
            if band is not None:
                _fail(
                    "derived-load-class-2",
                    f"{eid}: `load_class.{dimension}` is {band!r} with no `measured_magnitude` "
                    "behind it. A band asserted with no number is refused",
                    f,
                )
            continue
        if dimension in skip:
            continue  # no published boundary, so the band cannot be re-derived from the number
        if dimension == "availability_target":
            # I7: the UNIT is part of the derivation. A `req/s` number read as a percentage
            # derived a band and passed.
            unit = (ep.get("measured_unit") or "").strip()
            if unit not in ("%", "percent"):
                _fail(
                    "derived-load-class-1",
                    f"{eid}: `availability_target` is derived from a percentage and the unit is "
                    f"{unit!r}",
                    f,
                )
                continue
            derived = _availability_band(float(magnitude)) or "below the lowest band"
            if band != derived:
                _fail(
                    "derived-load-class-1",
                    f"{eid}: `load_class.availability_target` is {band!r} and {magnitude} "
                    f"derives {derived!r}. A band that disagrees with the number it was computed "
                    "from is a hard failure, not an opinion",
                    f,
                )


# ------------------------------------------ every ordered dimension carries its order


# --------------------------------- id grammar, `record_filename`, spawn-key parity


#: Part (b) of #42: an id already ending in a hashed stem cannot take the identity branch.
HASHED_STEM = re.compile(r"--[0-9a-f]{12}$")
PREFIX_CAP = 80
EPISODE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*#e[1-9][0-9]*$")
ID_PREFIX = re.compile(r"^(DOI-|ARXIV-|WEB-)")


def record_filename(item_id: str) -> str:
    """The filename stem a record for `item_id` must be written under.

    BOTH parts of the filename rule, mirroring the sibling that ships both and never the one with
    part (a) only, which genuinely collides.

    (a) Sanitize to `[A-Za-z0-9._-]`, cap the prefix, and append a 12-hex digest OF THE WHOLE
        ID — so two ids differing only in characters the sanitizer collapses still get
        different names.
    (b) The identity branch REFUSES an id that already ends in a hashed stem, so `f(f(x))`
        cannot equal `f(x)` for an `x` the sanitizer touched.

    This type is in the MOST-exposed class: a DOI always contains `/` and a `WEB-` id carries
    dots and may carry `/`. An id written verbatim lands the record in a directory nothing
    looks in, stays perfectly valid, and is treated as never written — and a caller that
    locates records on disk then re-requests the row on every pass while it looks correct.

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
            "id-grammar-2",
            f"`id_class` {id_class!r} is not one of the three prefixes",
            f,
        )
    else:
        # BOTH directions: an id whose class says one thing and whose prefix says
        # another is a row a later wave cannot resolve. `ID_PREFIX` was defined and read by
        # NOTHING, so the clause the spec states was never implemented at all.
        prefix = ID_PREFIX.match(sid)
        declared = f"{id_class}-"
        if prefix and prefix.group(1) != declared:
            _fail(
                "id-grammar-2",
                f"`id_class` is {id_class!r} and the id begins {prefix.group(1)!r}",
                f,
            )
        elif not prefix:
            _fail(
                "id-grammar-2",
                f"`id_class` is {id_class!r} and {sid!r} carries no `{declared}` prefix",
                f,
            )
    for ep in doc.get("episodes") or []:
        eid = str(ep.get("id") or "")
        # The PATH clause first: a DOI legitimately carries `/`, so this is about what the id
        # would mean if it were written to disk, not about its shape. Behind the shape check it
        # was unreachable -- the shape pattern forbade the very characters it looked for.
        if "\\" in eid or eid.startswith("/") or "/../" in eid or eid.endswith("/"):
            _fail("id-grammar-3a", f"episode id {eid!r} could be read as a path", f)
        if not EPISODE_ID.match(eid):
            _fail("id-grammar-1", f"episode id {eid!r} is not `<source-id>#e<N>`", f)
            continue
        if not eid.startswith(f"{sid}#e"):
            _fail("id-grammar-3b", f"episode id {eid!r} does not root on `{sid}`", f)
    # The CROSS-BRANCH property, not a round-trip: a within-branch round-trip passes while the
    # collision exists, which is exactly the false assurance #42 records.
    name = record_filename(sid)
    if HASHED_STEM.search(sid) and record_filename(name) == name:
        _fail(
            "record-filename-2",
            f"{sid!r} already ends in a hashed stem and took the identity branch, so f(f(x)) "
            "== f(x) for an id the sanitizer touched",
            f,
        )


# ------------------------------------------- the `score` presence and range rule


def check_score(doc, f: Findings) -> None:
    """The quality filter's `score`: PRESENT and in range. Ranking only, never a cut."""
    source = doc.get("source") or {}
    score = source.get("score")
    if score is None:
        _fail("quality-filter-1a", "the source record carries no `score`", f)
        return
    if not isinstance(score, int) or isinstance(score, bool) or not 0 <= score <= 10:
        _fail("quality-filter-1b", f"`score` {score!r} is not an integer 0-10", f)


# --------------------------------------------------------------------------- the CLI


def _read_extracts(directory, f: Findings):
    if directory is None:
        return None
    path = pathlib.Path(directory)
    if not path.is_dir():
        _fail("input-1", f"{path} is not a directory", f)
        return None
    out = []
    for child in sorted(path.glob("*.yaml")):
        doc = load_yaml(child, f, rule="input")
        if doc is not None:
            out.append(doc)
    return out


def build_parser() -> argparse.ArgumentParser:
    """Four subcommands, one per kind, with the signatures the skill documents.

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


class _ArtifactCrash(Exception):
    """A crash raised while walking ARTIFACT content, as opposed to package content.

    The distinction is the whole exit contract. A blanket handler around the run filed every
    crash under one rule, so a malformed registry — the spec's own canonical exit-2 case — exited
    1, sending the packet back to a producing agent to repair an artifact that
    was correct. It is raised only from `_walk_artifact`, which wraps the per-kind checks.
    """

    def __init__(self, cause: BaseException) -> None:
        super().__init__(str(cause))
        self.cause = f"{type(cause).__name__}: {cause}"


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    f = Findings()
    try:
        return _run(args, f)
    except _ArtifactCrash as exc:
        # ARTIFACT content is UNTRUSTED and arbitrarily shaped: a unit written into a numeric
        # field, a `reason:` line with no value, a list where a mapping belongs. The file read
        # and parsed, so the fault is the AUTHOR's — exit 1 — and the accompanying `schema`
        # finding already names it. None of them may discard the findings already collected.
        _fail(
            "artifact-untraversable",
            f"the artifact could not be traversed: {exc.cause}",
            f,
        )
        return _report_and_exit(f)
    except Exception as exc:  # noqa: BLE001
        # Anything OUTSIDE the artifact walk: a malformed registry that parses but is shaped
        # wrong, an unloadable schema, a bug in this validator. Those are PACKAGE faults and exit
        # 2, which is what a dispatcher routes on. Widening the artifact rule to cover them sent
        # the spec's own canonical exit-2 case — a malformed registry — back to the producing
        # agent to repair an artifact that was correct.
        _fail(
            "package-crash",
            f"the package failed before the artifact was judged: "
            f"{type(exc).__name__}: {exc}",
            f,
        )
        return _report_and_exit(f)


def _run(args, f: Findings) -> int:
    # The registry is a PACKAGE file, not an input file, so it files under its own rule and the
    # loader's message — which carries the parse error — is the one the reader gets. Filing it
    # under `input` and then asserting `registry-unreadable` separately produced two findings for
    # one fault, with the informative half misclassified; both exit 2, so no exit-class test saw it.
    reg = load_yaml(REGISTRY_PATH, f, rule="registry-unreadable")
    if reg is None:
        return _report_and_exit(f)
    check_registry(reg, f)

    path = pathlib.Path(args.artifact)
    doc = load_yaml(path, f, rule="input", empty_rule="artifact-untraversable")
    if doc is None:
        return _report_and_exit(f)
    if not isinstance(doc, dict):
        # NOT `input`, which is exit 2 and reserved for a file that could not be READ. This
        # one read and parsed; a list where a mapping belongs is content the author can
        # repair, which is what the artifact class means.
        _fail(
            "artifact-untraversable",
            f"{path} is a {type(doc).__name__}, not a mapping",
            f,
        )
        return _report_and_exit(f)

    try:
        return _walk_artifact(args, doc, reg, path, f)
    except Exception as exc:  # noqa: BLE001 — re-raised as the ARTIFACT class, see the handler
        raise _ArtifactCrash(exc) from exc


def _walk_artifact(args, doc, reg, path, f: Findings) -> int:
    """The per-kind checks, where a crash is the AUTHOR's fault.

    The boundary is about who can REPAIR the fault, not about which file a line happens to read.
    Three package files are read from in here — the schemas, the threshold table and the
    registry's rows and angle blocks — and each of those reads is guarded at its own site so it
    files under its own rule at exit 2 rather than reaching this function's handler. An earlier
    docstring said "everything in here reads ARTIFACT content", which was false in both
    directions and was the shape three separate blockers took.
    """
    if args.kind == "keyword-map":
        check_schema(doc, "scale-vocabulary-map", f)
        check_map(doc, reg, f)
    elif args.kind == "search":
        check_schema(doc, "search-output", f)
        kmap = load_yaml(pathlib.Path(args.keyword_map), f, rule="input")
        check_cell_sanitization(doc, f)
        check_search(doc, reg, kmap, f)
    elif args.kind == "extract":
        check_schema(doc, "extract-output", f)
        check_extract(doc, f)
        check_confidence(doc, f)
        check_load_band(doc, f)
        check_ids(doc, f)
        if doc.get("outcome") != "skipped":
            check_score(doc, f)
        if doc.get("outcome") != "skipped":
            body = path.with_suffix(".md")
            if body.exists():
                check_body_sections(body.read_text(), f)
            else:
                _fail(
                    "body-sections-1",
                    f"an extracted record with no body: {body.name} does not exist. Running the "
                    "family only where the file is present is a check over the population that "
                    "already satisfies it",
                    f,
                )
    elif args.kind == "synthesis":
        check_schema(doc, "scale-envelope-index", f)
        if args.extracts is None:
            _fail(
                "extracts-crosscheck-skipped",
                "no `--extracts`, so evidence resolution was NOT checked. This is exit 1: the "
                "artifact's author can supply the flag",
                f,
            )
            print("SKIP extracts-crosscheck")
        extracts = _read_extracts(args.extracts, f)
        check_synthesis(doc, extracts, f)
        check_queue(args.queue, args.extracts, f)

    return _report_and_exit(f)


if __name__ == "__main__":
    sys.exit(main())
