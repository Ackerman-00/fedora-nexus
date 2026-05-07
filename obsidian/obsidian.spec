Name:           obsidian
Version:        1.12.6
Release:        1%{?dist}
Summary:        A powerful knowledge base that works on top of a local folder of plain text Markdown files

License:        Commercial
URL:            https://obsidian.md/
ExclusiveArch:  x86_64 aarch64

# Define both sources so the SRPM bundles them correctly
Source0:        https://github.com/obsidianmd/obsidian-releases/releases/download/v%{version}/obsidian-%{version}.tar.gz
Source1:        https://github.com/obsidianmd/obsidian-releases/releases/download/v%{version}/obsidian-%{version}-arm64.tar.gz

%global debug_package %{nil}
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
# -c: Create directory
# -T: Disable automatic extraction of Source0
# -a #: Extract the specific Source number AFTER changing into the directory
%ifarch x86_64
%setup -q -c -T -a 0 -n %{name}-%{version}
%endif

%ifarch aarch64
%setup -q -c -T -a 1 -n %{name}-%{version}
%endif

%build
# Pre-built Electron binary, no compilation needed.
