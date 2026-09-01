# Writing an angle's search output

One file per angle. It records the search that ran — not a summary of what you found.

## A recorded ZERO is the evidence

`returned: 0` on a `reached` cell is a measurement: the retrieval executed and the source's answer
was empty. That is what makes a later "no prior art found" defensible. **Omitting the cell instead
destroys the distinction** between "we looked and found nothing" and "we could not look", and
nothing downstream can recover it.

So: `returned` is REQUIRED on a `reached` cell and is `null` — never `0` — on any other status. A
zero meaning "we could not look" is the failure this survey exists to prevent.

## Every non-reached cell carries its cause

With observable evidence: an HTTP status, a redirect target, an error string. `superseded` is this
corpus's characteristic status — a source that 301s to a live replacement is **not** `unreachable`,
because the fetch succeeded. Record the fallback you used.

`forbidden-by-terms` will never fire for this type: automated access is not addressed on any
registry row. Its silence is expected, not a gap.

## The summary duplicates the cells on purpose

`retrieval_summary.status_counts` must reconcile exactly with the cells. It is the record a
reviewer checks the cells against, and a discrepancy is the signal that a failure was laundered
into a zero.

## Three dates, and they are different facts

`retrieved_at` is when you fetched — yours, on your own authority. `as_of` is when the FACT became
true, and is `null` when the content states none. `source_claimed_modified_at` is what the page
says about *itself*, with its provenance — a **belief**, not a fact. One page in this corpus is
footer-dated 2012 while documenting a format from 2023.

**Never default an absent date to the fetch date.** That is the difference between a record saying
"we do not know when this became true" and one that lies.

## Worked example

```yaml
schema_version: 1
meta:
  angle_id: a1
  retrieved_at: "2026-09-01"
  revision: 1
outcome: ran
coverage:
  - source_id: vscode-api
    queries: ["site:code.visualstudio.com/api extension surface"]
    status: reached
    returned: 1
    kept: 1
    cause: null
    fallback_used: null
retrieval_summary:
  status_counts: {reached: 1}
  degraded_sources: []
bound: {cap: 12, hit: false, ordering: "ecosystem size, then documentation depth"}
candidates:
  - platform_slug: vscode
    mechanism: contribution point
    source_id: vscode-api
    locator: "https://code.visualstudio.com/api"
    retrieved_at: "2026-09-01"
    as_of: null
    source_claimed_modified_at: "2026-08-26"
    source_claim_provenance: visible-byline
    enumeration: null
unadmitted: []
notes: []
```
