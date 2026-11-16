---
name: Why From Record
description: Answer 'why is it this way' from the repo record before planning a fix - cite the commit, AGENTS.md section, relay block, or issue, mark inferences, name gaps. Use before any non-trivial change or when a rule looks unnecessary.
---

# Why From Record

Adapted from backnotprop/pstack `why` for this autonomous maintainer.

## Answer from the record, not from plausibility

- Before proposing a fix, read the record that introduced the behavior and
  each later change: `AGENTS.md` decision sections, spec changelogs, git log
  and the commit diff, issue/PR comments, and prior `.opencode-relay.md`
  blocks. Cite the exact source (commit hash, `AGENTS.md#section`, issue #N,
  relay run_id) in the relay.
- Quote or closely paraphrase what the authors wrote. A plausible story about
  "why the code does X" is an **inference** and must be marked as such.
- Say explicitly what the record does not answer. Do not fill the gap with a
  confident guess and then act on it.

## Use the answer

- A rule that exists because of a recorded incident is a constraint, not a
  cleanup target: check the incident before deleting or weakening it.
- If the record contradicts the proposed fix, change the plan, not the record.
- If the record is thin, gather evidence first (websearch, `git log -S`,
  `gh issue view`, build logs). An unproven "why" is not a basis for a change.

## Relay token

Record one line before acting:

```
why: <subject> - source: <commit | AGENTS.md#section | issue #N | relay run_id> - inference: <none | what you inferred>
```

The gate requires this line and a source token; a fix justified only by
"seems right" fails the evidence contract.
