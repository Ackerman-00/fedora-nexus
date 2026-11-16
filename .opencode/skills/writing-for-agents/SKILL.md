---
name: Writing for Agents
description: Author and edit agent-consumed docs - AGENTS.md, sweep-prompt.md, SKILL.md - with short labels, pointer-reached context, and no stale claims. Use for every documentation change.
---

# Writing for Agents

Adapted from writing-for-agents, documentation-and-ADRs, and this repo's
comment policy.

## Write for a reader with no history

- These files are read by models with no conversation context: state the
  constraint, the command, and the consequence inline. Never rely on "as
  discussed above".
- Comments in code and config are short `#topic` labels only, a few words,
  when strictly necessary. No incident narratives, dated lesson logs,
  restated code, commented-out code, or banners.
- AGENTS.md is the shared policy and gotcha store; `tools/sweep-prompt.md`
  and the SKILL.md bodies are the scheduler's working instructions. Keep them
  consistent - a rule in one must not contradict another.

## Keep it true and cheap

- Prefer a pointer to the canonical source over duplicating a rule. Where a
  contract must be duplicated (gate and verifier), keep a drift check such as
  `tools/check-workflows.sh` in place.
- Verify every command and path you write by running it. A stale command in
  an agent doc is worse than no doc, because the agent will trust it.
- Record decisions with rationale and consequences, not chronology. Supersede
  an old entry when facts change; keep the history that explains a pin, a
  version floor, or a safety guard.
