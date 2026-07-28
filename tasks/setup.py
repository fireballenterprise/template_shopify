"""Repo bootstrap tasks — called by setup.sh, safe to re-run any time."""

from invoke import task

from modules.common.shopify import ensure_shopify_section


@task
def properties(context):
    """Create/stamp properties.yml with this machine's repo path and git remote"""
    context.run("python -m modules.setup.properties")
    ensure_shopify_section()
