"""Common utilities for shopify_dawn_theme automation."""

import re
import sys
from typing import NoReturn


def success(message: str) -> None:
    """Print success message with emoji prefix."""
    print(f"✅ {message}")


def error(message: str, exit_code: int = 1) -> NoReturn:
    """Print error message to stderr and exit."""
    print(f"❌ {message}", file=sys.stderr)
    sys.exit(exit_code)


def warning(message: str) -> None:
    """Print warning message with emoji prefix."""
    print(f"⚠️ {message}")


def info(message: str) -> None:
    """Print info message with emoji prefix."""
    print(f"📂 {message}")


def create_slug(text: str) -> str:
    """
    Convert text to a URL/filename-safe slug.

    Lowercases the text, strips characters that are not alphanumeric, hyphens,
    or spaces, then collapses whitespace runs into single underscores.

    Args:
        text: The input string to slugify.

    Returns:
        A lowercase slug with spaces replaced by underscores.
    """
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "_", text.strip())
    return text
