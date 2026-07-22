"""
Bump the repo's VERSION file for development deploys, or finalize it for release.

VERSION tracks `Major.Minor.Patch[-Build]`. No build suffix means a released version
(e.g. `1.0.0`); a build suffix (e.g. `1.1.0-003`) means builds are in progress toward that
Major.Minor.Patch but it hasn't shipped yet. See `version.instructions.md` for the full rules.

Every write also restamps `snippets/fireball-version.liquid`, the theme snippet that renders
the version as an HTML comment on the home page, so the deployed theme reports its version.

Usage:
    uv run --no-sync invoke ver.project_bump_build      # dev deploy: new minor, or next build number
    uv run --no-sync invoke ver.project_bump_release    # release: drop the build suffix
"""

from __future__ import annotations

import re
from pathlib import Path

from ..common.properties import get_repo_root
from ..common.utils import error, success

_VERSION_PATTERN = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:-(\d+))?$")
_SNIPPET_STAMP_PATTERN = re.compile(r"(?<=<!-- Fireball Dawn Theme v)\d+\.\d+\.\d+(?:-\d+)?(?= -->)")
_BUILD_WIDTH = 3


def _version_file(repo_root: Path) -> Path:
    """Path to the repo's VERSION file."""
    return repo_root / "VERSION"


def _snippet_file(repo_root: Path) -> Path:
    """Path to the theme snippet that stamps the version into rendered pages."""
    return repo_root / "snippets" / "fireball-version.liquid"


def _read(repo_root: Path) -> tuple[int, int, int, int | None]:
    """Read and parse VERSION into (major, minor, patch, build)."""
    version_file = _version_file(repo_root)
    if not version_file.is_file():
        error(f"VERSION file not found at {version_file}")

    raw = version_file.read_text(encoding="utf-8").strip()
    match = _VERSION_PATTERN.match(raw)
    if not match:
        error(f"VERSION contents {raw!r} don't match Major.Minor.Patch[-Build]")

    major, minor, patch, build = match.groups()
    return int(major), int(minor), int(patch), int(build) if build else None


def _write(repo_root: Path, version: str) -> None:
    """Overwrite VERSION with a new value and restamp the theme's version snippet."""
    _version_file(repo_root).write_text(f"{version}\n", encoding="utf-8")

    snippet_file = _snippet_file(repo_root)
    if not snippet_file.is_file():
        error(f"Version snippet not found at {snippet_file}")
    stamped, count = _SNIPPET_STAMP_PATTERN.subn(version, snippet_file.read_text(encoding="utf-8"))
    if count != 1:
        error(f"Expected exactly one version stamp in {snippet_file}, found {count}")
    snippet_file.write_text(stamped, encoding="utf-8")


def bump_build() -> str:
    """
    Advance VERSION for a development deploy.

    No build suffix yet (freshly released, e.g. `1.0.0`) -> start the next minor's first
    build: `1.1.0-001`. Build suffix already present -> increment the build number only,
    keeping Major.Minor.Patch fixed: `1.1.0-001` -> `1.1.0-002`.
    """
    repo_root = get_repo_root()
    major, minor, patch, build = _read(repo_root)
    if build is None:
        minor, patch, build = minor + 1, 0, 1
    else:
        build += 1

    new_version = f"{major}.{minor}.{patch}-{build:0{_BUILD_WIDTH}d}"
    _write(repo_root, new_version)
    success(f"VERSION bumped to {new_version}")
    return new_version


def bump_release() -> str:
    """Finalize VERSION for release by dropping the build suffix (`1.1.0-003` -> `1.1.0`)."""
    repo_root = get_repo_root()
    major, minor, patch, _build = _read(repo_root)
    new_version = f"{major}.{minor}.{patch}"
    _write(repo_root, new_version)
    success(f"VERSION finalized to {new_version}")
    return new_version


if __name__ == "__main__":
    bump_build()
