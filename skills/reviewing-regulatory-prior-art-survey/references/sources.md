# Where your evidence lives, and what each source is worth

You judge against six things. Three of them are in the PRODUCER package, and the reason is
structural: an artifact cannot be its own contract.

| evidence | path |
| --- | --- |
| the artifact | handed to you |
| the scope map | handed to you alongside a search output |
| the scope and classification the producer was handed | handed to you alongside the map |
| the schemas | `regulatory-prior-art-survey/schemas/` |
| the source registry | `regulatory-prior-art-survey/references/source-registry.yaml` |
| the angle reference | `regulatory-prior-art-survey/references/angles/<angle_id>.md` |

## Why the map is a separate input

C2's whole test is a candidate's evidence against the group its `found_by` names, and the group
definitions are in the map. A search output reviewed without it can be checked for internal
consistency and nothing else.

## Why the registry cannot be inferred from the artifact

Deriving an angle's source list from the cells it wrote is circular: an artifact that omits a
source omits it from any list you read off it, so the omission becomes invisible in the same act
that should have exposed it.

The registry is also where the source POSTURES live — which hosts answer on the user agent, which
endpoint needs `Accept-Encoding`, which document host refuses while its index answers. C11, C12 and
C23 all rest on those, and the artifact's own account of them is what you are checking.

## Authority tiers are for RANKING, and you check them for honesty

`primary-law` > `regulator-guidance` > `incorporated-standard` > `secondary-compilation`.

Two rows in this registry are tier 4 and admitted as **navigational aids only**: a fines tracker
and a legislation tracker. They may be used to FIND an instrument; a record citing one as the
SOURCE of an obligation is a C16 finding.

## Three source classes cannot be read at all

ISO texts are paywalled behind a challenge; PCI documents are blocked by a host separate from the
index that answers; UK primary law returns a zero-byte body. A record naming one of these carries
its NUMBER and no quote — `evidence_quote: null` or the field omitted, both legal and both
meaning the same thing, because the schema requires a quote only when `text_retrievable` is
`full-text` or `summary-only`, and C23 is where you check the state matches
what the registry says about the host.

*Not yours to report:* a quote on a `paywalled` or `blocked` record. The validator refuses it at
`quote-forbidden-when-unretrievable`, so no artifact carrying one ever reaches you. What IS yours is
C23 — whether the state the record claims is the state the fetch actually reached, which is the
judgement that decides which of the two shapes applies.
