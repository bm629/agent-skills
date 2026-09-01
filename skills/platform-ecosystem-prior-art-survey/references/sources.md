# Sources

The registry (`source-registry.yaml`) is the single list of what this survey **searches**, and
every `coverage` cell and every `candidate` cites a row in it.

One thing may be read but never cited: a non-registry artifact that a registry source's own text
disagrees with. a3's headline finding is exactly that shape — a community-maintained schema
enumerating a manifest version the vendor page says is unsupported. Record it in `unadmitted` with
the disagreement as the finding, never as a candidate, and let the normative text govern. The line
is between the corpus you SEARCH (closed, re-runnable, the registry) and evidence you ENCOUNTER
while reading it (recorded, never counted). Every row was
verified at the primary source on the date it states — not inherited from a sibling survey and not
carried forward from an earlier pass.

## Every row names a fallback, and none names one that fails to resolve

A fallback that does not resolve is not a fallback. Two were found being carried as though they
were: one legislative endpoint returning HTTP 202 with a zero-byte body, and one entry reading
"the platform's own GitHub Discussions", which names no host.

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
