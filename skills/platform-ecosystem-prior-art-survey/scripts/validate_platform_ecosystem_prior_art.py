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
import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
SCHEMAS = HERE.parent / "schemas"
DEFAULT_REGISTRY = HERE.parent / "references" / "source-registry.yaml"

#: Capability-map paths a conditional trigger may ANCHOR on — the fields the map's own schema
#: marks REQUIRED, so a predicate resting on one always evaluates.
#:
#: The rule is about the SHAPE of the predicate, not about every field in it. An optional field
#: sitting beside a required one in an OR only ever ADDS firings, so it fails OPEN and is
#: legitimate — those are recorded as `widening_legs`. What fails CLOSED, silently, is an AND with
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

#: A date that starts with an ISO-8601 calendar date. A bare date is legitimate: many sources
#: state a day and no time, and rejecting that would push producers toward inventing a time.
_ISO_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}")


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
        conditional = angle.get("trigger") == "conditional"
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
                        "mark required; an optional leg belongs in widening_legs",
                    )
                )
    return out


def _angle_ids(registry: dict) -> set[str]:
    return {a["id"] for a in registry.get("angles") or []}


def validate_keyword_map(doc: dict, registry: dict | None = None) -> list[str]:
    """Shape of the wave-0 platform-and-mechanism vocabulary map."""
    reg = registry if registry is not None else load_registry()
    out = _schema_errors(doc, "platform-vocabulary-map")
    if out:
        return out

    meta = doc.get("meta") or {}
    if not _ISO_PREFIX.match(str(meta.get("retrieved_at", ""))):
        out.append(
            _fail(
                "timestamp-format", "meta.retrieved_at must start with an ISO-8601 date"
            )
        )

    declared = _angle_ids(reg)
    seen = set()
    for verdict in doc.get("angle_applicability") or []:
        aid = verdict.get("angle_id")
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
    doc: dict, keyword_map: dict, registry: dict | None = None
) -> list[str]:
    """Shape of one angle's search output.

    `registry` is accepted for parity with the sibling validators and is consumed by the
    type-specific rules (C2b), which resolve every cell and candidate `source_id` against it.
    The inherited rules below need only the artifact.
    """
    out = _schema_errors(doc, "search-output")
    if out:
        return out

    meta = doc.get("meta") or {}
    if not _ISO_PREFIX.match(str(meta.get("retrieved_at", ""))):
        out.append(
            _fail(
                "timestamp-format", "meta.retrieved_at must start with an ISO-8601 date"
            )
        )

    outcome = doc.get("outcome")
    cells = doc.get("coverage") or []
    if outcome == "not_run" and cells:
        out.append(
            _fail(
                "not-run-owes-no-cells",
                "an unrun angle owes NO coverage cells; empty ones manufacture zeros that look like searches",
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
    if summary is not None and summary != counts:
        out.append(
            _fail(
                "summary-mismatch",
                f"retrieval_summary.status_counts {summary} does not reconcile with the cells {counts}; "
                "the summary duplicates the cells deliberately, and a discrepancy is the signal that a "
                "failure was laundered into a zero",
            )
        )

    bound = doc.get("bound") or {}
    if bound.get("bound") and not str(bound.get("ordering") or "").strip():
        out.append(
            _fail(
                "bound-needs-ordering",
                "the cap BOUND but records no ordering; an unrecorded ordering makes the truncation unreviewable",
            )
        )
    return out


def _read(path: Path) -> tuple[object | None, str | None]:
    try:
        return yaml.safe_load(path.read_text()), None
    except OSError as exc:
        return None, _fail("input", f"{path}: {exc.strerror or exc}")
    except yaml.YAMLError as exc:
        return None, _fail("input", f"{path}: not valid YAML: {exc}")


def main(argv: list[str] | None = None) -> int:
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
    args = parser.parse_args(argv)

    # The registry ships INSIDE this package, so a defect in it is a package fault rather than a
    # fault in the artifact under test. Reporting it at exit 1 would send a caller off to edit a
    # map that may be perfectly fine, so it exits 2 with the could-not-be-used class — and it runs
    # BEFORE either subcommand touches its input, not on one path only.
    try:
        registry = load_registry()
    except (OSError, yaml.YAMLError) as exc:
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
        failures = validate_search(doc, kmap, registry)

    for line in failures:
        print(line)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
