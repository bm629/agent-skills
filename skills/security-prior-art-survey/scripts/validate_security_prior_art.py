#!/usr/bin/env python3
"""Deterministic gate for wave-1 security prior-art artifacts.

Checks SHAPE and completeness only — schema, enums, ranges, required fields, and arithmetic
that reconciles two records against each other. It never judges whether a finding matters,
whether a bail was honest, or whether a relevance line is persuasive; those are the reviewing
skill's numbered conditions. A fuzzy heuristic inside a deterministic gate produces false
failures and duplicates the reviewer, so resist making this smarter.

Usage:
    validate_security_prior_art.py keyword-map <file>
    validate_security_prior_art.py search <file> --keyword-map <file>

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
    "weakness",
    "attack-pattern",
    "control",
    "component",
    "vendor-product",
    "domain-incident",
)


def _fail(rule: str, detail: str) -> str:
    return f"FAIL {rule}: {detail}"


def _load_schema(name: str) -> dict:
    return json.loads((SCHEMAS / name).read_text())


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


# ── keyword-map ────────────────────────────────────────────────────────────────


def validate_keyword_map(doc: dict, registry: dict | None = None) -> list[str]:
    """Validate a threat-vocabulary map.

    Args:
        doc: The parsed map.
        registry: Source registry; defaults to this package's copy.

    Returns:
        One ``FAIL`` line per violation, empty when clean.
    """
    out = _schema_failures(doc, "threat-vocabulary-map.schema.json")
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

    verdicts = {a["angle_id"] for a in doc["angle_applicability"]}
    for angle in reg["angles"]:
        if angle["id"] not in verdicts:
            out.append(
                _fail(
                    "angle-verdict-complete",
                    f"no applicability verdict for angle {angle['id']!r}; an angle judged "
                    "inapplicable must leave a trace",
                )
            )

    return out


# ── search output ──────────────────────────────────────────────────────────────


def _applicable_set(mapping: dict, angle: dict) -> set[tuple[str, str]]:
    types = set(angle["applicable_group_types"])
    groups = [g["id"] for g in mapping["groups"] if g["type"] in types]
    active = {s["id"] for s in mapping["sources"]["active"]}
    sources = [s for s in angle["sources"] if s in active]
    return {(g, s) for g in groups for s in sources}


def _vocabulary(mapping: dict, group_id: str) -> tuple[str, list[str]]:
    for g in mapping["groups"]:
        if g["id"] == group_id:
            return g["canonical"], [e["term"] for e in g["expansions"]]
    return "", []


def validate_search(doc: dict, mapping: dict, registry: dict) -> list[str]:
    """Validate one angle's search output against its map and the registry.

    Args:
        doc: The parsed search output.
        mapping: The threat-vocabulary map it ran against.
        registry: The master source registry.

    Returns:
        One ``FAIL`` line per violation, empty when clean.
    """
    out = _schema_failures(doc, "search-output.schema.json")
    if out:
        return out

    angle_id = doc["meta"]["angle_id"]
    angle = next((a for a in registry["angles"] if a["id"] == angle_id), None)
    if angle is None:
        return [_fail("angle-known", f"angle {angle_id!r} is not in the source registry")]

    # An angle that did not run owes no coverage. That constraint is the SCHEMA's — its
    # if/then/not forbids `coverage` and `candidates` on a `not_run` or `vacated` outcome, and
    # this function returns early on any schema failure. A rule here could therefore never fire,
    # so it is not written: a check the schema short-circuits is dead code that reads as a
    # guarantee. `test_schema_owns_the_not_run_no_coverage_constraint` pins the ownership.
    if doc["outcome"] != "ran":
        return out

    cells = doc["coverage"]
    applicable = _applicable_set(mapping, angle)
    recorded = {(c["group_id"], c["source_id"]) for c in cells}

    for pair in sorted(applicable - recorded):
        out.append(_fail("coverage-complete", f"no cell for applicable pair {pair[0]}/{pair[1]}"))
    for pair in sorted(recorded - applicable):
        out.append(
            _fail(
                "cell-in-applicable-set",
                f"cell {pair[0]}/{pair[1]} is outside this angle's applicable set",
            )
        )

    dropped_by_cell: dict[tuple[str, str], int] = {}
    for d in doc["bound"]["dropped"]:
        key = (d["cell"]["group_id"], d["cell"]["source_id"])
        dropped_by_cell[key] = dropped_by_cell.get(key, 0) + 1

    for c in cells:
        key = (c["group_id"], c["source_id"])
        canonical, expansions = _vocabulary(mapping, c["group_id"])
        vocab = [t.lower() for t in [canonical, *expansions] if t]

        for q in c["queries"]:
            if not any(t in q.lower() for t in vocab):
                out.append(
                    _fail(
                        "query-provenance",
                        f"cell {key[0]}/{key[1]} ran {q!r}, which uses none of its group's "
                        "vocabulary; the map is the sole source of query terms",
                    )
                )
        if canonical and not any(canonical.lower() in q.lower() for q in c["queries"]):
            out.append(
                _fail(
                    "broad-pass",
                    f"cell {key[0]}/{key[1]} has no broad pass over its canonical term; an "
                    "angle of hyper-narrow queries returns honest zeros having covered nothing",
                )
            )

        if c["status"] == "reached":
            if c["kept"] > c["returned"]:
                out.append(
                    _fail(
                        "kept-le-returned",
                        f"cell {key[0]}/{key[1]} kept {c['kept']} of {c['returned']} returned",
                    )
                )
            elif c["kept"] < c["returned"]:
                gap = c["returned"] - c["kept"]
                if dropped_by_cell.get(key, 0) != gap:
                    out.append(
                        _fail(
                            "silent-relevance-cut",
                            f"cell {key[0]}/{key[1]} kept {c['kept']} of {c['returned']} but the "
                            f"drop record accounts for {dropped_by_cell.get(key, 0)}; this wave "
                            "applies no relevance cut",
                        )
                    )

    degraded_actual = {c["source_id"] for c in cells if c["status"] != "reached"}
    degraded_claimed = {d["source_id"] for d in doc["retrieval_summary"]["degraded_sources"]}
    if degraded_actual != degraded_claimed:
        out.append(
            _fail(
                "summary-reconciles",
                f"retrieval summary lists {sorted(degraded_claimed)} as degraded but the cells "
                f"say {sorted(degraded_actual)}; the two records must agree",
            )
        )

    counts: dict[str, int] = {}
    for c in cells:
        counts[c["status"]] = counts.get(c["status"], 0) + 1
    if counts != doc["retrieval_summary"]["status_counts"]:
        out.append(
            _fail(
                "status-counts",
                f"status_counts says {doc['retrieval_summary']['status_counts']} but the cells "
                f"are {counts}",
            )
        )

    by_cell = {(c["group_id"], c["source_id"]): c for c in cells}
    refs: dict[tuple[str, str], int] = {}
    for cand in doc["candidates"]:
        for fb in cand["found_by"]:
            key = (fb["group_id"], fb["source_id"])
            cell = by_cell.get(key)
            if cell is None:
                out.append(
                    _fail(
                        "found-by-resolves",
                        f"candidate {cand['id']!r} claims cell {key[0]}/{key[1]}, which has no "
                        "coverage record",
                    )
                )
                continue
            if fb["query"] not in cell["queries"]:
                out.append(
                    _fail(
                        "found-by-query",
                        f"candidate {cand['id']!r} claims query {fb['query']!r} in cell "
                        f"{key[0]}/{key[1]}, which never ran it",
                    )
                )
            refs[key] = refs.get(key, 0) + 1

        idc, cid = cand["id_class"], cand["id"]
        if idc == "registry" and not _looks_registry(cid):
            out.append(
                _fail(
                    "registry-id-shape",
                    f"candidate id {cid!r} is declared registry class but is not a "
                    "<DATABASE>-<ENTRY> identifier",
                )
            )
        if idc == "control-requirement" and not cid.startswith("v"):
            out.append(
                _fail(
                    "control-id-version-pinned",
                    f"control requirement {cid!r} is not version-pinned; a bare identifier means "
                    "something else after the next release of the standard",
                )
            )

    # C21's arithmetic, made deterministic. It was previously checked in ONE direction
    # (more candidates than kept), which never fires; the direction that parked three live
    # tickets is a cell claiming more kept than it lists. Both are now equality.
    dropped_per_cell: dict = {}
    for drop in (doc.get("bound") or {}).get("dropped") or []:
        dkey = (drop["cell"]["group_id"], drop["cell"]["source_id"])
        dropped_per_cell[dkey] = dropped_per_cell.get(dkey, 0) + 1

    for key, cell in by_cell.items():
        if cell["status"] != "reached":
            continue  # only a reached cell carries returned/kept at all
        named = refs.get(key, 0)
        if named != cell["kept"]:
            out.append(
                _fail(
                    "kept-accounted",
                    f"cell {key[0]}/{key[1]} kept {cell['kept']} but {named} candidates name "
                    "it; every kept item is a candidate row, so a mismatch is either a "
                    "miscount or a relevance cut nobody recorded",
                )
            )
        dropped = dropped_per_cell.get(key, 0)
        deduped = cell.get("deduped", 0)
        if cell["returned"] != cell["kept"] + dropped + deduped:
            out.append(
                _fail(
                    "returned-accounted",
                    f"cell {key[0]}/{key[1]} returned {cell['returned']} but accounts for "
                    f"{cell['kept'] + dropped + deduped} (kept {cell['kept']} + dropped "
                    f"{dropped} + deduped {deduped}); every result a source gave back was "
                    "carried forward, cut by the cap, or collapsed into an item already "
                    "counted — an unaccounted difference is a relevance cut with nowhere to hide",
                )
            )

    return out


# ── extract record ─────────────────────────────────────────────────────────────

#: Sentinel for the test helper's "remove this key" edit.
DELETE = object()

#: The nine body headings, in order. A record missing one, or carrying them out of order, is
#: not the artifact the extraction template describes.
EXTRACT_HEADINGS = (
    "## What the source says",
    "## Which surfaces it applies to",
    "## Evidence of exploitation",
    "## Severity as published",
    "## The control the source prescribes",
    "## Preconditions and limits",
    "## Relationship to other items",
    "## What this does not establish",
    "## Provenance",
)

#: Evidence kinds strong enough for tier 1 — something was actually exploited. Everything else
#: is tier 2 at best: it proves the weakness works somewhere, not that anyone used it.
TIER1_KINDS = frozenset({"kev-listed", "matching-incident"})


#: An ``item_id`` safe to use verbatim as a filename. Every registry-shaped id already is.
_SAFE_ID = re.compile(r"^[A-Za-z0-9._-]{1,100}$")

#: Longest sanitized prefix kept before the hash, so the whole name stays well inside every
#: filesystem's per-component limit once ``.md`` is appended.
_PREFIX_CAP = 80


def record_filename(item_id: str) -> str:
    """Return the filename stem a record for ``item_id`` must be written under.

    An ``item_id`` is an IDENTITY and may legitimately be a stable URL (the per-source-class
    policy: a conference talk or bug-bounty report has no registry id, and inventing one was
    the defect that policy fixed). A filename may not contain what a URL contains, so the two
    are encoded separately rather than conflated.

    Identity for anything already filename-safe — so every registry-shaped id
    (``CVE-…``, ``GHSA-…``, ``CWE-…``, ``v5.0.0-2.1.1``) is unchanged and every record written
    before this rule stays valid. Anything else becomes a sanitized prefix joined to a short
    digest of the WHOLE id, so two ids differing only in characters the sanitizer collapses
    still get different names.

    Args:
        item_id: The record's canonical identity, verbatim.

    Returns:
        The filename stem (no ``.md`` suffix).
    """
    if _SAFE_ID.match(item_id):
        return item_id
    prefix = re.sub(r"[^A-Za-z0-9._-]+", "-", item_id).strip("-.")[:_PREFIX_CAP].strip("-.")
    digest = hashlib.sha256(item_id.encode("utf-8")).hexdigest()[:8]
    return f"{prefix}-{digest}" if prefix else digest


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Split a record into its YAML frontmatter and its markdown body.

    Args:
        text: The whole file.

    Returns:
        ``(frontmatter, body)``.

    Raises:
        ValueError: The file does not open with a frontmatter block.
    """
    if not text.startswith("---"):
        raise ValueError("record does not start with a YAML frontmatter block")
    _, _, rest = text.partition("---")
    fm_text, sep, body = rest.partition("\n---")
    if not sep:
        raise ValueError("frontmatter block is not closed")
    return yaml.safe_load(fm_text) or {}, body.lstrip("\n")


def validate_extract(text: str, filename: str | None = None) -> list[str]:
    """Validate one extract record — frontmatter shape plus body structure.

    Args:
        text: The whole extract record file.
        filename: The record's own filename, when known. Checked against
            ``record_filename(item_id)``: a record whose name does not encode its identity is
            unreachable to the coordinator's disk cursor and to the synthesis loader, both of
            which look it up BY NAME — and it is otherwise perfectly valid, so nothing else
            would ever report it missing.

    Returns:
        One ``FAIL`` line per violation, empty when clean.
    """
    try:
        fm, body = parse_frontmatter(text)
    except ValueError as exc:
        return [_fail("frontmatter", str(exc))]

    out = _schema_failures(fm, "extract-output.schema.json")
    if filename is not None and isinstance(fm.get("item_id"), str):
        expected = record_filename(fm["item_id"]) + ".md"
        if Path(filename).name != expected:
            out.append(
                _fail(
                    "record-filename",
                    f"record for item_id {fm['item_id']!r} is named "
                    f"{Path(filename).name!r}; it must be {expected!r} or nothing that looks "
                    "it up by name will find it",
                )
            )
    if out:
        return out

    if fm["outcome"] == "skipped":
        if body.strip():
            out.append(
                _fail(
                    "skip-no-body",
                    "a bail is a decision, not an analysis; a skip record carries frontmatter "
                    "only",
                )
            )
        return out

    present = [h for h in EXTRACT_HEADINGS if h in body]
    missing = [h for h in EXTRACT_HEADINGS if h not in body]
    if missing:
        out.append(_fail("extract-headings", f"body is missing {', '.join(missing)}"))
    else:
        order = [body.index(h) for h in EXTRACT_HEADINGS]
        if order != sorted(order):
            out.append(
                _fail(
                    "extract-headings",
                    "body headings are out of order; the template's order is the reading order "
                    "a reviewer relies on",
                )
            )
    del present

    if fm["tier"] == 1:
        kinds = {e["kind"] for e in fm.get("tier_evidence", [])}
        if not (kinds & TIER1_KINDS):
            out.append(
                _fail(
                    "tier-evidence-strength",
                    f"tier 1 claims exploitation in the wild but its evidence is {sorted(kinds)}; "
                    "a proof-of-concept proves the weakness works somewhere, not that anyone "
                    "used it — that is tier 2",
                )
            )

    overlap = set(fm.get("aliases", [])) & set(fm.get("related", []))
    if overlap:
        out.append(
            _fail(
                "alias-related-disjoint",
                f"{sorted(overlap)} appears as both an alias and a related item; an alias names "
                "THIS item, related names a neighbour, and conflating them makes synthesis "
                "either merge two threats or report one twice",
            )
        )

    return out


# ── synthesis ──────────────────────────────────────────────────────────────────


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


def validate_synthesis(
    doc: dict, extracts: dict, registry: dict, searches: dict | None = None
) -> list[str]:
    """Validate a threat register against the extractions it was built from.

    Args:
        doc: The parsed register.
        extracts: ``{item_id: entry}`` from ``_load_extracts`` for every record available to
            synthesis. Extracted records carry ``tier``/``aliases``; records skipped as
            unavailable or withdrawn carry ``gap: True`` and are coverage gaps rather than
            evidence. This is what makes evidence resolution and alias-collapse checkable.
        registry: The master source registry, for the angle list.
        searches: ``{angle_id: outcome}`` read from the search artifacts, when available. The
            receipt restates each angle's outcome, so the two records must agree; without this
            the reconciliation cannot run and is skipped rather than assumed.

    Returns:
        One ``FAIL`` line per violation, empty when clean.
    """
    out = _schema_failures(doc, "threat-register.schema.json")
    if out:
        return out

    if searches:
        for entry in (doc.get("coverage_receipt") or {}).get("angles") or []:
            actual = searches.get(entry.get("angle_id"))
            # an angle with no artifact was never created — nothing to reconcile against.
            if actual is None or entry.get("outcome") == actual:
                continue
            out.append(
                _fail(
                    "receipt-matches-artifact",
                    f"the receipt records angle {entry['angle_id']!r} as "
                    f"{entry.get('outcome')!r} but its own search output says {actual!r}; "
                    "'we never started' and 'we ran and every source refused us' are different "
                    "facts, and the receipt exists to carry the artifact's, not to restate it",
                )
            )

    gaps = {i for i, e in extracts.items() if e.get("gap", False)}
    if gaps:
        receipted = {
            r.get("item_id")
            for r in (doc.get("coverage_receipt") or {}).get("unretrievable") or []
        }
        missing = sorted(gaps - receipted)
        if missing:
            out.append(
                _fail(
                    "coverage-gap-receipted",
                    f"{missing} were judged relevant and could not be read, but the coverage "
                    "receipt does not name them; an unread relevant item that goes unrecorded "
                    "is indistinguishable from one that does not apply",
                )
            )

    seen: set[str] = set()
    for row in doc["threats"]:
        if row["threat_id"] in seen:
            out.append(
                _fail("threat-id-unique", f"threat id {row['threat_id']!r} appears more than once")
            )
        seen.add(row["threat_id"])

        # a gap record is present so synthesis can receipt it; it carries no extraction, so it
        # is not citable evidence and does not make a row resolvable.
        unknown = [
            e for e in row["evidence"] if e not in extracts or extracts[e].get("gap", False)
        ]
        if unknown:
            out.append(
                _fail(
                    "evidence-resolves",
                    f"{row['threat_id']} cites {unknown}, which resolve to no extraction; a row "
                    "citing nothing extractable is an assertion, not a finding",
                )
            )

        known = [
            extracts[e]["tier"]
            for e in row["evidence"]
            if e in extracts and not extracts[e].get("gap", False)
        ]
        if known and row["tier"] < min(known):
            out.append(
                _fail(
                    "tier-not-promoted",
                    f"{row['threat_id']} claims tier {row['tier']} while its strongest evidence "
                    f"is tier {min(known)}; synthesis never promotes a row above its evidence",
                )
            )

        ref = row["control"].get("standard_reference")
        if ref and not ref.startswith("v"):
            out.append(
                _fail(
                    "standard-ref-pinned",
                    f"{row['threat_id']} cites control {ref!r} unpinned; a bare identifier means "
                    "something else after the standard's next release",
                )
            )

    # Alias collapse: two rows resting on items that name the same thing are one threat.
    owner: dict[str, str] = {}
    for row in doc["threats"]:
        for e in row["evidence"]:
            for name in {e, *extracts.get(e, {}).get("aliases", [])}:
                prior = owner.get(name)
                if prior is not None and prior != row["threat_id"]:
                    out.append(
                        _fail(
                            "alias-collapse",
                            f"{prior} and {row['threat_id']} rest on items that are aliases of "
                            "each other; one vulnerability under two identifiers is one row",
                        )
                    )
                owner[name] = row["threat_id"]

    receipt = doc["coverage_receipt"]
    reported = {a["angle_id"] for a in receipt["angles"]}
    for angle in registry["angles"]:
        if angle["id"] not in reported:
            out.append(
                _fail(
                    "receipt-angles-complete",
                    f"the coverage receipt omits angle {angle['id']!r}; a non-firing angle is "
                    "reported, never left out",
                )
            )

    novelty = receipt.get("novelty_statement", "")
    if novelty and "no documented prior art found" not in novelty.lower():
        out.append(
            _fail(
                "novelty-phrasing",
                "a novelty statement must read 'no documented prior art found across N angles "
                "and M terms'; no survey sees private or unpublished work",
            )
        )

    return out


def _load_search_outcomes(directory: Path) -> dict:
    """Read each angle's own recorded outcome from its search output.

    Args:
        directory: Holds the per-angle ``*.yaml`` search outputs.

    Returns:
        ``{angle_id: outcome}`` — what the artifact itself claims, for the receipt to be
        reconciled against.
    """
    out: dict = {}
    for path in sorted(directory.glob("*.yaml")):
        try:
            doc = yaml.safe_load(path.read_text()) or {}
        except yaml.YAMLError:
            continue
        angle = (doc.get("meta") or {}).get("angle_id")
        if angle and doc.get("outcome"):
            out[angle] = doc["outcome"]
    return out


def _load_extracts(directory: Path) -> dict:
    """Read a directory of extract records into the map ``validate_synthesis`` expects.

    Args:
        directory: Holds ``*.md`` extract records.

    Returns:
        ``{item_id: entry}``. An extracted record yields ``{"tier", "aliases", "gap": False}``.

        A record skipped as ``unavailable`` or ``withdrawn`` yields
        ``{"gap": True, "reason", "cause"}`` — it is a COVERAGE GAP, not an absence: the item
        was judged relevant and could not be read, so a reader must be able to tell it apart
        from an item that does not apply. Only ``irrelevant`` is omitted, because only a
        relevance bail genuinely rests on no evidence. Dropping all three alike is what let a
        relevant, unread threat disappear from a survey without trace.
    """
    out: dict = {}
    for path in sorted(directory.glob("*.md")):
        try:
            fm, _ = parse_frontmatter(path.read_text())
        except ValueError:
            continue
        outcome = fm.get("outcome")
        if outcome == "extracted":
            out[fm["item_id"]] = {
                "tier": fm["tier"],
                "aliases": fm.get("aliases", []),
                "gap": False,
            }
            continue
        skip = fm.get("skip") or {}
        reason = skip.get("reason")
        if reason in ("unavailable", "withdrawn"):
            out[fm["item_id"]] = {
                "gap": True,
                "reason": reason,
                "cause": skip.get("cause", ""),
            }
    return out


def _looks_registry(cid: str) -> bool:
    head, sep, tail = cid.partition("-")
    return bool(sep) and head.isupper() and head.isalpha() and bool(tail)


# ── CLI ────────────────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    """Entry point.

    Args:
        argv: Argument vector; defaults to ``sys.argv[1:]``.

    Returns:
        0 when the artifact is clean, 1 otherwise.
    """
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="kind", required=True)

    p_map = sub.add_parser("keyword-map", help="validate a threat-vocabulary map")
    p_map.add_argument("file")

    p_search = sub.add_parser("search", help="validate one angle's search output")
    p_search.add_argument("file")
    p_search.add_argument(
        "--keyword-map",
        required=True,
        help="the map the output ran against; coverage completeness is uncomputable without it",
    )

    p_extract = sub.add_parser("extract", help="validate one source-item extract record")
    p_extract.add_argument("file")

    p_syn = sub.add_parser("synthesis", help="validate a threat register")
    p_syn.add_argument("file")
    p_syn.add_argument(
        "--extracts",
        help="directory of extract records the register was built from. Without it, evidence "
        "resolution and alias-collapse cannot be checked and are reported as skipped.",
    )
    p_syn.add_argument(
        "--queue",
        help="the FROZEN extract-queue.yaml. Without it a queue row that produced no record "
        "is invisible: the register-side checks only run the other direction.",
    )
    p_syn.add_argument(
        "--search",
        help="directory of per-angle search outputs. Without it the receipt cannot be "
        "reconciled against the artifacts it restates, and that check is reported as skipped.",
    )

    args = p.parse_args(argv)
    raw = Path(args.file).read_text()

    if args.kind == "keyword-map":
        failures = validate_keyword_map(yaml.safe_load(raw))
    elif args.kind == "extract":
        failures = validate_extract(raw, filename=args.file)
    elif args.kind == "synthesis":
        doc = yaml.safe_load(raw)
        extracts = None
        if args.extracts:
            # A supplied-but-unusable directory is a broken invocation, not an absence of
            # evidence. Path.glob returns [] for a missing directory rather than raising, so
            # without these two branches a bad path, an empty one and a genuine citation
            # mismatch all arrive as the same per-row failure — which blames the author, and
            # whose cheapest route to the exit 0 the brief asks for is deleting the citations.
            directory = Path(args.extracts)
            if not directory.is_dir():
                print(
                    _fail(
                        "extracts-unreadable",
                        f"--extracts {args.extracts} is not a directory (resolved from "
                        f"{Path.cwd()}) — this is a broken invocation, not an absence of "
                        "evidence; correct the path and re-run, and do NOT remove the "
                        "register's citations to reach exit 0",
                    )
                )
                return 1
            extracts = _load_extracts(directory)
            cited = sum(1 for row in doc["threats"] if row.get("evidence"))
            if not extracts and cited:
                print(
                    _fail(
                        "extracts-empty",
                        f"--extracts {args.extracts} resolved but holds no extract records, "
                        f"while {cited} row(s) cite one — the extract wave produced nothing, "
                        "or it wrote somewhere else; either way the rows are not the defect",
                    )
                )
                return 1
        if extracts is None:
            print(
                "SKIP evidence-resolves, tier-not-promoted, alias-collapse: no --extracts "
                "directory supplied"
            )
            extracts = {e: {"tier": 1, "aliases": []} for r in doc["threats"] for e in r["evidence"]}
        searches = _load_search_outcomes(Path(args.search)) if args.search else None
        if searches is None:
            print("SKIP receipt-matches-artifact: no --search directory supplied")
        failures = validate_synthesis(doc, extracts, load_registry(), searches=searches)
        if args.queue and args.extracts:
            failures = failures + _queue_coverage(
                Path(args.queue), Path(args.extracts), (doc.get("meta") or {}).get("extract_count")
            )
        elif not args.queue:
            print("SKIP queue-coverage: pass --queue <extract-queue.yaml> to reconcile the "
                  "frozen queue against the records on disk")
    else:
        mapping = yaml.safe_load(Path(args.keyword_map).read_text())
        failures = validate_search(yaml.safe_load(raw), mapping, load_registry())

    for line in failures:
        print(line)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
