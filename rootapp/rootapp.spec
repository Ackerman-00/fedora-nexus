%global debug_package %{nil}
%global __requires_exclude_from ^/opt/rootapp/.*$
%global __provides_exclude_from ^/opt/rootapp/.*$

Name:           rootapp
Version:        0.9.118
Release:        1%{?dist}
Summary:        Root App is a new Discord alternative, designed for gaming communities and large online groups

License:        Proprietary
URL:            https://www.rootapp.com
ExclusiveArch:  x86_64

Source0:        https://installer.rootapp.com/installer/Linux/X64/Root.AppImage
# sha256: 7d0ad57e26fd235a926283224b23e1556536920c8a28e04b3ba532dc61dc6c92

BuildRequires:  binutils
BuildRequires:  squashfs-tools
BuildRequires:  coreutils

Requires:       gtk3
Requires:       nss
Requires:       alsa-lib
Requires:       libnotify
Requires:       xdg-utils
Requires:       at-spi2-core
Requires:       hicolor-icon-theme
Requires:       zlib
Requires:       libXScrnSaver
Requires:       libXtst
Requires:       mesa-libgbm
Requires:       libsecret

Provides:       rootapp = %{version}-%{release}

%description
Root App is a new Discord alternative, designed for gaming communities and
large online groups.

%prep
%setup -c -T

# Extract the Type 2 AppImage
OFFSET=$(od -An -N8 -t u8 -j 40 %{SOURCE0} | tr -d ' ')
MAGIC=$(dd if=%{SOURCE0} bs=1 skip=$OFFSET count=4 2>/dev/null)

if [ "$MAGIC" != "hsqs" ]; then
    OFFSET=$(python3 -c "
with open('%{SOURCE0}', 'rb') as f:
    d = f.read()
    p = d.find(b'hsqs', 200000)
    print(p if p >= 0 else 0)
")
fi

dd if=%{SOURCE0} bs=$OFFSET skip=1 of=squashfs.img 2>/dev/null
unsquashfs -f squashfs.img >/dev/null

%build
# Nothing to compile.

%install
install -dm755 %{buildroot}/opt/rootapp
cp -ar squashfs-root/* %{buildroot}/opt/rootapp/

install -dm755 %{buildroot}%{_bindir}
ln -s /opt/rootapp/AppRun %{buildroot}%{_bindir}/rootapp

install -Dm644 squashfs-root/Root.png %{buildroot}%{_datadir}/pixmaps/rootapp.png
install -Dm644 squashfs-root/Root.png %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/rootapp.png

if [ -f %{buildroot}/opt/rootapp/chrome-sandbox ]; then
    chmod 4755 %{buildroot}/opt/rootapp/chrome-sandbox
fi

install -dm755 %{buildroot}%{_datadir}/applications/
cat > %{buildroot}%{_datadir}/applications/rootapp.desktop <<DESKTOP_EOF
[Desktop Entry]
Type=Application
Name=Root
Comment=Root App is a new Discord alternative, designed for gaming communities and large online groups
Exec=rootapp %U
Icon=rootapp
Terminal=false
StartupWMClass=Root
Categories=Network;InstantMessaging;
MimeType=x-scheme-handler/rootapp;
DESKTOP_EOF

%files
%{_bindir}/rootapp
/opt/rootapp/
%{_datadir}/applications/rootapp.desktop
%{_datadir}/icons/hicolor/*/apps/rootapp.png
%{_datadir}/pixmaps/rootapp.png
%attr(4755, root, root) /opt/rootapp/chrome-sandbox

%changelog
* Sat Jul 11 2026 Ackerman-00 <quietcraft@gmail.com> - 0.9.118-1
- Initial package of Root App for Fedora Copr from AppImage
