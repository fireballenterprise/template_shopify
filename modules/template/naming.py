"""Repo-name rewriting shared by /template push and pull."""

from __future__ import annotations

_REPLACE_PLACEHOLDER = "\x00TEMPLATE_NAME\x00"


def rewrite_repo_references(content: str, old_name: str, new_name: str) -> str:
    """
    Replace references to old_name with new_name.

    Safe when one name contains the other (e.g. template_my_vault contains my_vault):
    existing new_name occurrences are masked with a placeholder first so they
    survive the replacement untouched.
    """
    if not old_name or old_name == new_name:
        return content
    masked = content.replace(new_name, _REPLACE_PLACEHOLDER)
    masked = masked.replace(old_name, new_name)
    return masked.replace(_REPLACE_PLACEHOLDER, new_name)
