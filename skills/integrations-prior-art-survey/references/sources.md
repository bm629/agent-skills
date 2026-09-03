# Sources — what each registry row IS, in its own words

Twenty-three rows, closed. Each is described here by what it holds and what it yields, so a reader
can tell whether a zero from it means anything.

Two different things are called "excluded" around this file, and they are not the same list.

**The registry's `excluded[]` block holds SOURCES that were considered and ruled out**, each with
observable evidence and a replacement row: `zapier-internal-api` and `make-internal-api` on
robots.txt, and `rapidapi-hub` because its terms could not be read without an account. Those three
are candidate sources; they simply lost.

**Separately, three CLASSES of thing that LOOK like rows are absent from the registry entirely** and
appear in neither `sources[]` nor `excluded[]`: the OAS 3.1 schema and the IANA HTTP auth-scheme
registry are VOCABULARY references that define enum members and are never queried; `web-search` is
the agent's own capability for LOCATING a first-party page, and giving it a fallback edge would
describe a route nobody can walk; and `postman-mcp-catalog` is folded into `postman-network`,
because listing one host twice would double-count the denominator a later wave divides by.

## Entry NAME SHAPE, per catalog — the difference between a real zero and a fabricated one

A cold run's own matching bug found this: n8n's directory names are CamelCase with no separator
(`AcuityScheduling`, `QuickBooks`, `InvoiceNinja`), so a word-boundary filter returned **0 for every
n8n cell** — five dishonest zeros that pass the gate cleanly and read exactly like real absence.

| row | what an entry looks like |
| --- | --- |
| `nango-providers` | lowercase hyphenated YAML keys (`google-calendar`, `active-campaign`) |
| `n8n-nodes` | CamelCase node names, no separator (`AcuityScheduling`, `QuickBooks`) — and **vendor families NEST one level**: `Google/Calendar/GoogleCalendar`, `Microsoft/...`, `Aws/...`. A top-level listing of `nodes/` sees only `Google`, so it returns an honest-looking zero for Google Calendar. **Walk the tree recursively and match the node's own basename**, or the zero is fabricated and `enumerated: true` on it is a false claim the gate cannot see |
| `activepieces-pieces` | lowercase hyphenated directories (`acuity-scheduling`) |
| `pipedream-components` | lowercase underscored directories (`acuity_scheduling`, `ez_texting`) |
| `zapier-apps-sitemap` | lowercase hyphenated URL slugs (`acuity-scheduling`) |
| `apis-guru` | `provider.com:version` keys (`googleapis.com:calendar`) |

**Normalise before matching, and record the query you actually ran.** A zero from a filter that
could not have matched is not evidence of absence.

## first-party

### `vendor-openapi`

Located from the vendor's own docs, never guessed. A first-party descriptor always wins over an
aggregator's copy of it.

**Yields:** One descriptor per vendor, or none. Not a listing.

**`complete_listing: n/a`** — not a listing at all, so an enumeration verdict against it would answer a question that does not apply.

**Access:** `open` as of 2026-09-03. Falls back to `apis-guru`.

### `vendor-docs`

Located from the vendor's own domain. The authority for every fact this survey records.

**Yields:** The authoritative statement of one vendor's API, auth and integration surface.

**`complete_listing: n/a`** — not a listing at all, so an enumeration verdict against it would answer a question that does not apply.

**Access:** `open` as of 2026-09-03. **This row is its family's TERMINAL.**

### `vendor-webhook-docs`

A section of the vendor's docs, recorded separately because b2 reads it directly.

**Yields:** One vendor's published event types and delivery semantics.

**`complete_listing: n/a`** — not a listing at all, so an enumeration verdict against it would answer a question that does not apply.

**Access:** `open` as of 2026-09-03. Falls back to `vendor-docs`.

### `vendor-trust-center`

MACHINE-READABLE means a /.well-known/security.txt with a real Contact:/Expires: field — an HTML
200 at that path is not one, and a trust host that only renders is not a walk.

**Yields:** One vendor's compliance posture. Measured over the regulated slice: 53.5% carry a trust surface, only 20.9% a machine-readable one.

**`complete_listing: n/a`** — not a listing at all, so an enumeration verdict against it would answer a question that does not apply.

**Access:** `open` as of 2026-09-03. Falls back to `vendor-docs`.

### `vendor-integration-pages`

The REACHABILITY risk this type carries: six of ten sampled directories could not be enumerated
from a sitemap. A directory that needs rendering is recorded as unreachable, not as empty.

**Yields:** One product's own integration directory. Measured over a ten-product sample of which FOUR are recorded by name -- atlassian 7,805, asana 563, airtable 207, monday 18; the six that yielded no count were not individually recorded, so the spread below is re-derivable and the sample's membership is not: 18 to 7,805 entries, and six of ten yielded no count at all.

**`complete_listing: n/a`** — not a listing at all, so an enumeration verdict against it would answer a question that does not apply.

**Access:** `open` as of 2026-09-03. Falls back to `vendor-docs`.

## connector-catalog

### `nango-providers`

One YAML file in git. The largest complete enumeration of the five catalogs and the family's
terminal. `docs` on every row points at nango.dev, NOT the vendor.

**Yields:** 990 providers across 31 categories, each with a docs link, an auth mode on 929 of them and — for 680 of them — a concrete vendor host derivable from authorization_url, token_url or proxy.base_url.

**`complete_listing: True`** — walkable end to end in one pass, so an enumerated zero from it is evidence of ABSENCE.

**Access:** `open` as of 2026-09-03. **This row is its family's TERMINAL.**

### `activepieces-pieces`

Walkable end to end through the contents API in one pass at this size.

**Yields:** 730 community pieces, each a directory with a manifest naming its service.

**`complete_listing: True`** — walkable end to end in one pass, so an enumerated zero from it is evidence of ABSENCE.

**Access:** `open` as of 2026-09-03. Falls back to `nango-providers`.

### `n8n-nodes`

Base nodes only; community nodes live outside this tree and are not counted.

**Yields:** 308 base nodes, one directory each.

**`complete_listing: True`** — walkable end to end in one pass, so an enumerated zero from it is evidence of ABSENCE.

**Access:** `open` as of 2026-09-03. Falls back to `nango-providers`.

### `pipedream-components`

BOUNDED: GitHub's contents API caps a directory listing at 1,000 entries, so the walk is
truncated by the API rather than by the corpus and the true total is not exposed.

**Yields:** >=1,000 component directories, one per app.

**`complete_listing: False`** — a listing with a BOUND, so a zero from it is not evidence of absence.

**Access:** `open` as of 2026-09-03. Falls back to `nango-providers`.

### `zapier-apps-sitemap`

SITEMAP-BOUNDED. robots.txt declares a `*` group and a separate named AI-crawler group with a
wider allowance (~10,000). The `*` group's restrictions are the OPERATIVE bound, because obeying
the stricter of two applicable groups is never a violation. The wider reading is recorded here
with its read date and the RFC 9309 rule that would select it, so it is not lost — but it is not
applied without a build-time measurement.

**Yields:** ~2,500 app pages reachable under the robots `*` group.

**`complete_listing: False`** — a listing with a BOUND, so a zero from it is not evidence of absence.

**Access:** `polite-pool` as of 2026-09-03. Falls back to `nango-providers`.

### `make-integrations-sitemap`

DEAD as of 2026-09-03: 403 with `cf-mitigated: challenge` and `server: cloudflare` on ALL ELEVEN
sitemaps its own robots.txt declares. It answered twelve days earlier. The row STAYS, with its
evidence and its fallback, because a row deleted on a 403 is a row nobody re-probes.

**Yields:** Nothing on this run — the channel is dead.

**`complete_listing: False`** — a listing with a BOUND, so a zero from it is not evidence of absence.

**Access:** `blocked` as of 2026-09-03. Falls back to `nango-providers`.

## aggregator

### `apis-guru`

CC0, one file, no auth. The repository behind it was 4.5 months stale at the last probe, so the
vendor's own current descriptor always wins on a conflict.

**Yields:** 2,529 API descriptors across 677 providers and 42 categories. By PROVIDER the largest category is developer_tools at 94; the union across a multi-category map reaches 180/235/282 at two/three/four categories.

**`complete_listing: True`** — walkable end to end in one pass, so an enumerated zero from it is evidence of ABSENCE.

**Access:** `open` as of 2026-09-03. **This row is its family's TERMINAL.**

### `mcp-registry-official`

BOUNDED by the cursor: no total is exposed, so a walk cannot prove completeness.

**Yields:** Server entries, cursor-paginated; the cursor still carries `/` at the last probe.

**`complete_listing: False`** — a listing with a BOUND, so a zero from it is not evidence of absence.

**Access:** `open` as of 2026-09-03. Falls back to `mcp-registry-github`.

### `postman-network`

One host under one robots group. `postman-mcp-catalog` is FOLDED into this row rather than
listed separately — listing it twice would double-count the denominator a later wave divides by.

**Yields:** Public workspaces and collections, paged with no total exposed.

**`complete_listing: False`** — a listing with a BOUND, so a zero from it is not evidence of absence.

**Access:** `polite-pool` as of 2026-09-03. Falls back to `mcp-registry-github`.

### `ecosystems-packages`

A per-package LOOKUP, not a corpus to walk — which is why complete_listing is n/a.

**Yields:** Per-package metadata and dependent counts across every registry the others cover singly.

**`complete_listing: n/a`** — not a listing at all, so an enumeration verdict against it would answer a question that does not apply.

**Access:** `polite-pool` as of 2026-09-03. **This row is its family's TERMINAL.**

### `npm-downloads`

A per-package lookup. A 200 on a registry name is NOT evidence a package exists: an UNPUBLISHED
name still answers 200 with an `unpublished` block and no versions.

**Yields:** Download counts for one named npm package per request.

**`complete_listing: n/a`** — not a listing at all, so an enumeration verdict against it would answer a question that does not apply.

**Access:** `open` as of 2026-09-03. Falls back to `ecosystems-packages`.

### `pypistats`

A per-package lookup.

**Yields:** Download counts for one named PyPI package per request.

**`complete_listing: n/a`** — not a listing at all, so an enumeration verdict against it would answer a question that does not apply.

**Access:** `polite-pool` as of 2026-09-03. Falls back to `ecosystems-packages`.

### `standard-webhooks`

Terminal on REACHABILITY, not adoption: one static spec page, no auth, no paging. Adoption
across the three conventions was never counted, and a terminal is the last channel rather than
the best one.

**Yields:** One specification and its adopter list. Not a listing of services.

**`complete_listing: n/a`** — not a listing at all, so an enumeration verdict against it would answer a question that does not apply.

**Access:** `open` as of 2026-09-03. **This row is its family's TERMINAL.**

### `cloudevents`

A CNCF specification; its adopter list is the searchable surface.

**Yields:** One specification and its adopter list.

**`complete_listing: n/a`** — not a listing at all, so an enumeration verdict against it would answer a question that does not apply.

**Access:** `open` as of 2026-09-03. Falls back to `standard-webhooks`.

### `asyncapi-spec`

Also supplies the descriptor kind a2 records as `asyncapi`.

**Yields:** One specification and its adopter list.

**`complete_listing: n/a`** — not a listing at all, so an enumeration verdict against it would answer a question that does not apply.

**Access:** `open` as of 2026-09-03. Falls back to `standard-webhooks`.

### `merge-docs`

A vendor's documentation of ITS coverage, not a listing of the ecosystem.

**Yields:** One unified-API vendor's own provider coverage, by category.

**`complete_listing: n/a`** — not a listing at all, so an enumeration verdict against it would answer a question that does not apply.

**Access:** `open` as of 2026-09-03. Falls back to `vendor-docs`.

## community

### `public-apis`

A single CC0 file, walkable end to end in one pass — which is the stated criterion for `true`.
Community-curated, so it ranks below both the vendor and the aggregator.

**Yields:** One curated markdown file listing free public APIs by category.

**`complete_listing: True`** — walkable end to end in one pass, so an enumerated zero from it is evidence of ABSENCE.

**Access:** `open` as of 2026-09-03. Falls back to `apis-guru`.

### `mcp-registry-github`

Same shape as the official registry, independently hosted.

**Yields:** Server entries, cursor-paginated with no total exposed.

**`complete_listing: False`** — a listing with a BOUND, so a zero from it is not evidence of absence.

**Access:** `open` as of 2026-09-03. **This row is its family's TERMINAL.**

## Excluded

These may not be queried at all. `forbidden-source-not-active` and `cell-source-excluded` read this block.

### `zapier-internal-api` — `excluded-on-robots`

zapier.com/robots.txt `Disallow: /api/` under the `*` group, read 2026-09-03. The paging shape
the app index uses also matches `Disallow: /*?`.

**Use instead:** `zapier-apps-sitemap`.

### `make-internal-api` — `excluded-on-robots`

make.com/robots.txt disallows the internal API paths, and the public sitemaps answer 403 with
cf-mitigated: challenge as of 2026-09-03.

**Use instead:** `nango-providers`.

### `rapidapi-hub` — `excluded-on-terms`

The hub's terms of use could not be read without an account, so the survey cannot establish that
enumeration is permitted. A source whose terms cannot be read is excluded, not assumed.

**Use instead:** `apis-guru`.
