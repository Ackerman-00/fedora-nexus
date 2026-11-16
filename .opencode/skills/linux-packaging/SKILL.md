---
name: Linux Packaging
description: Fedora/RPM packaging rules for fedora-nexus - dependency mapping, spec structure, desktop metadata, and clean-environment validation. Use for every spec, update.sh, or package change.
---

# Linux Packaging (Fedora subset)

Adapted from `wazimmerman/build-linux-apps-plugin` for this Fedora-RPM-only
repository. Apply to every package you touch.

## Read first

Identify the app's language, build system, license, runtime and native
dependencies, desktop files, AppStream metadata, icons, tests, and release
artifacts. Inspect the existing spec, `update.sh`, packaging files, and
workflows before editing. Preserve the project's current packaging style
unless the owner asks for a new target. DEB and PKGBUILD targets are out of
scope here.

## Dependency mapping

Do not assume dependency names match across distros. Fedora names to expect:
`gcc`, `gcc-c++`, `redhat-rpm-config`, `meson`, `ninja-build`, `cmake`,
`pkgconf-pkg-config`, `gtk4-devel`, `libadwaita-devel`,
`qt6-qtbase-devel`, `qt6-qtdeclarative-devel`. Verify the exact name in the
chroots you build; distro names drift. `rpm-build`'s own library requirements
must resolve to the real Fedora libraries, never to a bundled payload
advertising `libstdc++.so.6` or `libz.so.1`.

## RPM

A spec needs clear `BuildRequires`, `%prep`, `%build`, `%install`, `%check`,
and `%files`. Prefer `%meson`/`%cmake` with the `_build`/`_install` macros
where available. Validate with `rpmspec -P`, `rpmlint`, `dnf builddep`, and a
fresh `fedora:44` container (`rpmbuild -bb`, install, `rpm -V`, smoke) before
claiming a fix. Account for per-chroot availability: what resolves on F44 may
not on F45 or rawhide.

## Metadata and integration

Install `.desktop` to `%{_datadir}/applications`, AppStream metainfo to
`%{_datadir}/metainfo`, and icons under hicolor. Run `desktop-file-validate`
and `appstreamcli validate`. Check binaries, resources, schemas, MIME info,
systemd user units, udev rules, and polkit rules land in distro-appropriate
paths. Smoke graphical apps on Wayland and X11/XWayland (`xvfb-run` where
needed).

## CI and release

Use containers or distro-native builders, keep signing keys out of the
repository, store packages as CI artifacts, and test install/launch in a
clean environment. Document minimum supported Fedora versions when a
dependency floor or toolkit API requires them.
