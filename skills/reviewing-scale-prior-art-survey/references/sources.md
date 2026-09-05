# What each registry row IS, and what a zero from it means

Thirty-two admitted rows and seven excluded. Read this before walking anything: a zero from a row
whose `complete_listing` is `false` says nothing at all, and recording it as evidence is the error
this file exists to prevent.

## The asymmetry, declared

A **governed enumerable corpus** — a3's four listings, b3's index files, b4's limits pages —
carries both `yields` (what the row returns) and `complete_listing: true` (the listing can be
walked completely). A zero from one of these is REAL: you looked at everything and it was not
there.

An **unbounded channel** — `hn-algolia`, `crossref`, `semantic-scholar`, the status histories —
carries `yields` and declares `complete_listing: false`. There is no complete walk to claim, so a
zero says only that your query did not match. A row declaring `complete_listing: true` over an
unbounded index would be asserting a walk nobody performed.

`component-docs` and `open-engineering-blogs` carry `complete_listing: n/a`: they are per-vendor
and per-host, so what they yield depends entirely on which components the scope names.

## The forest

Every row carries a `fallback` and a `fallback_rationale`, and **nine rows are terminals** —
`fallback: null` with the reason recorded in place. Requiring every row to name a fallback in a
finite graph guarantees a cycle by pigeonhole, so the terminals are what make the graph walkable.
Follow `fallback` when a row is unreachable; when you reach a terminal, the branch is exhausted
and the honest record is a skipped cell with its cause, not a substitution from another branch.

## `as_of` is not decoration on this type

It is the direct answer to the six-hosts-moved finding. **A row whose `as_of` is older than the
corpus it claims to describe is a row nobody probed.** Two rows say so about themselves:
`gcp-quotas` was re-derived on 2026-09-04 because the upstream path was still 404, and
`openalex` — in the excluded set — is inherited from an earlier survey and NOT re-probed, flagged
as inherited because in a registry arguing that verification dates are load-bearing, the one
inherited row is exactly the one that must say so.

## The rows, by what they are for

| what it is | rows |
| --- | --- |
| Discovery over the engineering-blog long tail | `hn-algolia`, `awesome-scalability-index`, `engineering-blogs-index`, `highscalability-archive`, `github-blog`, `infoq`, `open-engineering-blogs` |
| Peer-reviewed systems literature | `usenix`, `pvldb`, `arxiv-listing`, `crossref`, `semantic-scholar` |
| First-party operational canon | `sre-google`, `aws-builders-library`, `azure-architecture-center`, `gcp-architecture-framework` |
| Published capacity envelopes | `docs-aws-quotas`, `azure-limits`, `gcp-quotas`, `kubernetes-docs`, `component-docs` |
| Independent safety analysis | `jepsen-analyses`, `jepsen-consistency` |
| Incidents and post-mortems | `post-mortems-index`, `aws-post-event`, `gcp-status`, `azure-status-history`, `cloudflare-outage-tag` |
| Audited and continuous benchmarks | `tpc-results`, `spec-results`, `techempower`, `clickbench` |

## The excluded seven, and why

Recorded so a later reader can tell EXCLUDED from OVERLOOKED. Each carries its `cause_class` and
observable evidence: `netflixtechblog` and `acm-queue` and `acm-digital-library` (403 to every
fetch), `linkedin-engineering` and `github-html` (a catch-all that disallows the paths), `openalex`
(key-mandatory and billed, inherited), `iso-25010` (403 with both mirrors 404). An ACM DOI stays
resolvable through `crossref`; only the HTML host is excluded.

## Recording what you read

Every ACTIVE row in the map carries `sanitization{status, cause}` — `clean` means you read it and
it carried nothing, `modified` means you neutralised something and the cause says what,
`unavailable` and `not-fetched` are different claims and mean what they say. A SKIPPED row carries
`cause_class` and `cause` instead, and never a posture: you did not read it, so there is no posture
to record.
