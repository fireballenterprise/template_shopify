"""Exclusion rules for /template pull's local clobber-copy and /template push's scope.

No hardcoded file list here: cache/build artifacts are already skipped because both directions
read `git ls-files` (which respects the source repo's own `.gitignore`), and everything else
project-specific (`properties.yml`, `README.md`, business modules, personal-vault content, ...)
is declared once in `template.ignore.yml`, including that file's own name so it protects itself.
"""

from __future__ import annotations

import fnmatch
from pathlib import Path

import yaml


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
