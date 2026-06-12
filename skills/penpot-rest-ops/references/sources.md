# Sources — penpot-rest-ops provenance

Research grounded the call mechanics + auth against official Penpot sources; the bundled spec is authoritative for command schemas. All web content was sanitized before use; facts are paraphrased, never lifted verbatim.

## Authoritative (bundled)

- `assets/penpot-openapi.json` — the official Penpot OpenAPI (Penpot 2.16, OpenAPI 3.0.0; 137 commands), fetched from `https://design.penpot.app/api/main/doc/openapi.json`. Authoritative for command names, request-body schemas, and required/optional fields. Note: declares request bodies only — no response or error schemas.

## Official

- Penpot Integration Guide — `https://help.penpot.app/technical-guide/integration/` — the runtime call path `POST /api/rpc/command/<command>`, the `Authorization: Token <token>` header, the access-token creation UI + expiration options, and the `get-profile` whoami example.
- Penpot Authentication subsystem — `https://help.penpot.app/technical-guide/developer/subsystems/authentication/` — session-token / cookie login model (the interactive alternative to token auth).
- Penpot Backend architecture — `https://help.penpot.app/technical-guide/developer/architecture/backend/` — RPC = Clojure command functions over HTTP; params transit-encoded internally.

## Community (on the official repo — flagged unofficial)

- `github.com/penpot/penpot` discussion #4180 (using the API) and issue #5112 (`update-file` changes object) — corroborate the opacity/instability of the `update-file` "changes" surface (basis for excluding rich canvas authoring).
- `github.com/penpot/penpot` issues #3670 / #4826 — large/truncated JSON on big file reads (basis for the "large reads" caution).

## Verified live

- None yet. The Phase 2.D live smoke (create → read → list → cleanup against a real Penpot instance with an injected token) is pending the owner's `base_url` + token.

## Flagged uncertain (carry as "confirm live")

- The error envelope `{type, code, hint}` is Penpot's `ex/raise` convention, not declared in the spec — confirm exact fields against a live failing call.
- The transit-default content negotiation is stated in official-repo discussion, not pinned on a single help page — `Accept: application/json` is the safe action regardless.
- `get-team`'s exact request field (schema shows no required field; the auto-generated example is mislabeled `fileId` — pass `{"id": <teamUuid>}`).
- Self-hosted `base_url` exact form behind a path prefix is deployment-dependent.
- Public rate limits — none documented.
