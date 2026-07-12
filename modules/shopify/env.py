"""Resolve and export Shopify CLI env vars, sourced from local config or CI secrets."""

import os

from ..common import cli as click
from ..common.properties import (
    get_shopify_local_theme_token,
    get_shopify_store,
    get_shopify_theme_id_dev,
    get_shopify_theme_id_prd,
    is_ci,
)
from ..common.utils import error


def _resolve_token() -> str:
    """Resolve the Shopify CLI theme token from the CI env var, or the local token file."""
    if is_ci():
        return os.environ["SHOPIFY_CLI_THEME_TOKEN"]

    token_file = get_shopify_local_theme_token()
    if not token_file.is_file():
        error(f"Token file not found: {token_file}")
    return token_file.read_text(encoding="utf-8").strip()


def ensure_env() -> None:
    """
    Populate SHOPIFY_FLAG_STORE/SHOPIFY_CLI_THEME_TOKEN/SHOPIFY_THEME_ID_* in os.environ if unset.

    In CI the workflow supplies these directly as env vars from secrets, and each deploy job
    only receives the theme ID it needs — resolving the other one would raise, so CI skips
    the backfill entirely.
    """
    if is_ci():
        return
    os.environ.setdefault("SHOPIFY_FLAG_STORE", get_shopify_store())
    os.environ.setdefault("SHOPIFY_CLI_THEME_TOKEN", _resolve_token())
    os.environ.setdefault("SHOPIFY_THEME_ID_DEV", get_shopify_theme_id_dev())
    os.environ.setdefault("SHOPIFY_THEME_ID_PRD", get_shopify_theme_id_prd())


def main() -> None:
    """Print `export KEY=value` lines for the current shell to eval."""
    ensure_env()
    click.echo(f"export SHOPIFY_FLAG_STORE={os.environ['SHOPIFY_FLAG_STORE']}")
    click.echo(f"export SHOPIFY_CLI_THEME_TOKEN={os.environ['SHOPIFY_CLI_THEME_TOKEN']}")
    click.echo(f"export SHOPIFY_THEME_ID_DEV={os.environ['SHOPIFY_THEME_ID_DEV']}")
    click.echo(f"export SHOPIFY_THEME_ID_PRD={os.environ['SHOPIFY_THEME_ID_PRD']}")


if __name__ == "__main__":
    main()
