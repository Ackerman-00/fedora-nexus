%global debug_package %{nil}

# Concat ships its own FFmpeg + onnxruntime under /opt/concat/lib with
# DT_RPATH $ORIGIN/lib (see upstream assets/linux/nfpm.yaml). Those bundled
# libraries must not be advertised as system-wide Provides, nor become
# system Requires; the genuine system deps below are declared explicitly.
%global __provides_exclude_from ^/opt/concat/.*$
%global __requires_exclude_from ^/opt/concat/.*$

Name:           concat
Version:        0.2.5
Release:        1%{?dist}
Summary:        Free and open source video editor (CapCut alternative)

License:        AGPL-3.0-or-later
URL:            https://github.com/jub0t/Concat
Source0:        %{url}/releases/download/v%{version}/Concat-%{version}-linux-x86_64.rpm
# sha256: 48cfca1b864b58799b0642b847d7ac13e2b35c6841235ec73480d1ebc697c950

ExclusiveArch:  x86_64
# aarch64 asset exists upstream (Concat-0.2.5-linux-aarch64.rpm) but this repo
# only enables x86_64 COPR chroots; extend with a %ifarch Source0 if that changes.

BuildRequires:  desktop-file-utils

# System libraries the binary loads outside its own lib/ — the exact set from
# upstream assets/linux/nfpm.yaml (rpm.depends), names already Fedora-style.
Requires:       gtk3
Requires:       fontconfig
Requires:       freetype
Requires:       libxkbcommon
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
* Sat Oct 03 2026 Ackerman-00 <quietcraft@gmail.com> - 0.2.5-1
- Initial packaging: repack upstream nfpm-built RPM (Rust+Slint, self-contained FFmpeg)
