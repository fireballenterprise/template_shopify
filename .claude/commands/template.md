---
description: Pull shared tooling updates from the parent template repo into this project (default), or push new generic tooling from this project into the parent template repo as a PR (template push).
subtask: false
agent: general
slash_command: /template
allowed-tools: Bash(uv run --no-sync *), Bash(gh pr create *)
---

If `$ARGUMENTS` is empty or "pull", do a **Pull**. If `$ARGUMENTS` starts with "push", do a **Push**.

Locate the shared template repo by running `uv run --no-sync python -m modules.template.route`
using the Bash tool. If it fails, show the full output to the user and ask how they'd like to
proceed. Otherwise, parse the `TEMPLATE_PATH=` line from its output for the resolved local path to
the template repo (cloned to `tmp/template_sync/` if it wasn't found locally). Both Pull and Push
use this path.

## Pull

Compare that template repo against this project and sync it in:

1. **Always exclude** (never touch, even if present in the template repo): `properties.yml`,
   `README.md`, `LICENSE`, `uv.lock`, `pyproject.toml`, `.claude/settings.local.json`, `.git/`,
   `.venv/`, `__pycache__/`, `.ruff_cache/`, any other cache/build artifact, anything under
   `logs/` or `tmp/`, and this project's own Shopify theme content (`assets/`, `config/`,
   `layout/`, `locales/`, `sections/`, `snippets/`, `templates/`, `docs/`) — the template repo has
   no equivalent of these, but never touch them regardless.
2. **Shared tooling — sync these by default** if present in the template repo: `modules/`,
   `tasks/`, `.github/instructions/`, `.github/prompts/`, `.github/workflows/`,
   `.claude/commands/`, `.vscode/`, `invoke.yml`, `setup.sh`, `CLAUDE.md`, `.editorconfig`,
   `.yamllint`. Also look at anything else at the template repo's top level that isn't covered by
   the exclude list — use judgment on whether it's generic tooling or project-specific, and ask
   the user if genuinely unsure.
3. For each candidate file:
   - Missing in this project → propose adding it.
   - Identical to what's already here → skip silently.
   - Different from what's already here → show a short diff and ask the user whether to overwrite,
     keep the local version, or merge by hand. Do not overwrite silently.
4. Apply only the changes the user approved (plus unambiguous additions/identical-skips), then
   summarize what was added, updated, and skipped.
5. If `.github/prompts/` changed, remind the user to run `uv run --no-sync invoke claude.sync`
   (add `--force` to overwrite hand-crafted `.claude/commands/`) afterward — do not run it
   automatically.

Never modify `pyproject.toml`, `properties.yml`, `README.md`, `LICENSE`, or `uv.lock` even if the
template repo's versions differ from this project's — those are always project-specific and must
be reconciled by hand.

## Push

Push proposes NEW generic improvements made in this repo into its parent template repo as a pull
request. Only genuinely generic, non-theme content may be proposed — never Dawn/Shopify
theme-specific content.

**Scope** (enforced by `modules/template/scope.py`, mirrored here for visibility):
- Eligible directories: `modules/`, `.github/instructions/`, `.github/prompts/`,
  `.claude/commands/`, `.clinerules/workflows/`, `.opencode/command/`, `.agents/skills/`.
- Always excluded everywhere: `properties.yml`, `active_topic.yml`, `topics/`, `screenshots/`,
  `uv.lock`, `README.md`, `LICENSE`, `pyproject.toml`, `.claude/settings.local.json`, `.git/`,
  `.venv/`, `__pycache__/`, `.ruff_cache/`, `logs/`, `tmp/`.
- Always excluded Dawn/Shopify theme-specific content: `modules/dawn/`, `modules/shopify/`,
  `.github/instructions/dawn.instructions.md`, `.github/instructions/shopify.instructions.md`,
  `.github/instructions/fireball.instructions.md`, and every prompt/command/workflow file for
  `dawn` and `shopify` — `template_python` is a generic Python template with no notion of a
  Shopify theme.

Repo-name references are rewritten automatically on copy (this repo's name → the template repo's
name, both derived from `properties.yml` `repo.local`/`template.local` basenames), so name-only
differences never need hand-editing and never count as modifications.

**Steps:**

1. Using the Bash tool, run `uv run --no-sync python -m modules.template.route "push diff"`.
   This clones/updates the template default branch and prints three scope-filtered lists:
   - `ADDED:` — in this repo, missing from the template.
   - `MODIFIED:` — differs from the template after repo-name rewriting.
   - `DELETED:` — in the template but no longer in this repo. These are deprecation candidates
     only; nothing is deleted without explicit approval in step 3.
2. Review all three lists and assemble the FULL change set for one complete PR:
   - Pair up renames: an ADDED file that replaces a DELETED one (e.g. a renamed command) should
     ship together — the add and the delete in the same PR, plus a scan of the template's docs
     for now-dangling references to the deleted name (fix those template-side files in step 4's
     review if needed).
   - Only propose a deletion when its replacement is included in this PR or the file is clearly
     obsolete. When unsure whether something is deprecated or project-specific, ask the user.
   - For borderline generic-vs-theme content not already covered by the fixed exclusion list,
     ask the user before including it. Drop anything the user doesn't want.
3. Show the user the final change set — files to add, update, and delete — with a one-line
   summary of what changed, and ask them to confirm proposing it to the template repo.
4. If approved, using the Bash tool, run (once, with one `--file` per approved copy and one
   `--delete` per approved removal):
   `uv run --no-sync python -m modules.template.route "push apply --file <path1> --file <path2> --delete <path3> ..."`
   This resolves/updates the local template checkout, creates a new branch, copies the approved
   files (with repo-name rewriting), applies the deletions, commits, and pushes the branch — it
   does **not** open a PR yet. Note the `TEMPLATE_PUSH_BRANCH=` and `TEMPLATE_PUSH_BASE=` values
   it prints. `--delete` refuses paths outside the push scope.
5. Show the user the pushed branch name and propose a PR title/body covering adds, updates, AND
   deletions. **Explicitly ask the user to confirm before opening the PR** — do not proceed
   without an explicit "yes".
6. Only after confirmation, using the Bash tool, run:
   `uv run --no-sync python -m modules.template.route "push create-pr --branch <branch> --title \"...\" --body \"...\""`
   This opens the PR against the template repo via `gh pr create`.
