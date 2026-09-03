"""Deterministic gate for the integrations prior-art survey (wave 1).

Two kinds: the integration vocabulary map, and one angle's search output.

Exit codes, and the distinction is load-bearing:
  0  clean
  1  the ARTIFACT has findings — the author has something to fix. `schema` is HERE, because a
     schema-invalid artifact is exactly what its author can repair.
  2  it could not be used at all — a fault in the package, the registry, the invocation or the
     input file. Never the author's to fix by editing the artifact, which is why reporting one of
     these as a 1 sends someone off to edit a file that is fine.

Every finding is one line, ``FAIL <rule-id>: <message>``, so a caller can grep the rule.

This gate checks SHAPE. Whether a locator really is the vendor's own, whether a quote supports its
claim, whether an authority band is defensible — those are the reviewing twin's, and each of its
conditions names the rule that owns the other half.
"""

from __future__ import annotations

import argparse
import json
import os
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
PKG = HERE.parent
REGISTRY = Path(os.environ.get("INTEGRATIONS_REGISTRY") or (PKG / "references" / "source-registry.yaml"))
SCHEMAS = PKG / "schemas"
_INSTALL = "uv run --with pyyaml --with jsonschema python validate_integrations_prior_art.py"

#: Derived from the capability-map schema's required leaves, and checked against it by the shared
#: root guard. A hand-maintained copy of this set is what shipped as a defect in a sibling.
REQUIRED_CAPABILITY_FIELDS = (
    "archetype.primary",
    "business.platform.type",
    "data_ml.ml_involvement",
    "domain.audience",
    "integrations.complexity",
    "integrations.expected",
    "regulatory.applies",
    "scale.availability_target",
    "scale.concurrency",
    "scale.data_volume",
    "scale.geo_distribution",
    "scale.real_time",
    "ui.complexity",
    "ui.has_ui",
)

#: The registry-integrity rules that return EXIT 2, asserted by EQUALITY in the suite so a rule
#: added later must pick a side rather than inherit one. Every member is a fault only an AUTHOR OF
#: THIS PACKAGE can cause — never the artifact author, who cannot edit the registry.
EXIT2_REGISTRY_RULES = frozenset(
    {
        "complete-listing-declared",
        "yields-declared",
        "authority-band-known",
        "probe-method-shape",
        "terminal-needs-rationale",
        "fallback-cycle",
        "fallback-unresolvable",
        "seed-input-not-widening",
    }
)

AUTHORITY_BANDS = ("first-party", "connector-catalog", "aggregator", "community")
COMPLETE_LISTING = (True, False, "n/a")


def _fail(rule: str, message: str) -> str:
    return f"FAIL {rule}: {message}"


def _read_yaml(path: Path) -> tuple[object, str | None]:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")), None
    except FileNotFoundError:
        return None, f"{path} does not exist"
    except OSError as exc:
        return None, f"{path} could not be read: {exc}"
    except yaml.YAMLError as exc:  # type: ignore[union-attr]
        return None, f"{path} is not valid YAML: {exc}"


def _schema_errors(doc: object, name: str) -> list[str]:
    """The JSON Schemas run FIRST and the caller returns EARLY on any finding.

    A sibling loaded its schemas nowhere: deleting a required field produced ZERO findings while
    silently disabling eight rules that read it. Running them first and returning early is what
    stops every rule below comparing against a shape that is not there.
    """
    try:
        schema = json.loads((SCHEMAS / f"{name}.schema.json").read_text(encoding="utf-8"))
    except OSError as exc:
        return [_fail("schema", f"{name}.schema.json could not be read: {exc}")]
    errors = sorted(Draft202012Validator(schema).iter_errors(doc), key=lambda e: list(e.path))
    return [
        _fail("schema", f"{'/'.join(str(p) for p in e.path) or '<root>'}: {e.message}")
        for e in errors
    ]


# =============================================================================================
# REGISTRY INTEGRITY — every finding here is EXIT 2.
# =============================================================================================


def registry_failures(reg: object) -> list[str]:
    """Faults in the REGISTRY. Every one is exit 2: only an author of this package can cause
    these, and a false positive at dispatch time parks every ticket in a live survey."""
    out: list[str] = []
    if not isinstance(reg, dict):
        return [_fail("registry-unreadable", "the registry is not a mapping")]

    sources = reg.get("sources")
    if not isinstance(sources, list) or not sources:
        return [_fail("registry-unreadable", "the registry declares no `sources` list")]

    default = reg.get("probe_default")
    if not isinstance(default, dict) or not str(default.get("method") or "").strip():
        out.append(
            _fail(
                "probe-method-shape",
                "the registry declares no `probe_default` with a `method`; without it a row "
                "carrying no `probe_method` has no declared method at all",
            )
        )

    ids: list[str] = []
    for row in sources:
        if not isinstance(row, dict):
            out.append(_fail("registry-unreadable", "a `sources` entry is not a mapping"))
            continue
        rid = str(row.get("id") or "?")
        ids.append(rid)

        if not str(row.get("yields") or "").strip():
            out.append(
                _fail("yields-declared", f"row {rid!r} declares no `yields`; a row that cannot state its yield is a row nobody probed")
            )
        if "complete_listing" not in row:
            out.append(
                _fail("complete-listing-declared", f"row {rid!r} declares no `complete_listing`; the value is derived from a stated rule, and an unassigned row would otherwise pass in silence")
            )
        elif row["complete_listing"] not in COMPLETE_LISTING:
            out.append(
                _fail("complete-listing-declared", f"row {rid!r} declares complete_listing {row['complete_listing']!r}, which is not one of true | false | n/a")
            )
        if row.get("authority_band") not in AUTHORITY_BANDS:
            out.append(
                _fail("authority-band-known", f"row {rid!r} declares authority_band {row.get('authority_band')!r}, which is not one of {' > '.join(AUTHORITY_BANDS)}")
            )
        pm = row.get("probe_method")
        if pm is not None and (not isinstance(pm, dict) or not str(pm.get("method") or "").strip()):
            out.append(
                _fail("probe-method-shape", f"row {rid!r} carries a `probe_method` that is not an object with a `method`; a criterion asserting only 'present and non-empty' is satisfied by `probe_method: \"yes\"`")
            )
        if row.get("fallback") is None and not str(row.get("fallback_rationale") or "").strip():
            out.append(
                _fail("terminal-needs-rationale", f"row {rid!r} is a TERMINAL (`fallback: null`) and states no rationale; null alone is a hole, null with a rationale is a decision")
            )

    known = set(ids)
    edges = {
        str(r.get("id")): r.get("fallback")
        for r in sources
        if isinstance(r, dict)
    }
    for rid, target in edges.items():
        if target is not None and target not in known:
            out.append(_fail("fallback-unresolvable", f"row {rid!r} falls back to {target!r}, which is not a row in this registry"))

    for start in edges:
        seen, node = {start}, start
        while True:
            nxt = edges.get(node)
            if nxt is None or nxt not in edges:
                break
            if nxt in seen:
                out.append(_fail("fallback-cycle", f"the fallback graph cycles through {nxt!r}; the graph is a FOREST, and requiring every row to name a fallback in a finite graph guarantees a cycle by pigeonhole"))
                break
            seen.add(nxt)
            node = nxt

    for angle in reg.get("angles") or []:
        if not isinstance(angle, dict):
            continue
        aid = str(angle.get("id") or "?")
        if angle.get("trigger") == "always" and (angle.get("widening_legs") or []):
            out.append(
                _fail(
                    "seed-input-not-widening",
                    f"angle {aid!r} is always-on and declares `widening_legs`; a widening leg is a "
                    "PREDICATE term and an always-on angle carries no predicate. `seed_input` is "
                    "the field for a term that seeds a FILTER without gating it",
                )
            )

    return out


# =============================================================================================
# ARTIFACT VALIDATION — every finding here is EXIT 1.
# =============================================================================================


def validate_keyword_map(doc: object, reg: dict) -> list[str]:
    out = _schema_errors(doc, "integration-vocabulary-map")
    if out:
        return out
    return out


def validate_search(doc: object, reg: dict, kmap: object) -> list[str]:
    out = _schema_errors(doc, "search-output")
    if out:
        return out
    return out


def main(argv: list[str] | None = None) -> int:
    if _MISSING_DEPENDENCY is not None:
        print(_fail("dependency-missing", f"{_MISSING_DEPENDENCY!r} is not installed. Run: {_INSTALL} <subcommand> …"))
        return 2

    parser = argparse.ArgumentParser(prog="validate_integrations_prior_art.py")
    sub = parser.add_subparsers(dest="kind", required=True)
    m = sub.add_parser("keyword-map", help="validate an integration vocabulary map (wave 0)")
    m.add_argument("path", type=Path)
    s = sub.add_parser("search", help="validate one angle's search output (wave 1)")
    s.add_argument("path", type=Path)
    s.add_argument("--keyword-map", dest="map_path", type=Path, required=True)
    args = parser.parse_args(argv)

    reg, err = _read_yaml(REGISTRY)
    if err is not None:
        print(_fail("registry-unreadable", err))
        return 2
    reg_findings = registry_failures(reg)
    if reg_findings:
        for line in reg_findings:
            print(line)
        return 2

    doc, err = _read_yaml(args.path)
    if err is not None:
        print(_fail("input", err))
        return 2

    if args.kind == "keyword-map":
        findings = validate_keyword_map(doc, reg)
    else:
        kmap, err = _read_yaml(args.map_path)
        if err is not None:
            print(_fail("keyword-map-invalid", err))
            return 2
        kmap_errs = _schema_errors(kmap, "integration-vocabulary-map")
        if kmap_errs:
            print(_fail("keyword-map-invalid", f"{args.map_path} does not satisfy the map schema: {kmap_errs[0]}"))
            return 2
        findings = validate_search(doc, reg, kmap)

    for line in findings:
        print(line)
    return 1 if findings else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
