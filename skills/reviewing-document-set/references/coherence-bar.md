# The eight-dimension corpus-coherence bar — pass/gap signals + worked findings

Depth for `reviewing-document-set`'s Step 2. Each dimension lists what a **pass** looks like,
what a **gap** looks like, and a worked cross-document finding (every defect is *between*
documents; every finding line starts with the affected document id(s) in brackets). The body
SKILL.md carries the method; this file carries the per-dimension detail. Dimensions 1–5 are the
kept spine; 6 is deepened; 7 and 8 are the production-grade additions — load this esp. for 6/7/8.

## Dimension 1 — Cross-document consistency (incl. one name per entity)

- **Pass:** the same fact/number/decision/scope/entity reads the same in every document that
  touches it; one name per concept.
- **Gap:** a substantive mismatch (a value/decision/scope stated differently) OR a key-term
  mismatch (one entity under two names with no statement they are the same).
- **Not a gap:** prose style, tone, harmless synonyms.
- **Worked:** `- [d-prd, d-data-model] the PRD calls them "members", the data-model "accounts", with no note they are the same entity — pick one name and align both.`

## Dimension 2 — Completeness & traceability (anchored on the root)

Root-anchored and bidirectional in substance (forward = dropped-requirement; backward = orphan).

- **Pass:** every root-document goal/requirement is carried forward into the docs that elaborate
  it (forward); no document references nothing upstream and is referenced by nothing (backward);
  no unresolved TBD/placeholder.
- **Gap:** a dropped requirement (in the root, absent everywhere downstream — only the
  root-anchored pass catches it, a pairwise scan cannot), an orphan, or a live TBD.
- **Worked:** `- [d-prd, d-feature-spec] PRD goal G3 (offline mode) is never elaborated in the feature-spec or any downstream doc — carry it forward or record it as cut.`

## Dimension 3 — Contradiction detection

- **Pass:** no two documents assert facts/decisions that cannot both be true.
- **Gap:** a logical impossibility (not merely worded differently — that is Dimension 1).
- **Worked:** `- [d-arch, d-feature-spec] arch-doc mandates async event delivery; the feature-spec's AC requires a synchronous confirmation in the same call — they cannot both hold; reconcile.`

## Dimension 4 — Dependency integrity

- **Pass:** each document faithfully elaborates its declared upstreams — same entities,
  decisions, scope; adds detail without contradicting or quietly re-scoping them.
- **Gap:** a document that silently re-scopes or contradicts a declared upstream (even with no
  single value visibly conflicting).
- **Worked:** `- [d-feature-spec] declares the PRD as upstream but adds a bulk-export feature the PRD's MVP boundary explicitly excludes — a quiet re-scope; align with the PRD or amend the PRD first.`

## Dimension 5 — No divergent duplication

- **Pass:** a fact/decision/definition lives in one owning document and is referenced elsewhere.
- **Gap:** the same thing copied into two places that now disagree (or substantial unowned
  redundancy that will drift).
- **Not a gap:** a one-line contextual recap that references the owner.
- **Worked:** `- [d-data-model, d-api-spec] the retention period is stated as 30 days in the data-model and 90 days in the api-spec — own it in one (the data-model) and reference it from the other.`

## Dimension 6 — Ready-to-plan (the verdict-driver, deepened)

The approve/revise pivot. Apply the **Definition-of-Ready backbone** as the concrete test:

- **Dependencies named** — every cross-document/external dependency the corpus relies on is
  identified somewhere in the set. *Gap:* a named-but-unspecified dependency (a doc says "via the
  billing service" but no document specifies it). 
- **Testable acceptance somewhere** — every load-bearing requirement has testable acceptance in
  *some* document of the set (the corpus, not one doc, must carry it).
- **No blocking TBD** — no unresolved decision a later phase depends on.
- **Referenced-but-absent load-bearing document** — a document the *handed-in set references but
  does not contain*. Infer it from the **dangling reference inside the set**; never demand a doc
  from an external "ideal list" (no data-model for a stateless CLI tool is not a defect — there
  is no manifest here).
- **Worked (referenced-but-absent):** `- [d-api-spec] references "the Order schema in the data-model" but no data-model is in the set — the corpus cannot be planned until the referenced data-model is provided.`
- **Worked (DoR backbone):** `- [d-feature-spec] feature F2 depends on "the notification service" but no document in the set specifies it — name and specify the dependency, or the planner is blocked.`

## Dimension 7 — Amend / delta-scoped re-review (CIA; applies only on a change)

- **Applies only** when a change was handed in (a delta, version bump, changelog). **n/a on a
  greenfield first-pass.** Both triggers — (a) producers fixing a prior `revise`, (b) an upstream
  doc changing independently — run the same method.
- **Method:** identify the changed doc(s) → trace the ripple to dependents (docs declaring the
  changed doc as upstream) → propagation check (did it land, or is the dependent stale?) →
  delta-scoped (re-validate only the affected edges + second-order ripples, not the whole corpus).
- **Pass:** every dependent of the changed document reflects the change.
- **Gap:** a dependent the ripple never reached (a freshly-created skew — see Dimension 8).
- **Changed-but-no-delta:** if the set clearly changed but no delta is handed in, the dynamic
  trace is n/a — rely on Dimension 8 (static) on the full pass; do not invent a change history.
- **Worked:** `- [d-prd, d-api-spec] the PRD changed the auth model OAuth → SAML (v2); the api-spec still specifies OAuth — propagate the change into the api-spec (the ripple did not reach it).`

## Dimension 8 — Version skew (stale cross-reference; static)

- For each explicit cross-reference (A cites a decision/value/entity/version of B), confirm A
  reflects B's **current** state.
- **Overlap guard (do not double-flag):** Dimension 8 fires **only** for a *staleness/currency*
  defect — A built on a **superseded version/decision** of B. A plain value-disagreement → 1; a
  flat impossibility → 3; a quiet re-scope → 4. Do not revise under 8 a defect already named
  under 1/3/4.
- **n/a on a single-version set** (no prior state to be stale against).
- **Relationship to 7:** 8 is the *static* twin of 7's *dynamic* propagation check — 7 finds a
  skew when a change is announced; 8 names a skew on any pass, signal or not.
- **Worked:** `- [d-arch] cites "the Customer entity (data-model §3)" but the data-model renamed it Account in v2 — update the architecture-doc's reference to the current entity (a stale-version reference, not a plain inconsistency).`

## Proportionality (the no-false-revise guard)

The audit depth and which dimensions apply scale with corpus size. A small, coherent set (2–3
docs, few edges) is **approved**. Dimensions 7 (amend) and 8 (version-skew) are explicitly n/a on
a greenfield first-pass / single-version set. A heavyweight RTM-style audit on a thin or first-pass
corpus is a false-revise — proportionality judges the corpus, not a fixed checklist.

## The output contract (unchanged)

Zero or more per-document-attributed finding lines (each starting `- [id, …]`), then **exactly
one** terminal `VERDICT: approve|revise` for the whole corpus. Never a verdict per document.
