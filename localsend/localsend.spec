%global debug_package %{nil}

%global __requires_exclude_from ^%{_libdir}/localsend_app/.*$
%global __provides_exclude_from ^%{_libdir}/localsend_app/.*$

Name:           localsend
Version:        1.19.0
Release:        1%{?dist}
Summary:        An open source cross-platform alternative to AirDrop

License:        Apache-2.0
URL:            https://github.com/localsend/localsend
Source0:        %{url}/releases/download/v1.19.0/LocalSend-1.19.0-linux-x86-64.deb
Source1:        %{url}/raw/v%{version}/LICENSE

ExclusiveArch:  x86_64

BuildRequires:  binutils
BuildRequires:  patchelf
BuildRequires:  tar

Requires:           hicolor-icon-theme
Requires:       libayatana-appindicator-gtk3
Requires:       libayatana-ido-gtk3
Requires:       libEGL.so.1()(64bit)
Requires:       libGLESv2.so.2()(64bit)
Requires:       xdg-user-dirs

%description
LocalSend is a free, open-source app that enables secure communication
between devices using a REST API and HTTPS encryption. Unlike other
messaging apps that rely on external servers, LocalSend doesn't require
an internet connection or third-party servers, making it a fast and
reliable solution for local communication.
Packaged exclusively for the Nexus repository. This version natively
extracts the upstream DEB payload.

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

install -d -m 0755 %{buildroot}%{_datadir}
cp -a usr/share/* %{buildroot}%{_datadir}/

install -d -m 0755 %{buildroot}%{_libdir}
cp -a opt/localsend_app %{buildroot}%{_libdir}/localsend_app

install -d -m 0755 %{buildroot}%{_bindir}
cat <<-'EOF' > %{buildroot}%{_bindir}/localsend_app
#!/bin/sh
exec %{_libdir}/localsend_app/localsend_app "$@"
EOF
chmod 0755 %{buildroot}%{_bindir}/localsend_app

find %{buildroot}%{_libdir}/localsend_app/lib -type f -name '*.so*' \
    -exec patchelf --set-rpath '$ORIGIN' {} +

install -Dpm 0644 %{SOURCE1} %{buildroot}%{_licensedir}/%{name}/LICENSE

find %{buildroot} \( -path '*/resources/app-update.yml' -o -path '*/resources/package-type' \) -delete 2>/dev/null || true

%files
%license %{_licensedir}/%{name}/LICENSE
%{_bindir}/localsend_app
%{_datadir}/applications/localsend_app.desktop
%{_datadir}/icons/hicolor/*/apps/localsend_app.png
%{_libdir}/localsend_app/

%changelog
* Wed Nov 25 2026 Ackerman-00 <no-reply> - 1.19.0-1
- Auto-update to upstream release v1.19.0
