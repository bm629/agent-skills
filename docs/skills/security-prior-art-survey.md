# security-prior-art-survey

A systematic security prior-art survey, end to end — packaged as four procedures over one set
of schema-validated contracts.

## Purpose

Before designing a system, find out what is realistically going to be attacked, with
evidence that it happens to products like this one, and what controls the evidence
prescribes. This skill teaches an agent to (1) derive a threat-vocabulary map — the
translation layer turning a product's surfaces into the terms security corpora actually
index, (2) execute one search angle, a single discovery mechanism worked across its sources
into a reproducible, coverage-audited record, and (3) deep-read one surfaced item into an
extraction whose tier carries its receipts.

It is a research method, not a scanner. It reads and classifies published security
knowledge; it never attacks anything and never runs retrieved code.

Covers all three waves: search, extract and synthesis.

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

## The four procedures

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

**Procedure 3 — deep-read one source item.** A cheap relevance skim runs first and bails only on
a confident "applies to none of the scope" — uncertainty *keeps* the item, and this is the only
cut in the entire survey. Past the skim, nine fixed body sections above a machine block carrying
the evidence tier with its receipts, severity as published per system and version, the control
the source itself prescribes, and `aliases` separated from `related` so synthesis can collapse
one vulnerability carrying two database identifiers into one register row.

Two things that record refuses to do: invent a control where the source prescribes none (it says
so instead), and let severity promote an item's tier. Severity orders items *within* a tier and
never moves one between tiers — catalog membership or a matching incident is tier 1, a
proof-of-concept is tier 2, and the validator rejects a tier-1 claim resting only on the latter.

**Procedure 4 — synthesis.** Aggregate the extractions into a threat register and a report.
Threats are named against an external vocabulary — an attack pattern first, a weakness class
where none fits — never coined, because a name invented here means the same threat carries three
names across three requests and the living register can never merge. Duplicates collapse on
`aliases` and never on `related`. A row's tier is its strongest evidence's tier and never above:
synthesis aggregates evidence, it does not create it.

The report leads with the coverage receipt — every angle with its outcome and a cause where it
did not run, every corpus release, every assumed default, and the dependency surface covered
*and* not covered — because a reader must know the shape of the search before trusting any
finding inside it. It carries no mandates in its own voice: the register's teeth are that the
architecture doc owes an answer to every tier-1 and tier-2 row, not that the survey can issue
orders.

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

Four authoritative JSON Schemas (draft 2020-12), a machine-readable source registry that
doubles as the validator's per-angle applicability input, eight per-source angle briefs, an
extraction template and an evidence-tier rubric, and a deterministic validator with
`keyword-map`, `search`, `extract` and `synthesis` subcommands.

```bash
python scripts/validate_security_prior_art.py keyword-map <map>
python scripts/validate_security_prior_art.py search <output> --keyword-map <map>
python scripts/validate_security_prior_art.py extract <record>
python scripts/validate_security_prior_art.py synthesis <register> --extracts <dir>
```

The map argument is required for `search`: coverage completeness is the cross product of the
map's applicable groups and its active sources, so the check is not computable without it.

The validator checks **shape only** — schema, enums, ranges, required fields, and arithmetic
reconciling two records against each other. It never judges whether a finding matters or
whether a bail was honest; those are the reviewing sibling's numbered conditions. That split
keeps it portable (it needs no scope context) and stops it false-failing an honest artifact.

77 tests, most of them mutation tests that break a valid fixture in exactly one way. Four run
the other direction, asserting that a not-run artifact, a vacated artifact, a tier-3 record with
no evidence, and a control recorded as not-stated all validate clean — a validator that faults
those is what pressures a producer into fabricating coverage, evidence, or a remedy.

## Companion

[`reviewing-security-prior-art-survey`](reviewing-security-prior-art-survey.md) is the
acceptance gate, and its conditions file is the authoritative statement of the quality bar
for everything this skill emits.
