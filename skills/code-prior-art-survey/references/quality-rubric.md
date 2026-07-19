# Production-quality rubric (the 0–10 extract score)

The frontmatter `score` is a **holistic integer 0–10 judgment** of the repo's
production-quality, made off the deep read — NOT a weighted sum of sub-scores. It is
**ranking-only**: synthesis sorts the extract set by it; it never cuts a repo
(relevance is the only cut, and it happened before the deep read).

Judge holistically against these ten signals (popularity is ONE signal, deliberately
de-emphasised — a low-star repo can still score high):

1. **Commit recency / velocity** — is it actively maintained?
2. **Issue responsiveness** — are issues triaged and answered?
3. **Bus factor** — more than one meaningful contributor?
4. **CI** — automated checks on PRs?
5. **Tests** — real coverage, especially integration?
6. **Releases** — tagged, changelog'd, semver-ish?
7. **Community profile** — docs, contributing guide, adoption evidence?
8. **OpenSSF signals** — security posture (Scorecard-style, where available)?
9. **Deploy evidence** — is it actually run in production somewhere?
10. **Popularity** — stars/downloads/dependents, as ONE input among ten.

Holistic mapping (guidance, not arithmetic):

- **8–10** — production-grade: maintained, tested, released, deployed in anger.
- **5–7** — solid but with gaps (thin tests, or quiet lately, or single-maintainer).
- **2–4** — promising or reference-only: useful patterns but not production-hardened.
- **0–1** — abandoned / toy / tutorial — record the extraction, score honestly.

The score is defensible (condition 17) when it maps to these signals as read; the
extraction body's "Solved well / poorly", "Testing approach", and "Production setup"
sections are where the evidence for the score lives.
