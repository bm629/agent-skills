# Sources / provenance

Authoritative references used to build this skill (provenance lives here, not in SKILL.md).

- Atlassian Document Format (ADF) — structure: https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/
- ADF `doc` node: https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/doc/
- Confluence Cloud REST API v2 (page group): https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/
- Jira Cloud platform REST API v3: https://developer.atlassian.com/cloud/jira/platform/rest/v3/

## Bundled specs (in `assets/`, added during augmentation)

- `confluence-v2.json` — Confluence Cloud REST API v2, OpenAPI 3.0.3, 147 paths / 213 operations (100% `operationId` coverage).
- `jira-v3.json` — Jira Cloud platform REST API v3, OpenAPI 3.0.1, 420 paths / 619 operations (100% `operationId` coverage).

Verified 2026-05-31: the per-API patterns + rich-text schemas were cross-checked against these specs and the official docs above; the rich-text findings (the spec is loose there) were researched from the official docs and passed the external-content-sanitizer (clean).
