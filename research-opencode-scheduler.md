# Research: opencode scheduler architecture (.github/workflows, verify-fedora, sweeps)

Scope per task. Primary sources fetched 2026-10-04 and cross-checked against the cited URLs in the
workflow PROMPT itself. Local artifact checks were grep/read-only against the repo at
`/home/ackerman/fedora-nexus`; no files were modified and nothing was committed.

## 1. COPR auto-build mechanism is real and correctly understood

The PROMPT's core premise - "COPR is configured to auto-trigger builds on every push to the main
branch, so pushing a fixed spec file IS how you trigger a rebuild" - matches the official docs.
[COPR User Documentation, Webhooks](https://docs.copr.fedorainfracloud.org/user_documentation.html):
"Create an SCM package and set its default source... Make sure the package auto-rebuild option is
checked... And next time you push anything to your git, Copr will automatically rebuild your package."
Same page documents the webhook URL form `https://copr.fedorainfracloud.org/webhooks/<GIT_FORGE>/<ID>/<UUID>/`
used by the PROMPT's GitHub-hook delivery check. Build states list in the PROMPT matches COPR's
StatusEnum as documented; EOL chroot 180-day retention is on the same docs site's outdated-chroots
policy page, consistent with the already-fielded research-concat-openchamber.md section 5.

## 2. V1/V2 installer split is real and the tripwire is justified

- [`https://opencode.ai/install`](https://opencode.ai/install) is confirmed fetchable and its own
  usage text says "Install a specific version (e.g., 1.0.180)" and it downloads from
  `github.com/anomalyco/opencode`. So the comment "the V1 installer ships opencode 1.x" is proven by
  the fetched script text itself.
- [`https://opencode.ai/v2/install`](https://opencode.ai/v2/install) exists, and its fetched script
  proves the V2 sourcing: `metadata=$(curl -fsSL https://opencode.ai/update/api/latest/cli/npm)`,
  `package_scope="@opencode"`, installs to `~/.opencode/bin`, and points at
  `https://opencode.ai/v2/docs`. The workflow's "npm @opencode/cli is the only authenticated V2
  source" claim for the fallback matches the script's own npm-scope logic.
- CI usage of `opencode run --standalone --model ... --agent build` matches
  [V2 CLI commands doc](https://opencode.ai/v2/docs/cli/commands) ("CI: npm install --global
  @opencode/cli; opencode run --standalone --model ... "). So the invocation shape is correct.

## 3. update-engine.yml scanner: sound, with one latent inconsistency

`.github/workflows/update-engine.yml` lines 62-153: the standard-package scanner only acts on specs
with no sibling `update.sh`, reads the first GitHub URL + `Version:` + optional `%global tag`, checks
`releases/latest`, and applies `SANE_TAG = ^v?[0-9]+(\.[0-9]+)*$` before writing. The comment cites
rpm-version(7) (dash not allowed in Version); the scanner's `version_match` regex
(`^Version:\s*([0-9a-zA-Z.-]+)`) accepts `-`, but since the replacement value always comes from a
SANE_TAG-passing tag it cannot actually write one, so the regex is permissive but harmless. Release
reset to `1%{?dist}` and prepend-style changelog entry via `re.sub(r'(%changelog\n)', ...)` match the
repo's RELEASE REVISION DISCIPLINE. The scanner commits with `--author` absence + `github-actions[bot]`
identity - consistent with the PROMPT's exemption for update-engine commits.
Primary-source note: the "releases/latest returns the most recent published release" semantics is
GitHub REST behavior; prerelease tags are excluded from `/releases/latest`, so the scanner cannot
bump a package to an RC. That is a correct default for this repo.

## 4. changelog-repair.py is non-destructive and correctly fail-open

`tools/changelog-repair.py` rebuilds `%changelog` by merging entries from `HEAD`'s spec with the
working-tree spec, keeping fresh entries first (RPM convention, newest on top). It runs with
`continue-on-error: true` in update-engine.yml and swallows all exceptions returning exit 0. Both
failure directions are safe: a repair bug can never break the updater, and the merge only ever
*adds back* history. AGENTS.md's changelog-history rule (2026-10-04) aligns with the code.
`tools/test-changelog-repair.py` exists and enumerates entry-merge cases; the test file header was
read and it is consistent with the implementation.

## 5. verify-fedora.sh vs the workflow gate: deliberate duplication, real drift risk

`tools/verify-fedora.sh` (154 lines) and the inline `gate_passes()` in opencode-schedule.yml lines
99-159 implement the SAME contract twice: RUN_ID-scoped block, `status: complete`, dependency-table
row counts (distinct package names), per-package `unproven:` coverage, dated `upstream:` rows,
`teardown-slice:` minimum size (`ceil(spec_count/8)`), per-slice `docker-teardown: ... PASS`,
the 10 mains list, and `rpmspec -P`/`dnf builddep`/`rpmlint` PASS strings. The comment at line 106
says "keep both in sync" - acknowledged drift surface. Also both hardcode the 10-main list:
verify-fedora.sh lines 5/118 and the PROMPT's priority-0 (line 1269-1276) list them inline, while
README and the relay enumerate elsewhere. Adding an 11th main requires editing at least four spots.

## 6. Relay scoping is by run_id but session blocks accumulate by design - freshness is date-filtered

`gate_passes()` line 114 and verify-fedora.sh line 35 scope evidence from the first exact
`run_id: $RUN_ID` line to the next `run_id:` line. Relay blocks confirm the deliberate pattern:
"No second `run_id:` line was added on purpose" appears repeatedly, and continuation sessions
append inside the same run's block. Consequence: within one run, accumulated rows from earlier
sessions satisfy count gates (the relay shows `upstream rows 755 need 63` - far above inventory).
The only freshness guard is the `($today|$yest)` date substring filter on `upstream:`/`docker-teardown:`
tokens. A run crossing midnight accepts yesterday's evidence; two runs sharing a date (impossible,
run_id differs) is excluded only because the block is run_id-scoped. Net: gate proves *some*
evidence exists today-or-yesterday per package, not that every package was checked in this run's
current session. The `>= expected` count on distinct packages is still intact.

## 7. opencode.yml (/oc trigger) cannot satisfy its own verify step for small fixes

`.github/workflows/opencode.yml` line 145-151 runs `bash tools/verify-fedora.sh` after any /oc
issue/PR fix, and its embedded prompt (line 105) tells the agent to set relay `status: complete`
+ `run_id:`. But verify-fedora.sh requires the FULL audit contract: every one of the N specs with
deps/unproven rows, dated upstream rows for every package, a 10-mains docker-teardown sweep, a
teardown-slice covering `ceil(N/8)`, install-test table, and version table. A single-issue /oc fix
that builds and installs one package cannot produce that without effectively running a full fleet
sweep. Either every /oc run degenerates into a full 6-hour sweep, or /oc runs will systematically
end red despite a correct fix. Recommend a per-invocation verifier mode (e.g. `--touched-only`,
scope tables to packages named in the issue) or skipping the full-table gate for issue_comment
triggers.

## 8. PROMPT duplication and dead references

- The RELAY / LONG-RUN HANDOFF section appears TWICE, near-verbatim (lines 226-254 and 1774-1813),
  including the same `gh workflow run` invocation and the same 4.5-5h trigger. The GIT IDENTITY
  block also appears twice (lines 256-263 and 400-436). Both duplicates are drift-prone; one copy
  of each already differs slightly (bottom copy has extra timeout-safety text).
- The SKILLS block (lines 442-470) mandates `/code-review`, `/make-pr-easy-to-review`, `/architect`,
  `/codebase-design`, `/research`, `/unslop`. In the current environment only `codebase-design`,
  `research`, `unslop` exist; `code-review`, `make-pr-easy-to-review`, and `architect` do not.
  The prompt softens this with "if a skill fails to load, apply its discipline manually and record
  `skill-missing:`" - so it degrades gracefully, but the "they are always available" line is false.
- `tools/docker-sweep.py` is referenced ONLY in AGENTS.md (Layer 1b); zero references in any
  workflow YAML or the PROMPT. The live harness is `tools/container-teardown.sh` +
  `tools/copr-install-check.sh`. docker-sweep.py is currently dead weight in the agent path.
- README says supported releases are "Fedora 44, 45 and Rawhide" while the relay's live chroot
  audit (and COPR API) still list `fedora-43-x86_64` as an enabled chroot receiving builds
  ("ly ... succeeded 4/4 chroots (fedora-43/44/45-x86_64 + rawhide)"). README/relay drift.

## 9. opencode.json model list has drifted from the workflow's

`opencode.json` pins `"model": "opencode/muse-spark-1.3-contributor-free"` and defines 9 model
entries. Both workflows inline a 13-model fallback chain starting with `opencode/fledge-alpha-free`
and ending with `opencode/muse-spark-1.2-contributor-free`. The two lists share 8 ids; the workflow
adds fledge-alpha-free, nemotron-3-ultra-free (present), ling-3.1-flash-free, deepseek-v4-flash-free,
space-bunny-free, longcat-2.5-preview-free. Also `OPENCODE_CONFIG_CONTENT` sets only the title
agent model. No single source of truth for the chain; a dead free-model id silently burns attempt
slots until the "MODEL FRESHNESS" note updates one of the three copies.

## 10. The verifier is grep-of-agent-attestation, not artifact proof - understood and accepted

`docker-teardown: <pkg> ... PASS | <date>`, `upstream: <pkg> ... | <cmd> | <date>`, and the tasksha
line counts are free-text strings the agent writes into `.opencode-relay.md`. The gate and
verify-fedora.sh never re-run the commands. This is the documented "proof-or-stop / agent is the
teardown" design (AGENTS.md Layer 2: "Sweep is evidence, not a pass-anyway script"), and the agent
logs back it via `~/.local/share/opencode/log/` artifacts, but strictly it is attestation. Any
future hardening (e.g. hash of a per-package log dir, or requiring the `BUILT=`/`INSTALL_EXIT=`
lines from container-teardown.sh rather than a hand-written token) would raise the bar; today the
contract is only "the right strings with today's date exist".

## Verified facts (primary sources)

- V1 installer (anomalyco/opencode, 1.0.180 example): https://opencode.ai/install (fetched 2026-10-04)
- V2 installer (@opencode scope, npm cli-<target> tarballs, `/v2/docs` footer):
  https://opencode.ai/v2/install (fetched 2026-10-04)
- V2 CI invocation (`opencode run --standalone`, `npm i -g @opencode/cli`):
  https://opencode.ai/v2/docs/cli/commands
- COPR webhook-on-push behavior + SCM/auto-rebuild + states + EOL chroot policy:
  https://docs.copr.fedorainfracloud.org/user_documentation.html
- Local greps: `docker-sweep` absent from `.github/`; 10-main list hardcoded in 4 places;
  PROMPT contains two near-verbatim copies of RELAY handoff and GIT IDENTITY blocks.

## Not verified / caveats

- Whether the relay's `upstream:`/`docker-teardown:` date filter admits yesterday's evidence into a
  run that starts after midnight is inferred from the grep pattern, not observed in a failed run.
- The /oc verify-step mismatch (section 7) is a structural reading of the two files; no live /oc
  run log was inspected to confirm red outcomes.
- GitHub Actions `permissions:` closed-set list in the PROMPT (line 378-386) was taken as given;
  its canonical source is the workflow-syntax docs page the same line cites.
- COPR API token 180-day expiry is asserted in the PROMPT from the owner's https://copr.fedorainfracloud.org/api/
  page; not re-verified live.
