"""Deterministic gate for the ML prior-art survey (wave 1).

Two kinds: the ML task vocabulary map, and one angle's search output.

Exit codes, and the distinction is load-bearing:
  0  clean
  1  the ARTIFACT has findings — the author has something to fix
  2  it could not be used at all — a fault in the package, the registry, the invocation or the
     input file. Never the author's to fix by editing the artifact, which is why reporting one of
     these as a 1 sends someone off to edit a file that is fine.

Every finding is one line, ``FAIL <rule-id>: <message>``, so a caller can grep the rule.

This gate checks SHAPE. Whether a query could be re-run, whether a cause carries observable
evidence, whether an authority ranking is defensible — those are the reviewing twin's, and each of
its conditions names the rule that owns the other half.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

try:
    import yaml
    from jsonschema import Draft202012Validator
except ModuleNotFoundError as exc:  # pragma: no cover — exercised through a subprocess
    # A missing dependency is a PACKAGE fault. An unguarded import reports it as exit 1 with a
    # traceback: the code that means "your artifact has findings", with no FAIL line to grep. The
    # guard must also be NON-RAISING — the shared root guard `exec_module`s this file, and a
    # raising import turns that test into an ERROR rather than a run.
    _MISSING_DEPENDENCY: str | None = exc.name
    yaml = None  # type: ignore[assignment]
    Draft202012Validator = None  # type: ignore[assignment]
else:
    _MISSING_DEPENDENCY = None

HERE = Path(__file__).resolve().parent
SCHEMAS = HERE.parent / "schemas"
REGISTRY = HERE.parent / "references" / "source-registry.yaml"

#: The classification leaves a conditional angle's `trigger_anchor` may root on. An anchor on an
#: OPTIONAL field fails closed for every map that omits it, which is silent and total.
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
    "business.platform.type",
)

_PREFIX_CAP = 80

#: The marker the hashing branch appends. The identity branch must never return a string that
#: looks like one, or the two branches share an output namespace and injectivity is lost.
_HASHED_STEM = re.compile(r"--[0-9a-f]{12}$")

#: `huggingface_hub`'s own repo-id grammar: at most one `/`, and the segments reject `--` and `..`
#: and a trailing `.git`. Checked here because `HF-`/`HFD-` ids are the common case in this type.
_HF_BODY = re.compile(r"^(?:[\w.-]+/)?[\w.-]{1,96}$")


def _fail(rule: str, message: str) -> str:
    """One finding, in the one format a caller greps."""
    return f"FAIL {rule}: {message}"


def _term_key(term: object) -> str:
    """Fold a vocabulary term to the form two groups would collide on.

    `LEDGAR` and ` ledgar ` reach the same corpus, so matching on the literal string would let a
    term be sited twice by changing its case.
    """
    return " ".join(str(term).split()).casefold() if isinstance(term, str) else ""


def record_filename(item_id: str) -> str:
    """Return the filename stem a record for ``item_id`` must be written under.

    An ``item_id`` is an IDENTITY and may legitimately contain characters a filename may not.
    This type is the MOST exposed of the ten: `HF-`, `HFD-` and `DOI-` ids essentially always
    carry a `/`, so the sanitizing branch is the COMMON case rather than the rare one and there is
    no version of this type in which part (b) looks optional.

    Identity for anything already filename-safe AND not already looking like a hashed stem;
    otherwise a sanitized prefix joined to a short digest of the WHOLE id.

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


def load_registry(path: Path | None = None) -> object:
    """Load this package's own source registry."""
    return yaml.safe_load((path or REGISTRY).read_text(encoding="utf-8"))


def _schema_errors(doc: object, name: str) -> list[str]:
    schema = json.loads((SCHEMAS / f"{name}.schema.json").read_text(encoding="utf-8"))
    out: list[str] = []
    for err in sorted(
        Draft202012Validator(schema).iter_errors(doc),
        key=lambda e: [str(p) for p in e.path],
    ):
        where = "/".join(str(p) for p in err.path) or "<root>"
        out.append(_fail("schema", f"{where}: {err.message}"))
    return out


def anchor_failures(registry: object) -> list[str]:
    """The registry's own integrity — a PACKAGE fault, checked before any artifact is read."""
    out: list[str] = []
    if not isinstance(registry, dict):
        return [
            _fail(
                "not-a-mapping",
                f"the shipped registry parsed as {type(registry).__name__}, not a mapping",
            )
        ]
    angles = registry.get("angles") or []
    if not isinstance(angles, list):
        return [_fail("not-a-mapping", f"registry `angles` is {type(angles).__name__}, not a list")]
    for angle in angles:
        if not isinstance(angle, dict):
            out.append(
                _fail(
                    "not-a-mapping",
                    f"registry angle entry is {type(angle).__name__}, not a mapping; the shape "
                    "guard stopped one level too shallow and this crashed at exit 1",
                )
            )
            continue
        aid = angle.get("id", "?")
        trigger = angle.get("trigger")
        if trigger not in ("always", "conditional"):
            out.append(
                _fail(
                    "trigger-must-be-known",
                    f"angle {aid!r} declares trigger {trigger!r}; a value outside "
                    "{always, conditional} reads as always-on to every check below, so a typo "
                    "disables the anchor rules and they fail OPEN",
                )
            )
            continue
        anchors = angle.get("trigger_anchor")
        if trigger == "always":
            if anchors:
                out.append(
                    _fail(
                        "anchor-only-on-conditional",
                        f"angle {aid!r} is always-on but declares a trigger_anchor",
                    )
                )
            continue
        if not anchors:
            out.append(
                _fail(
                    "anchor-required",
                    f"angle {aid!r} is conditional with no trigger_anchor; a predicate with no "
                    "required-rooted leg fails closed for every map that omits its fields",
                )
            )
            continue
        if not isinstance(anchors, list):
            out.append(
                _fail(
                    "anchor-must-be-a-list",
                    f"angle {aid!r} anchor is a scalar; a scalar cannot describe a disjunctive "
                    "predicate",
                )
            )
            continue
        for anchor in anchors:
            if anchor not in REQUIRED_CAPABILITY_FIELDS:
                out.append(
                    _fail(
                        "anchor-must-be-required",
                        f"angle {aid!r} anchors on {anchor!r}, which the capability schema does "
                        "not mark required. An optional leg cannot root a predicate: every map "
                        "that omits the field fails the angle closed. Root on a required field "
                        "and express the optional leg as a further disjunct of `predicate`",
                    )
                )
    return out


# ── the vocabulary map ────────────────────────────────────────────────────────


def validate_keyword_map(doc: object, registry: object | None = None) -> list[str]:
    """Shape of the ML task vocabulary map.

    Args:
        doc: The parsed map.
        registry: Source registry; defaults to this package's copy.

    Returns:
        One ``FAIL`` line per violation, empty when clean.
    """
    reg = registry if registry is not None else load_registry()
    if not isinstance(reg, dict):
        return [_fail("not-a-mapping", f"registry is {type(reg).__name__}, not a mapping")]
    out = _schema_errors(doc, "ml-task-vocabulary-map")
    if out or not isinstance(doc, dict):
        return out or [_fail("schema", "<root>: not a mapping")]

    groups = doc.get("groups") or []
    ids = [g.get("id") for g in groups]
    for dup in sorted({i for i in ids if ids.count(i) > 1}):
        out.append(
            _fail(
                "group-id-unique",
                f"group id {dup!r} is minted {ids.count(dup)} times; the point of minting once is "
                "that an id resolves to one group, and two rows for one id is the dedupe break "
                "this map exists to prevent, from the inside",
            )
        )

    declared_types = {g.get("type") for g in groups}
    absent = set(doc.get("scope_guard", {}).get("absent_types") or [])
    searched: set[str] = set()
    for angle in reg.get("angles") or []:
        searched |= set(angle.get("applicable_group_types") or [])
    for t in sorted(searched - declared_types - absent):
        out.append(
            _fail(
                "group-type-accounted",
                f"no group carries type {t!r} and `scope_guard.absent_types` does not list it; an "
                "axis an angle searches must either be populated or declared empty, because an "
                "unaccounted axis is indistinguishable from one nobody thought about",
            )
        )
    for t in sorted(absent & declared_types):
        out.append(
            _fail(
                "group-type-accounted",
                f"type {t!r} is declared absent AND carries groups; the two readings cannot both "
                "hold and a reader takes whichever it meets first",
            )
        )

    for g in groups:
        gid, cap = g.get("id"), g.get("expansion_cap")
        exps = g.get("expansions") or []
        if cap is not None and len(exps) > cap:
            out.append(
                _fail(
                    "expansion-cap",
                    f"group {gid!r} carries {len(exps)} expansions against its own cap of {cap}; "
                    "an unbounded expansion set turns one query into an unreviewable sweep",
                )
            )
        if g.get("type") in ("ml-task", "domain-term", "method") and not exps:
            out.append(
                _fail(
                    "expansion-floor",
                    f"group {gid!r} is a {g.get('type')} group with no expansions; vendors and "
                    "domains name one thing several ways, and a single-term query on this axis "
                    "reaches only the corpus that already uses your word",
                )
            )
        if g.get("type") == "ml-task" and not g.get("borrowed_from"):
            out.append(
                _fail(
                    "borrowed-vocabulary-unmarked",
                    f"group {gid!r} is an ml-task group whose `canonical` is a HuggingFace "
                    "pipeline_tag and does not say so; a borrowed name that is not marked as "
                    "borrowed reads as ours, and then nobody re-checks it when the upstream "
                    "vocabulary moves",
                )
            )
        if g.get("type") == "domain-term" and not (g.get("negative_terms") or []):
            out.append(
                _fail(
                    "negative-terms-required",
                    f"group {gid!r} is a domain-term group with no negative_terms; domain words "
                    "are where the homonyms are, and a term with no exclusions returns another "
                    "field's corpus as though it were yours",
                )
            )

    declared = {
        _term_key(d.get("term")): d
        for d in ((doc.get("scope_guard") or {}).get("shared_terms") or [])
        if isinstance(d, dict)
    }
    sited: dict[str, set[str]] = {}
    for g in groups:
        gid = g.get("id")
        for term in [g.get("canonical"), *(g.get("expansions") or [])]:
            key = _term_key(term)
            if key and gid:
                sited.setdefault(key, set()).add(gid)
    for key, gids in sorted(sited.items()):
        if len(gids) < 2:
            continue
        d = declared.get(key)
        if d is None:
            out.append(
                _fail(
                    "term-sited-once",
                    f"term {key!r} is sited in {len(gids)} groups ({', '.join(sorted(gids))}) and "
                    "is not declared in scope_guard.shared_terms; it reaches two cells, item_id is "
                    "unique across the artifact, and so whatever both surface is filed under one "
                    "cell and silently missing from the other",
                )
            )
        elif d.get("owner") not in gids:
            out.append(
                _fail(
                    "term-sited-once",
                    f"term {key!r} is declared shared with owner {d.get('owner')!r}, which is not "
                    f"one of the groups it reaches ({', '.join(sorted(gids))}); a declaration that "
                    "does not resolve reads as handled and is worse than none",
                )
            )

    probe = doc.get("probe") or {}
    if not str(probe.get("note") or "").strip():
        out.append(
            _fail(
                "probe-record",
                "the probe did not run and no note says why; the probe is the cheap check that "
                "this vocabulary reaches anything at all before nine angles are dispatched "
                "against it, and skipping it silently is how a whole survey returns nothing",
            )
        )

    declared_angles = {a.get("id") for a in reg.get("angles") or []}
    always_on = {a.get("id") for a in reg.get("angles") or [] if a.get("trigger") == "always"}
    seen: set[str] = set()
    for verdict in doc.get("angle_applicability") or []:
        aid = verdict.get("angle_id")
        if aid in seen:
            out.append(
                _fail(
                    "angle-verdict-unique",
                    f"angle {aid!r} carries more than one verdict; only ABSENCE was checked "
                    "elsewhere, so two contradictory verdicts passed and a reader takes whichever "
                    "it meets first",
                )
            )
        seen.add(aid)
        if aid not in declared_angles:
            out.append(
                _fail(
                    "angle-unknown",
                    f"verdict for {aid!r}, which is not an angle in the registry; a verdict on a "
                    "non-existent angle proves nothing",
                )
            )
        if aid in always_on and verdict.get("holds") is False:
            out.append(
                _fail(
                    "always-on-angle-holds",
                    f"angle {aid!r} is ALWAYS-ON and is recorded `holds: false`; it has no "
                    "precondition to fail, so this is not a judgement about the scope — it is an "
                    "angle being dropped with no predicate behind it",
                )
            )
    for missing in sorted(declared_angles - seen):
        out.append(
            _fail(
                "angle-verdict-complete",
                f"no verdict for angle {missing!r}; an angle judged inapplicable leaves no trace "
                "anywhere and cannot be reviewed",
            )
        )

    known_sources = {s.get("id") for s in reg.get("sources") or []}
    excluded = {e.get("id") for e in reg.get("excluded") or []}
    srcs = doc.get("sources") or {}

    # Every source an APPLICABLE angle declares must be accounted for — active or skipped.
    # Without this, a source in neither list is invisible: `_owed_cells` intersects the angle's
    # sources with the map's ACTIVE set, so an angle whose sources are all unaccounted owes ZERO
    # cells and passes with an empty coverage grid. The schema said "a source missing from BOTH
    # lists is unaccounted for" and nothing enforced it.
    accounted = {r.get("id") for r in srcs.get("active") or []}
    accounted |= {r.get("id") for r in srcs.get("skipped") or []}
    holds = {
        v.get("angle_id")
        for v in doc.get("angle_applicability") or []
        if v.get("holds")
    }
    for angle in reg.get("angles") or []:
        if angle.get("id") not in holds:
            continue
        for sid in sorted(set(angle.get("sources") or []) - accounted):
            out.append(
                _fail(
                    "source-unaccounted",
                    f"angle {angle['id']!r} holds and declares source {sid!r}, which this map "
                    "records neither ACTIVE nor SKIPPED. An unaccounted source is not a neutral "
                    "omission: the owed set intersects with the active list, so the angle simply "
                    "owes no cell for it and the gap leaves no trace anywhere",
                )
            )
    for row in srcs.get("active") or []:
        sid = row.get("id")
        if sid in excluded:
            out.append(
                _fail(
                    "forbidden-source-not-active",
                    f"source {sid!r} is recorded ACTIVE and the registry EXCLUDES it; an excluded "
                    "row is excluded for a reason the map does not get to overrule",
                )
            )
        elif sid not in known_sources:
            out.append(
                _fail(
                    "source-not-in-registry",
                    f"active source {sid!r} is in no registry row",
                )
            )
        san = row.get("sanitization") or {}
        if san.get("status") != "clean" and not str(san.get("cause") or "").strip():
            out.append(
                _fail(
                    "sanitization-cause",
                    f"source {sid!r} records sanitization status {san.get('status')!r} with no "
                    "cause; every source here is a fetched third-party page, and a non-clean "
                    "status with no cause is unreviewable",
                )
            )
    return out


# ── one angle's search output ─────────────────────────────────────────────────


def _owed_cells(angle: dict, keyword_map: dict) -> set[tuple[str, str]]:
    """The (group, source) pairs this angle owes a cell for.

    DERIVED, never "every group against every source": the angle's `applicable_group_types`
    selects the groups and the angle's own source list selects the columns, intersected with what
    the map recorded ACTIVE. Without the derivation an angle owes a cell for every group in the
    map — including ones its mechanism cannot search, which is a a5 owing a cell for every
    capability no vendor serves.
    """
    types = set(angle.get("applicable_group_types") or [])
    groups = [
        g.get("id") for g in keyword_map.get("groups") or []
        if isinstance(g, dict) and g.get("type") in types and g.get("id")
    ]
    active = {s.get("id") for s in (keyword_map.get("sources") or {}).get("active") or []}
    sources = [s for s in angle.get("sources") or [] if s in active]
    return {(g, s) for g in groups for s in sources}


def validate_search(
    doc: object, keyword_map: object, registry: object | None = None
) -> list[str]:
    """Shape of one angle's search output.

    Args:
        doc: The parsed search output.
        keyword_map: The wave-0 map, whose `groups` are the ONLY place ids are minted.
        registry: Source registry; defaults to this package's copy.

    Returns:
        One ``FAIL`` line per violation, empty when clean.
    """
    reg = registry if registry is not None else load_registry()
    if not isinstance(reg, dict):
        return [_fail("not-a-mapping", f"registry is {type(reg).__name__}, not a mapping")]
    if not isinstance(keyword_map, dict):
        # A caller fault, not an artifact fault. Coercing it to {} made every candidate look
        # unminted and returned thirty findings against an artifact that is fine.
        return [
            _fail(
                "keyword-map-invalid",
                f"the keyword map is {type(keyword_map).__name__}, not a mapping; the search "
                "output cannot be judged against it and nothing here is the artifact's fault",
            )
        ]
    out = _schema_errors(doc, "search-output")
    if out or not isinstance(doc, dict):
        return out or [_fail("schema", "<root>: not a mapping")]
    kmap = keyword_map

    angle_id = (doc.get("meta") or {}).get("angle_id")
    angle = next((a for a in reg.get("angles") or [] if a.get("id") == angle_id), None)
    if angle is None:
        # EVERYTHING downstream that bounds this artifact — the owed set, the cap, the fallback —
        # is keyed on the angle. With no angle those rules simply do not run, so an artifact
        # naming `a9` passed clean with one cell and any cap it liked. The schema pattern admits
        # a6-a9 and b5-b9, so this is a one-character escape from the grid the type exists for.
        return [
            _fail(
                "angle-unknown",
                f"meta.angle_id {angle_id!r} is not an angle in the registry; every coverage and "
                "cap rule is derived from the angle, so an unknown one disables them all rather "
                "than failing one",
            )
        ]
    outcome = doc.get("outcome")
    cells = doc.get("coverage") or []
    candidates = doc.get("candidates") or []
    unadmitted = doc.get("unadmitted") or []

    if outcome == "not_run":
        if cells:
            out.append(
                _fail(
                    "unrun-angle-has-cells",
                    "an unrun angle owes NO coverage cells; empty ones manufacture zeros that "
                    "look like searches",
                )
            )
        if candidates:
            out.append(
                _fail(
                    "unrun-angle-has-candidates",
                    "an unrun angle emitted candidates; this is the same manufacture the cell rule "
                    "catches one layer up, and it is the layer synthesis actually reads",
                )
            )
    if outcome == "ran" and cells and all(
        c.get("status") == "not-attempted" for c in cells
    ):
        out.append(
            _fail(
                "ran-attempted-nothing",
                "outcome is `ran` and every cell is `not-attempted`; a run that attempted nothing "
                "is `vacated`, and recording it as `ran` claims a search that did not happen",
            )
        )
    if outcome == "ran" and not cells:
        out.append(
            _fail(
                "ran-requires-coverage",
                "outcome is `ran` with no coverage cells; a pair with no cell is an unexplained "
                "gap, not a zero",
            )
        )
    if outcome == "vacated" and candidates:
        out.append(
            _fail(
                "vacated-not-empty",
                "a vacated angle emitted candidates; vacated means there was nothing to search, "
                "and cells with their causes are what it owes instead",
            )
        )
    if outcome == "not_run" and unadmitted:
        out.append(
            _fail(
                "unrun-angle-has-candidates",
                "an unrun angle recorded unadmitted rows; it searched nothing, so there was "
                "nothing to admit or reject",
            )
        )

    known_groups = {g.get("id") for g in kmap.get("groups") or []}
    active = {s.get("id") for s in (kmap.get("sources") or {}).get("active") or []}
    known_sources = {s.get("id") for s in reg.get("sources") or []}

    seen_pairs: set[tuple[str, str]] = set()
    counts: dict[str, int] = {}
    for cell in cells:
        gid, sid = cell.get("group_id"), cell.get("source_id")
        where = f"{gid}/{sid}"
        pair = (gid, sid)
        if pair in seen_pairs:
            out.append(
                _fail(
                    "cell-pair-unique",
                    f"cell {where} appears more than once; two cells for one pair means two "
                    "different accounts of the same search and no way to tell which ran",
                )
            )
        seen_pairs.add(pair)
        if gid not in known_groups:
            out.append(
                _fail(
                    "cell-group-known",
                    f"cell {where} names group {gid!r}, which the wave-0 map does not mint",
                )
            )
        if sid not in known_sources:
            out.append(
                _fail("cell-source-known", f"cell {where} names source {sid!r}, in no registry row")
            )
        elif sid not in active:
            out.append(
                _fail(
                    "cell-source-excluded",
                    f"cell {where} searches {sid!r}, which the map did not record ACTIVE; a "
                    "source the map could not reach at wave 0 cannot have answered an angle",
                )
            )

        status = cell.get("status")
        counts[status] = counts.get(status, 0) + 1
        returned, kept = cell.get("returned"), cell.get("kept")
        if status == "reached":
            if returned is None or kept is None:
                out.append(
                    _fail(
                        "reached-needs-counts",
                        f"cell {where} is `reached` without both returned and kept; a reached "
                        "cell with no arithmetic proves nothing",
                    )
                )
            if returned and not str(cell.get("count_frame") or "").strip():
                out.append(
                    _fail(
                        "count-frame-required",
                        f"cell {where} returned {returned} with no count_frame; this corpus "
                        "yields several defensible counts for one page, and a count whose frame "
                        "is missing cannot be re-derived",
                    )
                )
            if returned is not None and kept is not None and kept > returned:
                out.append(
                    _fail(
                        "kept-exceeds-returned",
                        f"cell {where} kept {kept} of {returned} returned",
                    )
                )
        else:
            if returned is not None or kept is not None:
                out.append(
                    _fail(
                        "coverage-unreached-has-count",
                        f"cell {where} has status {status!r} and records a count; a count on an "
                        "unreached cell is a zero laundered out of a failure",
                    )
                )
            if not str(cell.get("cause") or "").strip():
                out.append(
                    _fail(
                        "status-needs-cause",
                        f"cell {where} has status {status!r} and no cause; a non-reached status "
                        "without observable evidence is unreviewable",
                    )
                )

        # An OVERRIDE: absent means the map's wave-0 posture held for this source, so absence is
        # not a gap. Present and non-clean, it owes a cause for the same reason the map's does.
        csan = cell.get("sanitization")
        if isinstance(csan, dict) and csan.get("status") != "clean":
            if not str(csan.get("cause") or "").strip():
                out.append(
                    _fail(
                        "cell-sanitization-cause",
                        f"cell {where} records sanitization status {csan.get('status')!r} with no "
                        "cause; this cell fetched a third-party page and departed from the map's "
                        "posture to say so, and a departure with no cause is unreviewable",
                    )
                )

    if angle is not None and outcome in ("ran", "vacated"):
        # `vacated` owes cells and causes — that is what distinguishes it from `not_run`. Gating
        # this on `ran` alone let a vacated angle with twelve owed pairs and zero cells pass, which
        # is `not_run` wearing a different label and no verdict behind it.
        for gid, sid in sorted(_owed_cells(angle, kmap) - seen_pairs):
            out.append(
                _fail(
                    "coverage-complete",
                    f"no cell for {gid}/{sid}, which this angle's applicable_group_types and "
                    "source list make owed; an omitted pair and a recorded zero are different "
                    "facts and only one of them is evidence",
                )
            )
        for gid, sid in sorted(seen_pairs - _owed_cells(angle, kmap)):
            if gid in known_groups and sid in active:
                out.append(
                    _fail(
                        "cell-in-applicable-set",
                        f"cell {gid}/{sid} is outside this angle's owed set; searching an axis "
                        "the angle does not declare puts one group's evidence under another "
                        "angle's mechanism",
                    )
                )

    summary = (doc.get("retrieval_summary") or {}).get("status_counts")
    if summary is not None:
        summary = {k: v for k, v in summary.items() if v}
    if summary is None and cells:
        out.append(
            _fail(
                "summary-required",
                "no retrieval_summary.status_counts; the summary duplicates the cells on purpose, "
                "so a producer that omits it loses the reconciliation with no trace",
            )
        )
    if summary is not None and summary != counts:
        out.append(
            _fail(
                "summary-reconciles",
                f"retrieval_summary.status_counts {summary} does not reconcile with the cells "
                f"{counts}; the discrepancy is the signal that a failure was laundered into a zero",
            )
        )

    # ── candidates, kept arithmetic, bound and the id grammar ─────────────────
    rows: dict[str, int] = {}
    seen_ids: set[str] = set()
    for row in candidates + unadmitted:
        key = row.get("found_by")
        rows[key] = rows.get(key, 0) + 1

    for cand in candidates:
        iid = cand.get("item_id", "")
        if iid in seen_ids:
            out.append(
                _fail(
                    "candidate-id-unique",
                    f"item_id {iid!r} appears twice; one option is one row, and a duplicate is "
                    "two accounts of the same artifact competing for the same cap slot",
                )
            )
        seen_ids.add(iid)

        prefix = iid.split("-", 1)[0] if "-" in iid else ""
        if prefix != cand.get("id_class"):
            out.append(
                _fail(
                    "id-class-shape",
                    f"item_id {iid!r} carries prefix {prefix!r} against id_class "
                    f"{cand.get('id_class')!r}; the two are the same fact recorded twice, so a "
                    "discrepancy means one of them is wrong",
                )
            )
        body = iid.split("-", 1)[1] if "-" in iid else ""
        if prefix in ("HF", "HFD"):
            if not _HF_BODY.match(body):
                out.append(
                    _fail(
                        "hub-id-grammar",
                        f"item_id {iid!r} is not a Hub repo id: at most one `/`, and no `--`, "
                        "`..` or trailing `.git`. The grammar is the Hub's, not ours, and an id "
                        "that violates it resolves to nothing",
                    )
                )
            if "--" in body or ".." in body or body.endswith(".git"):
                out.append(
                    _fail(
                        "hub-id-grammar",
                        f"item_id {iid!r} contains a sequence the Hub grammar forbids (`--`, "
                        "`..` or a trailing `.git`)",
                    )
                )
        if prefix == "BENCH" and "--" in body:
            out.append(
                _fail(
                    "bench-slug-marker",
                    f"item_id {iid!r} contains `--`, which is the reserved hashed-stem marker; a "
                    "minted slug carrying it can collide with the sanitized form of a different "
                    "id, and the record filename stops being injective",
                )
            )

        key = cand.get("found_by") or ""
        gid = key.split("/", 1)[0] if "/" in key else ""
        if gid and gid not in known_groups:
            out.append(
                _fail(
                    "candidate-group-known",
                    f"candidate {iid!r} cites cell {key!r}, whose group the map does not mint",
                )
            )
        if key and (gid, key.split("/", 1)[1]) not in seen_pairs:
            out.append(
                _fail(
                    "candidate-provenance",
                    f"candidate {iid!r} names cell {key!r}, which has no coverage cell; a "
                    "candidate that came from no recorded search has no provenance at all",
                )
            )
        ev = cand.get("evaluation")
        if ev is not None and not str(ev.get("split") or "").strip():
            out.append(
                _fail(
                    "evaluation-needs-split",
                    f"candidate {iid!r} records an evaluation with no split; a rank is a claim "
                    "under a stated evaluation, on a stated split, at a stated date, and without "
                    "all three it is not comparable to anything",
                )
            )

    for cell in cells:
        key = f"{cell.get('group_id')}/{cell.get('source_id')}"
        if cell.get("status") != "reached":
            # A non-reached cell has `kept: null` by rule, so there is no arithmetic to check —
            # but rows may still CITE it, and skipping the cell entirely let them through. A
            # producer only had to mark the cell gated and the reconciliation was not failed, it
            # was skipped: exactly the "dropped without a record" case `kept` exists to catch.
            orphans = rows.get(key, 0)
            if orphans:
                out.append(
                    _fail(
                        "rows-cite-an-unreached-cell",
                        f"{orphans} candidate/unadmitted row(s) name cell {key}, which did not "
                        f"reach its source (status {cell.get('status')!r}). A cell that returned "
                        "nothing cannot have produced a row, and no count reconciles it",
                    )
                )
            continue
        if cell.get("kept") is None:
            continue
        actual = rows.get(key, 0)
        if cell["kept"] != actual:
            out.append(
                _fail(
                    "kept-matches-rows",
                    f"cell {key} declares kept={cell['kept']} but {actual} candidate/unadmitted "
                    "row(s) name it; kept counts rows carried forward, and an unreconciled count "
                    "hides rows that were dropped without a record",
                )
            )

    for key in sorted(k for k in rows if k and (k.split("/", 1)[0], k.split("/", 1)[-1]) not in seen_pairs):
        out.append(
            _fail(
                "row-cell-unknown",
                f"a candidate or unadmitted row names cell {key!r}, which no coverage cell "
                "records; the row cannot be reconciled against anything",
            )
        )

    bound = doc.get("bound")
    if outcome == "ran" and not bound:
        out.append(
            _fail(
                "bound-required",
                "outcome is `ran` with no `bound` block; every cap rule reads it, so omitting it "
                "does not record an unbounded run — it removes the ceiling from the gate",
            )
        )
    bound = bound or {}
    if angle is not None and bound.get("cap") is not None and bound["cap"] != angle.get("cap"):
        out.append(
            _fail(
                "cap-matches-registry",
                f"bound.cap is {bound['cap']} where the registry sets {angle.get('cap')} for "
                f"angle {angle_id!r}; a run may neither raise its own ceiling nor quietly lower it",
            )
        )
    if bound.get("cap") is not None and len(candidates) > bound["cap"]:
        # Checked UNCONDITIONALLY. Gating it on `hit is False` meant `hit: true` plus a
        # dropped_note carried any number of candidates past the ceiling — a cap that announces
        # it truncated and then exceeds itself is the one shape a cap cannot take.
        out.append(
            _fail(
                "cap-respected",
                f"{len(candidates)} candidates exceed the registry cap of {bound['cap']}. With "
                "`hit: false` that denies a truncation the count proves; with `hit: true` it "
                "exceeds the ceiling it declares it stopped at",
            )
        )
    if bound.get("hit") and not str(bound.get("dropped_note") or "").strip():
        out.append(
            _fail(
                "bound-hit-needs-note",
                "the cap was HIT and records nothing about what fell out; with no dropped_note "
                "the ordering is the only evidence a truncation leaves",
            )
        )
    if bound.get("hit") is not None and not str(bound.get("ordering") or "").strip():
        out.append(
            _fail(
                "bound-hit-consistent",
                "`bound` records no ordering; an unrecorded ordering makes a truncation "
                "unreviewable, and an untruncated cap still has to say what it would have used",
            )
        )

    row_fallbacks = {
        r["id"]: r.get("fallback") for r in reg.get("sources") or [] if r.get("fallback")
    }
    for cell in cells:
        used = cell.get("fallback_used")
        if not used:
            continue
        if not used.startswith(("angle:", "row:")):
            out.append(
                _fail(
                    "fallback-declared",
                    f"fallback_used {used!r} names no level; every registry row names a fallback "
                    "and every angle names one, they differ, and a bare id cannot say which was "
                    "walked. Prefix `angle:` or `row:`",
                )
            )
            continue
        level, target = used.split(":", 1)
        if target not in {s.get("id") for s in reg.get("sources") or []}:
            out.append(
                _fail(
                    "fallback-declared",
                    f"fallback_used {used!r} resolves to no registry row",
                )
            )
            continue
        # It must be the fallback that LEVEL actually declares. Checking only that the target is
        # some registry row let a cell claim it fell back to an unrelated source — which reads as
        # a documented recovery and is a walk nothing authorised.
        expected = angle.get("fallback") if level == "angle" else row_fallbacks.get(
            cell.get("source_id")
        )
        if expected and target != expected:
            out.append(
                _fail(
                    "fallback-declared",
                    f"cell {cell.get('group_id')}/{cell.get('source_id')} records "
                    f"fallback_used {used!r}, but the {level}-level fallback declared for it is "
                    f"{expected!r}. A fallback nobody declared is an unrecorded source, not a "
                    "recovery",
                )
            )
    degraded = set((doc.get("retrieval_summary") or {}).get("degraded_sources") or [])
    for cell in cells:
        # `not-attempted` is a DELIBERATE choice with a stated reason, not a weak channel.
        # `degraded_sources` is where a reader looks for what went wrong in this run, and listing
        # a source you chose not to walk there tells them the opposite of the truth.
        if cell.get("status") in ("reached", "not-attempted"):
            continue
        if cell.get("source_id") not in degraded:
            out.append(
                _fail(
                    "degraded-source-recorded",
                    f"cell {cell.get('group_id')}/{cell.get('source_id')} did not reach its "
                    "source and the source is not in degraded_sources; the summary is where a "
                    "reader looks for which channels were weak in this run",
                )
            )
    return out


# ── CLI ───────────────────────────────────────────────────────────────────────


def _read(path: Path) -> tuple[object | None, str | None]:
    """Read one YAML input, turning every unusable-input failure into an exit-2 line.

    `UnicodeDecodeError` is caught explicitly: it is a `ValueError`, not an `OSError`, so an
    `except OSError` that looks exhaustive lets a non-UTF-8 file escape as a traceback at exit 1.
    """
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")), None
    except UnicodeDecodeError as exc:
        return None, _fail("input", f"{path}: not UTF-8 text ({exc.reason} at byte {exc.start})")
    except OSError as exc:
        return None, _fail("input", f"{path}: {exc.strerror or exc}")
    except yaml.YAMLError as exc:
        return None, _fail("input", f"{path}: not valid YAML: {exc}")


def _build_parser() -> argparse.ArgumentParser:
    """The CLI surface, separated so a test can enumerate what is REGISTERED.

    A sibling shipped two subparsers `main()` never routed; both survived a large suite because
    every test called the `validate_*` functions directly. A test deriving the subcommand list
    from THIS function cannot miss a third one added later.
    """
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    km = sub.add_parser("keyword-map", help="validate the ML task vocabulary map")
    km.add_argument("file", type=Path)
    se = sub.add_parser("search", help="validate one angle's search output")
    se.add_argument("file", type=Path)
    se.add_argument("--keyword-map", type=Path, required=True, dest="keyword_map")
    return parser


def registered_subcommands() -> set[str]:
    """Every subcommand the parser registers, for the reachability guard."""
    for action in _build_parser()._actions:
        if isinstance(action, argparse._SubParsersAction):
            return set(action.choices)
    return set()


def main(argv: list[str] | None = None) -> int:
    if _MISSING_DEPENDENCY:
        print(
            _fail(
                "dependency-missing",
                f"this validator needs {_MISSING_DEPENDENCY!r} and the interpreter running it "
                "does not have it. That is a fault in how the script was invoked, not in your "
                "artifact. Run it as: uv run --no-project --with pyyaml --with jsonschema python "
                "scripts/validate_ml_prior_art.py ...",
            )
        )
        return 2
    args = _build_parser().parse_args(argv)

    try:
        registry = load_registry()
    except (OSError, yaml.YAMLError, UnicodeDecodeError) as exc:
        print(_fail("registry-unreadable", str(exc)))
        return 2
    reg_errs = anchor_failures(registry)
    if reg_errs:
        for line in reg_errs:
            print(line)
        return 2

    doc, err = _read(args.file)
    if err:
        print(err)
        return 2

    if args.cmd == "keyword-map":
        failures = validate_keyword_map(doc, registry)
    else:
        kmap, kerr = _read(args.keyword_map)
        if kerr:
            print(kerr)
            return 2
        kmap_errs = _schema_errors(kmap, "ml-task-vocabulary-map")
        if kmap_errs:
            print(
                _fail(
                    "keyword-map-invalid",
                    f"{args.keyword_map} is not a valid vocabulary map, so the search output "
                    f"cannot be judged against it: {kmap_errs[0]}",
                )
            )
            return 2
        failures = validate_search(doc, kmap, registry)

    for line in failures:
        print(line)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
