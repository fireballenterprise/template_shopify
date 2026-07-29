"""Verify .github/prompts/ is mirrored into .claude/commands/, .claude/skills/, and .clinerules/workflows/."""

from __future__ import annotations

from pathlib import Path

from ..common import cli as click
from ..common.properties import get_repo_local
from ..common.utils import error, success


def _prompt_names(repo_path: Path) -> set[str]:
    """Return the command names sourced from .github/prompts/*.prompt.md."""
    prompts_dir = repo_path / ".github" / "prompts"
    return {p.name.removesuffix(".prompt.md") for p in prompts_dir.glob("*.prompt.md")}


def _command_names(repo_path: Path) -> set[str]:
    """Return the command names mirrored into .claude/commands/*.md."""
    commands_dir = repo_path / ".claude" / "commands"
    return {p.stem for p in commands_dir.glob("*.md")}


def _skill_names(repo_path: Path) -> set[str]:
    """Return the command names mirrored into .claude/skills/*/SKILL.md."""
    skills_dir = repo_path / ".claude" / "skills"
    return {p.parent.name for p in skills_dir.glob("*/SKILL.md")}


def _clinerules_names(repo_path: Path) -> set[str]:
    """Return the command names mirrored into .clinerules/workflows/*.md."""
    workflows_dir = repo_path / ".clinerules" / "workflows"
    return {p.stem for p in workflows_dir.glob("*.md")}


def _report_diff(label: str, expected: set[str], actual: set[str]) -> bool:
    """Print any mismatch between the prompt set and a mirror's set; return whether they match."""
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if not missing and not extra:
        return True
    if missing:
        click.echo(f"  Missing from {label}: {', '.join(missing)}", err=True)
    if extra:
        click.echo(f"  Orphaned in {label} (no matching prompt): {', '.join(extra)}", err=True)
    return False


@click.command()
def main() -> None:
    """Verify every .github/prompts/*.prompt.md has a matching mirror in the other three command dirs."""
    repo_path = get_repo_local()
    prompts = _prompt_names(repo_path)

    click.echo(f"Checking {len(prompts)} prompt(s) are mirrored into commands, skills, and clinerules...")

    mirrors = {
        "commands": _command_names(repo_path),
        "skills": _skill_names(repo_path),
        "clinerules": _clinerules_names(repo_path),
    }

    in_sync = True
    for label, actual in mirrors.items():
        if not _report_diff(label, prompts, actual):
            in_sync = False

    if not in_sync:
        error("Command mirrors are out of sync — see .github/instructions/prompts.instructions.md.")

    success("All prompt mirrors are in sync")


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
