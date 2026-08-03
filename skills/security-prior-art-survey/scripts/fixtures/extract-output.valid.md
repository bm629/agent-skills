---
schema_version: 1
item_id: "CVE-2026-31337"
id_class: registry
outcome: extracted
surfaces: ["receipt upload"]
tier: 2
tier_evidence:
  - {kind: public-poc, reference: "public exploit archive entry 51999", as_of: "2026-08-03T12:00:00Z"}
source_authority: authoritative-registry
severity:
  - {system: CVSS, version: "3.1", vector: "AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H", score: 8.8}
  - {system: CVSS, version: "4.0", score: 8.6, as_of: "2026-08-03T12:00:00Z"}
control:
  stated: true
  text: "upgrade to 2.4.1, or disable the raster rendering path for untrusted input"
  source_reference: "advisory, Remediation section"
aliases: ["GHSA-aaaa-bbbb-cccc"]
related: ["CWE-434"]
weakness_refs: ["CWE-434"]
extracted_at: "2026-08-03T12:05:00Z"
sanitization: {status: sanitized}
---

## What the source says
A document rendering library mishandles a crafted raster stream, allowing code execution in the
process that parses an uploaded file.

## Which surfaces it applies to
Receipt upload. The scope names uploaded receipt images and PDFs; whether a server-side render
path exists is recorded under preconditions rather than asserted as a surface.

## Evidence of exploitation
A working proof-of-concept is published in a public exploit archive. No known-exploited catalog
lists it, and no incident corpus records an exploitation of it against this product class.

## Severity as published
The advisory publishes both a 3.1 vector and a 4.0 score. They are recorded separately and are
not comparable to each other.

## The control the source prescribes
Upgrade to the fixed release, or disable the raster rendering path for untrusted input.

## Preconditions and limits
Requires the vulnerable rendering path to be reachable with attacker-supplied input, and applies
only to releases before the fix.

## Relationship to other items
The same vulnerability carries a platform advisory identifier, recorded as an alias. The
underlying weakness class is recorded as related, not as an alias.

## What this does not establish
That this product is affected. No component set has been chosen, so whether the library is even
adopted is unknown. A published proof-of-concept establishes reproducibility somewhere, not
exposure here.

## Provenance
Read from the advisory record, sanitized on read.
