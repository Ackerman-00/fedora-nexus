Name:           obsidian
Version:        1.12.7
Release:        1%{?dist}
Summary:        A powerful knowledge base that works on top of a local folder of plain text Markdown files

License:        Commercial
URL:            https://obsidian.md/
ExclusiveArch:  x86_64 aarch64

%ifarch x86_64
%global arch_string %{nil}
%endif
%ifarch aarch64
%global arch_string -arm64
%endif

Source0:        https://github.com/obsidianmd/obsidian-releases/releases/download/v%{version}/obsidian-%{version}%{arch_string}.tar.gz

# Disable debug package extraction for pre-compiled closed-source binaries
%global debug_package %{nil}

# Stop RPM from scanning Obsidian's internal Electron .so files
AutoReqProv:    no

# Strict Fedora dependencies for Electron / Wayland
Requires:       alsa-lib
Requires:       at-spi2-core
Requires:       cairo
Requires:       cups-libs
Requires:       gtk3
Requires:       libX11
Requires:       libXScrnSaver
Requires:       libXcomposite
Requires:       libXcursor
Requires:       libXdamage
Requires:       libXext
Requires:       libXfixes
Requires:       libXi
Requires:       libXrandr
Requires:       libXtst
Requires:       libdrm
Requires:       libnotify
Requires:       libxcb
Requires:       libxkbcommon
Requires:       libxshmfence
Requires:       mesa-libgbm
Requires:       nss

%description
Obsidian is a powerful knowledge base that works on top of a local folder 
of plain text Markdown files. The human brain is non-linear: we jump from 
idea to idea, all the time. Your second brain should work the same.

%prep
# Extract directly into the build directory
%setup -q -c -n %{name}-%{version}

%build
# Pre-built Electron binary, no compilation needed.

%install
mkdir -p %{buildroot}/opt/Obsidian
cp -a * %{buildroot}/opt/Obsidian/

# Fix the SUID sandbox (Strict requirement for Electron apps on Linux)
chmod 4755 %{buildroot}/opt/Obsidian/chrome-sandbox

# Create the executable symlink
mkdir -p %{buildroot}%{_bindir}
ln -sf /opt/Obsidian/obsidian %{buildroot}%{_bindir}/obsidian

# Install the Desktop entry
mkdir -p %{buildroot}%{_datadir}/applications
install -m 644 %{buildroot}/opt/Obsidian/obsidian.desktop %{buildroot}%{_datadir}/applications/obsidian.desktop
sed -i 's|^Exec=obsidian|Exec=/usr/bin/obsidian|g' %{buildroot}%{_datadir}/applications/obsidian.desktop

# Install the Icon
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/512x512/apps
install -m 644 %{buildroot}/opt/Obsidian/obsidian.png %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/obsidian.png

%files
%defattr(-,root,root,-)
/opt/Obsidian
%{_bindir}/obsidian
%{_datadir}/applications/obsidian.desktop
%{_datadir}/icons/hicolor/512x512/apps/obsidian.png

%changelog
* Thu May 07 2026 Ackerman-00 <quietcraft@gmail.com> - 1.12.7-1
- Initial Fedora packaging via tarball for OBS
