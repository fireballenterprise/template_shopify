"""Version-lock check tasks — compare pyproject.toml deps and workflow actions against latest releases."""

from invoke import task

from modules.versioning import lib as lib_module
from modules.versioning import workflows as workflows_module


@task
def all(context, dry_run=False, yes=False):  # noqa: A001  # pylint: disable=redefined-builtin
    """Run every version check (libs, workflows)"""
    libs(context, dry_run=dry_run, yes=yes)
    workflows(context, dry_run=dry_run, yes=yes)


@task
def libs(_context, dry_run=False, yes=False):
    """Check pyproject.toml dependencies against latest releases and update version locks"""
    lib_module.main(dry_run=dry_run, no_confirm=yes)


@task
def workflows(_context, dry_run=False, yes=False):
    """Check .github/workflows/ action refs against latest major versions and update them"""
    workflows_module.main(dry_run=dry_run, no_confirm=yes)
