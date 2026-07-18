# The twelve conditions — expanded review checklist

The bar is single-sourced with the producer skill (`code-prior-art-survey`):
its dossier/Output section states these twelve conditions; the producer
produces TO them, this skill asserts them INDEPENDENTLY. Numbering and
headlines are fixed against the shared source — any change to the bar changes
that source first, then both skills, never one half alone. (Known nit: the
producer's Output bar currently truncates headline 10's trailing clause; the
shared source carries it, this file follows the shared source, and the
producer alignment is queued for its next version.)

Per condition: what to check, then the calibration — what IS a gap (revise,
naming this condition) vs what is NOT (approve-compatible; flagging it would
be a false-revise).

## Keyword map — conditions 1–6

### 1. Typed coverage — every in-scope capability has ≥1 group; all six types considered (an absent type is justified by scope, never silent)

Check: list the caller's in-scope capabilities (from the scope context) and
confirm each has at least one `type: capability` group; walk the six types
(`domain`, `capability`, `technique`, `ecosystem_anchor`, `community`,
`competitor`) and confirm each is either present or justified absent (the
map's convention: an `excluded` entry `"<type> (type absent)"` with a reason).

- IS a gap: an in-scope capability with no group; a type silently missing —
  no group AND no absence justification.
- NOT a gap: a type absent WITH a reasoned absence entry (e.g. no competitor
  products exist for a genuinely novel scope); one group covering two closely
  related capabilities when the scope context itself treats them as one.

### 2. Expansion quality — each group has 3–8 expansions mixing relation kinds, each with provenance; community vocabulary present via a probe receipt (or a reasoned degradation record)

Check: per group — expansion count within bounds (the validator enforces the
bounds; you judge the QUALITY), relation kinds mixed (an all-`synonym` or
all-`broader` set is a smell), provenance stamped and plausible; map-level —
`probe.performed: true` with sources + discoveries, or `performed: false`
with a reason; probe discoveries actually appearing as `probe-discovered`
expansions where they fit.

- IS a gap: expansions that are trivial restatements padding to the floor
  ("trading bot" / "bot for trading" / "a trading bot"); every group
  all-synonym; a probe claimed performed with empty discoveries AND no
  explanation; community jargon obviously missing (the scope's domain has a
  well-known folksonomy the map ignores and the probe was skipped without
  reason).
- NOT a gap: a competitor group whose expansions are all `related` product
  names (that is the natural shape for competitor groups); a reasoned
  `performed: false` probe with expansion quality carried by the other two
  provenances; thin-but-honest groups in a genuinely term-poor niche.

### 3. Disambiguation — negative terms present wherever the domain has known polysemy

Check: for each group whose canonical/expansions collide with unrelated
domains (judge from general knowledge: "trading" → cards/sports, "python" →
snakes, "swift" → the language vs the bird vs the payments network), confirm
`negative_terms` carry the disambiguators.

- IS a gap: a plainly polysemous canonical with empty negative terms (e.g.
  "trading" with nothing excluding card/sports senses).
- NOT a gap: empty negative terms on unambiguous technical terms
  ("backtesting", "OHLCV" — nothing to disambiguate); negatives absent for a
  collision so obscure no search would realistically hit it.

### 4. Scope honesty — excluded terms carry reasons; no group exceeds the caller's scope authority

Check: every `excluded` entry has a substantive reason; walk the groups
against the caller's scope context — no group drags the search into
capabilities/domains the scope does not contain.

- IS a gap: a group for a capability the scope never mentions (scope creep
  into the vocabulary); an excluded entry with a vacuous reason ("not
  needed"); a tempting broader term silently absent from BOTH groups and
  excluded (the guard's whole point is visibility).
- NOT a gap: adjacent-but-in-scope groups (the scope context, not your
  intuition, is the authority); a short exclusion list when the scope is
  naturally narrow.

### 5. Source contract — `sources.active` drawn from the registry; every skip reasoned

Check: the validator verifies ids exist in the registry (delegated); you
judge the JUDGMENT — are the skips' reasons substantive and consistent with
the scope (a conditional source skipped because its condition is false; a
plausibly-applicable source skipped with a real budget/overlap reason), and
is anything plausibly-applicable silently absent from both lists?

- IS a gap: a source whose registry condition plainly holds for this scope
  (e.g. an ML hub for an ML-capability scope) sitting in `skipped` with a
  reason that contradicts the scope — or absent from both lists; copy-paste
  reasons that don't fit ("not an android project" on a source skipped for
  budget).
- NOT a gap: aggressive-but-reasoned narrowing (a scoped dry run, an explicit
  budget decision); conditional sources absent when their condition plainly
  never applied.

### 6. Self-description — version/created_at/revision complete; a delta map names its baseline and inherited groups

Check: header fields present and coherent (the validator checks shape; you
check sense — a `revision: 3` map whose changes aren't explained anywhere,
a `created_at` in the future); delta maps: see the delta lens below.

- IS a gap: `mode: delta` with an empty `inherited_group_ids` AND a baseline
  that plainly shares groups (the inheritance is being hidden); incoherent
  self-description.
- NOT a gap: `request: null`/omitted (standalone callers have no request
  numbering); revision 1 with no changelog (there is nothing to log).

## Search output — conditions 7–11 (condition 11 applies to BOTH artifact types — see its section)

### 7. Coverage proven — every applicable (group × active source) cell present with exact queries + timestamp + count; zero-hits recorded

Check: DELEGATED — one run of the producer's validator (`search` subcommand
with `--keyword-map`) recomputes the owed cells from the map × the producer
package's registry and fails on any missing cell. Your added judgment: the
query strings look like real executed queries (engine-appropriate syntax,
the group's terms actually used), not summaries invented after the fact.

- IS a gap: validator FAIL lines (any); cells whose "queries" are vague
  narrative ("searched the usual places") rather than replayable strings.
- NOT a gap: many zero-hit cells (zeros are evidence of work — a thin domain
  yields them honestly); extra cells beyond the owed set.

### 8. Candidate integrity — canonical ids; copy flags honest; signals `as_of`-stamped; description (data) and relevance (judgment) both present

Check: ids follow `<host>__<owner>__<name>` (schema-checked; you spot-check
identity truth — the id matches the repo URL); `description` reads like the
repo's own words, `relevance` like the scout's scope-grounded judgment (not
two copies of the same sentence); flags plausible (a repo named `X-fork`
with `is_fork: false` deserves a spot-check); nulls honest (null signals
with a fresh `as_of` = "looked, couldn't resolve" — fine).

- IS a gap: relevance lines that are contentless ("relevant repo");
  descriptions fabricated (flowery marketing where the repo has none —
  spot-check 2-3 against the live repo when reachable); systematically
  missing flags on candidates from fork-happy channels.
- NOT a gap: null signals with honest `as_of`; a hub-native candidate whose
  id repeats the slug in the owner segment (that is the documented
  owner-less convention); modest candidate counts.

### 9. Boundary honesty — only the angle's channels; cross-angle leads in notes; no deep reads; no padding

Check: every coverage cell's source belongs to the output's angle (the
validator flags unknown sources; you catch KNOWN sources from OTHER angles
appearing as worked cells); candidates' found_by sources consistent with the
angle; no evidence of deep source-reading (relevance lines quoting file-level
internals a search couldn't see); candidate list not padded (near-duplicate
entries, obviously off-domain rows kept to inflate the count).

- IS a gap: worked cells on another angle's channels; relevance lines that
  required cloning/reading the repo; padding.
- NOT a gap: cross-angle LEADS recorded in notes (that is the contract);
  overlap with candidates another angle also found; a short list in a thin
  domain.

### 10. Failure transparency — unreachable sources/dead ends recorded with attempts; nothing silently narrowed

Check: compare the owed source set against what the cells + notes account
for — an unreachable source must appear in `notes.unreachable_sources` with
what was attempted; dead ends recorded; nothing just... missing (the
validator catches missing cells; you judge whether "unreachable" claims are
substantiated with attempts).

- IS a gap: an unreachable claim with no attempt described; a narrowing
  decision visible nowhere.
- NOT a gap: a genuinely down source recorded with its attempts (that IS the
  contract working); an empty unreachable list on a clean run.

### 11. Schema-valid — the deterministic validator exits 0 on the artifact

Applies to BOTH artifact types: the `search` subcommand for a search output
(also discharging condition 7) and the `keyword-map` subcommand for a keyword
map — a map is never approved without its validator run.

Check: DELEGATED — run the co-installed producer skill's
`validate_prior_art.py <kind> <artifact>` — with `--keyword-map <map>`
(required for `search`; not accepted for `keyword-map`) — and require
exit 0. (One run discharges both 7 and 11 for a search output; the
`keyword-map` subcommand discharges 11 for a map.) Never re-implement the
checks; never wave through FAIL lines as "cosmetic".

- IS a gap: any FAIL line.
- NOT a gap: nothing — exit 0 is binary.

## Judge-side rule — condition 12

### 12. Proportionality — a thin-but-honest result in a thin domain meets the bar; revise ONLY on a named gap against conditions 1–11

Apply to every prospective finding before it reaches the verdict: which
numbered condition does it violate, concretely? If you cannot name the
condition and the specific gap, it is not a finding. Yield is never a gap:
zero-hit-heavy coverage, short candidate lists, thin expansion sets in
term-poor niches are the HONEST shape of a thin domain — the bar judges the
search's craft (PRESS's spirit), not the domain's richness. Equally:
proportionality is not leniency — a real named gap in a thin domain is still
a gap.

## The delta lens (delta-mode keyword maps)

A map with `mode: delta` is judged as a SCOPED DELTA, not a fresh map:

1. Confirm `lineage.extends` names the baseline (the validator enforces
   non-null; you confirm it plausibly identifies a real predecessor) and
   `lineage.inherited_group_ids` lists what is deliberately not re-searched.
2. Judge conditions 1–6 against the NEW/CHANGED groups only, with condition
   1's capability coverage scoped to the delta's `scope_capabilities`
   (schema convention: an empty list means all-capabilities — then judge new
   groups against the full scope, with inherited groups still shielded by
   point 3).
3. Inherited groups are already-reviewed baseline material: do NOT
   re-litigate them, and do NOT count them as gaps ("group X looks thin") —
   a finding against an inherited group is a false-revise defect unless the
   delta itself modified that group.
4. IS a gap: a new capability in the delta scope with no new group; an
   inherited-groups list that hides changes (a "inherited" group whose
   content differs from any plausible baseline shape).
