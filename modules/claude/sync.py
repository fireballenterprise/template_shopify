"""
Sync .claude/commands/ from .github/prompts/*.prompt.md source of truth.

By default only writes NEW commands (files that don't exist yet).
Use --force to overwrite existing hand-crafted command files.

Usage:
    uv run python -m modules.claude.sync   # additive only
    uv run --no-sync invoke claude.sync              # additive only
    uv run --no-sync invoke claude.sync --force      # overwrite all
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from ..common import cli as click
from ..common.properties import get_repo_root
from ..common.utils import success


@dataclass
class _PromptCommand:
    """Parsed representation of one .github/prompts/*.prompt.md file."""

    slug: str
    description: str
    body: str


def _load_commands(prompts_dir: Path) -> list[_PromptCommand]:
    """Parse every .prompt.md file in prompts_dir into a _PromptCommand."""
    commands = []
    for path in sorted(prompts_dir.glob("*.prompt.md")):
        _, frontmatter_text, body = path.read_text(encoding="utf-8").split("---", 2)
        frontmatter = yaml.safe_load(frontmatter_text) or {}
        commands.append(
            _PromptCommand(
                slug=path.stem.replace(".prompt", ""),
                description=frontmatter.get("description", ""),
                body=body.strip(),
            )
        )
    return commands


def _command_content(command: _PromptCommand) -> str:
    """Build a minimal .claude/commands/*.md file for a new command."""
    header = (
        f"---\ndescription: {command.description}\nsubtask: false\nagent: general\nslash_command: /{command.slug}\n---"
    )
    return f"{header}\n\n{command.body}\n" if command.body else f"{header}\n"


def main(force: bool = False) -> None:
    """Sync .claude/commands/ from .github/prompts/ source of truth."""
    repo_root = get_repo_root()
    prompts_dir = repo_root / ".github" / "prompts"
    commands_dir = repo_root / ".claude" / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)

    written = skipped = 0
    for command in _load_commands(prompts_dir):
        out = commands_dir / f"{command.slug}.md"
        if out.exists() and not force:
            click.echo(f"  skip  {command.slug}.md (exists — use --force to overwrite)")
            skipped += 1
        else:
            out.write_text(_command_content(command), encoding="utf-8")
            click.echo(f"  write {command.slug}.md")
            written += 1

    success(f"Synced {written} command(s) -> .claude/commands/ ({skipped} skipped)")
    if written:
        click.echo("Note: newly written commands only have a minimal description header —")
        click.echo("add allowed-tools/argument-hint by hand if the command executes a shell task.")


if __name__ == "__main__":
    main()
