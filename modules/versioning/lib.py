"""
Check pyproject.toml [project.dependencies] against the latest published releases.

Only updates the version locks in pyproject.toml — does NOT install anything.
Run `uv run --no-sync invoke uv.upgrade` afterward to install the new versions.

Usage:
    uv run --no-sync python -m modules.versioning.lib
    uv run --no-sync invoke versioning.libs
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import tomlkit

from ..common import cli as click
from ..common.properties import get_repo_root
from ..common.utils import error, info, success

_DEPENDENCY_RE = re.compile(r"^([a-zA-Z0-9_-]+)\s*([~=><]+)\s*([\d.]+)")


def _get_installed_packages(repo_root: Path) -> list[dict]:
    """Return installed packages via `uv pip list --format json`."""
    result = subprocess.run(
        ["uv", "pip", "list", "--format", "json"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        error(f"Failed to list installed packages: {result.stderr}")
    return json.loads(result.stdout) if result.stdout else []


def _get_outdated_packages(repo_root: Path) -> list[dict]:
    """Return outdated packages via `uv pip list --outdated --format json`."""
    result = subprocess.run(
        ["uv", "pip", "list", "--outdated", "--format", "json"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        error(f"Failed to check for outdated packages: {result.stderr}")
    return json.loads(result.stdout) if result.stdout else []


def _load_pyproject(repo_root: Path) -> tuple[tomlkit.TOMLDocument, Path]:
    """Load pyproject.toml with tomlkit to preserve formatting."""
    pyproject_path = repo_root / "pyproject.toml"
    if not pyproject_path.exists():
        error(f"pyproject.toml not found at {pyproject_path}")
    with pyproject_path.open(encoding="utf-8") as f:
        return tomlkit.load(f), pyproject_path


def _parse_dependency(dep_string: str) -> dict | None:
    """Parse a dependency string into name/operator/version.

    Example: "ruff~=0.15.4" -> {"name": "ruff", "operator": "~=", "version": "0.15.4"}
    """
    match = _DEPENDENCY_RE.match(dep_string)
    if not match:
        return None
    return {"name": match.group(1), "operator": match.group(2), "version": match.group(3)}


def _find_updates(toml_doc: tomlkit.TOMLDocument, outdated: list[dict], installed: list[dict]) -> list[dict]:
    """Find [project.dependencies] entries with a newer version available than what's pinned."""
    outdated_lookup = {pkg["name"].lower(): pkg["latest_version"] for pkg in outdated}
    installed_lookup = {pkg["name"].lower(): pkg["version"] for pkg in installed}

    deps_list = toml_doc.get("project", {}).get("dependencies", [])
    updates = []
    for index, dep_string in enumerate(deps_list):
        parsed = _parse_dependency(dep_string)
        if not parsed:
            continue
        pkg_lower = parsed["name"].lower()
        latest = outdated_lookup.get(pkg_lower) or installed_lookup.get(pkg_lower)
        if latest and latest != parsed["version"]:
            updates.append(
                {
                    "package": parsed["name"],
                    "operator": parsed["operator"],
                    "current": parsed["version"],
                    "latest": latest,
                    "index": index,
                }
            )
    return updates


def _display_updates_table(updates: list[dict]) -> None:
    """Print a Package | Current | Latest table."""
    pkg_width = max(len("Package"), *(len(u["package"]) for u in updates))
    current_width = max(len("Current"), *(len(u["current"]) for u in updates))
    latest_width = max(len("Latest"), *(len(u["latest"]) for u in updates))

    def border(left: str, mid: str, right: str) -> str:
        return f"{left}{'─' * (pkg_width + 2)}{mid}{'─' * (current_width + 2)}{mid}{'─' * (latest_width + 2)}{right}"

    click.echo(border("╭", "┬", "╮"))
    click.echo(f"│ {'Package'.ljust(pkg_width)} │ {'Current'.ljust(current_width)} │ {'Latest'.ljust(latest_width)} │")
    click.echo(border("├", "┼", "┤"))
    for update in updates:
        click.echo(
            f"│ {update['package'].ljust(pkg_width)} │ {update['current'].ljust(current_width)} │ "
            f"{update['latest'].ljust(latest_width)} │"
        )
    click.echo(border("╰", "┴", "╯"))


def _apply_updates(toml_doc: tomlkit.TOMLDocument, updates: list[dict]) -> None:
    """Rewrite each updated dependency string in place, preserving its operator."""
    deps_list = toml_doc["project"]["dependencies"]
    for update in updates:
        deps_list[update["index"]] = f"{update['package']}{update['operator']}{update['latest']}"


@click.command()
@click.option("--dry-run", is_flag=True, help="Show available updates without writing changes")
@click.option("--yes", "-y", "no_confirm", is_flag=True, help="Skip the confirmation prompt")
def main(dry_run: bool = False, no_confirm: bool = False) -> None:
    """Check pyproject.toml dependencies against their latest releases and update version locks."""
    info("Checking pyproject.toml dependencies for available updates...")
    repo_root = get_repo_root()
    installed = _get_installed_packages(repo_root)
    outdated = _get_outdated_packages(repo_root)
    toml_doc, pyproject_path = _load_pyproject(repo_root)
    updates = _find_updates(toml_doc, outdated, installed)

    if not updates:
        success("All pyproject.toml dependencies are already at their latest version.")
        return

    click.echo(f"\n{len(updates)} dependencies have newer versions available:\n")
    _display_updates_table(updates)

    if dry_run:
        click.echo("\nDry run: no changes made.")
        return

    if not no_confirm and not click.confirm(f"\nUpdate {len(updates)} version lock(s) in pyproject.toml?"):
        click.echo("Cancelled.")
        return

    _apply_updates(toml_doc, updates)
    with pyproject_path.open("w", encoding="utf-8") as f:
        tomlkit.dump(toml_doc, f)

    success(f"Updated {len(updates)} version lock(s) in pyproject.toml")
    click.echo("Run `uv run --no-sync invoke uv.upgrade` to install the new versions.")


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
