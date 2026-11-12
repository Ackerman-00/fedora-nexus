%global             full_name zen-browser
%global             application_name zen
%global             debug_package %{nil}

%global             __provides_exclude_from ^/opt/%{application_name}/.*$
%global             __requires_exclude ^lib(gkcodecs|lgpllibs|mozavutil|mozgtk|mozsandbox|mozsqlite3|mozwayland|nssutil3|nss3|plc4|plds4|smime3|ssl3|nspr4)\\.so.*$

Name:               zen-browser
Epoch:              2
Version:        1.24.1b
Release:        2%{?dist}
Summary:            Zen Browser - A privacy-focused Firefox fork

License:            MPL-2.0
URL:                https://github.com/zen-browser/desktop
Source0:            https://github.com/zen-browser/desktop/releases/download/1.24.1b/zen.linux-x86_64.tar.xz
# sha256: c592a31fe8faa5ddfe91d6243b50c3107e1831c1247539fe03cc04f0fd5cb9cd
Source1:            %{full_name}.desktop
Source2:            policies.json
Source3:            %{full_name}
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

ln -sf %{full_name} %{buildroot}%{_bindir}/zen

install -Dpm 0644 %{SOURCE4} %{buildroot}%{_licensedir}/%{name}/LICENSE

if [ -f "%{buildroot}/opt/%{application_name}/libonnxruntime.so" ]; then
    patchelf --set-rpath '$ORIGIN' %{buildroot}/opt/%{application_name}/libonnxruntime.so
fi

ln -s ../../../../../../opt/%{application_name}/browser/chrome/icons/default/default128.png %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/%{full_name}.png
ln -s ../../../../../../opt/%{application_name}/browser/chrome/icons/default/default64.png %{buildroot}%{_datadir}/icons/hicolor/64x64/apps/%{full_name}.png
ln -s ../../../../../../opt/%{application_name}/browser/chrome/icons/default/default48.png %{buildroot}%{_datadir}/icons/hicolor/48x48/apps/%{full_name}.png
ln -s ../../../../../../opt/%{application_name}/browser/chrome/icons/default/default32.png %{buildroot}%{_datadir}/icons/hicolor/32x32/apps/%{full_name}.png
ln -s ../../../../../../opt/%{application_name}/browser/chrome/icons/default/default16.png %{buildroot}%{_datadir}/icons/hicolor/16x16/apps/%{full_name}.png

ln -s ../../../../../../opt/%{application_name}/browser/chrome/icons/default/default128.png %{buildroot}%{_datadir}/pixmaps/%{full_name}.png

%post
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
* Thu Nov 12 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 2:1.24.1b-2
- Exclude libplc4/libplds4/libssl3 from auto-requires: zen's bundle ships
  the full nss/nspr stack (release 1 dragged in system nspr+nss for them).
  Same upstream 1.24.1b.

* Fri Nov 06 2026 Ackerman-00 <no-reply> - 2:1.24.1b-1
- Auto-update to upstream release 1.24.1b
