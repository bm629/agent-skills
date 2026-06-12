# jenkins-rest-ops

> Drive a Jenkins server's **Remote Access REST API** with `curl` — no SDK.
> Jenkins is **path-addressed**: append `api/json` to an object's URL to read
> it, POST to action paths to write. Auth is HTTP Basic `username:API_TOKEN`.
> The skill handles the two Jenkins-specific traps — a build trigger is
> **async** (it returns a queue item, so you poll `queue/item/<id>/api/json` to
> the build), and the **CSRF crumb** is exempt under API-token auth (fetched
> only as a 403 fallback). It consumes **caller-injected** credentials and
> never prints the token.

**Skill file:** [`skills/jenkins-rest-ops/SKILL.md`](../../skills/jenkins-rest-ops/SKILL.md)
**Version:** 1.0.0

## Purpose

Gives an agent the feasible Jenkins CORE CI/CD surface — trigger a build, poll
the queue item to a build, read build status + console log, list/inspect jobs,
plus CORE job CRUD (`createItem` via `config.xml`, copy, delete, enable/disable)
and build management (stop/delete). It stays inside the Jenkins API: committing a
`Jenkinsfile` to a repo or configuring an SCM webhook are `vcs` operations, out
of scope. It is the REST-direct sibling of `atlassian-rest-ops`, adapted to
Jenkins' path-addressed API + HTTP-Basic token auth.

## The no-official-OpenAPI grounding

Jenkins ships **no** official OpenAPI (JENKINS-35808). So the authoritative CORE
path table (`assets/endpoint-index.md`) is grounded on the official Remote Access
API docs, and the bundled `assets/swaggy-jenkins-openapi.json` is the community
**unofficial** description — a partial schema cross-check (it omits
`buildWithParameters`, `consoleText`, arbitrary build `api/json`, and models a
few ops oddly). `scripts/endpoint.py` resolves the swaggy-jenkins subset; the
index is the source of truth.

## When to activate

- ✅ Triggering a build and following it to a result; reading status / console log.
- ✅ Listing/inspecting jobs, queue, nodes, views.
- ✅ Job CRUD via the Jenkins API + build management (stop/delete a build).

Not for: committing a `Jenkinsfile` / configuring an SCM webhook (`vcs`),
plugin-contributed endpoints (vary per install), or credential setup.

## Workflow

1. **Receive the injected credentials** — `base_url` + `username` from context +
   the token by variable name; bridge into `base_url` / `username` / `JENKINS_TOKEN`.
   Auth is `curl -u "$username:$JENKINS_TOKEN"`.
2. **Find the path** — scan `assets/endpoint-index.md` (the CORE Remote Access paths).
3. **Construct the call** — GET `…/api/json` (use `?tree=` to shrink responses);
   POST to action paths. No crumb needed under token auth.
4. **For a build, follow the async flow** — `trigger-build.sh` → `poll-queue-item.sh`
   (to the executable) → `build-status.sh` / `console-log.sh`.

## Key gotchas

- **The async-build trap** — a build POST returns a **queue item**, not a build;
  poll `queue/item/<id>/api/json` to `.executable` first.
- **The crumb is a fallback** — API-token Basic auth is CSRF-crumb-exempt since
  Jenkins 2.96/2.107; fetch+attach a crumb only on a `403 No valid crumb`, and a
  `404` crumb-fetch means CSRF is off.
- **config.xml content-type** — `createItem` needs `Content-Type: application/xml`
  (`--data-binary @config.xml`).
- **Folder nesting** — `job/<folder>/job/<name>`, one `job/` per level.

## Credential contract

Pure consumer of caller-injected credentials: `base_url` + `username` from context,
the token by variable NAME (project `.env`-then-env-var, no scope-walk, no
`.service-accounts.yaml`, no `--account`). The token value is read only by the
`curl` subprocess, never printed. A "Standalone usage" appendix documents the
by-hand bridge.
