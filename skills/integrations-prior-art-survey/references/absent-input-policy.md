# Absent input — what to record when something is not there

An absence recorded honestly is a finding. An absence recorded as a zero, or not recorded at all,
is a hole that reads like a result. Four cases, each with the shape it takes in the artifact.

## 1. A dead source

A channel that answered before and refuses now — `make-integrations-sitemap` today, which returns
403 with `cf-mitigated: challenge` on all eleven sitemaps its own robots.txt declares.

**In the MAP:** the row goes in `skipped[]` with `cause_class: refused` and a cause carrying
OBSERVABLE evidence — an HTTP status, a redirect target, a challenge body, an auth wall. Not "it
seemed down".

**In the SEARCH output:** the row is not in `active[]`, so it is not in the owed grid at all. Do not
write a cell for it. The registry keeps the row with its evidence and its fallback, because a row
deleted on a 403 is a row nobody re-probes.

**Never** record it as `active` with `access_status: blocked`. That combination is refused by
construction: `blocked` is a REGISTRY value only.

## 2. A thin corpus — the source answered and returned little or nothing

Record the cell as `reached` with `returned: 0` and, where the row is a COMPLETE listing
(`complete_listing: true`) that you walked end to end, `enumerated: true`. On a BOUNDED listing
(`complete_listing: false`) the honest value is `false`, and `enumerated-zero-is-a-claim` refuses
`true` there whatever `returned` is. **That is the whole point of the field.** An enumerated zero is evidence the
service is absent from that catalog; a bounded zero is not evidence of anything.

A zero needs no `count_frame` — there is nothing to frame — but one is PERMITTED and is often worth
recording, because the most useful zeros are the ones whose frame explains them. It does need `kept: 0`, and no candidate
or unadmitted row may cite the cell.

## 3. An out-of-enum classification value

The catalog says something the vocabulary does not carry — an `auth_mode` with no OAS 3.1 member,
a category outside the seeded union.

**For `auth_scheme` / `oauth_flow`:** record `null`. Forcing the nearest-looking member asserts a
scheme the service does not offer.

**The nine catalog auth modes this type maps, and what each maps to.** Count the `null` rows — the
number is not restated here, because a count beside a table is a second statement of the table:

| catalog `auth_mode` | OAS 3.1 `auth_scheme` |
| --- | --- |
| `API_KEY` | `apiKey` |
| `OAUTH2` | `oauth2` |
| `OAUTH2_CC` | `oauth2` |
| `BASIC` | `http` |
| `JWT` | `http` |
| `OAUTH1` | **`null`** — OAuth 1.0a is not an OAS 3.1 security-scheme type |
| `TWO_STEP` | **`null`** — a vendor-specific exchange with no OAS member |
| `MCP_OAUTH2` | **`null`** — an agent-channel profile, not an OAS scheme |
| `NONE` | **`null`** — the catalog states there is no auth at all |

**A value NOT in this table takes the same treatment**: record `null`, and put the catalog's own
value in `notes[]` so a reviewer can check what it was. Without that the null is unfalsifiable.

**For `api_style` and `descriptor` — a field THIS ANGLE cannot observe:** record `unknown`. a1
walks connector catalogs and an API style or a descriptor kind is a2's channel, so `none` from a1
asserts the vendor exposes neither — a finding a later wave produces, and recording it from an angle
that cannot establish it deletes exactly that finding. This is the same reasoning the admission
carve-out applies, one field down.

**For `category`:** it is a frozen-but-extensible VOCABULARY, not an enum, and the seed is in
`references/category-vocabulary.md`. Record the value the
corpus uses and put its provenance in `notes[]`. Calling it an enum would promise a closed set this
type cannot close.

**For `http_scheme`:** record the descriptor's spelling VERBATIM, including `bearer` in lower case.
The match is case-insensitive; the record is not normalised.

## 3b. What a CORPUS ROW is, and why a catalog cell can still fail conjunct (b)

`no-retrievable-corpus-row` and a `found_by` naming a catalog cell are not in tension, because the
two speak about different things. A **corpus row** is a structured entry the survey can retrieve and
re-read: a connector-catalog row, a descriptor, a package-registry record. A sitemap URL or a
listing page that names a service without carrying an entry for it is a POINTER, not a row.

So a service surfaced by `zapier-apps-sitemap` — `url_kind: sitemap` — whose name resolves to no
catalog entry and no descriptor correctly fails conjunct (b), even though a cell produced it. Say
so in the `reason`: name the channels you tried.

## 4. A ruled-out angle

The map recorded `holds: false` for this angle, naming the DECIDING value.

**In the SEARCH output:** `outcome: not_run`, and a `not_run{map_verdict}` block quoting the map's
reason. **Nothing else** — no cells, no candidates, no bound, no summary. Searching anyway inflates
the survey with an angle the scope excluded.

An always-on angle can never be here. `always-on-angle-holds` refuses a map that tries.

## The case that is NOT an absent input

Every channel refused, but the angle DOES hold. That is `outcome: vacated`: cells with their
statuses and observable causes, a `vacated{cause}`, and a `retrieval_summary`. Candidates and
unadmitted rows are NOT owed, because recording either means a search happened.
