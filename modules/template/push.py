"""
Push new generic tooling from this repo into its parent template repo as a PR.

The parent is configured in properties.yml (`template.local` / `template.remote`); repos chain
(e.g. root skeleton -> domain template -> project repo), each syncing only with its direct parent.

Three explicit phases, split at the confirmation boundary so the calling prompt can review
results between each step and only proceed after the user approves:

    uv run --no-sync python -m modules.template.push diff
    uv run --no-sync python -m modules.template.push apply --file <path> [--file ...] [--delete <path> ...]
    uv run --no-sync python -m modules.template.push create-pr --branch <name> [--title ...] [--body ...]
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from ..common import cli as click
from ..common.properties import get_repo_local, get_template_local
from ..common.utils import error, success
from .resolve import resolve_template_repo
from .scope import is_excluded, iter_candidates

_REPLACE_PLACEHOLDER = "\x00TEMPLATE_NAME\x00"


def rewrite_repo_references(content: str, repo_name: str, template_name: str) -> str:
    """
    Replace references to the working repo's name with the template repo's name.

    Safe when one name contains the other (e.g. template_my_vault contains my_vault):
    existing template-name occurrences are masked with a placeholder first so they
    survive the replacement untouched.
    """
    if not repo_name or repo_name == template_name:
        return content
    masked = content.replace(template_name, _REPLACE_PLACEHOLDER)
    masked = masked.replace(repo_name, template_name)
    return masked.replace(_REPLACE_PLACEHOLDER, template_name)


def _read_rewritten(src: Path, repo_name: str, template_name: str) -> bytes:
    """Read src as it would land in the template: text gets repo-name rewriting, binary is raw."""
    raw = src.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw
    return rewrite_repo_references(text, repo_name, template_name).encode("utf-8")


def _classify(
    repo_root: Path,
    template_root: Path,
    repo_name: str,
    template_name: str,
) -> tuple[list[Path], list[Path], list[Path]]:
    """Return (added, modified, deleted) candidate paths; identical files are skipped silently.

    Comparison happens on the rewritten content (repo name replaced with template name), so
    files that differ only by repo-name references are treated as identical. `deleted` lists
    in-scope template files with no counterpart in the working repo — deprecation candidates
    that the caller must confirm with the user before removing.
    """
    added: list[Path] = []
    modified: list[Path] = []
    repo_candidates = iter_candidates(repo_root)
    for rel in repo_candidates:
        src = repo_root / rel
        dst = template_root / rel
        if not dst.exists():
            added.append(rel)
        elif _read_rewritten(src, repo_name, template_name) != dst.read_bytes():
            modified.append(rel)

    repo_set = set(repo_candidates)
    deleted = [rel for rel in iter_candidates(template_root) if rel not in repo_set]
    return added, modified, deleted


def _default_branch(template_root: Path) -> str:
    result = subprocess.run(
        ["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
        cwd=template_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip().rsplit("/", 1)[-1]
    return "main"


def run_diff() -> None:
    """Print ADDED/MODIFIED/DELETED candidate files scoped by modules/template/scope.py."""
    repo_root = get_repo_local()
    template_root = resolve_template_repo()
    repo_name = repo_root.name
    template_name = get_template_local().name
    added, modified, deleted = _classify(repo_root, template_root, repo_name, template_name)

    click.echo("ADDED:")
    for path in added:
        click.echo(f"  {path}")
    click.echo("MODIFIED:")
    for path in modified:
        click.echo(f"  {path}")
    click.echo("DELETED (in template but not in this repo — confirm before removing):")
    for path in deleted:
        click.echo(f"  {path}")


def run_apply(files: list[str], deletes: list[str] | None = None) -> None:
    """Branch the template repo, apply approved copies and deletions, commit, and push."""
    deletes = deletes or []
    if not files and not deletes:
        error("apply mode requires at least one --file or --delete", exit_code=1)

    repo_root = get_repo_local()
    template_root = resolve_template_repo()
    repo_name = repo_root.name
    template_name = get_template_local().name

    for rel in deletes:
        rel_path = Path(rel)
        if is_excluded(rel_path):
            error(f"--delete {rel} is outside the push scope", exit_code=1)
        if not (template_root / rel_path).is_file():
            error(f"--delete {rel} not found in the template repo", exit_code=1)

    click.echo(f"📥 Updating {template_name} default branch...")
    subprocess.run(["git", "fetch", "origin"], cwd=template_root, check=False)
    default_branch = _default_branch(template_root)
    subprocess.run(["git", "checkout", default_branch], cwd=template_root, check=True)
    subprocess.run(["git", "pull", "--ff-only"], cwd=template_root, check=False)

    branch_name = f"sync-from-{repo_name.replace('_', '-')}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    subprocess.run(["git", "checkout", "-b", branch_name], cwd=template_root, check=True)

    for rel in files:
        src = repo_root / rel
        dst = template_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            content = src.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            shutil.copy2(src, dst)
            continue
        dst.write_text(rewrite_repo_references(content, repo_name, template_name), encoding="utf-8")

    if deletes:
        subprocess.run(["git", "rm", "-q", "--", *deletes], cwd=template_root, check=True)

    subprocess.run(["git", "add", "."], cwd=template_root, check=True)
    commit_message = f"Sync generic tooling from {repo_name} ({datetime.now().strftime('%Y-%m-%d')})"
    subprocess.run(["git", "commit", "-m", commit_message], cwd=template_root, check=True)
    subprocess.run(["git", "push", "-u", "origin", branch_name], cwd=template_root, check=True)

    success(f"Pushed branch {branch_name} to {template_name}")
    click.echo(f"TEMPLATE_PUSH_BRANCH={branch_name}")
    click.echo(f"TEMPLATE_PUSH_BASE={default_branch}")


def run_create_pr(branch: str | None, title: str | None, body: str | None) -> None:
    """Open a PR for `branch` against the parent template repo, confirming first in interactive runs."""
    if not branch:
        error("create-pr mode requires --branch", exit_code=1)

    template_root = resolve_template_repo()
    template_name = get_template_local().name

    if sys.stdin.isatty() and not click.confirm(
        f"Open a PR for branch {branch} against {template_name}?", default=False
    ):
        click.echo("PR creation cancelled.")
        raise SystemExit(0)

    cmd = ["gh", "pr", "create", "--head", branch]
    if title:
        cmd += ["--title", title]
    if body:
        cmd += ["--body", body]

    result = subprocess.run(cmd, cwd=template_root, check=False)
    if result.returncode != 0:
        error("Failed to create PR — see gh output above", exit_code=result.returncode)
    success("PR created")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="modules.template.push")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    subparsers.add_parser("diff")

    apply_parser = subparsers.add_parser("apply")
    apply_parser.add_argument("--file", dest="files", action="append", default=[])
    apply_parser.add_argument("--delete", dest="deletes", action="append", default=[])

    pr_parser = subparsers.add_parser("create-pr")
    pr_parser.add_argument("--branch", required=True)
    pr_parser.add_argument("--title", default=None)
    pr_parser.add_argument("--body", default=None)

    return parser


def main() -> None:
    """Parse the push subcommand and dispatch to the matching phase."""
    args = _build_parser().parse_args()

    if args.mode == "diff":
        run_diff()
    elif args.mode == "apply":
        run_apply(args.files, args.deletes)
    elif args.mode == "create-pr":
        run_create_pr(args.branch, args.title, args.body)


if __name__ == "__main__":
    main()
