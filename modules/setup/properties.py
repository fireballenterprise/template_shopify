"""
Create properties.yml (this machine's repo path, git remote, and template lineage) on first run.

Run via `inv setup.properties` (called automatically by setup.sh). A no-op if properties.yml
already exists — this only ever creates the file, never rewrites it. To regenerate (e.g. after
moving the repo, renaming it, or forking it to a new remote), delete or rename properties.yml
first, then run again.

properties.yml is gitignored. It's assembled from every tier fragment under
`modules/setup/templates/properties/*.yml` — one file per repo in the lineage, each named after
itself: `template_python.yml` (the root — repo, template, and its own repos entry), down through
`template_ai_vault.yml` (icloud, screenshots: generic to the ai_vault product line, tracked and
synced via /template) to `ai_vault.yml` (fireball, financials: this repo's own real business
config, tracked but never synced anywhere since it's a leaf). `repo.local`, `repo.remote`, and
`screenshots.location` (if present) are then stamped in with values detected at creation time.

template.* (this repo's parent template repo, used by /template) is
auto-detected from GitHub's generated-from link when possible, with an
interactive prompt as fallback.

repos (the GitHub org/repo map + template lineage) is built additively, one tier at a time, as you
go down the lineage: each fragment contributes just its own org/repo + the lineage edge to its
parent, deep-merged into whatever earlier tiers contributed. A repo only ever ends up knowing its
own ancestor chain — never a sibling branch it isn't descended from (e.g. this repo never learns
about the separate template_shopify branch, since no fragment here declares it).
"""

import re
import subprocess
from pathlib import Path
from typing import Any

import yaml

from modules.common import cli
from modules.common.utils import info, success

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_PROPERTIES_FILE = _REPO_ROOT / "properties.yml"
_TEMPLATES_DIR = Path(__file__).resolve().parent / "templates" / "properties"

_TEMPLATE_LOCAL_PLACEHOLDER = "$HOME/path/to/your/template/repo"
_TEMPLATE_REMOTE_PLACEHOLDER = "github.com/<your-username>/<your-template-repo>"


def _extract_repos_block(text: str) -> tuple[str, dict[str, Any] | None]:
    """Split a top-level `repos:` block out of raw YAML text.

    Returns (text with that block removed, its parsed value) — or (text, None) if there's no
    `repos:` block (a flow-style `repos: {}` placeholder doesn't count as one to extract).
    """
    lines = text.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.rstrip("\n") == "repos:":
            end = i + 1
            while end < len(lines) and (not lines[end].strip() or lines[end][0].isspace()):
                end += 1
            block = "".join(lines[i:end])
            remaining = "".join(lines[:i] + lines[end:])
            return remaining, yaml.safe_load(block)["repos"]
    return text, None


def _merge_repos(accumulated: dict[str, Any], addition: dict[str, Any]) -> dict[str, Any]:
    """Deep-merge one tier's repos contribution into the map accumulated from earlier tiers.

    Org lists are extended (no duplicates); `lineage` entries are merged key by key.
    """
    merged = {org: list(names) for org, names in accumulated.items() if org != "lineage"}
    lineage = dict(accumulated.get("lineage", {}))
    for org, names in addition.items():
        if org == "lineage":
            lineage.update(names)
            continue
        merged.setdefault(org, [])
        for name in names:
            if name not in merged[org]:
                merged[org].append(name)
    if lineage:
        merged["lineage"] = lineage
    return merged


def _lineage_depth(repo_key: str, lineage: dict[str, str]) -> int:
    """Return how many lineage hops `org/repo` is from its root (0 for the root itself)."""
    depth = 0
    current = repo_key
    seen: set[str] = set()
    while current in lineage and current not in seen:
        seen.add(current)
        current = lineage[current]
        depth += 1
    return depth


def _render_repos_block(repos: dict[str, Any]) -> str:
    """Render a merged repos dict back into this file's hand-formatted YAML block style.

    Each org's list is ordered root-to-leaf by lineage depth, regardless of merge order.
    """
    lineage = repos.get("lineage", {})
    lines = ["repos:"]
    for org, names in repos.items():
        if org == "lineage":
            continue
        ordered = sorted(names, key=lambda name: _lineage_depth(f"{org}/{name}", lineage))
        lines.append(f"  {org}:")
        lines.extend(f"    - {name}" for name in ordered)
    if lineage:
        lines.append("  lineage:")
        lines.extend(f"    {child}: {parent}" for child, parent in lineage.items())
    return "\n".join(lines) + "\n"


def _build_initial_content() -> str:
    """Assemble a fresh properties.yml from every tier fragment under templates/properties/*.yml.

    Each fragment's own `repos` contribution is deep-merged into the accumulated map (see module
    docstring) rather than concatenated; every other section is appended as raw text, ordered
    root-to-leaf by lineage depth regardless of filename/glob order.
    """
    repos: dict[str, Any] = {}
    fragments: list[tuple[str, str]] = []
    for template_file in sorted(_TEMPLATES_DIR.glob("*.yml")):
        remaining, template_repos = _extract_repos_block(template_file.read_text())
        if template_repos:
            repos = _merge_repos(repos, template_repos)
        if remaining.strip():
            fragments.append((template_file.stem, remaining.rstrip("\n")))

    lineage = repos.get("lineage", {})

    def _fragment_depth(stem: str) -> int:
        for org, names in repos.items():
            if org != "lineage" and stem in names:
                return _lineage_depth(f"{org}/{stem}", lineage)
        return 0

    fragments.sort(key=lambda item: _fragment_depth(item[0]))

    parts = [_render_repos_block(repos).rstrip("\n")]
    parts.extend(text for _, text in fragments)
    return "---\n\n" + "\n\n".join(parts) + "\n"


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
    """Return this repo's parent template as 'github.com/owner/name' via GitHub's generated-from link."""
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


def _has_section(lines: list[str], section: str) -> bool:
    """Return whether a top-level `section:` block exists (e.g. a tier fragment that wasn't present)."""
    return any(line.rstrip("\n") == f"{section}:" for line in lines)


def _prompt_icloud_enabled(lines: list[str]) -> None:
    """Ask (interactively) whether to turn on iCloud sync for a freshly created properties.yml."""
    enabled = cli.confirm(
        "Enable iCloud sync for /push and /pull? (most people don't need this — off by default)",
        default=False,
    )
    _replace_scalar(lines, "icloud", "enabled", "true" if enabled else "false", quote=False)
    if enabled:
        info("iCloud sync enabled — edit icloud.path in properties.yml to your Obsidian vault path")


def _stamp_template_parent(lines: list[str], repo_local: str, repo_remote: str | None) -> str | None:
    """Fill in template.* (the /template parent) while it still holds the placeholder.

    Auto-detects via GitHub's generated-from link, falling back to an interactive prompt.
    A hand-configured (non-placeholder) parent is never touched.

    Returns the parent remote now in effect (existing, detected, or prompted), or None.
    """
    current = _read_scalar(lines, "template", "remote")
    if current not in (None, "", _TEMPLATE_REMOTE_PLACEHOLDER):
        return current

    remote = _detect_template_remote(repo_remote)
    if remote:
        info(f"Detected parent template repo (GitHub generated-from): {remote}")
    elif cli.confirm("Sync shared tooling with a parent template repo via /template?", default=False):
        remote = cli.prompt("Parent template remote (e.g. github.com/<user>/<template-repo>)")

    if not remote:
        info("No parent template repo configured — edit template.* in properties.yml if you add one later")
        return None

    template_local = f"{repo_local.rsplit('/', 1)[0]}/{remote.rstrip('/').rsplit('/', 1)[-1]}"
    _replace_scalar(lines, "template", "remote", remote)
    _replace_scalar(lines, "template", "local", template_local)
    success(f"properties.yml: template.remote = {remote}")
    success(f"properties.yml: template.local = {template_local} (sibling-path guess — edit if it lives elsewhere)")
    return remote


@cli.command()
def main() -> None:
    """Create properties.yml from every tier fragment; a no-op if it already exists."""
    if _PROPERTIES_FILE.exists():
        info("properties.yml already exists — leaving it untouched (delete or rename it to regenerate)")
        return

    _PROPERTIES_FILE.write_text(_build_initial_content())
    info("Created properties.yml")

    repo_local = _detect_repo_local()
    repo_remote = _detect_repo_remote()

    lines = _PROPERTIES_FILE.read_text().splitlines(keepends=True)
    _replace_scalar(lines, "repo", "local", repo_local)
    if repo_remote:
        _replace_scalar(lines, "repo", "remote", repo_remote)
    has_screenshots = _has_section(lines, "screenshots")
    if has_screenshots:
        _replace_scalar(lines, "screenshots", "location", f"{repo_local}/screenshots")
    _stamp_template_parent(lines, repo_local, repo_remote)
    if _has_section(lines, "icloud"):
        _prompt_icloud_enabled(lines)
    _PROPERTIES_FILE.write_text("".join(lines))

    success(f"properties.yml: repo.local = {repo_local}")
    if repo_remote:
        success(f"properties.yml: repo.remote = {repo_remote}")
    else:
        info("No git remote 'origin' found — repo.remote left unchanged")
    if has_screenshots:
        success(f"properties.yml: screenshots.location = {repo_local}/screenshots")


if __name__ == "__main__":
    main()
