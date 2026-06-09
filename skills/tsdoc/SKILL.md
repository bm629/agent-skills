---
name: tsdoc
description: >
  Use when writing or reviewing TSDoc doc-comments on a TypeScript codebase —
  the standardized /** ... */ comment grammar (Microsoft's @microsoft/tsdoc) that
  TypeDoc, API Extractor, and editors parse. Covers what to document (the
  exported/public surface: functions, classes, types, React components + props,
  hooks) versus what to skip (private/internal, generated code, trivial cases,
  prose that restates a type); the tag taxonomy categorized into block tags
  (@param, @returns, @remarks, @example, @defaultValue, @typeParam, @see,
  @throws, @deprecated), inline tags ({@link}, {@inheritDoc}, {@label}), and
  modifier tags (@public, @internal, @beta, @alpha, @readonly, @override); the
  summary-then-@remarks structure; and the key TSDoc-vs-JSDoc rule — do NOT
  repeat types in comments (the TS types already have them), document
  intent/behavior. Use when establishing a doc-comment convention, deciding
  what/how to document, or fixing JSDoc-style type annotations in TS.
  Enforcement is convention-only by default; eslint-plugin-tsdoc is an optional
  CI pointer. Not TypeDoc-site or Storybook setup (pointers only).

extensions:
  claude:
    when_to_use: "Writing/reviewing doc-comments on a TypeScript public API surface, or setting a doc-comment convention."
  copilot:
    applyTo: "**/*.{ts,tsx}"
  cursor:
    globs: ["**/*.ts", "**/*.tsx"]
  gemini: {}
  codex: {}

version: "1.0.0"

forge:
  status: reviewed
  forged: 2026-06-09
  reviewed: 2026-06-09
---

# `tsdoc` — SKILL.md

> **Variant:** standard · **When to use:** the skill is invoked, applied to a TypeScript file or surface, and returns documented code / a convention decision; control passes back to the caller.

## Overview

TSDoc is Microsoft's standardized grammar for TypeScript doc-comments — the `/** ... */` block immediately preceding a declaration. The standard fixes a tag set and a parser (`@microsoft/tsdoc`) so independent tools — TypeDoc, API Extractor, editor IntelliSense — all agree on how a comment is structured. This skill is the convention for **writing** those comments: which symbols deserve a doc-comment, which TSDoc tags to use and how, and the single rule that separates TSDoc from legacy JSDoc — **you do not repeat types in the comment**, because the TypeScript type already carries them; the comment documents *intent and behavior*. It is the TypeScript analog of a public-surface docstring discipline (e.g. Python's Google-style docstrings checked by a docstring linter): document the exported API surface, skip the noise.

## When to activate

- ✅ Writing doc-comments on exported/public TypeScript symbols — functions, classes, types/interfaces, React components and their props, custom hooks.
- ✅ Establishing or codifying a doc-comment convention for a TS codebase.
- ✅ Deciding *what* to document and *how* (which tags) for a given symbol.
- ✅ Reviewing/fixing existing comments — e.g. removing JSDoc-style `{type}` annotations that duplicate the TS types, or correcting `@return` → `@returns`.

**Do NOT activate when:**

- Setting up a generated documentation **site** — that is TypeDoc; this skill only points at it (see Gotchas).
- Building a component catalog / interactive docs — that is Storybook; out of scope (pointer only).
- Linting or formatting general code style — that is the project's linter/formatter (e.g. Biome); it does **not** validate doc-comment content.
- Annotating types in plain JavaScript with no type system — that is JSDoc-as-types, a different practice this skill explicitly rejects for TS.

## Workflow

### Step 1: Decide whether the symbol gets a doc-comment

Document the **public/exported API surface** a consumer of the module reaches for. Skip the rest. The judgment, not a tag list, is the high-value part.

**Document:**

- Exported functions, classes, and methods whose behavior is not fully obvious from the name + signature.
- Exported types and interfaces — especially a React component's **props interface** (each non-obvious field gets a one-line description).
- Exported React **components** and custom **hooks** — what it renders / returns, and any non-obvious parameter or option.

**Skip (do not document):**

- Private/internal symbols not part of the consumed surface. Mark a symbol that is exported for tooling but not for third parties with the `@internal` modifier rather than documenting it as public.
- **Machine-generated code** — e.g. an OpenAPI/`openapi-ts` client, codegen output. Generated comments (or their absence) are owned by the generator; do not hand-author over them.
- Trivial, self-evident one-liners where name + types already say everything (`isEnabled: boolean`, a pass-through getter).
- Prose that merely **restates the type** (see Step 3 — the cardinal rule).

### Step 2: Write the summary, then add detail in `@remarks`

The first paragraph — everything before the first block tag — is the **summary**. Keep it brief: doc sites show it in API index listings. Start with a concise sentence describing what the symbol does.

Put longer discussion (caveats, design notes, context, links to related APIs) in a **`@remarks`** block. `@remarks` ends the summary and begins the detailed section; it should not restate the summary.

```ts
/**
 * Returns the arithmetic mean of two numbers.
 *
 * @remarks
 * Both inputs are treated as finite; passing `NaN` propagates `NaN`.
 * For a list of values, use {@link average} instead.
 *
 * @param x - The first input number
 * @param y - The second input number
 * @returns The arithmetic mean of `x` and `y`
 *
 * @example
 * Basic usage:
 *
 *     mean(2, 4); // 3
 */
export function mean(x: number, y: number): number {
  return (x + y) / 2;
}
```

### Step 3: Document intent, never the type (TSDoc vs JSDoc)

The cardinal rule. JSDoc historically annotated **types** inside comments because plain JavaScript had none (`@param {string} name`). TypeScript already declares the types in the code, so **TSDoc tags carry no `{type}`** — a TSDoc `@param` is `@param name - description`, full stop. Document *why/how/what-it-means*, not *what type it is*.

```ts
// ANTI-PATTERN — JSDoc-style type annotation, redundant with the TS signature
/**
 * @param {string} userId  the user id
 * @param {number} limit   the limit
 * @returns {Promise<User[]>}
 */

// CORRECT — TSDoc: hyphen syntax, no types, documents intent
/**
 * Fetches the most recent users created by `userId`'s organization.
 *
 * @param userId - Owner whose organization is queried
 * @param limit - Maximum rows to return; the server caps this at 100
 * @returns The users, newest first
 */
export async function recentUsers(userId: string, limit: number): Promise<User[]> { /* ... */ }
```

Note the `@param name - description` **hyphen** is required by the spec; omitting it is flagged by the TSDoc parser.

### Step 4: Reach for the right tag

Use the categorized taxonomy in [`references/tag-taxonomy.md`](references/tag-taxonomy.md) (block / inline / modifier — load it when you need the full per-tag detail). The everyday subset:

- **`@param name - desc`**, **`@returns desc`** — function inputs/output, where non-obvious.
- **`@typeParam T - desc`** — a generic type parameter (same hyphen syntax as `@param`).
- **`@remarks`** — detailed discussion beyond the summary.
- **`@example`** — a usage snippet; its first line is treated as the example's title.
- **`@defaultValue`** — the default for a class/interface field or property.
- **`@throws`** — one block per exception type the caller should know about.
- **`@see`** — a cross-reference; **`@deprecated <message>`** — mark removal + name the replacement.
- **`{@link Target | label}`**, **`{@inheritDoc}`** — inline cross-reference / inherit a base member's docs.
- **`@public` / `@internal` / `@beta` / `@alpha`** — release-stage modifiers controlling what a public release exposes.

### Step 5: Enforcement — convention-only by default

A linter/formatter that lints code (e.g. **Biome**) does **not** validate doc-comment *content* — it has no TSDoc-conformance rule. So the default is **convention-only**: this skill is the standard; no extra tooling, no second linter.

If a project wants CI to mechanically validate TSDoc syntax, the official tool is **`eslint-plugin-tsdoc`** (single rule `tsdoc/syntax`). See [`references/enforcement.md`](references/enforcement.md) for the config snippet and the explicit trade-off — **it requires ESLint, so adopting it reintroduces ESLint alongside an existing fast linter**, the two-linter situation a single-linter setup was chosen to avoid. Treat it as an opt-in CI pointer, not the default.

## Rules

**Hard rules (never violate):**

- **No types in comments.** TSDoc tags never carry a `{type}`. The TS signature is the source of truth for types; the comment is for intent/behavior. Never recommend or write JSDoc-style `{type}` annotations in a `.ts`/`.tsx` file.
- **Document the public surface, skip the rest.** Exported/consumed symbols get comments where behavior is non-obvious. Private/internal symbols, generated code, and trivial self-evident cases get **none**.
- **Categorize tags correctly.** Block tags introduce a section (first thing on their line); modifier tags are standalone flags with no content; inline tags are `{@...}` within text. Do not invent non-standard tags — the parser warns on unrecognized ones.
- **`@param`/`@typeParam` use the hyphen:** `@param name - description`. `@returns` (not `@return`).
- **Summary stays brief; detail goes in `@remarks`.** Don't dump everything into the summary paragraph.

**Preferences (override-able):**

- Default to **convention-only** enforcement; add `eslint-plugin-tsdoc` only when CI syntax-validation is explicitly wanted and the second-linter cost is accepted.
- Prefer documenting a non-obvious **behavior/edge case** over restating an obvious signature.
- Use `{@link}` to connect related APIs rather than repeating their descriptions.

## Gotchas

- **A code linter/formatter does not check doc comments.** Tools like Biome lint/format code; the closest they touch doc-comments is an asterisk-formatting rule (`useSingleJsDocAsterisk`) and tracking `{@link}` references for unused-imports — neither validates TSDoc *conformance*. Don't assume "lint passed" means the doc-comments are correct; that is a convention-or-`eslint-plugin-tsdoc` concern.
- **`@deprecated` is a *block* tag, not a modifier.** Per the spec it takes a trailing sentence naming the recommended alternative (`@deprecated Use {@link newFn} instead.`) — it is not a content-less flag like `@internal`. Categorizing it as a modifier is a common error.
- **`@return` vs `@returns`.** TSDoc standardizes on **`@returns`**. `@return` is a frequent JSDoc-muscle-memory slip the parser flags.
- **Forgetting the `@param` hyphen.** `@param x The value` is malformed; it must be `@param x - The value`. The TSDoc parser emits a hyphen warning.
- **`{@inheritDoc}` excludes a summary and `@remarks`.** When a comment uses `{@inheritDoc}`, it must not also declare its own summary or `@remarks` section — those are inherited.
- **`@override` vs the TS keyword.** Prefer TypeScript's `override` keyword in source; reserve the `@override` modifier tag for when docs are generated from `.d.ts` declaration files.
- **TypeDoc is a consumer, not a writer.** TSDoc comments are the **input** TypeDoc reads to generate an API site. Generating that site is a separate, out-of-scope concern — this skill only writes the comments TypeDoc would later consume. Don't pull TypeDoc setup into a doc-comment task.

## Anti-patterns

- **"TypeScript has the type, but I'll restate it in prose for clarity."** No — `@param userId - The user ID string` restates the type and adds nothing. Document why/how, or omit the tag.
- **"Every symbol should have a doc-comment for completeness."** No — documenting trivial getters, obvious params, and self-evident one-liners is noise that hides the comments that matter.
- **"Let me improve the comments on the generated client too."** No — machine-generated code is owned by its generator; hand-edits get overwritten and shouldn't be the place you spend doc effort.
- **"I'll add `eslint-plugin-tsdoc` to be safe."** Not by default — it drags ESLint back into a project that uses a single fast linter. Convention-only is the default; adopt the plugin only on an explicit decision that accepts the second linter.
- **"I'll invent an `@usage` / `@note` tag."** No — non-standard tags trigger parser warnings and break tool interop. Use the standard set (`@remarks`, `@example`, `@see`).

## Output

A TypeScript public surface carrying correct, conformant TSDoc doc-comments — summaries plus `@param`/`@returns`/`@remarks`/`@example` (and modifiers/inline tags) where warranted — with private/internal/generated/trivial symbols left undocumented, and **no** type-restating prose. Alternatively, a stated doc-comment **convention decision** (the discipline above + the convention-only-vs-`eslint-plugin-tsdoc` enforcement choice). The consumer is the next reviewer or the calling workflow; the comments also feed editor IntelliSense and (if a project later adds it) a TypeDoc site.

## Related

- `references/tag-taxonomy.md` — the full block/inline/modifier tag tables (load when you need a tag beyond the everyday subset).
- `references/enforcement.md` — `eslint-plugin-tsdoc` config snippet + the second-linter trade-off; the TypeDoc/Storybook pointers.
- `references/sources.md` — research provenance.
- A JS/TS linter+formatter skill (e.g. a Biome skill) — the code-quality gate that does **not** validate doc-comment content; this skill is the complementary doc-comment convention.
- A TypeScript type-checking skill — types are self-documenting, which is *why* this skill says don't restate them in prose.

## Progressive disclosure

- `references/tag-taxonomy.md` — block / inline / modifier tag reference with per-tag categorization and syntax. **Load when** writing a tag outside the everyday subset, or verifying a tag's category.
- `references/enforcement.md` — the `eslint-plugin-tsdoc` config + trade-off, and the TypeDoc / Storybook out-of-scope pointers. **Load when** deciding enforcement tooling or asked about doc-site generation.
- `references/sources.md` — citations. **Load when** auditing provenance.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap).
- Body ≤ ~500 lines / 5,000 tokens — kept in context every turn.
- Per reference file: warn >10k tokens, error >25k. Total references: warn >25k tokens, error >50k.
