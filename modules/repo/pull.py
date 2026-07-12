"""Pull updates from git remote (stash → pull --rebase → restore)."""

import subprocess
from pathlib import Path

from ..common import cli as click
from ..common.properties import get_repo_local
from ..common.utils import error, success, warning


def _stash_if_needed(repo_path: Path) -> bool:
    """Stash local changes if the working tree is dirty."""
    click.echo("🔍 Checking working directory status...")
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )

    if not result.stdout.strip():
        success("Working directory is clean")
        click.echo()
        return False

    click.echo("⚠️  Uncommitted changes detected — stashing...")
    stash_result = subprocess.run(
        ["git", "stash", "push", "--all", "-m", "auto-stash before pull"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=False,
    )
    if stash_result.returncode != 0:
        click.echo(stash_result.stderr.strip())
        error("Failed to stash changes.")

    success("Changes stashed")
    click.echo()
    return True


def _restore_stash(repo_path: Path) -> None:
    """Restore stashed changes after pull."""
    click.echo("📂 Restoring stashed changes...")
    pop_result = subprocess.run(
        ["git", "stash", "pop"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=False,
    )
    if pop_result.returncode != 0:
        click.echo(pop_result.stderr.strip())
        warning("Stash pop had conflicts — resolve manually, then: git stash drop")
        return
    success("Stashed changes restored")


def _pull_rebase(repo_path: Path) -> None:
    """Pull from remote with --rebase."""
    click.echo("📥 Pulling latest changes from remote (--rebase)...")
    result = subprocess.run(
        ["git", "pull", "--rebase"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.stdout:
        click.echo(result.stdout.strip())
    if result.returncode != 0:
        click.echo(result.stderr.strip())
        error("Git pull --rebase failed. Resolve conflicts then run: git rebase --continue")
    success("Pull completed")


def main() -> None:
    """Pull updates from git remote (stash → pull --rebase → restore)."""
    repo_path = get_repo_local()

    stashed = _stash_if_needed(repo_path)
    _pull_rebase(repo_path)

    if stashed:
        click.echo()
        _restore_stash(repo_path)


if __name__ == "__main__":
    main()
