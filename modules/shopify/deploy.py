"""Push local theme files to a Shopify theme (dev or prd)."""

import subprocess

from ..common import cli as click
from ..common.properties import get_shopify_store, get_shopify_theme_id
from ..common.utils import error, success
from .env import ensure_env


def main(env: str) -> None:
    """Push local theme files to the given environment's Shopify theme ('dev' or 'prd')."""
    ensure_env()

    try:
        theme_id = get_shopify_theme_id(env)
    except ValueError as exc:
        error(str(exc))

    store = get_shopify_store()

    command = ["shopify", "theme", "push", "--force", f"--theme={theme_id}", f"--store={store}"]
    if env == "prd":
        command.append("--allow-live")

    click.echo(f"Pushing local theme to {env} (theme {theme_id}) on {store}...")

    # shopify CLI requires a live TTY for auth and progress output — subprocess without
    # capturing stdio is intentional so it inherits the parent's TTY/CI log stream.
    result = subprocess.run(command, check=False)
    if result.returncode != 0:
        error("shopify theme push failed.")

    success(f"Deployed to {env}.")
