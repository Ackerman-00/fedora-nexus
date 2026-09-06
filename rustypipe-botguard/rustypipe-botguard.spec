# No debuginfo: prebuilt upstream binary is already stripped, so
# find-debuginfo would emit an empty debugsource list which rpm >= 6
# rejects as a hard error (same failure as mixtapes build 10955014;
# same convention as heroic/vesktop/fluxer prebuilt specs).
%global debug_package %{nil}

Name:           rustypipe-botguard
Version:        0.1.2
Release:        1%{?dist}
Summary:        YouTube Botguard challenge solver for PO token generation

License:        MIT
URL:            https://codeberg.org/ThetaDev/rustypipe-botguard

# sha256: 4f2ec561e8f9fadece7deadc6ce0624fbdedd852222c3eb194c22153b1323129
# Upstream prebuilt gnu tarball (single binary; also publishes aarch64,
# this repo only ships x86_64 chroots)
Source0:        https://codeberg.org/ThetaDev/rustypipe-botguard/releases/download/v%{version}/rustypipe-botguard-v%{version}-x86_64-unknown-linux-gnu.tar.xz

ExclusiveArch:  x86_64

%description
rustypipe-botguard runs YouTube Botguard challenges and generates PO
tokens, unlocking PO-token-gated formats (e.g. seekable Opus) in
yt-dlp based players. Packaged for the Nexus repository as a helper
binary for mixtapes (expected on PATH by yt-dlp-get-pot-rustypipe).

%prep
%setup -c -T
tar xJf %{SOURCE0}

%build
# No compilation - prebuilt upstream binary

%install
rm -rf %{buildroot}
install -Dpm0755 rustypipe-botguard -t %{buildroot}%{_bindir}

%files
%{_bindir}/rustypipe-botguard

%changelog
* Sun Sep 06 2026 Ackerman-00 <quietcraft@gmail.com> - 0.1.2-1
- Initial package (PO-token helper for mixtapes). Debuginfo disabled (prebuilt stripped binary).
