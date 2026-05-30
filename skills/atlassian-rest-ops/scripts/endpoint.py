#!/usr/bin/env python3
"""Resolve one OpenAPI operation from a bundled Atlassian spec.

Usage: python3 endpoint.py <confluence|jira> <operationId>

Finds the operation by operationId in the bundled spec, $ref-resolves its
request/response schemas (bounded depth + cycle guard), and prints a readable
summary + a curl skeleton. Python stdlib only; no pip dependency.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SPECS = {"confluence": "confluence-v2.json", "jira": "jira-v3.json"}
BASE = {"confluence": "$ATLASSIAN_BASE_URL/wiki/api/v2", "jira": "$ATLASSIAN_BASE_URL"}
MAXDEPTH = 5


def load(api):
    with open(os.path.join(HERE, "..", "assets", SPECS[api])) as f:
        return json.load(f)


def resolve_ref(spec, ref):
    node = spec
    for part in ref.lstrip("#/").split("/"):
        node = node[part]
    return node


def find_op(spec, opid):
    for path, item in spec.get("paths", {}).items():
        for method, op in (item or {}).items():
            if isinstance(op, dict) and op.get("operationId") == opid:
                return method.upper(), path, op
    return None


def prop_type(ps, spec):
    if "$ref" in ps:
        return ps["$ref"].split("/")[-1]
    t = ps.get("type")
    if t == "array":
        it = ps.get("items", {}) or {}
        inner = it["$ref"].split("/")[-1] if "$ref" in it else it.get("type", "?")
        return f"array<{inner}>"
    if ps.get("enum"):
        return f"{t or 'enum'} {ps['enum']}"
    return t or "object"


def schema_lines(schema, spec, seen, depth, indent):
    pad = "  " * indent
    if depth <= 0:
        yield pad + "… (max depth)"
        return
    if not isinstance(schema, dict):
        return
    if "$ref" in schema:
        ref = schema["$ref"]
        if ref in seen:
            yield pad + f"→ {ref.split('/')[-1]} (recursive)"
            return
        yield from schema_lines(resolve_ref(spec, ref), spec, seen | {ref}, depth, indent)
        return
    for comb in ("allOf", "oneOf", "anyOf"):
        if comb in schema:
            yield pad + f"({comb}):"
            for sub in schema[comb]:
                yield from schema_lines(sub, spec, seen, depth - 1, indent + 1)
            return
    t = schema.get("type")
    if t == "object" or "properties" in schema:
        req = set(schema.get("required", []))
        props = schema.get("properties", {}) or {}
        if not props:
            yield pad + "{ free-form object }"
            return
        for name, ps in props.items():
            mark = " *" if name in req else ""
            yield pad + f"- {name}{mark}: {prop_type(ps, spec)}"
            yield from schema_lines(ps, spec, seen, depth - 1, indent + 1)
    elif t == "array":
        yield pad + "[array of]:"
        yield from schema_lines(schema.get("items", {}), spec, seen, depth - 1, indent + 1)


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in SPECS:
        print("usage: python3 endpoint.py <confluence|jira> <operationId>", file=sys.stderr)
        sys.exit(2)
    api, opid = sys.argv[1], sys.argv[2]
    spec = load(api)
    found = find_op(spec, opid)
    if not found:
        print(f"operationId '{opid}' not found in {api}", file=sys.stderr)
        sys.exit(1)
    method, path, op = found

    print(f"operation: {opid}")
    print(f"{method} {path}")
    if op.get("summary"):
        print(f"summary: {op['summary'].strip()}")
    print(f"base: {BASE[api]} + path  (auth: -u \"$ATLASSIAN_EMAIL:$<token_env>\")")

    params = []
    for pr in (op.get("parameters") or []):
        if "$ref" in pr:
            pr = resolve_ref(spec, pr["$ref"])
        params.append(pr)
    if params:
        print("\nPARAMS (* = required):")
        for pr in params:
            mark = " *" if pr.get("required") else ""
            print(f"  - {pr.get('name')} ({pr.get('in')}){mark}: {prop_type(pr.get('schema', {}) or {}, spec)}")

    rb = op.get("requestBody", {})
    if "$ref" in rb:
        rb = resolve_ref(spec, rb["$ref"])
    content = rb.get("content", {}) or {}
    if content:
        ct = next(iter(content))
        print(f"\nREQUEST BODY ({ct})  (* = required):")
        for line in schema_lines(content[ct].get("schema", {}), spec, set(), MAXDEPTH, 1):
            print(line)

    resp = op.get("responses", {}) or {}
    code = next((c for c in ("200", "201", "202", "204") if c in resp), None)
    if code and code != "204":
        r = resp[code]
        if "$ref" in r:
            r = resolve_ref(spec, r["$ref"])
        rc = r.get("content", {}) or {}
        if rc:
            ct = next(iter(rc))
            print(f"\nRESPONSE {code} ({ct}):")
            for line in schema_lines(rc[ct].get("schema", {}), spec, set(), 3, 1):
                print(line)

    print("\nERRORS: see references/patterns.md (Jira: ErrorCollection {errorMessages, errors, status}; Confluence: inline JSON).")
    print("\nCURL SKELETON:")
    cth = ' -H "Content-Type: application/json"' if content else ""
    body = " -d '<json body>'" if content else ""
    print(f'  curl -sS -u "$ATLASSIAN_EMAIL:$<token_env>" -X {method} \\')
    print(f'    -H "Accept: application/json"{cth} \\')
    print(f'    "{BASE[api]}{path}"{body}')


if __name__ == "__main__":
    main()
