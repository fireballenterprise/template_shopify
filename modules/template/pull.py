"""
Resolve the local path to this repo's parent template repo for /template pull.

Prints the resolved path on its own line, prefixed `TEMPLATE_PATH=`, so the calling prompt can
parse it out of any other status output.

Usage:
    uv run --no-sync python -m modules.template.pull
"""

from __future__ import annotations

from ..common import cli as click
from .resolve import resolve_template_repo


@click.command()
def main() -> None:
    """Resolve and print the local path to the shared template repo."""
    local = resolve_template_repo()
    click.echo(f"TEMPLATE_PATH={local}")


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
