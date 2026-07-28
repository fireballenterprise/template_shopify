"""
Resolve the local path to this repo's parent template repo, and (when it's a local checkout)
clobber-copy its shared tooling into this project for /template pull.

Two phases:
    uv run --no-sync python -m modules.template.pull resolve
    uv run --no-sync python -m modules.template.pull copy
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

from ..common import cli as click
from ..common.properties import get_repo_local, get_template_local
from ..common.utils import success
from .ignore import is_hard_excluded, load_ignore_patterns, matches_ignore
from .naming import rewrite_repo_references
from .resolve import resolve_template_repo


def run_resolve() -> None:
    """Resolve the template repo path and report whether it's a local checkout."""
    is_local = get_template_local().is_dir()
    template_root = resolve_template_repo()
    click.echo(f"TEMPLATE_PATH={template_root}")
    click.echo(f"TEMPLATE_LOCAL={'true' if is_local else 'false'}")


def _tracked_files(template_root: Path) -> list[Path]:
    """List git-tracked files in template_root (skips gitignored/untracked junk automatically)."""
    result = subprocess.run(["git", "ls-files"], cwd=template_root, capture_output=True, text=True, check=True)
    return [Path(line) for line in result.stdout.splitlines() if line]


def run_copy() -> None:
    """
    Clobber-copy every git-tracked file from the local template repo into this project.

    Skips modules/template/ignore.py's hard safety excludes and anything matching this project's
    template.ignore.yml. No per-file diff or confirmation -- the working tree is git-tracked, so
    the resulting change is reviewed via `git status`/`git diff` after the fact, not before.
    """
    repo_root = get_repo_local()
    template_root = resolve_template_repo()
    repo_name = repo_root.name
    template_name = get_template_local().name
    ignore_patterns = load_ignore_patterns(repo_root)

    copied: list[Path] = []
    for rel in _tracked_files(template_root):
        if is_hard_excluded(rel) or matches_ignore(rel, ignore_patterns):
            continue
        src = template_root / rel
        dst = repo_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            text = src.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            shutil.copy2(src, dst)
        else:
            dst.write_text(rewrite_repo_references(text, template_name, repo_name), encoding="utf-8")
        copied.append(rel)

    success(f"Copied {len(copied)} files from {template_name}")
    for rel in copied:
        click.echo(f"  {rel}")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="modules.template.pull")
    subparsers = parser.add_subparsers(dest="mode")
    subparsers.add_parser("resolve")
    subparsers.add_parser("copy")
    return parser


def main() -> None:
    """Parse the pull subcommand (default: resolve) and dispatch."""
    args = _build_parser().parse_args()
    if args.mode == "copy":
        run_copy()
    else:
        run_resolve()


if __name__ == "__main__":
    main()
