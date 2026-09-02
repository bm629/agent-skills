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
import json
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
#: The enums the SCHEMA enforces. Kept here as the contract a reader of this module needs, and
#: deliberately NOT re-checked: a rule duplicating a schema enum is unreachable behind the schema
#: pass, and two statements of one enum drift.
#:
#: `authority` is how close to the ISSUING BODY the text is. L-5's four tiers, and it RANKS and
#: DEDUPES only -- never a cut.
AUTHORITY_TIERS = ("primary-law", "regulator-guidance", "incorporated-standard",
                   "secondary-compilation")

#: `binding_force` is whether and how it binds. Orthogonal to authority: the question is not how
#: authoritative the text is, but what happens if you ignore it.
BINDING_FORCES = ("law", "incorporated-by-reference", "contractual", "regulator-guidance",
                  "voluntary-standard")

#: Every member is a VERIFIABILITY class. None is an authority judgement, and that is the point:
#: free prose could phrase a verifiability failure as "low authority" and no keyword scan could
#: tell, which is exactly what build-contract §9b says to stop pretending a rule can do.
UNADMITTED_REASON_CLASSES = ("unresolvable-at-issuing-body", "no-stated-version-or-date",
                             "superseded", "out-of-scope-for-this-angle", "duplicate-of")

#: An instrument's text is not always readable. Three source classes in this registry cannot be,
#: and `paywalled` / `blocked` are legitimate terminal states rather than gaps.
TEXT_RETRIEVABLE = ("full-text", "summary-only", "paywalled", "blocked")

#: THREE control vocabularies, three grammars. A blanket OSCAL rule would refuse every WCAG
#: success criterion and every PCI requirement number -- two of the eight angles' own corpora.
CONTROL_GRAMMARS = {
    "oscal": re.compile(r"^[a-z]{2}-\d{1,2}(\.\d{1,2})*$"),
    "wcag": re.compile(r"^\d{1,2}(\.\d{1,2}){1,2}$"),
    "pci": re.compile(r"^\d{1,2}(\.\d{1,2}){0,3}$"),
}

#: `fallback_used` records WHICH fallback was walked, and an angle's and a row's are different
#: routes -- the registry gives each source a fallback and each angle its own. A bare id cannot say
#: which was taken, so the prefix is load-bearing and this is what enforces it.
FALLBACK_USED = re.compile(r"^(angle|row):(.+)$")

#: A locator is "a resolvable URL, and the one actually fetched"; an ELI is "a resolvable URI".
#: `minLength: 1` is all the schema can say about either, and `see the register` satisfies it while
#: resolving to nothing.
LOCATOR_SCHEMES = ("http://", "https://")

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

#: `provenance.cfr_citation` is the citation AS WRITTEN, so it carries a subpart or a section the
#: id never does. Only the title and the part are compared -- a grammar tight enough to refuse a
#: wrong citation outright would refuse `45 CFR 164.308(a)(1)(i)`, which is honest.
CFR_CITATION = re.compile(r"^(\d{1,2})\s+CFR\s+(\d{1,4})")

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
        merges two records into one filename. A later wave decides what still needs doing by
        looking at which records exist on disk, so the orphaned row is re-attempted every time
        while looking perfectly valid.

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


def _schema_errors(doc: object, name: str) -> list[str]:
    """Shape, types, enums, required keys and `additionalProperties` — the layer BELOW every rule.

    This ran nowhere for the first draft of this module: `Draft202012Validator` was imported only so
    the dependency guard could name it, and `SCHEMAS` was dead. The cost was not theoretical.
    Deleting `outcome` from a search output produced ZERO findings while silently disabling eight
    rules, because each is gated on `outcome in (...)` and none checks that `outcome` is a known
    value. A producer who typos the one field deciding what else is owed got a clean bill.

    It returns EARLY in both validate functions. A rule reading a field whose type it never checked
    is one `TypeError` away from exit 1 with no FAIL line to grep — which is the code that says
    "go edit your artifact" with nothing to act on.
    """
    try:
        schema = json.loads((SCHEMAS / f"{name}.schema.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [_fail("schema", f"{name}.schema.json could not be read: {exc}")]
    out = []
    for err in sorted(Draft202012Validator(schema).iter_errors(doc), key=lambda e: list(e.path)):
        where = "/".join(str(x) for x in err.path) or "(root)"
        out.append(_fail("schema", f"{where}: {err.message}"))
    return out


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
            out.append(_fail("not-a-mapping", "an angle entry is not a mapping"))
            continue
        aid = angle.get("id")
        if not aid:
            out.append(_fail("angle-id-required", "an angle declares no `id`"))
            continue
        trigger = angle.get("trigger")
        if trigger not in _TRIGGERS:
            out.append(_fail("trigger-must-be-known",
                             f"angle {aid!r} declares trigger {trigger!r}; known: {_TRIGGERS}"))
            # Do NOT fall through. The anchor rules below branch on the trigger, so an unknown one
            # produced "angle 'b1' is always-on and carries a trigger_anchor" -- factually false,
            # since the trigger was neither.
            continue
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
        # A map that PARSES but is not a usable map is still a class-2 fault: the search author
        # cannot fix the file they were handed. This used to fall through to validate_search, which
        # reported it as an ordinary finding at exit 1 -- and an empty map then produced dozens of
        # exit-1 findings against a correct search output, which is precisely the "sends someone
        # off to edit a file that is fine" this contract exists to prevent.
        if not isinstance(kmap, dict):
            print(_fail("keyword-map-invalid",
                        f"the handed keyword map parsed as {type(kmap).__name__}, not a mapping"))
            return 2
        kmap_errs = _schema_errors(kmap, "regulatory-scope-map")
        if kmap_errs:
            print(_fail("keyword-map-invalid",
                        f"the handed keyword map does not satisfy its own schema "
                        f"({len(kmap_errs)} errors, first: {kmap_errs[0]}). The search author "
                        "cannot repair the map they were given"))
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
    errs = _schema_errors(doc, "regulatory-scope-map")
    if errs:
        # EARLY. Every rule below reads fields this pass has not yet typed.
        return errs

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
    # The schema enforces `minItems: 9` and the family enum. What it cannot express is that the
    # nine are the nine DISTINCT families -- nine rows naming eight families with one repeated
    # satisfies both.
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

    for row in skipped:
        if not str(row.get("cause") or "").strip():
            out.append(_fail("skipped-source-cause",
                             f"source {row.get('id')!r} is skipped with no cause; a skipped source "
                             "is one NO angle can query, and moving a row here without observable "
                             "evidence removes it from every grid for free"))

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

    Dropping the angle's OWN source list is not a paraphrase. On the shipped exemplar it turns 25
    owed cells into 100, and a reviewer applying it finds 75 missing cells in a correct artifact.
    Dropping the ACTIVE intersection instead is invisible on that exemplar -- a1 carries none of the
    map's one skipped row -- and shows on b5, whose 12 owed cells become 16. The first draft of this
    docstring said "20 into 80", numbers inherited verbatim from the ML sibling and true of neither
    angle here, and it named the term whose loss changes nothing on the artifact it cites.
    """
    types = set(angle.get("applicable_group_types") or [])
    groups = [g.get("id") for g in (keyword_map.get("groups") or [])
              if isinstance(g, dict) and g.get("type") in types and g.get("id")]
    active = {s.get("id") for s in ((keyword_map.get("sources") or {}).get("active") or [])
              if isinstance(s, dict)}
    sources = [s for s in (angle.get("sources") or []) if s in active]
    return {(g, s) for g in groups for s in sources}


def _covers(stated: str, declared: str) -> bool:
    """Does `stated` select by what `declared` names?

    Word-set containment, not equality. The registry's signal is a phrase
    ("issuing-body authority, then instrument recency") and a run may legitimately say more about
    how it applied it; what it may not do is order by something the angle never declared. Hyphens
    read as spaces because the registry writes the signal hyphenated and prose does not.
    """
    def words(text: str) -> set[str]:
        return {w for w in re.split(r"[^a-z0-9]+", text.lower()) if len(w) > 2}

    return words(declared) <= words(stated)


def validate_search(doc: object, keyword_map: object, registry: dict) -> list[str]:
    """One angle's search output."""
    if not isinstance(doc, dict):
        return [_fail("schema", f"the search output parsed as {type(doc).__name__}, not a mapping")]
    errs = _schema_errors(doc, "search-output")
    if errs:
        return errs

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
    source_ids = {r["id"] for r in (registry.get("sources") or [])
                  if isinstance(r, dict) and r.get("id")}

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

        used = cell.get("fallback_used")
        if used is not None:
            m = FALLBACK_USED.fullmatch(str(used))
            if m is None:
                out.append(_fail("fallback-used-shape",
                                 f"cell {where} records fallback_used {used!r}, which names no "
                                 "route. An ANGLE fallback and a ROW fallback are different "
                                 "channels -- the registry declares one of each -- so a bare id "
                                 "cannot say which was walked"))
            else:
                kind, ref = m.group(1), m.group(2)
                known = angles if kind == "angle" else source_ids
                if ref not in known:
                    out.append(_fail("fallback-used-unknown",
                                     f"cell {where} walked fallback {used!r} and the registry has "
                                     f"no {kind} {ref!r}; a route recorded against nothing cannot "
                                     "be checked and reads as a channel that was never taken"))

        csan = cell.get("sanitization")
        if csan is not None and not isinstance(csan, dict):
            out.append(_fail("cell-sanitization-cause",
                             f"cell {where} records a sanitization that is not a mapping; the map "
                             "side of this field demands a cause, and a scalar here was silently "
                             "ignored"))
        elif isinstance(csan, dict) and csan.get("status") != "clean":
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
            for sid in sorted(declared_degraded - real_degraded):
                # The other direction, which was missing while its sibling `summary-reconciles`
                # used exact equality. A source declared degraded with no degraded cell overstates
                # the damage, and the rule exists to keep the summary and the cells in step.
                out.append(_fail("degraded-source-recorded",
                                 f"source {sid!r} is listed in degraded_sources and no cell of "
                                 "its is degraded"))

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
        declared = str(angle.get("ordering_signal") or "").strip()
        stated = str(bound.get("ordering") or "").strip()
        # `cap` is checked against the registry verbatim and `ordering` was not, so a run could
        # declare any rule at all and `dropped_note` would then reconcile against it. Compared on
        # the SIGNAL's own words rather than by equality: the registry states the signal and a run
        # may say more about how it applied it, but it may not select by something else.
        if declared and stated and not _covers(stated, declared):
            out.append(_fail("ordering-matches-registry",
                             f"bound.ordering is {stated!r} and the registry gives angle {aid!r} "
                             f"the ordering signal {declared!r}; a truncation justified by an "
                             "ordering the angle never declared is unreviewable, because "
                             "`dropped_note` then reconciles against the run's own invention"))

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
        # `authority`, `binding_force` and `text_retrievable` are enums the SCHEMA owns. Rules
        # duplicating them became unreachable the moment the schema pass returned early, and their
        # reasoning already lives in the schema descriptions -- which is where a producer reads it.
        tr = cand.get("text_retrievable")
        if tr in ("paywalled", "blocked") and str(cand.get("evidence_quote") or "").strip():
            out.append(_fail("quote-forbidden-when-unretrievable",
                             f"candidate {iid!r} is {tr!r} and carries an evidence_quote; the text "
                             "could not be read, so the quote is a paraphrase of a clause nobody "
                             "saw -- the fabrication this type must not have. `summary-only` is "
                             "the state where the CATALOGUE entry was readable and may be quoted"))

        vocab = cand.get("control_vocabulary") or "oscal"
        # `.get` returning None used to mean "check nothing", so an unrecognised vocabulary
        # silently disabled this rule. The schema's enum refuses an unknown value before this
        # runs; defaulting to the OSCAL grammar rather than to None means that even if it ever
        # did not, the check would tighten rather than vanish.
        pattern = CONTROL_GRAMMARS.get(vocab, CONTROL_GRAMMARS["oscal"])
        for cid in (cand.get("control_ids") or []):
            if not pattern.fullmatch(str(cid)):
                out.append(_fail("control-id-grammar",
                                 f"candidate {iid!r} carries control id {cid!r}, which does not "
                                 f"match the {vocab} grammar. `AT-2(2)` and `at-2.2` are the same "
                                 "control under two spellings, and mixing them silently splits a "
                                 "merge group in two"))

        loc = str(cand.get("locator") or "")
        if not loc.startswith(LOCATOR_SCHEMES):
            out.append(_fail("locator-resolvable",
                             f"candidate {iid!r} has locator {loc!r}, which is not an absolute "
                             "http(s) URL. The field is the URL actually fetched and the one a "
                             "reader re-fetches to check the quote; prose naming a register is "
                             "not a route back to the text"))
        eli = str((cand.get("provenance") or {}).get("eli") or "")
        if eli and not eli.startswith(LOCATOR_SCHEMES):
            out.append(_fail("locator-resolvable",
                             f"candidate {iid!r} has ELI {eli!r}, which is not an absolute URI. "
                             "The ELI is a RESOLVABLE identifier -- that is what distinguishes it "
                             "from the CELEX number beside it"))

        if not str(cand.get("issuing_body") or "").strip():
            out.append(_fail("issuing-body-required",
                             f"candidate {iid!r} names no issuing_body. L-7 admits an instrument "
                             "only when it resolves at a NAMED issuing body, so a row that cannot "
                             "name one belongs in `unadmitted` with reason_class "
                             "`unresolvable-at-issuing-body`, not among the candidates"))

        prov = cand.get("provenance")
        if isinstance(prov, dict):
            # The id and the external identifier are two spellings of ONE instrument, transcribed
            # from the same document at different moments. When they disagree, one of them was
            # attached to the wrong row -- which is how a quote from part 164 ends up filed under
            # part 160, and nothing downstream can tell.
            klass, rest = str(cand.get("id_class") or ""), iid.split("-", 1)[-1]
            celex = str(prov.get("celex") or "")
            if klass == "CELEX" and celex and celex != rest:
                out.append(_fail("provenance-matches-id",
                                 f"candidate {iid!r} carries CELEX {celex!r}; the id and the "
                                 "identifier name two different instruments"))
            cite = str(prov.get("cfr_citation") or "")
            if klass == "CFR" and cite:
                m = CFR_CITATION.match(cite)
                if m is None or f"{m.group(1)}-{m.group(2)}" != rest:
                    out.append(_fail("provenance-matches-id",
                                     f"candidate {iid!r} carries cfr_citation {cite!r}; the title "
                                     "and part it cites are not the title and part of the id"))
            std = str(prov.get("standard_number") or "")
            if klass == "ISO" and std:
                number = re.match(r"^(?:IEC-)?(\d{3,5})", rest)
                if number is None or number.group(1) not in std:
                    out.append(_fail("provenance-matches-id",
                                     f"candidate {iid!r} carries standard_number {std!r}, which "
                                     "does not contain the number the id is built from"))

    # Rows must cite a cell that exists AND that ran. Without the second half a row can name a cell
    # that never ran, and `kept` reconciliation never sees it because an unreached cell's kept is
    # null.
    for row, label in ([(c, "candidate") for c in (doc.get("candidates") or [])] +
                       [(u, "unadmitted row") for u in (doc.get("unadmitted") or [])]):
        if not isinstance(row, dict):
            continue
        fb = str(row.get("found_by") or "")
        if "/" not in fb:
            # Previously a `continue`, which let a row attached to no cell traverse the whole gate
            # clean -- the arithmetic never saw it because it counted only rows that named a cell.
            out.append(_fail("row-cell-unknown",
                             f"{label} {row.get('item_id')!r} records found_by {fb!r}, which is "
                             "not a `group/source` cell key; a row attached to no cell is counted "
                             "by no cell's kept"))
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
