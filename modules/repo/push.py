"""Push changes to git remote."""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

from ..common import cli as click
from ..common.properties import get_repo_local
from ..common.utils import error, success, warning
from .pr_diff import PROTECTED_BRANCHES
from .pr_diff import current_branch as _current_branch


def _tests_report_success(output: str) -> bool:
    return "Your code has been rated at 10.00/10" in output


def run_tests(repo_path: Path) -> None:
    """Run automated code fixes and tests."""
    # Auto-fix code style before push
    click.echo("🔧 Running automated code fixes...")
    try:
        subprocess.run(
            ["uv", "run", "invoke", "fix"],
            cwd=repo_path,
            check=True,
            capture_output=False,  # Show output to user
        )
        success("Code fixes completed")
    except subprocess.CalledProcessError:
        warning("Code fixes had issues, but continuing with tests...")

    click.echo()

    # Run tests to validate code quality
    click.echo("🧪 Running tests to validate code quality...")
    result = subprocess.run(
        ["uv", "run", "invoke", "test"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    combined_output = f"{result.stdout}{result.stderr}"
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)

    if result.returncode == 0 or _tests_report_success(combined_output):
        success("All tests passed! ✨")
        return

    click.echo()
    click.echo("❌ Tests failed! Must achieve 10/10 before pushing.")
    click.echo()
    click.echo("⚠️  Push has been stopped. You have three options:")
    click.echo("1. Fix the style issue in the code")
    click.echo("2. Update global rules (e.g., .pylintrc, pyproject.toml)")
    click.echo("3. Add a file-specific exception/exclusion")
    click.echo()
    click.echo("Please address the issues above and run /push again.")
    raise SystemExit(result.returncode)


def _resolve_conflicts(repo_path: Path, porcelain_output: str) -> None:
    """Reset any files stuck in merge-conflict state (e.g. from a previous failed stash pop)."""
    for entry in porcelain_output.splitlines():
        xy = entry[:2]
        filepath = entry[3:]
        if "U" in xy:
            warning(f"Resolving leftover merge conflict: {filepath}")
            subprocess.run(["git", "checkout", "HEAD", "--", filepath], cwd=repo_path, check=False, capture_output=True)
            subprocess.run(["git", "add", filepath], cwd=repo_path, check=False, capture_output=True)


def _stash_pop(repo_path: Path) -> None:
    """Pop the stash, erroring out if it fails (e.g. an unresolved conflict)."""
    pop_result = subprocess.run(
        ["git", "stash", "pop"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=False,
    )
    if pop_result.returncode != 0:
        error(f"Failed to restore stash:\n{pop_result.stdout}{pop_result.stderr}", exit_code=1)


def _has_commits_to_push(repo_path: Path) -> bool:
    """Return whether HEAD is ahead of its upstream tracking branch."""
    result = subprocess.run(
        ["git", "rev-list", "--count", "@{u}..HEAD"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0 and result.stdout.strip() != "0"


def _git_pull(repo_path: Path, stashed: bool, branch: str) -> bool:
    """
    Pull from remote, falling back to rebase on diverging branches.

    Returns True if the branch has no upstream yet and isn't a protected branch — i.e. it's a
    brand-new local feature branch for this change, so there's nothing to pull and the caller
    should push it (with -u) unconditionally rather than only when there are new commits.
    """
    pull_result = subprocess.run(["git", "pull"], cwd=repo_path, capture_output=True, text=True, check=False)
    if pull_result.returncode == 0:
        success("Pull completed")
        return False

    combined = (pull_result.stdout + pull_result.stderr).lower()

    if "no tracking information" in combined:
        # Re-check the branch live (not a cached/remembered value) so a stale assumption about
        # which branch is checked out never causes a protected branch to get auto-pushed.
        if _current_branch(repo_path) in PROTECTED_BRANCHES:
            if stashed:
                click.echo("⚠️  Restoring stash before exiting...")
                subprocess.run(["git", "stash", "pop"], cwd=repo_path, check=False)
            error(
                f"Protected branch '{branch}' has no upstream to pull from — resolve manually.",
                exit_code=1,
            )
        warning(f"No upstream for '{branch}' yet — treating it as this change's feature branch, will push with -u.")
        return True

    if "diverging" in combined or "fast-forward" in combined:
        warning("Diverging branches detected. Attempting git pull --rebase...")
        rebase_result = subprocess.run(
            ["git", "pull", "--rebase"], cwd=repo_path, capture_output=True, text=True, check=False
        )
        if rebase_result.returncode != 0:
            if stashed:
                click.echo("⚠️  Restoring stash before exiting...")
                subprocess.run(["git", "stash", "pop"], cwd=repo_path, check=False)
            error(
                f"Git pull --rebase failed:\n{rebase_result.stdout}\n{rebase_result.stderr}",
                exit_code=1,
            )
        success("Rebase successful. Continuing push.")
        return False

    if stashed:
        click.echo("⚠️  Restoring stash before exiting...")
        subprocess.run(["git", "stash", "pop"], cwd=repo_path, check=False)
    error(f"Git pull failed. Stopping.\n{pull_result.stdout}\n{pull_result.stderr}", exit_code=1)


def push_git(repo_path: Path, timestamp: str) -> None:
    """Stash, pull, unstash, commit, and push changes to git remote."""
    click.echo("🔍 Checking working directory status...")
    status_result = subprocess.run(
        ["git", "status", "--porcelain"], cwd=repo_path, capture_output=True, text=True, check=True
    )

    # Auto-resolve files stuck in conflict state from a previous failed stash pop
    _resolve_conflicts(repo_path, status_result.stdout)

    # Re-check status after conflict resolution
    status_result = subprocess.run(
        ["git", "status", "--porcelain"], cwd=repo_path, capture_output=True, text=True, check=True
    )

    stashed = False
    if status_result.stdout.strip():
        click.echo("📦 Stashing local changes before pull...")
        stash_result = subprocess.run(
            ["git", "stash", "push", "-u", "-m", "auto-stash before push"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=False,
        )
        if stash_result.returncode != 0:
            error(f"Failed to stash changes:\n{stash_result.stderr}", exit_code=1)
        success("Changes stashed")
        stashed = True
    else:
        success("Working directory is clean")

    click.echo()

    branch = _current_branch(repo_path)
    click.echo("📥 Pulling latest changes from remote...")
    needs_upstream_push = _git_pull(repo_path, stashed, branch)

    # Restore stash if we stashed earlier
    if stashed:
        click.echo()
        click.echo("📂 Restoring stashed changes...")
        _stash_pop(repo_path)
        success("Stash restored")

    click.echo()

    # Check for local changes (including just-unstashed)
    click.echo("🔍 Checking for uncommitted changes...")
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )

    if result.stdout.strip():
        click.echo("📝 Found local changes. Committing...")

        # Stage all changes
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True)

        # Commit with timestamp
        commit_message = f"Push repository: Automated commit {timestamp}"
        subprocess.run(["git", "commit", "-m", commit_message], cwd=repo_path, check=True)
        needs_upstream_push = True
    else:
        success("No local changes to commit")
        needs_upstream_push = needs_upstream_push or _has_commits_to_push(repo_path)

    if needs_upstream_push:
        # -u is a no-op when the branch already tracks a remote, so it's always safe here — it
        # only matters the first time a new feature branch is pushed.
        click.echo("📤 Pushing to remote...")
        subprocess.run(["git", "push", "-u", "origin", branch], cwd=repo_path, check=True)
        success("Push completed")


@click.command()
@click.option("--no-confirm", is_flag=True, help="Skip confirmation prompt")
def main(no_confirm: bool) -> None:
    """
    Push changes to git remote.

    Steps:
    1. Auto-fix code style (ruff check --fix, ruff format)
    2. Run tests (MUST be 10/10 or push stops)
    3. Prompt user to confirm push
    4. Pull latest changes from git remote — skipped for a non-protected branch with no
       upstream yet (a new local feature branch), which pushes with -u instead
    5. Commit and push any local changes to GitHub
    """
    repo_path = get_repo_local()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    click.echo("🔄 Starting repository push...")
    click.echo()

    # Run all steps
    run_tests(repo_path)
    click.echo()

    # Prompt user to confirm push only in interactive terminals
    if not no_confirm and sys.stdin.isatty():
        if not click.confirm("✅ Tests passed! Push to GitHub?", default=True):
            click.echo("Push cancelled by user.")
            raise SystemExit(0)

    click.echo()
    push_git(repo_path, timestamp)

    click.echo()
    click.echo("🎉 Repository push completed!")
    click.echo("   - Git: up to date")


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
