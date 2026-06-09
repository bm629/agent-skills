# typescript-typecheck

> Set up and run TypeScript type-checking as a standalone quality gate —
> `tsc --noEmit` (or `tsc -b --noEmit`) run separately from the bundler, a
> genuinely strict `tsconfig`, and project references for a pnpm/Turborepo
> monorepo. Covers why a dedicated gate is mandatory (no bundler/transpiler
> type-checks — Vite/esbuild/SWC strip type annotations without checking them),
> the strict compiler-option set beyond `strict: true`, the Vite split-config
> layout, cross-package types via composite project references, the CI gate, and
> the `tsgo`/typescript-go status. The TS analog of a separate `ty` type-check
> gate. TypeScript 5.x.

**Skill file:** [`skills/typescript-typecheck/SKILL.md`](../../skills/typescript-typecheck/SKILL.md)
**Version:** 1.0.0

## Purpose

`tsc` is the only tool that actually checks TypeScript types — bundlers and
transpilers (Vite/esbuild, the SWC React plugin) transpile and strip types
*without* checking them, so `vite build` passes even on type errors. This skill
sets up the missing gate: a dedicated `tsc --noEmit` check, a genuinely strict
`tsconfig`, project references so cross-package types resolve, and a CI step that
fails on a type error the bundler ignored. It owns the type-check gate; the build
belongs to `vite`, the task pipeline to `turborepo`.

## When to activate

- ✅ Setting up TypeScript type-checking for a project (a `typecheck` script + CI step).
- ✅ Writing or tightening a `tsconfig.json` to be *genuinely* strict (not just `strict: true`).
- ✅ Configuring `moduleResolution: "bundler"` and its companion flags for a Vite/bundler app.
- ✅ Wiring project references (`composite`, `references`, `tsc -b`) so an app consumes a library/generated package's types.

### When NOT to activate

- Lint/format rules — that's a linter's job (`biome`); a linter has no type system.
- The production bundle/build output — that's the bundler (`vite`).
- The monorepo task pipeline/caching — that's `turborepo`; this only contributes the `typecheck` task.

## Workflow

| Step | Does |
|---|---|
| 1 Why separate | No transpiler type-checks (Vite/esbuild/SWC strip types) → a `tsc --noEmit` gate is **mandatory**, distinct from `vite build`. |
| 2 Strict tsconfig | `strict: true` + extras (`noUncheckedIndexedAccess`, `noImplicitOverride`, `verbatimModuleSyntax`, …) or `extends: "@tsconfig/strictest"`; bundler block (`moduleResolution: bundler`, `noEmit`). |
| 3 Vite split-config | solution `tsconfig.json` + `tsconfig.app.json` + `tsconfig.node.json`; a standalone `"typecheck": "tsc -b --noEmit"`. |
| 4 Project references | `composite` on the *referenced* package, `references` on the consumer, build/check with `tsc -b`; defer the pipeline to `turborepo`. |
| 5 CI gate | run the `typecheck` script on push/PR so a type error fails the build the bundler would have let through. |

## Hard rules it enforces

- **The `tsc` check is separate from the build** — never imply `vite build`/esbuild/SWC validates types.
- **`strict: true` is the floor, not the ceiling** — ship `noUncheckedIndexedAccess` at minimum, prefer a strictest base.
- **With project references, check via `tsc -b`** (build mode walks the graph), not bare `tsc`.
- **Don't trust a scaffold to be strict — verify it** (`composite` belongs only on a referenced package, never on a `noEmit` app leaf).

## Progressive disclosure (`references/`)

- `references/strict-tsconfig.md` — the full `strict` family, the recommended extra flags, the bundler module block, shareable bases, a worked strict `tsconfig.app.json`.
- `references/vite-split-config.md` — the three-file Vite TS layout, the `tsc -b && vite build` + `typecheck` scripts, `vite-plugin-checker`.
- `references/project-references.md` — composite/references/`tsc -b`/incremental semantics with a worked app→generated-client example, and `skipLibCheck`.
- `references/ci-gate.md` — the `tsc` CLI flags, the GitHub Actions gate shape, and the verified `tsgo`/typescript-go status.
- `references/sources.md` — research provenance.

## Limitations

- **TypeScript 5.x** — pinned to the 5.x line; confirm the exact current version when installing.
- **`tsgo`/typescript-go** (the native Go compiler slated for TS 7.0) is **preview-only, not production-ready** — keep `tsc` as the authoritative gate.
- **Owns the type-check gate, not the build or the pipeline** — `vite` builds, `turborepo` runs the cached task.

## License

MIT — part of the [`agent-skills`](https://github.com/bm629/agent-skills) collection.
