"""Verify .github/prompts/ is mirrored into .claude/commands/, .claude/skills/, and .clinerules/workflows/."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _prompt_slugs() -> set[str]:
    return {p.name.removesuffix(".prompt.md") for p in (REPO_ROOT / ".github" / "prompts").glob("*.prompt.md")}


def _command_slugs() -> set[str]:
    return {p.stem for p in (REPO_ROOT / ".claude" / "commands").glob("*.md")}


def _skill_slugs() -> set[str]:
    return {p.parent.name for p in (REPO_ROOT / ".claude" / "skills").glob("*/SKILL.md")}


def _clinerules_slugs() -> set[str]:
    return {p.stem for p in (REPO_ROOT / ".clinerules" / "workflows").glob("*.md")}


def _assert_mirrored(label: str, expected: set[str], actual: set[str]) -> None:
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    assert not missing and not extra, f"{label} out of sync — missing={missing} extra={extra}"


def test_claude_commands_mirror_prompts() -> None:
    _assert_mirrored("`.claude/commands/`", _prompt_slugs(), _command_slugs())


def test_claude_skills_mirror_prompts() -> None:
    _assert_mirrored("`.claude/skills/`", _prompt_slugs(), _skill_slugs())


def test_clinerules_workflows_mirror_prompts() -> None:
    _assert_mirrored("`.clinerules/workflows/`", _prompt_slugs(), _clinerules_slugs())
