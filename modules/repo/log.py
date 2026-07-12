"""Save repository session logs to markdown files."""

from __future__ import annotations

from datetime import datetime

from ..common import cli as click
from ..common.properties import get_repo_local
from ..common.utils import create_slug, error, success


def main(title: str | None = None, content: str | None = None) -> None:
    """Save a repository log markdown file in logs/."""
    repo_root = get_repo_local()
    logs_dir = repo_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    if not title:
        title = click.prompt("Log title", type=str)

    if not title or not title.strip():
        error("Log title cannot be empty")

    now = datetime.now().astimezone()
    log_stamp = now.strftime("%Y%m%d%H%M")
    slug = create_slug(title)
    filename = f"{log_stamp}_{slug}.md"

    if content and content.strip():
        body = content.strip()
    else:
        body = (
            "## Summary\n\n"
            "[Repo coding work only]\n\n"
            "## Code Changes\n\n"
            "- [Files/modules updated]\n\n"
            "## Validation\n\n"
            "- [Tests/lint run and results]\n\n"
            "## Notes\n\n"
            "[Exclude unrelated chat/topic detours]"
        )

    file_content = f"# {title}\n\nDate: {now.isoformat(timespec='seconds')}\n\n{body}\n"

    log_file = logs_dir / filename
    log_file.write_text(file_content)

    success(f"Saved log: logs/{filename}")


if __name__ == "__main__":
    main()
