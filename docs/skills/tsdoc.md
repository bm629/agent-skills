# tsdoc

> Write TSDoc doc-comments on a TypeScript public surface — Microsoft's
> standardized `/** ... */` grammar (`@microsoft/tsdoc`) that TypeDoc, API
> Extractor, and editors parse. Covers what to document (exported functions,
> classes, types, React components + props, hooks) versus what to skip
> (private/internal, generated code, trivial cases, prose that restates a type);
> the tag taxonomy (block / inline / modifier); the summary-then-`@remarks`
> structure; and the cardinal TSDoc-vs-JSDoc rule — never repeat types in
> comments (the TS signature already has them). Enforcement convention-only by
> default (`eslint-plugin-tsdoc` an optional CI pointer). TypeDoc-site and
> Storybook are pointers only. The TS analog of a public-surface docstring
> discipline.

**Skill file:** [`skills/tsdoc/SKILL.md`](../../skills/tsdoc/SKILL.md)
**Version:** 1.0.0

## Purpose

A code linter/formatter (e.g. Biome) lints code but does **not** validate
doc-comment content, and TS already carries the types — so TSDoc's value is a
*convention*: which symbols deserve a doc-comment, which tags to use, and the one
rule that separates TSDoc from legacy JSDoc — **no `{type}` in the comment**, the
comment documents intent/behavior. This skill is that convention (the TS analog
of a Python Google-style docstring discipline): document the exported surface,
skip the noise.

## When to activate

- ✅ Writing doc-comments on exported/public TS symbols — functions, classes, types, React components + props, hooks.
- ✅ Establishing or codifying a doc-comment convention for a TS codebase.
- ✅ Deciding *what* to document and *how* (which tags) for a symbol.
- ✅ Reviewing/fixing comments — removing JSDoc-style `{type}` annotations, correcting `@return` → `@returns`.

### When NOT to activate

- Setting up a generated documentation **site** — that's TypeDoc (pointer only).
- Building a component catalog — that's Storybook (out of scope, pointer only).
- Linting/formatting code style — that's the linter (`biome`); it does not validate doc-comment content.
- Annotating types in plain JS — that's JSDoc-as-types, a different practice this skill rejects for TS.

## Workflow

| Step | Does |
|---|---|
| 1 Decide if it gets a comment | Document the public/exported surface; **skip** private/internal, generated code, trivial self-evident cases, type-restating prose. |
| 2 Summary then `@remarks` | A brief first-paragraph summary (shown in API indexes); longer detail goes in `@remarks`. |
| 3 Intent, not type | TSDoc tags carry **no `{type}`** — `@param name - description` (hyphen required); document why/how, not the type. |
| 4 Reach for the right tag | The everyday subset (`@param`/`@returns`/`@typeParam`/`@remarks`/`@example`/`@throws`/`@deprecated`/`{@link}`) + the categorized taxonomy. |
| 5 Enforcement | Convention-only by default; `eslint-plugin-tsdoc` (`tsdoc/syntax`) is an opt-in CI pointer **with** the second-linter trade-off. |

## Hard rules it enforces

- **No types in comments** — TSDoc tags never carry a `{type}`; never write JSDoc-style `{type}` in a `.ts`/`.tsx` file.
- **Document the public surface, skip the rest** — private/internal, generated code, and trivial cases get none.
- **Categorize tags correctly** (block / inline / modifier); don't invent non-standard tags (the parser warns).
- **`@param name - description`** (hyphen required); **`@returns`**, not `@return`.

## Progressive disclosure (`references/`)

- `references/tag-taxonomy.md` — the full block / inline / modifier tag tables with per-tag categorization and syntax.
- `references/enforcement.md` — the `eslint-plugin-tsdoc` config snippet + the second-linter trade-off, and the TypeDoc/Storybook out-of-scope pointers.
- `references/sources.md` — research provenance.

## Limitations

- **Convention-only by default** — `eslint-plugin-tsdoc` reintroduces ESLint alongside an existing fast linter; adopt only on an explicit decision.
- **TypeDoc-site generation and Storybook are pointers only** (out of scope) — this skill writes the comments TypeDoc would later consume.
- **A code linter does not validate doc-comment content** — conformance is a convention-or-`eslint-plugin-tsdoc` concern.

## License

MIT — part of the [`agent-skills`](https://github.com/bm629/agent-skills) collection.
