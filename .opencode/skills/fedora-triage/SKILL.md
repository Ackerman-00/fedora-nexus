---
name: Fedora Triage
description: Fedora-native triage with dnf, systemd, SELinux and firewalld, with verification after each step and a rollback plan. Use for any runtime, host, SELinux, or service issue around a built package, even when the spec itself looks correct.
---

# Fedora Triage

Adapted from github/awesome-copilot fedora-linux-triage, scoped to packaging.

## Triage in order

- Confirm the release and environment assumptions first (`/etc/os-release`,
  `rpm -E %fedora`). Never hardcode "the current Fedora" from memory.
- Build a stepwise plan with `dnf`, `repoquery`, `systemctl`, and `journalctl`.
  Every remediation step carries a copy-paste-ready command **and** a
  verification command that proves the change took effect.
- Check SELinux (`getenforce`, `ausearch`, setroubleshoot journal entries) and
  firewalld before blaming the package. A denial is not a packaging bug.
- Always include rollback or cleanup: the previous NVR (`dnf downgrade` or a
  pin), `systemctl disable --now`, a removed policy file, a reverted config.

## Bring it back to the package

- A defect found on a host belongs in the spec or `update.sh`; prove the fix
  with a clean-container install, not by patching the maintainer's machine.
- Never change the maintainer host's system state for a test - use a
  container. Never echo tokens into triage output.
