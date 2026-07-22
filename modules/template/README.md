# Template Module

Syncs shared, generic tooling between this repo and its **parent template repo** via
`/template`. The parent is configured in `properties.yml` (`template.local` / `template.remote`):

```yaml
template:
  local: "$HOME/path/to/template_python"
  remote: "github.com/LevonBecker/template_python"
```

## The chain

```
template_python  →  template_shopify
```

`template_shopify` syncs only with its direct parent, `template_python`. Shopify/Dawn
theme-specific tooling (`modules/dawn/`, `modules/shopify/`, and their instruction/prompt/command
files) never flows upstream — `template_python` is a generic Python template with no notion of a
Shopify theme. See `modules/template/scope.py` for the exact push scope.

## Usage

```sh
uv run --no-sync python -m modules.template.route              # pull (default)
uv run --no-sync python -m modules.template.route "push diff"  # push, phase 1
```

`/template` (the prompt) drives the flow above directly. `tasks/template.py` also exposes thin
invoke wrappers around the same functions, for manual use outside the prompt:

```sh
uv run --no-sync invoke template.pull
uv run --no-sync invoke template.push_diff
uv run --no-sync invoke template.push_apply --files=modules/foo.py,tasks/foo.py --deletes=modules/old.py
uv run --no-sync invoke template.push_create_pr --branch=sync-from-repo-20260101-000000 --title="..." --body="..."
```

## Pull

Resolves `template.local` from `properties.yml`. If that path exists on disk, it's used directly —
no `git pull` is run, since the assumption is you already pushed your changes there before running
`/template` here. If the local path isn't found (e.g. a different machine or CI), it
shallow-clones `template.remote` into `tmp/template_sync/` instead.

Either way, the resolved path is printed on its own line as `TEMPLATE_PATH=<path>` so the
`/template` prompt can parse it out of any other output.

The actual file-by-file comparison, classification (shared tooling vs. project-specific), and
conflict resolution happens in the `/template` prompt itself, not here — see
`.github/prompts/template.prompt.md`.

## Push

Proposes new generic improvements from this repo (in `modules/`, `.github/instructions/`,
`.github/prompts/`, `.claude/commands/`, `.clinerules/workflows/`, `.opencode/command/`,
`.agents/skills/` — excluding Shopify/Dawn theme-specific content, see
`modules/template/scope.py`) into the parent template repo as a pull request.

Three phases, split at the confirmation boundary so the agent can check in with the user between
each step:

1. `push diff` — enumerates and diffs the scoped candidates against the parent template repo,
   printing `ADDED:`/`MODIFIED:`/`DELETED:` lists.
2. `push apply --file <path> ... [--delete <path> ...]` — for the changes the user approved:
   fetches/updates the parent's default branch, creates a new `sync-from-<repo>-<timestamp>`
   branch, copies the files in (and applies approved deletions), commits, and pushes the branch.
   Does **not** open a PR.
3. `push create-pr --branch <name> [--title ...] [--body ...]` — opens the PR via `gh pr create`.
   Confirms with the user first in interactive runs.

Repo-name references are rewritten on copy (this repo's name → the parent's name, both derived
from `properties.yml` `repo.local`/`template.local` basenames), so name-only differences never
need hand-editing.

## Architecture

```
uv run --no-sync python -m modules.template.route ["pull" | "push <mode> ..."]
  ↓
modules/template/route.py
  ↓                                    ↓
modules/template/pull.py         modules/template/push.py
  ↓                                    ↓
modules/template/resolve.py  ←────┘  (shared local-path-or-clone resolution)
                                       modules/template/scope.py (fixed include/exclude rules)
  ↓
properties.yml (template.local / template.remote)  →  TEMPLATE_PATH=<resolved path>
```
