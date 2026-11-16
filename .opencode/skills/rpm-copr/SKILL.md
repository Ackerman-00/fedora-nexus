---
name: RPM and COPR
description: Fedora RPM and COPR build logistics - chroots, SRPM vs chroot stage, build logs, repodata, provider conflicts, and dist-git drift. Use for every build failure or publication claim.
---

# RPM and COPR

Adapted from live COPR/Fedora packaging practice. Apply to every build.

## Read the right state

- Read build state at **chroot level** (`/api_3/build-chroot/list/<id>`), never
  from the build row alone: one red chroot makes the whole row failed.
- `build/list` answers `{"items": [...], "meta": {...}}`; the package name is
  `source_package.name` (nullable). Page with `offset`/`limit`.
- Fetch logs from `download.copr.fedorainfracloud.org`; the old
  `download.fedorainfracloud.org` host is dead. SRPM-stage logs live under
  `results/<owner>/<proj>/srpm-builds/<id>/builder-live.log.gz`.
- `copr-cli status <id>` alone is not evidence; read the log and chroot states.

## Stage and resolution

- Distinguish SRPM stage (`rpmbuild -bs`) from the chroot build. A missing
  library at SRPM stage is a buildroot dependency-resolution problem, not a
  spec error.
- A package this repo publishes can advertise a system SONAME from a private
  payload and poison every chroot that can install it. Before calling a
  buildroot broken, query `dnf repoquery --whatprovides <capability>` or read
  the chroot repodata and paste the result.
- A spec fix cannot reach the buildroot until its new binary publishes. If an
  older published build is the bad provider, change the buildroot packages,
  rebuild, then revert the chroot setting.

## Publication and checks

- Verify publication in every chroot's repodata (`repomd.xml` ->
  `primary.xml.gz`), not just build state; never report a chroot gap from
  `build/list` rows.
- Run `python3 tools/hunt.py builds chroots published-nvr` and
  `bash tools/dgit-drift.sh`; paste the output as evidence.
- Never hardcode the chroot list: read `chroot_repos` from the live project API.
