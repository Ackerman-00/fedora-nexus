%global debug_package %{nil}

Name:           rustypipe-botguard
Version:        0.1.2
Release:        2%{?dist}
Summary:        YouTube Botguard challenge solver for PO token generation

License:        MIT
URL:            https://codeberg.org/ThetaDev/rustypipe-botguard

# sha256: 4f2ec561e8f9fadece7deadc6ce0624fbdedd852222c3eb194c22153b1323129
Source0:        https://codeberg.org/ThetaDev/rustypipe-botguard/releases/download/v%{version}/rustypipe-botguard-v%{version}-x86_64-unknown-linux-gnu.tar.xz
Source1:        %{url}/raw/tag/v%{version}/LICENSE

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

%install
install -Dpm0755 rustypipe-botguard -t %{buildroot}%{_bindir}
install -Dpm0644 %{SOURCE1} %{buildroot}%{_licensedir}/%{name}/LICENSE

%files
%license %{_licensedir}/%{name}/LICENSE
%{_bindir}/rustypipe-botguard

%changelog
* Tue Oct 20 2026 opencode-agent[bot] <41898282+opencode-agent[bot]@users.noreply.github.com> - 0.1.2-2
- Ship the upstream MIT LICENSE (Source1, same v0.1.2 tag); the release
  tarball contains only the binary.

* Sun Sep 06 2026 Ackerman-00 <quietcraft@gmail.com> - 0.1.2-1
- Initial package (PO-token helper for mixtapes). Debuginfo disabled (prebuilt stripped binary).
