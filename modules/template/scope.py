"""Shared include/exclude scope for /template push (this repo -> its parent template repo)."""

from __future__ import annotations

import subprocess
from pathlib import Path

from .ignore import load_ignore_patterns, matches_ignore

# Top-level directories eligible for push, mirroring the shared-tooling include list.
INCLUDE_DIRS = [
    "modules",
    ".github/instructions",
    ".github/prompts",
    ".claude/commands",
    ".claude/skills",
    ".clinerules/workflows",
]


def is_excluded(rel_path: Path, ignore_patterns: list[str]) -> bool:
    """Return True if rel_path (relative to repo root) must never be pushed.

    Cache/build artifacts are already excluded upstream of this check -- candidates come from
    `git ls-files`, which respects the repo's own `.gitignore`. This only checks this project's
    `template.ignore.yml`, so project-specific content a fork declares there (a business module, a
    personal-vault repo's topics/) never leaks upstream either; nothing is hardcoded here.
    """
    return matches_ignore(rel_path, ignore_patterns)


def iter_candidates(repo_root: Path) -> list[Path]:
    """Enumerate git-tracked files under INCLUDE_DIRS that survive is_excluded(), relative to repo_root."""
    existing_dirs = [d for d in INCLUDE_DIRS if (repo_root / d).is_dir()]
    if not existing_dirs:
        return []

    result = subprocess.run(
        ["git", "ls-files", "--", *existing_dirs], cwd=repo_root, capture_output=True, text=True, check=True
    )
    ignore_patterns = load_ignore_patterns(repo_root)
    results = [
        Path(line) for line in result.stdout.splitlines() if line and not is_excluded(Path(line), ignore_patterns)
    ]
    return sorted(results)
