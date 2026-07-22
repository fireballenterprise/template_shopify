"""Shared include/exclude scope for /template push (this repo -> its parent template repo)."""

from __future__ import annotations

from pathlib import Path

# Top-level directories eligible for push, mirroring the shared-tooling include list.
INCLUDE_DIRS = [
    "modules",
    ".github/instructions",
    ".github/prompts",
    ".claude/commands",
    ".clinerules/workflows",
    ".opencode/command",
    ".agents/skills",
]

# Repo-root-only entries (never push these top-level files/dirs).
ALWAYS_EXCLUDE_ROOT_NAMES = {
    "properties.yml",
    "README.md",
    "LICENSE",
    "pyproject.toml",
    "uv.lock",
    "active_topic.yml",
    "topics",
    "screenshots",
}

# Cache/build artifact names -- excluded wherever they occur in a path, not just at the root
# (e.g. modules/template/__pycache__/ must be caught, not just a top-level __pycache__/).
ALWAYS_EXCLUDE_ANYWHERE_NAMES = {
    ".git",
    ".venv",
    "__pycache__",
    ".ruff_cache",
    "logs",
    "tmp",
}

# One-off nested files, matched by their full relative path.
ALWAYS_EXCLUDE_EXACT_PATHS = {
    ".claude/settings.local.json",
}

# Shopify/Dawn theme-specific module directories -- never push these; template_python is a
# generic Python template and has no notion of a Shopify theme.
BUSINESS_DIRS = {
    "modules/dawn",
    "modules/shopify",
}

# Shopify/Dawn/Fireball theme-specific instruction files -- never push these.
BUSINESS_INSTRUCTION_FILES = {
    ".github/instructions/dawn.instructions.md",
    ".github/instructions/shopify.instructions.md",
    ".github/instructions/fireball.instructions.md",
}

# Filename stems tied to the Shopify/Dawn theme commands -- excluded across every command dir
# (.github/prompts, .claude/commands, .clinerules/workflows, .opencode/command).
BUSINESS_COMMAND_STEMS = {
    "dawn",
    "shopify",
}


def is_excluded(rel_path: Path) -> bool:
    """Return True if rel_path (relative to repo root) must never be pushed."""
    posix = rel_path.as_posix()
    parts = rel_path.parts

    if posix in ALWAYS_EXCLUDE_EXACT_PATHS:
        return True
    if parts and parts[0] in ALWAYS_EXCLUDE_ROOT_NAMES:
        return True
    if any(part in ALWAYS_EXCLUDE_ANYWHERE_NAMES for part in parts):
        return True
    if any(posix == d or posix.startswith(f"{d}/") for d in BUSINESS_DIRS):
        return True
    if posix in BUSINESS_INSTRUCTION_FILES:
        return True

    stem = rel_path.name.split(".")[0]
    return stem in BUSINESS_COMMAND_STEMS


def iter_candidates(repo_root: Path) -> list[Path]:
    """Enumerate all files under INCLUDE_DIRS that survive is_excluded(), relative to repo_root."""
    results: list[Path] = []
    for include_dir in INCLUDE_DIRS:
        base = repo_root / include_dir
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if path.is_dir():
                continue
            rel = path.relative_to(repo_root)
            if not is_excluded(rel):
                results.append(rel)
    return results
