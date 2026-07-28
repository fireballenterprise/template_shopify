"""
Parse `.github/prompts/*.prompt.md` — the source of truth for all slash commands — into a
structured command list used by modules/hermes/sync.py.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

from .route_utils import find_repo_root

REPO_ROOT = find_repo_root()
PROMPTS_DIR = REPO_ROOT / ".github" / "prompts"


class PromptCommand:  # pylint: disable=too-many-instance-attributes,too-few-public-methods
    """Parsed representation of one .github/prompts/*.prompt.md file."""

    def __init__(self, path: Path) -> None:
        self.path = path
        # name uses underscores (Python identifier), slug preserves hyphens (for r- prefix)
        self.slug: str = path.stem.replace(".prompt", "")
        self.name: str = self.slug.replace("-", "_")
        self.description: str = ""
        self.argument_hint: str = ""
        self.exec_line: str = ""
        self.body: str = ""
        self._parse()

    def _parse(self) -> None:
        text = self.path.read_text(encoding="utf-8")
        parts = text.split("---", 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            self.body = parts[2].strip()
            try:
                fm: dict = yaml.safe_load(fm_text) or {}
            except yaml.YAMLError:
                fm = {}
            self.description = str(fm.get("description", ""))
            self.argument_hint = str(fm.get("argument-hint", ""))
        else:
            self.body = text.strip()

        # Find exec line: line starting with !`
        exec_match = re.search(r"^!`([^`]+)`", self.body, re.MULTILINE)
        if exec_match:
            self.exec_line = exec_match.group(1).strip()


def load_commands() -> list[PromptCommand]:
    """Load and parse all .github/prompts/*.prompt.md files, deduplicating by name."""
    files = sorted(PROMPTS_DIR.glob("*.prompt.md"))
    seen: set[str] = set()
    unique: list[PromptCommand] = []
    for path in files:
        cmd = PromptCommand(path)
        if cmd.name in seen:
            # Warn only if descriptions differ — could indicate accidental divergence
            existing = next(c for c in unique if c.name == cmd.name)
            if existing.description != cmd.description:
                print(
                    f"  ⚠️  Duplicate '{cmd.name}' with differing descriptions "
                    f"({cmd.slug!r} vs {existing.slug!r}) — keeping {existing.slug!r}",
                    file=sys.stderr,
                )
            continue
        seen.add(cmd.name)
        unique.append(cmd)
    return unique
