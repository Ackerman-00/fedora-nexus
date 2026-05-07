%global app_id md.obsidian.Obsidian

Name:           obsidian
Version:        1.12.7
Release:        3%{?dist}
Summary:        A powerful knowledge base that works on top of a local folder of plain text Markdown files

License:        Commercial
URL:            https://obsidian.md/
ExclusiveArch:  x86_64 aarch64

# Define both sources for SRPM bundling
Source0:        https://github.com/obsidianmd/obsidian-releases/releases/download/v%{version}/obsidian-%{version}.tar.gz
Source1:        https://github.com/obsidianmd/obsidian-releases/releases/download/v%{version}/obsidian-%{version}-arm64.tar.gz

# The custom wrapper script to launch native Electron
Source2:        obsidian.sh

%global debug_package %{nil}
AutoReqProv:    no

# Build tools
BuildRequires:  desktop-file-utils

# Native System Dependencies
Requires:       electron
Requires:       bash
Requires:       hicolor-icon-theme

%description
Obsidian is a powerful knowledge base that works on top of a local folder 
of plain text Markdown files. The human brain is non-linear: we jump from 
idea to idea, all the time. Your second brain should work the same.

%prep
# Extract using -b to prevent double-directory nesting
%ifarch x86_64
%setup -q -T -b 0 -n %{name}-%{version}
%endif

%ifarch aarch64
%setup -q -T -b 1 -n %{name}-%{version}
%endif

%build
# Nothing to compile.

%install
# 1. Install ONLY the core Obsidian application resources
install -dm755 %{buildroot}%{_libdir}/%{name}
cp -r resources %{buildroot}%{_libdir}/%{name}/

# 2. Install the custom launcher script
install -Dm755 %{SOURCE2} %{buildroot}%{_bindir}/%{name}

# 3. Install the Desktop entry
install -Dm644 obsidian.desktop %{buildroot}%{_datadir}/applications/%{app_id}.desktop

sed -i 's|^Exec=obsidian|Exec=/usr/bin/obsidian|g' %{buildroot}%{_datadir}/applications/%{app_id}.desktop
sed -i 's|^Icon=obsidian|Icon=%{app_id}|g' %{buildroot}%{_datadir}/applications/%{app_id}.desktop

# 4. Install the Icon directly from the tarball root
install -Dm644 icon.png %{buildroot}%{_datadir}/pixmaps/%{app_id}.png

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{app_id}.desktop

%files
%defattr(-,root,root,-)
%{_bindir}/%{name}
%{_datadir}/applications/%{app_id}.desktop
%{_datadir}/pixmaps/%{app_id}.png
%dir %{_libdir}/%{name}
%{_libdir}/%{name}/*

%changelog
* Thu May 07 2026 Ackerman-00 <quietcraft@gmail.com> - 1.12.7-3
- Complete rewrite: Switched to native system Electron dependency
- Removed monolithic /opt/ installation
- Fixed architecture-specific tarball extraction
