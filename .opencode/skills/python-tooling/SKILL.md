---
name: Python Tooling
description: Standards for this repo's stdlib-only Python tools - pytest tests, negative tests for detectors, and no new runtime dependencies. Use for any tools/*.py change.
---

# Python Tooling

Adapted from the Python foundation and performance catalogs, constrained by
this repo's stdlib-only tool policy.

## Keep the tools dependency-free

- `tools/*.py` run on the CI's stock Python 3. Do not add `requests`, `uv`,
  profilers, or optional packages without changing the workflow dependency
  step and proving the change in CI.
- Prefer direct control flow, EAFP, modern built-in generic syntax, and clear
  exception boundaries. Keep public functions small and independently
  testable.

## Prove detectors, not just happy paths

- Every change to a check or detector needs a test in `tools/test-*.py`: a
  positive case, a negative case, and the exact false-positive or
  false-negative that motivated the change.
- Run `python3 tools/test-hunt-helpers.py` and
  `python3 tools/test-sweep-helpers.py` (and any other `test-*.py` you touch)
  before claiming a tool change works.
- Ruff/ty are optional local aids, never a gate this repo does not run.

## Measure before optimizing

- Profile with `cProfile`/`pstats` before changing a hot path. Execution time,
  memory, CPU, and I/O wait are separate signals; a faster micro-operation is
  not proof of a smaller relay or a faster CI run.
- Keep receipts deterministic: no random or wall-clock values inside a
  result that a gate depends on; stamp dates from the runner when recording.
