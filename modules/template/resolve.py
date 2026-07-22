"""Resolve the local path to this repo's parent template repo."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from ..common import cli as click
from ..common.properties import get_repo_local, get_template_local, get_template_remote
from ..common.utils import success, warning


def clone_remote(remote: str) -> Path:
    """Shallow-clone the template repo's remote into tmp/template_sync/."""
    dest = get_repo_local() / "tmp" / "template_sync"
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)

    url = f"https://{remote}.git"
    click.echo(f"Local template path not found — cloning {url}...")
    subprocess.run(["git", "clone", "--depth", "1", url, str(dest)], check=True)
    success(f"Cloned template repo to {dest}")
    return dest


def resolve_template_repo() -> Path:
    """
    Resolve the local path to the parent template repo configured in properties.yml.

    If `template.local` exists on disk, use it directly. Otherwise shallow-clone
    `template.remote` into tmp/template_sync/.
    """
    local = get_template_local()
    if local.is_dir():
        success(f"Using local template repo at {local}")
        return local

    warning(f"Template repo local path not found: {local}")
    return clone_remote(get_template_remote())
