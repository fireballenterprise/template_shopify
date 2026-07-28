"""
Stamp this machine's repo path (and git remote, if any) into properties.yml.

Idempotent and safe to re-run any time — e.g. after moving the repo on disk, renaming it, or
forking it to a new remote. Run via `inv setup.properties` (called automatically by setup.sh).

properties.yml is gitignored (machine-specific local paths) and created fresh from the built-in
template on first run. Every run after that only rewrites repo.local, repo.remote, and template.*
in place — everything else, including comments, is left exactly as-is, so hand edits survive.

template.* (this repo's parent template repo, used by /template) is auto-detected — first against
a small known-family map (template_ai_vault, template_shopify → template_python), then via
GitHub's generated-from link, with an interactive prompt as final fallback — and is only ever
written while it still holds the built-in placeholder, so a hand-configured parent is never
clobbered.
"""

import re
import subprocess
from pathlib import Path

from modules.common import cli
from modules.common.utils import info, success

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_PROPERTIES_FILE = _REPO_ROOT / "properties.yml"

_TEMPLATE = """---
# Repository Properties
# Central configuration for all scripts and automation.
# Created by /setup or ./setup.sh or ./setup.ps1

# This Repository's Local and Remote Paths
repo:
  local: "$HOME/path/to/this/repo"
  remote: "github.com/<your-username>/<your-repo-name>"

# Repository Template Parent Repository
template:
  local: "$HOME/path/to/your/template/repo"
  remote: "github.com/<your-username>/<your-template-repo>"
"""


_TEMPLATE_LOCAL_PLACEHOLDER = "$HOME/path/to/your/template/repo"
_TEMPLATE_REMOTE_PLACEHOLDER = "github.com/<your-username>/<your-template-repo>"

# Known direct children of this repo (template_python) — domain templates that fork straight from
# the root. Checked first, before GitHub's generated-from API, since it's instant and needs no
# network/gh dependency. Not exhaustive — leaf project repos (children of a domain template, e.g.
# fireball_enterprise_shopify under template_shopify) aren't and can't be listed here; those still
# rely on the API/prompt fallback below.
_KNOWN_TEMPLATE_PARENTS: dict[str, str] = {
    "template_ai_vault": "github.com/LevonBecker/template_python",
    "template_shopify": "github.com/LevonBecker/template_python",
}


def _repo_name(repo_remote: str | None) -> str:
    """Return this repo's own short name, preferring the git remote over the local folder name."""
    if repo_remote:
        return repo_remote.rstrip("/").rsplit("/", 1)[-1]
    return _REPO_ROOT.name


def _detect_repo_local() -> str:
    """Return this repo's absolute path, with $HOME swapped in for portability."""
    home = str(Path.home())
    repo_str = str(_REPO_ROOT)
    if repo_str.startswith(home):
        return "$HOME" + repo_str[len(home) :]
    return repo_str


def _detect_repo_remote() -> str | None:
    """Return the git origin remote as 'host/user/repo', or None if there isn't one."""
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None

    url = result.stdout.strip()
    url = re.sub(r"^git@([^:]+):", r"\1/", url)
    url = re.sub(r"^https?://", "", url)
    url = re.sub(r"\.git$", "", url)
    return url


def _detect_template_remote(repo_remote: str | None) -> str | None:
    """Return this repo's parent template as 'github.com/owner/name'.

    Checks the known template-family map first (instant, no `gh` dependency), then falls back to
    GitHub's generated-from link.
    """
    known = _KNOWN_TEMPLATE_PARENTS.get(_repo_name(repo_remote))
    if known:
        return known

    if not repo_remote or not repo_remote.startswith("github.com/"):
        return None
    try:
        result = subprocess.run(
            [
                "gh",
                "api",
                f"repos/{repo_remote.removeprefix('github.com/')}",
                "--jq",
                ".template_repository.full_name // empty",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return None  # gh CLI not installed
    if result.returncode != 0:
        return None
    full_name = result.stdout.strip()
    return f"github.com/{full_name}" if full_name else None


def _read_scalar(lines: list[str], section: str, key: str) -> str | None:
    """Return the unquoted value of `key:` within a top-level `section:` block, or None."""
    in_section = False
    for line in lines:
        if line.rstrip("\n") == f"{section}:":
            in_section = True
            continue
        if not in_section:
            continue
        if line.strip() and not line[0].isspace():
            return None  # reached the next top-level key without finding it
        match = re.match(rf"^\s*{re.escape(key)}:\s*(.*?)\s*$", line)
        if match:
            return match.group(1).strip('"')
    return None


def _replace_scalar(lines: list[str], section: str, key: str, value: str, *, quote: bool = True) -> bool:
    """Rewrite `key: ...` to `key: value` within a top-level `section:` block, in place."""
    formatted = f'"{value}"' if quote else value
    in_section = False
    for i, line in enumerate(lines):
        if line.rstrip("\n") == f"{section}:":
            in_section = True
            continue
        if not in_section:
            continue
        if line.strip() and not line[0].isspace():
            return False  # reached the next top-level key without finding it
        match = re.match(rf"^(\s*{re.escape(key)}:\s*).*$", line)
        if match:
            lines[i] = f"{match.group(1)}{formatted}\n"
            return True
    return False


def _strip_legacy_section(lines: list[str], section: str) -> list[str]:
    """Remove a stale top-level `section:` block (and everything indented under it), if present.

    Self-heals properties.yml files stamped by an older version of this template that included a
    section since removed from the schema (e.g. `screenshots:`).
    """
    out: list[str] = []
    skipping = False
    for line in lines:
        if line.rstrip("\n") == f"{section}:":
            skipping = True
            continue
        if skipping:
            if line.strip() and not line[0].isspace():
                skipping = False
            else:
                continue
        out.append(line)
    return out


def _stamp_template_parent(lines: list[str], repo_local: str, repo_remote: str | None) -> None:
    """Fill in template.* (the /template parent) while it still holds the placeholder.

    Auto-detects via GitHub's generated-from link, falling back to an interactive prompt.
    A hand-configured (non-placeholder) parent is never touched.
    """
    current = _read_scalar(lines, "template", "remote")
    if current not in (None, "", _TEMPLATE_REMOTE_PLACEHOLDER):
        return

    remote = _detect_template_remote(repo_remote)
    if remote:
        info(f"Detected parent template repo: {remote}")
    elif cli.confirm("Sync shared tooling with a parent template repo via /template?", default=False):
        remote = cli.prompt("Parent template remote (e.g. github.com/<user>/<template-repo>)")

    if not remote:
        info("No parent template repo configured — edit template.* in properties.yml if you add one later")
        return

    template_local = f"{repo_local.rsplit('/', 1)[0]}/{remote.rstrip('/').rsplit('/', 1)[-1]}"
    _replace_scalar(lines, "template", "remote", remote)
    _replace_scalar(lines, "template", "local", template_local)
    success(f"properties.yml: template.remote = {remote}")
    success(f"properties.yml: template.local = {template_local} (sibling-path guess — edit if it lives elsewhere)")


@cli.command()
def main() -> None:
    """Create properties.yml from the built-in template (if missing) and stamp local paths into it."""
    just_created = not _PROPERTIES_FILE.exists()
    if just_created:
        _PROPERTIES_FILE.write_text(_TEMPLATE)
        info("Created properties.yml")

    repo_local = _detect_repo_local()
    repo_remote = _detect_repo_remote()

    lines = _PROPERTIES_FILE.read_text().splitlines(keepends=True)
    lines = _strip_legacy_section(lines, "screenshots")
    _replace_scalar(lines, "repo", "local", repo_local)
    if repo_remote:
        _replace_scalar(lines, "repo", "remote", repo_remote)
    _stamp_template_parent(lines, repo_local, repo_remote)
    _PROPERTIES_FILE.write_text("".join(lines))

    success(f"properties.yml: repo.local = {repo_local}")
    if repo_remote:
        success(f"properties.yml: repo.remote = {repo_remote}")
    else:
        info("No git remote 'origin' found — repo.remote left unchanged")


if __name__ == "__main__":
    main()
