"""Every shipped skill's `description` fits the platform's 1,024-character cap.

Origin: the cap fails at INSTALL, not at review — a description over it is truncated by the
platform, and what a router reads is then a sentence that stops mid-clause. Two prior-art packages
guarded it, each for its OWN `SKILL.md` only, so a pair's reviewing half went unmeasured while its
producer's guard reported green. Sweeping the directory found SIX skills over the cap, one of them
a prior-art reviewer that had shipped that way.

Repo-level rather than per-package for the reason the per-package version failed: the invariant is
a property of every skill this repo ships, and a guard written once per package is a guard that
covers whichever halves someone remembered.
"""

from __future__ import annotations

import pathlib

import pytest
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILLS = sorted(ROOT.glob("skills/*/SKILL.md"))

#: The agentskills.io listing cap. A description longer than this is silently cut.
CAP = 1024


def _description(path: pathlib.Path) -> str:
    """One skill's description, whitespace-collapsed as the platform reads it.

    Args:
        path: The `SKILL.md` to read.

    Returns:
        The description with folded newlines joined, or the empty string where none is declared.

    Raises:
        AssertionError: If the frontmatter block is missing or does not parse as a mapping.
    """
    parts = path.read_text(encoding="utf-8").split("---", 2)
    assert len(parts) >= 3, f"{path}: no frontmatter block"
    front = yaml.safe_load(parts[1])
    assert isinstance(front, dict), f"{path}: frontmatter is not a mapping"
    return " ".join(str(front.get("description") or "").split())


def test_the_sweep_finds_every_shipped_skill():
    """A directory glob that matches nothing passes every assertion below it."""
    assert len(SKILLS) > 50, len(SKILLS)


@pytest.mark.parametrize("path", SKILLS, ids=lambda p: p.parent.name)
def test_the_description_fits_the_cap(path):
    desc = _description(path)
    assert desc, f"{path.parent.name}: no description"
    assert len(desc) <= CAP, f"{path.parent.name}: {len(desc)} > {CAP}"
