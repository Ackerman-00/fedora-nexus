%global debug_package %{nil}

%global __provides_exclude_from ^/opt/concat/.*$
%global __requires_exclude_from ^/opt/concat/.*$

Name:           concat
Version:        0.2.8
Release:        1%{?dist}
Summary:        Free and open source video editor (CapCut alternative)

License:        AGPL-3.0-or-later
URL:            https://github.com/jub0t/Concat
Source0:        %{url}/releases/download/v0.2.8/Concat-0.2.8-linux-x86_64.rpm
# sha256: 890d377c531d216f93f4888eff4f356ef9e54f70a858e8255328da7af8ea286d

ExclusiveArch:  x86_64

BuildRequires:  desktop-file-utils

Requires:       gtk3
Requires:       fontconfig
Requires:       freetype
Requires:       libxkbcommon
Requires:       libxkbcommon-x11
Requires:       mesa-libGL
Requires:       alsa-lib
Requires:       hicolor-icon-theme

Provides:       concat = %{version}-%{release}

%description
Concat is a free and open source video editor and CapCut alternative.
Auto-captions, text-to-speech, background removal, keyframe animation,
GPU-rendered effects, multi-track cutting and 4K export, all running
locally on a native Rust engine. No watermark, no account, no subscription.

%prep
%setup -T -c
rpm2cpio %{SOURCE0} | cpio -idmv

%install
mkdir -p %{buildroot}/opt/concat
cp -a opt/concat/* %{buildroot}/opt/concat/

mkdir -p %{buildroot}%{_bindir}
install -pm0755 usr/bin/concat %{buildroot}%{_bindir}/concat

install -Dm0644 usr/share/applications/concat.desktop \
    %{buildroot}%{_datadir}/applications/concat.desktop
install -Dm0644 usr/share/icons/hicolor/256x256/apps/concat.png \
    %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/concat.png

desktop-file-validate %{buildroot}%{_datadir}/applications/concat.desktop || true

%files
%license usr/share/doc/concat/LICENSE
%doc usr/share/doc/concat/THIRD_PARTY_NOTICES.md
%{_bindir}/concat
/opt/concat/
%{_datadir}/applications/concat.desktop
%{_datadir}/icons/hicolor/256x256/apps/concat.png

%changelog
* Tue Oct 20 2026 Ackerman-00 <quietcraft@gmail.com> - 0.2.8-1
- Auto-update to upstream release v0.2.8
