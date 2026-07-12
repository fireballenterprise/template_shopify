"""
Merge the upgraded dawn_vanilla branch into a feature branch for conflict resolution.

Assumes the "Upgrade" GitHub Actions workflow (.github/workflows/upgrade.yml) has already synced
`dawn_vanilla` to the target upstream version — the target is whatever `origin/dawn_vanilla`
contains, read from its `config/settings_schema.json`, so there's no version argument. If a
feature branch is already checked out it merges into that; from `development`/`main`/
`dawn_vanilla` it cuts (or reuses) `upgrade/dawn-vanilla-v<version>` off `origin/development`.
Real conflicts with Fireball customizations stop here and must be resolved by hand (or with an
AI's help), never auto-resolved. See dawn.instructions.md for the full workflow.

Usage:
    uv run --no-sync python -m modules.dawn.upgrade
    uv run --no-sync invoke dawn.upgrade
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from ..common import cli as click
from ..common.properties import get_repo_root
from ..common.utils import error, info, success, warning
from .version import parse_theme_version

_MAIN_BRANCHES = {"development", "main", "dawn_vanilla"}


def _run_ok(repo_path: Path, *args: str) -> bool:
    """Run a git command; return True on success (no output captured)."""
    result = subprocess.run(["git", "-C", str(repo_path), *args], check=False)
    return result.returncode == 0


def _run_out(repo_path: Path, *args: str) -> str:
    """Run a git command and return its stripped stdout."""
    result = subprocess.run(["git", "-C", str(repo_path), *args], capture_output=True, text=True, check=False)
    return result.stdout.strip()


def _vanilla_version(repo_path: Path) -> str:
    """Return the Dawn version origin/dawn_vanilla is synced to, per its settings_schema.json."""
    schema_json = _run_out(repo_path, "show", "origin/dawn_vanilla:config/settings_schema.json")
    if not schema_json:
        error("Could not read config/settings_schema.json from origin/dawn_vanilla.")
    return parse_theme_version(schema_json)


def _upgrade_branch(repo_path: Path, version: str) -> str:
    """Resolve the branch to merge into: the current feature branch, or upgrade/dawn-vanilla-v<version>."""
    current = _run_out(repo_path, "branch", "--show-current")
    if current and current not in _MAIN_BRANCHES:
        info(f"Using already-cut feature branch: {current}")
        return current

    branch = f"upgrade/dawn-vanilla-v{version}"
    if _run_ok(repo_path, "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}"):
        info(f"Reusing existing branch {branch}...")
        if not _run_ok(repo_path, "checkout", branch):
            error(f"Failed to check out existing branch {branch}.")
        return branch

    info(f"Creating {branch} from origin/development...")
    if not _run_ok(repo_path, "checkout", "-b", branch, "origin/development"):
        error(f"Failed to create branch {branch} from origin/development.")
    return branch


def _show_conflicts(repo_path: Path) -> None:
    """Print files with unresolved merge conflicts and how to proceed."""
    conflicted = _run_out(repo_path, "diff", "--name-only", "--diff-filter=U")
    warning("Merge hit conflicts — resolve manually:")
    for file in conflicted.splitlines():
        click.echo(f"  {file}")
    click.echo()
    click.echo("Resolve each file (see fireball.instructions.md's tracking table for what Fireball")
    click.echo("customizations to preserve), then:  git add <file>...  &&  git merge --continue")
    click.echo("Once the merge is committed, run /push then /pr to open a PR into development.")


def main() -> None:
    """
    Merge origin/dawn_vanilla into a feature branch for manual review.

    Assumes dawn_vanilla is already synced to the target upstream version (via the "Upgrade"
    GitHub Actions workflow). Merges into the currently checked-out feature branch if one is
    already cut, otherwise cuts (or reuses) upgrade/dawn-vanilla-v<version> off
    origin/development. Never auto-resolves conflicts or opens a PR — that's a deliberate,
    separate step.
    """
    repo_path = get_repo_root()

    if _run_out(repo_path, "status", "--porcelain"):
        error("Working tree has uncommitted changes — commit or stash them before running dawn.upgrade.")

    info("Fetching development and dawn_vanilla from origin...")
    if not _run_ok(repo_path, "fetch", "origin", "development", "dawn_vanilla"):
        error("Failed to fetch origin/development and origin/dawn_vanilla.")

    version = _vanilla_version(repo_path)
    info(f"origin/dawn_vanilla is synced to Dawn v{version}")

    branch = _upgrade_branch(repo_path, version)

    if _run_ok(repo_path, "merge-base", "--is-ancestor", "origin/dawn_vanilla", "HEAD"):
        success(f"{branch} already contains origin/dawn_vanilla (Dawn v{version}) — nothing to merge.")
        return

    info(f"Merging origin/dawn_vanilla into {branch}...")
    if _run_ok(repo_path, "merge", "--no-ff", "origin/dawn_vanilla", "-m", f"chore: upgrade Dawn to v{version}"):
        success(f"origin/dawn_vanilla (Dawn v{version}) merged cleanly into {branch} — no conflicts.")
        click.echo("Run /push then /pr to open a PR into development.")
        return

    _show_conflicts(repo_path)


if __name__ == "__main__":
    main()
