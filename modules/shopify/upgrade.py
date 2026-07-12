"""Upgrade dawn_vanilla from upstream Shopify/dawn, then merge into development."""

import subprocess
from pathlib import Path

from ..common import cli as click
from ..common.properties import get_repo_local
from ..common.utils import error, info, success, warning

VANILLA_BRANCH = "dawn_vanilla"
DEV_BRANCH = "development"
UPSTREAM_REMOTE = "upstream"
UPSTREAM_BRANCH = "main"


def _run_ok(repo_path: Path, *args: str) -> bool:
    """Run a git command; return True on success (no output captured)."""
    result = subprocess.run(["git", "-C", str(repo_path), *args], check=False)
    return result.returncode == 0


def _run_out(repo_path: Path, *args: str) -> str:
    """Run a git command and return its stripped stdout."""
    result = subprocess.run(["git", "-C", str(repo_path), *args], capture_output=True, text=True, check=False)
    return result.stdout.strip()


# ── Version helpers ──────────────────────────────────────────────────────


def _current_dawn_version(repo_path: Path) -> str | None:
    """Return the latest tag reachable from dawn_vanilla, if any."""
    out = _run_out(repo_path, "describe", "--tags", "--abbrev=0", VANILLA_BRANCH)
    return out or None


def _latest_upstream_version(repo_path: Path) -> str | None:
    """Return the newest semver tag reachable from upstream/main."""
    out = _run_out(
        repo_path,
        "tag",
        "--merged",
        f"{UPSTREAM_REMOTE}/{UPSTREAM_BRANCH}",
        "--sort=-version:refname",
    )
    lines = [line.strip() for line in out.splitlines() if line.strip()]
    return lines[0] if lines else None


def _latest_local_version(repo_path: Path) -> str:
    """Return the latest tag reachable from dawn_vanilla."""
    return _run_out(repo_path, "describe", "--tags", "--abbrev=0", VANILLA_BRANCH)


# ── Branch helpers ───────────────────────────────────────────────────────


def _current_branch(repo_path: Path) -> str:
    """Return the current checked-out branch name."""
    return _run_out(repo_path, "rev-parse", "--abbrev-ref", "HEAD")


def _checkout(repo_path: Path, branch: str) -> None:
    """Checkout a branch, exiting on failure."""
    click.echo(f"Switching to {branch}...")
    if not _run_ok(repo_path, "checkout", branch):
        error(f"Failed to checkout {branch}.")


# ── Stash helpers ────────────────────────────────────────────────────────


def _stash_changes(repo_path: Path, branch: str) -> bool:
    """Stash local changes if the working tree is dirty."""
    out = _run_out(repo_path, "status", "--porcelain")
    if not out:
        return False

    info(f"Uncommitted changes on '{branch}' detected — stashing...")
    if not _run_ok(repo_path, "stash", "push", "--all", "-m", "auto-stash before shopify upgrade"):
        error("Failed to stash changes. Commit or stash manually before upgrading.")
    success("Changes stashed.")
    click.echo()
    return True


def _restore_stash(repo_path: Path) -> None:
    """Restore stashed changes, warning on conflicts."""
    info("Restoring stashed changes...")
    if _run_ok(repo_path, "stash", "pop"):
        success("Stash restored.")
    else:
        warning("Stash pop had conflicts. Run: git stash pop   to restore manually.")


# ── Prerequisite confirmation ────────────────────────────────────────────


def _confirm_prerequisites(repo_path: Path) -> None:
    """Fetch upstream and confirm the user wants to proceed with the upgrade."""
    info(f"Fetching upstream {UPSTREAM_REMOTE}/{UPSTREAM_BRANCH}...")
    if not _run_ok(repo_path, "fetch", UPSTREAM_REMOTE, "--tags", "--quiet"):
        error(
            f"Failed to fetch from {UPSTREAM_REMOTE}. Check network and remote config.\n"
            "Run: git remote -v   to verify upstream remote exists."
        )
    success("Fetch complete.")
    click.echo()

    current = _current_dawn_version(repo_path)
    latest = _latest_upstream_version(repo_path)

    if current is None or latest is None:
        warning("Could not detect Dawn version tags.")
        warning(f"current={current!r}  latest={latest!r}")
    elif current == latest:
        info(f"dawn_vanilla is already at {current} (latest upstream).")
        if not click.is_tty():
            return
        if not click.confirm("No upgrade available. Proceed anyway to re-merge into development?", default=False):
            info("Upgrade skipped.")
            raise SystemExit(0)
    else:
        info(f"dawn_vanilla is at : {current}")
        info(f"Upstream latest is : {latest}")
        click.echo()
        if not click.is_tty():
            return
        if not click.confirm(f"Upgrade dawn_vanilla {current} → {latest} and merge into development?", default=True):
            info("Upgrade cancelled.")
            raise SystemExit(0)

    click.echo()


# ── Core upgrade steps ───────────────────────────────────────────────────


def _upgrade_dawn_vanilla(repo_path: Path) -> None:
    """Checkout dawn_vanilla, merge upstream/main into it, and push to origin."""
    _checkout(repo_path, VANILLA_BRANCH)

    info(f"Merging {UPSTREAM_REMOTE}/{UPSTREAM_BRANCH} into {VANILLA_BRANCH}...")
    if not _run_ok(repo_path, "merge", f"{UPSTREAM_REMOTE}/{UPSTREAM_BRANCH}", "--no-edit"):
        error(
            f"Merge of upstream/{UPSTREAM_BRANCH} into {VANILLA_BRANCH} failed.\n"
            f"{VANILLA_BRANCH} should track upstream cleanly — check for unexpected commits.\n"
            "Resolve conflicts, then: git merge --continue && "
            f"git push origin {VANILLA_BRANCH}"
        )

    info(f"Pushing {VANILLA_BRANCH} to origin...")
    if not _run_ok(repo_path, "push", "origin", VANILLA_BRANCH):
        error(f"Failed to push {VANILLA_BRANCH} to origin.")

    success(f"{VANILLA_BRANCH} updated and pushed.")
    click.echo()


def _show_conflicts(repo_path: Path) -> None:
    """Print files with unresolved merge conflicts."""
    out = _run_out(repo_path, "diff", "--name-only", "--diff-filter=U")
    conflicted = [line.strip() for line in out.splitlines() if line.strip()]

    click.echo(f"Merge conflicts in {DEV_BRANCH}. Resolve the following files:", err=True)
    for file in conflicted:
        click.echo(f"  {file}", err=True)


def _merge_into_development(repo_path: Path, stashed: bool, original_branch: str) -> None:
    """Checkout development and merge dawn_vanilla into it."""
    _checkout(repo_path, DEV_BRANCH)

    info(f"Merging {VANILLA_BRANCH} into {DEV_BRANCH}...")
    if not _run_ok(repo_path, "merge", VANILLA_BRANCH, "--no-edit"):
        if stashed:
            _restore_stash(repo_path)
        _show_conflicts(repo_path)
        click.echo()
        click.echo("Next steps after resolving conflicts:")
        click.echo("  git add .  &&  git merge --continue")
        click.echo("  Then run /push or uv run --no-sync invoke repo.push")
        raise SystemExit(1)

    success(f"{DEV_BRANCH} updated with {VANILLA_BRANCH} changes.")

    if stashed and original_branch == DEV_BRANCH:
        _restore_stash(repo_path)


def main() -> None:
    """Upgrade dawn_vanilla from upstream Shopify/dawn, then merge into development."""
    repo_path = get_repo_local()

    _confirm_prerequisites(repo_path)

    original_branch = _current_branch(repo_path)
    stashed = _stash_changes(repo_path, original_branch)

    _upgrade_dawn_vanilla(repo_path)
    _merge_into_development(repo_path, stashed, original_branch)

    click.echo()
    success("Upgrade complete!")
    info(f"dawn_vanilla and development are now at {_latest_local_version(repo_path)}.")
    info("Run /push or repo.push to push development to origin.")


if __name__ == "__main__":
    main()
