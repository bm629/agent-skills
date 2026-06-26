#!/usr/bin/env python3
"""Deterministic validator for capability-map.yaml + manifest.yaml.

The single deterministic gate for the project-document-discovery output: JSON
Schema validation against both schemas plus the algorithmic checks the schema
cannot express (uniqueness, referential integrity, acyclicity, ISO-8601, cross-
file scope). Read-only: it reports, it never rewrites the files.

Usage:
    python validate.py <capability-map.yaml> <manifest.yaml>

Exit 0 and one OK line when every check passes; exit 1 and one "FAIL <rule>: ..."
line per violation otherwise. Requires pyyaml + jsonschema.
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

import jsonschema
import yaml

HERE = Path(__file__).parent
SCHEMAS = HERE.parent / "schemas"

# Kept-enum string fields canonicalised (whitespace stripped) before the enum
# check, so a cosmetic slip like "< 100" matches "<100". Comparison-only — the
# in-memory copy is normalised, the file on disk is untouched.
_NORMALIZE_SCALAR = [
    ("archetype", "primary"),
    ("domain", "audience"),
    ("scale", "concurrency"),
    ("scale", "throughput"),
    ("scale", "real_time"),
    ("scale", "data_volume"),
    ("scale", "availability_target"),
    ("scale", "consistency"),
    ("scale", "geo_distribution"),
    ("integrations", "complexity"),
    ("ui", "complexity"),
    ("ui", "target_users"),
    ("data_ml", "pipeline_type"),
    ("data_ml", "data_volume_class"),
    ("data_ml", "ml_involvement"),
    ("infrastructure", "deployment_model"),
    ("infrastructure", "compute_paradigm"),
    ("business", "model"),
]
_NORMALIZE_LIST = []
_PER_CAP_SCALAR = ["subdomain", "ui_complexity", "status"]


def _canon(value):
    return re.sub(r"\s+", "", value) if isinstance(value, str) else value


def _normalize(capmap):
    cm = capmap.get("capability_map") or {}
    for section, key in _NORMALIZE_SCALAR:
        block = cm.get(section)
        if isinstance(block, dict) and isinstance(block.get(key), str):
            block[key] = _canon(block[key])
    for section, key in _NORMALIZE_LIST:
        block = cm.get(section)
        if isinstance(block, dict) and isinstance(block.get(key), list):
            block[key] = [_canon(x) for x in block[key]]
    for cap in capmap.get("product_capabilities") or []:
        if isinstance(cap, dict):
            for key in _PER_CAP_SCALAR:
                if isinstance(cap.get(key), str):
                    cap[key] = _canon(cap[key])


def _schema_failures(doc, schema, label, out):
    validator = jsonschema.Draft202012Validator(schema)
    for err in sorted(validator.iter_errors(doc), key=lambda e: list(e.absolute_path)):
        loc = ".".join(str(p) for p in err.absolute_path) or "(root)"
        out.append(f"FAIL schema: {label}: {loc}: {err.message}")


def _is_iso(value):
    if not isinstance(value, str):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def _cap_ids(capmap):
    return [c.get("id") for c in capmap.get("product_capabilities") or [] if isinstance(c, dict)]


def _doc_ids(manifest):
    return [d.get("id") for d in manifest.get("documents") or [] if isinstance(d, dict)]


def _dupes(ids):
    seen, dup = set(), []
    for i in ids:
        if i in seen and i not in dup:
            dup.append(i)
        seen.add(i)
    return dup


def _has_cycle(edges):
    """edges: {node: [deps]}. True if any cycle reachable."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in edges}

    def visit(node):
        color[node] = GRAY
        for dep in edges.get(node, []):
            if dep not in color:
                continue
            if color[dep] == GRAY:
                return True
            if color[dep] == WHITE and visit(dep):
                return True
        color[node] = BLACK
        return False

    return any(color[n] == WHITE and visit(n) for n in edges)


def _check_refs_and_cycles(capmap, manifest, out):
    cap_ids = set(_cap_ids(capmap))
    cap_edges = {}
    for cap in capmap.get("product_capabilities") or []:
        if not isinstance(cap, dict):
            continue
        cid = cap.get("id")
        cap_edges[cid] = [d for d in cap.get("depends_on") or []]
        for field in ("depends_on", "superseded_by"):
            for ref in cap.get(field) or []:
                if ref not in cap_ids:
                    out.append(f"FAIL ref-integrity: capability-map.yaml: {cid}.{field} -> '{ref}' not a capability id")
        merged = cap.get("merged_into")
        if isinstance(merged, str) and merged not in cap_ids:
            out.append(f"FAIL ref-integrity: capability-map.yaml: {cid}.merged_into -> '{merged}' not a capability id")
    if _has_cycle(cap_edges):
        out.append("FAIL acyclicity: capability-map.yaml: depends_on graph has a cycle")

    doc_ids = set(_doc_ids(manifest))
    doc_edges = {}
    for doc in manifest.get("documents") or []:
        if not isinstance(doc, dict):
            continue
        did = doc.get("id")
        deps = [d for d in doc.get("depends_on") or []]
        doc_edges[did] = deps
        for ref in deps:
            if ref not in doc_ids:
                out.append(f"FAIL ref-integrity: manifest.yaml: {did}.depends_on -> '{ref}' not a document id")
    if _has_cycle(doc_edges):
        out.append("FAIL acyclicity: manifest.yaml: depends_on graph has a cycle")


def _check_cross_file(capmap, manifest, out):
    cap_ids = set(_cap_ids(capmap))
    for doc in manifest.get("documents") or []:
        if not isinstance(doc, dict):
            continue
        scope = doc.get("scope")
        if scope != "system" and scope not in cap_ids:
            out.append(f"FAIL cross-file: manifest.yaml: {doc.get('id')}.scope -> '{scope}' is not \"system\" or a capability id")


def main(argv):
    if len(argv) != 3:
        print("usage: validate.py <capability-map.yaml> <manifest.yaml>", file=sys.stderr)
        return 2
    capmap_path, manifest_path = Path(argv[1]), Path(argv[2])
    capmap = yaml.safe_load(capmap_path.read_text())
    manifest = yaml.safe_load(manifest_path.read_text())
    capmap_schema = json.loads((SCHEMAS / "capability-map.schema.json").read_text())
    manifest_schema = json.loads((SCHEMAS / "manifest.schema.json").read_text())

    out = []
    _normalize(capmap)
    _schema_failures(capmap, capmap_schema, "capability-map.yaml", out)
    _schema_failures(manifest, manifest_schema, "manifest.yaml", out)

    for dup in _dupes(_cap_ids(capmap)):
        out.append(f"FAIL uniqueness: capability-map.yaml: duplicate capability id '{dup}'")
    for dup in _dupes(_doc_ids(manifest)):
        out.append(f"FAIL uniqueness: manifest.yaml: duplicate document id '{dup}'")

    _check_refs_and_cycles(capmap, manifest, out)
    _check_cross_file(capmap, manifest, out)

    if not _is_iso(manifest.get("generated_at")):
        out.append(f"FAIL iso-8601: manifest.yaml: generated_at '{manifest.get('generated_at')}' is not ISO-8601")
    meta_ts = (capmap.get("_meta") or {}).get("generated_at")
    if meta_ts is not None and not _is_iso(meta_ts):
        out.append(f"FAIL iso-8601: capability-map.yaml: _meta.generated_at '{meta_ts}' is not ISO-8601")

    if out:
        for line in out:
            print(line)
        print(f"\n{len(out)} failure(s).")
        return 1
    print("OK: capability-map.yaml + manifest.yaml pass all deterministic checks.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
