"""Exclusion rules for /template pull's local clobber-copy."""

from __future__ import annotations

import fnmatch
from pathlib import Path

import yaml

# Root-only entries -- never pulled down from the template repo, regardless of template.ignore.yml.
HARD_EXCLUDE_ROOT_NAMES = {
    "properties.yml",
    "properties.yml.example",
    "README.md",
    "LICENSE",
    "pyproject.toml",
    "uv.lock",
    "VERSION",
    "template.ignore.yml",
}

# Cache/build artifact names -- excluded wherever they occur in a path, not just at the root.
HARD_EXCLUDE_ANYWHERE_NAMES = {
    ".git",
    ".venv",
    "__pycache__",
    ".ruff_cache",
    "logs",
    "tmp",
}

# One-off nested files, matched by their full relative path.
HARD_EXCLUDE_EXACT_PATHS = {
    ".claude/settings.local.json",
}


def is_hard_excluded(rel_path: Path) -> bool:
    """Return True if rel_path must never be touched by /template pull, ignore file aside."""
    posix = rel_path.as_posix()
    parts = rel_path.parts
    if posix in HARD_EXCLUDE_EXACT_PATHS:
        return True
    if parts and parts[0] in HARD_EXCLUDE_ROOT_NAMES:
        return True
    return any(part in HARD_EXCLUDE_ANYWHERE_NAMES for part in parts)


def load_ignore_patterns(repo_root: Path) -> list[str]:
    """Load this project's `template.ignore.yml` `exclude:` list (empty if the file is missing)."""
    ignore_file = repo_root / "template.ignore.yml"
    if not ignore_file.is_file():
        return []
    data = yaml.safe_load(ignore_file.read_text(encoding="utf-8")) or {}
    return list(data.get("exclude") or [])


def matches_ignore(rel_path: Path, patterns: list[str]) -> bool:
    """Return True if rel_path matches a `template.ignore.yml` entry (prefix or glob pattern)."""
    posix = rel_path.as_posix()
    for pattern in patterns:
        cleaned = pattern.rstrip("/")
        if posix == cleaned or posix.startswith(f"{cleaned}/"):
            return True
        if fnmatch.fnmatch(posix, pattern):
            return True
    return False
