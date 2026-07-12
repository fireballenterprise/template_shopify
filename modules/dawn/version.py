"""
Print the Dawn theme version currently checked out on this branch.

Reads `config/settings_schema.json`'s `theme_info.theme_version` — the same field Shopify's
theme editor reads to show the theme version in the admin. This can drift from what
`dawn_vanilla` is tagged at (see `dawn.list`) if `development` picked up version-bumping content
some other way than a `dawn_vanilla` merge.

Usage:
    uv run --no-sync python -m modules.dawn.version
    uv run --no-sync invoke dawn.version
"""

from __future__ import annotations

import json

from ..common import cli as click
from ..common.properties import get_repo_root
from ..common.utils import error


def parse_theme_version(schema_json: str) -> str:
    """Return theme_info.theme_version from settings_schema.json contents (public: upgrade.py reuses it)."""
    schema = json.loads(schema_json)
    for block in schema:
        if isinstance(block, dict) and block.get("name") == "theme_info":
            version = block.get("theme_version")
            if version:
                return version
            break
    error("theme_info.theme_version not found in settings_schema.json contents")


def _theme_version() -> str:
    """Return theme_info.theme_version from config/settings_schema.json."""
    path = get_repo_root() / "config" / "settings_schema.json"
    if not path.is_file():
        error(f"settings_schema.json not found at {path}")

    return parse_theme_version(path.read_text(encoding="utf-8"))


def main() -> None:
    """Print the Dawn theme version currently checked out, per config/settings_schema.json."""
    click.echo(f"Dawn v{_theme_version()} (config/settings_schema.json theme_info.theme_version)")


if __name__ == "__main__":
    main()
