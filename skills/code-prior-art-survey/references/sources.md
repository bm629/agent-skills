# Research provenance — code-prior-art-survey

This skill was forged spec-guided from a consolidated research dossier (two
citation-tracked deep-research rounds + mined source material, all externally
sanitized with zero findings). Claims in the skill body trace to:

## Search-protocol + record standards (method backbone)

- PRISMA-S (PRISMA extension for reporting literature searches) — per-source
  reporting: name/platform, exact query as run, date searched, result counts,
  justified limits, documented dedupe. → coverage cells, justified filters.
- PRESS 2015 (Peer Review of Electronic Search Strategies) — concept
  translation, operators, variant completeness, spelling, limits. → the
  reviewing sibling's craft conditions; produce-side bar items 1–5.
- SKOS (W3C Simple Knowledge Organization System) — prefLabel/altLabel,
  broader/narrower/related relations. → canonical + expansions with relation
  kinds.
- Query-expansion literature (synonym/morphological expansion; negative terms
  must be explicit; polysemy/disambiguation). → expansions + negative_terms.
- Living systematic reviews (Cochrane model: baseline + predefined updates
  recording inheritance). → delta maps with lineage.
- Data-provenance practice (revisions supersede; never silent edits). →
  revision discipline.
- CodeMeta / schema.org software vocabulary — minimal software record fields.
  → candidate record completeness (description, language, license).
- Software Heritage / SWHID-style identity — canonical, persistent artifact
  identity vs mutable URLs. → `<host>__<owner>__<name>` canonical ids.
- MSR-2020 GitHub deduplication research (10.6M repositories are copies of
  others). → fork/mirror/archived honesty flags.
- Screening-tool practice (Covidence/Rayyan; PRISMA counts) — stable record
  identity, per-source records preserved, premature merges break counts. →
  point-in-time `as_of` signals; per-angle outputs kept intact.

## Discovery-channel taxonomy (the 6+3 angles + the source registry)

15-search sweep across: GitHub-native surfaces (topics/collections/trending/
operators), awesome/best-of lists + landscape/radar catalogs, package
registries + dependents graphs (deps.dev, libraries.io, ecosyste.ms, GitHub
Used-by), public code search (Sourcegraph, grep.app), alternative/self-hosted
directories, community channels (Reddit/HN/Stack Overflow), academic code
channels post-Papers-With-Code (arXiv, Semantic Scholar, HF Papers,
CatalyzeX, OpenCodePapers), model hubs, platform registries/marketplaces,
analytics/criticality datasets (OSS Insight, OpenSSF criticality score —
screening-wave inputs, deliberately not search angles).

## Mined source material (sanitized before reading; paraphrased, never copied)

- bytedance/deer-flow `github-deep-research` — broad-to-narrow query round
  templates; source-prioritization weighting; record-the-URL provenance rule.
- lingzhi227/agent-research-skills `github-research` — independent pipeline
  convergence (discover 50–200 → filter 15–30 → deep-dive 8–15); separation
  of computable scores from LLM relevance judgment; GitHub search API rate
  limits; code-search-by-identifier query shapes.
- github/awesome-copilot `autoresearch` — reviewed; no method adopted
  (experiment-loop skill, different problem).
