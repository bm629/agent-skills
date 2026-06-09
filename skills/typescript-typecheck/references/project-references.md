# Project references — cross-package type-checking in a monorepo

Load this when an app package needs to type-check against a library or generated package in a multi-package repo.

## The model

TypeScript project references let one tsconfig depend on another. When package A references package B:

- Importing from B resolves against B's **emitted `.d.ts`** (its declaration output), not B's `.ts` source.
- Build mode (`tsc -b`) builds referenced projects **in dependency order**, only rebuilding what is out of date.
- It is **incremental**: each project writes a `.tsbuildinfo` file recording the last build's project graph, so subsequent runs skip unchanged projects.

## `composite: true` — what it forces

A referenced project must set `composite: true`. That has consequences (verified against the project-references handbook):

- `declaration: true` becomes mandatory (emitting `.d.ts` is how the reference resolves types).
- Every implementation file must be matched by `include` or listed in `files` — `tsc` errors and tells you which file was missed if not.
- `rootDir` defaults to the directory containing the tsconfig if not set explicitly.

Also note: `tsc -b` behaves as if `noEmitOnError` is on for all projects, so a type error in a dependency stops the dependent from being built with stale output.

## Worked 2-package example: app → generated client

Layout:

```
packages/
  api-client/        # a generated package (e.g. an OpenAPI TS client)
    src/index.ts
    tsconfig.json
  app/               # the dashboard app, consumes the client
    src/main.ts
    tsconfig.json
```

`packages/api-client/tsconfig.json` (the referenced/library project):

```jsonc
{
  "compilerOptions": {
    "composite": true,           // required to be referenced
    "declaration": true,         // forced by composite, stated for clarity
    "declarationMap": true,      // lets editors jump to source across the boundary
    "outDir": "./dist",
    "rootDir": "./src",
    "module": "esnext",
    "moduleResolution": "bundler",
    "target": "ES2023",
    "skipLibCheck": true,
    "strict": true
  },
  "include": ["src"]
}
```

`packages/app/tsconfig.json` (the consumer — the *top* of the build, not itself referenced):

```jsonc
{
  "compilerOptions": {
    "noEmit": true,              // app is bundled by the bundler, not tsc
    "module": "esnext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx",
    "target": "ES2023",
    "lib": ["ES2023", "DOM", "DOM.Iterable"],
    "strict": true
  },
  "references": [{ "path": "../api-client" }],
  "include": ["src"]
}
```

> The consumer does **not** set `composite` — only a project that is *referenced by* another (here, `api-client`) must be `composite`. A project that merely *has* a `references` array (the build root) does not, and adding `composite` to a `noEmit` app would force a declaration emit it does not want. The rule: `composite` belongs on the dependency (`api-client`), not on the top-level consumer.

Then:

```sh
tsc -b packages/app   # builds api-client first, then type-checks app against its .d.ts
```

`tsc -b` walks the `references` graph, builds `api-client` (emitting its `.d.ts`), then checks `app` against those declarations. A type mismatch across the package boundary — e.g. the app passing the wrong shape to a generated client function — is caught here and nowhere else.

> Wire this `tsc -b` (or a `typecheck` script that runs it) into the monorepo task runner so it runs with the right dependency order and caching — use the `turborepo` skill for that pipeline. Do not duplicate the pipeline config here; this skill only provides the task.

## `skipLibCheck` and generated code

`skipLibCheck: true` skips type-checking of **all** `.d.ts` files — third-party `node_modules` declarations, conflicting lib types, and your own/generated emitted declarations.

- **Why it is commonly on:** speed, and silencing noisy or conflicting third-party/generated `.d.ts` that you don't own and can't fix.
- **What it trades away:** it will not catch an error *inside* a declaration file. If a generated client's emitted `.d.ts` is itself malformed or internally inconsistent, `skipLibCheck` lets it pass. The check still validates *your code's use* of those types — it just trusts the declarations themselves.
- **Nuance for generated clients:** keeping `skipLibCheck` on is usually right (you regenerate the client, you don't hand-edit its `.d.ts`), but know that a broken generated declaration won't be flagged by your type-check. The generator's own validity is your safety net there, not `tsc`.
