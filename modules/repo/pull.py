"""Pull updates from git remote."""

import subprocess

from ..common import cli as click
from ..common.properties import get_repo_local
from ..common.utils import error, success, warning


def _restore_stash(repo_path, *, on_failure: str) -> bool:
    """Restore stashed changes and report outcome."""
    pop_result = subprocess.run(
        ["git", "stash", "pop"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=False,
    )
    if pop_result.returncode != 0:
        click.echo(pop_result.stderr.strip())
        warning(on_failure)
        return False
    success("Stashed changes restored")
    return True


def _stash_if_needed(repo_path) -> bool:
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
        error("Failed to stash changes.", exit_code=1)

    success("Changes stashed")
    click.echo()
    return True


@click.command()
def main() -> None:
    """
    Pull updates from git remote.

    Steps:
    1. Check working directory and stash local changes if needed
    2. Pull latest changes from git remote
        - Uses rebase to handle divergent local/remote history
    3. Restore stashed changes, if any
    """
    repo_path = get_repo_local()

    click.echo("📥 Starting pull from remote...")
    click.echo()

    stashed = _stash_if_needed(repo_path)

    click.echo("📥 Pulling latest changes from git remote...")
    try:
        subprocess.run(["git", "pull", "--rebase"], cwd=repo_path, check=True)
        success("Git pull completed")
    except subprocess.CalledProcessError:
        if stashed:
            click.echo()
            click.echo("📦 Restoring stashed changes after pull failure...")
            _restore_stash(
                repo_path,
                on_failure="Stash pop failed — your changes are still in the stash. Run: git stash pop",
            )
        error("Git pull failed. Check network or merge conflicts.", exit_code=1)

    if stashed:
        click.echo()
        click.echo("📦 Restoring stashed changes...")
        _restore_stash(
            repo_path,
            on_failure="Stash pop failed — your changes are still in the stash. Run: git stash pop",
        )

    click.echo()
    click.echo("🎉 Pull completed!")


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
