# Disable debuginfo extraction since we are repackaging pre-compiled binaries
%global debug_package %{nil}

# The upstream Ubuntu binary carries a RUNPATH for Ubuntu-only paths and is
# linked against an unversioned libgtk4-layer-shell.so shipped inside the .deb.
%global __brp_check_rpaths %{nil}

# The binary's Needs an unversioned "libgtk4-layer-shell.so" which we ship
# ourselves in %{_libdir}; it must not be turned into a (unresolvable) RPM dep,
# nor advertised as a system Provide.
# NOTE on filter shape: rpm matches these filters against the DECORATED form
# `libgtk4-layer-shell.so()(64bit)` on both sides (verified 2026-09-05: the old
# `\.so$` filters left the Provide in the published 1.3.1-2 RPM and the
# Require reappeared under rpm 6.0.2), so both must use `\.so.*$`.
%global __requires_exclude ^libgtk4-layer-shell\.so.*$
%global __provides_exclude ^libgtk4-layer-shell\.so.*$

# Upstream Ghostty version (drives RPM Version)
%global ghostty_version 1.3.1
# mkasberg/ghostty-ubuntu release tag - "1.3.1-0-ppa2" = PPA build counter,
# bumped whenever the maintainer rebuilds the same Ghostty version.
%global ppatag 1.3.1-0-ppa2
# Debian-style version embedded in the .deb asset name (tag with the last
# dash becoming a dot: "1.3.1-0-ppa2" -> "1.3.1-0.ppa2")
%global debver 1.3.1-0.ppa2

Name:           ghostty
Version:        %{ghostty_version}
Release:        3%{?dist}
Summary:        A fast, feature-rich, and cross-platform terminal emulator

License:        MIT
URL:            https://github.com/mkasberg/ghostty-ubuntu
# Ghostty only publishes macOS binaries itself; this is the community-built
# Ubuntu .deb linked from ghostty.org's install docs. The 24.04 (noble) build
# has the lowest glibc baseline of all published variants, hence the best
# compatibility on Fedora.
Source0:        %{url}/releases/download/%{ppatag}/ghostty_%{debver}_amd64_24.04.deb

ExclusiveArch:  x86_64

# Required to unpack the upstream DEB natively
BuildRequires:  binutils
BuildRequires:  tar
BuildRequires:  xz
BuildRequires:  zstd

# Defines %{_userunitdir} (usr/lib/systemd/user), used for the bundled
# per-user systemd unit
BuildRequires:  systemd-rpm-macros

# Runtime dependencies mapped from the upstream DEB's Depends field
# (libadwaita-1-0 -> libadwaita, libc6 -> glibc, libfontconfig1 -> fontconfig,
#  libfreetype6 -> freetype, libglib2.0-0 -> glib2, libgtk-4-1 -> gtk4,
#  libharfbuzz0b -> harfbuzz, libonig5 -> oniguruma, libx11-6 -> libX11)
Requires:       libadwaita
Requires:       glibc
Requires:       fontconfig
Requires:       freetype
Requires:       glib2
Requires:       gtk4
Requires:       harfbuzz
Requires:       oniguruma
Requires:       libX11

%description
Ghostty is a terminal emulator that differentiates itself by being fast,
feature-rich, and native. While there are many excellent terminal emulators
available, they all force you to choose between speed, features, or native
UIs. Ghostty provides all three.

%prep
%setup -c -T
# Rip open the upstream DEB natively
ar x %{SOURCE0}
# Detect whichever data archive the .deb actually contains and extract it
for data_archive in data.tar.zst data.tar.xz data.tar.gz; do
    if [ -f "$data_archive" ]; then
        tar xf "$data_archive"
        break
    fi
done

%build
# No compilation required for pre-built binaries

%install
rm -rf %{buildroot}

# 1. Install the main binary
install -d -m 0755 %{buildroot}%{_bindir}
cp -a usr/bin/ghostty %{buildroot}%{_bindir}/ghostty

# 2. Install the bundled libraries. libgtk4-layer-shell.so has NO soname so
#    ld.so only finds it through its default-dir fallback: keep the exact
#    unversioned filename upstream ships in %{_libdir}. libghostty-vt is
#    properly versioned (SONAME libghostty-vt.so.0) and resolves via the
#    ld.so cache like any system library.
install -d -m 0755 %{buildroot}%{_libdir}
cp -a usr/lib/libgtk4-layer-shell.so %{buildroot}%{_libdir}/libgtk4-layer-shell.so
cp -a usr/lib/libghostty-vt.so.0.1.0 %{buildroot}%{_libdir}/libghostty-vt.so.0.1.0
ln -s libghostty-vt.so.0.1.0 %{buildroot}%{_libdir}/libghostty-vt.so.0
ln -s libghostty-vt.so.0.1.0 %{buildroot}%{_libdir}/libghostty-vt.so

# 3. Install the per-user systemd unit (single-instance D-Bus service host)
install -d -m 0755 %{buildroot}%{_userunitdir}
cp -a usr/lib/systemd/user/app-com.mitchellh.ghostty.service %{buildroot}%{_userunitdir}/

# 4. Install all desktop integration data (applications, icons, completions,
#    locale, man pages, metainfo, terminfo, themes, editor integrations...)
#    minus the Debian-specific doc/ directory.
install -d -m 0755 %{buildroot}%{_datadir}
cp -a usr/share/* %{buildroot}%{_datadir}/
rm -rf %{buildroot}%{_datadir}/doc

%files
%{_bindir}/ghostty
%{_libdir}/libgtk4-layer-shell.so
%{_libdir}/libghostty-vt.so
%{_libdir}/libghostty-vt.so.0
%{_libdir}/libghostty-vt.so.0.1.0
%{_userunitdir}/app-com.mitchellh.ghostty.service
%{_datadir}/applications/com.mitchellh.ghostty.desktop
%{_datadir}/bash-completion/completions/ghostty.bash
%{_datadir}/bat/
%{_datadir}/dbus-1/services/com.mitchellh.ghostty.service
%{_datadir}/fish/vendor_completions.d/ghostty.fish
%{_datadir}/ghostty/
%{_datadir}/icons/hicolor/*/apps/com.mitchellh.ghostty.png
%{_datadir}/kio/servicemenus/com.mitchellh.ghostty.desktop
%{_datadir}/locale/*/LC_MESSAGES/com.mitchellh.ghostty.mo
%{_datadir}/man/man1/ghostty.1.gz
%{_datadir}/man/man5/ghostty.5.gz
%{_datadir}/metainfo/com.mitchellh.ghostty.metainfo.xml
%{_datadir}/nautilus-python/extensions/ghostty.py
%{_datadir}/nvim/
%{_datadir}/pkgconfig/libghostty-vt.pc
%{_datadir}/terminfo/
%{_datadir}/vim/
%{_datadir}/zsh/vendor-completions/_ghostty

%changelog
* Sat Sep 05 2026 Ackerman-00 <quietcraft@gmail.com> - 1.3.1-3
- Fix __provides_exclude for the bundled libgtk4-layer-shell.so: rpm matches
  provides-filters against the decorated `libgtk4-layer-shell.so()(64bit)`
  form, so `\.so$` never matched and the published RPM advertised a system
  soname it must not own (same hijack class as helium-browser/libvulkan).
  Same upstream .deb, spec-only fix.
* Wed Aug 12 2026 Ackerman-00 <quietcraft@gmail.com> - 1.3.1-2
- Fix COPR build (10850831): add BuildRequires: systemd-rpm-macros so
  %{_userunitdir} expands, and create %{_datadir} before copying usr/share/*

* Wed Aug 12 2026 Ackerman-00 <quietcraft@gmail.com> - 1.3.1-1
- Initial packaging: repackage the official community-built Ubuntu .deb of
  ghostty 1.3.1 (mkasberg/ghostty-ubuntu PPA release 1.3.1-0-ppa2, noble
  build) for Fedora, following the repo's .deb repackaging pattern