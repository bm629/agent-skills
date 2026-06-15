# Sources — reviewing-document-set

Research provenance for the eight-dimension cross-document coherence bar. The findings are paraphrased established practice; no source text is copied.

## Requirements quality characteristics (consistency, completeness, traceability)

- IEEE 830 SRS quality characteristics — correct, unambiguous, complete, consistent, ranked, verifiable, modifiable, traceable. [IEEE 830-1998](https://ieeexplore.ieee.org/document/720574/) · [overview](https://www.numberanalytics.com/blog/mastering-ieee-830-for-software-requirements) · [Wikipedia](https://en.wikipedia.org/wiki/IEEE_830)
- The Three Cs of Requirements (Consistency, Completeness, Correctness). [paper](https://www.researchgate.net/publication/2571755_The_Three_Cs_of_Requirements_Consistency_Completeness_and_Correctness)
- SRS review/inspection checklists — conflicting/duplicate requirements, cross-reference correctness, consistent level of detail, error-condition coverage. [Toronto requirements checklist (PDF)](https://www.cs.toronto.edu/~sme/CSC340F/2005/assignments/inspections/reqts_checklist.pdf) · [SRS review guidelines](https://www.softwaretestingclass.com/guidelines-to-review-software-requirements-specification-srs-document-the-complete-checklist/) · [specification inspection](https://t2informatik.de/en/blog/inspection-of-the-specification/)

## Traceability (carried-downstream, orphans, dependency integrity)

- Requirements traceability — forward / backward / bidirectional; orphans and coverage gaps; periodic audits. [Jama](https://www.jamasoftware.com/requirements-management-guide/requirements-traceability/traceability-matrix/) · [Perforce](https://www.perforce.com/resources/alm/requirements-traceability-matrix) · [forward/backward](https://www.kualitee.com/blog/testing/traceability-in-testing-and-how-to-achieve-it/) · [RTM best practices](https://www.compliancequest.com/cq-guide/creating-maintaining-requirements-traceability-matrix/)

## Terminology consistency & no-duplication

- Single source of truth + terminology management — one authoritative term per concept, controlled vocabulary, avoid divergent duplication. [SSOT (Wikipedia)](https://en.wikipedia.org/wiki/Single_source_of_truth) · [SSOT (Paligo)](https://paligo.net/blog/content-reuse/what-is-single-source-of-truth-ssot/) · [terminology management](https://www.adoc-studio.app/blog/terminology-management-in-technical-communication)

## Ready-to-plan (Dimension 6)

- Definition of Ready / INVEST — sufficient to plan & estimate, dependencies identified, testable acceptance, no TBD. [Atlassian: DoR](https://www.atlassian.com/agile/project-management/definition-of-ready) · [Scrum.org: DoR](https://www.scrum.org/resources/blog/walking-through-definition-ready)

## Amend / delta-scoped re-review (Dimension 7)

- Change Impact Analysis — trace a change's ripple across artifacts (requirements, design, docs) to the dependents that must change; identify not just the directly-changed artifact but the artifacts changed *due to* ripple. [LDRA: CIA](https://ldra.com/capabilities/change-impact-analysis-cia-capability/) · [Jama: CIA best practices](https://www.jamasoftware.com/blog/change-impact-analysis-2/) · [Tricentis](https://www.tricentis.com/learn/change-impact-assessment)
- Requirements ripple-effect — the probability that a change in one requirement affects another; delta-scoped re-validation of the affected edges. [Springer: ripple-effect metric](https://link.springer.com/article/10.1007/s11219-021-09581-y)

## Version skew / stale cross-reference (Dimension 8)

- Artifacts "evolve at different rates" — a document built on a superseded version/decision of another is a distinct staleness defect (the root cause consistency-checking research names). [academia.edu: automated consistency checking](https://www.academia.edu/6134829/Automated_consistency_checking_of_requirements_specifications) · [DTIC ADA465574](https://apps.dtic.mil/sti/tr/pdf/ADA465574.pdf)

The full synthesized bar — what to look for, how to judge it across documents, and example defects per dimension — is encoded in this skill's `## Workflow` (the eight dimensions) + `references/coherence-bar.md`, grounded in the sources above.
