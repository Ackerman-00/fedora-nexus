# Research: Does the scheduled maintainer agent actually read the 1600-line PROMPT?

Scope per task: investigate, via primary sources only (docs, arXiv, lab/benchmark
posts), whether `opencode run --standalone --model <m> --agent build "$PROMPT"` causes
the agent to read and follow a ~1600-line prompt (4h30m self-deadline, handoff trigger,
relay protocol, verification loop). Primary sources fetched 2026-10-04. Local artifact
checks were read/grep-only. No files modified, nothing committed, workflows untouched.

## 1. What the invocation actually does (opencode V2 docs)

[https://opencode.ai/v2/docs/cli/commands](https://opencode.ai/v2/docs/cli/commands):
- `run` "Sends a message and prints the reply without opening the interactive interface."
- CI example: `opencode run --standalone --model anthropic/claude-sonnet-4-5 "Review this repository for correctness and summarize any issues."` — so the PROMPT argument is the
  user message sent to the model, in standalone (private-server) mode.
- `--agent build "Fix the failing test"` is a documented flag: "Run with a specific agent."

[https://opencode.ai/v2/docs/agents](https://opencode.ai/v2/docs/agents):
- "An agent combines a system prompt, model preference, permissions, and display details
  into a named assistant profile."
- Markdown agent body "becomes the agent's `system` prompt"; JSONC `system` "sets the
  agent's system prompt... Project instructions, skills, references, and other instruction
  sources are still added."
- Built-in `build`: "Default coding agent. Tools are allowed by default; sensitive
  environment-file reads and access outside the workspace ask for approval." Nothing in
  the doc says `--agent build` changes instruction-following discipline; it selects the
  permission set and base system prompt. So `--agent build` does NOT add any guarantee
  that the PROMPT is obeyed — the PROMPT is just the (user) message.

Consequence: the worker's instructions live in exactly one user-turn message, subject to
normal long-context instruction-following limits (sections 2-4).

## 2. Long-prompt instruction adherence: primary evidence

- **Lost in the Middle**, Liu et al., TACL 2024 (arXiv:2307.03172):
  https://arxiv.org/abs/2307.03172 — "We analyze the performance of language models on
  two tasks that require identifying relevant information in their input contexts..."
  Finding: U-shaped performance — relevant info in the middle of long contexts is used
  much worse than at the start or end. A mid-prompt 4h30m deadline buried in a 1600-line
  message is exactly the worst position.
- **IFScale** ("How Many Instructions Can LLMs Follow at Once?"), arXiv:2507.11538:
  "We evaluate 20 state-of-the-art models across seven major providers and find that
  even the best frontier models only achieve 68% accuracy at the max density of 500
  instructions" and "Nearly all models exhibit mid-range peaks around 150-200
  instructions where selective attention mechanisms favor earlier instructions, followed
  by convergence toward uniform failure patterns at extreme densities... a fundamental
  shift from selective to universal instruction abandonment." This is the direct
  instruction-compliance cliff for dense prompts. (Arize AI blog, May 2026, re-ran
  IFScale: 2026 models better, ~2000-constraint ceiling vs 150-200 a year earlier —
  improvement, not solved. Secondary source; citing only to note the trend.)
- **VerIFY / long-context instruction following**, Robinette et al. (Google DeepMind,
  Vanderbilt), EACL 2026 Findings: introduces "a Verifiable Instruction Following
  Yardstick dataset designed to benchmark the compliance and accuracy of LLMs in
  adhering to various types of instructions across multi-turn, long-context
  conversations" and evaluates six mitigation strategies.
- **Omission Constraints Decay While Commission Constraints Persist**, Gamage, arXiv:2604.20911
  (2026, 4,416 trials): "Omission compliance falls from 73% at turn 5 to 33% at turn 16
  and 20% at turn 25 in the worst case... while commission compliance remains at 100%
  throughout." Negative-form rules ("never do X", "do not skip the handoff") decay with
  context depth while positive-form compliance looks healthy — the exact failure mode of
  a rule-only PROMPT where "looks done" masks violated omissions.
- **EACL 2026 VerIFY / "We Are What We Repeatedly Do"** (Robinette et al., same
  citation as above) and Dente et al., arXiv:2605.06445 ("Constraint decay: the fragility
  of LLM agents in backend code generation"): multi-constraint agents drop ~30pp in
  assertion pass rate as constraints accumulate.

## 3. Can the agent self-monitor wall-clock time / meet the 4h30m deadline?

Primary evidence says no, not reliably:

- **Your LLM Agents are Temporally Blind**, Cheng et al., ACL 2026 Findings, arXiv:2510.23853:
  "by default, [agents] assume a stationary context, failing to account for the
  real-world time elapsed between messages" — "temporal blindness". On TicToc (76
  scenarios), without timestamps alignment is near chance; adding timestamps in the
  prompt only lifts alignment to ~65% and prompting does not fix it (per the authors'
  own summary and the companion "Can LLMs Perceive Time?" line of work).
- **Real-Time Deadlines Reveal Temporal Awareness Failures in LLM Strategic
  Dialogues**, arXiv:2601.13206 (2026): models "honor deadlines expressed in turns and
  ignore the same deadlines expressed in [wall-clock time]" — "the limitation appears
  to be in representing and acting on real-time".
- **Can LLMs Perceive Time? An Empirical Investigation**, arXiv:2604.00010 (2026):
  "The model observes tokens, not elapsed time. It does not directly perceive wall-clock
  duration while generating"; LLM inference gives "text, not direct access to elapsed
  time".
- **Discrete Minds in a Continuous World**, Wang et al., arXiv:2506.05790 (EMNLP 2025
  Findings): models operate on Token-Time (discrete) and can only indirectly infer
  Wall-Clock-Time. Implication: a 4h30m self-deadline has no internal clock; the agent
  needs external signals (timestamps each turn, scheduler-imposed timeout, or the CI
  job's `timeout-minutes`) to act on it.

## 4. Do the cited sources support "external verifier + gate = near-100%"?

The workflow PROMPT (.github/workflows/opencode-schedule.yml line ~1959) says: "Prompt
alone achieves 70-90% compliance; external verifier + gate achieves near-100%" citing
agentpatterns.ai 2026-07-19 / contextOS 2026-08-14 / digitalapplied.com 2026-08-11.

What the sources actually say:

- **agentpatterns.ai/instructions** (https://agentpatterns.ai/instructions): supports the
  DIRECTION of the claim — "Restraint Rules Need External Enforcement — Agents comply
  with rules that add work and never with rules that stop it; additive rules belong in
  the auto-loaded instruction file, restraint rules in CI or required review";
  "Enforcing Agent Behavior with Hooks — Move critical behavioral rules out of prompts
  and into deterministic shell hooks that the model cannot override";
  "Constraint Encoding Does Not Fix Constraint Compliance — Restructuring how
  constraints are formatted in prompts does not improve model compliance". Also its
  anti-patterns page names "The Mega-Prompt — A single instruction file containing
  every rule, convention, and example degrades agent compliance rather than improving
  it" and "The Prompt Tinkerer — Endlessly refining prompts to prevent errors that
  structural controls would eliminate deterministically". NO 70-90%/near-100% numbers.
- **dotzlaw.com/insights/claude-hooks** (https://dotzlaw.com/insights/claude-hooks) is
  the actual origin of the figure: "Prompt-based instructions achieve 70-90% compliance
  ... Hooks achieve 100% compliance. They execute at the system level, outside the LLM's
  reasoning chain." It is an assertion about Claude Code hooks, not a benchmark.
- **contextosai.com** (https://contextosai.com) — the cited "contextOS" is a product page
  ("ContextOS gives teams the harness around the model: ... validation before
  completion, and an audit record that can be replayed"), no compliance percentages
  found on fetch.
- **digitalapplied.com** nearest article is "Define Done, Not Effort: Prompts That Make
  Agents Verify", published Aug 12 2026 (https://www.digitalapplied.com/blog/define-done-acceptance-criteria-agent-prompts-2026):
  "write the completion bar into the prompt — a named check, an iterate-until
  instruction, and required evidence — instead of asking for more effort", and notes
  "separate fresh-context verifier subagents tend to outperform self-critique".
  Direction matches the repo's verify-fedora.sh gate; again no 70-90%/near-100% numbers.

Verdict on the claim: direction correct and well-supported (prompt rules alone are
probabilistic; external, deterministic verification is the documented fix), but the
specific percentages are folklore recycled from the hooks discourse, not from the three
cited sources.

## 5. Bottom line

- The agent does read the PROMPT (it is the first/only user message), but there is no
  mechanism that forces it to "think about" each clause. Long-context decay (Lost in the
  Middle), instruction-load cliffs (IFScale, ~68% max accuracy even in 2026 models),
  constraint decay over turns (Gamage, Dente), and temporal blindness (Cheng, Wang)
  all say mid-prompt rules like a 4h30m deadline and handoff trigger will be followed
  inconsistently without external enforcement.
- Strongest mitigations, with sources:
  1. Keep a deterministic external gate and treat the prompt as advisory — it already
     exists: `gate_passes()` + `tools/verify-fedora.sh` (proved in
     research-opencode-scheduler.md §5). This matches agentpatterns.ai
     "Restraint Rules Need External Enforcement" and digitalapplied's "named check +
     iterate-until + evidence".
  2. Enforce the deadline mechanically: CI `timeout-minutes`, a scheduler-side kill, or
     timestamp each user turn — prompt-only deadlines fail (arXiv:2601.13206,
     arXiv:2510.23853).
  3. Shrink/front-load critical rules and repeat them at both ends of the prompt
     (primacy/recency, "Critical Instruction Repetition" per agentpatterns.ai), and
     re-inject critical constraints near the end of each session window to counter
     constraint decay (arXiv:2604.20911).
