%global appid app.fluxer.Fluxer

Name:           fluxer
Version:        2026.724.203709
Release:        4%{?dist}
Summary:        Free and open source instant messaging and VoIP platform

License:        AGPL-3.0-or-later AND BSD
URL:            https://fluxer.app
Source0:        https://api.fluxer.app/dl/desktop/stable/linux/x64/latest/rpm

Requires:       (falcond or gamemode)
Requires:       mangohud

%global _enable_debug_packages 0

%description
Fluxer is a free and open source instant messaging and VoIP platform built for
friends, groups, and communities. Self-hosting and more.

%prep
%setup -T -c
rpm2cpio %{SOURCE0} | cpio -idmv

%install
mkdir -p %{buildroot}%{_libdir}/%{name}
cp -a opt/Fluxer/* %{buildroot}%{_libdir}/%{name}/

mkdir -p %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/%{name} <<'EOF'
#!/bin/sh
exec %{_libdir}/%{name}/%{name} "$@"
EOF
chmod 0755 %{buildroot}%{_bindir}/%{name}

install -Dm0644 usr/share/applications/fluxer.desktop \
    %{buildroot}%{_datadir}/applications/%{appid}.desktop

for size in 256 512; do
    install -Dm0644 usr/share/icons/hicolor/${size}x${size}/apps/fluxer.png \
        %{buildroot}%{_datadir}/icons/hicolor/${size}x${size}/apps/%{appid}.png
done

desktop-file-validate %{buildroot}%{_datadir}/applications/%{appid}.desktop || true

%files
%license opt/Fluxer/LICENSE.electron.txt
%doc opt/Fluxer/LICENSES.chromium.html
%{_bindir}/%{name}
%{_libdir}/%{name}/
%{_datadir}/applications/%{appid}.desktop
%{_datadir}/icons/hicolor/256x256/apps/%{appid}.png
%{_datadir}/icons/hicolor/512x512/apps/%{appid}.png

%changelog
* Thu Jul 30 2026 Ackerman-00 <quietcraft@gmail.com> - 2026.724.203709-4
- Fix RPM 6 auto-generated debugsource subpackage: use _enable_debug_packages 0 instead of _debuginfo_policy none
