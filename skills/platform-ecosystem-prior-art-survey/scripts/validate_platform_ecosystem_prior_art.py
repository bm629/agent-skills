#!/usr/bin/env python3
"""Deterministic gate for platform-ecosystem prior-art artifacts (wave 1).

Checks SHAPE and completeness only — schema, enums, ranges, required fields, and arithmetic that
reconciles two records against each other. It never judges whether a platform is comparable,
whether a mechanism claim is persuasive, or whether an exclusion was fair; those are the reviewing
skill's numbered conditions. A fuzzy heuristic inside a deterministic gate produces false failures
and duplicates the reviewer, so resist making this smarter.

Usage:
    validate_platform_ecosystem_prior_art.py keyword-map <file>
    validate_platform_ecosystem_prior_art.py search <file> --keyword-map <file>

Prints one ``FAIL <rule>: ...`` line per violation. Exit 0 clean, 1 the artifact under test has
findings, 2 it could not be used at all — unreadable, unparseable, or a PACKAGE fault such as a
malformed registry. The 2 class exists so a package defect never sends a caller off to edit an
artifact that is fine.
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
    # A missing dependency is a PACKAGE fault, and an unguarded import reports it as exit 1 with
    # a traceback: the code that means "the artifact has findings", with no FAIL line to grep. A
    # cold agent then has an exit gate it cannot satisfy and no way to tell that the fault is not
    # its own. Caught here so it lands in the exit-2 class with the remedy stated.
    _MISSING_DEPENDENCY = exc.name
    yaml = None  # type: ignore[assignment]
    Draft202012Validator = None  # type: ignore[assignment]
else:
    _MISSING_DEPENDENCY = None

HERE = Path(__file__).resolve().parent
SCHEMAS = HERE.parent / "schemas"
DEFAULT_REGISTRY = HERE.parent / "references" / "source-registry.yaml"

#: Capability-map paths a conditional trigger may ANCHOR on — the fields the map's own schema
#: marks REQUIRED, so a predicate resting on one always evaluates.
#:
#: The rule is about the SHAPE of the predicate, not about every field in it. An optional field
#: sitting beside a required one in an OR only ever ADDS firings, so it fails OPEN and is
#: legitimate — those are further disjuncts of `predicate`. What fails CLOSED, silently, is an AND with
#: an optional field or a sole optional leg: the angle looks configured and never runs.
#:
#: The governing convention is "absent input implies not-in-set implies false", which is WHY an
#: optional leg fails closed: the disjunct is false for any map that omitted the field, and that
#: looks identical to an angle nobody configured.
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

#: Longest sanitized prefix kept before the digest is appended.
_PREFIX_CAP = 80

#: The marker the hashing branch appends. The identity branch must never return a string that
#: looks like one, or the two branches share an output namespace and injectivity is lost: a raw id
#: that already ends this way would map to itself, colliding with the hash of some other id.
_HASHED_STEM = re.compile(r"--[0-9a-f]{12}$")

#: A date that starts with an ISO-8601 calendar date. A bare date is legitimate: many sources
#: state a day and no time, and rejecting that would push producers toward inventing a time.


def _fail(rule: str, message: str) -> str:
    """One finding, in the only format a caller can grep for."""
    return f"FAIL {rule}: {message}"


def load_registry(path: Path | str = DEFAULT_REGISTRY) -> dict:
    """Load the master source registry that ships inside this package."""
    return yaml.safe_load(Path(path).read_text())


def _schema(name: str) -> dict:
    return json.loads((SCHEMAS / f"{name}.schema.json").read_text())


def _schema_errors(doc: object, name: str) -> list[str]:
    validator = Draft202012Validator(_schema(name))
    out = []
    for err in sorted(validator.iter_errors(doc), key=lambda e: list(e.path)):
        where = "/".join(str(p) for p in err.path) or "<root>"
        out.append(_fail("schema", f"{where}: {err.message}"))
    return out


def anchor_failures(registry: dict) -> list[str]:
    """The registry's own integrity — a PACKAGE fault, checked before any artifact is read."""
    out: list[str] = []
    for angle in registry.get("angles") or []:
        aid = angle.get("id", "?")
        trigger = angle.get("trigger")
        if trigger not in ("always", "conditional"):
            out.append(
                _fail(
                    "trigger-must-be-known",
                    f"angle {aid!r} declares trigger {trigger!r}; a value outside "
                    "{always, conditional} reads as always-on to every check below, so a "
                    "one-character typo disables the anchor rules and they fail OPEN",
                )
            )
            continue
        conditional = trigger == "conditional"
        anchors = angle.get("trigger_anchor")
        if not conditional:
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
                    f"angle {aid!r} anchor is a scalar; a scalar cannot describe a disjunctive predicate",
                )
            )
            continue
        for anchor in anchors:
            if anchor not in REQUIRED_CAPABILITY_FIELDS:
                out.append(
                    _fail(
                        "anchor-must-be-required",
                        f"angle {aid!r} anchors on {anchor!r}, which the capability schema does not "
                        "mark required. An optional leg cannot root a predicate: every map that omits the field fails the angle closed. Root the anchor on a required field and express the optional leg as a further disjunct of `predicate`",
                    )
                )
    return out


def record_filename(item_id: str) -> str:
    """Return the filename stem a record for ``item_id`` must be written under.

    An ``item_id`` is an IDENTITY and may legitimately contain characters a filename may not.
    This type's ids are `<platform_slug>__<angle_id>`, which are filename-safe — but the hash
    branch IS reachable, because a URL-minted id carries slashes and dots. #42 warns that the
    least-exposed type is the one most likely to skip the rule and the most likely to be wrong
    later, so both parts ship now rather than when a slash first appears.

    Identity for anything already filename-safe, so readable ids stay readable. Anything else
    becomes a sanitized prefix joined to a short digest of the WHOLE id, so two ids differing only
    in characters the sanitizer collapses still get different names.

    Args:
        item_id: The record's canonical identity, verbatim.

    Returns:
        The filename stem, without extension.

    NOT dead code, though nothing in this package calls it yet. Wave 1 registers `keyword-map`
    and `search` only; the extract records this names arrive in wave 2, and the spec requires the
    function that turns a source id into a filename to exist BEFORE the rows do — a sibling minted
    filenames ad hoc for one wave and inherited a cross-branch collision it could not undo. The
    siblings that DO call it (`visual`, `market-competitive`) are the shape this will take.
    """
    # PART (b): the identity branch REFUSES an input that already looks like a hashed stem.
    # Without this the two branches share an output namespace and f(f(x)) == f(x) becomes
    # constructible — which is a real, shipped collision in one sibling.
    if re.fullmatch(r"[A-Za-z0-9._-]+", item_id) and not _HASHED_STEM.search(item_id):
        return item_id
    prefix = re.sub(r"[^A-Za-z0-9._-]+", "-", item_id)[:_PREFIX_CAP].strip("-")
    digest = hashlib.sha256(item_id.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}--{digest}" if prefix else f"--{digest}"


def _angle_ids(registry: dict) -> set[str]:
    return {a["id"] for a in registry.get("angles") or []}


def validate_keyword_map(doc: object, registry: dict | None = None) -> list[str]:
    """Shape of the wave-0 platform-and-mechanism vocabulary map."""
    reg = registry if registry is not None else load_registry()
    out = _schema_errors(doc, "platform-vocabulary-map")
    if out:
        return out

    slugs = [p.get("slug") for p in doc.get("platforms") or []]
    for dup in sorted({s for s in slugs if slugs.count(s) > 1}):
        out.append(
            _fail(
                "slug-minted-twice",
                f"platform slug {dup!r} is minted {slugs.count(dup)} times; the whole point of "
                "minting once is that a slug resolves to one platform, and two rows for one slug "
                "is the dedupe break this map exists to prevent, from the inside",
            )
        )

    declared = _angle_ids(reg)
    seen = set()
    for verdict in doc.get("angle_applicability") or []:
        aid = verdict.get("angle_id")
        if aid in seen:
            out.append(
                _fail(
                    "verdict-declared-twice",
                    f"angle {aid!r} carries more than one verdict; only ABSENCE was checked, so "
                    "two contradictory verdicts for one angle passed and a reader takes whichever "
                    "it meets first",
                )
            )
        seen.add(aid)
        if aid not in declared:
            out.append(
                _fail(
                    "applicability-angle-unknown",
                    f"verdict for {aid!r}, which is not an angle in the registry; a verdict on a non-existent angle proves nothing",
                )
            )
        if not str(verdict.get("reason", "")).strip():
            out.append(
                _fail(
                    "applicability-reason-required",
                    f"angle {aid!r} verdict carries no reason",
                )
            )
    for missing in sorted(declared - seen):
        out.append(
            _fail(
                "applicability-incomplete",
                f"no verdict for angle {missing!r}; an angle judged inapplicable leaves no trace "
                "anywhere and cannot be reviewed",
            )
        )
    return out


def validate_search(
    doc: object, keyword_map: object, registry: dict | None = None
) -> list[str]:
    """Shape of one angle's search output.

    Args:
        doc: The parsed search output.
        keyword_map: The wave-0 map, whose `platforms` block is the ONLY place slugs are minted.
        registry: Source registry; defaults to this package's copy.

    Returns:
        One ``FAIL`` line per violation, empty when clean.
    """
    reg = registry if registry is not None else load_registry()
    out = _schema_errors(doc, "search-output")
    if out:
        return out

    outcome = doc.get("outcome")
    cells = doc.get("coverage") or []
    if outcome == "not_run" and cells:
        out.append(
            _fail(
                "not-run-owes-no-cells",
                "an unrun angle owes NO coverage cells; empty ones manufacture zeros that look like searches",
            )
        )
    if outcome == "not_run" and (doc.get("candidates") or []):
        out.append(
            _fail(
                "not-run-owes-no-candidates",
                "an unrun angle emitted candidates; this is the same manufacture the cell rule "
                "catches one layer up, and it is the layer synthesis actually reads",
            )
        )
    if outcome == "ran" and not cells:
        out.append(
            _fail(
                "ran-needs-cells",
                "outcome is `ran` with no coverage cells; a pair with no cell is an unexplained gap, not a zero",
            )
        )

    counts: dict[str, int] = {}
    for cell in cells:
        sid = cell.get("source_id", "?")
        status = cell.get("status")
        counts[status] = counts.get(status, 0) + 1
        returned, kept = cell.get("returned"), cell.get("kept")
        if status == "reached":
            if returned is None:
                out.append(
                    _fail(
                        "coverage-reached-needs-count",
                        f"cell {sid!r} was reached but records no `returned`; a recorded zero is what proves the search ran",
                    )
                )
            if kept is None:
                out.append(
                    _fail(
                        "coverage-reached-needs-kept",
                        f"cell {sid!r} was reached but records no `kept`; the field the schema "
                        "spends six lines defining is optional in practice if its absence is not "
                        "checked, and every rule about it then silently does nothing",
                    )
                )
            if returned is not None and kept is not None and kept > returned:
                out.append(
                    _fail(
                        "kept-exceeds-returned",
                        f"cell {sid!r} kept {kept} of {returned} returned",
                    )
                )
        else:
            if returned is not None or kept is not None:
                out.append(
                    _fail(
                        "coverage-unreached-has-count",
                        f"cell {sid!r} has status {status!r} but records a count; a count on an unreached cell is a zero laundered out of a failure",
                    )
                )
            if not str(cell.get("cause") or "").strip():
                out.append(
                    _fail(
                        "coverage-cause-required",
                        f"cell {sid!r} has status {status!r} and no cause; a non-reached status without observable evidence is unreviewable",
                    )
                )

    summary = (doc.get("retrieval_summary") or {}).get("status_counts")
    if summary is None and cells:
        out.append(
            _fail(
                "summary-required",
                "no retrieval_summary.status_counts; the summary duplicates the cells on purpose, "
                "so a producer that omits it loses the reconciliation with no trace — which is "
                "indistinguishable from a run where it happened to agree",
            )
        )
    if summary is not None:
        # "we had no unreachable cells" is a reasonable thing to write down, and comparing raw
        # dicts rejected it. Zeros carry no information the cells do not; compare what is present.
        summary = {k: v for k, v in summary.items() if v}
    if summary is not None and summary != counts:
        out.append(
            _fail(
                "summary-mismatch",
                f"retrieval_summary.status_counts {summary} does not reconcile with the cells {counts}; "
                "the summary duplicates the cells deliberately, and a discrepancy is the signal that a "
                "failure was laundered into a zero",
            )
        )

    # ── type-specific ──────────────────────────────────────────────────────────
    known_slugs = {p["slug"] for p in (keyword_map or {}).get("platforms") or []}
    known_sources = {s["id"] for s in reg.get("sources") or []}
    angle_id = (doc.get("meta") or {}).get("angle_id")

    for cell in cells:
        sid = cell.get("source_id")
        if sid not in known_sources:
            out.append(
                _fail(
                    "source-not-in-registry",
                    f"coverage cell cites source {sid!r}, which no registry row declares",
                )
            )

    for cand in doc.get("candidates") or []:
        slug = cand.get("platform_slug")
        if slug not in known_slugs:
            out.append(
                _fail(
                    "slug-not-in-map",
                    f"candidate carries platform_slug {slug!r}, which the wave-0 map does not mint; "
                    "a slug invented by an angle produces two rows for one platform and the dedupe "
                    "never fires",
                )
            )
        sid = cand.get("source_id")
        if sid not in known_sources:
            out.append(
                _fail(
                    "source-not-in-registry",
                    f"candidate cites source {sid!r}, which no registry row declares",
                )
            )
        if angle_id == "a3" and not str(cand.get("locator") or "").strip():
            out.append(
                _fail(
                    "enumeration-needs-locator",
                    f"a3 candidate for {slug!r} records no locator; a count without the location of "
                    "the set it counted cannot be re-derived, and re-derivation is the only thing "
                    "that catches a fabricated enumeration",
                )
            )

    # ── the three shape halves of C9, which the CONDITION was carrying alone ────────────────
    # All three are decidable from the registry and the artifact, so by #49/#56 they belong to the
    # gate and the condition keeps only its judgment. Two were named as inputs to the code-review
    # task and then not built when that task landed; this is where they were owed.
    angle_row = next(
        (a for a in reg.get("angles") or [] if a.get("id") == angle_id), None
    )
    if angle_row and outcome == "ran":
        celled = {c.get("source_id") for c in cells}
        for missing in sorted(set(angle_row.get("sources") or []) - celled):
            out.append(
                _fail(
                    "angle-source-without-a-cell",
                    f"angle {angle_id!r} declares source {missing!r} and no cell records it; an "
                    "omitted source and a recorded zero are different facts, and only one of them "
                    "is evidence",
                )
            )
        for cell in cells:
            used = cell.get("fallback_used")
            if used and used not in celled:
                out.append(
                    _fail(
                        "fallback-without-a-cell",
                        f"cell {cell.get('source_id')!r} names fallback {used!r}, which has no "
                        "cell of its own; a walked fallback that returned nothing and one that "
                        "was never walked are indistinguishable without a trace",
                    )
                )

    # `kept` counts candidate ROWS (#32), which makes this an EQUALITY rather than a direction —
    # the check the blind reviewer asked for, logged as a code-review input and owed since.
    cited: dict[str, int] = {}
    for cand in doc.get("candidates") or []:
        sid = cand.get("source_id")
        cited[sid] = cited.get(sid, 0) + 1
    # `unadmitted` rows count too. Counting only candidates scores a row that was found and
    # dropped WITHOUT a record as correct — which is the one thing `unadmitted` exists to make
    # impossible, and the reading three shipped siblings already use.
    for un in doc.get("unadmitted") or []:
        sid = un.get("found_by")
        cited[sid] = cited.get(sid, 0) + 1
    for cell in cells:
        if cell.get("status") != "reached" or cell.get("kept") is None:
            continue
        actual = cited.get(cell.get("source_id"), 0)
        if cell["kept"] != actual:
            out.append(
                _fail(
                    "kept-does-not-match-candidates",
                    f"cell {cell.get('source_id')!r} records kept={cell['kept']} while {actual} "
                    "candidate/unadmitted row(s) name it; kept counts rows carried forward, and "
                    "an unreconciled count hides a row that was dropped without a record",
                )
            )

    explained = bool(doc.get("unadmitted")) or bool(doc.get("notes"))
    for cell in cells:
        if (
            cell.get("status") == "reached"
            and cell.get("kept") == 0
            and (cell.get("returned") or 0) > 0
            and not explained
        ):
            out.append(
                _fail(
                    "kept-zero-unexplained",
                    f"cell {cell.get('source_id')!r} retrieved {cell['returned']} and admitted "
                    "none, with no `unadmitted` entry and no note; something was discarded and "
                    "the reason for discarding it is the evidence",
                )
            )

    bound = doc.get("bound") or {}
    if (
        angle_row
        and bound.get("cap") is not None
        and bound["cap"] != angle_row.get("cap")
    ):
        out.append(
            _fail(
                "cap-not-the-registrys",
                f"bound.cap is {bound['cap']} where the registry sets {angle_row.get('cap')} for "
                f"angle {angle_id!r}; a run may neither raise its own ceiling nor quietly lower it",
            )
        )
    n_candidates = len(doc.get("candidates") or [])
    if (
        bound.get("hit") is False
        and bound.get("cap") is not None
        and n_candidates > bound["cap"]
    ):
        out.append(
            _fail(
                "not-hit-contradicts-the-count",
                f"bound.hit is false while {n_candidates} candidates exceed the cap of "
                f"{bound['cap']}; `hit: false` is the STRONGER claim — that every admissible "
                "candidate is present — and it cannot hold above the ceiling",
            )
        )
    if bound.get("hit"):
        if not str(bound.get("ordering") or "").strip():
            out.append(
                _fail(
                    "bound-needs-ordering",
                    "the cap was HIT but records no ordering; an unrecorded ordering makes the truncation unreviewable",
                )
            )
        if not str(bound.get("dropped_note") or "").strip():
            out.append(
                _fail(
                    "bound-needs-dropped-note",
                    "the cap was HIT but records nothing about what fell out; with no dropped_note the "
                    "ordering is the only evidence a truncation leaves, and a reader cannot tell a cap "
                    "that dropped one near-miss from one that dropped half the corpus",
                )
            )
    return out


def _read(path: Path) -> tuple[object | None, str | None]:
    """Read one YAML input, turning every unusable-input failure into an exit-2 line.

    `UnicodeDecodeError` is caught explicitly: it is a `ValueError`, not an `OSError`, so an
    `except OSError` that looks exhaustive lets a non-UTF-8 file escape as a traceback at exit 1 —
    the code that means "the artifact has findings", with no FAIL line for a caller to grep.
    """
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")), None
    except UnicodeDecodeError as exc:
        return None, _fail(
            "input", f"{path}: not UTF-8 text ({exc.reason} at byte {exc.start})"
        )
    except OSError as exc:
        return None, _fail("input", f"{path}: {exc.strerror or exc}")
    except yaml.YAMLError as exc:
        return None, _fail("input", f"{path}: not valid YAML: {exc}")


#: How old a CONTRACTUAL record may be, relative to the index's own date, before the row resting on
#: it must carry a staleness marker. Grounded in two measured platform changes rather than chosen:
#: one marketplace's terms took effect on a stated date with a further billing migration announced
#: eighteen months later, and one store removed its entire payments rail inside about four months
#: of announcing it. A constant here rather than a number in prose, because a lens divides by it.
STALENESS_DAYS = 90


#: The report's fixed sections, in order. An angle the TRIGGER excluded renders its section with a
#: predicate rather than an empty heading -- so the section named must be one that exists, or the
#: marker renders nowhere and the reader sees the silence it was written to prevent.
REPORT_SECTIONS = (
    "Extension model and attachment surface",
    "Permission and trust model",
    "Developer experience and onboarding funnel",
    "Commercial terms and monetization",
    "Discovery, ranking and categorisation",
    "Review, certification and enforcement",
    "Regulatory and gatekeeper exposure",
    "Growth path: build first, defer, and when to migrate",
    "Coverage and absence receipt",
)


def _queue_reconciliation(args, wave) -> list[str]:
    """The frozen queue against the records this wave actually wrote, BOTH directions.

    Args:
        args: The parsed arguments, for `--queue`.
        wave: THIS wave's extract records.

    Returns:
        The FAIL lines, in the order they were found.
    """
    if args.queue is None:
        return [
            _fail(
                "queue-crosscheck-skipped",
                "no `--queue`, so the frozen queue was NOT reconciled against the records. Exit 1 "
                "on its own: the dispatcher can supply the queue and re-run, and the index is not "
                "what needs repairing",
            )
        ]
    queue, err = _read(args.queue)
    if err is not None:
        return [
            _fail(
                "queue-crosscheck-skipped",
                f"the `--queue` file could not be read: {err}. The reconciliation did NOT run",
            )
        ]
    schema_errs = _schema_errors(queue, "extract-queue")
    if schema_errs:
        return [
            _fail(
                "queue-invalid",
                f"the frozen queue does not satisfy its own schema: {schema_errs[0]}",
            )
        ]
    # Where no record arrived, the extracts skip is already the report; naming every frozen row a
    # second time for one missing directory would blame the author twice for the dispatcher's gap.
    if not wave:
        return []
    asked = [row.get("item_id") for row in queue.get("queue") or []]
    written = {str(((r or {}).get("meta") or {}).get("item_id")) for r in wave}
    findings = [
        _fail(
            "queue-1",
            f"the frozen queue asked for {item!r} and no record was written for it. A row that "
            "wrote no file is invisible to the index, which can only see the records that exist",
        )
        for item in asked
        if item not in written
    ]
    findings += [
        _fail(
            "queue-2",
            f"a record was written for {item!r}, which no frozen queue row asked for. The queue is "
            "written once and never rewritten, so extraction outside it is work the survey cannot "
            "account for",
        )
        for item in sorted(written - set(asked))
    ]
    return findings


def read_record(path: Path):
    """One extract record: frontmatter and body, from the SINGLE file that carries both.

    Args:
        path: The `.md` record.

    Returns:
        `(doc, body, err)` -- the parsed frontmatter, the markdown after it, and a FAIL line where
        the file could not be read or carries no frontmatter block at all.
    """
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        return (
            None,
            "",
            _fail(
                "input", f"{path}: not UTF-8 text ({exc.reason} at byte {exc.start})"
            ),
        )
    except OSError as exc:
        return None, "", _fail("input", f"{path}: {exc.strerror or exc}")
    if not raw.startswith("---"):
        return (
            None,
            "",
            _fail(
                "input",
                f"{path}: no frontmatter block -- the record is ONE file carrying both halves, and this one opens with the body",
            ),
        )
    front, sep, body = raw[3:].partition("\n---\n")
    if not sep:
        return (
            None,
            "",
            _fail("input", f"{path}: the frontmatter block is never closed"),
        )
    try:
        return yaml.safe_load(front), body, None
    except yaml.YAMLError as exc:
        return (
            None,
            "",
            _fail("input", f"{path}: the frontmatter is not valid YAML: {exc}"),
        )


def validate_extract(doc, body: str, path: Path) -> list[str]:
    """One extract record, and the body carried in the same file.

    Args:
        doc: The parsed frontmatter.
        body: The markdown after it.
        path: Where it was read from -- the derived filename is checked against it.

    Returns:
        The FAIL lines, in the order they were found.
    """
    failures: list[str] = []
    for err in _schema_errors(doc, "extract-output"):
        failures.append(_fail("schema", err))
    if failures:
        return failures

    meta = doc.get("meta") or {}
    item = str(meta.get("item_id") or "")
    stem = record_filename(item)
    if path.stem != f"extract-{stem}":
        failures.append(
            _fail(
                "filename-1",
                f"the record is at {path.name!r} but its own id derives {f'extract-{stem}.md'!r}. "
                "The frozen queue reconciles on the derived name, so a record under any other one "
                "is reported as never written -- which is not what went wrong",
            )
        )

    finding = doc.get("finding")
    if doc.get("outcome") == "skipped":
        if not doc.get("skipped"):
            failures.append(
                _fail(
                    "bail-1",
                    f"{item}: `outcome: skipped` with no `skipped` block -- a bail states its typed "
                    "cause and what was checked, because a record that declines silently is "
                    "indistinguishable from a spawn that never ran",
                )
            )
        if finding is not None:
            failures.append(
                _fail(
                    "bail-2",
                    f"{item}: `outcome: skipped` still carrying a `finding` -- a record cannot both "
                    "decline the mechanism and report it",
                )
            )
        return failures

    if finding is None:
        failures.append(
            _fail("record-1", f"{item}: `outcome: extracted` with no `finding` block")
        )
        return failures
    if doc.get("skipped"):
        failures.append(
            _fail(
                "record-2", f"{item}: `outcome: extracted` carrying a `skipped` block"
            )
        )

    # The id is `<platform>__<angle>` and BOTH halves are restated inside the finding. A record
    # that disagrees with itself joins to the wrong platform in every lens that groups on it.
    platform, _, mechanism = item.partition("__")
    if platform and finding.get("platform_id") != platform:
        failures.append(
            _fail(
                "item-id-1",
                f"{item}: the finding declares `platform_id: {finding.get('platform_id')}`, which "
                f"is not the {platform!r} its own id names. Every lens groups on this key",
            )
        )
    if mechanism and finding.get("mechanism") != mechanism:
        failures.append(
            _fail(
                "item-id-2",
                f"{item}: the finding declares `mechanism: {finding.get('mechanism')}`, which is "
                f"not the {mechanism!r} its own id names",
            )
        )

    if not body.strip():
        failures.append(
            _fail(
                "body-sections-1",
                f"{item}: the record carries frontmatter and no body. The machine block and the "
                "human analysis live in one file precisely so neither can ship without the other",
            )
        )

    if (
        finding.get("enumeration_count") is not None
        and finding.get("mechanism") != "a3"
    ):
        failures.append(
            _fail(
                "enumeration-1",
                f"{item}: `enumeration_count` is carried by a `{finding.get('mechanism')}` record. "
                "The surface-size lens computes on this field, and a count from an angle that "
                "never enumerated is a number with no walk behind it",
            )
        )

    announced, enforced = finding.get("announced_on"), finding.get("enforced_on")
    if (announced or enforced) and finding.get("mechanism") != "a4":
        failures.append(
            _fail(
                "interval-1",
                f"{item}: a migration date is carried by a `{finding.get('mechanism')}` record. "
                "Both dates are a4-only, because the interval between them is what the "
                "migration-debt lens divides by",
            )
        )
    if announced and enforced and str(enforced) < str(announced):
        failures.append(
            _fail(
                "interval-2",
                f"{item}: `enforced_on` {enforced} precedes `announced_on` {announced}. A negative "
                "interval is not a short runway, it is a broken record, and the lens that divides "
                "by it would report the migration as already over before it was announced",
            )
        )
    return failures


def validate_synthesis(doc, records) -> list[str]:
    """The decision index, wave 3.

    Args:
        doc: The parsed index.
        records: Every extract record it may cite, or None where they did not arrive and resolution
            therefore cannot run.

    Returns:
        The FAIL lines, in the order they were found.
    """
    failures: list[str] = []
    for err in _schema_errors(doc, "decision-index"):
        failures.append(_fail("schema", err))
    if failures:
        return failures

    # None where the records did not arrive. Resolving against an EMPTY set would report every
    # legitimate citation as unresolvable and send the author to repair a correct artifact.
    known = (
        None
        if records is None
        else {str(((r or {}).get("meta") or {}).get("item_id")) for r in records}
    )
    platforms = (
        None
        if records is None
        else {((r or {}).get("finding") or {}).get("platform_id") for r in records}
    )
    contractual = (
        {}
        if records is None
        else {
            str(((r or {}).get("meta") or {}).get("item_id")): str(
                ((r or {}).get("meta") or {}).get("as_of")
            )
            for r in records
            if ((r or {}).get("finding") or {}).get("volatility") == "contractual"
        }
    )

    if doc.get("mode") == "delta" and not (doc.get("lineage") or {}).get("extends"):
        failures.append(
            _fail(
                "lineage-1",
                "`mode: delta` with no `lineage.extends` -- a delta index that does not name the "
                "one it extends cannot be read as an amendment of anything",
            )
        )

    as_of = str(doc.get("as_of") or "")
    for row in doc.get("decisions") or []:
        did = row.get("decision_id")
        if known is not None:
            for ref in row.get("evidence") or []:
                if ref not in known:
                    failures.append(
                        _fail(
                            "synthesis-1",
                            f"{did}: evidence {ref!r} resolves to no extract record",
                        )
                    )
        if row.get("dissenting_platforms") and not row.get("dissent_basis"):
            failures.append(
                _fail(
                    "dissent-1",
                    f"{did}: a dissent is recorded with no `dissent_basis`. A divergence is never "
                    "resolved by dropping the weaker source, and a dissent with no basis is that "
                    "done silently -- the reader cannot tell whether the disagreement partitions "
                    "on platform type or is genuinely open",
                )
            )
        if platforms is not None:
            for name in [
                *(row.get("supporting_platforms") or []),
                *(row.get("dissenting_platforms") or []),
            ]:
                if name not in platforms:
                    failures.append(
                        _fail(
                            "platform-1",
                            f"{did}: {name!r} is named as supporting or dissenting and no extract "
                            "record reports that platform. A lens output must be copied from a "
                            "record that says it",
                        )
                    )
        build = str(row.get("build_first") or "")
        if (
            build.startswith("defer-until:")
            and not build[len("defer-until:") :].strip()
        ):
            failures.append(
                _fail(
                    "defer-1",
                    f"{did}: the deferral names no trigger. A deferral says what un-defers it, "
                    "taken from the migration-debt evidence -- a bare `later` is exactly what this "
                    "field replaces",
                )
            )
        if not row.get("stale") and as_of:
            for ref in row.get("evidence") or []:
                dated = contractual.get(ref)
                if dated and _days_between(dated, as_of) > STALENESS_DAYS:
                    failures.append(
                        _fail(
                            "stale-1",
                            f"{did}: it rests on the contractual record {ref!r} dated {dated}, more "
                            f"than {STALENESS_DAYS} days before this index's own {as_of}, and "
                            "carries no staleness marker. A contractual term read as current is "
                            "how a figure nobody re-checked becomes an industry standard",
                        )
                    )
                    break

    for entry in doc.get("not_applicable") or []:
        if entry.get("section") not in REPORT_SECTIONS:
            failures.append(
                _fail(
                    "section-1",
                    f"a `not-applicable` marker names section {entry.get('section')!r}, which is "
                    "not one the report has. The marker exists so an excluded angle's section says "
                    "WHY rather than rendering empty -- and one attached to a section that does "
                    "not exist renders nowhere, leaving exactly the silence it was written to "
                    "prevent",
                )
            )

    for n, entry in enumerate(doc.get("absence") or [], start=1):
        if not (entry.get("angles_ran") and entry.get("platforms_checked")):
            failures.append(
                _fail(
                    "absence-1",
                    f"absence entry {n} has no receipt: it names no angles that ran, or no "
                    "platforms checked. A zero without its receipt is indistinguishable from a "
                    "search that never happened",
                )
            )
    return failures


def _days_between(earlier: str, later: str) -> int:
    """Whole days between two ISO dates, or 0 where either will not parse.

    Args:
        earlier: The earlier ISO date.
        later: The later ISO date.

    Returns:
        The difference in days, and 0 where a date is unparseable -- the schema's own pattern owns
        that fault, and reporting it twice would send the author to two places for one defect.
    """
    import datetime

    try:
        a = datetime.date.fromisoformat(earlier)
        b = datetime.date.fromisoformat(later)
    except ValueError:
        return 0
    return (b - a).days


def _read_records(directory) -> list:
    """Every extract record in one directory, or an empty list where none was given.

    Args:
        directory: The directory to read, or None.

    Returns:
        The parsed frontmatter blocks, skipping anything that does not read as a record.
    """
    if directory is None:
        return []
    out = []
    for child in sorted(Path(directory).glob("*.md")):
        doc, _, err = read_record(child)
        if err is None and isinstance(doc, dict):
            out.append(doc)
    return out


def _build_parser() -> argparse.ArgumentParser:
    """The CLI surface, separated so a test can enumerate what is REGISTERED.

    #51: a sibling shipped two subparsers `main()` never routed — one fell through to another
    branch and raised, the other hit a whole-file YAML read before its own dispatch. Both
    survived a 117-test suite because every test called the `validate_*` functions directly. A
    test deriving the subcommand list from THIS function cannot miss a third one added later.
    """
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    km = sub.add_parser(
        "keyword-map", help="validate a platform-and-mechanism vocabulary map"
    )
    km.add_argument("file", type=Path)
    se = sub.add_parser("search", help="validate one angle's search output")
    se.add_argument("file", type=Path)
    se.add_argument("--keyword-map", dest="keyword_map", type=Path, required=True)
    ex = sub.add_parser("extract", help="validate one extract record")
    ex.add_argument("file", type=Path)
    sy = sub.add_parser("synthesis", help="validate the decision index")
    sy.add_argument("file", type=Path)
    sy.add_argument("--extracts", type=Path)
    sy.add_argument("--baseline-extracts", type=Path)
    # The frozen queue is the ONLY record of what extraction was ASKED to produce. The index can
    # see only the records that EXIST, so a row that wrote no file is invisible to it.
    sy.add_argument("--queue", type=Path)
    return parser


def registered_subcommands() -> set[str]:
    """Every subcommand the parser actually registers. Derived, never hand-listed."""
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
                "scripts/validate_platform_ecosystem_prior_art.py ...",
            )
        )
        return 2
    args = _build_parser().parse_args(argv)

    # The registry ships INSIDE this package, so a defect in it is a package fault rather than a
    # fault in the artifact under test. Reporting it at exit 1 would send a caller off to edit a
    # map that may be perfectly fine, so it exits 2 with the could-not-be-used class — and it runs
    # BEFORE either subcommand touches its input, not on one path only.
    try:
        registry = load_registry()
    except (OSError, yaml.YAMLError, UnicodeDecodeError) as exc:
        print(_fail("registry-unreadable", str(exc)))
        return 2
    # Unreadable and unparseable were covered; WRONG-SHAPED was not, and it reaches the same
    # place — a registry that is valid YAML but a list, a scalar or empty raised out of
    # `anchor_failures` as a traceback at exit 1, which is the artifact-fault code.
    if not isinstance(registry, dict):
        print(
            _fail(
                "registry-unreadable",
                f"the shipped registry parsed as {type(registry).__name__}, not a mapping",
            )
        )
        return 2
    reg_errs = anchor_failures(registry)
    if reg_errs:
        for line in reg_errs:
            print(line)
        return 2

    # The extract record is a `.md` carrying frontmatter, not a YAML file, so the generic reader
    # would report a correct record as unparseable. Its own reader runs inside its branch.
    if args.cmd == "extract":
        doc, err = None, None
    else:
        doc, err = _read(args.file)
    if err:
        print(err)
        return 2

    if args.cmd == "keyword-map":
        failures = validate_keyword_map(doc, registry)
    elif args.cmd == "extract":
        record, body, rerr = read_record(args.file)
        if rerr:
            print(rerr)
            return 2
        failures = validate_extract(record, body, args.file)
    elif args.cmd == "synthesis":
        wave = _read_records(args.extracts)
        failures = []
        if not wave:
            # WHATEVER the reason the records did not arrive -- flag absent, path wrong, directory
            # empty -- the cross-check did not run, and saying so IS the report.
            cause = (
                "no `--extracts`, so evidence resolution was NOT checked"
                if args.extracts is None
                else "the `--extracts` directory supplied no readable record, so evidence "
                "resolution was NOT checked"
            )
            failures.append(
                _fail(
                    "extracts-crosscheck-skipped",
                    f"{cause}. Exit 1 on its own: the dispatcher can supply the records and re-run, "
                    "and the index is not what needs repairing",
                )
            )
        failures += _queue_reconciliation(args, wave)
        # The queue reconciliation is PER-WAVE; evidence resolution is CUMULATIVE. One directory
        # cannot serve both scopes, which is why they are two flags.
        resolvable = [*wave, *_read_records(args.baseline_extracts)] if wave else None
        failures += validate_synthesis(doc, resolvable)
    else:
        kmap, kerr = _read(args.keyword_map)
        if kerr:
            print(kerr)
            return 2
        # The keyword map is a CALLER input, and an unusable one is not a fault in the artifact
        # under test. Unchecked, a list-shaped map crashed on `.get` and a `platforms`-less one
        # produced `slug-not-in-map` against every candidate of a correct file — exit 1 either
        # way, which sends the author off to edit an artifact that is fine. That is precisely the
        # harm the exit-2 class exists to prevent, so the map is validated as a map first.
        kmap_errs = _schema_errors(kmap, "platform-vocabulary-map")
        if kmap_errs:
            print(
                _fail(
                    "keyword-map-unusable",
                    f"{args.keyword_map} is not a valid vocabulary map, so the search output "
                    f"cannot be judged against it: {kmap_errs[0]}",
                )
            )
            return 2
        failures = validate_search(doc, kmap, registry)

    for line in failures:
        # DERIVED from the rule id, never a paired print: a SKIP line written out separately is a
        # line that can go missing when the rule is renamed.
        rule = line.removeprefix("FAIL ").split(":", 1)[0]
        if rule.endswith("-crosscheck-skipped"):
            print(f"SKIP {rule.removesuffix('-skipped')}")
        print(line)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
