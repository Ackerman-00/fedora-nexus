%global app_id md.obsidian.Obsidian
%global debug_package %{nil}

Name:           obsidian
Version:        1.14.5
Release:        1%{?dist}
Summary:        A powerful knowledge base that works on top of a local folder of plain text Markdown files

License:        LicenseRef-Proprietary
URL:            https://obsidian.md/
ExclusiveArch:  x86_64

Source0:        https://github.com/obsidianmd/obsidian-releases/releases/download/v%{version}/obsidian_%{version}_amd64.deb

AutoReqProv:    no

BuildRequires:  binutils
BuildRequires:  tar
BuildRequires:  xz
BuildRequires:  zstd

Requires:       zlib
Requires:       nss
Requires:       alsa-lib
Requires:       gtk3
Requires:       hicolor-icon-theme
Requires:       at-spi2-core
Requires:       libnotify
Requires:       libsecret
Requires:       libuuid
Requires:       libXScrnSaver
Requires:       libXtst
Requires:       mesa-libgbm
Requires:       xdg-utils
Recommends:     libappindicator-gtk3

%description
Obsidian is a powerful knowledge base that works on top of a local folder 
of plain text Markdown files. The human brain is non-linear: we jump from 
idea to idea, all the time. Your second brain should work the same.

%prep
%setup -c -T

ar x %{SOURCE0}

if [ -f data.tar.xz ]; then
    tar -xf data.tar.xz
elif [ -f data.tar.zst ]; then
    tar --zstd -xf data.tar.zst
elif [ -f data.tar.gz ]; then
    tar -xzf data.tar.gz
else
    echo "Error: Unknown data tarball format in deb package."
    exit 1
fi

%build

%install
install -dm755 %{buildroot}/opt
install -dm755 %{buildroot}%{_datadir}
install -dm755 %{buildroot}%{_bindir}

cp -a opt/Obsidian %{buildroot}/opt/
cp -a usr/share/* %{buildroot}%{_datadir}/

ln -sf /opt/Obsidian/obsidian %{buildroot}%{_bindir}/obsidian

%files
%defattr(-,root,root,-)
%{_bindir}/obsidian
/opt/Obsidian/
%attr(4755, root, root) /opt/Obsidian/chrome-sandbox
%{_datadir}/applications/%{app_id}.desktop
%{_datadir}/mime/packages/obsidian.xml
%{_datadir}/icons/hicolor/*/apps/obsidian.png
%doc %{_datadir}/doc/obsidian/

%changelog
* Thu Oct 22 2026 Ackerman-00 <quietcraft@gmail.com> - 1.14.5-1
- Auto-updated to 1.14.5 via update.sh
- Track upstream deb Recommends with Recommends: libappindicator-gtk3
