# Sources — jenkins-rest-ops provenance

Jenkins has **no official OpenAPI/Swagger spec** (a long-standing gap, JENKINS-35808). This skill is grounded PRIMARILY on the official Jenkins Remote Access API docs; the bundled OpenAPI is the community `swaggy-jenkins` description, flagged unofficial. All web content was sanitized before use; facts are paraphrased, never lifted verbatim.

## Official (authoritative for the CORE paths)

- Jenkins Remote Access API — `https://www.jenkins.io/doc/book/using/remote-access-api/` — the `api/json` pattern, HTTP Basic auth, `build` / `buildWithParameters` POST, `?tree=` / `?depth=` / `?pretty=`, nested `job/<folder>/job/<name>/` folders, and the **API-token-exempts-crumb** note.
- Authenticating scripted clients — `https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/` — token creation via `/me/configure`, token vs password.
- New API token system (2.129+) blog — `https://www.jenkins.io/blog/2018/07/02/new-api-token-system/` — multiple named tokens, SHA-256-hashed / shown-once, revoke, use tracking.
- Jenkins wiki — Remote Access API — `createItem` / copy / `doDelete` / `enable` / `disable`, `config.xml` GET/POST, `stop`, `consoleText`, `logText/progressiveText` (+ `X-Text-Size` / `X-More-Data`).

## Vendor (credible, not jenkins.io)

- CloudBees — CSRF Protection Explained — the crumbIssuer fields, `Jenkins-Crumb` default, session-scope, and the API-token CSRF exemption from 2.96/2.107 (citing JENKINS-22474).

## Community / unofficial (flagged)

- `cliffano/swaggy-jenkins` — the **unofficial** OpenAPI 3.1.0 description bundled as `assets/swaggy-jenkins-openapi.json` (raw: `https://raw.githubusercontent.com/cliffano/swaggy-jenkins/master/specification/jenkins.yml`). A partial cross-check only; it omits several CORE ops and models `postJobBuild` with an invented `json` query param.
- Baeldung (403 crumb error), marslo (crumbIssuer xpath / 404-when-off), Stitchflow (201 + Location queue item), `Queue.Item` javadoc + JENKINS-31039 (queue-item ephemerality ~5 min) — corroborate the async-build + crumb behavior.
- `avivsinai/jenkins-cli` (~197 installs) — consulted as source material for the CLI-ops shape (sanitized); not adopted (sub-1K, not on the credential contract).

## Verified live

- 2026-06-13 — live smoke PASS against a real Jenkins 2.555.3-lts (a hardened JCasC fixture, agents-hq `docs/superpowers/jenkins-fixture/`). Token generated via the crumb path (password auth needs a crumb; `generateNewToken` → `data.tokenValue`), then token-auth (crumb-exempt) for list → `buildWithParameters` → poll-queue-item → build-status (`result: SUCCESS`) → consoleText. Verified on both docker and podman.
- Findings folded from that smoke:
  - `list-jobs.sh` (and any `?tree=...[...]` URL) aborted with curl "bad range" (error 3) — the `[brackets]` are curl glob metacharacters. Fixed: added `-g`/`--globoff` to `list-jobs.sh` + a SKILL.md note on the `?tree=` pattern.
  - A **parameterized** job rejects `POST .../build` with `400 Bad Request` — `buildWithParameters` is required (even with defaults). Documented as a gotcha (the reverse of the existing "buildWithParameters needs a parameterized job"); `trigger-build.sh <job>` with no `K=V` posts to `/build` and so cannot trigger a parameterized job.

## Flagged uncertain (carry as "confirm live")

- The build POST returning **201 + `Location:` queue-item** is well-established + in swaggy-jenkins/community guides but not stated verbatim on the official Remote Access page — treat as correct, officially-underdocumented.
- Per-token permission scoping: evidence indicates tokens carry full user authority with no per-endpoint scopes (absence inferred, not stated).
- Exact token-creation UI labels ("Add new Token") — lightly unverified wording.
