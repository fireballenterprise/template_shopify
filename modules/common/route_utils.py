"""Shared helpers for AI-tool command routing modules."""

from __future__ import annotations

import os
from pathlib import Path


def find_repo_root() -> Path:
    """Find repository root by locating properties.yml or repository markers."""
    current = Path.cwd()
    while current != current.parent:
        if (current / "properties.yml").exists():
            return current
        if (current / ".git").exists() or (current / "VERSION").exists():
            return current
        current = current.parent
    return Path.cwd()


def build_env(_repo_root: Path) -> dict[str, str]:
    """Build the subprocess environment for a routed command."""
    return os.environ.copy()
