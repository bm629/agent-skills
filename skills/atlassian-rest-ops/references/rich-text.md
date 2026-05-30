# Rich text — ADF (Jira) vs Confluence body representations

The #1 source of failed writes. Jira and Confluence model rich text **differently**.

## Jira v3 — ADF as a RAW JSON object

`fields.description`, comment `body`, etc. take an Atlassian Document Format (ADF) document — a **raw JSON object**, not stringified:

```json
{ "version": 1, "type": "doc", "content": [
  { "type": "paragraph", "content": [ { "type": "text", "text": "Hello" } ] }
] }
```

Common nodes: `doc` (root), `paragraph`, `text`, `heading` (`attrs.level`), `bulletList`/`orderedList` + `listItem`, `codeBlock`. Marks (bold, link) attach to `text` nodes. Plain text → wrap in `paragraph` → `text`. Source: developer.atlassian.com/cloud/jira/platform/apis/document/structure/.

Create-issue example:
```json
{ "fields": {
    "project": { "key": "ABC" },
    "issuetype": { "name": "Task" },
    "summary": "Example",
    "description": { "version":1, "type":"doc", "content":[
      { "type":"paragraph", "content":[ { "type":"text", "text":"body" } ] } ] }
} }
```

## Confluence v2 — body = `{ representation, value }`, value is a STRING

```json
{ "representation": "storage" | "atlas_doc_format", "value": "<string>" }
```

- `storage` → `value` is storage-format XHTML, e.g. `"<p>Hello</p>"`.
- `wiki` → `value` is legacy wiki-markup (also accepted; `storage`/`atlas_doc_format` are preferred).
- `atlas_doc_format` → `value` is the ADF document JSON **stringified/escaped**, e.g.
  `"value": "{\"version\":1,\"type\":\"doc\",\"content\":[{\"type\":\"paragraph\",\"content\":[{\"type\":\"text\",\"text\":\"Hello\"}]}]}"`.

Source: developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/.

## The cross-API gotcha

Same ADF document, two embeddings:
- **Jira:** the ADF as a **raw object** (`"description": { …adf… }`).
- **Confluence `atlas_doc_format`:** the ADF object **JSON-stringified** inside `value`.

Sending a raw object to Confluence — or a stringified blob to Jira — fails. **Confluence `value` is always a string**, regardless of representation.
