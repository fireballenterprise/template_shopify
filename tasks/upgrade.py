"""Upgrade tasks — install Python/library upgrades reviewed via ver.update (installs; run ver.update first)."""

from invoke import task

from modules.versioning import upgrade as upgrade_module


@task(default=True)
def all(_context, yes=False):  # noqa: A001  # pylint: disable=redefined-builtin
    """Upgrade Python and libraries (installs new Python if needed, rebuilds .venv, runs uv sync --upgrade)"""
    upgrade_module.main(no_confirm=yes, python_only=False, libs_only=False)


@task
def python(_context, yes=False):
    """Upgrade Python only (installs the new version, rebuilds .venv)"""
    upgrade_module.main(no_confirm=yes, python_only=True, libs_only=False)


@task
def libs(_context, yes=False):
    """Upgrade libraries only (uv sync --upgrade)"""
    upgrade_module.main(no_confirm=yes, python_only=False, libs_only=True)


@task
def sync(_context):
    """Sync dependencies without checking for updates first (uv sync --upgrade)"""
    upgrade_module.run_uv_sync()
