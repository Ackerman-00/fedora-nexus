---
name: Repo Improvement
description: Autonomous improvement thinking for fedora-nexus - frame the problem, generate 5-7 approaches, stress-test assumptions with probes, then land the best fix. Use every run.
---

# Repo Improvement

Adapted from Anthropic's product-brainstorming and caldoai's untangle-codebase
for an agent that is both the thinker and the owner.

## Frame before changing anything

- Start from this run's evidence: hunt findings, failed builds, stale receipts,
  slow gates, recurring defects. Separate symptoms from root causes by asking
  "why" until you reach something structural.
- Ask who suffers: users of the published repo, the scheduler itself, or a
  maintainer reading AGENTS.md. A change that only improves prose is not an
  improvement.

## Diverge without judgment

- Generate at least 5-7 distinct approaches, varying scope (tweak vs bet),
  approach (spec vs tool vs workflow vs docs), and timing (quick win vs
  investment). Include one that **removes** something and one that does the
  **opposite**. Do not anchor on the first plausible fix.
- Techniques: constraint removal, analogy from another distro or repo,
  inversion ("how could we make this worse?"), decomposition, and hat-switching
  (new user, power user, the scheduler itself).

## Stress-test with evidence

- List the assumptions the top idea depends on. Name the riskiest one and the
  cheapest probe that would disprove it, then run that probe now.
- Play devil's advocate: the strongest case against the idea, who would hate
  it, what is not being seen.
- If the thinking circles, use OODA: observe, orient, decide, act, observe
  again. Keep the decision reversible and small when evidence is thin.

## Structural lens

- Ask of every candidate: should these pieces change together? List hidden
  links (copied logic, hidden state, split features), needless links (callers
  depending on internals, stable code importing volatile code), surplus
  (wrappers, speculative config, dead code), and special cases (one-off `if`,
  retry, sleep, swallowed exception, disabled test).
- Write each fix above the problems it solves as a decision-log entry in the
  relay. Prefer the one structural fix behind several findings over patching
  each special case; fix the generator, not the instance.
- Remove comments that restate code; keep one-line labels naming a constraint
  the code cannot show. Remove tests that cannot fail, and rewrite tests tied
  to internals so they depend on behavior.

## Converge and land

- Pick the top 2-3 by evidence strength, user impact, feasibility, and fit with
  the contract. Name each one's biggest unknown and cheapest probe.
- Implement the winner **in this run**: a spec, tool, workflow, doc, or an issue
  opened with the proving command. A brainstorm that ends as a list is a
  failure; there is no human here to hand it to.
- Record `improve: <N candidates> - <top pick> - landed: <commit or issue #>`
  in the relay. The gate requires N >= 5 and a landed outcome.
- Time-box divergence against the run deadline; checkpoint what is proven
  instead of circling.
