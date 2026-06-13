---
# ─── UNIVERSAL CORE ──────────────────────────────────────────────────────
name: jenkins-rest-ops
description: >
  Use when driving a Jenkins server's REST (Remote Access) API directly with
  curl (no SDK) — triggering a build, polling the queue item to a build,
  reading build status + console log, listing/inspecting jobs, job CRUD
  (createItem/copy/delete/enable/disable via config.xml), and build
  management (stop/delete). Jenkins is path-addressed REST authenticated with
  HTTP Basic username:API_TOKEN. A build trigger is ASYNC — it returns a queue
  item, not a build, so you poll queue/item/<id>/api/json to the executable.
  API-token auth is exempt from the CSRF crumb (Jenkins 2.96/2.107+); a crumb
  is only a 403 fallback. No official Jenkins OpenAPI exists, so the CORE path
  table is grounded on the official Remote Access docs (the bundled
  swaggy-jenkins spec is an unofficial cross-check). Consumes caller-injected
  credentials (base_url + username + a token resolved by variable name) — it
  does not provision or resolve them; the token value is read only by curl,
  never printed.

# ─── PROVIDER-SPECIFIC EXTENSIONS ────────────────────────────────────────
extensions:
  claude:
    allowed-tools: [Read, Write, Edit, Grep, Glob, Bash]
    user-invocable: true
    when_to_use: "performing a Jenkins CI/CD operation directly via the Remote Access REST API"
    argument-hint: "<operation, e.g. 'trigger a build of job X and read its result'>"
  copilot: {}
  cursor:
    alwaysApply: false
    globs: []
  gemini: {}
  codex: {}

version: "1.0.0"

forge:
  status: reviewed
  forged: 2026-06-12
  reviewed: 2026-06-13
---

# jenkins-rest-ops

## Overview

This skill lets an agent perform Jenkins CI/CD operations by calling the **Remote Access REST API directly with `curl`** — no SDK, no `pip` dependency. Jenkins is **path-addressed**: append `api/json` to almost any object's URL to read it, POST to action paths to write. The agent consumes the credentials the caller injected, finds a CORE path in a bundled index, constructs the `curl`, and parses the JSON. It covers the feasible CORE surface — trigger/poll/status/console/list plus job CRUD and build management — and deliberately stays inside the Jenkins API (it does not commit a `Jenkinsfile` to a repo or configure SCM webhooks; those are `vcs` operations). Jenkins ships no official OpenAPI, so the CORE paths are grounded on the official Remote Access docs.

## When to activate

- ✅ Triggering a build (`build` / `buildWithParameters`) and following it to a result.
- ✅ Reading build **status** (`result` / `building` / `duration`) or the **console log**.
- ✅ Listing / inspecting **jobs**, queue, nodes, views.
- ✅ **Job CRUD** via the Jenkins API — create (`createItem` + `config.xml`), copy, delete, enable/disable — and build management (stop/delete a build).

**Do NOT activate when:**

- You need to **commit a `Jenkinsfile` / pipeline config into a repo**, or configure an SCM webhook that points a repo at Jenkins — those are `vcs` operations (a GitHub/GitLab/Bitbucket ops skill), **not** Jenkins-API operations. (Creating a Jenkins *job* via `createItem` is in scope; committing pipeline source to the repo is not.)
- You only need credential setup — credentials are provided by the caller; this skill does not provision or resolve them (see `references/credentials.md`).
- The operation depends on a **plugin-contributed endpoint** — the CORE API is plugin-independent; plugin endpoints vary per install and are out of the guaranteed surface.

## Workflow

### Step 1 — Receive the injected credentials

The caller has already resolved the account and injected what this operation needs — **consume** it; do **not** look for a record yourself. You receive from context:

- **`base_url`**, **`username`**, and the **capability** (`cicd`) — as context values, not read from a file.
- **The token, by an ordered load rule** the context carries the **variable NAME** for: the project-level **`.env` value if that file exists** and defines the var, **else** the **environment variable** of that name (project `.env` first). The token **value** is never in context prose — only its variable name; `curl` reads the value from the environment. Perform **no** scope resolution or directory walk to find the `.env`, and it is project `.env`, not `.envrc`.

Bridge into the scripts' fixed vars `base_url` / `username` / `JENKINS_TOKEN`. Auth is HTTP Basic: `curl -u "$username:$JENKINS_TOKEN"`. Full contract: [`references/credentials.md`](references/credentials.md).

### Step 2 — Find the path

Scan [`assets/endpoint-index.md`](assets/) — the authoritative CORE path table grounded on the official Remote Access docs. Jenkins is path-addressed, so paths are templates (`job/<name>/build`) that serve every job. For the subset the bundled (unofficial) `swaggy-jenkins` spec also describes, `python3 scripts/endpoint.py <operationId>` prints its request/response schema as a cross-check (see [`references/patterns.md`](references/patterns.md) for why it is only a cross-check).

### Step 3 — Construct + run the `curl`

Apply the patterns from [`references/patterns.md`](references/patterns.md):

- **Auth:** `-u "$username:$JENKINS_TOKEN"` on every call.
- **Reads:** GET `<base_url>/<path>/api/json`; use `?tree=field[sub]` to keep responses small. Pass `curl -g` (`--globoff`) whenever the `?tree=` has `[brackets]` — they are curl glob metacharacters and abort the request with "bad range" (curl error 3) otherwise.
- **Writes:** POST. With token auth no crumb is needed (token is CSRF-exempt). Only on a `403 No valid crumb` add `-H "$(bash scripts/crumb.sh)"`.
- **Folders:** repeat `job/` per nesting level; URL-encode job names.

The bundled `scripts/*.sh` (`trigger-build`, `poll-queue-item`, `build-status`, `console-log`, `list-jobs`, `crumb`) are worked examples.

### Step 4 — For a build, follow the async flow

A build trigger is **asynchronous** — it returns a **queue item**, not a build:

1. `trigger-build.sh <job> [K=V …]` → prints the queue-item URL (the `Location` header).
2. `poll-queue-item.sh <queue-item-url>` → polls until the build starts, prints the build URL + number.
3. `build-status.sh <job> [<n>]` for `result`/`building`, `console-log.sh <job> [<n>]` for the log.

Never read a build number before the queue item resolves — the build may still be queued.

### Step 5 — Handle the response

- **Reads** return JSON (`result` is `null` while `building` is true). Use `?tree=` to avoid huge payloads; `?depth=N` inflates fast.
- **Errors:** a `403 No valid crumb` on a POST means add a crumb (Step 3); a `404` on `crumbIssuer` means CSRF is off (no crumb needed); a `401`/`403` otherwise means a bad/again token or insufficient permission.

## Rules

**Hard rules (never violate):**

- **No SDK, no `pip`.** API calls use `curl`; the only helper is `scripts/endpoint.py` (`python3` **stdlib** only).
- **Never read or print the token value.** Reference it only as `$JENKINS_TOKEN` in a `curl -u` argument; the subprocess reads it from the environment. The token lives only in `.env` (gitignored) or the environment.
- **A build trigger returns a queue item, not a build.** Always poll `queue/item/<id>/api/json` to the executable before reading build status.
- **Token auth is crumb-exempt.** Do not blindly fetch/attach a crumb on every POST; attach one only as a fallback on a `403 No valid crumb`.
- **Ground on the CORE index, not swaggy-jenkins.** Use `assets/endpoint-index.md` (official-grounded) for paths; the bundled `swaggy-jenkins` spec is an unofficial, partial cross-check — never the source of truth.
- **Stay in the Jenkins API.** Don't commit a `Jenkinsfile` or configure an SCM webhook — those are `vcs` ops.
- **This skill never writes credentials.** Credentials are provided by the caller.

**Preferences (override-able):**

- Prefer `?tree=` field selection over `?depth=N` to keep responses small.
- Prefer the per-user **API token** over the login password (the official docs discourage the password).
- Use `consoleText` for a finished build; `logText/progressiveText?start=<offset>` to stream a running one.

## Gotchas

- **The async-build trap.** A build POST returns `201` + a `Location:` queue item — NOT a build number. Reading `job/<name>/lastBuild` immediately can return a *previous* build. Poll the queue item to `.executable` first.
- **Queue-item ephemerality.** The queue item is valid only ~5 min after the build ends — poll promptly and capture `.executable.url`.
- **Crumb confusion.** With a current Jenkins + API token you do NOT need a crumb (token-exempt since 2.96/2.107). A `403 No valid crumb` means old Jenkins or password auth → then fetch one. A `404` on `crumbIssuer/api/json` means CSRF is disabled → skip it.
- **config.xml content-type.** `createItem` needs the body sent as `Content-Type: application/xml` (use `--data-binary @config.xml`) or the XML gets form-mangled.
- **Folder nesting.** A job inside a folder is `job/<folder>/job/<name>` — repeat `job/` per level; a single `job/<folder>/<name>` is wrong.
- **`buildWithParameters` needs a parameterized job.** Params only take effect if the job declares them; on an unparameterized job they are ignored. Define the parameter in the job config first.
- **A parameterized job REJECTS `/build` with `400 Bad Request`.** The reverse of the above: once a job declares parameters, `POST job/<name>/build` returns 400 — you must use `buildWithParameters` (even to build with the declared defaults, sending no overrides). So `trigger-build.sh <job>` with no `K=V` args (which posts to `/build`) cannot trigger a parameterized job; pass at least one `K=V` (or a default) so it routes to `buildWithParameters`.
- **swaggy-jenkins is partial + quirky.** The bundled spec omits `buildWithParameters`, `consoleText`, arbitrary `job/<n>/<build>/api/json`, and models `postJobBuild` with an invented `json` query param. Trust `assets/endpoint-index.md` for paths.
- **`result` is null while building.** A build still running reports `building: true`, `result: null` — don't treat null as failure.
- **A poll timeout means "still queued," not "failed."** `poll-queue-item.sh` gives up after ~3 min; a build legitimately blocked (no free executor, quiet period, `.blocked`/`.stuck`) hits that without having failed. Inspect `.why` and re-poll — don't report a false failure.
- **Huge responses.** `api/json` without `?tree=`/`?depth=` on a busy instance can be large; always filter.

## Anti-patterns

- **Reading the build before polling the queue.** The most common failure — the trigger gave you a queue item, not a build. Poll first.
- **Attaching a crumb to every POST.** Wasteful and wrong-headed under token auth (it's exempt); fetch a crumb only on a 403, and handle the 404-when-disabled case.
- **Trusting swaggy-jenkins as authoritative.** It's unofficial and partial — cross-check only; the CORE index is the source of truth.
- **Echoing the token.** Never `echo $JENKINS_TOKEN`, never paste it into a printed command, never write its value to a file. Reference the env var inside `curl -u` only.
- **Committing a `Jenkinsfile` / configuring a webhook.** That's a `vcs` op, not a Jenkins-API op — out of scope.
- **SDK creep.** Don't reach for the jar-based Jenkins CLI or a `pip` client — `curl` + the index cover the CORE surface.

## Output

This skill produces **API side effects** (the requested Jenkins operation) and returns the parsed JSON (or plaintext console log) to the calling agent. It writes no files of its own (it only *consumes* the caller-injected credentials). For a build it reports the queue item → build URL/number → terminal `result`; for reads it returns the requested JSON. The abstract consumer is the calling agent (or a sub-agent) that needs the CI/CD operation performed; secrets never enter that output.

## Related

- [`references/credentials.md`](references/credentials.md) — the credential contract this skill consumes (caller-injected `base_url` + `username` + the ordered token-load rule + the HTTP-Basic bridge).
- [`references/patterns.md`](references/patterns.md) — the async-build flow, the crumb fallback, paths/folders/response-shaping, status+console, job CRUD, and the no-official-OpenAPI grounding caveat.
- The REST-direct + bundled-spec pattern generalizes to other API providers (the same `curl`-driven REST ops shape, adapted to Jenkins' path-addressed API + HTTP-Basic token auth).

## Progressive disclosure

Heavy content lives in subfolders, loaded only on demand:

- [`references/credentials.md`](references/credentials.md) — caller-injected fields, the ordered token-load rule, the HTTP-Basic bridge, honest-secret handling. Load in Step 1.
- [`references/patterns.md`](references/patterns.md) — async builds + queue poll, the crumb fallback, paths/folders/`?tree=`, status+console, job CRUD, grounding caveat. Load in Steps 3–5.
- [`references/sources.md`](references/sources.md) — provenance (official Remote Access docs + the unofficial swaggy-jenkins flag) + the "confirm live" items.
- `assets/endpoint-index.md` — the authoritative CORE path table (Step 2).
- `assets/swaggy-jenkins-openapi.json` — the bundled UNOFFICIAL OpenAPI (queried via the resolver, never loaded wholesale; a partial cross-check).
- `scripts/endpoint.py` + `.validation.md` — the `python3` resolver over swaggy-jenkins (Step 2 cross-check).
- `scripts/{trigger-build,poll-queue-item,build-status,console-log,list-jobs,crumb}.sh` + `.validation.md` — six validated example scripts.

## Standalone usage (optional, not required)

This is a convenience for a **human running the skill by hand** outside an agent-flow — it is **not a dependency of the skill**. The skill's normative contract is caller-injection (Step 1); this appendix is only the manual-operator bridge.

To run by hand, create an API token (`<base_url>/me/configure` → API Token → Add new token), store its value in a gitignored `.env`, then populate the three vars yourself:

```bash
set -a; source .env; set +a                 # loads $JENKINS_CI_TOKEN, never prints it
export base_url="https://jenkins.example.com"
export username="my-user"
export JENKINS_TOKEN="$JENKINS_CI_TOKEN"
bash scripts/list-jobs.sh                    # verify auth
q="$(bash scripts/trigger-build.sh my-job BRANCH=main)"
bash scripts/poll-queue-item.sh "$q"
```

The token value is referenced by name only, never printed. A Jenkins token carries full user authority (no scopes) — prefer a revocable token.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap).
- Body ≤ ~500 lines / 5,000 tokens — kept in context every turn; REST detail lives in `references/`.
- `assets/swaggy-jenkins-openapi.json` is large (queried on disk, never loaded into context).
