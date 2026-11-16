---
name: Code Review
description: Evidence-backed review of specs, tools, and workflow changes before anything lands - findings with location, proof, and severity, never a rubber stamp. Use before every commit, squash-merge, or PR landing, including changes that look trivial or already passed CI.
---

# Code Review

Adapted from gstack review, coderabbitai/skills, and requesting-code-review.

## Review the diff, not the prose

- Every finding names a file, a line, and a reproducing command or log.
  A finding without proof is an opinion; record it and keep looking.
- For spec changes check: pinned checksums, changelog NVR, license text,
  `%files` paths, sandbox attrs, private-payload guards, and arch declarations.
- For tools/workflows check: gate and verifier stay in sync
  (`bash tools/check-workflows.sh`), permission scopes are actionlint-valid,
  and no evidence check was weakened.
- For update scripts check: the updater can actually track a release, no
  broken shebang, and a real version regex.

## Output contract

- Write findings as one terse line each: **location, problem, fix, severity**
  (bug / risk / nit / question). No praise, restated diff, or hedging.
- Run five axes on every change: correctness, readability, architecture,
  security, performance. Ask whether an abstraction earns its complexity and
  whether the change can remove a concept, branch, wrapper, or special case.
- Approve when the change clearly improves overall code health, not when it
  matches your preferred style. A finding you cannot reproduce stays a nit.

## Disposition

- Fix the generator, not the instance: a recurring finding means the tool or
  prompt is wrong, not the package.
- Never land a package change you have not built and install-tested.
- Comments are short `#topic` labels only; remove incident narratives,
  dated lesson logs, restated code, and commented-out code.
- Review your own work as strictly as someone else's; a passing gate is the
  start of the review, not the end.
