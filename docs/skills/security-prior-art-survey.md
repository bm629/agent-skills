# security-prior-art-survey

The search wave of a systematic security prior-art survey — packaged as two procedures
over one set of schema-validated contracts.

## Purpose

Before designing a system, find out what is realistically going to be attacked, with
evidence that it happens to products like this one, and what controls the evidence
prescribes. This skill teaches an agent to (1) derive a threat-vocabulary map — the
translation layer turning a product's surfaces into the terms security corpora actually
index — and (2) execute one search angle, a single discovery mechanism worked across its
sources into a reproducible, coverage-audited record.

It is a research method, not a scanner. It reads and classifies published security
knowledge; it never attacks anything, never runs retrieved code, and never deep-reads a
source item.

Version 1 covers the SEARCH wave only. Extraction and synthesis land in later versions.

## What makes this survey different from the others

Everything here is built around one distinction: **"we did not look" and "we looked and
found nothing" are different facts**, and confusing them makes a team rebuild what already
exists or ship a threat someone documented years ago.

That distinction is enforced structurally rather than by exhortation. The search-output
schema is a discriminated union over three outcomes — an angle whose precondition was
unmet, an angle whose applicable set was emptied upstream, and an angle that ran — and the
first two *structurally forbid* coverage cells and candidates. An unrun angle cannot be
dressed as an empty search, because the schema rejects the shape. Within a run, every
coverage cell carries a status: only `reached` may carry counts, and `unreachable`,
`partial`, `embargoed-placeholder`, `content-withheld` and `not-attempted` each owe a
cause, with the registry's fallbacks required before the first of them may be claimed.

## The two procedures

**Procedure 1 — threat-vocabulary map.** Translate scope into corpus terms across six group
types (weakness, attack-pattern, control, component, vendor-product, domain-incident), with
three to eight expansions per group beside the canonical term, each carrying provenance and
a relation kind. Negative terms guard ambiguous vocabulary — "injection" means one thing in
web security and another in medical devices. Every group type is present or recorded absent
*with a reason*, because coverage arithmetic downstream is computed from types and a silent
omission empties the angle depending on it. Every active source records the release it read
plus an `as_of` and a sanitization record; a per-angle applicability verdict makes a dropped
angle traceable; and every value the absent-input policy forced is recorded as an assumption
with the signal it was inferred from.

**Procedure 2 — angle execution.** Read the angle brief, check its precondition, and work
only that angle's channels. Queries come from the map — the group's canonical term and
expansions, honouring its negative terms — and at least one per cell is a broad pass.
Later passes rank; they never exclude, and per-cell `returned` versus `kept` makes any
silent relevance cut visible. Candidates carry an identifier appropriate to their source
class, because three of the four always-on angles surface items that have no registry
identifier at all, and a rigid rule would force inventing one.

## The eight angles

| id | mechanism | precondition |
|---|---|---|
| `a1` | Control-standard enumeration (ASVS, Top 10, API Top 10, cheat sheets) | always |
| `a1m` | Mobile control standards (MASVS, MASWE, MASTG) | ships a mobile client, **or the scope is silent** |
| `a2` | Weakness-to-attack-pattern traversal (CWE → CAPEC → ATT&CK) | always |
| `a3` | Real-world incident mining (VERIS community corpus, industry reporting) | always |
| `a4` | Disclosure-corpus mining (bug-bounty disclosures, write-ups, talks) | always |
| `b1` | Ecosystem advisory lookup (OSV, GitHub Advisory) | a named package set exists |
| `b2` | Vendor and service advisory retrieval (CSAF/VEX feeds) | named third-party services exist |
| `b3` | Supply-chain attack-pattern enumeration | supply-chain exposure medium or higher, **or unstated** |

Two of those preconditions run on silence rather than treating it as a negative answer —
that is deliberate, and the absent-input policy explains why: in security, under-coverage
is the invisible failure.

## Two source policies worth knowing

**The national vulnerability registry is corroboration, never the package-level primary.**
Its enrichment policy narrowed sharply in 2026 — a large unenriched backlog moved to a
not-scheduled state and ongoing enrichment was restricted to a prioritised subset — so a
record can exist while its severity and affected-version metadata never arrive. The
aggregating open-source advisory database is the primary.

**An embargoed advisory is incomplete, not absent.** At least one major cloud provider
publishes bulletins saying only "security update" until an embargo lifts, then amends them.
That is a typed cell status, never a reached zero.

## Contracts and the gate

Two authoritative JSON Schemas (draft 2020-12), a machine-readable source registry that
doubles as the validator's per-angle applicability input, eight per-source angle briefs, and
a deterministic validator with `keyword-map` and `search` subcommands.

```bash
python scripts/validate_security_prior_art.py keyword-map <map>
python scripts/validate_security_prior_art.py search <output> --keyword-map <map>
```

The map argument is required for `search`: coverage completeness is the cross product of the
map's applicable groups and its active sources, so the check is not computable without it.

The validator checks **shape only** — schema, enums, ranges, required fields, and arithmetic
reconciling two records against each other. It never judges whether a finding matters or
whether a bail was honest; those are the reviewing sibling's numbered conditions. That split
keeps it portable (it needs no scope context) and stops it false-failing an honest artifact.

45 tests, 42 of them mutation tests that break a valid fixture in exactly one way. Two run
the other direction, asserting a not-run and a vacated artifact validate clean with no
coverage at all — a validator that faults those is what pressures a producer into
fabricating coverage.

## Companion

[`reviewing-security-prior-art-survey`](reviewing-security-prior-art-survey.md) is the
acceptance gate, and its conditions file is the authoritative statement of the quality bar
for everything this skill emits.
