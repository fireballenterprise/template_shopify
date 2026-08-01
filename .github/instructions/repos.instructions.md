---
applyTo: "**"
---
# Repos Instructions
Rules for the `repos` key in `properties.yml` — the map of GitHub repos related to this repository.

## Purpose
`properties.yml`'s `repos` key records which other GitHub repos are part of this repo's family
(grouped by org), plus a `lineage` sub-key recording parent → child template-stamping
relationships — e.g. `fireballenterprise/template_shopify: LevonBecker/template_python` means
`template_shopify` was stamped from `template_python`.

It's built additively, tier by tier, from `modules/setup/templates/properties/*.yml` — one fragment
file per repo in the lineage, each named after itself. This repo (`template_shopify`) is a mid-tier
template: its own fragment, `template_shopify.yml`, holds its own `repos` entry (with the lineage
edge to `template_python`) plus `shopify.local_config`, generic to every Shopify-line repo
descended from here. Each fragment contributes only its own org/repo + the lineage edge to its
parent; a repo only ever ends up knowing its own ancestor chain, never a sibling branch it isn't
descended from (e.g. this repo never learns about the separate `template_ai_vault` branch). See
`modules/setup/README.md` for the build mechanism.

## "Related Repos" Trigger
When the user says **"related repos"**, **"the repos"**, **"other repos"**, **"all of the repos"**,
**"all the repos"**, or similar in the context of this repo's family — not generic talk about "the
repository" — **read this file in full before acting**, then read the `repos` key in
`properties.yml` to know which other repos are part of this repo's family and how they're related.
This applies whether or not the user ran `/repos` — the phrase itself is the trigger.

Two distinct requests look similar but aren't:
- **"What are the related repos?"** — just resolve and show the `repos`/`lineage` map (`/repos`
  does this).
- **"Apply this to the related/other repos"** vs. **"apply this to all of the repos"** — both run
  the Cross-Repo Change Workflow below, but scope differs:
  - "related repos" / "other repos" — the *other* repos in the family; this repo is assumed already
    handled (e.g. its own PR already exists).
  - "all of the repos" / "all the repos" — **includes this repo too**. If this repo's own change
    isn't committed/pushed/PR'd yet, do that first (same format as every other repo — commit, push,
    PR), then continue through the rest of the family in lineage order.

## Cross-Repo Change Workflow
When the user asks to apply a change (already made in this repo, or described fresh) to the related
repos, run it as **two phases with a checkpoint in between** — don't pipeline straight through to
pushing/PRs for every repo unattended.

### Phase 1 — Apply (no pushing yet)
1. Resolve which repos are in scope from `repos`/`lineage`. If the request is ambiguous about scope
   (all of them? just this branch? a specific sub-tree?), ask.
2. For each repo in scope, **in root-to-leaf lineage order** (a child repo may depend on its parent
   having the change first — e.g. `/template` pulling it down):
   a. Confirm its local clone exists (sibling path convention, e.g.
      `$HOME/Development/<org>/<repo>` — check `repo.local` in this repo's own `properties.yml` for
      the pattern actually in use).
   b. `git status` — if there are uncommitted changes, stash them (`git stash push -u`) rather than
      losing or clobbering in-progress work.
   c. Switch to the repo's default branch (check GitHub's actual default — some repos in this
      family use `development`, not `main`).
   d. `git fetch --prune`, then pull the default branch up to date.
   e. Create a feature branch for this change.
   f. Apply the change in that repo — either port the actual diff/pattern from the source repo/PR,
      or run the specific command/action the user named (e.g. `/update`), whichever the request
      calls for. If it's unclear what a given repo's own tier fragment or config should contain
      (e.g. what's generic to that repo's product line vs. real business config), **ask rather than
      guessing**.

### Checkpoint
Once the change is applied (uncommitted) in every repo in scope, stop and ask the user, e.g.: "Made
the changes in all N repos — ready to ship them, or is there more to add first?" Don't proceed to
Phase 2 until they confirm.

### Phase 2 — Ship
For each repo (same order), run the equivalent of `/ship-it`: fix, test, commit, push, draft PR
notes, open the PR (assigned to the user per `git.instructions.md`'s Pull Request Assignee rule).
Report each repo's PR URL back to the user. Never merge a PR yourself, and never push directly to a
shared/default branch across multiple repos without being asked.

**Example:** "run `/update` on all the related repos" → Phase 1: for each repo in scope, cd in,
stash/switch/pull, branch, run `/update`. Checkpoint: confirm ready to ship. Phase 2: ship each
one — end state is one PR per repo, each showing that repo's own `/update` result, not one combined
PR.

No dedicated automation exists for this yet (as of 2026-08-01) — each step above is done directly
(git commands, the repo's own test/push/PR tooling), not via a single script.

## Module Implementation
For the build mechanism (tier fragments, additive `repos` merge, no-op-if-exists behavior), see
`modules/setup/README.md` and `modules/setup/properties.py`.
