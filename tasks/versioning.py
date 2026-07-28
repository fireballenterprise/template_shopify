"""Version-lock checks (pyproject.toml deps, workflow actions, Python) and repo VERSION-file bumps."""

from invoke import task

from modules.versioning import libs as libs_module
from modules.versioning import project as project_module
from modules.versioning import python as python_module
from modules.versioning import upgrade as upgrade_module
from modules.versioning import workflows as workflows_module


@task
def libs(_context, dry_run=False, yes=False):
    """Check pyproject.toml dependencies against latest releases and update version locks"""
    libs_module.main(dry_run=dry_run, no_confirm=yes)


@task
def python(_context, dry_run=False, yes=False):
    """Check the pinned Python version against the latest stable release and update config refs"""
    python_module.main(dry_run=dry_run, no_confirm=yes)


@task
def workflows(_context, dry_run=False, yes=False):
    """Check .github/workflows/ action refs against latest major versions and update them"""
    workflows_module.main(dry_run=dry_run, no_confirm=yes)


@task
def all(context, dry_run=False, yes=False):  # noqa: A001  # pylint: disable=redefined-builtin
    """Run every version check (libs, workflows)"""
    libs(context, dry_run=dry_run, yes=yes)
    workflows(context, dry_run=dry_run, yes=yes)


@task
def update(context, dry_run=False, yes=False):
    """Run every version check (libs, python, workflows) — each section runs even if an earlier one exits early"""
    for check in (libs, python, workflows):
        try:
            check(context, dry_run=dry_run, yes=yes)
        except SystemExit:
            pass


@task
def upgrade(_context, yes=False):
    """Install the Python/library upgrades reviewed via ver.update (installs; rebuilds .venv if Python changed)"""
    upgrade_module.main(no_confirm=yes, python_only=False, libs_only=False)


@task
def project_bump_build(_context):
    """Advance VERSION for a dev build (new minor's first build, or next build number)"""
    project_module.bump_build()


@task
def project_bump_release(_context):
    """Finalize VERSION for release by dropping the build suffix"""
    project_module.bump_release()
