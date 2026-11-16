---
name: GitHub Ops
description: Issue and PR triage with the gh CLI - the tracker is the queue, evidence in every comment, close only with proof, strict bot identity. Use for every issue, PR, and commit.
---

# GitHub Ops

Adapted from fvadicamo/dev-agent-skills and openclaw-pr-maintainer.

## The queue

- Start every run with `gh issue list --state open`. Reproduce each issue
  before commenting; never close on a claim.
- Open an issue for every real defect you find, with the command that proves
  it. The tracker is this repo's audit trail, not a human handover.
- Every verdict comment carries commands, build ids, and the verification
  result. Close only after the fix is built, installed, and verified.
- PRs you open are yours to review and merge (squash) in the same run. Run
  `gh pr checks <n>` and confirm the build/install evidence before
  `gh pr merge <n> --squash`; never merge on a green checkbox alone.
- Never wait for owner approval: you are the owner. Pushes, merges, COPR
  writes, chroot edits, and issue closure are yours to execute now. The gate
  fails `needs-owner` / `waiting for owner` / approval markers. A missing
  secret or a real outage is a probed `GAP: external` with one tracking
  issue, never a request for permission.

## Commits and pushes

- Commit identity is exactly
  `opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com>`.
  No `--author`, no trailers, no invented emails.
- `git fetch origin && git pull --rebase origin main` before pushing; a push
  triggers COPR rebuilds, so push only on a verified state.
- Never echo or paste tokens; rely on env-provided gh/COPR auth.
- Keep .opencode-relay.md current and never delete it; one block per run_id.
