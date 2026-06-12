# netlify-ops

> Drive Netlify web-hosting **CLI-first** (the `netlify` CLI) with a **REST
> fallback** on Netlify's official OpenAPI — no SDK. The CLI is the ergonomic
> common path (create a site, deploy a directory, read status); the REST API is
> the comprehensive long tail (custom domains, fine-grained reads, DNS),
> grounded on a bundled spec via an endpoint index + a `$ref`-resolver. Auth is
> a Bearer PAT the CLI reads from `NETLIFY_AUTH_TOKEN` — it **never** runs
> `netlify login`. It consumes **caller-injected** credentials and never prints
> the token.

**Skill file:** [`skills/netlify-ops/SKILL.md`](../../skills/netlify-ops/SKILL.md)
**Version:** 1.0.0

## Purpose

Gives an agent the Netlify static/JAMstack + serverless surface — create-site,
deploy (draft or `--prod`), set + verify a custom domain, read deploy status,
and the adjacent sites/deploys/domains/DNS REST surface. It is the CLI-first
sibling of `github-cli-ops` and the OpenAPI-grounded sibling of
`atlassian-rest-ops`. Full-stack container/app hosting is out of scope.

## When to activate

- ✅ Creating a site, or deploying a build (draft/preview or `--prod`).
- ✅ Setting + verifying a custom domain, or configuring a site's DNS.
- ✅ Reading deploy status, or listing/inspecting sites/deploys.

Not for: full-stack container hosting, credential setup, or `netlify login`.

## Workflow

1. **Receive the injected credentials** — the token by variable name (Netlify has
   no non-secret record field beyond the token); bridge into `NETLIFY_AUTH_TOKEN`.
   Never `netlify login`.
2. **Pick the path** — CLI (`assets/cli-index.md`) for the common path; REST
   (`assets/endpoint-index.md` + `scripts/endpoint.py`) for the long tail.
3. **Run it** — the four scripts cover create-site / deploy / set-custom-domain /
   deploy-status.
4. **Handle the response** — deploys are async + multi-stage (poll the `state`);
   every REST response is checked for `success`, not just HTTP status.

## Key gotchas

- **Don't log in** — a missing/expired token is a hard caller error, not a cue to
  run `netlify login`.
- **`--no-build`, not `--build`** — the CLI builds by default.
- **Draft vs `--prod`** — omitting `--prod` is a draft/preview deploy.
- **The digest-deploy protocol** — a hand-rolled REST `createSiteDeploy` returns a
  `required` array of SHA1s you must then upload; the CLI handles this.
- **Rate limits** — 500 req/min general, deploys 3/min · 100/day.
- **Escape hatch** — `netlify api <operationId> --data '<json>'`; for body-carrying
  writes prefer the pure-REST `curl` (the escape-hatch body-key is unverified).

## Credential contract

Pure consumer of caller-injected credentials: only the token by variable NAME
(project `.env`-then-env-var, no scope-walk, no `.service-accounts.yaml`, no
`--account`, no login). The token value is read only by the CLI/`curl` subprocess,
never printed. A "Standalone usage" appendix documents the by-hand bridge.
