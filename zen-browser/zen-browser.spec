%global             full_name zen-browser
%global             application_name zen
%global             debug_package %{nil}

Name:               zen-browser
Version:            1.20.1b
Release:            1%{?dist}
Summary:            Zen Browser - A privacy-focused Firefox fork

License:            MPLv2.0
URL:                https://github.com/zen-browser/desktop
Source0:            https://github.com/zen-browser/desktop/releases/download/%{version}/zen.linux-x86_64.tar.xz
Source1:            %{full_name}.desktop
Source2:            policies.json
Source3:            %{full_name}

ExclusiveArch:      x86_64
BuildRequires:      patchelf

Recommends:         (plasma-browser-integration if plasma-workspace)
Recommends:         (gnome-browser-connector if gnome-shell)

Requires(post):     gtk-update-icon-cache
Conflicts:          zen-browser-avx2, zen-browser-aarch64
Provides:           zen-browser-avx2 = %{version}-%{release}
Obsoletes:          zen-browser-avx2 < 1.0.2.b.3-3

%description
Zen Browser is a highly optimized, privacy-focused fork of Firefox designed for performance and simplicity. 

%prep
%setup -q -n %{application_name}

%install
rm -rf %{buildroot}

install -d %{buildroot}/opt/%{application_name}
install -d %{buildroot}%{_bindir}
install -d %{buildroot}%{_datadir}/applications
install -d %{buildroot}%{_datadir}/icons/hicolor/{16x16,32x32,48x48,64x64,128x128}/apps

cp -r * %{buildroot}/opt/%{application_name}

install -D -m 0644 %{SOURCE1} -t %{buildroot}%{_datadir}/applications
install -D -m 0444 %{SOURCE2} -t %{buildroot}/opt/%{application_name}/distribution
install -D -m 0755 %{SOURCE3} -t %{buildroot}%{_bindir}

# Safeguard: Only run patchelf if upstream actually shipped libonnxruntime.so in the root
if [ -f "%{buildroot}/opt/%{application_name}/libonnxruntime.so" ]; then
    patchelf --set-rpath '$ORIGIN' %{buildroot}/opt/%{application_name}/libonnxruntime.so
fi

ln -s ../../../../../../opt/%{application_name}/browser/chrome/icons/default/default128.png %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/%{full_name}.png
ln -s ../../../../../../opt/%{application_name}/browser/chrome/icons/default/default64.png %{buildroot}%{_datadir}/icons/hicolor/64x64/apps/%{full_name}.png
ln -s ../../../../../../opt/%{application_name}/browser/chrome/icons/default/default48.png %{buildroot}%{_datadir}/icons/hicolor/48x48/apps/%{full_name}.png
ln -s ../../../../../../opt/%{application_name}/browser/chrome/icons/default/default32.png %{buildroot}%{_datadir}/icons/hicolor/32x32/apps/%{full_name}.png
ln -s ../../../../../../opt/%{application_name}/browser/chrome/icons/default/default16.png %{buildroot}%{_datadir}/icons/hicolor/16x16/apps/%{full_name}.png

%post
# Added || : to prevent post-install scriptlet failures if the icon cache is locked
gtk-update-icon-cache -f -t %{_datadir}/icons/hicolor || :

%files
%{_datadir}/applications/%{full_name}.desktop
%{_datadir}/icons/hicolor/128x128/apps/%{full_name}.png
%{_datadir}/icons/hicolor/64x64/apps/%{full_name}.png
%{_datadir}/icons/hicolor/48x48/apps/%{full_name}.png
%{_datadir}/icons/hicolor/32x32/apps/%{full_name}.png
%{_datadir}/icons/hicolor/16x16/apps/%{full_name}.png
%{_bindir}/%{full_name}
/opt/%{application_name}

%changelog
* Wed May 27 2026 Ackerman-00 <quietcraft@gmail.com> - 1.20.1b-1
- Auto-update to upstream release 1.20.1b
- Add patchelf safeguard for libonnxruntime.so

* Sun May 24 2026 Ackerman-00 <quietcraft@gmail.com> - 1.20b-1
- Auto-update to upstream release 1.20b

* Thu May 14 2026 Ackerman-00 <quietcraft@gmail.com> - 1.19.13b-1
- Auto-update to upstream release 1.19.13b

* Sat May 09 2026 Ackerman-00 <quietcraft@gmail.com> - 1.19.12b-1
- Auto-update to upstream release 1.19.12b
