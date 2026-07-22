"""Bump the repo's VERSION file for development deploys and releases.

Task names (`version.bump_build`/`version.bump_release`) are kept stable — the reusable
`fireballenterprise/workflows` deploy.yml/release.yml call them by these exact names
(`uv run --no-sync invoke version.bump_build`/`version.bump_release`), so renaming them here
would break deploys across every repo using that shared workflow.
"""

from invoke import task

from modules.versioning import project as project_module


@task
def bump_build(_context):
    """Advance VERSION for a dev deploy (new minor's first build, or next build number)"""
    project_module.bump_build()


@task
def bump_release(_context):
    """Finalize VERSION for release by dropping the build suffix"""
    project_module.bump_release()
