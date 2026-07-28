---
name: template
description: Pull shared tooling updates from the parent template repo into this project (default), or push new generic tooling from this project into the parent template repo as a PR (template push).
argument-hint: "[pull [diff]|push]"
agent: agent
---

If `$ARGUMENTS` is empty or "pull", do a **Pull**. If `$ARGUMENTS` starts with "push", do a
**Push**. If `$ARGUMENTS` is "pull diff" (or the user otherwise asks for a manual/diff review),
use Pull's fallback path (step 3) instead of its default copy.

## Pull

1. Resolve the template repo and check whether it's a local checkout:

   !`uv run --no-sync python -m modules.template.route "pull resolve"`

   Parse `TEMPLATE_PATH=` (the resolved local path, cloned to `tmp/template_sync/` if not found
   locally) and `TEMPLATE_LOCAL=` (`true`/`false`) from the output.

2. **Default path — `TEMPLATE_LOCAL=true` and the user didn't ask for a manual/diff review:**
   using the Bash tool, run `uv run --no-sync python -m modules.template.route "pull copy"`. This
   clobber-copies every git-tracked file from the template repo into this project, skipping:
   - the built-in safety excludes in `modules/template/ignore.py` (`properties.yml`,
     `properties.yml.example`, `README.md`, `LICENSE`, `uv.lock`, `pyproject.toml`, `VERSION`,
     `.claude/settings.local.json`, `template.ignore.yml`, and cache/build dirs like `.git/`,
     `.venv/`, `__pycache__/`, `logs/`, `tmp/`)
   - anything listed in this project's `template.ignore.yml` `exclude:` list — add project-specific
     content directories there (e.g. `topics/`, `active_topic.yml`) so future pulls leave them alone
   Text files get the template repo's name rewritten to this repo's name (basenames of
   `template.local`/`repo.local` in `properties.yml`); binary files copy as-is. Every other synced
   file is overwritten outright — no per-file diff or confirmation.

   Afterward, run `git status` and summarize what changed (added/modified) so the user can review
   and correct with normal git tools — the copy only touches the working tree, so nothing is
   committed or pushed and mistakes are just a `git checkout`/edit away.

3. **Fallback — `TEMPLATE_LOCAL=false`, or the user explicitly asked for a manual/diff review:**
   compare the template repo against this project by hand instead of running `pull copy`. Slower
   and less complete than the copy above; prefer it only when there's no local template checkout.

   a. **Always exclude** (never touch, even if present in the template repo): everything in step
      2's built-in safety excludes, plus this project's `template.ignore.yml` `exclude:` list.
   b. **Shared tooling — sync these by default** if present in the template repo: `modules/`,
      `tasks/`, `.github/instructions/`, `.github/prompts/`, `.github/workflows/`,
      `.claude/commands/`, `.vscode/`, `invoke.yml`, `setup.sh`, `CLAUDE.md`, `.editorconfig`,
      `.yamllint`. Also look at anything else at the template repo's top level not covered by the
      exclude list — use judgment on whether it's generic tooling or project-specific, and ask the
      user if genuinely unsure.
   c. For each candidate file:
      - Missing in this project → propose adding it.
      - Identical to what's already here → skip silently.
      - Different from what's already here → show a short diff and ask the user whether to
        overwrite, keep the local version, or merge by hand. Do not overwrite silently.
   d. Apply only the changes the user approved (plus unambiguous additions/identical-skips), then
      summarize what was added, updated, and skipped.

4. If `.github/prompts/` changed (either path), mirror the same changes into `.claude/commands/`
   and `.clinerules/workflows/` by hand — see `.github/instructions/prompts.instructions.md` for
   the required frontmatter/body per tool. There is no sync task; these dirs are hand-maintained.

## Push

Push proposes NEW generic improvements made in this repo into its parent template repo as a pull
request. Only genuinely generic, non-business content may be proposed — never fireball/
product-metadata content.

**Scope** (enforced by `modules/template/scope.py`, mirrored here for visibility):
- Eligible directories: `modules/`, `.github/instructions/`, `.github/prompts/`,
  `.claude/commands/`, `.clinerules/workflows/`, `.agents/skills/`.
- Always excluded everywhere: `topics/`, `properties.yml`, `active_topic.yml`,
  `uv.lock`, `README.md`, `LICENSE`, `pyproject.toml`, `.claude/settings.local.json`, `.git/`,
  `.venv/`, `__pycache__/`, `.ruff_cache/`, `logs/`, `tmp/`.
- Always excluded business content: `modules/fireball/`, `modules/financials/`,
  `.agents/skills/fireball/`, `.agents/skills/product-metadata/`,
  `.github/instructions/travel.instructions.md`,
  `.github/instructions/product_metadata.instructions.md`, and every prompt/command/workflow
  file for `add_expense`, `add_size_chart`, `calc_cost`, `list_expenses`, `financials`,
  `update_card_limit`, `fireball`, `new_product_metadata`.

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
     obsolete. When unsure whether something is deprecated or template-specific, ask the user.
   - For borderline generic-vs-business content not already covered by the fixed exclusion list,
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
