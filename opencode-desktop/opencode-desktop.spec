%global debug_package %{nil}
%global __requires_exclude_from ^/opt/opencode-desktop/.*$
%global __provides_exclude_from ^/opt/opencode-desktop/.*$

Name:           opencode-desktop
Version:        1.17.17
Release:        2%{?dist}
Summary:        Open source AI coding agent

License:        Apache-2.0
URL:            https://github.com/anomalyco/opencode
Source0:        https://github.com/anomalyco/opencode/releases/download/v%{version}/opencode-desktop-linux-x86_64.rpm

ExclusiveArch:  x86_64

BuildRequires:  cpio

Requires:       gtk3
Requires:       nss
Requires:       alsa-lib
Requires:       libxkbcommon
Requires:       cups-libs
Requires:       dbus-libs
Requires:       nspr
Requires:       expat
Requires:       mesa-libgbm
Requires:       systemd-libs

%description
OpenCode is an open source AI coding agent that helps you write,
debug, and refactor code directly in your editor. It provides
intelligent code suggestions, automated refactoring, and natural
language code generation capabilities.

%prep
%setup -c -T
rpm2cpio %{SOURCE0} | cpio -idmv

%install
rm -rf %{buildroot}

# Install the main application directory
mkdir -p %{buildroot}/opt
cp -ar opt/OpenCode %{buildroot}/opt/opencode-desktop

# Create the binary symlink
mkdir -p %{buildroot}%{_bindir}
ln -s /opt/opencode-desktop/ai.opencode.desktop %{buildroot}%{_bindir}/opencode-desktop

# Set SUID on chrome-sandbox if present
if [ -f %{buildroot}/opt/opencode-desktop/chrome-sandbox ]; then
    chmod 4755 %{buildroot}/opt/opencode-desktop/chrome-sandbox
fi

# Install icons
for size in 32 64 128; do
    install -Dm644 usr/share/icons/hicolor/${size}x${size}/apps/ai.opencode.desktop.png \
        %{buildroot}%{_datadir}/icons/hicolor/${size}x${size}/apps/opencode-desktop.png
done

# Install desktop file from RPM
install -Dm644 usr/share/applications/ai.opencode.desktop.desktop \
    %{buildroot}%{_datadir}/applications/opencode-desktop.desktop
sed -i 's/^Exec=.*/Exec=opencode-desktop %U/' \
    %{buildroot}%{_datadir}/applications/opencode-desktop.desktop
sed -i 's/^Icon=.*/Icon=opencode-desktop/' \
    %{buildroot}%{_datadir}/applications/opencode-desktop.desktop

%files
%{_bindir}/opencode-desktop
%{_datadir}/applications/opencode-desktop.desktop
%{_datadir}/icons/hicolor/*/apps/opencode-desktop.png
/opt/opencode-desktop/

%changelog
* Sat Jul 11 2026 Ackerman-00 <quietcraft@gmail.com> - 1.17.17-2
- Switch from DEB to RPM source; install desktop file from RPM

* Sat Jul 11 2026 Ackerman-00 <quietcraft@gmail.com> - 1.17.18-1
- Initial package of OpenCode Desktop for Fedora Copr from DEB
