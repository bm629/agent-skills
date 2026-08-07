#!/usr/bin/env python3
"""Deterministic gate for market & competitive prior-art artifacts (wave 1).

Checks SHAPE and completeness only — schema, enums, ranges, required fields, and arithmetic
that reconciles two records against each other. It never judges whether a competitor is real,
whether a relevance line is persuasive, or whether an exclusion was fair; those are the
reviewing skill's numbered conditions. A fuzzy heuristic inside a deterministic gate produces
false failures and duplicates the reviewer, so resist making this smarter.

Usage:
    validate_market_competitive_prior_art.py keyword-map <file>
    validate_market_competitive_prior_art.py search <file> --keyword-map <file>

Prints one ``FAIL <rule>: ...`` line per violation; exits 0 when clean.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
SCHEMAS = HERE.parent / "schemas"
DEFAULT_REGISTRY = HERE.parent / "references" / "source-registry.yaml"

GROUP_TYPES = (
    "category",
    "capability",
    "job-to-be-done",
    "audience-segment",
    "seed-product",
)

#: Group types whose terms routinely collide with ordinary language, so a search built from
#: them cannot be made precise without exclusions. A product called "Notion", "Linear" or
#: "Arc" matches an enormous amount of unrelated text. A registry identifier never does, which
#: is why this rule belongs to a market survey specifically.
COLLISION_PRONE_TYPES = ("category", "seed-product")

#: Capability-map paths a conditional trigger may ANCHOR on — the fields the map's own schema
#: marks REQUIRED, so a predicate resting on one always evaluates.
#:
#: The rule is about the SHAPE of the predicate, not about every field in it. An optional field
#: sitting beside a required one in an OR only ever ADDS firings, so it fails OPEN and is
#: legitimate — those are recorded as `widening_legs`. What fails CLOSED, silently, is an AND
#: with an optional field or a sole optional leg: the angle looks configured and never runs.
#: So `trigger_anchor` is the LIST of required-rooted legs and must be NON-EMPTY. A scalar
#: cannot describe a disjunctive trigger: naming one leg of a two-required-leg predicate makes
#: the assertion stop matching the predicate it claims to check.
REQUIRED_CAPABILITY_FIELDS = (
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
)

#: Capability-map paths a conditional trigger may rest on. These are the fields the map's own
#: schema marks REQUIRED, so a predicate anchored on one always evaluates. Anything else is
#: optional, and the governing convention is "absent input implies not-in-set implies false" —
#: so an angle anchored on an optional field silently never fires for any map that omitted it,
#: which looks identical to an angle nobody configured.
REQUIRED_CAPABILITY_FIELDS = (
    "archetype.primary",
    "domain.audience",
    "ui.has_ui",
    "ui.complexity",
    "business.platform",
)

_PREFIX_CAP = 80

#: The marker the hashing branch appends. The identity branch must never return a string that
#: looks like one, or the two branches share an output namespace and injectivity is lost: a
#: caller could pass the hashed stem of one id and receive it back unchanged, colliding with the
#: id it was derived from.
_HASHED_STEM = re.compile(r"--[0-9a-f]{12}$")


def _fail(rule: str, detail: str) -> str:
    return f"FAIL {rule}: {detail}"


def _load_schema(name: str) -> dict:
    return json.loads((SCHEMAS / name).read_text())


def anchor_failures(registry: dict) -> list[str]:
    """Check every conditional angle's trigger anchors against the required-field set.

    A conditional angle must have at least one REQUIRED-rooted leg, or it fails closed and
    invisibly: the predicate is false for every map that omitted the field, so the angle looks
    configured and never runs. Optional legs beside a required one only ADD firings, so they are
    legitimate and are declared separately as ``widening_legs``.

    Args:
        registry: The parsed source registry.

    Returns:
        One ``FAIL`` line per violation, empty when clean.
    """
    out: list[str] = []
    for a in registry["angles"]:
        if a["trigger"] != "conditional":
            if a.get("trigger_anchor"):
                out.append(
                    _fail(
                        "anchor-only-on-conditional",
                        f"angle {a['id']!r} is always-on but declares a trigger_anchor",
                    )
                )
            continue
        anchors = a.get("trigger_anchor") or []
        if isinstance(anchors, str):
            out.append(
                _fail(
                    "anchor-must-be-a-list",
                    f"angle {a['id']!r} declares a scalar trigger_anchor; a disjunctive predicate "
                    "has more than one leg, and naming one of them makes the assertion stop "
                    "matching the predicate it claims to check",
                )
            )
            anchors = [anchors]
        if not anchors:
            out.append(
                _fail(
                    "anchor-required",
                    f"angle {a['id']!r} is conditional with no trigger_anchor; a predicate with "
                    "no required-rooted leg fails closed for every map that omits its fields",
                )
            )
        for anchor in anchors:
            if anchor not in REQUIRED_CAPABILITY_FIELDS:
                out.append(
                    _fail(
                        "anchor-must-be-required",
                        f"angle {a['id']!r} anchors on {anchor!r}, which the capability schema "
                        "does not mark required; an optional leg belongs in widening_legs",
                    )
                )
    return out


def load_registry(path: Path | str = DEFAULT_REGISTRY) -> dict:
    """Load the master source registry.

    Args:
        path: Registry location; defaults to the copy shipped in this package.

    Returns:
        The parsed registry.
    """
    return yaml.safe_load(Path(path).read_text())


def _schema_failures(doc: dict, schema_name: str) -> list[str]:
    validator = Draft202012Validator(_load_schema(schema_name))
    out = []
    for err in sorted(validator.iter_errors(doc), key=lambda e: list(e.path)):
        where = "/".join(str(p) for p in err.path) or "<root>"
        out.append(_fail("schema", f"{where}: {err.message}"))
    return out


def record_filename(item_id: str) -> str:
    """Return the filename stem a record for ``item_id`` must be written under.

    An ``item_id`` is an IDENTITY and may legitimately contain characters a filename may not:
    a package URL carries ``/`` and ``:``, a minted ``WEB-`` id carries dots. Downstream stages
    locate a record by deriving its filename from the id, so an id written verbatim turns its
    slashes into directories: the record lands where nothing looks for it, stays perfectly
    valid so nothing reports it missing, and is treated as never written.

    Identity for anything already filename-safe, so registry-shaped ids stay readable and
    every record written before this rule stays valid. Anything else becomes a sanitized
    prefix joined to a short digest of the WHOLE id, so two ids differing only in characters
    the sanitizer collapses still get different names.

    Args:
        item_id: The record's canonical identity, verbatim.

    Returns:
        The filename stem, without extension.
    """
    if re.fullmatch(r"[A-Za-z0-9._-]+", item_id) and not _HASHED_STEM.search(item_id):
        return item_id
    prefix = re.sub(r"[^A-Za-z0-9._-]+", "-", item_id)[:_PREFIX_CAP].strip("-")
    digest = hashlib.sha256(item_id.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}--{digest}" if prefix else f"--{digest}"


# ── keyword-map ────────────────────────────────────────────────────────────────


def validate_keyword_map(doc: dict, registry: dict | None = None) -> list[str]:
    """Validate a market vocabulary map.

    Args:
        doc: The parsed map.
        registry: Source registry; defaults to this package's copy.

    Returns:
        One ``FAIL`` line per violation, empty when clean.
    """
    out = _schema_failures(doc, "market-vocabulary-map.schema.json")
    if out:
        return out

    reg = registry if registry is not None else load_registry()
    groups = doc["groups"]

    seen: set[str] = set()
    for g in groups:
        if g["id"] in seen:
            out.append(_fail("group-id-unique", f"group id {g['id']!r} appears more than once"))
        seen.add(g["id"])

    for g in groups:
        n = len(g["expansions"])
        if n > g["expansion_cap"]:
            out.append(
                _fail(
                    "expansion-cap",
                    f"group {g['id']!r} has {n} expansions, above its declared cap "
                    f"of {g['expansion_cap']}",
                )
            )
        if n < 3 and not g.get("short_reason"):
            out.append(
                _fail(
                    "expansion-floor",
                    f"group {g['id']!r} has {n} expansions and no short_reason; fold it into a "
                    "related group or record why it is short — never pad",
                )
            )
        if g["type"] in COLLISION_PRONE_TYPES and not g.get("negative_terms"):
            out.append(
                _fail(
                    "negative-terms-required",
                    f"group {g['id']!r} is type {g['type']!r} and declares no negative_terms; "
                    "category and product names collide with ordinary language, so a search "
                    "built from this group cannot be made precise",
                )
            )

    present = {g["type"] for g in groups}
    declared_absent = {a["type"] for a in doc["scope_guard"]["absent_types"]}
    for t in GROUP_TYPES:
        if t not in present and t not in declared_absent:
            out.append(
                _fail(
                    "group-type-accounted",
                    f"group type {t!r} is neither present nor recorded in scope_guard."
                    "absent_types; a silent omission empties the angle that depends on it",
                )
            )

    # Checked across the WHOLE map, not per group. A group may legitimately be uniform — every
    # expansion of one term can be `narrower`, and a system's aliases are all `alt-label` — so
    # requiring a MIXED group false-failed a map whose groups were each uniform but collectively
    # varied. What is degenerate is a map with only ONE relation kind anywhere in it.
    #
    # This deliberately does not catch a map that is mostly spelling lists with one varied group.
    # Judging whether expansions genuinely expand is semantic and belongs to the reviewing twin's
    # honestly-typed-expansions condition, not to a shape gate.
    kinds = {e["relation"] for g in groups for e in g["expansions"]}
    if len(kinds) < 2:
        only = next(iter(kinds), "none")
        out.append(
            _fail(
                "relation-variety",
                f"every expansion in the map is {only!r}; a map of a single relation kind is a "
                "spelling list, not an expansion",
            )
        )

    probe_used = any(e["provenance"] == "probe-discovered" for g in groups for e in g["expansions"])
    probe = doc.get("probe")
    if probe_used and not (probe and probe.get("performed")):
        out.append(
            _fail(
                "probe-record",
                "an expansion claims probe-discovered provenance but no performed probe is "
                "recorded; the provenance is unfalsifiable without it",
            )
        )
    if probe is not None and not probe.get("performed") and not probe.get("reason"):
        out.append(_fail("probe-record", "probe.performed is false with no reason recorded"))

    for s in doc["sources"]["active"]:
        san = s["sanitization"]
        if san["status"] != "sanitized" and not san.get("cause"):
            out.append(
                _fail(
                    "sanitization-cause",
                    f"active source {s['id']!r} records sanitization status "
                    f"{san['status']!r} with no cause",
                )
            )
        if s.get("access") == "forbidden-by-terms":
            out.append(
                _fail(
                    "forbidden-source-not-active",
                    f"source {s['id']!r} is recorded active with access 'forbidden-by-terms'; "
                    "a source excluded on its terms was never read, so listing it active is a "
                    "false receipt — move it to sources.skipped",
                )
            )

    out.extend(_angle_verdict_failures(doc, reg))
    return out


def _angle_verdict_failures(doc: dict, reg: dict) -> list[str]:
    """Check the angle verdicts in BOTH directions.

    Corroborating only that a *negative* verdict was
    justified, so a wrong *positive* ran a whole angle against a product the scope had ruled
    out — and an always-on angle switched off is how a survey silently does nothing. A
    one-directional check on a two-directional property reads as covered and is not.

    Args:
        doc: The parsed map.
        reg: The source registry.

    Returns:
        One ``FAIL`` line per violation.
    """
    out: list[str] = []
    known = {a["id"] for a in reg["angles"]}
    always_on = {a["id"] for a in reg["angles"] if a["trigger"] == "always"}
    seen_ids: set[str] = set()
    for a in doc["angle_applicability"]:
        if a["angle_id"] in seen_ids:
            out.append(
                _fail(
                    "angle-verdict-unique",
                    f"more than one applicability verdict for angle {a['angle_id']!r}; a "
                    "contradictory pair would collapse and hide whichever verdict lost",
                )
            )
        seen_ids.add(a["angle_id"])
    verdicts = {a["angle_id"]: a for a in doc["angle_applicability"]}

    for angle_id in sorted(known - set(verdicts)):
        out.append(
            _fail(
                "angle-verdict-complete",
                f"no applicability verdict for angle {angle_id!r}; an angle judged "
                "inapplicable must leave a trace",
            )
        )

    for angle_id in sorted(set(verdicts) - known):
        out.append(
            _fail(
                "angle-unknown",
                f"applicability verdict for {angle_id!r}, which is not an angle in the "
                "registry; a verdict on a non-existent angle proves nothing",
            )
        )

    for angle_id in sorted(always_on & set(verdicts)):
        if not verdicts[angle_id]["holds"]:
            out.append(
                _fail(
                    "always-on-angle-holds",
                    f"angle {angle_id!r} is trigger 'always' but its verdict is holds=false; "
                    "an always-on angle cannot be switched off by a map, and doing so is how "
                    "a survey silently does nothing",
                )
            )

    return out


# ── search output ──────────────────────────────────────────────────────────────


def _angle(reg: dict, angle_id: str) -> dict | None:
    return next((a for a in reg["angles"] if a["id"] == angle_id), None)


def _applicable_set(mapping: dict, angle: dict) -> set[tuple[str, str]]:
    """The (group, source) pairs this angle owed a cell for.

    An angle queries only the group types it declares, against only the sources that are both
    in its registry entry and ACTIVE in the vocabulary map — a source the map skipped was
    never available to it.

    Args:
        mapping: The vocabulary map.
        angle: The angle's registry entry.

    Returns:
        Every (group_id, source_id) pair the angle owed a coverage cell for.
    """
    types = set(angle["applicable_group_types"])
    groups = [g["id"] for g in mapping["groups"] if g["type"] in types]
    active = {s["id"] for s in mapping["sources"]["active"]}
    sources = [s for s in angle["sources"] if s in active]
    return {(g, s) for g in groups for s in sources}


def validate_search(doc: dict, mapping: dict, registry: dict | None = None) -> list[str]:
    """Validate one angle's search output against its map and the registry.

    Args:
        doc: The parsed search output.
        mapping: The vocabulary map this run queried from.
        registry: Source registry; defaults to this package's copy.

    Returns:
        One ``FAIL`` line per violation, empty when clean.
    """
    out = _schema_failures(doc, "search-output.schema.json")
    if out:
        return out

    # The map is a second untrusted input — an empty file, a half-written map, or
    # --keyword-map aimed at the wrong file are all first-order caller mistakes. Without this
    # the checks below dereference it raw and raise instead of reporting. The rule name is
    # distinct so a caller can tell WHICH of the two files is broken.
    map_errs = _schema_failures(mapping, "market-vocabulary-map.schema.json")
    if map_errs:
        return [_fail("keyword-map-invalid", e.split(": ", 1)[1]) for e in map_errs]

    reg = registry if registry is not None else load_registry()
    outcome = doc["outcome"]

    if outcome in ("not_run", "vacated") and outcome not in doc:
        out.append(
            _fail(
                "outcome-block-required",
                f"outcome is {outcome!r} but no {outcome!r} block records why",
            )
        )
    if outcome == "vacated":
        angle = _angle(reg, doc["meta"]["angle_id"])
        if angle is not None:
            owed = _applicable_set(mapping, angle)
            if owed:
                out.append(
                    _fail(
                        "vacated-not-empty",
                        f"outcome is 'vacated' but {len(owed)} applicable (group x source) pair(s) "
                        "exist; an angle may not vacate itself while work was owed",
                    )
                )

    if outcome != "ran":
        if doc.get("coverage"):
            out.append(
                _fail(
                    "unrun-angle-has-cells",
                    f"outcome is {outcome!r} but coverage cells are present; an angle that did "
                    "not run owes no cells, and writing them manufactures zeros that read as "
                    "searches",
                )
            )
        return out

    for key in ("coverage", "retrieval_summary", "bound"):
        if not doc.get(key):
            out.append(_fail("ran-requires-coverage", f"outcome is 'ran' but {key!r} is absent"))
    if any(o.startswith("FAIL ran-requires-coverage") for o in out):
        return out

    out.extend(_cell_failures(doc, mapping, reg))
    out.extend(_coverage_completeness_failures(doc, mapping, reg))
    out.extend(_summary_failures(doc, reg, _angle(reg, doc["meta"]["angle_id"])))
    out.extend(_bound_failures(doc, _angle(reg, doc["meta"]["angle_id"])))
    out.extend(_candidate_failures(doc))
    return out


def _coverage_completeness_failures(doc: dict, mapping: dict, reg: dict) -> list[str]:
    """Reconcile the coverage grid against the pairs this angle actually owed, BOTH ways.

    A missing cell and a surplus cell are different defects with the same root: the grid no
    longer describes the search that was run. A missing one is the serious direction — the pair
    was owed and there is no receipt, so downstream cannot tell an unsearched pair from one that
    returned nothing, which is the whole distinction this artifact exists to preserve. A surplus
    one means the angle worked outside its assignment, which duplicates a sibling and inflates
    this angle's arithmetic.

    Args:
        doc: The parsed search output.
        mapping: The vocabulary map this run queried from.
        reg: The source registry.

    Returns:
        One ``FAIL`` line per violation.
    """
    angle = _angle(reg, doc["meta"]["angle_id"])
    if angle is None:
        return [
            _fail(
                "angle-unknown",
                f"search output claims angle {doc['meta']['angle_id']!r}, which the registry "
                "does not define; its owed coverage cannot be derived",
            )
        ]

    owed = _applicable_set(mapping, angle)
    present = {(c["group_id"], c["source_id"]) for c in doc["coverage"]}
    out: list[str] = []

    for group_id, source_id in sorted(owed - present):
        out.append(
            _fail(
                "coverage-complete",
                f"no cell for applicable pair {group_id}/{source_id}; a pair the angle owed and "
                "did not record is an unexplained gap, not a zero",
            )
        )
    for group_id, source_id in sorted(present - owed):
        out.append(
            _fail(
                "cell-in-applicable-set",
                f"cell {group_id}/{source_id} is outside this angle's applicable set; working "
                "another angle's channels duplicates a sibling and inflates this angle's coverage",
            )
        )
    return out


def _cell_failures(doc: dict, mapping: dict, reg: dict) -> list[str]:
    """Per-cell shape, and that each cell names a group and source that exist."""
    out: list[str] = []
    known_groups = {g["id"] for g in mapping["groups"]}
    known_sources = set(reg["sources"])
    excluded = set(reg.get("excluded") or {})

    seen_pairs: set[tuple[str, str]] = set()
    for c in doc["coverage"]:
        pair = (c["group_id"], c["source_id"])
        if pair in seen_pairs:
            out.append(
                _fail(
                    "cell-pair-unique",
                    f"more than one cell for {pair[0]}/{pair[1]}; two records for one pair leave "
                    "no way to tell which is the receipt",
                )
            )
        seen_pairs.add(pair)

    for c in doc["coverage"]:
        where = f"{c['group_id']}/{c['source_id']}"
        if c["status"] == "reached":
            carried = sum(
                1
                for row in (doc.get("candidates") or []) + (doc.get("unadmitted") or [])
                if row.get("found_by") == where
            )
            if c.get("kept") is not None and c["kept"] != carried:
                out.append(
                    _fail(
                        "kept-matches-rows",
                        f"cell {where} declares kept={c['kept']} but {carried} candidate/"
                        "unadmitted row(s) name it; kept counts rows carried forward, and an "
                        "unreconciled count hides rows that were dropped without a record",
                    )
                )
            if c.get("returned") is None or c.get("kept") is None:
                out.append(
                    _fail(
                        "reached-needs-counts",
                        f"cell {where} is 'reached' without both returned and kept; a reached "
                        "cell with no arithmetic proves nothing",
                    )
                )
            elif c["kept"] > c["returned"]:
                out.append(
                    _fail(
                        "kept-exceeds-returned",
                        f"cell {where} kept {c['kept']} of {c['returned']} returned",
                    )
                )
        elif not c.get("cause"):
            out.append(
                _fail(
                    "status-needs-cause",
                    f"cell {where} has status {c['status']!r} with no cause; an unexplained "
                    "non-result is indistinguishable from a zero",
                )
            )

        if c["group_id"] not in known_groups:
            out.append(_fail("cell-group-known", f"cell {where} names a group absent from the map"))
        if c["source_id"] in excluded:
            out.append(
                _fail(
                    "cell-source-excluded",
                    f"cell {where} sources {c['source_id']!r}, which the registry excludes; "
                    "reaching it is a policy breach, not a coverage detail",
                )
            )
        elif c["source_id"] not in known_sources:
            out.append(
                _fail("cell-source-known", f"cell {where} names a source absent from the registry")
            )
    return out


def _summary_failures(doc: dict, reg: dict, angle: dict | None = None) -> list[str]:
    """Reconcile retrieval_summary against the cells.

    The duplication IS the check: a discrepancy between the two is the signal that a source
    failure was laundered into a zero, which is the failure mode the whole survey exists to
    prevent.
    """
    out: list[str] = []
    summary = doc["retrieval_summary"]
    known_sources = set(reg["sources"])
    excluded = set(reg.get("excluded") or {})

    tally: dict[str, int] = {}
    for c in doc["coverage"]:
        tally[c["status"]] = tally.get(c["status"], 0) + 1
    declared = {k: v for k, v in summary["status_counts"].items() if v}
    if declared != {k: v for k, v in tally.items() if v}:
        out.append(
            _fail(
                "summary-reconciles",
                f"retrieval_summary.status_counts {declared} does not match the cells {tally}",
            )
        )

    for d in summary["degraded_sources"]:
        fb = d.get("fallback_used")
        if not fb:
            continue
        if fb in excluded:
            out.append(
                _fail(
                    "cell-source-excluded",
                    f"fallback_used names {fb!r}, which the registry excludes; substituting an "
                    "excluded source is the same policy breach as querying it directly",
                )
            )
        elif fb not in known_sources:
            out.append(
                _fail("cell-source-known", f"fallback_used names {fb!r}, absent from the registry")
            )
        elif angle is not None and fb != angle.get("fallback"):
            out.append(
                _fail(
                    "fallback-declared",
                    f"fallback_used is {fb!r} but angle {angle['id']!r} declares "
                    f"{angle.get('fallback')!r}; the substitution belongs to the registry",
                )
            )

    degraded_declared = {d["source_id"] for d in summary["degraded_sources"]}
    degraded_actual = {c["source_id"] for c in doc["coverage"] if c["status"] != "reached"}
    for src in sorted(degraded_actual - degraded_declared):
        out.append(
            _fail(
                "degraded-source-recorded",
                f"source {src!r} has a non-reached cell but is absent from "
                "retrieval_summary.degraded_sources",
            )
        )
    return out


def _bound_failures(doc: dict, angle: dict | None = None) -> list[str]:
    """The per-angle search limit: that it matches the registry, and that a hit is described.

    The cap is the registry's to declare, not the output's to choose. Reading it from the
    artifact would let a run quietly raise its own ceiling (making the limit meaningless) or
    quietly lower it (truncating coverage while looking compliant) — so both directions are
    checked against the registry rather than trusted.

    Args:
        doc: The parsed search output.
        angle: The angle's registry entry; when absent the registry comparison is skipped.

    Returns:
        One ``FAIL`` line per violation.
    """
    out: list[str] = []
    bound = doc["bound"]

    if angle is not None and bound["cap"] != angle["cap"]:
        out.append(
            _fail(
                "cap-matches-registry",
                f"bound.cap is {bound['cap']} but angle {angle['id']!r} declares {angle['cap']}; "
                "the cap belongs to the registry, where it is sized against the corpus this "
                "angle walks",
            )
        )

    if bound["hit"] and not bound.get("dropped_note"):
        out.append(
            _fail(
                "bound-hit-needs-note",
                "bound.hit is true with no dropped_note; a cap that bound and is not described "
                "reads downstream as exhaustive coverage",
            )
        )

    n = len(doc.get("candidates") or [])
    if n > bound["cap"]:
        out.append(
            _fail(
                "cap-respected", f"{n} candidates carried against a declared cap of {bound['cap']}"
            )
        )
    if bound["hit"] and n < bound["cap"]:
        out.append(
            _fail(
                "bound-hit-consistent",
                f"bound.hit is true but only {n} of {bound['cap']} candidates were carried; a "
                "limit that did not bind must not be recorded as though it had",
            )
        )
    return out


_REGISTRY_SHAPED = re.compile(r"^(WD-Q\d+|APPLE-\d+|STEAM-\d+|pkg:)")


def _candidate_failures(doc: dict) -> list[str]:
    """Candidate identity, provenance, and the L-8a admission rule."""
    out: list[str] = []
    cells = {f"{c['group_id']}/{c['source_id']}" for c in doc["coverage"]}

    seen: set[str] = set()
    for cand in doc.get("candidates") or []:
        cid = cand["id"]
        if cid in seen:
            out.append(_fail("candidate-id-unique", f"candidate id {cid!r} appears more than once"))
        seen.add(cid)

        if cand["id_class"] == "web":
            if not cand.get("url"):
                out.append(_fail("web-id-needs-url", f"candidate {cid!r} is web-class with no url"))
            if _REGISTRY_SHAPED.match(cid):
                out.append(
                    _fail(
                        "id-class-shape",
                        f"candidate {cid!r} is web-class but carries a registry-shaped id; "
                        "inventing a registry id for an item that has none is the defect the "
                        "minted WEB- form exists to prevent",
                    )
                )
        elif not _REGISTRY_SHAPED.match(cid):
            out.append(
                _fail(
                    "id-class-shape",
                    f"candidate {cid!r} is {cand['id_class']!r} but its id is not registry-shaped",
                )
            )

        if cand["found_by"] not in cells:
            out.append(
                _fail(
                    "candidate-provenance",
                    f"candidate {cid!r} claims found_by {cand['found_by']!r}, which is not a "
                    "cell in this angle's coverage",
                )
            )

        adm = cand["admission"]
        if adm["basis"] == "corroborated":
            angles = adm.get("corroborating_angles") or []
            if len(set(angles)) < 2:
                out.append(
                    _fail(
                        "admission-corroboration",
                        f"candidate {cid!r} is admitted as corroborated but names "
                        f"{len(set(angles))} independent angle(s); the rule needs two",
                    )
                )
        elif not adm.get("capability_stated"):
            out.append(
                _fail(
                    "admission-first-party",
                    f"candidate {cid!r} is admitted on a first-party site that states no "
                    "capability; a site that resolves but claims nothing relevant is not evidence",
                )
            )
    return out



# ── extract record ─────────────────────────────────────────────────────────────

#: Body sections every EXTRACTED record must carry. The frontmatter holds the machine fields;
#: these hold what a human reads and what synthesis quotes.
EXTRACT_HEADINGS = ("Positioning", "Evidence", "Overlap")


def _load_frontmatter(path: Path) -> tuple[dict | None, str | None, list[str]]:
    """Split a record's leading YAML frontmatter from its markdown body.

    A missing file or a malformed block is an INPUT fault, not an artifact rule violation.

    Args:
        path: The record path.

    Returns:
        ``(frontmatter, body, failures)``; the first two are ``None`` when unreadable.
    """
    try:
        text = path.read_text()
    except OSError as exc:
        return None, None, [_fail("input", f"{path}: {exc.strerror or exc}")]
    except UnicodeDecodeError as exc:
        return None, None, [_fail("input", f"{path}: not valid UTF-8 text: {exc}")]
    if not text.lstrip().startswith("---"):
        return None, None, [_fail("no-frontmatter", f"{path}: must open with a frontmatter block")]
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, None, [_fail("no-frontmatter", f"{path}: unterminated frontmatter block")]
    try:
        fm = yaml.safe_load(parts[1])
    except yaml.YAMLError as exc:
        return None, None, [_fail("input", f"{path}: frontmatter is not valid YAML: {exc}")]
    if not isinstance(fm, dict):
        return None, None, [_fail("not-a-mapping", f"{path}: frontmatter must be a mapping")]
    return fm, parts[2], []


def validate_extract(path: Path | str) -> list[str]:
    """Validate one extract record — shape and completeness only.

    Whether a tier is argued well, whether the positioning is the vendor's own claim rather than
    the extractor's endorsement of it, and whether the overlap reasoning holds are the reviewing
    twin's conditions. This gate checks the schema, then the two things a schema cannot express:
    that a skip carries a substantive cause, and that the body has the sections synthesis quotes.

    Args:
        path: The record path (``.md`` with YAML frontmatter).

    Returns:
        One ``FAIL <rule>: ...`` line per violation; empty when clean.
    """
    path = Path(path)
    fm, body, out = _load_frontmatter(path)
    if fm is None:
        return out
    out += _schema_failures(fm, "extract-output.schema.json")
    if out:
        return out
    # The filename rule (record_filename(item_id) + .md) is the QA PHASE's check, not this
    # gate's — 5a puts it there and playbook #45 forbids diverging.

    if fm.get("outcome") == "skipped":
        detail = str((fm.get("skipped") or {}).get("detail", "")).strip()
        if len(detail) < 10:
            out.append(
                _fail(
                    "skip-detail",
                    "a skipped record must say WHY in its own terms; a bare cause code is a "
                    "verdict without evidence",
                )
            )
        return out

    for heading in EXTRACT_HEADINGS:
        if f"## {heading}" not in (body or ""):
            out.append(_fail("missing-heading", f"the record body is missing '## {heading}'"))
    return out


# ── competitor register (synthesis) ────────────────────────────────────────────


def _queue_coverage(queue: Path, extracts: Path, expected_count) -> list[str]:
    """Reconcile the FROZEN queue against the extract directory.

    The third direction. `row-without-record` checks register -> file and `record-without-row`
    checks file -> register, so a queue row that produced NO file is invisible to both: a bail
    that wrote nothing deflates the survey, and a mis-named stray inflates `extract_count`
    (taken from a directory listing), with the gate reporting neither. A live run shipped a
    register at exit 0 with 5 of 49 rows uncovered.

    Args:
        queue: The frozen ``extract-queue.yaml``.
        extracts: The directory the records were written to.
        expected_count: ``meta.extract_count`` from the register, or None.

    Returns:
        Failure lines; empty when every queue row has its record.
    """
    out: list[str] = []
    if not queue.is_file():
        return [
            _fail(
                "queue-unreadable",
                f"--queue {queue} is not a file (resolved from {Path.cwd()}) — a broken "
                "invocation, not an absence of evidence; correct the path and re-run",
            )
        ]
    try:
        doc = yaml.safe_load(queue.read_text()) or {}
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        return [_fail("queue-unreadable", f"--queue {queue}: {exc}")]

    rows = doc.get("queue") or []
    present = {p.name for p in extracts.glob("*.md")}
    for row in rows:
        item = row.get("item_id")
        if not item:
            continue
        want = f"{record_filename(item)}.md"
        if want not in present:
            out.append(
                _fail(
                    "queue-row-without-record",
                    f"queue row {item!r} has no record at {want!r} in {extracts} — the "
                    "extraction produced nothing for it, and a comment is not a substitute; "
                    "a bail still writes a skip record",
                )
            )
    if expected_count is not None and rows and expected_count != len(rows):
        out.append(
            _fail(
                "extract-count-vs-queue",
                f"meta.extract_count is {expected_count} but the frozen queue holds "
                f"{len(rows)} row(s) — the count is taken from a directory listing, so a "
                "stray file inflates it; the queue is the denominator",
            )
        )
    return out


def validate_synthesis(doc: dict, extracts: Path | None = None) -> list[str]:
    """Validate the competitor register — shape, arithmetic, and traceability to records.

    ``extracts`` is OPTIONAL because the register is also read on its own, but omitting it SKIPS
    the cross-check rather than passing it: a sibling type shipped a check that silently no-opped
    without its directory and hid a real gap for four runs.

    Args:
        doc: The parsed register.
        extracts: The request's ``extract/`` directory, or ``None`` to skip the cross-check.

    Returns:
        One ``FAIL <rule>: ...`` line per violation; empty when clean.
    """
    out = _schema_failures(doc, "competitor-register.schema.json")
    if out:
        return out

    rows = doc.get("competitors") or []
    ids = [r.get("id") for r in rows]
    for dupe in sorted({i for i in ids if ids.count(i) > 1}):
        out.append(_fail("id-unique", f"product id {dupe!r} appears more than once"))

    receipt = doc.get("coverage_receipt") or {}
    for angle in receipt.get("angles") or []:
        if angle.get("outcome") != "ran" and not str(angle.get("cause", "")).strip():
            out.append(
                _fail(
                    "absence-cause",
                    f"angle {angle.get('angle_id')!r} is {angle.get('outcome')!r} with no cause "
                    "— an angle that produced nothing must say why, or it reads as a zero hit",
                )
            )

    if extracts is None:
        print("SKIP extracts-crosscheck: pass --extracts <dir> to reconcile rows against records")
        return out

    # A supplied-but-unusable directory is a broken invocation, not an absence of evidence.
    # Path.glob returns [] for a missing directory rather than raising, so without these two
    # branches a bad path, an empty one and a genuine mismatch all arrive as the same per-row
    # failure — which blames the author, and whose cheapest route to the exit 0 the brief asks
    # for is deleting the citations. One cause, one message, and the row checks do not run.
    directory = Path(extracts)
    if not directory.is_dir():
        out.append(
            _fail(
                "extracts-unreadable",
                f"--extracts {extracts} is not a directory (resolved from {Path.cwd()}) — "
                "this is a broken invocation, not an absence of evidence; correct the path "
                "and re-run, and do NOT remove the register's citations to reach exit 0",
            )
        )
        return out

    present = {p.name for p in directory.glob("*.md")}
    cited_rows = sum(1 for row in rows if row.get("record"))
    if not present and cited_rows:
        out.append(
            _fail(
                "extracts-empty",
                f"--extracts {extracts} resolved but holds no extract records, while "
                f"{cited_rows} row(s) cite one — the extract wave produced nothing, or it "
                "wrote somewhere else; either way the rows are not the defect",
            )
        )
        return out
    for row in rows:
        if row.get("record") and row["record"] not in present:
            out.append(
                _fail(
                    "row-without-record",
                    f"{row.get('id')!r} cites record {row['record']!r}, which is not in "
                    f"{extracts} — a row with no record behind it is a claim with no evidence",
                )
            )

    cited = {row.get("record") for row in rows if row.get("record")}
    for orphan in sorted(present - cited):
        # A SKIPPED record legitimately has no row — the bail is counted in the coverage receipt,
        # not carried as a finding. Flagging it would punish the survey for recording an unread
        # source, which is the behaviour #20 exists to require.
        try:
            head = (Path(extracts) / orphan).read_text().split("---", 2)[1]
        except (OSError, IndexError):
            head = ""
        if "outcome: skipped" in head:
            continue
        out.append(
            _fail(
                "record-without-row",
                f"{orphan} is in {extracts} but no register row cites it and it is not a recorded "
                "skip — the mirror of row-without-record. A record left behind by a rename is "
                "indistinguishable from a real one, and it inflates every count taken from the "
                "directory",
            )
        )

    counted = (doc.get("meta") or {}).get("extract_count")
    if counted is not None and counted != len(present):
        out.append(
            _fail(
                "extract-count",
                f"meta.extract_count is {counted} but {len(present)} record(s) are on disk",
            )
        )
    return out


def main(argv: list[str] | None = None) -> int:
    """Run the gate.

    Args:
        argv: Argument vector; defaults to ``sys.argv[1:]``.

    Returns:
        Process exit status — 0 clean, 1 when a check failed, 2 when an input
        could not be read at all.
    """
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    p_map = sub.add_parser("keyword-map", help="validate a market vocabulary map")
    p_map.add_argument("file", type=Path)

    p_extract = sub.add_parser("extract", help="validate one extract record")
    p_extract.add_argument("file", type=Path)

    p_syn = sub.add_parser("synthesis", help="validate the competitor register")
    p_syn.add_argument("file", type=Path)
    p_syn.add_argument("--extracts", dest="extracts", type=Path, default=None)
    p_syn.add_argument("--queue", dest="queue", type=Path, default=None)

    p_search = sub.add_parser("search", help="validate one angle's search output")
    p_search.add_argument("file", type=Path)
    p_search.add_argument("--keyword-map", dest="mapping", type=Path, required=True)

    args = p.parse_args(argv)

    def _read(path: Path):
        """Load one YAML input, or report why it could not be read.

        A missing path and a syntax error are INPUT faults, not artifact faults. Reporting
        them as rule violations would tell a caller to edit an artifact that may be fine.
        """
        try:
            return yaml.safe_load(path.read_text()), None
        except OSError as exc:
            return None, _fail("input", f"{path}: {exc.strerror or exc}")
        except yaml.YAMLError as exc:
            return None, _fail("input", f"{path}: not valid YAML: {exc}")

    # The registry ships INSIDE this package, so a defect in it is a package fault rather than
    # a fault in the artifact under test. Reporting it at exit 1 would send a caller off to edit
    # a map that may be perfectly fine, so it exits 2 with the could-not-be-used class — and it
    # runs before either subcommand touches its input, not on one path only.
    reg_errs = anchor_failures(load_registry())
    if reg_errs:
        for line in reg_errs:
            print(line)
        return 2

    doc, err = _read(args.file)
    if err:
        print(err)
        return 2

    if args.cmd == "extract":
        failures = validate_extract(args.file)
        for line in failures:
            print(line)
        return 1 if failures else 0

    if args.cmd == "keyword-map":
        failures = validate_keyword_map(doc)
    elif args.cmd == "search":
        mapping, err = _read(args.mapping)
        if err:
            print(err)
            return 2
        failures = validate_search(doc, mapping)
    elif args.cmd == "synthesis":
        failures = validate_synthesis(doc, args.extracts)
        if args.queue and args.extracts:
            failures = failures + _queue_coverage(
                Path(args.queue), Path(args.extracts),
                (doc.get("meta") or {}).get("extract_count"),
            )
        elif not args.queue:
            print(
                "SKIP queue-coverage: pass --queue <extract-queue.yaml> to reconcile the "
                "frozen queue against the records on disk"
            )
    else:  # pragma: no cover - argparse rejects anything else
        raise AssertionError(args.cmd)

    for line in failures:
        print(line)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
