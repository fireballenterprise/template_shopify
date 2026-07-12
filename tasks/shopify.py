"""Shopify theme workflow tasks (pull, deploy, upgrade, fix, env)."""

from invoke import task

from modules.shopify import deploy as deploy_module
from modules.shopify import env as env_module
from modules.shopify import pull as pull_module
from modules.shopify import upgrade as upgrade_module


@task
def deploy(_context, env=None):
    """Push local theme to Shopify. Pass env=dev or env=prd."""
    deploy_module.main(env=env)


@task(name="env")
def print_env(_context):
    """Print `export KEY=value` Shopify CLI env vars — use: eval "$(uv run --no-sync invoke shopify.env)" """
    env_module.main()


@task
def fix(context):
    """Auto-correct Shopify theme-check offenses"""
    print("\n------------")
    print("Shopify Theme Fix")
    print("------------\n")
    context.run("shopify theme check --auto-correct")


@task
def pull(_context, env=None, theme=None):
    """Pull live theme from Shopify store to local branch. Pass env=dev, env=prd, or theme=<name_or_id>."""
    pull_module.main(env=env, theme=theme)


@task
def upgrade(_context):
    """Upgrade dawn_vanilla from upstream Shopify/dawn, then merge into development"""
    upgrade_module.main()
