# Template Module

Syncs shared, generic tooling between this repo and its **parent template repo** via
`/template`. The parent is configured in `properties.yml` (stamped automatically by
`inv setup.properties` when GitHub's generated-from link is available):

```yaml
template:
  local: "$HOME/path/to/parent-template-repo"
  remote: "github.com/<user>/<parent-template-repo>"
```

## The chain

```
root skeleton  →  domain template  →  project repo
```

Repos form a chain, and each repo syncs **only with its direct parent**. A domain template absorbs
the root skeleton's updates by running `/template` inside itself (its own `properties.yml`
points at the root skeleton) — never from further down the chain. To move a change across the whole
chain, sync it one hop at a time: push it up to the parent, then run `/template push` inside
the parent to continue upward (or pull downward hop by hop).

## Usage

```sh
uv run --no-sync python -m modules.template.route "pull resolve"  # pull, phase 1
uv run --no-sync python -m modules.template.route "pull copy"     # pull, phase 2 (local only)
uv run --no-sync python -m modules.template.route "push diff"     # push, phase 1
```

`/template` (the prompt) drives the flow above directly. `tasks/template.py` also exposes thin
invoke wrappers around the same functions, for manual use outside the prompt:

```sh
uv run --no-sync invoke template.pull
uv run --no-sync invoke template.pull_copy
uv run --no-sync invoke template.push_diff
uv run --no-sync invoke template.push_apply --files=modules/foo.py,tasks/foo.py --deletes=modules/old.py
uv run --no-sync invoke template.push_create_pr --branch=sync-from-repo-20260101-000000 --title="..." --body="..."
```

## Pull

`pull resolve` resolves `template.local` from `properties.yml`. If that path exists on disk, it's
used directly — no `git pull` is run, since the assumption is you already pushed your changes
there before running `/template` here. If the local path isn't found (e.g. a different machine or
CI), it shallow-clones `template.remote` into `tmp/template_sync/` instead. Either way, it prints
`TEMPLATE_PATH=<path>` and `TEMPLATE_LOCAL=<true|false>` so the `/template` prompt can parse them
out of any other output.

When the template repo is local (`TEMPLATE_LOCAL=true`), `pull copy` does the actual sync
deterministically — no AI-driven diffing:

1. Lists every git-tracked file in the parent (`git ls-files`, so the parent's own gitignored/
   untracked junk -- caches, build artifacts, `.venv/`, etc. -- is skipped automatically; nothing
   about that is hardcoded here).
2. Drops anything matched by this project's `template.ignore.yml` `exclude:` list -- the only
   other exclusion mechanism, covering everything project-specific the parent has no equivalent of
   (`properties.yml`, `README.md`, business modules, personal-vault content, and its own filename
   so local customizations survive future pulls).
3. Overwrites every remaining file outright — text files get the parent's name rewritten to this
   repo's name via `modules/template/naming.py` (the same rename helper `push` uses, in reverse);
   binary files copy as-is. No per-file diff or confirmation: the working tree is git-tracked, so
   the result is reviewed with `git status`/`git diff` afterward, not gated before the write.

When the template repo isn't local, or the user explicitly asks for a manual/diff review instead,
the file-by-file comparison, classification (shared tooling vs. project-specific), and conflict
resolution happens in the `/template` prompt itself, not here — see
`.github/prompts/template.prompt.md`.

## Push

Proposes new generic improvements from this repo (in `modules/`, `.github/instructions/`,
`.github/prompts/`, `.claude/commands/`, `.claude/skills/`, `.clinerules/workflows/`) into the
parent template repo as a pull request. Candidates come from `git ls-files` (so this repo's own
`.gitignore` is already applied) filtered again by `template.ignore.yml` -- the same file `pull`
uses, applied in reverse so project-specific content (business modules, personal-vault content,
...) never leaks upstream. See `modules/template/scope.py`.

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
uv run --no-sync python -m modules.template.route ["pull <mode>" | "push <mode> ..."]
  ↓
modules/template/route.py
  ↓                                              ↓
modules/template/pull.py                   modules/template/push.py
  ↓ resolve          ↓ copy                      ↓ diff / apply / create-pr
  │                  modules/template/ignore.py  modules/template/scope.py
  │                  (template.ignore.yml only   (INCLUDE_DIRS + git ls-files +
  │                   -- .gitignore is handled    template.ignore.yml via ignore.py)
  │                   via git ls-files, not
  │                   hardcoded)
  │                  ↓
  │                  modules/template/naming.py  ←──────────────────┘
  │                  (shared repo-name rewrite, used by both pull and push)
  ↓                  ↓
modules/template/resolve.py  ←──────────────────────────────────────┘
(shared local-path-or-clone resolution)
  ↓
properties.yml (template.local / template.remote)  →  TEMPLATE_PATH=<resolved path>
```
