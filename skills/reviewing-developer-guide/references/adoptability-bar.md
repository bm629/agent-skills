# The adoptability + accuracy bar — 14 conditions (single source)

The single-sourced bar for the developer-guide pair. `authoring-developer-guide` produces to it (its Step-5 self-check, 1:1); `reviewing-developer-guide` judges against it. One bar, no drift. Each condition: the **pass** signal, the **gap** signal, and the **proportionality collapse** (when a thin tool legitimately omits it). Non-collapsing baselines that bind at any size: cond-2 (verify + env-var), cond-9 (no fabrication / upstream-accuracy), cond-7 (mode separation), cond-8 (link-not-duplicate where a catalog exists), cond-11 (no fabrication).

| # | Condition | Pass | Gap | Collapse (thin tool) |
|---|---|---|---|---|
| 1 | Goal-organized | framed by what the developer can build; recipes named by goal | an endpoint dump, no adoption narrative | always holds (a hard framing rule) |
| 2 | Verifiable first success | prereq (+ where the credential comes from + test/sandbox) → install → env-var creds → one real call → **verify** with expected output; short + unblocked (TTFC intent) | no verify step, not runnable, hardcoded creds, or a needlessly long/blocked path | binds at any size (verify + env-var are non-negotiable); a no-key CLI collapses the credential step |
| 3 | Concepts before recipes | the mental model (client, nouns, lifecycle, environments) precedes the recipes | concepts absent or buried after/inside the recipes | light concepts on a thin tool, but still before recipes |
| 4 | How-tos cover the handed-in scenarios | one goal-named runnable recipe per common scenario; links out | a handed-in scenario has no recipe (coverage hole) | few recipes for a thin surface |
| 5 | End-to-end tutorial, kept separate | one guided build start→finish, separate from the lookup recipes | no end-to-end build, or tutorial fused with recipes | a tiny tool's tutorial is short; still separate |
| 6 | Best-practices grounded | auth/secrets, retryable-vs-fatal errors, retries+idempotency+backoff, pagination, rate-limits, webhooks (if any), resource hygiene — pattern + snippet | absent, or a bare option list with no recommendation | small tool → light surface; webhooks collapse if none |
| 7 | Diataxis modes typed + separated | each piece in its mode; no bleed | reference dumped in the tutorial; concepts smeared in recipes; tutorial fused with recipes | always |
| 8 | Links into, never duplicates, the api-reference | the catalog is pointed to as the source of truth | the catalog re-listed inline (a drifting copy) | non-API tool → no catalog to link (note as assumption) |
| 9 | Samples runnable + accurate to the CURRENT tool | every sample a real capability/endpoint from the handed-in upstreams; env-var creds; targeted tool version stated | a sample calls something absent from the upstreams (fabrication) | binds at any size; no tool-version oracle beyond the upstream (freshness teeth are cond-12) |
| 10 | Tool versioning + migration stated | scheme, deprecation policy/timelines, changelog link, per-major before/after | a versioned tool ships none | unversioned/no-major-yet tool collapses it |
| 11 | Grounded, not fabricated | gaps surfaced as explicit assumptions | a missing answer fabricated to look complete | always |
| 12 | Delta-scoped amend (amend-mode only) | the delta meets the bar on touched blocks; the staleness sweep is complete (no removed/renamed-capability sample); internal coherence holds; guide-version bumped + changelog row; superseded marked | a stale sample survives; no change history; superseded silently deleted | **n/a on a greenfield first build** (no change request handed in) |
| 13 | Troubleshooting / common-errors path | a self-serve symptom→cause→fix path for the frequent knowable errors | a frequent knowable error has no resolution path in the guide | a thin tool folds it into getting-started — not a gap |
| 14 | Findable — signposted start-here + reader-journey order | a first-time reader can locate the start-here + their goal's section without knowing the API | no orientation / no start-here so a new reader can't begin | a one-page guide is trivially findable — not a gap |

## The three named checks

- **Upstream-accuracy (cond-9).** Spot-check every load-bearing sample/step against the handed-in feature-spec/api-reference. An invented capability/endpoint is the highest-impact defect. A not-handed-in upstream is an assumption, never a revise.
- **Api-reference-linking (cond-8).** Point into the catalog; never re-list it inline.
- **Amend staleness-sweep (cond-12, amend-mode only).** After a tool change, no guide location may still reference a removed/renamed capability. A surviving stale sample is the dominant amend defect.

## cond-14 overlap guard (load-bearing)

cond-14 is **navigation/findability** — distinct from cond-1 (goal-*organization*) and cond-3 (concepts-*ordering*). Fail cond-14 ONLY when the orientation/start-here itself is missing or unfollowable. Do NOT raise cond-14 for an endpoint-dump (that is cond-1) or concepts-after-recipes (that is cond-3) — never double-penalize one defect across cond-1/3/14.

## Worked findings

- **revise** — Upstream-accuracy (cond-9), "Send a message" recipe: calls `client.messages.schedule(at=...)`, but the api-reference has no scheduling endpoint. Fix: use a real capability, or surface scheduling as an open-question.
- **revise** — Amend staleness-sweep (cond-12): bumped to SDK v3 but "Refund a charge" still calls `Client(key=...)` (removed in v3). Fix: sweep all samples to `Client.from_env()`; mark the v2 form superseded.
- **revise** — Api-reference-linking (cond-8): the "Reference" appendix re-lists all 40 endpoints with parameter tables. Fix: replace with a pointer to the api-reference; keep only the endpoints the recipes use.
- **approve (thin tool)** — a one-command CLI guide: one recipe, light concepts, troubleshooting folded into getting-started, no migration matrix, single-page (trivially findable). Every applicable condition holds; cond-12/10/13-dedicated/14-nav legitimately collapse. Do NOT manufacture a gap from brevity.

## Source

This bar is the developer-guide pair's adoptability + accuracy bar, single-sourced with `authoring-developer-guide`'s Step-5 self-check. Provenance for the underlying practice is in `references/sources.md`.
</content>
