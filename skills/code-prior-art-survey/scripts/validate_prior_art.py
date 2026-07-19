#!/usr/bin/env python3
"""Deterministic validator for code-prior-art-survey artifacts.

Subcommands:
    keyword-map <file>                       validate a keyword map
    search <file> --keyword-map <map-file>   validate a search output
    extract <file>                           validate an extract output (frontmatter + body)

Prints one "FAIL <rule>: ..." line per violation; exits 0 when clean, 1 on
violations, 2 on usage errors. Schema files and the master source registry are
resolved relative to this script's package (schemas/, references/).
"""

import argparse
import datetime
import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

PKG = Path(__file__).resolve().parent.parent
SCHEMAS = PKG / "schemas"
REGISTRY_PATH = PKG / "references" / "source-registry.yaml"

# The canonical 10 extraction section headings — the single source shared by the
# extraction-template guide and the validator's body-completeness check.
EXTRACT_HEADINGS = [
    "Core abstractions",
    "Architectural pattern",
    "Solved well",
    "Solved poorly",
    "Trusted dependencies",
    "Patterns to borrow",
    "Anti-patterns",
    "Testing approach",
    "Production setup",
    "Verdict",
]


def _normalize(obj):
    """Recursively convert YAML-parsed datetime/date objects to ISO-8601 strings."""
    if isinstance(obj, dict):
        return {k: _normalize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_normalize(v) for v in obj]
    if isinstance(obj, datetime.datetime):
        return obj.isoformat().replace("+00:00", "Z")
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    return obj


def _load_yaml(path: Path, fails: list, label: str):
    try:
        with open(path) as fh:
            doc = _normalize(yaml.safe_load(fh))
    except OSError as exc:
        fails.append(f"FAIL unreadable: {label} {path}: {exc}")
        return None
    except yaml.YAMLError as exc:
        fails.append(f"FAIL yaml_parse: {label} {path}: {exc}")
        return None
    if doc is None:
        fails.append(f"FAIL empty: {label} {path}: document is empty")
        return None
    if not isinstance(doc, dict):
        fails.append(f"FAIL not_a_mapping: {label} {path}: top level must be a mapping")
        return None
    return doc


def _schema_fails(doc, schema_file: str, fails: list):
    schema = json.loads((SCHEMAS / schema_file).read_text())
    for err in sorted(
        Draft202012Validator(schema).iter_errors(doc), key=lambda e: e.json_path
    ):
        fails.append(f"FAIL schema: {err.json_path}: {err.message}")


def validate_keyword_map(path) -> list:
    """Validate a keyword-map artifact; returns FAIL lines (empty = clean)."""
    fails: list = []
    doc = _load_yaml(Path(path), fails, "keyword-map")
    if doc is None:
        return fails
    _schema_fails(doc, "keyword-map.schema.json", fails)
    if fails:
        return fails

    registry = _load_registry(fails)
    if registry is None:
        return fails
    for sid in doc["sources"]["active"]:
        if sid not in registry:
            fails.append(
                f"FAIL unknown_source: sources.active id '{sid}' is not in the "
                "source registry (coverage against it would be unverifiable)"
            )
    for entry in doc["sources"]["skipped"]:
        if entry["id"] not in registry:
            fails.append(
                f"FAIL unknown_source: sources.skipped id '{entry['id']}' is "
                "not in the source registry"
            )

    seen = set()
    for g in doc["groups"]:
        if g["id"] in seen:
            fails.append(f"FAIL group_id_unique: duplicate group id '{g['id']}'")
        seen.add(g["id"])
        terms = [e["term"].strip().lower() for e in g["expansions"]]
        dupes = {t for t in terms if terms.count(t) > 1}
        for t in sorted(dupes):
            fails.append(
                f"FAIL expansion_term_unique: group '{g['id']}' repeats term '{t}'"
            )
    if doc["mode"] == "delta" and not doc["lineage"]["extends"]:
        fails.append(
            "FAIL delta_lineage: mode is 'delta' but lineage.extends is null — "
            "a delta map must name its baseline"
        )
    return fails


def _load_registry(fails: list):
    reg = _load_yaml(REGISTRY_PATH, fails, "source-registry")
    if reg is None:
        return None
    return {s["id"]: s for s in reg["sources"]}


def validate_search(path, keyword_map_path) -> list:
    """Validate a search-output artifact against its keyword map + the registry."""
    fails: list = []
    doc = _load_yaml(Path(path), fails, "search-output")
    kw = _load_yaml(Path(keyword_map_path), fails, "keyword-map")
    registry = _load_registry(fails)
    if doc is None or kw is None or registry is None:
        return fails
    kw_fails: list = []
    _schema_fails(kw, "keyword-map.schema.json", kw_fails)
    if kw_fails:
        fails.extend(
            f.replace("FAIL schema:", "FAIL keyword_map_invalid:", 1)
            for f in kw_fails
        )
        return fails
    _schema_fails(doc, "search-output.schema.json", fails)
    if fails:
        return fails

    group_by_id = {g["id"]: g for g in kw["groups"]}
    active = set(kw["sources"]["active"])
    angle = doc["meta"]["angle_id"]

    if doc["meta"]["project"] != kw["project"]:
        fails.append(
            f"FAIL project_mismatch: output is for project "
            f"'{doc['meta']['project']}' but the supplied map is for "
            f"'{kw['project']}'"
        )

    if doc["meta"]["keyword_map_revision"] != kw["revision"]:
        fails.append(
            f"FAIL revision_mismatch: output ran against map revision "
            f"{doc['meta']['keyword_map_revision']} but the supplied map is "
            f"revision {kw['revision']}"
        )

    for cell in doc["coverage"]:
        if cell["group_id"] not in group_by_id:
            fails.append(
                f"FAIL unknown_group: coverage cell references '{cell['group_id']}' "
                "which is not in the keyword map"
            )
        if cell["source"] not in registry:
            fails.append(
                f"FAIL unknown_source: coverage cell references '{cell['source']}' "
                "which is not in the source registry"
            )

    covered = {(c["group_id"], c["source"]) for c in doc["coverage"]}
    for src in registry.values():
        if src["angle"] != angle or src["id"] not in active:
            continue
        for g in kw["groups"]:
            if g["type"] in src["group_types"] and (g["id"], src["id"]) not in covered:
                fails.append(
                    f"FAIL coverage_missing: group {g['id']} x source {src['id']} "
                    "has no coverage cell (zero-hit cells are required too)"
                )

    seen_ids = set()
    for cand in doc["candidates"]:
        if cand["id"] in seen_ids:
            fails.append(
                f"FAIL candidate_id_unique: duplicate candidate id '{cand['id']}'"
            )
        seen_ids.add(cand["id"])
        for gid in cand["found_by"]["group_ids"]:
            if gid not in group_by_id:
                fails.append(
                    f"FAIL unknown_group: candidate '{cand['id']}' found_by "
                    f"references '{gid}' which is not in the keyword map"
                )
        for src in cand["found_by"]["sources"]:
            if src not in registry:
                fails.append(
                    f"FAIL unknown_source: candidate '{cand['id']}' found_by "
                    f"references '{src}' which is not in the source registry"
                )
    return fails


def _load_frontmatter(path: Path, fails: list, label: str):
    """Read a `.md`, split its leading YAML frontmatter from the body; returns (fm, body)."""
    try:
        text = path.read_text()
    except OSError as exc:
        fails.append(f"FAIL unreadable: {label} {path}: {exc}")
        return None, None
    if not text.lstrip().startswith("---"):
        fails.append(
            f"FAIL no_frontmatter: {label} {path}: must open with a frontmatter block"
        )
        return None, None
    parts = text.split("---", 2)
    if len(parts) < 3:
        fails.append(f"FAIL no_frontmatter: {label} {path}: unterminated frontmatter block")
        return None, None
    try:
        fm = _normalize(yaml.safe_load(parts[1]))
    except yaml.YAMLError as exc:
        fails.append(f"FAIL yaml_parse: {label} {path}: {exc}")
        return None, None
    if not isinstance(fm, dict):
        fails.append(f"FAIL not_a_mapping: {label} {path}: frontmatter must be a mapping")
        return None, None
    return fm, parts[2]


def validate_extract(path) -> list:
    """Validate an extract-output artifact (frontmatter + body); shape + completeness only."""
    fails: list = []
    fm, body = _load_frontmatter(Path(path), fails, "extract-output")
    if fm is None:
        return fails
    _schema_fails(fm, "extract-output.schema.json", fails)
    if fails:
        return fails
    if fm.get("skipped") is True:
        if fm.get("reason") == "irrelevant" and len((fm.get("bail_rationale") or "").strip()) < 10:
            fails.append(
                "FAIL bail_rationale: an 'irrelevant' skip must carry a non-trivial "
                "bail_rationale (why the repo touches none of the scope)"
            )
        return fails
    for heading in EXTRACT_HEADINGS:
        if f"## {heading}" not in body:
            fails.append(f"FAIL missing_heading: the extraction body is missing '## {heading}'")
    return fails


def main(argv=None) -> int:
    """CLI entry point; returns the process exit code."""
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="kind", required=True)
    p_kw = sub.add_parser("keyword-map")
    p_kw.add_argument("file")
    p_s = sub.add_parser("search")
    p_s.add_argument("file")
    p_s.add_argument("--keyword-map", required=True)
    p_e = sub.add_parser("extract")
    p_e.add_argument("file")
    args = parser.parse_args(argv)

    if args.kind == "keyword-map":
        fails = validate_keyword_map(args.file)
    elif args.kind == "search":
        fails = validate_search(args.file, args.keyword_map)
    else:
        fails = validate_extract(args.file)

    for line in fails:
        print(line)
    if fails:
        print(f"{len(fails)} violation(s).")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
