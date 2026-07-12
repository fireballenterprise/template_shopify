"""Detect a PR's base branch, print diff context, save notes, and open the PR via gh."""

from __future__ import annotations

import subprocess
from datetime import UTC, datetime
from pathlib import Path

from ..common import cli as click
from ..common.properties import get_repo_local, get_repo_remote
from ..common.utils import error, success

_BASE_CANDIDATES = ("development", "main")
_DIFF_CHAR_LIMIT = 20_000


def _gh_repo_slug() -> str:
    """Return 'owner/repo' for --repo, so gh targets this fork instead of its upstream parent."""
    return get_repo_remote().removeprefix("github.com/")


def _current_branch(repo_path: Path) -> str:
    """Return the current checked-out branch name."""
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_path, capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def _remote_branches(repo_path: Path) -> list[str]:
    """Return all remote-tracking branch refs (e.g. 'origin/main')."""
    result = subprocess.run(["git", "branch", "-r"], cwd=repo_path, capture_output=True, text=True, check=True)
    return [line.strip() for line in result.stdout.splitlines()]


def _commits_ahead(repo_path: Path, base_ref: str) -> int:
    """Return the number of commits HEAD is ahead of base_ref."""
    result = subprocess.run(
        ["git", "rev-list", "--count", f"{base_ref}..HEAD"], cwd=repo_path, capture_output=True, text=True, check=True
    )
    return int(result.stdout.strip())


def _detect_base_branch(repo_path: Path, current_branch: str) -> str:
    """Detect which base branch (development/main/etc.) the current branch forked from."""
    remotes = _remote_branches(repo_path)
    candidates = [
        f"origin/{name}" for name in _BASE_CANDIDATES if f"origin/{name}" in remotes and name != current_branch
    ]
    if not candidates:
        error("No base branch found (looked for development, main on origin).")

    if len(candidates) == 1:
        return candidates[0]

    # Multiple candidates exist — pick the one this branch forked from most recently
    # (fewest commits between its merge-base and HEAD).
    return min(candidates, key=lambda ref: _commits_ahead(repo_path, ref))


def _commit_log(repo_path: Path, base_ref: str) -> str:
    """Return the one-line commit log for base_ref..HEAD."""
    result = subprocess.run(
        ["git", "log", "--oneline", "--no-decorate", f"{base_ref}..HEAD"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip() or "(no commits)"


def _diff_stat(repo_path: Path, base_ref: str) -> str:
    """Return the diffstat for base_ref...HEAD."""
    result = subprocess.run(
        ["git", "diff", "--stat", f"{base_ref}...HEAD"], cwd=repo_path, capture_output=True, text=True, check=True
    )
    return result.stdout.strip() or "(no changes)"


def _diff(repo_path: Path, base_ref: str) -> str:
    """Return the full diff for base_ref...HEAD, truncated if very large."""
    result = subprocess.run(
        ["git", "diff", f"{base_ref}...HEAD"], cwd=repo_path, capture_output=True, text=True, check=True
    )
    diff = result.stdout
    if len(diff) > _DIFF_CHAR_LIMIT:
        diff = diff[:_DIFF_CHAR_LIMIT] + "\n... (diff truncated — run `git diff` locally for the full change)"
    return diff.strip() or "(no changes)"


def main() -> None:
    """Print the current branch's commit log and diff vs. its detected base branch."""
    repo_path = get_repo_local()

    click.echo("Fetching remote refs...")
    subprocess.run(["git", "fetch", "--prune"], cwd=repo_path, check=False)

    current_branch = _current_branch(repo_path)
    base_ref = _detect_base_branch(repo_path, current_branch)
    base_name = base_ref.removeprefix("origin/")

    click.echo(f"Current branch: {current_branch}")
    click.echo(f"Base branch:    {base_name}")
    click.echo()
    click.echo(f"## Commits ({base_name}..{current_branch})")
    click.echo(_commit_log(repo_path, base_ref))
    click.echo()
    click.echo("## Diff Stat")
    click.echo(_diff_stat(repo_path, base_ref))
    click.echo()
    click.echo("## Diff")
    click.echo(_diff(repo_path, base_ref))


def save_notes(content: str | None = None) -> None:
    """Save PR notes markdown to tmp/pull_requests/<timestamp>_<branch>.md."""
    if not content or not content.strip():
        error("PR notes content cannot be empty")

    repo_path = get_repo_local()
    branch = _current_branch(repo_path)
    safe_branch = branch.replace("/", "-")

    out_dir = repo_path / "tmp" / "pull_requests"
    out_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(UTC).strftime("%Y-%m-%dT%H-%M-%SZ")
    out_file = out_dir / f"{timestamp}_{safe_branch}.md"
    out_file.write_text(content.strip() + "\n", encoding="utf-8")

    success(f"Saved PR notes: tmp/pull_requests/{out_file.name}")


def create_pr(title: str | None = None, content: str | None = None) -> None:
    """Open a GitHub PR for the current branch against its detected base branch."""
    if not title or not title.strip():
        error("PR title cannot be empty")
    if not content or not content.strip():
        error("PR notes content cannot be empty")

    repo_path = get_repo_local()
    current_branch = _current_branch(repo_path)
    base_ref = _detect_base_branch(repo_path, current_branch)
    base_name = base_ref.removeprefix("origin/")

    repo_slug = _gh_repo_slug()
    click.echo(f"Creating PR: {current_branch} -> {base_name} (repo: {repo_slug})")
    result = subprocess.run(
        [
            "gh",
            "pr",
            "create",
            "--repo",
            repo_slug,
            "--base",
            base_name,
            "--head",
            current_branch,
            "--title",
            title,
            "--body",
            content,
        ],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        if "already exists" in result.stderr.lower():
            existing = subprocess.run(
                ["gh", "pr", "view", "--repo", repo_slug, "--json", "url", "-q", ".url"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=False,
            )
            if existing.returncode == 0 and existing.stdout.strip():
                success(f"PR already exists: {existing.stdout.strip()}")
                return
        error(f"gh pr create failed:\n{result.stderr}")

    success("PR created!")
    click.echo(result.stdout.strip())


if __name__ == "__main__":
    main()
