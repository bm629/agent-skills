# The `tsc` CLI, the CI gate, and the native compiler

Load this when adding a CI type-check step, or when asked about `tsc` flags or the native (Go) compiler.

## `tsc` CLI flags worth knowing

| Flag | Purpose |
|---|---|
| `tsc --noEmit` | Type-check only; emit no output files. The core "gate" invocation for a single project. |
| `tsc -b` / `tsc --build` | Build mode — honors the `references` graph, builds dependencies in order, incremental. Use this (not bare `tsc`) whenever project references are in play. |
| `tsc -p <path>` / `--project <path>` | Use the tsconfig at the given path or directory. |
| `tsc -w` / `--watch` | Re-check on file change (dev loop). |
| `tsc --incremental` | Persist project-graph info to `.tsbuildinfo` for faster subsequent runs (implied under `composite`/build mode). |
| `tsc --pretty` | Colorized, formatted diagnostics (on by default in a TTY). |

The standalone gate is `tsc --noEmit` (single project) or `tsc -b --noEmit` (references). Expose it as a `typecheck` npm script so CI and developers run the same command.

## The CI gate (GitHub Actions + pnpm)

Run the `typecheck` script on every push/PR so a type error fails the build the bundler would have let through. High-level shape:

```yaml
name: typecheck
on: [push, pull_request]
jobs:
  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: pnpm
      - run: pnpm install --frozen-lockfile
      - run: pnpm run typecheck      # or: pnpm turbo run typecheck
```

Notes:

- `actions/setup-node` with `cache: pnpm` caches the pnpm store; `pnpm/action-setup` installs pnpm itself. Pin action versions to your repo's policy.
- In a Turborepo monorepo, run the gate via the task runner (`turbo run typecheck`) so it respects task dependencies and remote/local caching — see the `turborepo` skill for the pipeline. This skill only contributes the `typecheck` task.
- Keep `typecheck` a **distinct CI step** from any build/bundle step. A build passing is not evidence the types are sound.

## The native compiler: `tsgo` / typescript-go (verified status)

Microsoft is building a native port of the TypeScript compiler and toolset in Go (the `microsoft/typescript-go` repository), informally "TypeScript native" and slated to underpin **TypeScript 7.0**. As of this skill's research date it is an explicit **preview / work-in-progress, not production-ready** — the repo states it is "still a work in progress and is not yet at full feature parity with TypeScript." You can try it via the `@typescript/native-preview` npm package, which provides a `tsgo` command used like `tsc`; core type-checking, declaration emit, and build mode / project references are reported "done", while watch mode is a non-incremental prototype, the language service is in progress, and the API is "not ready". **Do not adopt `tsgo` as your authoritative gate yet** — keep `tsc` (the regular TypeScript compiler) as the CI type-check; treat `tsgo` as an experiment to watch. Re-verify its status before relying on it, as it is moving quickly.
