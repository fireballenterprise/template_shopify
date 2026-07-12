"""
List every version tag published on upstream Shopify/dawn, latest highlighted.

Compares against the tag `dawn_vanilla` is currently on, so you know what to pass as the
`version` input on the "Upgrade" GitHub Actions workflow (.github/workflows/upgrade.yml) —
that workflow deliberately fetches a single pinned tag rather than every upstream tag, to avoid
colliding with our own same-named release tags (see upgrade.yml for details).

Usage:
    uv run --no-sync python -m modules.dawn.list
    uv run --no-sync invoke dawn.list
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from ..common import cli as click
from ..common.properties import get_repo_root
from ..common.utils import error, info

UPSTREAM_URL = "https://github.com/Shopify/dawn.git"
_TAG_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")


def _fetch_tags() -> list[str]:
    """Return every semver tag published on upstream Shopify/dawn (git ls-remote — no clone/auth needed)."""
    result = subprocess.run(
        ["git", "ls-remote", "--tags", "--refs", UPSTREAM_URL],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        error(f"Failed to list tags from {UPSTREAM_URL}: {result.stderr}")

    tags = []
    for line in result.stdout.splitlines():
        ref = line.rsplit("/", maxsplit=1)[-1]
        if _TAG_RE.match(ref):
            tags.append(ref)
    return tags


def _sort_key(tag: str) -> tuple[int, int, int]:
    """Numeric sort key for a "vX.Y.Z" tag, so v10.0.0 sorts after v9.0.0."""
    match = _TAG_RE.match(tag)
    return (int(match.group(1)), int(match.group(2)), int(match.group(3)))


def _current_dawn_vanilla_tag(repo_root: Path) -> str | None:
    """Return the latest tag reachable from the local dawn_vanilla branch, if resolvable."""
    result = subprocess.run(
        ["git", "-C", str(repo_root), "describe", "--tags", "--abbrev=0", "dawn_vanilla"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() or None


def main() -> None:
    """List every version tag published on upstream Shopify/dawn, latest highlighted."""
    info("Fetching tags from upstream Shopify/dawn...")
    tags = _fetch_tags()
    if not tags:
        error("No version tags found on upstream Shopify/dawn.")

    tags.sort(key=_sort_key)
    latest = tags[-1]
    current = _current_dawn_vanilla_tag(get_repo_root())

    click.echo()
    for tag in tags:
        markers = []
        if tag == current:
            markers.append("current dawn_vanilla")
        if tag == latest:
            markers.append("latest")
        suffix = f"  ← {', '.join(markers)}" if markers else ""
        click.echo(f"  {tag}{suffix}")
    click.echo()

    if current == latest:
        click.echo(f"dawn_vanilla is already at {latest} (latest upstream).")
    else:
        click.echo(f"dawn_vanilla is at {current or 'unknown'}; latest upstream is {latest}.")
        click.echo(f'Run the "Upgrade" GitHub Actions workflow with version="{latest}" to sync,')
        click.echo("then `uv run --no-sync invoke dawn.upgrade` to merge it into a feature branch.")


if __name__ == "__main__":
    main()
