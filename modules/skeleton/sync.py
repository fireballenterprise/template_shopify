"""
Resolve the local path to the shared skeleton repo (repo_setup_python) for /sync-setup.

Prints the resolved path on its own line, prefixed `SKELETON_PATH=`, so the calling prompt can
parse it out of any other status output.

Usage:
    uv run --no-sync invoke skeleton.locate_source
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from ..common import cli as click
from ..common.properties import get_repo_root, get_skeleton_local, get_skeleton_remote
from ..common.utils import success, warning


def _clone_remote(remote: str) -> Path:
    """Shallow-clone the skeleton repo's remote into tmp/skeleton_sync/."""
    dest = get_repo_root() / "tmp" / "skeleton_sync"
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)

    url = f"https://{remote}.git"
    click.echo(f"Local skeleton path not found — cloning {url}...")
    subprocess.run(["git", "clone", "--depth", "1", url, str(dest)], check=True)
    success(f"Cloned skeleton to {dest}")
    return dest


def main() -> None:
    """Resolve and print the local path to the shared skeleton repo."""
    local = get_skeleton_local()
    if local.is_dir():
        success(f"Using local skeleton at {local}")
        click.echo(f"SKELETON_PATH={local}")
        return

    warning(f"Skeleton local path not found: {local}")
    source = _clone_remote(get_skeleton_remote())
    click.echo(f"SKELETON_PATH={source}")


if __name__ == "__main__":
    main()
