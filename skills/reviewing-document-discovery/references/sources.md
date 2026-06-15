# Sources — reviewing-document-discovery

Research provenance for the nine-condition plan-quality bar. The findings are paraphrased
established practice; no source text is copied. The bar is single-sourced with
`project-document-discovery`'s Self-check, so the grounding is shared with that skill.

## Document planning & tailoring (the standard)

- **ISO/IEC/IEEE 15289** — Content of life-cycle information items (documentation): identifying and
  planning the specific information items to be developed and revised; content by generic document
  type; **tailoring** (items combined/subdivided/omitted as the project needs). Grounds conditions
  1 (proportional), 2 (load-bearing), 8 (open-ended). https://www.iso.org/standard/74909.html · https://standards.ieee.org/ieee/15289/7196/
- **ISO/IEC/IEEE 12207 / 15288** — software / systems life-cycle processes the information items serve. https://www.iso.org/standard/63712.html

## Right-sizing / proportionality (conditions 1, 7)

- **"Just barely good enough" (JBGE) / right-sizing** — a document earns its place only when the
  value beats the cost to write + maintain (ROI); too little OR too much is a risk. Grounds the
  no-over/under-selection + no-padding judgement. https://agilemodeling.com/essays/agileDocumentationBestPractices.htm · https://www.testrail.com/blog/lean-documentation-agile-project/

## Dependency / traceability (conditions 4, 5)

- **Requirements traceability (RTM) + the requirements → design → delivery → docs flow** — the
  acyclic, one-directional information order the production DAG encodes. https://www.testrail.com/blog/requirements-traceability-matrix/

## Amend / living documentation (condition 9)

- **Living documentation** — the document set is re-tailored at planning when the project changes;
  the change-scoped delta (not a re-derive) is the discipline. https://www.ministryoftesting.com/software-testing-glossary/living-documentation
- **Change Impact Analysis** — trace a change to the artifacts that must change; the delta-scoped
  re-validation. https://ldra.com/capabilities/change-impact-analysis-cia-capability/

The full synthesized bar — the nine conditions, their pass/gap signals, and worked findings — is
encoded in this skill's `## Workflow` + `references/plan-quality-bar.md`, grounded in the sources
above.
