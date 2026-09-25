# Writing one service's extract record

One admitted service, deep-read. **Two files, one stem**: the record
`extract-<record_filename(item_id)>.yaml` and its companion `.md` carrying the three fixed body
sections. The schema is the contract; this guide says what each field means and where its value
may come from.

## The three rules that decide whether a record is trustworthy

**Every point-in-time fact carries its own date.** A download count, a price, a compliance gate —
each is true on a day and may not be true now. `sdk_downloads` without `sdk_downloads_as_of` and
`pricing_model` without `pricing_as_of` are refused, because an undated number reads as current
forever.

**A count is recorded as the source reports it, never as a rate.** `sdk_downloads_period` carries
the endpoint's OWN window — "last-week", "last-month" — and you do not convert it. Two registries
report over different windows; normalising them here destroys the only thing that made them
comparable, which is knowing they were not.

**`unknown` and `unchecked` are values, not failures.** `api_style`, `descriptor`, `versioning`,
`webhook_signing` and `mcp_server` all carry `unknown`; `rate_limit_documented` carries
`unchecked`. Use them. A candidate surfaced from a catalog cell has not had its docs read, and
recording `none` there asserts a finding nobody established.

## The fields that need saying out loud

| field | where the value comes from |
| --- | --- |
| `id` / `id_class` | verbatim from the spawn param — never re-derived here |
| `category` | frozen-but-extensible, seeded from the discovery convention and a measured vendor taxonomy. Where the two disagree on spelling, the UPSTREAM form wins, because the join with the capability map is what this field is for |
| `integration_pattern` | the upstream's snake_case verbatim, so the value is directly comparable to `integrations.patterns` |
| `auth_scheme` / `oauth_flow` | OAS 3.1's `security-scheme.type` and `oauth-flows` keys, VERBATIM, or `null` where no OAS type expresses the scheme (a token in the URL path is one) — `references/absent-input-policy.md` section 3, the same rule as wave 1. There is no IANA OAuth grant-types registry — that path 404s — so do not cite one |
| `http_scheme` | the IANA HTTP Authentication Scheme Registry, or null |
| `sdk_purls` | purls; `sdk_licenses` are SPDX ids |
| `compliance_gates` | an EMPTY LIST where the gate angle ran and found none — never absent. Absent is indistinguishable from nobody looking |
| `found_by_angle` | comma-joined, written by the coordinator at merge. You carry it through; you do not compute it |

## `presence_count` is NOT a record field

It is a REGISTER field, computed at synthesis by the one stage that reads every record. Reaching
for it here would be an extract child reading a sibling angle's output, which is the dependency
this survey forbids. If you find yourself wanting it, the answer belongs to a later stage.

## The three body sections

- `## Integration surface` — the API products this vendor exposes and the operations this domain
  actually uses, as a bounded top-N list with evidence. Operations outside the list exist; say so.
- `## Evidence` — attributed, dated, quoted from the first-party source. A quote is not a summary.
- `## Cost to integrate` — auth complexity, event handling, normalisation, sandbox, rate limits:
  the components the complexity score sums, written so a reader can audit the score rather than
  accept it.

## A bail still WRITES the record

If the service turns out to serve none of the scope, publishes no public API, is access-gated,
is unreachable, or duplicates a row already queued — write the record in the `skipped` form, with
the typed `cause` and a `detail` in your own words saying what you checked. A queue row with no
file is indistinguishable from work never done, and that is the defect this rule exists for.
