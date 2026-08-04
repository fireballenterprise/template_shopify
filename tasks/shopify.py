"""Shopify theme CI tasks (deploy, env). Dev-time tooling (pull, upgrade, fix) moved to
fireball_orchestrator — see topics/shopify/ there."""

from invoke import task

from modules.shopify import deploy as deploy_module
from modules.shopify import env as env_module


@task
def deploy(_context, env=None):
    """Push local theme to Shopify. Pass env=dev or env=prd."""
    deploy_module.main(env=env)


@task(name="env")
def print_env(_context):
    """Print `export KEY=value` Shopify CLI env vars — use: eval "$(uv run --no-sync invoke shopify.env)" """
    env_module.main()
