# Sources

The registry (`source-registry.yaml`) is the single list of what this survey reads. Every row was
verified at the primary source on the date it states — not inherited from a sibling survey and not
carried forward from an earlier pass.

## Every row names a fallback that itself resolves

A fallback that does not resolve is not a fallback. Two were found being carried as though they
were: one legislative endpoint returning HTTP 202 with a zero-byte body, and one entry reading
"the platform's own discussion board", which names no host.

## Channel death is the failure mode here, not access

This corpus is unusually open — no ToS gate, no key gate on any row. What it does instead is
**move**. In one eleven-day window four URLs changed, one row went from 404 to 403, and a
previously-undated policy page gained a date. So:

- Re-verify at authoring time. A row verified last month is not verified.
- A `200` that returns a JavaScript shell is **not** verified. Two rows are recorded `unavailable`
  for exactly this reason.
- A `403` is not a `404`. Blocked and absent are different facts needing different remedies.

## Machine-readable variants are channels too

Prefer them, but record which one you read and treat the convention as mutable: one host's
plain-text variant moved to a different extension inside eleven days while another host kept the
old one, so two hosts in this corpus now disagree.
