"""Fixture tests for the project-document-discovery schemas + validator.

Repo has no harness; run author-side:
    uv run --with pyyaml --with jsonschema --with pytest pytest \
        skills/project-document-discovery/scripts/test_validate.py
"""

import copy
import json
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest
import yaml

HERE = Path(__file__).parent
SCHEMAS = HERE.parent / "schemas"
CAPMAP_SCHEMA = json.loads((SCHEMAS / "capability-map.schema.json").read_text())
MANIFEST_SCHEMA = json.loads((SCHEMAS / "manifest.schema.json").read_text())
VALIDATE = HERE / "validate.py"


def _capmap(**caps):
    """A minimal schema-valid capability-map; override capability_map subkeys."""
    doc = {
        "capability_map": {},
        "product_capabilities": [
            {
                "id": "analytics",
                "name": "Analytics",
                "scope": "Tracks usage metrics; does NOT store PII.",
                "owns": ["metric"],
                "has_ui": False,
                "has_api": False,
                "has_persistence": False,
            }
        ],
    }
    doc["capability_map"].update(caps)
    return doc


def _manifest(**over):
    doc = {
        "version": 1,
        "generated_at": "2026-06-25T00:00:00Z",
        "schema": "manifest/v1",
        "documents": [],
        "capabilities": [],
        "roles": [],
        "skills": [],
        "tools": [],
        "amendments": [],
    }
    doc.update(over)
    return doc


def _valid(instance, schema):
    jsonschema.validate(instance, schema)


def _invalid(instance, schema):
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance, schema)


# --- Cycle 1: capability-map relaxations ---

def test_capmap_schema_accepts_relaxed():
    doc = _capmap(
        security={"compliance_requirements": ["SEBI"], "auth_type": ["saml"]},
        ui={"ui_types": ["voice"]},
        infrastructure={"cloud_provider": ["digitalocean"]},
        scale={"expected_users": "<100"},
    )
    cap = doc["product_capabilities"][0]
    cap["scope"] = "A" * 437  # was maxLength 300
    cap["owns"] = []  # was minItems 1
    _valid(doc, CAPMAP_SCHEMA)


def test_capmap_schema_keeps_hard_constraints():
    bad_id = _capmap()
    bad_id["product_capabilities"][0]["id"] = "Bad_Id"
    _invalid(bad_id, CAPMAP_SCHEMA)

    missing = _capmap()
    del missing["product_capabilities"][0]["scope"]
    _invalid(missing, CAPMAP_SCHEMA)

    bad_users = _capmap(scale={"expected_users": "loads"})
    _invalid(bad_users, CAPMAP_SCHEMA)  # expected_users enum stays hard


# --- Cycle 2: manifest relaxations ---

def test_manifest_schema_accepts_relaxed():
    doc = _manifest(
        skills=[{"id": "alembic", "version": None, "source": None, "category": "ops"}],
        tools=[
            {
                "id": "db",
                "name": "Database",
                "type": "database",
                "access": "read-write",
                "credential_key": None,
                "auth_type": None,
            }
        ],
    )
    _valid(doc, MANIFEST_SCHEMA)


def test_manifest_schema_keeps_hard_constraints():
    doc = _manifest(
        documents=[{"id": "prd", "title": "PRD"}]  # missing required Document fields
    )
    _invalid(doc, MANIFEST_SCHEMA)


# --- Cycles 3-9: the validator ---

GOOD_CAPMAP = {
    "capability_map": {"scale": {"expected_users": "<100"}},
    "product_capabilities": [
        {
            "id": "catalog",
            "name": "Catalog",
            "scope": "Manages listings; does NOT handle orders.",
            "owns": ["product"],
            "has_ui": True,
            "has_api": True,
            "has_persistence": True,
            "ui_complexity": "moderate",
            "depends_on": [],
        },
        {
            "id": "cart",
            "name": "Cart",
            "scope": "Manages cart; does NOT process payments.",
            "owns": ["cart"],
            "has_ui": True,
            "has_api": True,
            "has_persistence": True,
            "ui_complexity": "moderate",
            "depends_on": ["catalog"],
        },
    ],
    "_meta": {"generated_at": "2026-06-25T00:00:00Z"},
}

GOOD_MANIFEST = {
    "version": 1,
    "generated_at": "2026-06-25T00:00:00Z",
    "schema": "manifest/v1",
    "documents": [
        {
            "id": "prd", "title": "PRD", "type": "prd", "scope": "system",
            "capability": "docs", "archetype": "strategist", "role": "document-author",
            "skills": ["authoring-prd"], "depends_on": [], "account": None, "status": "active",
        },
        {
            "id": "feature-spec-catalog", "title": "Catalog Spec", "type": "feature-spec",
            "scope": "catalog", "capability": "docs", "archetype": "engineer",
            "role": "document-author", "skills": ["authoring-feature-spec"],
            "depends_on": ["prd"], "account": None, "status": "active",
        },
    ],
    "capabilities": [], "roles": [], "skills": [], "tools": [], "amendments": [],
}


def _run(tmp_path, capmap, manifest):
    cm = tmp_path / "capability-map.yaml"
    mf = tmp_path / "manifest.yaml"
    cm.write_text(yaml.safe_dump(capmap))
    mf.write_text(yaml.safe_dump(manifest))
    proc = subprocess.run(
        [sys.executable, str(VALIDATE), str(cm), str(mf)],
        capture_output=True, text=True,
    )
    return proc, cm, mf


def test_validate_good_pair_exit0(tmp_path):
    proc, _, _ = _run(tmp_path, copy.deepcopy(GOOD_CAPMAP), copy.deepcopy(GOOD_MANIFEST))
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_validate_schema_violation(tmp_path):
    cap = copy.deepcopy(GOOD_CAPMAP)
    cap["product_capabilities"][0]["id"] = "Bad_Id"
    proc, _, _ = _run(tmp_path, cap, copy.deepcopy(GOOD_MANIFEST))
    assert proc.returncode != 0
    assert "schema" in proc.stdout.lower()


def test_validate_duplicate_id(tmp_path):
    man = copy.deepcopy(GOOD_MANIFEST)
    man["documents"][1]["id"] = "prd"  # duplicate
    proc, _, _ = _run(tmp_path, copy.deepcopy(GOOD_CAPMAP), man)
    assert proc.returncode != 0
    assert "uniqueness" in proc.stdout.lower() or "duplicate" in proc.stdout.lower()


def test_validate_dangling_refs(tmp_path):
    cap = copy.deepcopy(GOOD_CAPMAP)
    cap["product_capabilities"][1]["depends_on"] = ["ghost"]  # within-file dangling
    man = copy.deepcopy(GOOD_MANIFEST)
    man["documents"][1]["scope"] = "nonexistent-cap"  # cross-file dangling scope
    proc, _, _ = _run(tmp_path, cap, man)
    assert proc.returncode != 0
    out = proc.stdout.lower()
    assert "ghost" in out and "nonexistent-cap" in out


def test_validate_cycle(tmp_path):
    cap = copy.deepcopy(GOOD_CAPMAP)
    cap["product_capabilities"][0]["depends_on"] = ["cart"]  # catalog<->cart cycle
    proc, _, _ = _run(tmp_path, cap, copy.deepcopy(GOOD_MANIFEST))
    assert proc.returncode != 0
    assert "cycle" in proc.stdout.lower() or "acyclic" in proc.stdout.lower()


def test_validate_bad_timestamp(tmp_path):
    man = copy.deepcopy(GOOD_MANIFEST)
    man["generated_at"] = "not-a-date"
    proc, _, _ = _run(tmp_path, copy.deepcopy(GOOD_CAPMAP), man)
    assert proc.returncode != 0
    assert "iso" in proc.stdout.lower() or "timestamp" in proc.stdout.lower()


def test_validate_enum_whitespace_normalized(tmp_path):
    cap = copy.deepcopy(GOOD_CAPMAP)
    cap["capability_map"]["scale"]["expected_users"] = "< 100"  # cosmetic space
    proc, cm, _ = _run(tmp_path, cap, copy.deepcopy(GOOD_MANIFEST))
    assert proc.returncode == 0, proc.stdout + proc.stderr
    # comparison-only: the file on disk is NOT rewritten
    assert "< 100" in cm.read_text()
