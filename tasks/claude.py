"""Claude Code command sync task."""

from invoke import task

from modules.claude import sync as sync_module


@task
def sync(_context, force=False):
    """Sync .claude/commands/ from .github/prompts/ source of truth"""
    sync_module.main(force=force)
