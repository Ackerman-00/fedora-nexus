---
name: Verification Before Completion
description: Final gate discipline - run the real verifier, prove every verdict cell, and never write status complete on belief. Use before every relay checkpoint and completion claim.
---

# Verification Before Completion

Adapted from obra/superpowers verification-before-completion and this repo's
battle-tested gate.

## The contract is the truth

- Before `status: complete`, run `RUN_ID=$RUN_ID bash tools/verify-fedora.sh`
  and paste the `VERIFICATION REPORT` into the relay block.
- Every relay verdict is a transcript of a command, not a summary of a
  belief. A FAIL cell is a broken package: fix and re-test, or mark EXTERNAL
  with a probed GAP line.
- Changed packages need a fresh install PASS. Every external gap must carry
  a `[probe: <command + result>]` token. An actionable gap fails the run.
- Confirm the relay block is scoped to this `run_id` and that dated evidence
  is from today or yesterday UTC.
- Check that the toolchain evidence (`rpmspec -P`, `dnf builddep`, `rpmlint`)
  is from this run's fresh container, not memory.

## Never game the gate

- Never weaken the gate or verifier to make a run pass; strengthen them.
- If verification fails, fix exactly what it names and re-run until exit 0.
- A checkpoint pushed as `unfinished` is better than a lost run with no
  evidence; push early, then finish properly.
