# Research: scheduler timeout (360min cap ignored) + YAML relay-input surgery

Scope per task. Primary sources fetched 2026-10-04 (opencode.ai V2 docs,
docs.github.com) and cross-checked against the repo at
`/home/ackerman/fedora-nexus`. Local checks were grep/read-only; one file was
created (this one). Nothing committed, no YAML edited.

## 1. opencode V2 has NO self-stop CLI flag — config `steps` caps agentic steps

`opencode run --help` on the local V2 binary (v2.0.22, 2026-10-04) lists:
`--standalone`, `--server`, `--continue`, `--session`, `--fork`, `--model`,
`--agent`, `--format`, `--file`, `--title`, `--thinking`, `--auto`. No
`--timeout`, `--max-steps`, `--max-iterations`, `--max-tokens`, or `--deadline`.
The doc page agrees: "Every command accepts `--help` for its full flag list" and
shows only the flags above
(https://opencode.ai/v2/docs/cli/commands).

The only config-based cap is the agent `steps` field:
[https://opencode.ai/v2/docs/agents](https://opencode.ai/v2/docs/agents),
"### Steps":
> `steps` sets a positive maximum number of model steps:
> ...
> On the final step, OpenCode removes tools and asks the model to summarize in
> text. New user input resets the allowance.
and the legacy note: "Do not use legacy top-level fields such as `temperature`,
`top_p`, `prompt`, `permission`, `tools`, `disable`, or `maxSteps` in new V2
agent configuration." Same text on
https://opencode.ai/docs/agents ("### Max steps": "Control the maximum number of
agentic iterations an agent can perform before being forced to respond with
text only... The legacy `maxSteps` field is deprecated. Use `steps` instead.").

Caveats: `steps` caps iteration COUNT, not wall-clock minutes, so a run with
slow tools can still burn hours under a large `steps`. For `opencode run` the
whole session is one user message, so "New user input resets the allowance"
does not fire mid-run. The config `timeout` keys documented at
https://opencode.ai/docs/config ("Provider options can include `timeout`,
`headerTimeout`, `chunkTimeout`... `timeout` - Request timeout in milliseconds
(default: 300000)") are per-HTTP-request timeouts, NOT run-level wall clock —
do not rely on them. There is no max-tokens or cost cap documented.

To bound the `build` agent, add `"steps": N` under
`"agents": {"build": {...}}` in `OPENCODE_CONFIG_CONTENT` (workflow already
uses that env var for the title agent) — this ends the run mechanically with a
forced text summary, but does NOT guarantee finishing before 360min by itself.

## 2. GitHub Actions: timeout-minutes kill semantics; no started-time in contexts

[https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
jobs:
> `jobs.<job_id>.timeout-minutes`: "The maximum number of minutes to let a job
> run before GitHub automatically cancels it. Default: 360"
> `jobs.<job_id>.steps[*].timeout-minutes`: "The maximum number of minutes to
> run the step before killing the process. Maximum: 360 for both GitHub-hosted
> and self-hosted runners."
Timeout is a kill, not a graceful finish: the step/job is cancelled and the
process killed (runners end a job with SIGINT then SIGTERM/SIGKILL on
cancellation — https://github.com/actions/runner/issues/921 trace comment:
`2666 --- SIGINT {si_signo=SIGINT, si_code=SI_USER ...}` then
`2666 --- SIGTERM ... +++ killed by SIGTERM +++` and `Job run completed with
result: Canceled`). So `timeout-minutes` must stay a LAST-RESORT ceiling; it
cannot itself trigger the relay handoff.

Elapsed time is NOT available as an expression: the contexts reference
(https://docs.github.com/en/actions/reference/workflows-and-actions/contexts)
lists `github.run_attempt`, `github.run_id`, `github.run_number`, etc., but no
`github.run_started_at`; `run_started_at` exists only in the REST API response
(https://docs.github.com/en/rest/actions/workflow-runs, field
`run_started_at`: string, format: date-time). Practical in-step clocks:
`date +%s`/`SECONDS` in bash, and `gh run view $GITHUB_RUN_ID --json startedAt`
(the latter is what the duplicate RELAY paragraph already tells the agent to
use, opencode-schedule.yml:1825).

## 3. Relay input is load-bearing; `gh workflow run ... -f relay=true` is correct

- Syntax: docs.github "Running a workflow using the GitHub CLI": `gh workflow
  run` takes "the name, ID, or file name of the workflow" and "If your workflow
  accepts inputs... use `-f` or `-F`... in `key=value` format"
  (https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow).
  `gh workflow run opencode-schedule.yml --ref main --repo Ackerman-00/fedora-nexus
  -f relay=true` is correct for this repo (file name form).
- Do NOT delete the `relay:` key under `on.workflow_dispatch.inputs`
  (opencode-schedule.yml:6-12). GitHub validates dispatch inputs against the
  declared workflow inputs and rejects unknown keys with HTTP 422
  "Unexpected inputs provided" — observed at
  https://github.com/nijosmsft/etw-mcp/commit/3713628ci ("'gh workflow run -f
  tag=...' failed with HTTP 422 Unexpected inputs provided. Declare both as
  workflow inputs.") and https://github.com/marcusrbrown/systematic/pull/433.
  REST doc supports the validation reading: "`inputs`... Input keys and values
  configured in the workflow file"
  (https://docs.github.com/en/rest/actions/workflows).
- Removing comments or duplicated PROMPT paragraphs does NOT affect the relay
  trigger path: the workflow maps `RELAY: ${{ github.event.inputs.relay == 'true'
  && '1' || '0' }}` (opencode-schedule.yml:220) from the event payload, and the
  post-run gate greps `.opencode-relay.md` on main (lines 99-159, `run_id:`
  scoping per lines 110-114) — never the PROMPT text.
  `tools/verify-fedora.sh` does not reference the workflow YAML at all
  (grep, 2026-10-04).

## 4. Safe deletions (no protocol change)

1. `# 3) REMOVED:` legacy comment blocks — opencode-schedule.yml:73-76 and
   opencode.yml:66. Comments only; the installer logic around them is live.
   Safe to delete.
2. The duplicate "RELAY / LONG-RUN HANDOFF (MANDATORY)" paragraph — second copy
   at opencode-schedule.yml:1808-1846, vs first copy at lines 226-254. Keep ONE
   canonical copy. Merge the bottom copy's unique content before deleting: its
   elapsed-time hint "`gh run view <id> --json startedAt`, or the workflow
   clock" (line 1825) and its "TIMEOUT SAFETY" clause (lines 1833-1837).
   Without a merge those clauses are lost; with the merge the deletion is safe.
3. The duplicate GIT IDENTITY paragraph — first copy lines 257-263, second
   bullet form at line 404. Same contract; keep one. Safe.
4. NO "relay button" exists in the repo: grep for `button` across
   `.github/` and README hits nothing. The only relay UI surface is the
   `relay` workflow_dispatch input, which section 3 says must stay because
   `-f relay=true` depends on it (and it renders the "Run workflow" input
   form on the Actions tab).
5. Do NOT delete gate-string references to `run_id: $RUN_ID` / `status:
   complete` / `unfinished` — those document the contract the gate enforces.

## 5. Recommendations (for the owner; not applied)

Mechanical (ends the run):
- Wrap the agent call: `timeout --signal=TERM --kill-after=60s 250m opencode
  run ...` (GNU coreutils timeout, ubuntu-24.04 has it) so the agent process
  dies hard at 250m even if it ignores every prompt instruction; plus
  `"steps": N` in the agent config to cap iteration count
  (https://opencode.ai/v2/docs/agents). Keep job `timeout-minutes: 360` as the
  outer ceiling and add a step-level `timeout-minutes: 300` on the run step
  (step kill "before killing the process", workflow-syntax doc above). The
  agent must trigger its relay BEFORE 250m, so the prompt handoff bar stays
  at 225-240m.

Env/state (makes the deadline visible):
- Export a concrete deadline in the run step, e.g.
  `DEADLINE_EPOCH=$(date +%s -d '+250 minutes')` and
  `DEADLINE_UTC=$(date -u -d "@$DEADLINE_EPOCH" +'%Y-%m-%d %H:%M UTC')`,
  print both, and pass them through `GITHUB_ENV`. There is no
  `github.run_started_at` in expression contexts (contexts doc above), so the
  agent's reliable clock is `date` in bash + `gh run view $GITHUB_RUN_ID
  --json startedAt` (`run_started_at` REST field). GitHub masks nothing here;
  plain env vars work.

Prompt (tells the model the number):
- Replace the fuzzy "YOU must finish within 270 minutes (4h30m)" with the
  concrete injected value: "RUN_DEADLINE_UTC is $DEADLINE_UTC; at
  4h00m elapsed (`date -u` + `gh run view ... startedAt`) you MUST already
  have pushed status unfinished + triggered the relay, or the 250m timeout
  kills the run and the gate fails it." Prompt alone is not enforcement —
  that is why the mechanical `timeout` wrapper above must do the real
  stopping.

## Not verified / caveats

- `timeout` signal choice: tested not; SIGTERM-first with a SIGKILL grace is
  standard coreutils behavior but the agent's opencode server may need a
  trapped handler to flush the session — killing loses in-flight session
  state, which is exactly why the relay must fire earlier.
- `"steps"` under `agents.build` in V2.0.22 was read from docs, not exercised
  against a live run.
- Whether GitHub 422s on undeclared `-f` inputs is documented behavior in the
  REST doc + widely reproduced issue links; no live 422 test was run here.
