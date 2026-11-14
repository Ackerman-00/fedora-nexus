%global debug_package %{nil}

%global __brp_check_rpaths %{nil}

%global __requires_exclude ^libgtk4-layer-shell\.so.*$
%global __provides_exclude ^libgtk4-layer-shell\.so.*$

%global ghostty_version 1.4.0
%global ppatag 1.4.0-0-ppa2
%global debver 1.4.0-0.ppa2
%global debfile ghostty_1.4.0-0.ppa2_amd64_trixie.deb

Name:           ghostty
Version:        %{ghostty_version}
Release:        2%{?dist}
Summary:        A fast, feature-rich, and cross-platform terminal emulator

License:        MIT
URL:            https://github.com/mkasberg/ghostty-ubuntu
# sha256: 82cae2f554a6a666ac9a79095f32d1e9f100a000aa4ba5d45cfea22e1e16c2b6
Source0:        %{url}/releases/download/%{ppatag}/%{debfile}
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
Requires:       libglvnd-egl
Requires:       libwayland-client
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

install -d -m 0755 %{buildroot}%{_includedir}
cp -a usr/include/ghostty %{buildroot}%{_includedir}/ghostty
cp -a usr/include/gtk4-layer-shell.h usr/include/gtk4-session-lock.h %{buildroot}%{_includedir}/

install -d -m 0755 %{buildroot}%{_userunitdir}
cp -a usr/lib/systemd/user/app-com.mitchellh.ghostty.service %{buildroot}%{_userunitdir}/

install -d -m 0755 %{buildroot}%{_datadir}
cp -a usr/share/* %{buildroot}%{_datadir}/
rm -rf %{buildroot}%{_datadir}/doc

install -Dpm 0644 %{SOURCE1} %{buildroot}%{_licensedir}/%{name}/LICENSE

find %{buildroot} \( -path '*/resources/app-update.yml' -o -path '*/resources/package-type' \) -delete 2>/dev/null || true

%files
%license %{_licensedir}/%{name}/LICENSE
%{_bindir}/ghostty
%{_includedir}/ghostty/
%{_includedir}/gtk4-layer-shell.h
%{_includedir}/gtk4-session-lock.h
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
%{_datadir}/pkgconfig/libghostty-vt-static.pc
%{_datadir}/terminfo/
%{_datadir}/vim/
%{_datadir}/zsh/vendor-completions/_ghostty

%changelog
* Sat Nov 14 2026 Ackerman-00 <no-reply> - 1.4.0-2
- Move the in-app updater strip into %install

* Sun Nov 08 2026 Ackerman-00 <no-reply> - 1.4.0-1
- Update to upstream 1.4.0 (PPA release 1.4.0-0-ppa2, trixie amd64 deb; the
  24.04 asset is no longer published for 1.4.0); pin Source0 sha256; add
  Requires: libglvnd-egl (libEGL.so.1) and libwayland-client (libwayland-client.so.0)
  per readelf NEEDED of the shipped binary
