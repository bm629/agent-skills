# Synthesis lenses — the six corpus cuts + the seventh per-capability rollup

Load when running Procedure 4 (synthesis). The extract set (`extract/<repo_id>.md`
frontmatter + body) is the input; these lenses turn it into the report's conclusions.
Read all non-skipped extract YAML blocks (compact) to compute the aggregates; rank repos
by their refined 10-point score, read the top repos' full prose closely, skim the tail.

## The six lenses (cut ACROSS the corpus)

1. **Entity convergence.** For each recurring load-bearing abstraction, the share of
   extracted repos that carry it: **≥70% → load-bearing** (the corpus agrees this entity is
   core), **30–70% → common**, **<30% → niche**. High convergence is a strong signal to
   adopt the entity in the design.
2. **Architectural-pattern consensus.** A pattern adopted by **≥60%** of repos is
   *adopt-unless-overridden* — the default the design takes unless a stated reason beats it.
3. **Dependency consensus.** A dependency used by **5+ high-quality repos** is *trusted* —
   the corpus has de-risked it. Fewer than 5, or only in low-score repos, is not.
4. **Failure-mode aggregation.** A failure mode that appears in the most-commented issues of
   **multiple** repos is *systemic* — design for it upfront, not as an afterthought. A
   single-repo failure is anecdote, not signal.
5. **Borrow-vs-build matrix (per subsystem).** For each subsystem the system decomposes
   into: is there prior art worth borrowing (architecture / patterns), or is it built cold?
   This is the per-SUBSYSTEM view (how the system decomposes), distinct from the
   per-CAPABILITY rollup below.
6. **Gaps.** A capability or subsystem **no** repo handles well is either an innovation
   opportunity or a risk flag — name which, with the evidence.

## The seventh rollup — per-capability coverage

The six lenses cut across the corpus; none answers the question the build phase actually
asks, per capability: *do I assemble this from references, or design it cold?* So roll up,
for **every capability in the capability map**: candidates found, extractions produced,
verdicts returned, and one classification —

- **`borrow`** — real prior art exists with patterns worth taking.
- **`borrow-partial`** — implementations exist but are weak (low scores, `discard` verdicts,
  nothing borrowable); take what is there and build the rest.
- **`original`** — no prior art found.

### The evidenced-`original` rule (load-bearing)

Two very different situations produce identical-looking `original` data: a capability nobody
has built, and a capability *searched badly for* (wrong vocabulary, wrong sources, filed
under a name never guessed). Treating the second as the first means rebuilding from scratch
something that already exists — the exact failure this survey prevents.

The distinction is already in the data: the search wave records a coverage cell for every
(group × source), and zero-hit cells are MANDATORY — a recorded zero is evidence the search
ran. So **an `original` classification must carry its evidence**: how many angles ran for
that capability, how many terms, how many recorded zeros, and whether the vocabulary probe
found community terms. With that attached, "no prior art" is an evidenced finding; without
it, it is an absence that proves nothing.

**Phrase the claim precisely** — "no open-source prior art found across N angles and M
terms", never "this is novel". A well-run survey cannot see private or proprietary
implementations; overclaiming novelty is how a team commits to originality it did not verify.

## Handoff

Alongside the report, emit the **borrow-index** (`borrow-index.yaml`,
`schemas/borrow-index.schema.json`) — one entry per extracted (non-skipped) repo:
`{repo_id, url, brief, capability_tags, borrow_verdict, license, score}`. It records the
repo URL plus the signals extract already produced, so a later build phase can act on it
(re-clone from the URL, synthesize the patterns, license permitting) without re-deriving the
analysis. Validate it with `validate_prior_art.py synthesis <borrow-index.yaml>`.
