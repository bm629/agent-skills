# The threat-vocabulary map, explained

`schemas/threat-vocabulary-map.schema.json` is the contract. This guide explains it and shows a
worked example; where the two appear to differ, the schema wins.

The map exists because security corpora do not index your product's feature names. It is the
translation layer, and everything downstream — which angles run, which cells owe coverage, which
queries are legitimate — is computed from it. That is why it carries guards and stamps rather
than just a term list: a map is not a convenience, it is the denominator.

## The six group types

Every group carries a type, and the source registry joins on it to decide which angles a group
is applicable to.

| type | holds | indexed by |
|---|---|---|
| `weakness` | weakness classes | CWE |
| `attack-pattern` | attack mechanisms and categories | CAPEC, ATT&CK |
| `control` | verification requirements and risk categories | OWASP ASVS, Top 10, MASVS |
| `component` | named packages, libraries, ecosystems | OSV, GitHub Advisory |
| `vendor-product` | named services, platforms, vendors | CSAF/VEX feeds |
| `domain-incident` | the product class as incident corpora describe it | VERIS, disclosures |

A type with no group goes in `scope_guard.absent_types` **with a reason** — never silently
missing. This is the single highest-leverage field in the artifact: the coverage arithmetic is
computed from types, so an omitted type empties the angle that depends on it, and the resulting
search output reports no gap at all. A reviewer corroborates each absent type against your scope,
so the reason has to be true, not merely present.

## Expansions

Three to eight terms **beside** the canonical term, each carrying where it came from
(`extracted` from scope, `model-knowledge`, `probe-discovered`) and how it relates to the
canonical (`broader`, `narrower`, `related`, `alt-label`). A group whose expansions are all
`alt-label` is a spelling list, not an expansion.

If a concept genuinely cannot support three sister terms, fold it into a related group or record
`short_reason`. Never pad — a floor with no relief valve just manufactures filler, and padding is
a defect in its own right.

If any expansion claims `probe-discovered`, the `probe` block records what you probed and what it
surfaced. Set `performed: false` with a reason if you did not probe. An unrecorded probe makes
the provenance unfalsifiable.

## Negative terms

Security vocabulary collides across domains. "Injection" means one thing in web security and
another in medical devices; "poisoning" spans caches, training data and wells. Without negative
terms, an ambiguous group drags a wrong corpus into your coverage. These are consumed at search
time — a cell's queries must honour its own group's negative terms.

## Angle applicability

One verdict per angle: the angle, its precondition, whether it holds, and why. Without this
record, an angle you judged inapplicable leaves no trace anywhere and nobody can tell a
considered decision from an oversight. A negative verdict is corroborated against your scope, and
**silence in the scope is not a negative answer** — where the absent-input policy directs an
angle to run on an unstated input, it runs.

## Sources and stamps

Every active source records the `release` you read and an `as_of`. Cadences diverge wildly —
CWE ships several releases in a year while CAPEC can sit unchanged for years — so an unstamped
map cannot be reproduced or compared against a later run. A rolling source with no release
concept (OSV, GitHub Advisory, KEV) records `release: "rolling"`.

Stamping a source means you read it, so each active source also carries a `sanitization` record.
You cannot stamp a release you did not fetch.

## Assumptions

Every value the absent-input policy forced appears in `assumptions` with the signal it was
inferred from. A reader must be able to tell "the caller said the product handles payment data"
from "no verification level was given, so one was inferred from the mention of payouts".

## Worked example (abridged)

A team expense product: receipt upload, an approval workflow, payouts through a named payments
provider.

```yaml
schema_version: 1
meta: {as_of: "2026-08-03T10:00:00Z", revision: 1}
groups:
  - id: file-upload-weaknesses
    type: weakness
    canonical: "unrestricted file upload"
    expansion_cap: 5
    expansions:
      - {term: "CWE-434", provenance: extracted, relation: alt-label}
      - {term: "path traversal on upload", provenance: model-knowledge, relation: narrower}
      - {term: "content-type confusion", provenance: probe-discovered, relation: related}
    negative_terms: ["firmware upload", "medical device"]
  - id: approval-authz
    type: weakness
    canonical: "authorization bypass through user-controlled key"
    expansion_cap: 4
    expansions:
      - {term: "CWE-639", provenance: extracted, relation: alt-label}
      - {term: "self-approval", provenance: model-knowledge, relation: narrower}
      - {term: "broken object level authorization", provenance: model-knowledge, relation: broader}
    negative_terms: ["physical access control"]
probe:
  performed: true
  sources: ["CWE 4.20"]
  discoveries: ["content-type confusion"]
scope_guard:
  excluded:
    - {item: "the payments provider's own infrastructure", reason: "out of our trust boundary; we consume its API"}
  absent_types:
    - {type: domain-incident, reason: "no public incident corpus classifies expense-reimbursement products as a category"}
angle_applicability:
  - {angle_id: a1, precondition: "always", holds: true, reason: "control standards apply to every product"}
  - {angle_id: a1m, precondition: "ships a mobile client, or scope is silent", holds: true,
     reason: "scope does not say; absent-input policy directs the angle to run"}
  - {angle_id: b1, precondition: "a named package set exists", holds: false,
     reason: "no dependency set named at this stage"}
sources:
  active:
    - {id: cwe, release: "4.20", as_of: "2026-08-03T10:00:00Z", sanitization: {status: sanitized}}
    - {id: osv, release: "rolling", as_of: "2026-08-03T10:05:00Z", sanitization: {status: sanitized}}
  skipped:
    - {id: hackerone-hacktivity, reason: "no programmatic access; deferred to the disclosure angle's browse pass"}
assumptions:
  - {input: "verification level", assumed: "level 2",
     inferred_from: "scope names payouts and stored personal data"}
```

Note what the example does not do: it does not omit `domain-incident` silently, it does not route
`a1m` to not-run on silence, and it does not present the inferred verification level as though the
caller stated it.
