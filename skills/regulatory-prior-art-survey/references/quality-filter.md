# The quality filter — ranking only, never a cut

Thirteen signals. They order a corpus; they never remove anything from it.

1. A **resolvable `obligation_ref`** — the article, section or clause, not a page.
2. A **verbatim anchor** that is neither a paraphrase nor the whole provision.
3. **Consolidated issuing-body text with a date**, over a summary of it.
4. A **scope condition naming why it binds THIS product** — not a category.
5. **Binding force typed honestly**: binding, guidance, voluntary, contractual.
6. **Externally-owned control ids that actually resolve**, in OSCAL lowercase-dotted form.
7. **A checkable unit** — an ISO-8601 duration beats "promptly".
8. **Ambiguity declared rather than resolved.**
9. **Enforcement evidence attributed** to its article or its published decision.
10. **Delegated acts followed** where the parent instrument defers to one.
11. **Both dates present and distinct** — consolidation and retrieval.
12. **Staged application recorded** where an instrument binds later than it entered force.
13. **What the reading does NOT establish**, written down.

## Explicitly NEVER a cut

- **A paywalled instrument.** Naming it and recording that its text costs money to read is a
  finding. Dropping it means the architecture never learns the standard applies.
- **A guidance-tier instrument.** Guidance that a regulator actually enforces against is worth more
  than a binding instrument nobody has ever applied to a product like this one.
- **An instrument with a low requirement count.** One obligation that reshapes the architecture is
  not thinner than ten that do not.
- **An instrument whose applicability is `undetermined`.** That is a question for counsel, recorded
  as one — not a reason to delete the instrument from the record.

## What the filter is not

It is not a relevance test — the bail is. It is not a confidence score on the LAW; it is a score on
how well THIS record evidences what it claims. And it never resolves an ambiguity: a low score on
signal 8 means the ambiguity was declared, which is the correct outcome.
