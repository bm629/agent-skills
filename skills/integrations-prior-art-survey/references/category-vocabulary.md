# The seeded `category` vocabulary

`category` on a candidate is a **frozen-but-extensible VOCABULARY**, not an enum. No rule can close
it, and calling it an enum would promise a closed set this type cannot close.

Four sites depend on this list and none of them shipped it before: the absent-input policy, the
reviewing twin's C13, the schema's `category` description, and the map guide's `category` axis.
A list required by four readers and written for none is a check nobody can run.

## The seed

Two sources, unioned, with the upstream spelling winning where they overlap.

**The five classification keys** the capability map itself carries:
`analytics` · `communication` · `payments` · `productivity` · `storage`

**The measured Nango taxonomy** — 31 categories over 990 providers, read 2026-09-03:
`accounting` · `analytics` · `banking` · `cms` · `communication` · `crm` · `design` · `dev-tools` ·
`e-commerce` · `education` · `erp` · `gaming` · `hr` · `insurance` · `knowledge-base` · `legal` ·
`marketing` · `other` · `payment` · `payroll` · `productivity` · `real-estate` · `search` ·
`social` · `sports` · `support` · `surveys` · `ticketing` · `video` · `warehousing` · `workspace`

**Where the two disagree, the CATALOG spelling wins**, because it is what the corpus indexes on.
Nango writes `payment`; the classification key is `payments`. Record the catalog's.

## Using a value that is not here

Legal, and the point of "extensible". Record it and put its provenance in `notes[]` — which catalog
or descriptor used it, and where you read it. A value invented silently is not legal; a value
observed in the corpus and sourced is.
