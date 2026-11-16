---
name: Linux Packaging
description: Fedora/RPM packaging rules for fedora-nexus - dependency mapping, spec structure, desktop metadata, clean-environment validation. Use for every spec, update.sh, or package change, including version-only bumps that look mechanical.
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

## Dependency first, then packaging

Order matters: establish what upstream actually needs before changing the
spec, so the fix is driven by evidence rather than by the symptom. Check the
official Fedora dist-git spec first; if none exists, read the FULL upstream
build-system files (Cargo.toml/Cargo.lock, meson.build, CMakeLists.txt,
go.mod, pyproject.toml, including subdirs), derive the dependency list, and
compare it with BuildRequires/Requires. Record that comparison before the
edit. Only then make the spec excellent: pinned checksum, correct NVR and
changelog, license text, minimal proven dependencies, native build macros,
correct %files paths, private-payload guards, and the updater strip. Prove it
with rpmspec -P, rpmlint, dnf builddep, and a clean container install/smoke.

## Tear the artifact apart by format

The download name is a label, not evidence. Open the artifact and read the
version and dependencies from inside it:

| Format | What to run |
| --- | --- |
| `.deb` | `dpkg-deb -x` plus the `control` metadata |
| `.rpm` | `rpm2cpio \| cpio -idm` plus header tags |
| AppImage | `--appimage-extract` (gives `squashfs-root`) or `unsquashfs -l` with the offset |
| `.tar`/`.zip` | full listing, then read build files and internal version files |
| GNU/source tree | the whole build system: Cargo.toml/Cargo.lock, meson.build, CMakeLists.txt, go.mod, pyproject.toml and all subdirs |
| git snapshot | commit ID and the checked-out tree |

Then read ELF `NEEDED` entries with `ldd`/`readelf` and map each one to Fedora
with `dnf repoquery --whatprovides <capability>`. This is why a package that
"looks fine" from its filename can still be wrong: the payload may bundle a
library that shadows a real Fedora dependency.
Fedora's Bundled Software policy requires a `Provides: bundled(<lib>) =
<version>` for each bundled library that stays, and its automatic-filtering
guidelines require private capabilities to stay out of global Provides via
`__provides_exclude_from` / `__requires_exclude_from`. Both apply here.

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
