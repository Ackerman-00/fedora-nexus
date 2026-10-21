%global             full_name zen-browser
%global             application_name zen
%global             debug_package %{nil}

# Bundled /opt Gecko libs must not become Provides.
%global             __provides_exclude_from ^/opt/%{application_name}/.*$
# bundled libnssutil3.so needs NSSUTIL_3.130, F45 nss-util is 3.129.0
%global             __requires_exclude ^lib(gkcodecs|lgpllibs|mozavutil|mozgtk|mozsandbox|mozsqlite3|mozwayland|nssutil3|nss3|smime3|nspr4)\\.so.*$

Name:               zen-browser
# Epoch 2 supersedes the 1.23.4b build upstream withdrew; keep it forever.
Epoch:              2
Version:        1.23.3b
Release:        4%{?dist}
Summary:            Zen Browser - A privacy-focused Firefox fork

License:            MPL-2.0
URL:                https://github.com/zen-browser/desktop
Source0:            https://github.com/zen-browser/desktop/releases/download/1.23.3b/zen.linux-x86_64.tar.xz
# sha256: bb2045d3e21654d40fe841250092eeadfd2c1fc831eefb509222773c8bdca149
Source1:            %{full_name}.desktop
Source2:            policies.json
Source3:            %{full_name}
# Tarball lacks MPL text; fetch from the tag.
Source4:            https://github.com/zen-browser/desktop/raw/%{version}/LICENSE

ExclusiveArch:      x86_64
BuildRequires:      patchelf

Recommends:         (plasma-browser-integration if plasma-workspace)
Recommends:         (gnome-browser-connector if gnome-shell)

Requires(post):     gtk-update-icon-cache
Requires:           hicolor-icon-theme
Conflicts:          zen-browser-avx2
Provides:           zen-browser-avx2 = %{epoch}:%{version}-%{release}
Obsoletes:          zen-browser-avx2 < 1.0.2.b.3-3

%description
Zen Browser is a highly optimized, privacy-focused fork of Firefox designed for performance and simplicity. 

%prep
%setup -q -n %{application_name}

%install
install -d %{buildroot}/opt/%{application_name}
install -d %{buildroot}%{_bindir}
install -d %{buildroot}%{_datadir}/applications
install -d %{buildroot}%{_datadir}/icons/hicolor/{16x16,32x32,48x48,64x64,128x128}/apps
install -d %{buildroot}%{_datadir}/pixmaps

cp -r * %{buildroot}/opt/%{application_name}

install -D -m 0644 %{SOURCE1} -t %{buildroot}%{_datadir}/applications
install -D -m 0444 %{SOURCE2} -t %{buildroot}/opt/%{application_name}/distribution
install -D -m 0755 %{SOURCE3} -t %{buildroot}%{_bindir}

# Convenience symlink
ln -sf %{full_name} %{buildroot}%{_bindir}/zen

# Ship the MPL-2.0 text the binary tarball does not carry
install -Dpm 0644 %{SOURCE4} %{buildroot}%{_licensedir}/%{name}/LICENSE

# Safeguard: Only run patchelf if upstream actually shipped libonnxruntime.so in the root
if [ -f "%{buildroot}/opt/%{application_name}/libonnxruntime.so" ]; then
    patchelf --set-rpath '$ORIGIN' %{buildroot}/opt/%{application_name}/libonnxruntime.so
fi

# Icons - symlinks from upstream icons
ln -s ../../../../../../opt/%{application_name}/browser/chrome/icons/default/default128.png %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/%{full_name}.png
ln -s ../../../../../../opt/%{application_name}/browser/chrome/icons/default/default64.png %{buildroot}%{_datadir}/icons/hicolor/64x64/apps/%{full_name}.png
ln -s ../../../../../../opt/%{application_name}/browser/chrome/icons/default/default48.png %{buildroot}%{_datadir}/icons/hicolor/48x48/apps/%{full_name}.png
ln -s ../../../../../../opt/%{application_name}/browser/chrome/icons/default/default32.png %{buildroot}%{_datadir}/icons/hicolor/32x32/apps/%{full_name}.png
ln -s ../../../../../../opt/%{application_name}/browser/chrome/icons/default/default16.png %{buildroot}%{_datadir}/icons/hicolor/16x16/apps/%{full_name}.png

# Pixmaps icon for legacy apps
ln -s ../../../../../../opt/%{application_name}/browser/chrome/icons/default/default128.png %{buildroot}%{_datadir}/pixmaps/%{full_name}.png

%post
# Added || : to prevent post-install scriptlet failures if the icon cache is locked
gtk-update-icon-cache -f -t %{_datadir}/icons/hicolor || :

%postun
gtk-update-icon-cache -f -t %{_datadir}/icons/hicolor || :

%files
%license %{_licensedir}/%{name}/LICENSE
%{_datadir}/applications/%{full_name}.desktop
%{_datadir}/icons/hicolor/128x128/apps/%{full_name}.png
%{_datadir}/icons/hicolor/64x64/apps/%{full_name}.png
%{_datadir}/icons/hicolor/48x48/apps/%{full_name}.png
%{_datadir}/icons/hicolor/32x32/apps/%{full_name}.png
%{_datadir}/icons/hicolor/16x16/apps/%{full_name}.png
%{_datadir}/pixmaps/%{full_name}.png
%{_bindir}/%{full_name}
%{_bindir}/zen
/opt/%{application_name}

%changelog
* Wed Oct 21 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 2:1.23.3b-4
- Return to 1.23.3b: upstream withdrew release 1.23.4b. Its release page,
  git tag and every asset now answer HTTP 404 (verified 2026-10-21 12:25
  UTC), so a spec pointing at it cannot rebuild. Same tarball as -3,
  sha256 bb2045d3.... Epoch 2 supersedes the published 1:1.23.4b-1, so a
  fresh install no longer selects the withdrawn build.
* Tue Oct 20 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 1:1.23.3b-3
- Ship the upstream MPL-2.0 LICENSE as Source4 (same 1.23.3b tag). The
  package declared MPL-2.0 but the binary tarball carries no license text.

* Sun Oct 18 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 1:1.23.3b-2
- Exclude the bundled NSS/NSPR sonames from auto-generated Requires. The
  private /opt/zen/libnssutil3.so demands libnssutil3.so(NSSUTIL_3.130)
  while Fedora 45 ships nss-util 3.129.0, so zen-browser-1.23.3b-1.fc45
  could not install there ("nothing provides libnssutil3.so
  (NSSUTIL_3.130)") and dnf silently offered the older 1.23.2b build.
  Fedora 44 resolved it by luck with nss-util 3.131.0. Every ELF in this
  package lives under /opt/zen next to its own NSS/NSPR copies, so the
  system is never asked for those sonames. Same upstream 1.23.3b.
* Sat Oct 17 2026 Ackerman-00 <quietcraft@gmail.com> - 1:1.23.3b-1
- Auto-update to upstream release 1.23.3b
