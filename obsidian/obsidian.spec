%global app_id md.obsidian.Obsidian
%global debug_package %{nil}

Name:           obsidian
Version:        1.13.7
Release:        1%{?dist}
Summary:        A powerful knowledge base that works on top of a local folder of plain text Markdown files

License:        Commercial
URL:            https://obsidian.md/
ExclusiveArch:  x86_64

# Directly source the official Debian package
Source0:        https://github.com/obsidianmd/obsidian-releases/releases/download/v%{version}/obsidian_%{version}_amd64.deb

# Disable automatic dependency generation to prevent RPM from tracking bundled Electron .so files
AutoReqProv:    no

# Build tools required to natively unpack the .deb payload
BuildRequires:  binutils
BuildRequires:  tar
BuildRequires:  xz
BuildRequires:  zstd

# Core runtime dependencies for Electron on Linux (matching upstream deb Depends)
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

%description
Obsidian is a powerful knowledge base that works on top of a local folder 
of plain text Markdown files. The human brain is non-linear: we jump from 
idea to idea, all the time. Your second brain should work the same.

%prep
# Create an empty build directory and enter it without looking for a tarball
%setup -c -T

# 1. Extract the .deb archive natively using binutils
ar x %{SOURCE0}

# 2. Extract the data payload. 
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
# Nothing to compile.

%install
# 1. Recreate the host architecture
install -dm755 %{buildroot}/opt
install -dm755 %{buildroot}%{_datadir}
install -dm755 %{buildroot}%{_bindir}

# 2. Transpose the pre-configured directory structure from the extracted deb
cp -a opt/Obsidian %{buildroot}/opt/
cp -a usr/share/* %{buildroot}%{_datadir}/

# 3. Create the global executable symlink
ln -sf /opt/Obsidian/obsidian %{buildroot}%{_bindir}/obsidian

%files
%defattr(-,root,root,-)
%{_bindir}/obsidian
/opt/Obsidian/
%{_datadir}/applications/%{app_id}.desktop
%{_datadir}/icons/hicolor/*/apps/obsidian.png
# Include doc directory if upstream continues to package it
%doc %{_datadir}/doc/obsidian/

%changelog
* Wed Aug 12 2026 Ackerman-00 <quietcraft@gmail.com> - 1.13.7-1
- Auto-updated to 1.13.7 via update.sh
