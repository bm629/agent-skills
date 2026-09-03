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
        # Emitted by registry_failures and routed to 2 like the rest. Omitted from an earlier
        # version of this set with no reason given, which the derived equality check now refuses.
        "registry-unreadable",
    }
)

#: Faults in the PACKAGE itself, also exit 2. Kept separate from the registry-integrity set because
#: they are found on a different path -- before any registry rule can run.
EXIT2_PACKAGE_RULES = frozenset({"schema-unavailable", "dependency-missing"})

AUTHORITY_BANDS = ("first-party", "connector-catalog", "aggregator", "community")

#: The canonical id is the vendor HOST, lowercased. Lowercase, no scheme, path, port or userinfo;
#: at least two LDH labels; a trailing alphabetic TLD.
_HOST_ID = re.compile(r"^(?!-)[a-z0-9-]+(?<!-)(?:\.(?!-)[a-z0-9-]+(?<!-))*\.[a-z]{2,}$")
#: The slug is PINNED to the filename-safe charset, so `record_filename`'s charset branch is never
#: taken by an id of this type. The ENDING stays unconstrained, which is what keeps the hash branch
#: reachable.
_NODOMAIN_ID = re.compile(r"^NODOMAIN-[A-Za-z0-9._-]+$")
_SAFE_STEM = re.compile(r"^[A-Za-z0-9._-]+$")
_HASHED_STEM = re.compile(r"--[0-9a-f]{12}$")

#: OAS 3.1 security-scheme types, and the OAuth flow names. `null` is the recorded value for a
#: catalog auth_mode with no OAS member, which is why neither is a schema enum.
OAS_AUTH_SCHEMES = ("apiKey", "http", "mutualTLS", "oauth2", "openIdConnect")
OAS_OAUTH_FLOWS = ("implicit", "password", "clientCredentials", "authorizationCode")
#: The IANA HTTP Authentication Scheme registry. Matched CASE-INSENSITIVELY, because HTTP auth
#: scheme names are case-insensitive and real descriptors overwhelmingly write `scheme: bearer`.
IANA_HTTP_SCHEMES = (
    "Basic", "Bearer", "Concealed", "Digest", "DPoP", "GNAP", "HOBA", "Mutual",
    "Negotiate", "OAuth", "PrivateToken", "SCRAM-SHA-1", "SCRAM-SHA-256", "vapid",
)

#: The nine catalog auth modes this type maps, and the three that map to NULL. A catalog value with
#: no OAS member records `null` rather than the nearest-looking member: forcing one would assert a
#: scheme the service does not offer.
AUTH_MODE_TO_OAS = {
    "OAUTH2": "oauth2",
    "OAUTH1": None,
    "BASIC": "http",
    "API_KEY": "apiKey",
    "APP": None,
    "APP_STORE": None,
    "CUSTOM": None,
    "JWT": "http",
    "TBA": None,
}


def record_filename(item_id: str) -> str:
    """The per-record filename for one candidate.

    TWO conditions on the identity branch, not one: the safe charset AND the anti-fixed-point
    guard. Without the second, an id that already ends in `--<12 hex>` would map to itself and
    collide with the hashed form of a different id.
    """
    import hashlib

    if _SAFE_STEM.fullmatch(item_id) and not _HASHED_STEM.search(item_id):
        return item_id
    digest = hashlib.sha256(item_id.encode("utf-8")).hexdigest()[:12]
    return f"{item_id}--{digest}"


COMPLETE_LISTING = (True, False, "n/a")


def _is_complete_listing(value: object) -> bool:
    """`is` for the booleans, `==` for the string.

    `value in (True, False, "n/a")` uses == throughout, so `complete_listing: 0` passed the registry
    gate and then silently disabled `enumerated-zero-is-a-claim` for that row -- `0 == False`. Using
    `is` for the string half would be wrong the other way: identity is not guaranteed for a string
    loaded from YAML.
    """
    return value is True or value is False or value == "n/a"


def _fail(rule: str, message: str) -> str:
    return f"FAIL {rule}: {message}"


def _read_yaml(path: Path) -> tuple[object, str | None]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None, f"{path} does not exist"
    except (OSError, ValueError) as exc:
        # ValueError catches UnicodeDecodeError -- a non-UTF-8 file crashed to exit 1 with a
        # traceback and no FAIL line, which is the code that means "go edit your artifact".
        return None, f"{path} could not be read: {exc}"
    try:
        return yaml.safe_load(text), None
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
    except (OSError, ValueError) as exc:
        # ValueError covers JSONDecodeError and UnicodeDecodeError. A separate id, routed to exit 2:
        # an unreadable schema FILE is a package fault the artifact's author cannot repair, unlike
        # `schema`, which means their artifact does not satisfy a schema that loaded fine.
        return [_fail("schema-unavailable", f"{name}.schema.json could not be read: {exc}")]
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
        elif not _is_complete_listing(row["complete_listing"]):
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


#: The four axes whose terms the corpus spells more than one way. NOT `service` or `seed-product`,
#: where the canonical is a proper noun the corpus spells once. Naming the set here rather than
#: leaving it to the builder is the difference between a rule and a guess.
EXPANSION_FLOOR_AXES = ("category", "capability", "domain-noun", "pattern")
NEGATIVE_TERM_AXES = ("category", "domain-noun")
ANGLE_IDS = ("a1", "a2", "a3", "b1", "b2", "b3", "b4", "b5")
ALWAYS_ON = ("a1", "a2", "a3")


def validate_keyword_map(doc: object, reg: dict) -> list[str]:
    out = _schema_errors(doc, "integration-vocabulary-map")
    if out:
        return out

    assert isinstance(doc, dict)
    groups = doc.get("groups") or []
    guard = doc.get("scope_guard") or {}
    absent = set(guard.get("absent_types") or [])

    seen: set[str] = set()
    for g in groups:
        gid = str(g.get("id"))
        if gid in seen:
            out.append(_fail("group-id-unique", f"group id {gid!r} appears more than once"))
        seen.add(gid)

        axis = g.get("type")
        expansions = g.get("expansions") or []
        if axis in EXPANSION_FLOOR_AXES and len(expansions) < 2:
            out.append(_fail(
                "expansion-floor",
                f"group {gid!r} is on the {axis!r} axis and carries {len(expansions)} expansion(s); "
                "the four axes the corpus spells more than one way need at least two",
            ))
        cap = g.get("expansion_cap")
        if isinstance(cap, int) and len(expansions) > cap:
            out.append(_fail(
                "expansion-cap",
                f"group {gid!r} carries {len(expansions)} expansions against an expansion_cap of {cap}",
            ))
        if axis in NEGATIVE_TERM_AXES and not (g.get("negative_terms") or []):
            out.append(_fail(
                "negative-terms-required",
                f"group {gid!r} is on the {axis!r} axis and states no negative_terms; the words are "
                "ordinary English and the false-positive corpus is large",
            ))

    # every axis is accounted for: it has a group, or it is declared absent
    for axis in ("category", "capability", "service", "pattern", "domain-noun", "seed-product"):
        if not any(g.get("type") == axis for g in groups) and axis not in absent:
            out.append(_fail(
                "group-type-accounted",
                f"axis {axis!r} has no group and is not in scope_guard.absent_types",
            ))

    # a term may be queried once: a shared term names its owner, and the owner must carry it
    owned: dict[str, str] = {}
    for st in guard.get("shared_terms") or []:
        term, owner = st.get("term"), st.get("owner")
        owned[str(term)] = str(owner)
        if owner not in seen:
            out.append(_fail("term-sited-once", f"shared term {term!r} names owner {owner!r}, which is not a group"))
            continue
    for term, owner in owned.items():
        carriers = [
            str(g.get("id")) for g in groups
            if term == g.get("canonical") or term in (g.get("expansions") or [])
        ]
        if owner not in carriers:
            out.append(_fail(
                "term-sited-once",
                f"shared term {term!r} is owned by {owner!r}, which does not carry it",
            ))

    # angle verdicts: one per angle, no duplicates, no unknown angle, always-on never false
    verdicts = doc.get("angle_applicability") or []
    ids = [v.get("angle_id") for v in verdicts]
    for aid in ANGLE_IDS:
        if aid not in ids:
            out.append(_fail("angle-verdict-complete", f"no angle_applicability verdict for {aid!r}"))
    for aid in set(ids):
        if ids.count(aid) > 1:
            out.append(_fail("angle-verdict-unique", f"angle {aid!r} carries {ids.count(aid)} verdicts"))
    declared = {str(a.get("id")) for a in (reg.get("angles") or [])}
    for aid in ids:
        if aid not in declared:
            out.append(_fail(
                "applicability-angle-unknown",
                f"the map names angle {aid!r}, which the registry does not declare",
            ))
    for v in verdicts:
        if v.get("angle_id") in ALWAYS_ON and v.get("holds") is False:
            out.append(_fail(
                "always-on-angle-holds",
                f"angle {v.get('angle_id')!r} is always-on and cannot record holds: false",
            ))

    probe = doc.get("probe") or {}
    if probe.get("ran") is not None and not str(probe.get("note") or "").strip():
        out.append(_fail(
            "probe-record",
            "the probe records no note; a recorded zero here is a finding about the corpus rather "
            "than a failure, and a probe with no note says neither",
        ))

    # sources: every registry row in exactly one of active / skipped
    rows = {str(s.get("id")) for s in (reg.get("sources") or [])}
    excluded = {str(e.get("id")) for e in (reg.get("excluded") or [])}
    srcs = doc.get("sources") or {}
    active = {str(a.get("id")): a for a in (srcs.get("active") or [])}
    skipped = {str(s.get("id")): s for s in (srcs.get("skipped") or [])}
    for rid in sorted(rows - set(active) - set(skipped)):
        out.append(_fail("source-unaccounted", f"registry row {rid!r} is in neither active[] nor skipped[]"))
    for rid in sorted(set(active) & set(skipped)):
        out.append(_fail("source-unaccounted", f"row {rid!r} is in BOTH active[] and skipped[]"))
    for rid in sorted((set(active) | set(skipped)) - rows):
        out.append(_fail("source-unaccounted", f"the map names {rid!r}, which is not a registry row"))
    for rid in sorted(set(active) & excluded):
        out.append(_fail(
            "forbidden-source-not-active",
            f"row {rid!r} is in the registry's excluded[] block and cannot be active",
        ))

    for rid, row in sorted(skipped.items()):
        if not str(row.get("cause") or "").strip():
            out.append(_fail("skipped-source-cause", f"skipped row {rid!r} states no cause"))
        if row.get("cause_class") == "no-holding-angle":
            holders = [
                str(a.get("id")) for a in (reg.get("angles") or [])
                if rid in (a.get("sources") or [])
            ]
            held = {v.get("angle_id") for v in verdicts if v.get("holds")}
            still = sorted(set(holders) & held)
            if still:
                out.append(_fail(
                    "skipped-source-still-carried",
                    f"row {rid!r} is skipped as no-holding-angle, but {still} hold and carry it",
                ))

    for rid, row in sorted(active.items()):
        san = row.get("sanitization") or {}
        if san.get("status") != "clean" and not str(san.get("cause") or "").strip():
            out.append(_fail(
                "sanitization-cause",
                f"active row {rid!r} records sanitization {san.get('status')!r} with no cause",
            ))

    return out


_FALLBACK_USED = re.compile(r"^(angle|row):([a-z0-9][a-z0-9-]*)$")


def _owed_cells(angle: dict, kmap: dict) -> set[tuple[str, str]]:
    """The owed set is DERIVED from THREE terms, and dropping any one inflates or deflates it.

    groups of the angle's APPLICABLE types x the angle's OWN sources x the map's ACTIVE sources.
    Dropping the second term makes every angle owe every source; dropping the third makes it owe
    rows this run never had.
    """
    types = set(angle.get("applicable_group_types") or [])
    groups = [str(g.get("id")) for g in (kmap.get("groups") or []) if g.get("type") in types]
    active = {str(a.get("id")) for a in ((kmap.get("sources") or {}).get("active") or [])}
    sources = [s for s in (angle.get("sources") or []) if s in active]
    return {(g, s) for g in groups for s in sources}


def validate_search(doc: object, reg: dict, kmap: object) -> list[str]:
    out = _schema_errors(doc, "search-output")
    if out:
        return out

    assert isinstance(doc, dict)
    assert isinstance(kmap, dict)  # main() rejects a non-mapping map at exit 2 before we are called

    aid = str((doc.get("meta") or {}).get("angle_id"))
    angle = next((a for a in (reg.get("angles") or []) if str(a.get("id")) == aid), None)
    if angle is None:
        # EARLY RETURN, so nothing below compares against an empty contract.
        return [_fail("angle-unknown", f"the artifact names angle {aid!r}, which the registry does not declare")]

    rows = {str(s.get("id")): s for s in (reg.get("sources") or [])}
    excluded = {str(e.get("id")) for e in (reg.get("excluded") or [])}
    kgroups = {str(g.get("id")) for g in (kmap.get("groups") or [])}
    cells = doc.get("coverage") or []

    seen: set[tuple[str, str]] = set()
    for c in cells:
        key = (str(c.get("group_id")), str(c.get("source_id")))
        if key in seen:
            out.append(_fail("cell-pair-unique", f"cell {key[0]}/{key[1]} appears more than once"))
        seen.add(key)

        if key[0] not in kgroups:
            out.append(_fail("cell-group-known", f"cell names group {key[0]!r}, which the map does not declare"))
        # EXCLUDED is tested FIRST and independently. An excluded id is deliberately NOT a source
        # row, so testing membership first shadows this rule permanently -- it fired as
        # `cell-source-known` and the policy breach went unnamed.
        if key[1] in excluded:
            out.append(_fail("cell-source-excluded", f"cell names source {key[1]!r}, which the registry EXCLUDES; substituting an excluded source is the same policy breach as querying it directly"))
        elif key[1] not in rows:
            out.append(_fail("cell-source-known", f"cell names source {key[1]!r}, which the registry does not declare"))
        if key[1] not in (angle.get("sources") or []):
            out.append(_fail("cell-in-applicable-set", f"cell names source {key[1]!r}, which angle {aid!r} does not carry"))

        status = c.get("status")
        returned = c.get("returned")
        if status == "reached":
            if returned is None or c.get("kept") is None:
                out.append(_fail("reached-needs-counts", f"cell {key[0]}/{key[1]} is reached and states no returned/kept"))
            if returned and not str(c.get("count_frame") or "").strip():
                out.append(_fail("count-frame-required", f"cell {key[0]}/{key[1]} returned {returned} and states no count_frame; a catalog count is unre-derivable without knowing what it counted"))
        else:
            if not str(c.get("cause") or "").strip():
                out.append(_fail("status-needs-cause", f"cell {key[0]}/{key[1]} is {status!r} and states no cause"))
            if returned:
                out.append(_fail("coverage-unreached-has-count", f"cell {key[0]}/{key[1]} is {status!r} and reports returned={returned}"))

        san = c.get("sanitization") or {}
        if san.get("status") not in (None, "clean") and not str(san.get("cause") or "").strip():
            out.append(_fail("cell-sanitization-cause", f"cell {key[0]}/{key[1]} records sanitization {san.get('status')!r} with no cause"))

        listing = rows.get(key[1], {}).get("complete_listing")
        enumerated = c.get("enumerated")
        if listing == "n/a":
            if enumerated is not None:
                out.append(_fail("enumerated-absent-on-na", f"cell {key[0]}/{key[1]} records enumerated={enumerated!r} against a row whose complete_listing is `n/a`. `false` there asserts a bounded walk of something that is not a listing, as meaningless as `true`"))
        elif listing is True or listing is False:
            if status == "reached" and enumerated is None:
                out.append(_fail("enumerated-required", f"cell {key[0]}/{key[1]} is reached against a LISTING row and does not say whether its walk was an enumeration; it is what makes a zero readable"))
            if enumerated is True and listing is False:
                out.append(_fail("enumerated-zero-is-a-claim", f"cell {key[0]}/{key[1]} claims enumerated=true against a row whose traversal is BOUNDED; the claim is about the walk, not the count, so it is refused whatever `returned` is"))

        fb = c.get("fallback_used")
        if fb is not None:
            m = _FALLBACK_USED.fullmatch(str(fb))
            if m is None:
                out.append(_fail("fallback-used-shape", f"cell {key[0]}/{key[1]} records fallback_used {fb!r}, which names no route. An ANGLE fallback and a ROW fallback are different channels, so a bare id cannot say which was walked -- prefix `angle:` or `row:`"))
            else:
                level, target = m.group(1), m.group(2)
                if target not in rows:
                    out.append(_fail("fallback-used-unknown", f"cell {key[0]}/{key[1]} walked fallback {fb!r} and the registry has no row {target!r}"))
                else:
                    # the PARSED TARGET against the level's own declaration, never the raw token
                    expected = angle.get("fallback") if level == "angle" else rows[key[1]].get("fallback")
                    # NOT `if expected and ...`: a TERMINAL row declares `fallback: null`, so the
                    # falsy guard skipped the check on six of twenty-three rows -- including a1's
                    # own primary source, which is also its angle-level fallback. A terminal's None
                    # never equals a target, which IS the intended refusal.
                    if target != expected:
                        out.append(_fail("fallback-declared", f"cell {key[0]}/{key[1]} records fallback_used {fb!r}, but the {level}-level fallback declared for it is {expected!r}. A fallback nobody declared is an unrecorded source, not a recovery"))

    owed = _owed_cells(angle, kmap)
    if doc.get("outcome") in ("ran", "vacated"):
        for g, s in sorted(owed - seen):
            out.append(_fail("coverage-complete", f"cell {g}/{s} is owed and absent"))

    # ---- outcome decides what else is owed -------------------------------------------------
    outcome = doc.get("outcome")
    if outcome == "ran":
        if not cells:
            out.append(_fail("ran-requires-coverage", "outcome is `ran` and the artifact records no coverage cells"))
        if cells and all(c.get("status") == "not-attempted" for c in cells):
            out.append(_fail("ran-attempted-nothing", "outcome is `ran` and every cell is `not-attempted`; a run that attempted nothing did not run"))
        if doc.get("bound") is None:
            out.append(_fail("bound-required", "outcome is `ran` and the artifact records no `bound`"))
        if doc.get("retrieval_summary") is None:
            out.append(_fail("summary-required", "outcome is `ran` and the artifact records no `retrieval_summary`"))
    elif outcome == "not_run":
        if doc.get("not_run") is None:
            out.append(_fail("outcome-block-required", "outcome is `not_run` and no `not_run{map_verdict}` block says which map verdict ruled the angle out"))
        if cells:
            out.append(_fail("unrun-angle-has-cells", "outcome is `not_run` and the artifact records coverage cells; the map's verdict ruled this angle out, and searching anyway inflates the survey"))
        if doc.get("candidates"):
            out.append(_fail("unrun-angle-has-candidates", "outcome is `not_run` and the artifact records candidates"))
        if doc.get("bound") is not None:
            out.append(_fail("unrun-angle-has-cells", "outcome is `not_run` and the artifact records a `bound`; an angle that did not run bounded nothing"))
        if doc.get("retrieval_summary") is not None:
            out.append(_fail("unrun-angle-has-cells", "outcome is `not_run` and the artifact records a `retrieval_summary`; there is no coverage to summarise"))
    elif outcome == "vacated":
        if doc.get("vacated") is None:
            out.append(_fail("outcome-block-required", "outcome is `vacated` and no `vacated{cause}` block says why"))
        if doc.get("candidates") or doc.get("unadmitted"):
            out.append(_fail("vacated-not-empty", "outcome is `vacated` and the artifact records candidates or unadmitted rows; recording either means a search happened"))
        if doc.get("bound") is not None:
            out.append(_fail("vacated-not-empty", "outcome is `vacated` and the artifact records a `bound`; a vacated angle bounded nothing"))
        if doc.get("retrieval_summary") is None:
            out.append(_fail("summary-required", "outcome is `vacated` and the artifact records no `retrieval_summary`"))

    # `bound` is owed on `ran` ALONE -- an angle that did not run bounded nothing.
    bound = doc.get("bound")
    if bound is not None and outcome == "ran":
        cap, hit = bound.get("cap"), bound.get("hit")
        declared = angle.get("cap")
        # UNCONDITIONAL. Guarding this on `cap is not None` let a null cap skip the comparison
        # entirely, and `cap-respected` then keyed off the artifact's own null rather than the
        # registry's number -- 206 candidates against a declared cap of 90 produced no findings.
        # A null is legal only where the REGISTRY declares one, which is the transcription rule.
        if cap != declared:
            out.append(_fail("cap-matches-registry", f"bound.cap is {cap!r} but the registry declares {declared!r} for angle {aid!r}; the cap is transcribed VERBATIM"))
        # `cap` bounds the CARRIED ROWS -- candidates plus unadmitted -- and is enforced against the
        # REGISTRY's value, so a mis-transcribed cap cannot raise its own ceiling.
        carried = len(doc.get("candidates") or []) + len(doc.get("unadmitted") or [])
        if isinstance(declared, int) and carried > declared:
            out.append(_fail("cap-respected", f"the artifact carries {carried} rows against a cap of {declared}"))
        if cap is None and hit:
            out.append(_fail("bound-hit-consistent", "bound.cap is null and bound.hit is true; with no cap there is nothing to hit"))
        if hit and not str(bound.get("dropped_note") or "").strip():
            out.append(_fail("bound-hit-needs-note", "bound.hit is true and no dropped_note says what fell off the end, so a reader cannot re-apply the ordering"))
        reg_order = str(angle.get("ordering_signal") or "")
        if str(bound.get("ordering") or "") != reg_order and not str(bound.get("ordering_deviation") or "").strip():
            out.append(_fail("ordering-matches-registry", f"bound.ordering differs from the registry's {reg_order!r} and states no ordering_deviation"))
        if str(bound.get("ordering") or "") == reg_order and str(bound.get("ordering_deviation") or "").strip():
            out.append(_fail("ordering-deviation-contradicts", "bound.ordering matches the registry and an ordering_deviation claims it did not"))

    summary = doc.get("retrieval_summary")
    if isinstance(summary, dict) and cells:
        counts: dict[str, int] = {}
        for c in cells:
            counts[str(c.get("status"))] = counts.get(str(c.get("status")), 0) + 1
        if summary.get("status_counts") != counts:
            out.append(_fail("summary-reconciles", f"retrieval_summary.status_counts is {summary.get('status_counts')!r} but the coverage list gives {counts!r}; both are DERIVED from the finished list rather than counted as you go"))
        degraded = {str(d.get("source_id")) for d in (summary.get("degraded_sources") or [])}
        real = {str(c.get("source_id")) for c in cells if c.get("status") not in (None, "reached")}
        for sid in sorted(real - degraded):
            out.append(_fail("degraded-source-recorded", f"source {sid!r} has a non-reached cell and is absent from degraded_sources"))
        # BOTH directions. One-way, a fabricated entry for a source with no cell at all passed.
        for sid in sorted(degraded - real):
            out.append(_fail("degraded-source-recorded", f"degraded_sources names {sid!r}, which has no non-reached cell in this artifact"))
        statuses = {str(c.get("source_id")): c.get("status") for c in cells if c.get("status") not in (None, "reached")}
        for d in summary.get("degraded_sources") or []:
            sid, st = str(d.get("source_id")), d.get("status")
            if sid in statuses and st != statuses[sid]:
                out.append(_fail("degraded-source-recorded", f"degraded_sources records {sid!r} as {st!r} but its cell is {statuses[sid]!r}"))

    reached = {(str(c.get("group_id")), str(c.get("source_id"))) for c in cells if c.get("status") == "reached"}
    for row in (doc.get("candidates") or []) + (doc.get("unadmitted") or []):
        fbk = str(row.get("found_by") or "")
        if "/" not in fbk:
            out.append(_fail("row-cell-unknown", f"row {row.get('item_id')!r} cites found_by {fbk!r}, which is not a group/source cell key"))
            continue
        pair = tuple(fbk.split("/", 1))
        if pair not in seen:
            out.append(_fail("row-cell-unknown", f"row {row.get('item_id')!r} cites cell {fbk!r}, which this artifact does not record"))
        elif pair not in reached:
            out.append(_fail("rows-cite-an-unreached-cell", f"row {row.get('item_id')!r} cites cell {fbk!r}, which was not reached"))

    # `kept` counts candidate rows PLUS unadmitted rows, per cell. It is NEVER a result count.
    per_cell: dict[tuple[str, str], int] = {}
    for row in (doc.get("candidates") or []) + (doc.get("unadmitted") or []):
        fbk = str(row.get("found_by") or "")
        if "/" in fbk:
            pair = tuple(fbk.split("/", 1))
            per_cell[pair] = per_cell.get(pair, 0) + 1
    for c in cells:
        key = (str(c.get("group_id")), str(c.get("source_id")))
        kept, returned = c.get("kept"), c.get("returned")
        if kept is None:
            continue
        if isinstance(returned, int) and kept > returned:
            out.append(_fail("kept-exceeds-returned", f"cell {key[0]}/{key[1]} kept {kept} of {returned} returned"))
        if kept != per_cell.get(key, 0):
            out.append(_fail("kept-matches-rows", f"cell {key[0]}/{key[1]} records kept={kept} but {per_cell.get(key, 0)} row(s) cite it; kept counts candidates PLUS unadmitted"))

    seen_ids: set[str] = set()
    for cand in doc.get("candidates") or []:
        iid = str(cand.get("item_id"))
        if iid in seen_ids:
            out.append(_fail("candidate-id-unique", f"candidate item_id {iid!r} appears more than once"))
        seen_ids.add(iid)

        gid = str(cand.get("found_by") or "/").split("/", 1)[0]
        if gid not in kgroups:
            out.append(_fail("candidate-group-known", f"candidate {iid!r} cites group {gid!r}, which the map does not declare"))

        loc = str(cand.get("locator") or "")
        if not loc.startswith(("http://", "https://")):
            out.append(_fail("locator-resolvable", f"candidate {iid!r} records locator {loc!r}, which is not an absolute http(s) URL"))

        klass = cand.get("id_class")
        if klass == "host" and not _HOST_ID.fullmatch(iid):
            out.append(_fail("host-id-grammar", f"candidate {iid!r} declares id_class `host` and is not syntactically a host: lowercase, no scheme/path/port/userinfo, at least two LDH labels, a trailing alphabetic TLD"))
        if klass == "nodomain" and not _NODOMAIN_ID.fullmatch(iid):
            out.append(_fail("nodomain-id-grammar", f"candidate {iid!r} declares id_class `nodomain` and does not FULL-match NODOMAIN-[A-Za-z0-9._-]+"))
        if klass == "host" and iid.startswith("NODOMAIN-"):
            out.append(_fail("id-class-matches-id", f"candidate {iid!r} declares id_class `host` on a NODOMAIN- id"))
        if klass == "nodomain" and not iid.startswith("NODOMAIN-"):
            out.append(_fail("id-class-matches-id", f"candidate {iid!r} declares id_class `nodomain` on an id that is not NODOMAIN-prefixed"))

        scheme = cand.get("auth_scheme")
        flow = cand.get("oauth_flow")
        http_scheme = cand.get("http_scheme")
        if scheme is not None and scheme not in OAS_AUTH_SCHEMES:
            out.append(_fail("oas-auth-vocabulary", f"candidate {iid!r} records auth_scheme {scheme!r}, which is not an OAS 3.1 security-scheme type. `null` is the recorded value for a catalog auth_mode with no OAS member"))
        if flow is not None and flow not in OAS_OAUTH_FLOWS:
            out.append(_fail("oas-auth-vocabulary", f"candidate {iid!r} records oauth_flow {flow!r}, which is not an OAS 3.1 flow name"))
        if flow is not None and scheme != "oauth2":
            out.append(_fail("oauth-flow-needs-oauth2", f"candidate {iid!r} records an oauth_flow against auth_scheme {scheme!r}; a flow belongs to oauth2 alone"))
        if http_scheme is not None and scheme != "http":
            out.append(_fail("http-scheme-needs-http", f"candidate {iid!r} records an http_scheme against auth_scheme {scheme!r}; it belongs to the `http` scheme alone"))
        if http_scheme is not None and str(http_scheme).lower() not in {s.lower() for s in IANA_HTTP_SCHEMES}:
            out.append(_fail("http-scheme-vocabulary", f"candidate {iid!r} records http_scheme {http_scheme!r}, which is not in the IANA registry's fourteen members. The record stores the descriptor's spelling VERBATIM and the match is CASE-INSENSITIVE"))

        present = cand.get("present_on")
        if aid == "a1":
            own = str(cand.get("found_by") or "/").split("/", 1)[1] if "/" in str(cand.get("found_by") or "") else ""
            for member in present or []:
                if member not in (angle.get("sources") or []):
                    out.append(_fail("present-on-source-known", f"candidate {iid!r} lists present_on member {member!r}, which is not a registry row angle a1 carries"))
                elif not any(
                    str(c.get("source_id")) == member and c.get("status") == "reached" for c in cells
                ):
                    out.append(_fail("present-on-needs-reached-cell", f"candidate {iid!r} lists present_on member {member!r}, which has no REACHED cell in this artifact; a source this run skipped or never attempted cannot evidence presence"))
            if own and present is not None and own not in present:
                out.append(_fail("present-on-found-by-included", f"candidate {iid!r} omits its own found_by source {own!r} from present_on; the list is the COMPLETE membership, not the membership minus the catalog that won"))
        elif present is not None:
            out.append(_fail("present-on-a1-only", f"candidate {iid!r} is from angle {aid!r} and carries present_on, which is a1's alone"))

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
        if not isinstance(kmap, dict):
            print(_fail("keyword-map-invalid", f"{args.map_path} is not a mapping"))
            return 2
        kmap_errs = _schema_errors(kmap, "integration-vocabulary-map")
        if kmap_errs:
            print(_fail("keyword-map-invalid", f"{args.map_path} does not satisfy the map schema: {kmap_errs[0]}"))
            return 2
        findings = validate_search(doc, reg, kmap)

    for line in findings:
        print(line)
    # A package fault found on the artifact path still exits 2: `schema` means the ARTIFACT does not
    # satisfy a schema that loaded, which its author can fix; `schema-unavailable` means the schema
    # did not load at all, which they cannot.
    if any(line.startswith(f"FAIL {r}:") for line in findings for r in EXIT2_PACKAGE_RULES):
        return 2
    return 1 if findings else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
