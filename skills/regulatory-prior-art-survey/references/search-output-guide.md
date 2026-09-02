# Writing one angle's search output (wave 1)

One file per search child, at `search/<angle_id>.yaml`. It records what this angle retrieved as a
2-D coverage grid, plus the instruments it admitted.

## Read `outcome` first — it decides what is owed

| `outcome` | owed |
| --- | --- |
| `ran` | cells, and candidates if anything was admitted |
| `not_run` | NOTHING, plus a `not_run.map_verdict` naming the verdict being honoured |
| `vacated` | cells, their causes, a `vacated.cause` and a `retrieval_summary`; candidates and `unadmitted` rows are NOT owed |

`not_run` means the map ruled this angle out. Searching anyway inflates the survey with an angle
the scope excluded.

## The owed set has THREE terms

    groups = the map's groups whose `type` is in your angle's `applicable_group_types`
    owed   = {(g, s) for g in groups for s in YOUR angle's sources INTERSECT the map's ACTIVE list}

Dropping the angle's OWN source list is not a paraphrase. On the shipped exemplar it turns 25
owed cells into 100, and a reviewer applying it finds 75 missing cells in a correct artifact.
Dropping the ACTIVE intersection instead is invisible HERE — a1 carries none of the map's one
skipped row — and shows on b5, whose 12 owed cells become 16. That is why the number has to be
read off the angle in front of you and not off this exemplar.

## Say "as adopted" in any count frame over an EU act

The `CELEX-` grammar this survey ships accepts only the as-adopted form — sector 3 and sector 6,
no date suffix — so every angle that resolves at `eu-cellar` carries acts AS ADOPTED, not
consolidated. A frame that does not say so describes a different document from the one fetched.
This binds a1, b1, b2, b3, b4 and b5 alike; a1's reference restates it because a1 is where the
whole EU legal corpus is entered.

## One document reached on two axes

`item_id` is unique across the artifact, so when a jurisdiction cell and an instrument cell reach
the same document only one of them can carry a row. **Either shape is legal and the FRAME must say
which you took**: record it `reached` with the document counted in `returned` and `kept: 0`, naming
where it is carried; or record the cell `not-attempted` because the identifier was already
resolved. What is not legal is choosing differently for two cells in one artifact without saying so
— a reviewer reading "reach" on one axis and "no attempt" on the other for identical facts cannot
tell which is the record.

## Record every query VERBATIM as issued

For an identifier resolver that means the URI **and the headers**, because on this corpus the
headers are part of the query: the same Cellar URI returns 200 under `Accept: application/xhtml+xml`
and 404 under `Accept: text/html`. A query recorded without them cannot be re-run.

## A zero is RECORDED, never omitted

`returned: 0` on a reached cell IS the evidence, and it owes no cause and no frame. An omitted pair
and a recorded zero are different facts and only one of them is evidence.

A non-zero count owes a `count_frame`: in this corpus a bare count is not re-derivable, because
whether an amending act counts separately from the act it amends changes the number without
changing the search.

## `kept` counts ROWS, and it counts BOTH lists

`kept` is the candidate rows this cell carried into `candidates` **plus** the `unadmitted` rows
naming it. Never a result count: under a result-count reading, a row found and dropped WITHOUT a
record satisfies the arithmetic — which is the one thing `unadmitted` exists to make impossible.

## `authority` and `binding_force` are two fields

`authority` is how close to the ISSUING BODY the text is. `binding_force` is whether and how it
binds. PCI DSS is authority `incorporated-standard` and binding force `contractual` — it is not law
and it binds anyway. **Neither ever CUTS.**

## An instrument you cannot verify is `unadmitted`, and the reason is VERIFIABILITY

An instrument known only from a tier-4 tracker is recorded in `unadmitted` with a `reason_class`
from a closed set — `unresolvable-at-issuing-body`, `no-stated-version-or-date`, `superseded`,
`out-of-scope-for-this-angle`, `duplicate-of`.

**No member of that set is an authority judgement, and that is deliberate.** Admission is refused
on VERIFIABILITY — whether the instrument resolves at a NAMED issuing body with a stated version or
date — never on how its source ranks.

Read that precisely, because it is narrower than it looks: `unresolvable-at-issuing-body` and
`no-stated-version-or-date` are the verifiability members. `superseded`, `duplicate-of` and
`out-of-scope-for-this-angle` are not — they are facts about the instrument's standing, its
uniqueness in this artifact, and this angle's mechanism. What the set excludes is an AUTHORITY
judgement, not everything that is not verifiability. An instrument that resolves cleanly and simply
does not bind this scope fits none of the five, and goes in the top-level `notes`. Free
prose could phrase the first as the second with nothing able to tell; an enum cannot.

## Never quote a text you could not read

`text_retrievable` is `full-text | summary-only | paywalled | blocked`. A `paywalled` or `blocked`
record carries its NUMBER and **no** `evidence_quote`. *"ISO/IEC 27001 applies here and its text
costs money to read"* is a genuine finding. A paraphrase of a clause nobody saw is the fabrication
this type must not have.

`summary-only` is the state where the CATALOGUE entry was readable even though the instrument was
not — quoting the catalogue there is honest.

## Worked example — angle b4, against the shipped clean map

Nine owed cells: three groups (`adequacy-decision`, `eu`, `us-federal`) across b4's three
sources, all active.

```yaml
schema_version: 1
meta:
  angle_id: b4
  retrieved_at: '2026-09-02'
  revision: 1
  note: >
    Every EU act was resolved by CELEX through eu-cellar under the Accept/Accept-Language pair the
    registry row records. `ico` was budgeted at its declared 6 s. No fallback was walked.
outcome: ran
coverage:
- group_id: adequacy-decision
  source_id: eu-cellar
  queries:
  - 'GET http://publications.europa.eu/resource/celex/32021D0914 (Accept: application/xhtml+xml; Accept-Language: eng)'
  timestamp: '2026-09-02'
  status: reached
  returned: 1
  count_frame: One implementing decision, resolved AS ADOPTED by CELEX. The identifier resolves to exactly one
    document, so the count is 1 by construction rather than by selection.
  kept: 1
  cause: null
  fallback_used: null
- group_id: adequacy-decision
  source_id: edpb
  queries:
  - 'GET https://www.edpb.europa.eu/documents_en (filtered for transfer-tool guidance)'
  timestamp: '2026-09-02'
  status: reached
  returned: 3
  count_frame: Guidance documents listed under the transfer-tools heading, counted as index
    entries. Guidance is not an instrument, so none is a candidate on its own.
  kept: 0
  cause: null
  fallback_used: null
- group_id: adequacy-decision
  source_id: ico
  queries:
  - 'GET https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/international-transfers/'
  timestamp: '2026-09-02'
  status: reached
  returned: 1
  count_frame: One guidance page on the UK transfer mechanism, counted as an index entry.
  kept: 1
  cause: null
  fallback_used: null
- group_id: eu
  source_id: eu-cellar
  queries:
  - 'GET http://publications.europa.eu/resource/celex/32021D1772 (Accept: application/xhtml+xml; Accept-Language: eng)'
  timestamp: '2026-09-02'
  status: reached
  returned: 1
  count_frame: One adequacy decision, resolved AS ADOPTED by CELEX from the destination-jurisdiction
    shortlist.
  kept: 1
  cause: null
  fallback_used: null
- group_id: eu
  source_id: edpb
  queries:
  - 'GET https://www.edpb.europa.eu/documents_en (filtered for adequacy)'
  timestamp: '2026-09-02'
  status: reached
  returned: 0
  count_frame: null
  kept: 0
  cause: null
  fallback_used: null
- group_id: eu
  source_id: ico
  queries:
  - '(not attempted) would have been GET https://ico.org.uk/for-organisations/sector-guidance/'
  timestamp: '2026-09-02'
  status: not-attempted
  returned: null
  count_frame: null
  kept: null
  cause: >
    The EU jurisdiction axis against the UK supervisory authority's own guidance index. The ICO
    publishes on the UK side of the transfer; the EU-side instruments are eu-cellar's. Recorded as
    a choice, not a failure.
  fallback_used: null
- group_id: us-federal
  source_id: eu-cellar
  queries:
  - '(not attempted) would have been GET http://publications.europa.eu/resource/celex/<id> over the
    US jurisdiction shortlist, which resolves no CELEX'
  timestamp: '2026-09-02'
  status: not-attempted
  returned: null
  count_frame: null
  kept: null
  cause: >
    The US jurisdiction axis against the EU act register. Cellar holds no US federal transfer
    instrument by construction.
  fallback_used: null
- group_id: us-federal
  source_id: edpb
  queries:
  - 'GET https://www.edpb.europa.eu/documents_en (filtered for third-country transfers)'
  timestamp: '2026-09-02'
  status: reached
  returned: 2
  count_frame: >
    Guidance documents on transfers to this destination, counted as index entries. Guidance is not
    an instrument, so neither is a candidate on its own.
  kept: 0
  cause: null
  fallback_used: null
- group_id: us-federal
  source_id: ico
  queries:
  - 'GET https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/international-transfers/'
  timestamp: '2026-09-02'
  status: reached
  returned: 1
  count_frame: One guidance page on transfers to this destination, counted as an index entry.
  kept: 0
  cause: null
  fallback_used: null
retrieval_summary:
  status_counts:
    reached: 7
    not-attempted: 2
  degraded_sources: []
bound:
  cap: 18
  hit: false
  ordering: adequacy status, then jurisdiction reach
  dropped_note: null
  ordering_deviation: null
candidates:
- item_id: CELEX-32021D0914
  id_class: CELEX
  found_by: adequacy-decision/eu-cellar
  name: Standard Contractual Clauses implementing decision
  authority: primary-law
  binding_force: law
  locator: http://publications.europa.eu/resource/celex/32021D0914
  retrieved_at: '2026-09-02'
  as_of: null
  source_claimed_modified_at: null
  source_claim_provenance: absent
  evidence_quote: >
    "The standard contractual clauses set out in the Annex to this Decision combine general clauses
    with a modular approach to cater for various transfer scenarios and the complexity of modern
    processing chains."
  claim: >
    The decision states that the clauses are modular and selected per transfer scenario. Which
    module binds is therefore a function of the transfer topology, not of the instrument alone.
  text_retrievable: full-text
  in_force_date: null
  jurisdiction: European Union
  issuing_body: European Commission
  instrument_type: decision
  finding: null
  provenance:
    celex: '32021D0914'
    eli: null
    cfr_citation: null
    standard_number: null
    doi: null
  notes: []
- item_id: CELEX-32021D1772
  id_class: CELEX
  found_by: eu/eu-cellar
  name: UK adequacy decision (GDPR)
  authority: primary-law
  binding_force: law
  locator: http://publications.europa.eu/resource/celex/32021D1772
  retrieved_at: '2026-09-02'
  as_of: null
  source_claimed_modified_at: null
  source_claim_provenance: absent
  evidence_quote: 'celex: 32021D1772; instrument_type: decision; issuing_body: European Commission'
  claim: >
    The register carries an adequacy decision for this destination. Where one covers the
    destination, the controller does not run the assessment the next candidate describes.
  text_retrievable: full-text
  in_force_date: null
  jurisdiction: European Union
  issuing_body: European Commission
  instrument_type: decision
  finding: >
    The decision states a review date rather than an indefinite term, so the transfer route it
    authorises has an expiry an architecture decision has to account for.
  provenance:
    celex: '32021D1772'
    eli: null
    cfr_citation: null
    standard_number: null
    doi: null
  notes: []
unadmitted:
- item_id: UK-IDTA
  found_by: adequacy-decision/ico
  name: International Data Transfer Agreement
  locator: https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/international-transfers/
  reason_class: unresolvable-at-issuing-body
  reason: >
    The ICO's guidance names the instrument and links its text at legislation.gov.uk, which answers
    202 with a zero-byte body to every user agent tried. It does not resolve at a named issuing
    body, so it is not admitted. NOT an authority judgement -- the ICO is authority tier 2 and its
    guidance is carried elsewhere; this row fails on verifiability, which is a different test.
notes:
- >
  Cross-group lead for a1: the empowering article behind these instruments sits in the general
  privacy regulation, which is a1's corpus rather than this angle's.
```

Note what the second candidate's `evidence_quote` does. The adequacy register returns a structured
entry rather than prose, so the quote is the FIELD VALUES verbatim. That is a full warrant, not a
degraded one — quoting fields is what an identifier resolver makes available, and reaching for a
rendered page to obtain a sentence would spend budget for evidence no stronger.
