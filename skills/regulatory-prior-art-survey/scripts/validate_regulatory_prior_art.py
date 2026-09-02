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
import hashlib
import os
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

_PREFIX_CAP = 80

#: The marker the hashing branch appends. The identity branch must never return a string that
#: looks like one, or the two branches share an output namespace and injectivity is lost.
_HASHED_STEM = re.compile(r"--[0-9a-f]{12}$")

#: Six externally-owned grammars. `WEB-` has none: it is the honest fallback for an instrument with
#: no registry identity, and giving it a shape would force one onto the single class that has none.
#: Each pattern is written to reject a PLAUSIBLE wrong id -- `32016R679` is one digit short and
#: reads exactly like a real CELEX number.
ID_GRAMMARS = {
    # sector + 4-digit year + 1-2 letter descriptor + 4-digit number. Sector 3 is legislation,
    # sector 6 is case law, and both resolve through the same channel.
    "CELEX": ("celex-grammar", re.compile(r"^[1-9]\d{4}[A-Z]{1,2}\d{4}$")),
    # <title>-<part>. Titles run 1-50; a part is at most four digits.
    "CFR": ("cfr-citation-grammar", re.compile(r"^([1-9]|[1-4]\d|50)-\d{1,4}$")),
    "USC": ("usc-citation-grammar", re.compile(r"^([1-9]|[1-4]\d|5[0-4])-\d{1,5}$")),
    # SP-<series>-<number><revision>, e.g. SP-800-53r5.
    "NIST": ("nist-pub-grammar", re.compile(r"^SP-\d{3}-\d{1,3}(r\d+)?$")),
    # [IEC-]<number>[-<part>]-<4-digit year>. The YEAR is what makes a standard citable.
    "ISO": ("iso-number-grammar", re.compile(r"^(IEC-)?\d{3,5}(-\d{1,3})*-\d{4}$")),
    # <BODY>-<NAME>-<version>. The body is what distinguishes WCAG 2.2 from anyone else's 2.2.
    "STD": ("std-slug-grammar", re.compile(r"^[A-Z][A-Z0-9]*-[A-Za-z0-9]+-\d+(\.\d+)*$")),
}

#: L-10's nine families. A verdict per family, always — a family silently absent from the receipt
#: is a validator failure rather than a judgement call.
SECTOR_FAMILIES = (
    "health", "financial-payments", "children-minors", "public-sector", "employment-hr",
    "insurance", "education", "telecom-critical-infrastructure", "export-controlled",
)

#: Axes whose terms the corpus spells more than one way. An instrument is cited by short name, by
#: identifier and by nickname; a jurisdiction is not.
_EXPANSION_FLOOR_AXES = ("instrument", "sector", "obligation-dimension", "control-catalog",
                         "model-term", "ui-term", "platform-role", "transfer-mechanism")

#: Axes whose terms are ordinary English, which is where the homonym corpus is.
_NEGATIVE_TERM_AXES = ("sector", "obligation-dimension")

_INSTALL = (
    "uv run --no-project --with pyyaml --with jsonschema "
    "python scripts/validate_regulatory_prior_art.py"
)


def _fail(rule: str, message: str) -> str:
    """One finding, in the one format a caller greps."""
    return f"FAIL {rule}: {message}"


def record_filename(item_id: str) -> str:
    """Return the filename stem a record for ``item_id`` must be written under.

    An ``item_id`` is an IDENTITY and may legitimately contain characters a filename may not. This
    type's ids are CITATIONS -- `ISO/IEC 27001` carries a slash, `45 CFR 164.312` carries spaces
    and dots, `AT-2(2)` carries parentheses -- so the sanitizing branch is not an edge case here.

    Two parts, and the second is what makes the mapping injective:

    (a) identity for anything already filename-safe;
    (b) the identity branch REFUSES an input already shaped like a hashed stem. Without (b) the two
        branches share an output namespace and ``f(f(x)) == f(x)`` for some x -- a fixed point that
        merges two records into one filename. Because the extract cursor is disk-authoritative, the
        orphaned row is then re-spawned on every wake while looking perfectly valid.

    The digest covers the WHOLE id, so two ids differing only where the sanitizer collapses still
    get different names.

    Args:
        item_id: The record's canonical identity, verbatim.

    Returns:
        A filename stem, without an extension.
    """
    if re.fullmatch(r"[A-Za-z0-9._-]+", item_id) and not _HASHED_STEM.search(item_id):
        return item_id
    prefix = re.sub(r"[^A-Za-z0-9._-]+", "-", item_id)[:_PREFIX_CAP].strip("-")
    digest = hashlib.sha256(item_id.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}--{digest}" if prefix else f"--{digest}"


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


def _term_key(term: object) -> str:
    """Fold a term to the form two groups would collide on.

    `GDPR` and ` gdpr ` reach the same corpus, so matching on the literal string would let a term
    be sited twice by changing its case.
    """
    return " ".join(str(term).split()).casefold() if isinstance(term, str) else ""


def validate_keyword_map(doc: object, registry: dict) -> list[str]:
    """The regulatory scope map's rules."""
    if not isinstance(doc, dict):
        return [_fail("schema", f"the map parsed as {type(doc).__name__}, not a mapping")]

    out: list[str] = []
    groups = [g for g in (doc.get("groups") or []) if isinstance(g, dict)]
    guard = doc.get("scope_guard") or {}
    angles = {a["id"]: a for a in (registry.get("angles") or []) if isinstance(a, dict) and a.get("id")}

    # ── ids ──────────────────────────────────────────────────────────────────
    seen_ids: set[str] = set()
    for g in groups:
        gid = g.get("id")
        if gid in seen_ids:
            out.append(_fail("group-id-unique",
                             f"group id {gid!r} is minted twice; two angles spelling one group two "
                             "ways produces two rows for one thing and the dedupe never fires"))
        seen_ids.add(gid)

    # ── axes: populated, or DECLARED absent, but never both ──────────────────
    populated = {g.get("type") for g in groups}
    absent = set(guard.get("absent_types") or [])
    both = sorted(populated & absent)
    for t in both:
        out.append(_fail("group-type-accounted",
                         f"axis {t!r} is declared absent AND carries groups; the two readings "
                         "cannot both hold and a reader takes whichever it meets first"))
    holding = {v.get("angle_id") for v in (doc.get("angle_applicability") or [])
               if isinstance(v, dict) and v.get("holds")}
    needed: set[str] = set()
    for aid in holding:
        a = angles.get(aid)
        if a:
            needed |= set(a.get("applicable_group_types") or [])
    for t in sorted(needed - populated - absent):
        out.append(_fail("group-type-accounted",
                         f"axis {t!r} is searched by an angle that HOLDS, and is neither populated "
                         "nor listed in scope_guard.absent_types; an unaccounted axis is "
                         "indistinguishable from one nobody thought about"))

    # ── vocabulary ───────────────────────────────────────────────────────────
    for g in groups:
        gid, gtype = g.get("id"), g.get("type")
        exps = g.get("expansions") or []
        cap = g.get("expansion_cap")
        if isinstance(cap, int) and len(exps) > cap:
            out.append(_fail("expansion-cap",
                             f"group {gid!r} carries {len(exps)} expansions against its own cap of "
                             f"{cap}; an unbounded set turns one query into an unreviewable sweep"))
        if gtype in _EXPANSION_FLOOR_AXES and not exps:
            out.append(_fail("expansion-floor",
                             f"group {gid!r} is a {gtype} group with no expansions; this corpus "
                             "cites one instrument by short name, by identifier and by nickname, "
                             "and a single-term query reaches only the corpus that already uses "
                             "your word"))
        if gtype in _NEGATIVE_TERM_AXES and not (g.get("negative_terms") or []):
            out.append(_fail("negative-terms-required",
                             f"group {gid!r} is a {gtype} group with no negative_terms; these are "
                             "ordinary English words, and a term with no exclusions returns "
                             "another field's corpus as though it were yours"))

    # ── one term, one group — DECLARED where it is two ───────────────────────
    declared = {_term_key(d.get("term")): d
                for d in (guard.get("shared_terms") or []) if isinstance(d, dict)}
    sited: dict[str, set[str]] = {}
    for g in groups:
        for term in [g.get("canonical"), *(g.get("expansions") or [])]:
            key = _term_key(term)
            if key and g.get("id"):
                sited.setdefault(key, set()).add(g["id"])
    for key, d in sorted(declared.items()):
        if len(sited.get(key, set())) < 2:
            out.append(_fail("term-sited-once",
                             f"scope_guard.shared_terms declares {d.get('term')!r} shared, and it "
                             f"is sited in {len(sited.get(key, set()))} group(s); a declaration "
                             "for a collision that does not exist records something that did not "
                             "happen, and reads as handled exactly like a real one"))
    for key, gids in sorted(sited.items()):
        if len(gids) < 2:
            continue
        d = declared.get(key)
        if d is None:
            out.append(_fail("term-sited-once",
                             f"term {key!r} is sited in {len(gids)} groups "
                             f"({', '.join(sorted(gids))}) and is not declared in "
                             "scope_guard.shared_terms; it reaches two cells, item_id is unique "
                             "across the artifact, and so whatever both surface is filed under one "
                             "cell and silently missing from the other"))
        elif d.get("owner") not in gids:
            out.append(_fail("term-sited-once",
                             f"term {key!r} is declared shared with owner {d.get('owner')!r}, "
                             f"which is not one of the groups it reaches "
                             f"({', '.join(sorted(gids))}); a declaration that does not resolve "
                             "reads as handled and is worse than none"))

    # ── angle verdicts ───────────────────────────────────────────────────────
    verdicts = [v for v in (doc.get("angle_applicability") or []) if isinstance(v, dict)]
    seen_v: set[str] = set()
    for v in verdicts:
        aid = v.get("angle_id")
        if aid in seen_v:
            out.append(_fail("angle-verdict-unique",
                             f"two verdicts for angle {aid!r}; a reader takes whichever it meets "
                             "first, and the two can disagree"))
        seen_v.add(aid)
        if aid not in angles:
            out.append(_fail("angle-unknown",
                             f"a verdict names angle {aid!r}, which the registry does not declare"))
        elif angles[aid].get("trigger") == "always" and not v.get("holds"):
            out.append(_fail("always-on-angle-holds",
                             f"angle {aid!r} is ALWAYS-ON and the map records holds: false; it has "
                             "no precondition to fail, so this is a producer error rather than a "
                             "fact about the scope"))
    for aid in sorted(set(angles) - seen_v):
        out.append(_fail("angle-verdict-complete",
                         f"no verdict for angle {aid!r}; an angle that never ran and an angle that "
                         "ran and found nothing are different facts, and only a recorded verdict "
                         "distinguishes them before the search wave starts"))

    # ── the sector receipt ───────────────────────────────────────────────────
    fams = [s.get("family") for s in (doc.get("sector_scoping") or []) if isinstance(s, dict)]
    for fam in SECTOR_FAMILIES:
        n = fams.count(fam)
        if n == 0:
            out.append(_fail("sector-verdict-complete",
                             f"no verdict for sector family {fam!r}; L-10 requires one per family, "
                             "and a family silently absent is a validator failure rather than a "
                             "judgement call"))
        elif n > 1:
            out.append(_fail("sector-verdict-complete",
                             f"{n} verdicts for sector family {fam!r}; they can disagree"))

    # ── the probe ────────────────────────────────────────────────────────────
    probe = doc.get("probe") or {}
    if not str(probe.get("note") or "").strip():
        out.append(_fail("probe-record",
                         "the probe records no note; a recorded zero here is a finding about the "
                         "vocabulary, and silence is not"))

    # ── sources ──────────────────────────────────────────────────────────────
    rows = {s["id"] for s in (registry.get("sources") or [])
            if isinstance(s, dict) and s.get("id")}
    excluded = {e["id"] for e in (registry.get("excluded") or [])
                if isinstance(e, dict) and e.get("id")}
    srcs = doc.get("sources") or {}
    active = [a for a in (srcs.get("active") or []) if isinstance(a, dict)]
    skipped = [a for a in (srcs.get("skipped") or []) if isinstance(a, dict)]

    for a in active:
        sid = a.get("id")
        if sid in excluded:
            out.append(_fail("forbidden-source-not-active",
                             f"source {sid!r} is EXCLUDED in the registry and the map lists it "
                             "active; an excluded row is one no angle may cite"))
        elif sid not in rows:
            out.append(_fail("source-not-in-registry",
                             f"source {sid!r} is active in the map and is not a registry row; a "
                             "source the registry never admitted has no recorded posture"))
        san = a.get("sanitization") or {}
        if san.get("status") != "clean" and not str(san.get("cause") or "").strip():
            out.append(_fail("sanitization-cause",
                             f"source {sid!r} records sanitization status "
                             f"{san.get('status')!r} with no cause; every source here is a fetched "
                             "third-party page, and a non-clean status with no cause is "
                             "unreviewable"))

    accounted = {a.get("id") for a in active} | {a.get("id") for a in skipped}
    for sid in sorted(rows - accounted):
        out.append(_fail("source-unaccounted",
                         f"registry row {sid!r} is in neither `active` nor `skipped`; a source "
                         "nobody decided about reads exactly like one that was fine"))
    return out


def _owed_cells(angle: dict, keyword_map: dict) -> set[tuple[str, str]]:
    """The (group, source) pairs this angle owes a cell for.

    DERIVED from THREE terms, never "every group against every source":

      groups = the map's groups whose `type` is in the angle's `applicable_group_types`
      owed   = {(g, s) for g in groups for s in the angle's OWN sources INTERSECT the map's ACTIVE}

    Dropping the third term is not a paraphrase. On the shipped exemplar it turns 20 owed cells
    into 80, and a reviewer applying it finds 60 missing cells in a correct artifact.
    """
    types = set(angle.get("applicable_group_types") or [])
    groups = [g.get("id") for g in (keyword_map.get("groups") or [])
              if isinstance(g, dict) and g.get("type") in types and g.get("id")]
    active = {s.get("id") for s in ((keyword_map.get("sources") or {}).get("active") or [])
              if isinstance(s, dict)}
    sources = [s for s in (angle.get("sources") or []) if s in active]
    return {(g, s) for g in groups for s in sources}


def validate_search(doc: object, keyword_map: object, registry: dict) -> list[str]:
    """One angle's search output."""
    if not isinstance(doc, dict):
        return [_fail("schema", f"the search output parsed as {type(doc).__name__}, not a mapping")]
    if not isinstance(keyword_map, dict):
        return [_fail("keyword-map-invalid",
                      f"the keyword map parsed as {type(keyword_map).__name__}, not a mapping")]

    out: list[str] = []
    angles = {a["id"]: a for a in (registry.get("angles") or [])
              if isinstance(a, dict) and a.get("id")}
    aid = (doc.get("meta") or {}).get("angle_id")
    angle = angles.get(aid)
    if angle is None:
        # Early return ON PURPOSE. Without the angle there is no cap, no source list and no
        # applicable-type set, so every rule below would compare against an empty contract and
        # report a correct artifact as clean.
        return [_fail("angle-unknown",
                      f"meta.angle_id is {aid!r}, which the registry does not declare; the owed "
                      "set, the cap and the ordering all come from the angle, so nothing below "
                      "this can be checked")]

    outcome = doc.get("outcome")
    cells = [c for c in (doc.get("coverage") or []) if isinstance(c, dict)]
    minted = {g.get("id") for g in (keyword_map.get("groups") or []) if isinstance(g, dict)}
    active = {s.get("id") for s in ((keyword_map.get("sources") or {}).get("active") or [])
              if isinstance(s, dict)}
    excluded = {e["id"] for e in (registry.get("excluded") or [])
                if isinstance(e, dict) and e.get("id")}

    seen_pairs: set[tuple[str, str]] = set()
    reached_pairs: set[tuple[str, str]] = set()
    for cell in cells:
        gid, sid = cell.get("group_id"), cell.get("source_id")
        where = f"{gid}/{sid}"
        pair = (gid, sid)
        if pair in seen_pairs:
            out.append(_fail("cell-pair-unique",
                             f"cell {where} appears twice; two cells for one pair can disagree and "
                             "the arithmetic closes against whichever is read second"))
        seen_pairs.add(pair)

        if gid not in minted:
            out.append(_fail("cell-group-known",
                             f"cell {where} names group {gid!r}, which the map never minted"))
        if sid in excluded:
            out.append(_fail("cell-source-excluded",
                             f"cell {where} names source {sid!r}, which the registry EXCLUDES"))
        elif sid not in active:
            out.append(_fail("cell-source-known",
                             f"cell {where} names source {sid!r}, which the map did not record "
                             "ACTIVE; a source the map could not reach is one no angle can query"))

        status = cell.get("status")
        returned, kept = cell.get("returned"), cell.get("kept")
        if status == "reached":
            reached_pairs.add(pair)
            if returned is None or kept is None:
                out.append(_fail("reached-needs-counts",
                                 f"cell {where} is reached and records no counts; a reached cell "
                                 "with no numbers cannot be reconciled against anything"))
            else:
                if returned and not str(cell.get("count_frame") or "").strip():
                    out.append(_fail("count-frame-required",
                                     f"cell {where} returned {returned} with no count_frame; a "
                                     "bare count in this corpus is not re-derivable, because "
                                     "whether an amending act counts separately changes the number "
                                     "without changing the search"))
                if kept > returned:
                    out.append(_fail("kept-exceeds-returned",
                                     f"cell {where} kept {kept} of {returned} returned"))
        else:
            if returned is not None or kept is not None:
                out.append(_fail("coverage-unreached-has-count",
                                 f"cell {where} has status {status!r} and records a count; a count "
                                 "on an unreached cell is a zero laundered out of a failure"))
            if not str(cell.get("cause") or "").strip():
                out.append(_fail("status-needs-cause",
                                 f"cell {where} has status {status!r} and no cause; a non-reached "
                                 "status without observable evidence is unreviewable"))

        csan = cell.get("sanitization")
        if isinstance(csan, dict) and csan.get("status") != "clean":
            if not str(csan.get("cause") or "").strip():
                out.append(_fail("cell-sanitization-cause",
                                 f"cell {where} records sanitization status "
                                 f"{csan.get('status')!r} with no cause; this cell departed from "
                                 "the map's posture to say so, and a departure with no cause is "
                                 "unreviewable"))

    if outcome in ("ran", "vacated"):
        owed = _owed_cells(angle, keyword_map)
        for gid, sid in sorted(owed - seen_pairs):
            out.append(_fail("coverage-complete",
                             f"no cell for {gid}/{sid}, which this angle's applicable_group_types "
                             "and source list make owed; an omitted pair and a recorded zero are "
                             "different facts and only one of them is evidence"))
        for gid, sid in sorted(seen_pairs - owed):
            out.append(_fail("cell-in-applicable-set",
                             f"cell {gid}/{sid} is outside this angle's owed set; it searched an "
                             "axis or a source the angle does not carry"))

    # ── outcome: three shapes, and each owes something different ─────────────
    if outcome == "ran":
        if not cells:
            out.append(_fail("ran-requires-coverage",
                             "outcome is `ran` and there are no coverage cells; an angle that ran "
                             "and found nothing records the zeros"))
        elif not reached_pairs:
            out.append(_fail("ran-attempted-nothing",
                             "outcome is `ran` and not one cell was reached; an output whose every "
                             "cell is a recorded choice or a failure did not run, whatever the "
                             "outcome says"))
    elif outcome == "not_run":
        if cells:
            out.append(_fail("unrun-angle-has-cells",
                             f"outcome is `not_run` and there are {len(cells)} cells; the map's "
                             "verdict ruled this angle out, and searching anyway inflates the "
                             "survey with an angle the scope excluded"))
        if doc.get("candidates") or doc.get("unadmitted"):
            out.append(_fail("unrun-angle-has-candidates",
                             "outcome is `not_run` and rows are recorded; nothing was searched, so "
                             "nothing can have been found"))
        if not str((doc.get("not_run") or {}).get("map_verdict") or "").strip():
            out.append(_fail("outcome-block-required",
                             "outcome is `not_run` and no `not_run.map_verdict` names the verdict "
                             "being honoured; without it a skipped angle and a ruled-out one read "
                             "identically"))
    elif outcome == "vacated":
        if doc.get("candidates") or doc.get("unadmitted"):
            out.append(_fail("vacated-not-empty",
                             "outcome is `vacated` and rows are recorded; vacated means there was "
                             "nothing to search, so cells and causes are owed and candidates are "
                             "not"))
        if not str((doc.get("vacated") or {}).get("cause") or "").strip():
            out.append(_fail("outcome-block-required",
                             "outcome is `vacated` and no `vacated.cause` says why; a vacated "
                             "angle and one that searched and found nothing are different facts"))

    # ── kept reconciles against candidates PLUS unadmitted, per cell ─────────
    row_counts: dict[tuple[str, str], int] = {}
    for row in list(doc.get("candidates") or []) + list(doc.get("unadmitted") or []):
        if isinstance(row, dict) and "/" in str(row.get("found_by") or ""):
            key = tuple(str(row["found_by"]).split("/", 1))
            row_counts[key] = row_counts.get(key, 0) + 1
    for cell in cells:
        if cell.get("status") != "reached":
            continue
        pair = (cell.get("group_id"), cell.get("source_id"))
        want = row_counts.get(pair, 0)
        if cell.get("kept") is not None and cell["kept"] != want:
            out.append(_fail("kept-matches-rows",
                             f"cell {pair[0]}/{pair[1]} records kept {cell['kept']} and carries "
                             f"{want} rows (candidates PLUS unadmitted); under a result-count "
                             "reading a row found and dropped WITHOUT a record satisfies the "
                             "arithmetic, which is the one thing `unadmitted` exists to prevent"))

    # ── the summary duplicates the cells on purpose ──────────────────────────
    summary = doc.get("retrieval_summary")
    if outcome in ("ran", "vacated"):
        if not isinstance(summary, dict):
            out.append(_fail("summary-required",
                             "no retrieval_summary; it duplicates the cells on purpose, and a "
                             "discrepancy is the signal a failure was laundered into a zero"))
        else:
            actual: dict[str, int] = {}
            for cell in cells:
                st = str(cell.get("status"))
                actual[st] = actual.get(st, 0) + 1
            if dict(summary.get("status_counts") or {}) != actual:
                out.append(_fail("summary-reconciles",
                                 f"status_counts {dict(summary.get('status_counts') or {})} does "
                                 f"not reconcile with the cells {actual}"))
            declared_degraded = set(summary.get("degraded_sources") or [])
            real_degraded = {c.get("source_id") for c in cells
                             if c.get("status") not in ("reached", "not-attempted")}
            for sid in sorted(real_degraded - declared_degraded):
                out.append(_fail("degraded-source-recorded",
                                 f"source {sid!r} has a cell that is neither reached nor a "
                                 "recorded choice, and is not in degraded_sources"))

    # ── the cap ──────────────────────────────────────────────────────────────
    bound = doc.get("bound")
    candidates = [c for c in (doc.get("candidates") or []) if isinstance(c, dict)]
    if outcome == "ran" and not isinstance(bound, dict):
        out.append(_fail("bound-required",
                         "outcome is `ran` and there is no `bound`; the cap, whether it truncated "
                         "and the ordering it truncated by are what make a truncation reviewable"))
    elif isinstance(bound, dict):
        cap = bound.get("cap")
        if cap != angle.get("cap"):
            out.append(_fail("cap-matches-registry",
                             f"bound.cap is {cap} and the registry gives angle {aid!r} a cap of "
                             f"{angle.get('cap')}; a run may neither raise its own ceiling nor "
                             "quietly lower it"))
        if isinstance(cap, int) and len(candidates) > cap:
            # Checked UNCONDITIONALLY. Gating on `hit is False` let `hit: true` plus a dropped_note
            # carry any number past the ceiling.
            out.append(_fail("cap-respected",
                             f"{len(candidates)} candidates exceed the cap of {cap}. With "
                             "`hit: false` that denies a truncation the count proves; with "
                             "`hit: true` it exceeds the ceiling it declares it stopped at"))
        if bound.get("hit") and not str(bound.get("dropped_note") or "").strip():
            out.append(_fail("bound-hit-needs-note",
                             "the cap was HIT and records nothing about what fell out; with no "
                             "dropped_note the ordering is the only evidence a truncation leaves"))
        if not bound.get("hit") and str(bound.get("dropped_note") or "").strip():
            out.append(_fail("bound-hit-consistent",
                             "`hit: false` with a dropped_note; nothing was dropped and something "
                             "is recorded as dropped, and the two cannot both hold"))

    # ── candidates ───────────────────────────────────────────────────────────
    seen_items: set[str] = set()
    for cand in candidates:
        iid = str(cand.get("item_id") or "")
        if iid in seen_items:
            out.append(_fail("candidate-id-unique",
                             f"item_id {iid!r} appears twice; one instrument is one row, and a "
                             "duplicate double-counts it in every sum downstream"))
        seen_items.add(iid)
        gid = iid.split("-", 1)[0]
        if cand.get("id_class") != gid:
            out.append(_fail("id-class-shape",
                             f"item_id {iid!r} carries prefix {gid!r} against id_class "
                             f"{cand.get('id_class')!r}; the class a scout CLAIMS is checkable "
                             "against the id it minted, and inventing a CELEX number is the worst "
                             "thing this type can do"))
        klass = cand.get("id_class")
        if klass in ID_GRAMMARS and iid.startswith(f"{klass}-"):
            rule, pattern = ID_GRAMMARS[klass]
            body = iid[len(klass) + 1:]
            if not pattern.fullmatch(body):
                out.append(_fail(rule,
                                 f"item_id {iid!r} does not match the {klass} grammar; six of the "
                                 "seven prefixes are someone else's, and an identifier that is one "
                                 "character wrong reads exactly like a real one"))

        grp = str(cand.get("found_by") or "").split("/")[0]
        if grp and grp not in minted:
            out.append(_fail("candidate-group-known",
                             f"candidate {iid!r} names group {grp!r}, which the map never minted"))
        if not isinstance(cand.get("provenance"), dict):
            out.append(_fail("candidate-provenance",
                             f"candidate {iid!r} carries no `provenance` block; the external "
                             "identifiers are what make a citation checkable, and their ABSENCE "
                             "has to be recorded as null rather than omitted"))

    # Rows must cite a cell that exists AND that ran. Without the second half a row can name a cell
    # that never ran, and `kept` reconciliation never sees it because an unreached cell's kept is
    # null.
    for row, label in ([(c, "candidate") for c in (doc.get("candidates") or [])] +
                       [(u, "unadmitted row") for u in (doc.get("unadmitted") or [])]):
        if not isinstance(row, dict):
            continue
        fb = str(row.get("found_by") or "")
        if "/" not in fb:
            continue
        pair = tuple(fb.split("/", 1))
        if pair not in seen_pairs:
            out.append(_fail("row-cell-unknown",
                             f"{label} {row.get('item_id')!r} cites cell {fb}, which this output "
                             "has no cell for"))
        elif pair not in reached_pairs:
            out.append(_fail("rows-cite-an-unreached-cell",
                             f"{label} {row.get('item_id')!r} cites cell {fb}, which did not run; "
                             "an unreached cell records no kept, so the arithmetic never sees it"))
    return out


if __name__ == "__main__":
    sys.exit(main())
