---
name: Systematic Debugging
description: Root-cause investigation before fixing - form competing hypotheses, probe each, and prove the mechanism instead of patching symptoms. Use for every failure that is not immediately obvious.
---

# Systematic Debugging

Adapted from obra/superpowers systematic-debugging and gstack investigate.

## Stop the line and shrink the failure

- Preserve the original failure before any cleanup: logs, build ids, exit
  codes, state, timing, and input. A clean rerun does not explain the run
  that failed.
- Minimize the reproduction to a deterministic, agent-runnable red loop
  (the exact `rpmbuild`/`dnf`/`gh` command) before forming hypotheses.
- For a complex failure with several plausible causes, split the
  investigation across subagents; require file/line citations and a
  confidence tier for each conclusion before arbitrating.
- After three failed fixes, stop patching and question the architecture or
  the tooling: change the generator, not the instance. Escalate to a
  different hypothesis or subagent, never to a human approval.

## Prove the cause before the fix

- Record the symptom verbatim: log lines, build ids, exit codes, URLs.
- Write at least two competing hypotheses and, for each, the command that
  would falsify it. Run those commands.
- Separate upstream from local causes. For a missing dependency, query
  **which provider was chosen** and why, not merely that it is missing.
- A plausible story is not a proof. Pasting a symptom plus a probe of the
  symptom is not evidence for the proposed cause.
- If an external blocker is claimed, run the probe that would show a local
  cause first; if you cannot run it, the item is actionable.

## After the fix

- Break publication cycles explicitly: if an old artifact prevents the new
  one from being produced, change the buildroot/artifact state first and
  record the order of operations.
- Re-run the original failing command. If it fails identically, the cause
  was not proven and the fix is wrong.
- Keep the reasoning short in the relay: symptom, competing probes, proven
  mechanism, fix, re-test result.
