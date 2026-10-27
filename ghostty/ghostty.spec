%global debug_package %{nil}

%global __brp_check_rpaths %{nil}

%global __requires_exclude ^libgtk4-layer-shell\.so.*$
%global __provides_exclude ^libgtk4-layer-shell\.so.*$

%global ghostty_version 1.3.1
%global ppatag 1.3.1-0-ppa2
%global debver 1.3.1-0.ppa2

Name:           ghostty
Version:        %{ghostty_version}
Release:        4%{?dist}
Summary:        A fast, feature-rich, and cross-platform terminal emulator

License:        MIT
URL:            https://github.com/mkasberg/ghostty-ubuntu
Source0:        %{url}/releases/download/%{ppatag}/ghostty_%{debver}_amd64_24.04.deb
Source1:        https://raw.githubusercontent.com/ghostty-org/ghostty/v%{ghostty_version}/LICENSE

ExclusiveArch:  x86_64

BuildRequires:  binutils
BuildRequires:  tar
BuildRequires:  xz
BuildRequires:  zstd

BuildRequires:  systemd-rpm-macros

Requires:           hicolor-icon-theme
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
ar x %{SOURCE0}
for data_archive in data.tar.zst data.tar.xz data.tar.gz; do
    if [ -f "$data_archive" ]; then
        tar xf "$data_archive"
        break
    fi
done

%build

%install

install -d -m 0755 %{buildroot}%{_bindir}
cp -a usr/bin/ghostty %{buildroot}%{_bindir}/ghostty

install -d -m 0755 %{buildroot}%{_libdir}
cp -a usr/lib/libgtk4-layer-shell.so %{buildroot}%{_libdir}/libgtk4-layer-shell.so
cp -a usr/lib/libghostty-vt.so.0.1.0 %{buildroot}%{_libdir}/libghostty-vt.so.0.1.0
ln -s libghostty-vt.so.0.1.0 %{buildroot}%{_libdir}/libghostty-vt.so.0
ln -s libghostty-vt.so.0.1.0 %{buildroot}%{_libdir}/libghostty-vt.so

install -d -m 0755 %{buildroot}%{_userunitdir}
cp -a usr/lib/systemd/user/app-com.mitchellh.ghostty.service %{buildroot}%{_userunitdir}/

install -d -m 0755 %{buildroot}%{_datadir}
cp -a usr/share/* %{buildroot}%{_datadir}/
rm -rf %{buildroot}%{_datadir}/doc

install -Dpm 0644 %{SOURCE1} %{buildroot}%{_licensedir}/%{name}/LICENSE

%files
%license %{_licensedir}/%{name}/LICENSE
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
* Tue Oct 20 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 1.3.1-4
- Ship the upstream MIT LICENSE (Source1, pinned to ghostty v1.3.1); the
  PPA deb payload carries no license text.

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