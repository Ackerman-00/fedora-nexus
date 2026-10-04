# Research: GitHub Actions runtime limits vs the 4:30h cap (.github/workflows/opencode-schedule.yml)

Scope per task. Primary sources fetched 2026-10-04: the official GitHub docs limits and workflow-syntax
pages, plus the workflow file itself. Local artifact checks were grep/read-only against the repo at
`/home/ackerman/fedora-nexus`; no files were modified and nothing was committed.

## 1. GitHub-hosted hard cap: 6 hours per job, job is terminated and fails

[Actions limits](https://docs.github.com/en/actions/reference/limits), "All GitHub-hosted runners" row:
"Job execution time | 6 hours | Each job in a workflow can run for up to 6 hours of execution time. If a
job reaches this limit, the job is terminated and fails." Self-hosted runners get "Job execution time |
5 days | ... the job is terminated and fails." So a `timeout-minutes: 355` job on `ubuntu-24.04` can never
legitimately run longer than 360 min; GitHub kills it at 6h and marks the job failed. The doc's general
statement "the expected behavior when a limit is reached is that the workflow/job will get cancelled"
applies; the limits table phrases the 6h case as "terminated and fails."

Distinct limits on the same page: workflow run time is "35 days / workflow run ... This period includes
execution duration, and time spent on waiting and approval"; job queue time is "24 hours ... before it is
automatically cancelled" (listed under Self-hosted; GitHub-hosted jobs can also sit queued but that time
is not what timeout-minutes measures).

## 2. timeout-minutes semantics: default 360, run time only, queue time does not count

[Workflow syntax, `jobs.<job_id>.timeout-minutes`](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax):
"The maximum number of minutes to let a job run before GitHub automatically cancels it. Default: 360.
If the timeout exceeds the job execution time limit for the runner, the job will be canceled when the
execution time limit is met instead." Step-level analogue exists
(`jobs.<job_id>.steps[*].timeout-minutes`, same page: "Fractional values are not supported.
timeout-minutes must be a positive integer"). Because the GitHub-hosted execution cap is 360 and the
default is also 360, any `timeout-minutes` above 360 is clamped by reality to 360 — which is exactly
what the workflow is experiencing: the job gets killed, not handed over.

## 3. Workflow file facts (.github/workflows/opencode-schedule.yml)

- Line 27: `timeout-minutes: 355` on `jobs.opencode` (line 25), runner `ubuntu-24.04` (line 26).
- Lines 20-22: `concurrency: group: opencode-schedule, cancel-in-progress: false` — a run hogging the
  runner queues the next scheduled run; it is not cancelled. Combined with cron `'10 */6 * * *'`
  (line 5) and a 6h kill, runs can pile up.
- Lines 245-250 (PROMPT): the agent's own handoff trigger is "when the run has been going ~4.5-5
  hours" — inside a 355-min budget this trigger is nearly useless, because by then the 6h wall is
  close and a kill (not a handoff) follows.
- Lines 1987-1990: `cleanup:` job, `runs-on: ubuntu-24.04`, `if: always()`, `needs: opencode`.
  The cleanup job has no explicit `timeout-minutes`, so it defaults to 360 (per the syntax doc above).
  It runs only after the opencode job finishes; its minutes do NOT count toward the opencode job's
  355 (or the 6h per-job cap) — each job's timeout is its own — but they DO count toward the 35-day
  workflow-run total and toward the elapsed wall time before the next queued run can start, because
  `concurrency.cancel-in-progress: false` serializes the whole group.

## 4. Recommendation for a 4:30h wall-clock max on the opencode job

- Set `jobs.opencode.timeout-minutes: 270` (4:30 = 270 min; hard ceiling satisfied well under 360).
- Move the prompt's HANDOFF TRIGGER from "~4.5-5 hours" to "~3:45-4:00"
  (225-240 min), leaving 30-45 min to finish pushes, write `.opencode-relay.md` with
  `status: unfinished` + `run_id:`, commit, push, and fire
  `gh workflow run opencode-schedule.yml --ref main -f relay=true`. Anything later risks the
  270-min cancellation cutting the handoff record itself.
- With cron every 6h and cancel-in-progress false, a 270-min opencode job + cleanup (typically
  minutes) leaves the next scheduled run a comfortable window to start queued; today a 355-min job
  plus cleanup can overlap the next `*/6` slot and queue it.

Not verified: actual observed SIGTERM-vs-cancellationlog text at the 6h kill in this repo's run
history, and the exact queue-time treatment of GitHub-hosted runners (docs list queue cancellation
explicitly only under Self-hosted).
