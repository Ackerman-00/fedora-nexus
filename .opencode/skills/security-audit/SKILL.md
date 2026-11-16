---
name: Security Audit
description: Package and repository security review - OSV ranges, checksum pins, secrets, unsafe scriptlets, SUID helpers, supply-chain floors. Use for every spec, incident, dependency change, and any 'no CVEs' or 'clean' claim.
---

# Security Audit

Adapted from Trail of Bits insecure-defaults/static-analysis and gstack CSO.

## Secrets and supply chain

- Keep tokens out of logs, commits, and issues: a leaked token ends every
  run. Check presence, never the value, and redact command output.
- Verify every `# sha256:` pin against the artifact it names. A pin that lags
  the version shipped is a false receipt, not evidence.
- Trivy floor >= 0.72.0 with commit-SHA-pinned actions; the March 2026
  v0.69.4 / hijacked-action-tag compromise (GHSA-69fq-xp46-6x23) makes the
  distro 0.69.3 unsafe by default.
- Query OSV with `version` top-level and a real ecosystem (gentoo/fedora ->
  omit it); re-read each advisory's own ranges before calling a version
  affected. A mention is not an infection.

## Packaging-specific checks

- `chrome-sandbox` must be `%attr(4755, root, root)` or removed; verify with
  a non-root launch test. A plain 0755 helper aborts every normal user.
- Any spec excluding `/opt/<pkg>` from autorequires must declare all shipped
  ELF sonames by hand and prove them with `rpm -q --requires` / `ldd`.
- Audit `%post`/`%pre` for chmod/chown of setuid files, `curl | sh`,
  world-writable paths, and unpinned downloads.
- Bundled shared libraries under a private directory must not be published
  as system-wide Provides.

## Method

- Run `python3 tools/teardown-sweep.py --type fedora` and
  `python3 tools/hunt.py cves pins sandbox`; paste the output.
- Never weaken a check to clear a false positive: fix the detector and
  negative-test it.
