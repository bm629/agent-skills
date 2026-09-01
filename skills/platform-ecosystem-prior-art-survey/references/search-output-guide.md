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

`forbidden-by-terms` will never fire for this type: **no registry row prohibits automated
access.** Several rows do address it, and three publish an affirmative
`Content-Signal: ai-train=yes` grant. Addressed-and-permitted is not the same as
unaddressed — `absent-input-policy.md` reserves "not addressed" for the other state — so
read the row before recording either. The enum value's silence is expected, not a gap.

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

An **a3** output, because a3 declares four sources and the example can therefore be COMPLETE. A
shorter angle was used here before with one cell out of eleven declared sources, which taught the
wrong lesson: every source the angle declares owes a cell, and the validator now says so.

```yaml
schema_version: 1
meta:
  angle_id: a3
  retrieved_at: "2026-09-01"
  revision: 1
outcome: ran
coverage:
  - source_id: vscode-contrib
    queries: ["site:code.visualstudio.com/api/references/contribution-points"]
    status: reached
    returned: 38
    kept: 38
    cause: null
    fallback_used: null
  - source_id: vscode-manifest
    queries: ["site:code.visualstudio.com/api/references/extension-manifest"]
    status: reached
    returned: 28
    kept: 0
    cause: null
    fallback_used: null
  - source_id: chrome-ext
    queries: ["site:developer.chrome.com/docs/extensions/reference/manifest"]
    status: reached
    returned: 29
    kept: 0
    cause: null
    fallback_used: null
  - source_id: figma-plugins
    queries: ["site:developers.figma.com/docs/plugins manifest"]
    status: reached
    returned: 21
    kept: 0
    cause: null
    fallback_used: figma-plugin-typings
  - source_id: figma-plugin-typings
    queries: ["site:github.com/figma/plugin-typings index.d.ts manifest"]
    status: reached
    returned: 17
    kept: 0
    cause: null
    fallback_used: null
retrieval_summary:
  status_counts: {reached: 5}
  degraded_sources: []
bound: {cap: 14, hit: false, ordering: "whether the artifact is vendor-published, then schema completeness"}
candidates:
  - platform_slug: vscode
    mechanism: contribution point
    source_id: vscode-contrib
    locator: "https://code.visualstudio.com/api/references/contribution-points"
    retrieved_at: "2026-09-01"
    as_of: null
    source_claimed_modified_at: "2026-08-26"
    source_claim_provenance: visible-byline
    enumeration:
      count: 38
      artifact: "contribution-points reference page"
      method: "h2 heading count over raw HTML"
      branch: null
      reconciled_by: "A second count over the page's own table-of-contents anchor ids returned 38."
unadmitted:
  - item: "the four sources that returned nothing admissible"
    reason: >
      Each was reached and read; none yielded an enumeration with a second derivation available on
      this pass, so nothing was carried at an unreconciled count.
notes: []
```

Read the four `kept: 0` rows: they are the point. A source that was reached and yielded nothing
still owes a cell and a reason, because that is what makes it distinguishable from a source that
was never searched.
