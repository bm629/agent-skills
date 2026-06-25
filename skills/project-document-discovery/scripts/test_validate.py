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


# --- Cycle 10 (discovery-doc-fanout): impl_complexity + has_model fields ---

def test_capmap_accepts_impl_complexity_and_has_model():
    doc = _capmap()
    cap = doc["product_capabilities"][0]
    cap["impl_complexity"] = "complex"
    cap["has_model"] = True
    _valid(doc, CAPMAP_SCHEMA)


def test_capmap_rejects_bad_impl_complexity():
    doc = _capmap()
    doc["product_capabilities"][0]["impl_complexity"] = "trivial"  # out of enum
    _invalid(doc, CAPMAP_SCHEMA)


# Golden fixture: a small ML + UI project exercising EVERY new doc type at its
# correct scope with its DAG edges (manifest ids). Must pass validate.py exit 0.
# - signal-engine: complex + has_model, no UI -> technical-design + model-card
# - dashboard: moderate + ui complex -> technical-design + hi-fi + user-flows-{id}
# - accounts: simple + ui simple -> no technical-design, no hi-fi, no model-card

GOLDEN_CAPMAP = {
    "capability_map": {
        "archetype": {"primary": "api-service"},
        "ui": {"has_ui": True},
        "data_ml": {"has_ml_model": True},
        "scale": {"expected_users": "<100"},
    },
    "product_capabilities": [
        {
            "id": "signal-engine", "name": "Signal Engine",
            "scope": "Generates trading signals; does NOT execute trades.",
            "subdomain": "core", "owns": ["signal"],
            "has_ui": False, "has_api": True, "has_persistence": True,
            "has_model": True, "impl_complexity": "complex", "depends_on": [],
        },
        {
            "id": "dashboard", "name": "Dashboard",
            "scope": "Visualizes signals and positions; does NOT compute them.",
            "subdomain": "supporting", "owns": ["view-config"],
            "has_ui": True, "has_api": True, "has_persistence": True,
            "ui_complexity": "complex", "impl_complexity": "moderate",
            "depends_on": ["signal-engine"],
        },
        {
            "id": "accounts", "name": "Accounts",
            "scope": "Manages user accounts; does NOT handle billing.",
            "subdomain": "generic", "owns": ["account"],
            "has_ui": True, "has_api": True, "has_persistence": True,
            "ui_complexity": "simple", "impl_complexity": "simple",
            "depends_on": [],
        },
    ],
    "_meta": {"generated_at": "2026-06-25T00:00:00Z"},
}


def _doc(did, dtype, scope, cap, arch, role, skills, deps):
    return {
        "id": did, "title": did, "type": dtype, "scope": scope,
        "capability": cap, "archetype": arch, "role": role,
        "skills": skills, "depends_on": deps, "account": None, "status": "active",
    }


GOLDEN_MANIFEST = {
    "version": 1, "generated_at": "2026-06-25T00:00:00Z", "schema": "manifest/v1",
    "documents": [
        # system docs
        _doc("prd", "prd", "system", "docs", "strategist", "document-author", ["authoring-prd"], []),
        _doc("architecture-doc", "architecture-doc", "system", "docs", "engineer", "document-author", ["authoring-architecture-doc"], ["prd"]),
        _doc("design-system", "design-system", "system", "design", "designer", "designer", ["authoring-design-system"], ["prd", "architecture-doc"]),
        _doc("user-flows", "user-flows", "system", "design", "designer", "designer", ["authoring-user-flows"], ["prd"]),
        _doc("system-wireframes", "wireframes", "system", "design", "designer", "designer", ["authoring-wireframes"], ["design-system", "user-flows"]),
        _doc("release-runbook", "release-runbook", "system", "docs", "engineer", "document-author", ["authoring-release-runbook"], ["architecture-doc"]),
        _doc("eval-plan", "eval-plan", "system", "docs", "engineer", "document-author", ["authoring-eval-plan"], ["prd"]),
        # signal-engine (complex, has_model, no UI)
        _doc("feature-spec-signal-engine", "feature-spec", "signal-engine", "docs", "engineer", "document-author", ["authoring-feature-spec"], ["prd"]),
        _doc("data-model-signal-engine", "data-model", "signal-engine", "docs", "engineer", "document-author", ["authoring-data-model"], ["feature-spec-signal-engine"]),
        _doc("api-spec-signal-engine", "api-spec", "signal-engine", "docs", "engineer", "document-author", ["authoring-api-spec"], ["feature-spec-signal-engine", "data-model-signal-engine"]),
        _doc("technical-design-signal-engine", "technical-design", "signal-engine", "docs", "engineer", "document-author", ["authoring-technical-design"], ["feature-spec-signal-engine", "architecture-doc", "api-spec-signal-engine", "data-model-signal-engine"]),
        _doc("model-card-signal-engine", "model-card", "signal-engine", "docs", "engineer", "document-author", ["authoring-model-card"], ["eval-plan", "data-model-signal-engine"]),
        # dashboard (moderate, ui complex)
        _doc("feature-spec-dashboard", "feature-spec", "dashboard", "docs", "engineer", "document-author", ["authoring-feature-spec"], ["prd"]),
        _doc("data-model-dashboard", "data-model", "dashboard", "docs", "engineer", "document-author", ["authoring-data-model"], ["feature-spec-dashboard"]),
        _doc("api-spec-dashboard", "api-spec", "dashboard", "docs", "engineer", "document-author", ["authoring-api-spec"], ["feature-spec-dashboard", "data-model-dashboard"]),
        _doc("user-flows-dashboard", "user-flows", "dashboard", "design", "designer", "designer", ["authoring-user-flows"], ["user-flows", "feature-spec-dashboard"]),
        _doc("wireframes-dashboard", "wireframes", "dashboard", "design", "designer", "designer", ["authoring-wireframes"], ["system-wireframes", "feature-spec-dashboard", "user-flows-dashboard"]),
        _doc("hi-fi-dashboard", "hi-fi", "dashboard", "design", "designer", "designer", ["authoring-hi-fi"], ["wireframes-dashboard", "design-system"]),
        _doc("technical-design-dashboard", "technical-design", "dashboard", "docs", "engineer", "document-author", ["authoring-technical-design"], ["feature-spec-dashboard", "architecture-doc", "api-spec-dashboard", "data-model-dashboard"]),
        # accounts (simple, ui simple) -> no TDD, no hi-fi, no model-card
        _doc("feature-spec-accounts", "feature-spec", "accounts", "docs", "engineer", "document-author", ["authoring-feature-spec"], ["prd"]),
        _doc("data-model-accounts", "data-model", "accounts", "docs", "engineer", "document-author", ["authoring-data-model"], ["feature-spec-accounts"]),
        _doc("api-spec-accounts", "api-spec", "accounts", "docs", "engineer", "document-author", ["authoring-api-spec"], ["feature-spec-accounts", "data-model-accounts"]),
        _doc("user-flows-accounts", "user-flows", "accounts", "design", "designer", "designer", ["authoring-user-flows"], ["user-flows", "feature-spec-accounts"]),
        _doc("wireframes-accounts", "wireframes", "accounts", "design", "designer", "designer", ["authoring-wireframes"], ["system-wireframes", "feature-spec-accounts", "user-flows-accounts"]),
    ],
    "capabilities": [], "roles": [], "skills": [], "tools": [], "amendments": [],
}


def test_validate_golden_fixture_exit0(tmp_path):
    proc, _, _ = _run(tmp_path, copy.deepcopy(GOLDEN_CAPMAP), copy.deepcopy(GOLDEN_MANIFEST))
    assert proc.returncode == 0, proc.stdout + proc.stderr
