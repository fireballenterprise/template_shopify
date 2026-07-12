"""Bump the repo's VERSION file for development deploys and releases."""

from invoke import task

from modules.version import bump as bump_module


@task
def bump_build(_context):
    """Advance VERSION for a dev deploy (new minor's first build, or next build number)"""
    bump_module.bump_build()


@task
def bump_release(_context):
    """Finalize VERSION for release by dropping the build suffix"""
    bump_module.bump_release()
