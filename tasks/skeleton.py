"""Skeleton sync task — locates the shared repo_setup_python skeleton for /sync-setup."""

from invoke import task

from modules.skeleton import sync as sync_module


@task
def locate_source(_context):
    """Resolve the local path to the shared skeleton repo (clone from remote if not found locally)"""
    sync_module.main()
