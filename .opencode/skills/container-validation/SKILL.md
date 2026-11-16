---
name: Container Validation
description: Clean-environment proof for RPMs - fresh Fedora container build, install, rpm -V, ldd, and the real smoke test. Never build on the maintainer host. Use before any install PASS claim.
---

# Container Validation

Adapted from this repo's teardown harness and Linux release-validation.

## One package, one clean environment

- Use `tools/container-teardown.sh`, `tools/teardown-fresh.sh`,
  `tools/teardown-batch.sh`, and `tools/install-sweep.sh` with
  `tools/probes.txt`.
- Copy the package directory's local files (patches, extra sources, scripts)
  into SOURCES before `spectool -g`; tracked local files are not downloaded.
- Use one container per package, with a per-package lock; a shared buildroot
  can empty another job's RPM output and read as an install failure.

## What must pass

- `rpmbuild -bb`, `dnf install` from the live repo, `rpm -V` clean, `ldd`
  over the real entry points (`/usr/bin`, `/usr/libexec`, or `/usr/lib64/*.so`,
  with the bundle's `/opt/*/lib` on the path), and the package's real smoke.
- Read `rpm -qpl` first and probe what the package actually installs. A
  yt-dlp plugin's namespace is not its Python module name.
- Graphical apps: `xvfb-run` with `seccomp=unconfined`. A
  `setuid_sandbox_host` FATAL is a real bug; a docker namespace error is a
  container artifact.
- Compression-specific paths (`man1/x.1.gz`) belong to the published package;
  a bare `rpmbuild -bb` may not run brp compression, so use a glob.
- Record PASS tokens with package, chroot, and date. Never claim an install
  result you did not observe in a container.
