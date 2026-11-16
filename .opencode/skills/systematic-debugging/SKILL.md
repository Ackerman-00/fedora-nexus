---
name: Systematic Debugging
description: Root-cause investigation before fixing - competing hypotheses, falsifying probes, and attacking the premise after two failed fixes. Use for every non-obvious failure and before any second attempt at the same fix.
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

## Attack the premise

- After two fixes that share one premise fail the same gate, suspect the
  premise, not the fixes. Write the one-sentence premise down and test it
  with an observation that would differ if it were false.
- Look at how failures are distributed, not only their size; make the check
  rerunnable. If evidence contradicts the premise, stop fixing that cause.
- Do not start a third fix before the premise has been written and tested.

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
