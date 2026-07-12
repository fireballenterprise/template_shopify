---
description: "Use when bumping the repo's VERSION file, or editing deploy.yml/release.yml's version jobs. Covers the version.* invoke tasks and the Major.Minor.Patch-Build scheme."
applyTo: "modules/version/**"
---
# Version Instructions

## Purpose
The root `VERSION` file tracks this repo's release version — what gets tagged as a GitHub
Release and deployed to production. This is separate from `pyproject.toml`'s own `[project]
version` field (Python package metadata, unrelated) and from `versioning.instructions.md`'s
`ver.libs`/`ver.workflows` checks (dependency locks and GitHub Action ref pins against external
sources — a different concern entirely).

Scheme: `Major.Minor.Patch[-Build]`
- No build suffix (e.g. `1.0.0`) — a released version, currently what's tagged and live on `main`.
- A build suffix (e.g. `1.1.0-003`) — build `003` toward `1.1.0`, already deployed to the
  `development` Shopify theme, not yet released to `main`/production.

Two operations, one per `version.*` invoke task:
- `version.bump_build` — no build suffix yet -> bump the minor and start build `001`
  (`1.0.0` -> `1.1.0-001`); build suffix present -> increment the build number only
  (`1.1.0-001` -> `1.1.0-002`)
- `version.bump_release` — drop the build suffix (`1.1.0-003` -> `1.1.0`)

See `modules/version/README.md` for full behavior/data-flow details.

## Usage
```sh
uv run --no-sync invoke version.bump_build        # dev deploy: new minor's first build, or next build number
uv run --no-sync invoke version.bump_release     # release: drop the build suffix
```
Both only rewrite `VERSION` and restamp `snippets/fireball-version.liquid` — they don't commit,
branch, or push. `deploy.yml`/`release.yml` handle all git/PR plumbing themselves (same spirit as
the promote (`release.yml`) and `upgrade.yml` inline `git` steps), so the module stays a pure file
operation, easy to reason about and lint independently of git state.

## Relationship to Other Workflows
- **`deploy.yml`** — its first job runs `version.bump_build`, then opens and immediately merges a
  PR carrying the `VERSION` change into `development` (see "Why a PR, Not a Direct Push" below),
  but only when deploying to the **dev** theme (`(inputs.env || 'dev') == 'dev'`). It's skipped
  when `deploy.yml` is called with `env: prd` (from `release.yml`, after its `promote` job) since
  `release.yml` already finalized `VERSION` for that release — bumping it again here would
  double-bump.
- **`release.yml`** — its first job runs `version.bump_release` against `development`, then opens
  and merges the same kind of PR with the finalized version (no build suffix), then feeds that
  value through its `promote` job (which merges the now-finalized `VERSION` into `main`), `deploy.yml`
  (`env: prd`), and the GitHub Release step, which tags `main` as `v<version>`. There's no manual
  `version` input to the workflow — the release version is always whatever `VERSION` resolves to
  once the build suffix is dropped, so the git tag and the `VERSION` file can never disagree.
- Both jobs set `concurrency: version-bump-development` (a name shared across both workflows) so a
  dev-deploy bump and a release finalize can never race on `VERSION` — GitHub queues the second
  run's job until the first's PR has merged.
- All of this uses the default `GITHUB_TOKEN`, which GitHub does not use to trigger new workflow
  runs — squash-merging the `VERSION` PR doesn't cause a second `deploy.yml`/`tests.yml` run.

## Why a PR, Not a Direct Push
`development` has a repo ruleset ("PR to Dev") requiring changes to land via a merged pull
request — a direct `git push origin development` is rejected with `GH013: Repository rule
violations ... Changes must be made through a pull request`, even from a workflow using
`GITHUB_TOKEN`. The ruleset's `required_approving_review_count` is `0` though, so no human
review is actually required — a token with `contents: write` + `pull-requests: write` can open
the PR and merge it (`gh pr merge --squash --delete-branch`) in the same step, immediately. No
bot/app or bypass actor is needed; the fix is routing the change through the PR API instead of a
raw push, not bypassing the rule. `main` has no such rule (only `release.yml`'s `promote` job pushes there,
directly), so that path is unaffected.

## `gh pr create`/`gh pr merge` Need an Explicit `--repo`
This repo is a GitHub fork of `Shopify/dawn`. Without `--repo`, `gh pr create`/`gh pr merge`
resolve the target repo by walking the fork network (to find the parent, in case you meant to
open the PR upstream) — that walk queries `repository.parent`, and the `Shopify` GitHub org has
an IP allow list that blocks GitHub-hosted runner IPs from that query entirely, failing the whole
step with `GraphQL: ... IP address is not permitted to access this resource. (repository.parent)`,
even though the PR only ever targets our own fork. Passing `--repo "${{ github.repository }}"`
skips that fork-network walk. Same fix `modules/repo/pr.py`'s `_gh_repo_slug()` already uses for
`/pr` (`gh pr create --repo ...` from `create_pr()`) — see its docstring comment.

## Run Names Show the Version
Both workflows' `run-name:` is a static placeholder (`"Deploy to ${{ inputs.env || 'dev' }}"`,
`"Release"`) — GitHub evaluates `run-name:` before any job runs, and it can't see job outputs or
file contents, so it can't show the version up front. Each workflow instead renames its own run
mid-flight, once the version is actually known, via `gh api --method PATCH
repos/{owner}/{repo}/actions/runs/{run_id} -f display_title=...`:
- `deploy.yml`'s `deploy` job reads `VERSION` right after checkout (`ref: development` for dev,
  `ref: main` for prd — always the branch that already has the current value) and renames to
  `Deploy to dev (v1.1.0-001)` / `Deploy to prd (v1.1.0)`
- `release.yml`'s `version` job renames to `Release (v1.1.0)` using its own `steps.bump.outputs.version`
- Both need `permissions: actions: write` in addition to `contents: write` — updating a run's
  display title needs its own write scope

## Why `deploy.yml`'s `deploy` Job Checks Out an Explicit `ref`
Without `ref:`, `actions/checkout` pins to the commit that triggered the run, not the branch's
current HEAD. For a dev deploy, `build_version` pushes a new commit to `development` in an earlier
job of the *same* run — the triggering commit is already stale by the time `deploy` starts. Explicit
`ref: development` (dev) / `ref: main` (prd) guarantees `deploy` sees the `VERSION` that job/that
workflow just wrote, not the pre-bump value from whatever originally triggered the run.

## Module Conventions
- Same conventions as `modules.instructions.md` generally, except this module exposes
  `bump_build()`/`bump_release()` (public, no leading `_`) instead of a single `main()` — both are
  equally valid entry points, one per `version.*` invoke task
- Resolve the repo path via `modules.common.properties.get_repo_root()`, not `get_repo_local()`
  — these tasks run in CI, where `get_repo_local()`'s hardcoded local-machine path doesn't exist
- `subprocess.run([...], cwd=repo_path)` never `shell=True`, output via `modules.common.utils`
