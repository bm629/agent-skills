# Sources

Provenance for the research behind this skill. **Not the runtime source list** — that is
`source-registry.yaml`, which is a validator input rather than prose.

Every entry below was read at its primary source on the date shown, not taken from a summary of
it. Two earlier drafts of this survey's source list were built from second-hand digests and each
misreported at least one source, which is why the method is recorded here alongside the finding.

## Method standards

- **PRISMA-S** — the reporting extension for literature searches in systematic reviews, 16
  checklist items (Rethlefsen et al., 2021; read at the open PMC mirror, 2026-08-04). Three items
  ground this survey's coverage grid directly: item 8 requires search strategies "copied and
  pasted exactly as run", item 13 requires the date of each search, and item 15 requires the
  number of records identified from each source. The grid is those three per cell.
- **GRADE Working Group** — certainty of evidence and its rating domains (read 2026-08-04).
  GRADE folds **indirectness into the single certainty rating**, which is exactly why this survey
  keeps transferability as a separate field: a methodologically excellent study of a different
  population is high-certainty and low-transferability, and one collapsed rating hides the thing
  the reader must decide on. Both fields belong to the extract wave.
- **SKOS** — the relation vocabulary (`broader`, `narrower`, `related`, `alt-label`) the map's
  expansions are typed with.

## Source access, verified by direct fetch (all 2026-08-04)

Each of the following was checked at its own robots file, terms page or API documentation. The
findings are encoded in `source-registry.yaml` with their `verified` dates; the notable ones:

- **arXiv** — the API Terms of Use expressly permit programmatic metadata retrieval at one
  request per three seconds on a single connection, and require the acknowledgement "Thank you to
  arXiv for use of its open access interoperability." The API host's robots file is nonetheless
  `Disallow: /` outright, and the main host's catch-all disallows `/api`. The registry records the
  conflict rather than adjudicating it, and reaches arXiv through the listing and abstract paths,
  which the same robots file explicitly allows at a 15-second crawl delay.
- **Crossref** — no sign-up, no key; polite pool via a `mailto` parameter; metadata stated to be
  almost entirely free of copyright.
- **Semantic Scholar** — key optional; the unauthenticated pool is documented as one thousand
  requests per second **shared across all unauthenticated users**, explicitly throttleable under
  load. This is why a 429 there is a normal operating condition rather than an outage.
- **Europe PMC** — the website's robots names several crawlers individually and closes with
  `User-agent: * / Disallow: /`; its REST API is a **separate host** whose catch-all allows the
  webservices path at a 10-second delay. Two hosts, two policies.
- **Nielsen Norman Group** — catch-all `Crawl-Delay: 60`, with `/search/` disallowed. The delay is
  why the practitioner angle's cap is twelve.
- **Baymard** — free articles reachable; `/design-examples/` and all of `/premium` disallowed by
  robots, and the guideline set is behind the subscription.
- **W3C WAI**, **Android developers**, **Apple developer**, **Stack Overflow survey** — the
  relevant documentation paths are reachable; the disallowed paths are recorded per source.

## Excluded, and why

- **OpenAlex** — an API key became mandatory on 2026-02-13, usage is billed, and the polite pool
  is discontinued. A key-less survey cannot reach it at all.
- **ACM Digital Library** — a direct fetch returns HTTP 403. Excluded as a fetch target only:
  ACM-published work remains reachable by DOI, so a candidate carrying an ACM DOI is admissible.

Both were named by this survey's superseded draft. They are recorded rather than dropped so a
later reader can tell an excluded source from an overlooked one.
