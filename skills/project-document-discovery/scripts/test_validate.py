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


# Canonical valid v2 capability_map: 10 grounded clusters + the 10-boolean
# prior_art_triggers block (flags match the formulas over this classification).
V2_CLUSTERS = {
    "archetype": {"primary": "api-service"},
    "domain": {"audience": "b2c"},
    "regulatory": {"applies": True},
    "scale": {
        "concurrency": "high", "real_time": "near", "availability_target": "99.9",
        "geo_distribution": "single-region", "data_volume": "large",
    },
    "security": {"asvs_level": 2},
    "integrations": {"expected": True, "complexity": "complex"},
    "ui": {"has_ui": True, "complexity": "complex"},
    "data_ml": {"ml_involvement": "trains-from-scratch"},
    "infrastructure": {"deployment_model": "cloud"},
    "business": {"model": "saas", "platform": {"type": "none"}},
    "prior_art_triggers": {
        "code": True, "visual": True, "market_competitive": True, "user_research": True,
        "security": True, "ml": True, "regulatory": True, "scale": True,
        "integrations": True, "platform_ecosystem": False,
    },
}


def _capmap(**cluster_overrides):
    """A minimal schema-valid v2 capability-map; override capability_map clusters."""
    cm = copy.deepcopy(V2_CLUSTERS)
    cm.update(cluster_overrides)
    return {
        "capability_map": cm,
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
    doc = _capmap()
    cap = doc["product_capabilities"][0]
    cap["scope"] = "A" * 437  # no maxLength cap
    cap["owns"] = []  # minItems 0
    _valid(doc, CAPMAP_SCHEMA)


def test_capmap_schema_keeps_hard_constraints():
    bad_id = _capmap()
    bad_id["product_capabilities"][0]["id"] = "Bad_Id"
    _invalid(bad_id, CAPMAP_SCHEMA)

    missing = _capmap()
    del missing["product_capabilities"][0]["scope"]
    _invalid(missing, CAPMAP_SCHEMA)

    bad_archetype = _capmap(archetype={"primary": "not-a-real-archetype"})
    _invalid(bad_archetype, CAPMAP_SCHEMA)  # archetype.primary enum stays hard


# --- Cycle 2: manifest relaxations ---

def test_manifest_schema_accepts_relaxed():
    doc = _manifest(
        skills=[{
            "id": "alembic", "version": None, "source": None, "category": "ops",
            "purpose": "Manage database migrations for the project.",
            "requirements": ["generates alembic revisions", "runs upgrade/downgrade"],
            "resolved_id": None, "match_status": None,
        }],
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

# Pure-persona role entries (v5 shape: no skills/tools arrays).
ROLE_AUTHOR = {
    "id": "document-author", "name": "Document Author",
    "goal": "Produce high-quality, evidence-grounded project documents.",
    "persona": "Senior technical writer and engineer with deep domain expertise.",
    "model": "claude-sonnet-4-6",
    "resolved_id": None, "match_status": None,
}
ROLE_DOC_REVIEWER = {
    "id": "document-reviewer", "name": "Document Reviewer",
    "goal": "Gate-check project documents against their acceptance bar before approval.",
    "persona": "Senior staff engineer acting as an adversarial reviewer.",
    "model": "claude-sonnet-4-6",
    "resolved_id": None, "match_status": None,
}
ROLE_DESIGNER = {
    "id": "designer", "name": "Designer",
    "goal": "Produce structural, buildable design artifacts grounded in UX research.",
    "persona": "Senior product designer with UX research and interaction-design expertise.",
    "model": "claude-sonnet-4-6",
    "resolved_id": None, "match_status": None,
}
ROLE_DESIGN_REVIEWER = {
    "id": "design-reviewer", "name": "Design Reviewer",
    "goal": "Gate-check design artifacts for buildability, coverage, and accessibility before approval.",
    "persona": "Senior product-design lead acting as an adversarial reviewer.",
    "model": "claude-sonnet-4-6",
    "resolved_id": None, "match_status": None,
}

GOOD_CAPMAP = {
    "capability_map": copy.deepcopy(V2_CLUSTERS),
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
    "version": 2,
    "generated_at": "2026-06-25T00:00:00Z",
    "schema": "manifest/v1",
    "documents": [
        {
            "id": "prd", "title": "PRD", "type": "prd", "scope": "system",
            "capability": "docs", "archetype": "strategist",
            "roles": ["document-author", "document-reviewer"],
            "skills": ["authoring-prd", "reviewing-prd"],
            "depends_on": [], "account": None, "status": "active",
        },
        {
            "id": "feature-spec-catalog", "title": "Catalog Spec", "type": "feature-spec",
            "scope": "catalog", "capability": "docs", "archetype": "engineer",
            "roles": ["document-author", "document-reviewer"],
            "skills": ["authoring-feature-spec", "reviewing-feature-spec"],
            "depends_on": ["prd"], "account": None, "status": "active",
        },
    ],
    "capabilities": [],
    "roles": [copy.deepcopy(ROLE_AUTHOR), copy.deepcopy(ROLE_DOC_REVIEWER)],
    "skills": [], "tools": [], "amendments": [],
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
    cap["capability_map"]["scale"]["concurrency"] = "hi gh"  # cosmetic space
    proc, cm, _ = _run(tmp_path, cap, copy.deepcopy(GOOD_MANIFEST))
    assert proc.returncode == 0, proc.stdout + proc.stderr
    # comparison-only: the file on disk is NOT rewritten
    assert "hi gh" in cm.read_text()


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
    "capability_map": copy.deepcopy(V2_CLUSTERS),
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


def _doc(did, dtype, scope, cap, arch, roles, skills, deps):
    return {
        "id": did, "title": did, "type": dtype, "scope": scope,
        "capability": cap, "archetype": arch, "roles": roles,
        "skills": skills, "depends_on": deps, "account": None, "status": "active",
    }


AUTHOR_PAIR = ["document-author", "document-reviewer"]
DESIGNER_PAIR = ["designer", "design-reviewer"]


def _skills(kind):
    """Dual authoring+reviewing skills for a document type."""
    return [f"authoring-{kind}", f"reviewing-{kind}"]


GOLDEN_MANIFEST = {
    "version": 2, "generated_at": "2026-06-25T00:00:00Z", "schema": "manifest/v1",
    "documents": [
        # system docs
        _doc("prd", "prd", "system", "docs", "strategist", AUTHOR_PAIR, _skills("prd"), []),
        _doc("architecture-doc", "architecture-doc", "system", "docs", "engineer", AUTHOR_PAIR, _skills("architecture-doc"), ["prd"]),
        _doc("design-system", "design-system", "system", "design", "designer", DESIGNER_PAIR, _skills("design-system"), ["prd", "architecture-doc"]),
        _doc("user-flows", "user-flows", "system", "design", "designer", DESIGNER_PAIR, _skills("user-flows"), ["prd"]),
        _doc("system-wireframes", "wireframes", "system", "design", "designer", DESIGNER_PAIR, _skills("wireframes"), ["design-system", "user-flows"]),
        _doc("release-runbook", "release-runbook", "system", "docs", "engineer", AUTHOR_PAIR, _skills("release-runbook"), ["architecture-doc"]),
        _doc("eval-plan", "eval-plan", "system", "docs", "engineer", AUTHOR_PAIR, _skills("eval-plan"), ["prd"]),
        # signal-engine (complex, has_model, no UI)
        _doc("feature-spec-signal-engine", "feature-spec", "signal-engine", "docs", "engineer", AUTHOR_PAIR, _skills("feature-spec"), ["prd"]),
        _doc("data-model-signal-engine", "data-model", "signal-engine", "docs", "engineer", AUTHOR_PAIR, _skills("data-model"), ["feature-spec-signal-engine"]),
        _doc("api-spec-signal-engine", "api-spec", "signal-engine", "docs", "engineer", AUTHOR_PAIR, _skills("api-spec"), ["feature-spec-signal-engine", "data-model-signal-engine"]),
        _doc("technical-design-signal-engine", "technical-design", "signal-engine", "docs", "engineer", AUTHOR_PAIR, _skills("technical-design"), ["feature-spec-signal-engine", "architecture-doc", "api-spec-signal-engine", "data-model-signal-engine"]),
        _doc("model-card-signal-engine", "model-card", "signal-engine", "docs", "engineer", AUTHOR_PAIR, _skills("model-card"), ["eval-plan", "data-model-signal-engine"]),
        # dashboard (moderate, ui complex)
        _doc("feature-spec-dashboard", "feature-spec", "dashboard", "docs", "engineer", AUTHOR_PAIR, _skills("feature-spec"), ["prd"]),
        _doc("data-model-dashboard", "data-model", "dashboard", "docs", "engineer", AUTHOR_PAIR, _skills("data-model"), ["feature-spec-dashboard"]),
        _doc("api-spec-dashboard", "api-spec", "dashboard", "docs", "engineer", AUTHOR_PAIR, _skills("api-spec"), ["feature-spec-dashboard", "data-model-dashboard"]),
        _doc("user-flows-dashboard", "user-flows", "dashboard", "design", "designer", DESIGNER_PAIR, _skills("user-flows"), ["user-flows", "feature-spec-dashboard"]),
        _doc("wireframes-dashboard", "wireframes", "dashboard", "design", "designer", DESIGNER_PAIR, _skills("wireframes"), ["system-wireframes", "feature-spec-dashboard", "user-flows-dashboard"]),
        _doc("hi-fi-dashboard", "hi-fi", "dashboard", "design", "designer", DESIGNER_PAIR, _skills("hi-fi"), ["wireframes-dashboard", "design-system"]),
        _doc("technical-design-dashboard", "technical-design", "dashboard", "docs", "engineer", AUTHOR_PAIR, _skills("technical-design"), ["feature-spec-dashboard", "architecture-doc", "api-spec-dashboard", "data-model-dashboard"]),
        # accounts (simple, ui simple) -> no TDD, no hi-fi, no model-card
        _doc("feature-spec-accounts", "feature-spec", "accounts", "docs", "engineer", AUTHOR_PAIR, _skills("feature-spec"), ["prd"]),
        _doc("data-model-accounts", "data-model", "accounts", "docs", "engineer", AUTHOR_PAIR, _skills("data-model"), ["feature-spec-accounts"]),
        _doc("api-spec-accounts", "api-spec", "accounts", "docs", "engineer", AUTHOR_PAIR, _skills("api-spec"), ["feature-spec-accounts", "data-model-accounts"]),
        _doc("user-flows-accounts", "user-flows", "accounts", "design", "designer", DESIGNER_PAIR, _skills("user-flows"), ["user-flows", "feature-spec-accounts"]),
        _doc("wireframes-accounts", "wireframes", "accounts", "design", "designer", DESIGNER_PAIR, _skills("wireframes"), ["system-wireframes", "feature-spec-accounts", "user-flows-accounts"]),
    ],
    "capabilities": [],
    "roles": [
        copy.deepcopy(ROLE_AUTHOR), copy.deepcopy(ROLE_DOC_REVIEWER),
        copy.deepcopy(ROLE_DESIGNER), copy.deepcopy(ROLE_DESIGN_REVIEWER),
    ],
    "skills": [], "tools": [], "amendments": [],
}


def test_validate_golden_fixture_exit0(tmp_path):
    proc, _, _ = _run(tmp_path, copy.deepcopy(GOLDEN_CAPMAP), copy.deepcopy(GOLDEN_MANIFEST))
    assert proc.returncode == 0, proc.stdout + proc.stderr


# --- Cycle 11 (capability-map v2): strict v2 classification + prior_art_triggers ---


def test_v2_capmap_valid():
    _valid(_capmap(), CAPMAP_SCHEMA)


def test_v2_rejects_missing_prior_art_triggers():
    doc = _capmap()
    del doc["capability_map"]["prior_art_triggers"]
    _invalid(doc, CAPMAP_SCHEMA)


def test_v2_rejects_out_of_enum_platform_type():
    doc = _capmap(business={"model": "saas", "platform": {"type": "bogus-platform"}})
    _invalid(doc, CAPMAP_SCHEMA)


def test_v2_rejects_missing_scale_trigger_field():
    doc = _capmap()
    del doc["capability_map"]["scale"]["concurrency"]  # required [trigger] field
    _invalid(doc, CAPMAP_SCHEMA)


def test_v2_rejects_unknown_cluster_field():
    doc = _capmap()
    doc["capability_map"]["scale"]["concurency"] = "high"  # typo — strict cluster
    _invalid(doc, CAPMAP_SCHEMA)


def test_v2_rejects_dropped_team():
    doc = _capmap(team={"team_size": "small"})  # team removed in v2; strict map rejects
    _invalid(doc, CAPMAP_SCHEMA)


# --- Cycle 12 (capability-map v2): validator trigger formula-check ---

def test_validate_correct_triggers_pass(tmp_path):
    # GOOD_CAPMAP's prior_art_triggers match the formulas over its classification.
    proc, _, _ = _run(tmp_path, copy.deepcopy(GOOD_CAPMAP), copy.deepcopy(GOOD_MANIFEST))
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_validate_wrong_trigger_ml_fails(tmp_path):
    cap = copy.deepcopy(GOOD_CAPMAP)
    cap["capability_map"]["prior_art_triggers"]["ml"] = False  # ml_involvement != none -> must be True
    proc, _, _ = _run(tmp_path, cap, copy.deepcopy(GOOD_MANIFEST))
    assert proc.returncode != 0
    out = proc.stdout.lower()
    assert "prior-art-trigger" in out and "ml" in out


def test_validate_wrong_trigger_platform_fails(tmp_path):
    cap = copy.deepcopy(GOOD_CAPMAP)
    cap["capability_map"]["prior_art_triggers"]["platform_ecosystem"] = True  # platform.type none -> must be False
    proc, _, _ = _run(tmp_path, cap, copy.deepcopy(GOOD_MANIFEST))
    assert proc.returncode != 0
    assert "prior-art-trigger" in proc.stdout.lower()


# --- Cycle 13 (manifest review roles): roles pair shape + ref-integrity ---

def test_manifest_schema_rejects_role_with_skills():
    """A Role entry carrying the removed skills/tools fields is rejected."""
    doc = _manifest(roles=[{**copy.deepcopy(ROLE_AUTHOR), "skills": ["deep-research"]}])
    _invalid(doc, MANIFEST_SCHEMA)


def test_manifest_schema_rejects_singular_role_field():
    """The old singular `role` field is no longer an allowed Document property."""
    doc = _manifest(documents=[{
        "id": "prd", "title": "PRD", "type": "prd", "scope": "system",
        "capability": "docs", "archetype": "strategist", "role": "document-author",
        "skills": ["authoring-prd"], "depends_on": [], "account": None, "status": "active",
    }])
    _invalid(doc, MANIFEST_SCHEMA)


def test_manifest_schema_rejects_one_element_roles():
    """`roles` must hold exactly two ids (minItems/maxItems 2)."""
    doc = _manifest(documents=[{
        "id": "prd", "title": "PRD", "type": "prd", "scope": "system",
        "capability": "docs", "archetype": "strategist", "roles": ["document-author"],
        "skills": ["authoring-prd", "reviewing-prd"], "depends_on": [],
        "account": None, "status": "active",
    }])
    _invalid(doc, MANIFEST_SCHEMA)


def test_validate_unknown_role_id_fails(tmp_path):
    """A role id in document.roles absent from manifest.roles fails ref-integrity."""
    man = copy.deepcopy(GOOD_MANIFEST)
    man["documents"][0]["roles"] = ["document-author", "ghost-reviewer"]
    proc, _, _ = _run(tmp_path, copy.deepcopy(GOOD_CAPMAP), man)
    assert proc.returncode != 0
    out = proc.stdout.lower()
    assert "ref-integrity" in out and "ghost-reviewer" in out and "role" in out


def test_validate_archetype_pair_mismatch_fails(tmp_path):
    """A designer-archetype doc carrying the document-author pair fails role-pair."""
    man = copy.deepcopy(GOLDEN_MANIFEST)
    # design-system is a designer doc; force the wrong (author) pair.
    ds = next(d for d in man["documents"] if d["id"] == "design-system")
    ds["roles"] = ["document-author", "document-reviewer"]
    proc, _, _ = _run(tmp_path, copy.deepcopy(GOLDEN_CAPMAP), man)
    assert proc.returncode != 0
    assert "role-pair" in proc.stdout.lower()


# --- Cycle 14 (skill intent + resolution fields): purpose/requirements + resolved_id/match_status ---

SKILL_OK = {
    "id": "authoring-prd", "version": None, "source": None, "category": "authoring",
    "purpose": "Author the PRD from the approved request.",
    "requirements": ["evidences the problem", "sets measurable success metrics"],
    "resolved_id": None, "match_status": None,
}


def test_manifest_schema_accepts_skill_intent_and_resolution():
    """A skill with purpose + requirements + null resolution fields is valid."""
    _valid(_manifest(skills=[copy.deepcopy(SKILL_OK)]), MANIFEST_SCHEMA)


def test_manifest_schema_accepts_resolved_skill():
    """A resolved skill (match_status complete + resolved_id set) is schema-valid."""
    s = {**copy.deepcopy(SKILL_OK), "resolved_id": "authoring-prd", "match_status": "complete"}
    _valid(_manifest(skills=[s]), MANIFEST_SCHEMA)


def test_manifest_schema_rejects_skill_missing_purpose():
    s = {k: v for k, v in copy.deepcopy(SKILL_OK).items() if k != "purpose"}
    _invalid(_manifest(skills=[s]), MANIFEST_SCHEMA)


def test_manifest_schema_rejects_skill_empty_requirements():
    s = {**copy.deepcopy(SKILL_OK), "requirements": []}
    _invalid(_manifest(skills=[s]), MANIFEST_SCHEMA)


def test_manifest_schema_rejects_bad_match_status():
    s = {**copy.deepcopy(SKILL_OK), "match_status": "kinda"}
    _invalid(_manifest(skills=[s]), MANIFEST_SCHEMA)


def test_manifest_schema_rejects_role_missing_resolution():
    """A role lacking the required (null) resolution fields is rejected."""
    r = {k: v for k, v in copy.deepcopy(ROLE_AUTHOR).items() if k != "match_status"}
    _invalid(_manifest(roles=[r]), MANIFEST_SCHEMA)


def test_validate_resolution_complete_without_resolved_id_fails(tmp_path):
    """match_status complete with a null resolved_id fails the resolution check."""
    man = copy.deepcopy(GOOD_MANIFEST)
    man["skills"] = [{**copy.deepcopy(SKILL_OK), "match_status": "complete", "resolved_id": None}]
    proc, _, _ = _run(tmp_path, copy.deepcopy(GOOD_CAPMAP), man)
    assert proc.returncode != 0
    assert "resolution" in proc.stdout.lower()


def test_validate_resolution_none_with_resolved_id_fails(tmp_path):
    """match_status none with a non-null resolved_id fails the resolution check."""
    man = copy.deepcopy(GOOD_MANIFEST)
    man["skills"] = [{**copy.deepcopy(SKILL_OK), "match_status": "none", "resolved_id": "authoring-prd"}]
    proc, _, _ = _run(tmp_path, copy.deepcopy(GOOD_CAPMAP), man)
    assert proc.returncode != 0
    assert "resolution" in proc.stdout.lower()


def test_validate_resolution_partial_with_resolved_id_ok(tmp_path):
    """match_status partial WITH a resolved_id passes (names the skill to improve)."""
    man = copy.deepcopy(GOOD_MANIFEST)
    man["skills"] = [{**copy.deepcopy(SKILL_OK), "match_status": "partial", "resolved_id": "authoring-prd"}]
    proc, _, _ = _run(tmp_path, copy.deepcopy(GOOD_CAPMAP), man)
    assert proc.returncode == 0, proc.stdout + proc.stderr
