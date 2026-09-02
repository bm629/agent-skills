"""Deterministic gate for the regulatory prior-art survey (wave 1).

Two kinds: the regulatory scope map, and one angle's search output.

Exit codes, and the distinction is load-bearing:
  0  clean
  1  the ARTIFACT has findings — the author has something to fix
  2  it could not be used at all — a fault in the package, the registry, the invocation or the
     input file. Never the author's to fix by editing the artifact, which is why reporting one of
     these as a 1 sends someone off to edit a file that is fine.

Every finding is one line, ``FAIL <rule-id>: <message>``, so a caller can grep the rule.

This gate checks SHAPE. Whether an instrument actually binds this scope, whether a quote supports
its claim, whether an authority ranking is defensible — those are the reviewing twin's, and each of
its conditions names the rule that owns the other half.
"""

from __future__ import annotations

import argparse
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
SCHEMAS = HERE.parent / "schemas"
REGISTRY = Path(os.environ.get("REGULATORY_REGISTRY_OVERRIDE") or
                (HERE.parent / "references" / "source-registry.yaml"))

#: The classification leaves a conditional angle's `trigger_anchor` may root on. An anchor on an
#: OPTIONAL field fails closed for every map that omits it, which is silent and total. Exported
#: because the shared root guard SKIPS its constant check without it, and a silent skip is a green
#: test checking nothing.
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

_TRIGGERS = ("always", "conditional")

_INSTALL = (
    "uv run --no-project --with pyyaml --with jsonschema "
    "python scripts/validate_regulatory_prior_art.py"
)


def _fail(rule: str, message: str) -> str:
    """One finding, in the one format a caller greps."""
    return f"FAIL {rule}: {message}"


def _probe_method_failures(where: str, block: object) -> list[str]:
    """`probe_method` is an OBJECT, not prose.

    A criterion that only asserts "present and non-empty" is satisfied by ``probe_method: "yes"``,
    which records nothing and reads as recorded.
    """
    out: list[str] = []
    if not isinstance(block, dict):
        return [_fail("probe-method-shape",
                      f"{where} probe method is {type(block).__name__}, not a mapping; a status "
                      "with no request behind it is not evidence, and a string here records none")]
    method = block.get("method")
    if not isinstance(method, str) or not method.strip():
        out.append(_fail("probe-method-shape", f"{where} probe method declares no `method`"))
    headers = block.get("headers", {})
    if not isinstance(headers, dict):
        out.append(_fail("probe-method-shape", f"{where} `headers` is not a mapping"))
    else:
        bad = sorted(k for k, v in headers.items() if not isinstance(v, str))
        if bad:
            out.append(_fail("probe-method-shape",
                             f"{where} header values must be strings; {bad} are not"))
    ua = block.get("user_agent")
    if ua is not None and not isinstance(ua, str):
        out.append(_fail("probe-method-shape", f"{where} `user_agent` is not a string"))
    return out


def registry_failures(doc: object) -> list[str]:
    """Faults in the REGISTRY. Every one is exit 2: only an author can cause these, and a false
    positive at dispatch time parks every ticket in a live survey."""
    if not isinstance(doc, dict):
        return [_fail("not-a-mapping",
                      f"the source registry parsed as {type(doc).__name__}, not a mapping")]

    out: list[str] = []
    out += _probe_method_failures("registry-wide default:", doc.get("probe_default"))

    rows = [s for s in (doc.get("sources") or []) if isinstance(s, dict)]
    ids = {s.get("id") for s in rows if s.get("id")}

    for row in rows:
        rid = row.get("id")
        if "probe_method" in row:
            out += _probe_method_failures(f"source {rid!r}:", row["probe_method"])
        if "fallback" in row and row.get("fallback") is None:
            if not str(row.get("fallback_rationale") or "").strip():
                out.append(_fail(
                    "terminal-needs-rationale",
                    f"source {rid!r} declares `fallback: null` with no `fallback_rationale`; a "
                    "terminal is a claim that no second channel exists, so say why"))

    # The fallback graph. A self-fallback and a null both mean TERMINAL — a sibling registry uses
    # the first idiom and documents it, and reading it as a cycle would report ten false defects
    # there. The defect is a cycle through two or more DISTINCT rows: it promises a second channel
    # and returns to the first.
    edges: dict[str, str | None] = {}
    for row in rows:
        rid, f = row.get("id"), row.get("fallback")
        if rid:
            edges[rid] = None if (not isinstance(f, str) or f == rid) else f
    for rid, dest in edges.items():
        if dest is not None and dest not in ids:
            out.append(_fail("fallback-unresolvable",
                             f"source {rid!r} falls back to {dest!r}, which is not a row; a route "
                             "on paper only is worse than none"))
    done: set[str] = set()
    seen_cycles: set[tuple[str, ...]] = set()

    def walk(node: str, stack: list[str]) -> None:
        if node in stack:
            seen_cycles.add(tuple(stack[stack.index(node):] + [node]))
            return
        if node in done:
            return
        nxt = edges.get(node)
        if nxt:
            walk(nxt, stack + [node])
        done.add(node)

    for rid in edges:
        walk(rid, [])
    for cyc in sorted(seen_cycles):
        out.append(_fail("fallback-cycle",
                         "fallback cycle " + " -> ".join(cyc) + "; every hop promises a second "
                         "channel and the chain returns to the first, so there is none"))

    for angle in (doc.get("angles") or []):
        if not isinstance(angle, dict):
            out.append(_fail("angle-id-required", "an angle entry is not a mapping"))
            continue
        aid = angle.get("id")
        if not aid:
            out.append(_fail("angle-id-required", "an angle declares no `id`"))
            continue
        trigger = angle.get("trigger")
        if trigger not in _TRIGGERS:
            out.append(_fail("trigger-must-be-known",
                             f"angle {aid!r} declares trigger {trigger!r}; known: {_TRIGGERS}"))
        anchor = angle.get("trigger_anchor")
        if trigger == "conditional":
            if anchor is None:
                out.append(_fail("anchor-required",
                                 f"angle {aid!r} is conditional and names no `trigger_anchor`"))
            elif not isinstance(anchor, list):
                out.append(_fail("anchor-must-be-a-list",
                                 f"angle {aid!r} declares a scalar `trigger_anchor`; one anchor "
                                 "field is a list of one, and a scalar hides the second"))
            else:
                for leaf in anchor:
                    if leaf not in REQUIRED_CAPABILITY_FIELDS:
                        out.append(_fail(
                            "anchor-must-be-required",
                            f"angle {aid!r} anchors on {leaf!r}, which is not a REQUIRED "
                            "classification leaf; an optional anchor fails CLOSED for every map "
                            "that omits it, silently and for exactly the products that need it"))
        elif anchor is not None:
            out.append(_fail("anchor-only-on-conditional",
                             f"angle {aid!r} is always-on and carries a `trigger_anchor`; it has "
                             "no precondition to anchor"))

        srcs = angle.get("sources") or []
        for s in srcs:
            if s not in ids:
                out.append(_fail("angle-source-unknown",
                                 f"angle {aid!r} names source {s!r}, which is not a registry row"))
        fb = angle.get("fallback")
        if fb is not None and fb not in srcs:
            out.append(_fail("angle-fallback-unreachable",
                             f"angle {aid!r} falls back to {fb!r}, which is not in its own source "
                             "list; an angle cannot walk a channel it does not carry"))
    return out


def _read_yaml(path: Path) -> tuple[object | None, str | None]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, f"{path}: {exc.strerror or exc}"
    except UnicodeDecodeError as exc:
        return None, f"{path}: not UTF-8 ({exc.reason})"
    try:
        return yaml.safe_load(text), None
    except yaml.YAMLError as exc:
        return None, f"{path}: {exc}"


def main(argv: list[str] | None = None) -> int:
    if _MISSING_DEPENDENCY is not None:
        print(_fail("dependency-missing",
                    f"{_MISSING_DEPENDENCY!r} is not installed. Run: {_INSTALL} <subcommand> …"))
        return 2

    parser = argparse.ArgumentParser(prog="validate_regulatory_prior_art.py")
    sub = parser.add_subparsers(dest="kind", required=True)
    m = sub.add_parser("keyword-map", help="validate a regulatory scope map (wave 0)")
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

    findings: list[str] = []
    if args.kind == "keyword-map":
        findings = validate_keyword_map(doc, reg)
    else:
        kmap, err = _read_yaml(args.map_path)
        if err is not None:
            print(_fail("keyword-map-invalid", err))
            return 2
        findings = validate_search(doc, kmap, reg)

    for line in findings:
        print(line)
    return 1 if findings else 0


def validate_keyword_map(doc: object, registry: dict) -> list[str]:
    """The map's rules. C2b fills this in."""
    return []


def validate_search(doc: object, keyword_map: object, registry: dict) -> list[str]:
    """The search output's rules. C2c and C2d fill this in."""
    return []


if __name__ == "__main__":
    sys.exit(main())
