# Reference — structure, Diataxis, information architecture & onboarding

Depth for `authoring-developer-guide` Step 4. Load when you need the method behind the structure + onboarding angles. The SKILL.md body carries the one-line method; this file carries the how.

## The grounding: two named models

- **Diataxis** — four documentation modes, each for a distinct reader need: **tutorial** (learning — a guided lesson, the reader does something under instruction), **how-to** (a task recipe for an already-competent reader), **explanation** (understanding — the "why", the mental model), **reference** (information — the complete factual listing). A developer guide composes all four; the dominant failure is **mode-bleed** (a reference dump in the getting-started tutorial, concepts smeared across recipes, the tutorial fused with the lookup recipes). Reference = the *linked* api-reference, not re-listed.
- **The developer-docs quality rubric** — the bar is an instance of six dimensions: **Findability, Accuracy, Relevance, Clarity, Completeness, Readability** (idratherbewriting's ~80-characteristic rubric) + the Good Docs Project. The current conditions instantiate it; the axis the old forge under-served is **Findability** (→ IA below).

## Information architecture — a signposted start-here + reader-journey order

"No clear start-here / endpoints with no context" is a top abandonment driver (52% of developers name poor docs their biggest obstacle). The findability method:

- **A signposted start-here.** The reader's entry is unmistakable; lead with what they can build + the path to a first success.
- **Reader-journey order.** orient → first success → concepts → recipes → tutorial → best-practices → troubleshooting → reference. (This is why concepts precede recipes — generalized to the whole guide order.)
- **Prominent key sections.** Auth + getting-started where a new reader hits them first.
- **Predictable cross-links.** Recipes link to the reference + to the concept they rely on; consistent labels.
- **Resource/goal grouping** for a broad surface (group by goal/functionality, not HTTP verb).

The reviewer judges the OUTCOME (a first-time reader can locate the start-here + their goal's section), never "add a nav" — and never double-counts a defect already caught by goal-organization or concepts-ordering.

## Scannability + progressive disclosure

- **Scannable** — a focused, shallow on-page ToC (avoid too many levels); descriptive headings a reader can skim; short paragraphs over walls of prose; lists where they aid.
- **Progressive disclosure** — the common/happy path first; edge configuration + exhaustive options deferred or linked ("see the reference for the full option set"). Reduces cognitive load. Proportional — a one-page CLI guide needs little of this.

## Light accessibility / readability (for the prose artifact)

WCAG-for-prose, the proportional subset (far lighter than a UI design system):
- **Meaningful link text** — never "click here" or sensory-only cues ("the blue button"); use the actual target/label.
- **Alt text** on any diagram/screenshot.
- **Acronyms + jargon defined on first use.**
- **Real heading hierarchy** (`#`/`##`, not bold-as-heading) — also aids scannability + screen-reader navigation.
- **Reasonable reading level** + inclusive language.

## Getting-started — the load-bearing first success

The whole section delivers ONE thing: a fast, verifiable first successful call. The 6-step shape:

1. **Prerequisites** — runtime/version, account, AND **where the credential comes from** (the signup-to-key / dashboard path — don't just say "set your key"; say where to get it).
2. **Install** — the one command per supported package manager / language.
3. **Configure credentials** — from an **env var / config, never hardcoded**.
4. **First call** — runnable, copy-pasteable, showing **real value** (a created resource / real response), not hello-world.
5. **Verify** — the **literal expected output**, so the reader KNOWS it worked.
6. Close with the **2–3 most common first-call failures + a one-line fix each** (deeper ones → the troubleshooting section).

- **Sandbox / test mode.** Steer the first call through the safe **test** path (test keys, often prefixed e.g. `test_`/`_sdbx`; separate endpoints/accounts) so the reader can't break anything. Proportional — a non-API CLI may have no key; then this collapses.
- **Time-to-first-call (TTFC) is the intent.** Minimize the steps to the first verified 200 (Stripe/Vercel set TTFC <90s; a first call within ~10 min → 3–4× conversion). The bar is *few steps to a verified first call*, not a stopwatch — a getting-started that needs 12 steps + three accounts before the first call fails the intent even if each step is runnable.

## Core concepts before recipes

Explain the mental model as Diataxis *explanation*, ahead of recipes, so parameters + recipes have MEANING: the client/resource object (create once, reuse), the domain nouns + relations, the request lifecycle (sync vs async, webhooks, idempotency conceptually — not the retry code yet, that's best-practices), and environments (test vs live). The dominant failure is concepts smuggled piecemeal into the recipes — a reader hits code before the model.

## Sources

Diataxis (diataxis.fr; Ubuntu/Canonical; idratherbewriting). Quality rubric (idratherbewriting "measuring documentation quality — a rubric for developer docs"; the Good Docs Project). IA/navigation/scannability (Fern; GitBook; idratherbewriting doc-navigation; LogRocket + IxDF progressive disclosure). Accessibility (document360 WCAG for docs; W3C WAI; WCAG 2.2 SC 1.1.1/2.4.4; Google for Developers tech-writing). TTFC + onboarding (Postman/TechCrunch/Nordic APIs "time to first call"; Stripe/Vercel <90s; sandbox sign-up: BILL/Paddle/Authorize.net/Amazon SP-API). Abandonment (Postman 52%; dev.to "your API isn't hard to use, your docs are"). External content (§5) — paraphrased, no URLs/commands lifted into actions.
</content>
