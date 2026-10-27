%global             full_name zen-browser
%global             application_name zen
%global             debug_package %{nil}

%global             __provides_exclude_from ^/opt/%{application_name}/.*$
%global             __requires_exclude ^lib(gkcodecs|lgpllibs|mozavutil|mozgtk|mozsandbox|mozsqlite3|mozwayland|nssutil3|nss3|smime3|nspr4)\\.so.*$

Name:               zen-browser
Epoch:              2
Version:        1.23.4b
Release:        1%{?dist}
Summary:            Zen Browser - A privacy-focused Firefox fork

License:            MPL-2.0
URL:                https://github.com/zen-browser/desktop
Source0:            https://github.com/zen-browser/desktop/releases/download/1.23.4b/zen.linux-x86_64.tar.xz
# sha256: ba81dd70af70d645f2f0a692f7fa4510f819290abfd8d8e60273d3d5a60d0536
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
* Wed Oct 21 2026 Ackerman-00 <quietcraft@gmail.com> - 2:1.23.4b-1
- Auto-update to upstream release 1.23.4b
